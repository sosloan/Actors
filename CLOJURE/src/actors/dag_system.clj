(ns actors.dag-system
  "Directed Acyclic Graph (DAG) System for ACTORS"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.set :as set]
            [clojure.data.json :as json]
            [clojure.math.numeric-tower :as math]
            [actors.simple-higher-order-functions :as hof]
            [actors.advanced-functional-patterns :as afp]
            [actors.working-memoization :as memo]))

;; =============================================================================
;; CORE DAG DATA STRUCTURES
;; =============================================================================

(defprotocol DAGNode
  "Protocol for DAG nodes"
  (node-id [this] "Get node ID")
  (node-type [this] "Get node type")
  (node-data [this] "Get node data")
  (node-metadata [this] "Get node metadata")
  (execute-node [this context] "Execute node with context"))

(defprotocol DAGEdge
  "Protocol for DAG edges"
  (edge-id [this] "Get edge ID")
  (source-node [this] "Get source node ID")
  (target-node [this] "Get target node ID")
  (edge-weight [this] "Get edge weight")
  (edge-metadata [this] "Get edge metadata"))

(defrecord DAGNodeImpl [id type data metadata execute-fn]
  DAGNode
  (node-id [_] id)
  (node-type [_] type)
  (node-data [_] data)
  (node-metadata [_] metadata)
  (execute-node [this context]
    (if execute-fn
      (execute-fn context)
      (throw (ex-info "No execute function defined" {:node-id id})))))

(defrecord DAGEdgeImpl [id source target weight metadata]
  DAGEdge
  (edge-id [_] id)
  (source-node [_] source)
  (target-node [_] target)
  (edge-weight [_] weight)
  (edge-metadata [_] metadata))

(defrecord DAG [id name nodes edges metadata]
  Object
  (toString [this]
    (str "DAG[" id ":" name " nodes:" (count nodes) " edges:" (count edges) "]")))

(defrecord DAGExecutionContext [dag context-data execution-state results errors]
  Object
  (toString [this]
    (str "DAGExecutionContext[" (:id dag) " state:" execution-state " results:" (count results) "]")))

;; =============================================================================
;; DAG CONSTRUCTION AND VALIDATION
;; =============================================================================

(defn create-dag-node
  "Create a DAG node"
  [id type data & {:keys [metadata execute-fn]
                   :or {metadata {} execute-fn nil}}]
  (->DAGNodeImpl id type data metadata execute-fn))

(defn create-dag-edge
  "Create a DAG edge"
  [id source target & {:keys [weight metadata]
                       :or {weight 1.0 metadata {}}}]
  (->DAGEdgeImpl id source target weight metadata))

(defn create-dag
  "Create a DAG"
  [id name & {:keys [metadata]
              :or {metadata {}}}]
  (->DAG id name {} {} metadata))

(defn add-node
  "Add a node to a DAG"
  [dag node]
  (let [node-id (node-id node)]
    (if (contains? (:nodes dag) node-id)
      (throw (ex-info "Node already exists" {:node-id node-id}))
      (update dag :nodes assoc node-id node))))

(defn add-edge
  "Add an edge to a DAG"
  [dag edge]
  (let [edge-id (edge-id edge)
        source (source-node edge)
        target (target-node edge)]
    (cond
      (not (contains? (:nodes dag) source))
      (throw (ex-info "Source node does not exist" {:source source}))
      
      (not (contains? (:nodes dag) target))
      (throw (ex-info "Target node does not exist" {:target target}))
      
      (contains? (:edges dag) edge-id)
      (throw (ex-info "Edge already exists" {:edge-id edge-id}))
      
      :else
      (update dag :edges assoc edge-id edge))))

(defn remove-node
  "Remove a node from a DAG"
  [dag node-id]
  (let [connected-edges (filter (fn [[_ edge]]
                                  (or (= (source-node edge) node-id)
                                      (= (target-node edge) node-id)))
                                (:edges dag))]
    (if (seq connected-edges)
      (throw (ex-info "Cannot remove node with connected edges" 
                      {:node-id node-id :connected-edges (map first connected-edges)}))
      (update dag :nodes dissoc node-id))))

(defn remove-edge
  "Remove an edge from a DAG"
  [dag edge-id]
  (update dag :edges dissoc edge-id))

(defn get-node
  "Get a node by ID"
  [dag node-id]
  (get (:nodes dag) node-id))

(defn get-edge
  "Get an edge by ID"
  [dag edge-id]
  (get (:edges dag) edge-id))

(defn get-incoming-edges
  "Get all incoming edges for a node"
  [dag node-id]
  (filter (fn [[_ edge]]
            (= (target-node edge) node-id))
          (:edges dag)))

(defn get-outgoing-edges
  "Get all outgoing edges for a node"
  [dag node-id]
  (filter (fn [[_ edge]]
            (= (source-node edge) node-id))
          (:edges dag)))

(defn get-predecessors
  "Get all predecessor nodes for a node"
  [dag node-id]
  (map (fn [[_ edge]]
         (get-node dag (source-node edge)))
       (get-incoming-edges dag node-id)))

(defn get-successors
  "Get all successor nodes for a node"
  [dag node-id]
  (map (fn [[_ edge]]
         (get-node dag (target-node edge)))
       (get-outgoing-edges dag node-id)))

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
                        :when (= (source-node edge) node-id)]
                  (dfs (target-node edge)))
                
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
      (when-not (contains? (:nodes dag) (source-node edge))
        (swap! errors conj (str "Edge " edge-id " references non-existent source node " (source-node edge))))
      (when-not (contains? (:nodes dag) (target-node edge))
        (swap! errors conj (str "Edge " edge-id " references non-existent target node " (target-node edge)))))
    
    ;; Check for duplicate node IDs
    (let [node-ids (keys (:nodes dag))
          unique-ids (set node-ids)]
      (when-not (= (count node-ids) (count unique-ids))
        (swap! errors conj "Duplicate node IDs found")))
    
    ;; Check for duplicate edge IDs
    (let [edge-ids (keys (:edges dag))
          unique-ids (set edge-ids)]
      (when-not (= (count edge-ids) (count unique-ids))
        (swap! errors conj "Duplicate edge IDs found")))
    
    {:valid (empty? @errors)
     :errors @errors}))

;; =============================================================================
;; DAG EXECUTION ENGINE
;; =============================================================================

(defn create-execution-context
  "Create DAG execution context"
  [dag initial-data]
  (->DAGExecutionContext dag initial-data :ready {} {}))

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
      (swap! in-degree update (target-node edge) inc))
    
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
                :when (= (source-node edge) current)]
          (let [successor (target-node edge)]
            (swap! in-degree update successor dec)
            (when (zero? (get @in-degree successor))
              (swap! queue conj successor)))))
    
    @result))

(defn execute-dag
  "Execute DAG with dependency resolution"
  [dag initial-data & {:keys [parallel? max-concurrency]
                       :or {parallel? false max-concurrency 4}}]
  (let [validation (validate-dag dag)]
    (if-not (:valid validation)
      (throw (ex-info "Invalid DAG" {:errors (:errors validation)}))
      
      (let [execution-order (get-execution-order dag)
            context (create-execution-context dag initial-data)
            results (atom {})
            errors (atom {})]
        
        (if parallel?
          ;; Parallel execution
          (let [execution-channels (atom {})
                completed (atom #{})]
            
            (doseq [node-id execution-order]
              (let [node (get-node dag node-id)
                    predecessors (get-predecessors dag node-id)
                    pred-results (select-keys @results (map node-id predecessors))
                    node-context (merge initial-data pred-results)]
                
                (when (every? #(contains? @completed %) (map node-id predecessors))
                  (let [ch (chan)]
                    (swap! execution-channels assoc node-id ch)
                    (go
                      (try
                        (let [result (execute-node node node-context)]
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
                  pred-results (select-keys @results (map node-id predecessors))
                  node-context (merge initial-data pred-results)]
              
              (try
                (let [result (execute-node node node-context)]
                  (swap! results assoc node-id result))
                (catch Exception e
                  (swap! errors assoc node-id e))))))
        
        {:dag dag
         :execution-order execution-order
         :results @results
         :errors @errors
         :success (empty? @errors)}))))

;; =============================================================================
;; DAG VISUALIZATION AND ANALYSIS
;; =============================================================================

(defn dag-to-dot
  "Convert DAG to Graphviz DOT format"
  [dag & {:keys [node-attributes edge-attributes]
          :or {node-attributes {} edge-attributes {}}}]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        node-attrs (fn [node]
                     (let [attrs (merge node-attributes (:metadata node))]
                       (if (seq attrs)
                         (str " [" (str/join ", " (map (fn [[k v]] (str (name k) "=\"" v "\"")) attrs)) "]")
                         "")))
        edge-attrs (fn [edge]
                     (let [attrs (merge edge-attributes (:metadata edge))]
                       (if (seq attrs)
                         (str " [" (str/join ", " (map (fn [[k v]] (str (name k) "=\"" v "\"")) attrs)) "]")
                         "")))]
    
    (str "digraph " (:id dag) " {\n"
         "  label=\"" (:name dag) "\";\n"
         "  rankdir=TB;\n"
         "  node [shape=box, style=filled, fillcolor=lightblue];\n"
         "  edge [color=gray];\n\n"
         
         ;; Nodes
         (str/join "\n" (map (fn [[node-id node]]
                               (str "  " node-id " [label=\"" (:type node) "\"]" (node-attrs node) ";"))
                             nodes))
         "\n\n"
         
         ;; Edges
         (str/join "\n" (map (fn [[edge-id edge]]
                               (str "  " (source-node edge) " -> " (target-node edge) (edge-attrs edge) ";"))
                             edges))
         "\n}")))

(defn analyze-dag
  "Analyze DAG structure and properties"
  [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        node-count (count nodes)
        edge-count (count edges)
        
        ;; Calculate node degrees
        in-degrees (reduce (fn [acc [_ edge]]
                             (update acc (target-node edge) (fnil inc 0)))
                           {} edges)
        out-degrees (reduce (fn [acc [_ edge]]
                              (update acc (source-node edge) (fnil inc 0)))
                            {} edges)
        
        ;; Find root and leaf nodes
        root-nodes (filter (fn [node-id]
                             (zero? (get in-degrees node-id 0)))
                           (keys nodes))
        leaf-nodes (filter (fn [node-id]
                             (zero? (get out-degrees node-id 0)))
                           (keys nodes))
        
        ;; Calculate longest path
        longest-path (let [distances (atom {})
                           queue (atom (map vector root-nodes (repeat 0)))]
                       
                       (doseq [root root-nodes]
                         (swap! distances assoc root 0))
                       
                       (while (seq @queue)
                         (let [[current dist] (first @queue)]
                           (swap! queue rest)
                           
                           (doseq [[_ edge] edges
                                   :when (= (source-node edge) current)]
                             (let [target (target-node edge)
                                   new-dist (+ dist (edge-weight edge))]
                               (when (> new-dist (get @distances target 0))
                                 (swap! distances assoc target new-dist)
                                 (swap! queue conj [target new-dist])))))
                       
                       (if (seq @distances)
                         (apply max (vals @distances))
                         0))]
    
    {:node-count node-count
     :edge-count edge-count
     :root-nodes root-nodes
     :leaf-nodes leaf-nodes
     :in-degrees in-degrees
     :out-degrees out-degrees
     :longest-path longest-path
     :density (/ edge-count (* node-count (dec node-count)))
     :has-cycles (has-cycle? dag)}))

(defn find-critical-path
  "Find critical path in DAG"
  [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        distances (atom {})
        predecessors (atom {})
        queue (atom [])]
    
    ;; Initialize distances
    (doseq [node-id (keys nodes)]
      (swap! distances assoc node-id 0))
    
    ;; Find root nodes
    (let [in-degrees (reduce (fn [acc [_ edge]]
                               (update acc (target-node edge) (fnil inc 0)))
                             {} edges)
          root-nodes (filter (fn [node-id]
                               (zero? (get in-degrees node-id 0)))
                             (keys nodes))]
      
      (doseq [root root-nodes]
        (swap! queue conj root))
      
      ;; Process nodes in topological order
      (while (seq @queue)
        (let [current (first @queue)]
          (swap! queue rest)
          
          (doseq [[_ edge] edges
                  :when (= (source-node edge) current)]
            (let [target (target-node edge)
                  new-dist (+ (get @distances current) (edge-weight edge))]
              (when (> new-dist (get @distances target))
                (swap! distances assoc target new-dist)
                (swap! predecessors assoc target current)
                (swap! queue conj target))))))
    
    ;; Find the node with maximum distance
    (let [max-node (first (apply max-key (fn [[_ dist]] dist) @distances))
          path (loop [node max-node
                      path []]
                 (if node
                   (recur (get @predecessors node) (conj path node))
                   (reverse path)))]
      {:critical-path path
       :total-weight (get @distances max-node)
       :distances @distances})))

;; =============================================================================
;; FINANCIAL DAG WORKFLOWS
;; =============================================================================

(defn create-financial-dag-nodes
  "Create financial DAG nodes"
  []
  (let [nodes [
               ;; Data collection nodes
               (create-dag-node
                "market-data-collector"
                :data-collector
                {:symbols ["AAPL" "GOOGL" "MSFT"]}
                :execute-fn (fn [context]
                              (let [symbols (get-in context [:data :symbols] ["AAPL" "GOOGL" "MSFT"])]
                                (zipmap symbols (map (fn [sym] {:price (+ 100 (rand 100)) :volume (rand 1000000)}) symbols)))))
               
               (create-dag-node
                "price-data-processor"
                :data-processor
                {:normalize true :filter-outliers true}
                :execute-fn (fn [context]
                              (let [market-data (get context :market-data-collector)]
                                (into {} (map (fn [[symbol data]]
                                                [symbol (assoc data :normalized-price (/ (:price data) 200))])
                                              market-data)))))
               
               ;; Technical analysis nodes
               (create-dag-node
                "rsi-calculator"
                :technical-indicator
                {:period 14 :thresholds {:oversold 30 :overbought 70}}
                :execute-fn (fn [context]
                              (let [processed-data (get context :price-data-processor)]
                                (into {} (map (fn [[symbol data]]
                                                [symbol (assoc data :rsi (+ 20 (rand 60)))])
                                              processed-data)))))
               
               (create-dag-node
                "ema-calculator"
                :technical-indicator
                {:period 12 :smoothing 2}
                :execute-fn (fn [context]
                              (let [processed-data (get context :price-data-processor)]
                                (into {} (map (fn [[symbol data]]
                                                [symbol (assoc data :ema (:price data))])
                                              processed-data)))))
               
               ;; Signal generation nodes
               (create-dag-node
                "signal-generator"
                :signal-generator
                {:strategy :rsi-ema-crossover}
                :execute-fn (fn [context]
                              (let [rsi-data (get context :rsi-calculator)
                                    ema-data (get context :ema-calculator)]
                                (into {} (map (fn [[symbol _]]
                                                [symbol {:signal (rand-nth [:buy :sell :hold])
                                                        :confidence (+ 0.5 (rand 0.5))}])
                                              rsi-data)))))
               
               ;; Portfolio analysis nodes
               (create-dag-node
                "portfolio-analyzer"
                :portfolio-analyzer
                {:portfolio {"AAPL" 100 "GOOGL" 50 "MSFT" 75}}
                :execute-fn (fn [context]
                              (let [signals (get context :signal-generator)
                                    portfolio (get-in context [:data :portfolio] {"AAPL" 100 "GOOGL" 50 "MSFT" 75})]
                                {:portfolio-value (hof/calculate-portfolio-value portfolio)
                                 :signals signals
                                 :recommendations (into {} (map (fn [[symbol signal]]
                                                                 [symbol (if (= (:signal signal) :buy) :increase :hold)])
                                                               signals))})))
               
               ;; Risk management nodes
               (create-dag-node
                "risk-calculator"
                :risk-calculator
                {:max-risk 0.05 :var-confidence 0.95}
                :execute-fn (fn [context]
                              (let [portfolio-analysis (get context :portfolio-analyzer)]
                                {:portfolio-risk (Math/sqrt (rand))
                                 :var (rand 1000)
                                 :expected-shortfall (rand 500)})))
               
               ;; Decision engine
               (create-dag-node
                "decision-engine"
                :decision-engine
                {:risk-tolerance :moderate}
                :execute-fn (fn [context]
                              (let [portfolio-analysis (get context :portfolio-analyzer)
                                    risk-analysis (get context :risk-calculator)]
                                {:decision (if (< (:portfolio-risk risk-analysis) 0.03) :execute :wait)
                                 :confidence (rand)
                                 :reasoning "Risk within acceptable limits"})))
               ]]
    
    nodes))

(defn create-financial-dag-edges
  "Create financial DAG edges"
  []
  (let [edges [
               ;; Data flow edges
               (create-dag-edge "e1" "market-data-collector" "price-data-processor" :weight 1.0)
               (create-dag-edge "e2" "price-data-processor" "rsi-calculator" :weight 1.0)
               (create-dag-edge "e3" "price-data-processor" "ema-calculator" :weight 1.0)
               
               ;; Signal generation edges
               (create-dag-edge "e4" "rsi-calculator" "signal-generator" :weight 1.0)
               (create-dag-edge "e5" "ema-calculator" "signal-generator" :weight 1.0)
               
               ;; Portfolio analysis edges
               (create-dag-edge "e6" "signal-generator" "portfolio-analyzer" :weight 1.0)
               
               ;; Risk management edges
               (create-dag-edge "e7" "portfolio-analyzer" "risk-calculator" :weight 1.0)
               
               ;; Decision engine edges
               (create-dag-edge "e8" "portfolio-analyzer" "decision-engine" :weight 1.0)
               (create-dag-edge "e9" "risk-calculator" "decision-engine" :weight 1.0)
               ]]
    
    edges))

(defn create-financial-dag
  "Create a complete financial DAG"
  []
  (let [dag (create-dag "financial-trading-dag" "Financial Trading DAG")
        nodes (create-financial-dag-nodes)
        edges (create-financial-dag-edges)]
    
    (-> dag
        (as-> d (reduce add-node d nodes))
        (as-> d (reduce add-edge d edges)))))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-dag-construction
  "Demonstrate DAG construction"
  []
  (println "=== DAG Construction Demo ===")
  
  (let [dag (create-dag "demo-dag" "Demo DAG")
        node1 (create-dag-node "node1" :input {:data "input data"})
        node2 (create-dag-node "node2" :processor {:operation "process"})
        node3 (create-dag-node "node3" :output {:format "result"})
        edge1 (create-dag-edge "edge1" "node1" "node2")
        edge2 (create-dag-edge "edge2" "node2" "node3")]
    
    (println "1. Creating DAG with nodes and edges:")
    (let [dag-with-nodes (-> dag
                             (add-node node1)
                             (add-node node2)
                             (add-node node3)
                             (add-edge edge1)
                             (add-edge edge2))]
      (println "   DAG created:" dag-with-nodes)
      (println "   Nodes:" (keys (:nodes dag-with-nodes)))
      (println "   Edges:" (keys (:edges dag-with-nodes))))
    
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
        node1 (create-dag-node "input" :input {:value 10}
                               :execute-fn (fn [context] (* 2 (:value context))))
        node2 (create-dag-node "process" :processor {:multiplier 3}
                               :execute-fn (fn [context] (* (:input context) (:multiplier context))))
        node3 (create-dag-node "output" :output {:format "final"}
                               :execute-fn (fn [context] (str "Result: " (:process context))))
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
        analysis (analyze-dag dag)
        critical-path (find-critical-path dag)]
    
    (println "1. DAG Analysis:")
    (println "   Node count:" (:node-count analysis))
    (println "   Edge count:" (:edge-count analysis))
    (println "   Root nodes:" (:root-nodes analysis))
    (println "   Leaf nodes:" (:leaf-nodes analysis))
    (println "   Longest path:" (:longest-path analysis))
    (println "   Density:" (format "%.3f" (:density analysis)))
    (println "   Has cycles:" (:has-cycles analysis))
    
    (println "2. Critical Path Analysis:")
    (println "   Critical path:" (:critical-path critical-path))
    (println "   Total weight:" (:total-weight critical-path))
    
    (println "3. DAG Visualization (DOT format):")
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
        (println "   Risk analysis:" (get-in result [:results :risk-calculator]))
        (println "   Final decision:" (get-in result [:results :decision-engine]))))
    
    (println "2. DAG structure:")
    (let [analysis (analyze-dag dag)]
      (println "   Nodes:" (:node-count analysis))
      (println "   Edges:" (:edge-count analysis))
      (println "   Root nodes:" (:root-nodes analysis))
      (println "   Leaf nodes:" (:leaf-nodes analysis)))))

(defn run-all-dag-demos
  "Run all DAG demonstrations"
  []
  (println "🎯 === ACTORS DAG System Comprehensive Demo ===")
  (println)
  (demo-dag-construction)
  (println)
  (demo-dag-execution)
  (println)
  (demo-dag-analysis)
  (println)
  (demo-financial-dag)
  (println)
  (println "🎉 === All DAG Demos Complete ==="))

(defn -main
  "Main entry point for DAG system demo"
  [& args]
  (run-all-dag-demos))
