(ns actors.simple-dag-system
  "Simple Directed Acyclic Graph (DAG) System for ACTORS"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.set :as set]
            [actors.simple-higher-order-functions :as hof]))

;; =============================================================================
;; SIMPLE DAG DATA STRUCTURES
;; =============================================================================

(defrecord DAGNode [id type data execute-fn])
(defrecord DAGEdge [id source target weight])
(defrecord DAG [id name nodes edges])

(defn create-dag-node
  "Create a DAG node"
  [id type data execute-fn]
  (->DAGNode id type data execute-fn))

(defn create-dag-edge
  "Create a DAG edge"
  [id source target & {:keys [weight] :or {weight 1.0}}]
  (->DAGEdge id source target weight))

(defn create-dag
  "Create a DAG"
  [id name]
  (->DAG id name {} {}))

(defn add-node
  "Add a node to a DAG"
  [dag node]
  (update dag :nodes assoc (:id node) node))

(defn add-edge
  "Add an edge to a DAG"
  [dag edge]
  (update dag :edges assoc (:id edge) edge))

(defn get-node
  "Get a node by ID"
  [dag node-id]
  (get (:nodes dag) node-id))

(defn get-predecessors
  "Get all predecessor nodes for a node"
  [dag node-id]
  (let [edges (:edges dag)]
    (map (fn [[_ edge]]
           (get-node dag (:source edge)))
         (filter (fn [[_ edge]]
                   (= (:target edge) node-id))
                 edges))))

(defn get-successors
  "Get all successor nodes for a node"
  [dag node-id]
  (let [edges (:edges dag)]
    (map (fn [[_ edge]]
           (get-node dag (:target edge)))
         (filter (fn [[_ edge]]
                   (= (:source edge) node-id))
                 edges))))

;; =============================================================================
;; DAG VALIDATION
;; =============================================================================

(defn has-cycle?
  "Check if DAG has cycles using DFS"
  [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        visited (atom #{})
        rec-stack (atom #{})]
    
    (letfn [(dfs [node-id]
              (when (contains? @rec-stack node-id)
                (throw (ex-info "Cycle detected" {:cycle-node node-id})))
              
              (when-not (contains? @visited node-id)
                (swap! visited conj node-id)
                (swap! rec-stack conj node-id)
                
                (doseq [[_ edge] edges
                        :when (= (:source edge) node-id)]
                  (dfs (:target edge)))
                
                (swap! rec-stack disj node-id)))]
      
      (try
        (doseq [node-id (keys nodes)]
          (when-not (contains? @visited node-id)
            (dfs node-id)))
        false
        (catch Exception e
          true)))))

(defn validate-dag
  "Validate DAG structure"
  [dag]
  (let [errors (atom [])]
    
    ;; Check for cycles
    (when (has-cycle? dag)
      (swap! errors conj "DAG contains cycles"))
    
    ;; Check for orphaned edges
    (doseq [[edge-id edge] (:edges dag)]
      (when-not (contains? (:nodes dag) (:source edge))
        (swap! errors conj (str "Edge " edge-id " references non-existent source node " (:source edge))))
      (when-not (contains? (:nodes dag) (:target edge))
        (swap! errors conj (str "Edge " edge-id " references non-existent target node " (:target edge)))))
    
    {:valid (empty? @errors)
     :errors @errors}))

;; =============================================================================
;; DAG EXECUTION ENGINE
;; =============================================================================

(defn get-execution-order
  "Get topological sort of nodes for execution"
  [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        in-degree (atom {})
        queue (atom [])
        result (atom [])]
    
    ;; Initialize in-degree for all nodes
    (doseq [node-id (keys nodes)]
      (swap! in-degree assoc node-id 0))
    
    ;; Calculate in-degree for each node
    (doseq [[_ edge] edges]
      (swap! in-degree update (:target edge) inc))
    
    ;; Add nodes with in-degree 0 to queue
    (doseq [[node-id degree] @in-degree]
      (when (zero? degree)
        (swap! queue conj node-id)))
    
    ;; Process queue
    (while (seq @queue)
      (let [current (first @queue)]
        (swap! queue rest)
        (swap! result conj current)
        
        ;; Update in-degree for successors
        (doseq [[_ edge] edges
                :when (= (:source edge) current)]
          (let [successor (:target edge)]
            (swap! in-degree update successor dec)
            (when (zero? (get @in-degree successor))
              (swap! queue conj successor)))))
    
    @result))

(defn execute-dag
  "Execute DAG with dependency resolution"
  [dag initial-data & {:keys [parallel?] :or {parallel? false}}]
  (let [validation (validate-dag dag)]
    (if-not (:valid validation)
      (throw (ex-info "Invalid DAG" {:errors (:errors validation)}))
      
      (let [execution-order (get-execution-order dag)
            results (atom {})
            errors (atom {})]
        
        (if parallel?
          ;; Parallel execution
          (let [execution-channels (atom {})
                completed (atom #{})]
            
            (doseq [node-id execution-order]
              (let [node (get-node dag node-id)
                    predecessors (get-predecessors dag node-id)
                    pred-results (select-keys @results (map :id predecessors))
                    node-context (merge initial-data pred-results)]
                
                (when (every? #(contains? @completed (:id %)) predecessors)
                  (let [ch (chan)]
                    (swap! execution-channels assoc node-id ch)
                    (go
                      (try
                        (let [result ((:execute-fn node) node-context)]
                          (>! ch {:node-id node-id :result result :success true}))
                        (catch Exception e
                          (>! ch {:node-id node-id :error e :success false}))))))))
            
            ;; Collect results
            (doseq [node-id execution-order]
              (when-let [ch (get @execution-channels node-id)]
                (let [result (<!! ch)]
                  (if (:success result)
                    (swap! results assoc node-id (:result result))
                    (swap! errors assoc node-id (:error result)))
                  (swap! completed conj node-id)))))
          
          ;; Sequential execution
          (doseq [node-id execution-order]
            (let [node (get-node dag node-id)
                  predecessors (get-predecessors dag node-id)
                  pred-results (select-keys @results (map :id predecessors))
                  node-context (merge initial-data pred-results)]
              
              (try
                (let [result ((:execute-fn node) node-context)]
                  (swap! results assoc node-id result))
                (catch Exception e
                  (swap! errors assoc node-id e))))))
        
        {:dag dag
         :execution-order execution-order
         :results @results
         :errors @errors
         :success (empty? @errors)}))))

;; =============================================================================
;; DAG ANALYSIS
;; =============================================================================

(defn analyze-dag
  "Analyze DAG structure and properties"
  [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        node-count (count nodes)
        edge-count (count edges)
        
        ;; Calculate node degrees
        in-degrees (reduce (fn [acc [_ edge]]
                             (update acc (:target edge) (fnil inc 0)))
                           {} edges)
        out-degrees (reduce (fn [acc [_ edge]]
                              (update acc (:source edge) (fnil inc 0)))
                            {} edges)
        
        ;; Find root and leaf nodes
        root-nodes (filter (fn [node-id]
                             (zero? (get in-degrees node-id 0)))
                           (keys nodes))
        leaf-nodes (filter (fn [node-id]
                             (zero? (get out-degrees node-id 0)))
                           (keys nodes))]
    
    {:node-count node-count
     :edge-count edge-count
     :root-nodes root-nodes
     :leaf-nodes leaf-nodes
     :in-degrees in-degrees
     :out-degrees out-degrees
     :has-cycles (has-cycle? dag)}))

(defn dag-to-dot
  "Convert DAG to Graphviz DOT format"
  [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)]
    
    (str "digraph " (:id dag) " {\n"
         "  label=\"" (:name dag) "\";\n"
         "  rankdir=TB;\n"
         "  node [shape=box, style=filled, fillcolor=lightblue];\n"
         "  edge [color=gray];\n\n"
         
         ;; Nodes
         (str/join "\n" (map (fn [[node-id node]]
                               (str "  " node-id " [label=\"" (:type node) "\"];"))
                             nodes))
         "\n\n"
         
         ;; Edges
         (str/join "\n" (map (fn [[edge-id edge]]
                               (str "  " (:source edge) " -> " (:target edge) ";"))
                             edges))
         "\n}")))

;; =============================================================================
;; FINANCIAL DAG WORKFLOWS
;; =============================================================================

(defn create-financial-dag
  "Create a complete financial DAG"
  []
  (let [dag (create-dag "financial-trading-dag" "Financial Trading DAG")
        
        ;; Create nodes
        market-data-node (create-dag-node
                          "market-data-collector"
                          :data-collector
                          {:symbols ["AAPL" "GOOGL" "MSFT"]}
                          (fn [context]
                            (let [symbols (get-in context [:data :symbols] ["AAPL" "GOOGL" "MSFT"])]
                              (zipmap symbols (map (fn [sym] {:price (+ 100 (rand 100)) :volume (rand 1000000)}) symbols)))))
        
        price-processor-node (create-dag-node
                              "price-data-processor"
                              :data-processor
                              {:normalize true}
                              (fn [context]
                                (let [market-data (get context :market-data-collector)]
                                  (into {} (map (fn [[symbol data]]
                                                  [symbol (assoc data :normalized-price (/ (:price data) 200))])
                                                market-data)))))
        
        rsi-calculator-node (create-dag-node
                             "rsi-calculator"
                             :technical-indicator
                             {:period 14}
                             (fn [context]
                               (let [processed-data (get context :price-data-processor)]
                                 (into {} (map (fn [[symbol data]]
                                                 [symbol (assoc data :rsi (+ 20 (rand 60)))])
                                               processed-data)))))
        
        signal-generator-node (create-dag-node
                               "signal-generator"
                               :signal-generator
                               {:strategy :rsi-based}
                               (fn [context]
                                 (let [rsi-data (get context :rsi-calculator)]
                                   (into {} (map (fn [[symbol _]]
                                                   [symbol {:signal (rand-nth [:buy :sell :hold])
                                                           :confidence (+ 0.5 (rand 0.5))}])
                                                 rsi-data)))))
        
        portfolio-analyzer-node (create-dag-node
                                 "portfolio-analyzer"
                                 :portfolio-analyzer
                                 {:portfolio {"AAPL" 100 "GOOGL" 50 "MSFT" 75}}
                                 (fn [context]
                                   (let [signals (get context :signal-generator)
                                         portfolio (get-in context [:data :portfolio] {"AAPL" 100 "GOOGL" 50 "MSFT" 75})]
                                     {:portfolio-value (hof/calculate-portfolio-value portfolio)
                                      :signals signals
                                      :recommendations (into {} (map (fn [[symbol signal]]
                                                                      [symbol (if (= (:signal signal) :buy) :increase :hold)])
                                                                    signals))})))
        
        decision-engine-node (create-dag-node
                              "decision-engine"
                              :decision-engine
                              {:risk-tolerance :moderate}
                              (fn [context]
                                (let [portfolio-analysis (get context :portfolio-analyzer)]
                                  {:decision (if (> (rand) 0.5) :execute :wait)
                                   :confidence (rand)
                                   :reasoning "Analysis complete"})))
        
        ;; Create edges
        edge1 (create-dag-edge "e1" "market-data-collector" "price-data-processor")
        edge2 (create-dag-edge "e2" "price-data-processor" "rsi-calculator")
        edge3 (create-dag-edge "e3" "rsi-calculator" "signal-generator")
        edge4 (create-dag-edge "e4" "signal-generator" "portfolio-analyzer")
        edge5 (create-dag-edge "e5" "portfolio-analyzer" "decision-engine")]
    
    (-> dag
        (add-node market-data-node)
        (add-node price-processor-node)
        (add-node rsi-calculator-node)
        (add-node signal-generator-node)
        (add-node portfolio-analyzer-node)
        (add-node decision-engine-node)
        (add-edge edge1)
        (add-edge edge2)
        (add-edge edge3)
        (add-edge edge4)
        (add-edge edge5))))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-dag-construction
  "Demonstrate DAG construction"
  []
  (println "=== DAG Construction Demo ===")
  
  (let [dag (create-dag "demo-dag" "Demo DAG")
        node1 (create-dag-node "node1" :input {:data "input data"} (fn [ctx] "processed input"))
        node2 (create-dag-node "node2" :processor {:operation "process"} (fn [ctx] "processed data"))
        node3 (create-dag-node "node3" :output {:format "result"} (fn [ctx] "final result"))
        edge1 (create-dag-edge "edge1" "node1" "node2")
        edge2 (create-dag-edge "edge2" "node2" "node3")]
    
    (println "1. Creating DAG with nodes and edges:")
    (let [dag-complete (-> dag
                           (add-node node1)
                           (add-node node2)
                           (add-node node3)
                           (add-edge edge1)
                           (add-edge edge2))]
      (println "   DAG created:" dag-complete)
      (println "   Nodes:" (keys (:nodes dag-complete)))
      (println "   Edges:" (keys (:edges dag-complete))))
    
    (println "2. DAG validation:")
    (let [validation (validate-dag (-> dag
                                       (add-node node1)
                                       (add-node node2)
                                       (add-node node3)
                                       (add-edge edge1)
                                       (add-edge edge2)))]
      (println "   Valid:" (:valid validation))
      (if (seq (:errors validation))
        (println "   Errors:" (:errors validation))
        (println "   No errors found")))))

(defn demo-dag-execution
  "Demonstrate DAG execution"
  []
  (println "=== DAG Execution Demo ===")
  
  (let [dag (create-dag "execution-dag" "Execution Demo DAG")
        node1 (create-dag-node "input" :input {:value 10} (fn [ctx] (* 2 (:value ctx))))
        node2 (create-dag-node "process" :processor {:multiplier 3} (fn [ctx] (* (:input ctx) (:multiplier ctx))))
        node3 (create-dag-node "output" :output {:format "final"} (fn [ctx] (str "Result: " (:process ctx))))
        edge1 (create-dag-edge "e1" "input" "process")
        edge2 (create-dag-edge "e2" "process" "output")
        dag-complete (-> dag
                         (add-node node1)
                         (add-node node2)
                         (add-node node3)
                         (add-edge edge1)
                         (add-edge edge2))
        initial-data {:value 10 :multiplier 3}]
    
    (println "1. Sequential execution:")
    (let [result (execute-dag dag-complete initial-data :parallel? false)]
      (println "   Execution order:" (:execution-order result))
      (println "   Results:" (:results result))
      (println "   Success:" (:success result)))
    
    (println "2. Parallel execution:")
    (let [result (execute-dag dag-complete initial-data :parallel? true)]
      (println "   Execution order:" (:execution-order result))
      (println "   Results:" (:results result))
      (println "   Success:" (:success result)))))

(defn demo-dag-analysis
  "Demonstrate DAG analysis"
  []
  (println "=== DAG Analysis Demo ===")
  
  (let [dag (create-financial-dag)
        analysis (analyze-dag dag)]
    
    (println "1. DAG Analysis:")
    (println "   Node count:" (:node-count analysis))
    (println "   Edge count:" (:edge-count analysis))
    (println "   Root nodes:" (:root-nodes analysis))
    (println "   Leaf nodes:" (:leaf-nodes analysis))
    (println "   Has cycles:" (:has-cycles analysis))
    
    (println "2. DAG Visualization (DOT format):")
    (println (dag-to-dot dag))))

(defn demo-financial-dag
  "Demonstrate financial DAG execution"
  []
  (println "=== Financial DAG Demo ===")
  
  (let [dag (create-financial-dag)
        initial-data {:portfolio {"AAPL" 100 "GOOGL" 50 "MSFT" 75}}]
    
    (println "1. Financial DAG execution:")
    (let [result (execute-dag dag initial-data :parallel? true)]
      (println "   Execution order:" (:execution-order result))
      (println "   Success:" (:success result))
      
      (when (:success result)
        (println "   Market data collected:" (keys (get-in result [:results :market-data-collector])))
        (println "   Signals generated:" (keys (get-in result [:results :signal-generator])))
        (println "   Portfolio analysis:" (get-in result [:results :portfolio-analyzer]))
        (println "   Final decision:" (get-in result [:results :decision-engine]))))
    
    (println "2. DAG structure:")
    (let [analysis (analyze-dag dag)]
      (println "   Nodes:" (:node-count analysis))
      (println "   Edges:" (:edge-count analysis))
      (println "   Root nodes:" (:root-nodes analysis))
      (println "   Leaf nodes:" (:leaf-nodes analysis)))))

(defn run-all-simple-dag-demos
  "Run all simple DAG demonstrations"
  []
  (println "🎯 === ACTORS Simple DAG System Comprehensive Demo ===")
  (println)
  (demo-dag-construction)
  (println)
  (demo-dag-execution)
  (println)
  (demo-dag-analysis)
  (println)
  (demo-financial-dag)
  (println)
  (println "🎉 === All Simple DAG Demos Complete ==="))

(defn -main
  "Main entry point for simple DAG system demo"
  [& args]
  (run-all-simple-dag-demos))
