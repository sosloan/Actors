(ns actors.basic-dag-system
  "Basic Directed Acyclic Graph (DAG) System for ACTORS"
  (:require [clojure.string :as str]))

;; Basic DAG structures
(defrecord DAGNode [id type data execute-fn])
(defrecord DAGEdge [id source target])
(defrecord DAG [id name nodes edges])

;; DAG construction functions
(defn create-dag-node [id type data execute-fn]
  (->DAGNode id type data execute-fn))

(defn create-dag-edge [id source target]
  (->DAGEdge id source target))

(defn create-dag [id name]
  (->DAG id name {} {}))

(defn add-node [dag node]
  (update dag :nodes assoc (:id node) node))

(defn add-edge [dag edge]
  (update dag :edges assoc (:id edge) edge))

(defn get-node [dag node-id]
  (get (:nodes dag) node-id))

;; DAG validation
(defn has-cycle? [dag]
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

(defn validate-dag [dag]
  (let [errors (atom [])]
    
    (when (has-cycle? dag)
      (swap! errors conj "DAG contains cycles"))
    
    (doseq [[edge-id edge] (:edges dag)]
      (when-not (contains? (:nodes dag) (:source edge))
        (swap! errors conj (str "Edge " edge-id " references non-existent source node " (:source edge))))
      (when-not (contains? (:nodes dag) (:target edge))
        (swap! errors conj (str "Edge " edge-id " references non-existent target node " (:target edge)))))
    
    {:valid (empty? @errors)
     :errors @errors}))

;; DAG execution
(defn get-execution-order [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        in-degree (atom {})
        queue (atom [])
        result (atom [])]
    
    (doseq [node-id (keys nodes)]
      (swap! in-degree assoc node-id 0))
    
    (doseq [[_ edge] edges]
      (swap! in-degree update (:target edge) inc))
    
    (doseq [[node-id degree] @in-degree]
      (when (zero? degree)
        (swap! queue conj node-id)))
    
    (while (seq @queue)
      (let [current (first @queue)]
        (swap! queue rest)
        (swap! result conj current)
        
        (doseq [[_ edge] edges
                :when (= (:source edge) current)]
          (let [successor (:target edge)]
            (swap! in-degree update successor dec)
            (when (zero? (get @in-degree successor))
              (swap! queue conj successor)))))
    
    @result))

(defn get-predecessors [dag node-id]
  (let [edges (:edges dag)]
    (map (fn [[_ edge]]
           (get-node dag (:source edge)))
         (filter (fn [[_ edge]]
                   (= (:target edge) node-id))
                 edges))))

(defn execute-dag [dag initial-data]
  (let [validation (validate-dag dag)]
    (if-not (:valid validation)
      (throw (ex-info "Invalid DAG" {:errors (:errors validation)}))
      
      (let [execution-order (get-execution-order dag)
            results (atom {})
            errors (atom {})]
        
        (doseq [node-id execution-order]
          (let [node (get-node dag node-id)
                predecessors (get-predecessors dag node-id)
                pred-results (select-keys @results (map :id predecessors))
                node-context (merge initial-data pred-results)]
            
            (try
              (let [result ((:execute-fn node) node-context)]
                (swap! results assoc node-id result))
              (catch Exception e
                (swap! errors assoc node-id e)))))
        
        {:dag dag
         :execution-order execution-order
         :results @results
         :errors @errors
         :success (empty? @errors)}))))

;; DAG analysis
(defn analyze-dag [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)
        node-count (count nodes)
        edge-count (count edges)
        
        in-degrees (reduce (fn [acc [_ edge]]
                             (update acc (:target edge) (fnil inc 0)))
                           {} edges)
        out-degrees (reduce (fn [acc [_ edge]]
                              (update acc (:source edge) (fnil inc 0)))
                            {} edges)
        
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

(defn dag-to-dot [dag]
  (let [nodes (:nodes dag)
        edges (:edges dag)]
    
    (str "digraph " (:id dag) " {\n"
         "  label=\"" (:name dag) "\";\n"
         "  rankdir=TB;\n"
         "  node [shape=box, style=filled, fillcolor=lightblue];\n"
         "  edge [color=gray];\n\n"
         
         (str/join "\n" (map (fn [[node-id node]]
                               (str "  " node-id " [label=\"" (:type node) "\"];"))
                             nodes))
         "\n\n"
         
         (str/join "\n" (map (fn [[edge-id edge]]
                               (str "  " (:source edge) " -> " (:target edge) ";"))
                             edges))
         "\n}")))

;; Demo functions
(defn demo-dag-construction []
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

(defn demo-dag-execution []
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
    (let [result (execute-dag dag-complete initial-data)]
      (println "   Execution order:" (:execution-order result))
      (println "   Results:" (:results result))
      (println "   Success:" (:success result)))))

(defn demo-dag-analysis []
  (println "=== DAG Analysis Demo ===")
  
  (let [dag (create-dag "analysis-dag" "Analysis Demo DAG")
        node1 (create-dag-node "input" :input {} (fn [ctx] "input"))
        node2 (create-dag-node "process1" :processor {} (fn [ctx] "process1"))
        node3 (create-dag-node "process2" :processor {} (fn [ctx] "process2"))
        node4 (create-dag-node "output" :output {} (fn [ctx] "output"))
        edge1 (create-dag-edge "e1" "input" "process1")
        edge2 (create-dag-edge "e2" "input" "process2")
        edge3 (create-dag-edge "e3" "process1" "output")
        edge4 (create-dag-edge "e4" "process2" "output")
        dag-complete (-> dag
                         (add-node node1)
                         (add-node node2)
                         (add-node node3)
                         (add-node node4)
                         (add-edge edge1)
                         (add-edge edge2)
                         (add-edge edge3)
                         (add-edge edge4))
        analysis (analyze-dag dag-complete)]
    
    (println "1. DAG Analysis:")
    (println "   Node count:" (:node-count analysis))
    (println "   Edge count:" (:edge-count analysis))
    (println "   Root nodes:" (:root-nodes analysis))
    (println "   Leaf nodes:" (:leaf-nodes analysis))
    (println "   Has cycles:" (:has-cycles analysis))
    
    (println "2. DAG Visualization (DOT format):")
    (println (dag-to-dot dag-complete))))

(defn run-all-basic-dag-demos []
  (println "🎯 === ACTORS Basic DAG System Comprehensive Demo ===")
  (println)
  (demo-dag-construction)
  (println)
  (demo-dag-execution)
  (println)
  (demo-dag-analysis)
  (println)
  (println "🎉 === All Basic DAG Demos Complete ==="))

(defn -main [& args]
  (run-all-basic-dag-demos))
