(ns actors.system-inventory
  "Complete System Inventory - Symbols, Routes, Actions, and States"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.data.json :as json]
            [clojure.set :as set]
            [clojure.math.numeric-tower :as math]
            [actors.simple-core :as core]
            [actors.simple-procedures :as procedures]
            [actors.grid-state :as grid]
            [actors.kawpow-consciousness :as kawpow]
            [actors.minimal-registers-handlers :as registers]
            [actors.simple-higher-order-functions :as hof]
            [actors.advanced-functional-patterns :as afp]
            [actors.working-memoization :as memo]))

;; =============================================================================
;; SYSTEM INVENTORY COLLECTOR
;; =============================================================================

(defrecord SystemComponent
  [id
   name
   type
   namespace
   description
   dependencies
   metadata])

(defrecord SystemRoute
  [id
   name
   path
   method
   handler
   parameters
   description])

(defrecord SystemAction
  [id
   name
   function
   inputs
   outputs
   side-effects
   description])

(defrecord SystemState
  [id
   name
   type
   initial-value
   current-value
   transitions
   description])

(def ^:private system-inventory (atom {}))
(def ^:private component-registry (atom {}))
(def ^:private route-registry (atom {}))
(def ^:private action-registry (atom {}))
(def ^:private state-registry (atom {}))

;; =============================================================================
;; INVENTORY COLLECTION FUNCTIONS
;; =============================================================================

(defn register-component
  "Register a system component"
  [component]
  (swap! component-registry assoc (:id component) component)
  component)

(defn register-route
  "Register a system route"
  [route]
  (swap! route-registry assoc (:id route) route)
  route)

(defn register-action
  "Register a system action"
  [action]
  (swap! action-registry assoc (:id action) action)
  action)

(defn register-state
  "Register a system state"
  [state]
  (swap! state-registry assoc (:id state) state)
  state)

(defn collect-symbols
  "Collect all symbols from a namespace"
  [namespace-sym]
  (try
    (let [ns-obj (find-ns namespace-sym)]
      (if ns-obj
        (let [publics (ns-publics ns-obj)
              internals (ns-interns ns-obj)]
          {:namespace (str namespace-sym)
           :public-symbols (map (fn [[name var]] 
                                  {:name (str name)
                                   :type (str (:type (meta var)))
                                   :doc (:doc (meta var))
                                   :arglists (:arglists (meta var))})
                                publics)
           :internal-symbols (map (fn [[name var]]
                                    {:name (str name)
                                     :type (str (:type (meta var)))
                                     :doc (:doc (meta var))
                                     :arglists (:arglists (meta var))})
                                  internals)})
        {:namespace (str namespace-sym)
         :error "Namespace not found"}))
    (catch Exception e
      {:namespace (str namespace-sym)
       :error (.getMessage e)})))

(defn collect-all-symbols
  "Collect symbols from all ACTORS namespaces"
  []
  (let [namespaces ['actors.simple-core
                    'actors.simple-procedures
                    'actors.grid-state
                    'actors.kawpow-consciousness
                    'actors.minimal-registers-handlers
                    'actors.simple-higher-order-functions
                    'actors.advanced-functional-patterns
                    'actors.minimal-memoization-data-driven
                    'actors.system-inventory]]
    (into {} (map (fn [ns-sym]
                    [ns-sym (collect-symbols ns-sym)])
                  namespaces))))

;; =============================================================================
;; COMPONENT DEFINITIONS
;; =============================================================================

(defn define-core-components
  "Define core system components"
  []
  (let [components [
                   ;; Core Components
                   (->SystemComponent
                    "core-market-data"
                    "Market Data Component"
                    :data-model
                    "actors.simple-core"
                    "Core market data structure and operations"
                    []
                    {:record-type "MarketData"})
                   
                   (->SystemComponent
                    "core-trading-signal"
                    "Trading Signal Component"
                    :data-model
                    "actors.simple-core"
                    "Core trading signal structure and operations"
                    []
                    {:record-type "TradingSignal"})
                   
                   ;; Procedure Components
                   (->SystemComponent
                    "procedure-protocol"
                    "Procedure Protocol"
                    :protocol
                    "actors.simple-procedures"
                    "Protocol for defining reusable procedures"
                    []
                    {:protocol-name "Procedure"})
                   
                   (->SystemComponent
                    "procedure-result"
                    "Procedure Result"
                    :data-model
                    "actors.simple-procedures"
                    "Result structure for procedure execution"
                    []
                    {:record-type "ProcedureResult"})
                   
                   ;; Grid State Components
                   (->SystemComponent
                    "grid-state-manager"
                    "Grid State Manager"
                    :state-manager
                    "actors.grid-state"
                    "Manages immutable grid state operations"
                    []
                    {:grid-operations ["get-cell" "set-cell" "copy-grid"]})
                   
                   ;; KawPow Consciousness Components
                   (->SystemComponent
                    "kawpow-signal-generator"
                    "KawPow Signal Generator"
                    :signal-generator
                    "actors.kawpow-consciousness"
                    "Generates consciousness-based trading signals"
                    []
                    {:algorithm "KawPow" :consciousness-metrics true})
                   
                   (->SystemComponent
                    "highway-101-north"
                    "Highway 101 North Data"
                    :data-model
                    "actors.kawpow-consciousness"
                    "Mathematical consciousness framework data"
                    []
                    {:record-type "Highway101NorthData"})
                   
                   (->SystemComponent
                    "croatian-bowtie"
                    "Croatian Bowtie Data"
                    :data-model
                    "actors.kawpow-consciousness"
                    "Sacred geometry consciousness data"
                    []
                    {:record-type "CroatianBowtieData"})
                   
                   ;; Register and Handler Components
                   (->SystemComponent
                    "event-registry"
                    "Event Registry"
                    :registry
                    "actors.minimal-registers-handlers"
                    "Global event registry for event-driven architecture"
                    []
                    {:registry-type "event"})
                   
                   (->SystemComponent
                    "handler-registry"
                    "Handler Registry"
                    :registry
                    "actors.minimal-registers-handlers"
                    "Global handler registry for event processing"
                    []
                    {:registry-type "handler"})
                   
                   (->SystemComponent
                    "register-registry"
                    "Register Registry"
                    :registry
                    "actors.minimal-registers-handlers"
                    "Global register registry for data storage"
                    []
                    {:registry-type "register"})
                   
                   ;; Higher Order Function Components
                   (->SystemComponent
                    "function-composer"
                    "Function Composer"
                    :composer
                    "actors.simple-higher-order-functions"
                    "Composes functions for complex transformations"
                    []
                    {:composition-types ["compose" "pipe"]})
                   
                   (->SystemComponent
                    "memoizer"
                    "Memoizer"
                    :optimizer
                    "actors.simple-higher-order-functions"
                    "Caches function results for performance"
                    []
                    {:memoization-types ["ttl" "lru"]})
                   
                   ;; Advanced Functional Pattern Components
                   (->SystemComponent
                    "transducer-engine"
                    "Transducer Engine"
                    :processor
                    "actors.advanced-functional-patterns"
                    "Efficient data processing with transducers"
                    []
                    {:processing-type "transducer"})
                   
                   (->SystemComponent
                    "lens-system"
                    "Lens System"
                    :manipulator
                    "actors.advanced-functional-patterns"
                    "Functional nested data manipulation"
                    []
                    {:manipulation-type "lens"})
                   
                   ;; Memoization and Data-Driven Components
                   (->SystemComponent
                    "data-flow-engine"
                    "Data Flow Engine"
                    :processor
                    "actors.minimal-memoization-data-driven"
                    "Executes data-driven function compositions"
                    []
                    {:flow-type "data-driven"})
                   
                   (->SystemComponent
                    "intelligent-cache"
                    "Intelligent Cache"
                    :cache
                    "actors.minimal-memoization-data-driven"
                    "Intelligent caching with multiple strategies"
                    []
                    {:cache-strategies ["lru" "ttl" "size-based"]})
                   ]]
    
    (doseq [component components]
      (register-component component))
    
    components))

;; =============================================================================
;; ROUTE DEFINITIONS
;; =============================================================================

(defn define-system-routes
  "Define system routes for API access"
  []
  (let [routes [
                ;; Core Routes
                (->SystemRoute
                 "core-market-data-route"
                 "Market Data Route"
                 "/api/market-data"
                 :GET
                 "get-market-data"
                 {:symbol "string" :required true}
                 "Get market data for a symbol")
                
                (->SystemRoute
                 "core-trading-signal-route"
                 "Trading Signal Route"
                 "/api/trading-signal"
                 :POST
                 "create-trading-signal"
                 {:type "string" :confidence "number" :data "object"}
                 "Create a new trading signal")
                
                ;; Procedure Routes
                (->SystemRoute
                 "procedure-execute-route"
                 "Execute Procedure Route"
                 "/api/procedure/execute"
                 :POST
                 "execute-procedure"
                 {:procedure-id "string" :parameters "object"}
                 "Execute a procedure with parameters")
                
                (->SystemRoute
                 "procedure-list-route"
                 "List Procedures Route"
                 "/api/procedures"
                 :GET
                 "list-procedures"
                 {}
                 "List all available procedures")
                
                ;; Grid State Routes
                (->SystemRoute
                 "grid-state-route"
                 "Grid State Route"
                 "/api/grid-state"
                 :GET
                 "get-grid-state"
                 {:grid-id "string"}
                 "Get current grid state")
                
                (->SystemRoute
                 "grid-update-route"
                 "Grid Update Route"
                 "/api/grid-state/update"
                 :PUT
                 "update-grid-state"
                 {:grid-id "string" :operations "array"}
                 "Update grid state with operations")
                
                ;; KawPow Consciousness Routes
                (->SystemRoute
                 "kawpow-signal-route"
                 "KawPow Signal Route"
                 "/api/kawpow/signal"
                 :POST
                 "generate-kawpow-signal"
                 {:symbol "string" :consciousness-level "number"}
                 "Generate KawPow consciousness signal")
                
                (->SystemRoute
                 "kawpow-session-route"
                 "KawPow Session Route"
                 "/api/kawpow/session"
                 :GET
                 "get-kawpow-session"
                 {:session-id "string"}
                 "Get KawPow session data")
                
                ;; Register and Handler Routes
                (->SystemRoute
                 "event-emit-route"
                 "Emit Event Route"
                 "/api/events/emit"
                 :POST
                 "emit-event"
                 {:type "string" :data "object" :source "string"}
                 "Emit an event to the system")
                
                (->SystemRoute
                 "register-update-route"
                 "Update Register Route"
                 "/api/registers/update"
                 :PUT
                 "update-register"
                 {:register-id "string" :data "object"}
                 "Update register data")
                
                ;; Higher Order Function Routes
                (->SystemRoute
                 "function-compose-route"
                 "Compose Functions Route"
                 "/api/functions/compose"
                 :POST
                 "compose-functions"
                 {:functions "array" :composition-type "string"}
                 "Compose multiple functions")
                
                (->SystemRoute
                 "memoize-function-route"
                 "Memoize Function Route"
                 "/api/functions/memoize"
                 :POST
                 "memoize-function"
                 {:function-id "string" :strategy "string" :ttl "number"}
                 "Memoize a function with strategy")
                
                ;; Advanced Functional Pattern Routes
                (->SystemRoute
                 "transducer-process-route"
                 "Process with Transducer Route"
                 "/api/transducers/process"
                 :POST
                 "process-with-transducer"
                 {:data "array" :transducer-id "string"}
                 "Process data with transducer")
                
                (->SystemRoute
                 "lens-manipulate-route"
                 "Manipulate with Lens Route"
                 "/api/lenses/manipulate"
                 :POST
                 "manipulate-with-lens"
                 {:data "object" :lens-id "string" :operation "string"}
                 "Manipulate data with lens")
                
                ;; Memoization and Data-Driven Routes
                (->SystemRoute
                 "dataflow-execute-route"
                 "Execute Data Flow Route"
                 "/api/dataflows/execute"
                 :POST
                 "execute-dataflow"
                 {:dataflow-id "string" :input-data "object"}
                 "Execute a data flow")
                
                (->SystemRoute
                 "cache-operations-route"
                 "Cache Operations Route"
                 "/api/cache"
                 :GET
                 "cache-operations"
                 {:operation "string" :key "string"}
                 "Perform cache operations")
                ]]
    
    (doseq [route routes]
      (register-route route))
    
    routes))

;; =============================================================================
;; ACTION DEFINITIONS
;; =============================================================================

(defn define-system-actions
  "Define system actions"
  []
  (let [actions [
                 ;; Core Actions
                 (->SystemAction
                  "create-market-data"
                  "Create Market Data"
                  "actors.simple-core/create-market-data"
                  [:symbol :price :volume :volatility]
                  [:market-data]
                  [:database-write]
                  "Create new market data record")
                 
                 (->SystemAction
                  "create-trading-signal"
                  "Create Trading Signal"
                  "actors.simple-core/create-trading-signal"
                  [:type :confidence :data]
                  [:trading-signal]
                  [:signal-broadcast]
                  "Create new trading signal")
                 
                 ;; Procedure Actions
                 (->SystemAction
                  "execute-procedure"
                  "Execute Procedure"
                  "actors.simple-procedures/execute-procedure"
                  [:procedure-id :parameters]
                  [:result]
                  [:procedure-execution]
                  "Execute a procedure with parameters")
                 
                 (->SystemAction
                  "create-procedure-workflow"
                  "Create Procedure Workflow"
                  "actors.simple-procedures/create-procedure-workflow"
                  [:steps :context]
                  [:workflow]
                  [:workflow-creation]
                  "Create a procedure workflow")
                 
                 ;; Grid State Actions
                 (->SystemAction
                  "get-grid-cell"
                  "Get Grid Cell"
                  "actors.grid-state/get-cell"
                  [:grid :row :col]
                  [:cell-value]
                  []
                  "Get value from grid cell")
                 
                 (->SystemAction
                  "set-grid-cell"
                  "Set Grid Cell"
                  "actors.grid-state/set-cell"
                  [:grid :row :col :value]
                  [:updated-grid]
                  [:grid-mutation]
                  "Set value in grid cell")
                 
                 (->SystemAction
                  "copy-grid-in-place"
                  "Copy Grid In Place"
                  "actors.grid-state/copy-grid-in-place"
                  [:grid :operations]
                  [:copied-grid]
                  [:grid-copy]
                  "Copy grid data in place")
                 
                 ;; KawPow Consciousness Actions
                 (->SystemAction
                  "generate-kawpow-signal"
                  "Generate KawPow Signal"
                  "actors.kawpow-consciousness/generate-signal"
                  [:symbol :highway-data :bowtie-data :config]
                  [:kawpow-signal]
                  [:consciousness-calculation]
                  "Generate KawPow consciousness signal")
                 
                 (->SystemAction
                  "calculate-consciousness-metrics"
                  "Calculate Consciousness Metrics"
                  "actors.kawpow-consciousness/calculate-consciousness-metrics"
                  [:highway-data :bowtie-data]
                  [:consciousness-metrics]
                  [:metrics-calculation]
                  "Calculate consciousness metrics")
                 
                 ;; Register and Handler Actions
                 (->SystemAction
                  "emit-event"
                  "Emit Event"
                  "actors.minimal-registers-handlers/emit-event"
                  [:event]
                  [:event-id]
                  [:event-broadcast]
                  "Emit event to system")
                 
                 (->SystemAction
                  "register-handler"
                  "Register Handler"
                  "actors.minimal-registers-handlers/register-handler"
                  [:handler]
                  [:handler-id]
                  [:handler-registration]
                  "Register event handler")
                 
                 (->SystemAction
                  "update-register-data"
                  "Update Register Data"
                  "actors.minimal-registers-handlers/update-register-data"
                  [:register-id :update-fn :args]
                  [:updated-register]
                  [:register-update]
                  "Update register data")
                 
                 ;; Higher Order Function Actions
                 (->SystemAction
                  "compose-functions"
                  "Compose Functions"
                  "actors.simple-higher-order-functions/compose"
                  [:functions]
                  [:composed-function]
                  []
                  "Compose multiple functions")
                 
                 (->SystemAction
                  "pipe-functions"
                  "Pipe Functions"
                  "actors.simple-higher-order-functions/pipe"
                  [:functions]
                  [:piped-function]
                  []
                  "Pipe multiple functions")
                 
                 (->SystemAction
                  "memoize-function"
                  "Memoize Function"
                  "actors.simple-higher-order-functions/memoize-with-ttl"
                  [:function :ttl-ms]
                  [:memoized-function]
                  [:cache-creation]
                  "Memoize function with TTL")
                 
                 ;; Advanced Functional Pattern Actions
                 (->SystemAction
                  "process-with-transducer"
                  "Process with Transducer"
                  "actors.advanced-functional-patterns/process-with-transducer"
                  [:transducer :data]
                  [:processed-data]
                  [:data-processing]
                  "Process data with transducer")
                 
                 (->SystemAction
                  "manipulate-with-lens"
                  "Manipulate with Lens"
                  "actors.advanced-functional-patterns/update-lens"
                  [:lens :data :value]
                  [:manipulated-data]
                  [:data-manipulation]
                  "Manipulate data with lens")
                 
                 ;; Memoization and Data-Driven Actions
                 (->SystemAction
                  "execute-dataflow"
                  "Execute Data Flow"
                  "actors.minimal-memoization-data-driven/execute-dataflow"
                  [:dataflow-id :input-data]
                  [:flow-result]
                  [:dataflow-execution]
                  "Execute data flow")
                 
                 (->SystemAction
                  "cache-put"
                  "Cache Put"
                  "actors.minimal-memoization-data-driven/cache-put"
                  [:cache-manager :key :value :options]
                  [:cache-entry]
                  [:cache-write]
                  "Put value in cache")
                 
                 (->SystemAction
                  "cache-get"
                  "Cache Get"
                  "actors.minimal-memoization-data-driven/cache-get"
                  [:cache-manager :key]
                  [:cached-value]
                  [:cache-read]
                  "Get value from cache")
                 ]]
    
    (doseq [action actions]
      (register-action action))
    
    actions))

;; =============================================================================
;; STATE DEFINITIONS
;; =============================================================================

(defn define-system-states
  "Define system states"
  []
  (let [states [
                ;; Core States
                (->SystemState
                 "market-data-state"
                 "Market Data State"
                 :data-state
                 {}
                 {}
                 [:create :update :delete :query]
                 "Global market data state")
                
                (->SystemState
                 "trading-signal-state"
                 "Trading Signal State"
                 :signal-state
                 []
                 []
                 [:generate :process :execute :archive]
                 "Global trading signal state")
                
                ;; Procedure States
                (->SystemState
                 "procedure-registry-state"
                 "Procedure Registry State"
                 :registry-state
                 {}
                 {}
                 [:register :unregister :execute :list]
                 "Registry of all procedures")
                
                (->SystemState
                 "workflow-execution-state"
                 "Workflow Execution State"
                 :execution-state
                 {}
                 {}
                 [:start :step :complete :fail]
                 "Current workflow execution state")
                
                ;; Grid State States
                (->SystemState
                 "grid-state"
                 "Grid State"
                 :grid-state
                 {}
                 {}
                 [:get-cell :set-cell :copy :transform]
                 "Current grid state")
                
                (->SystemState
                 "grid-operations-state"
                 "Grid Operations State"
                 :operations-state
                 []
                 []
                 [:add-operation :execute-operation :clear-operations]
                 "Queue of grid operations")
                
                ;; KawPow Consciousness States
                (->SystemState
                 "kawpow-session-state"
                 "KawPow Session State"
                 :session-state
                 {}
                 {}
                 [:start-session :generate-signal :update-metrics :end-session]
                 "Current KawPow consciousness session")
                
                (->SystemState
                 "consciousness-metrics-state"
                 "Consciousness Metrics State"
                 :metrics-state
                 {}
                 {}
                 [:calculate :update :reset :query]
                 "Current consciousness metrics")
                
                ;; Register and Handler States
                (->SystemState
                 "event-registry-state"
                 "Event Registry State"
                 :registry-state
                 {}
                 {}
                 [:register-event :emit-event :process-event :cleanup-events]
                 "Global event registry state")
                
                (->SystemState
                 "handler-registry-state"
                 "Handler Registry State"
                 :registry-state
                 {}
                 {}
                 [:register-handler :unregister-handler :execute-handler :list-handlers]
                 "Global handler registry state")
                
                (->SystemState
                 "register-registry-state"
                 "Register Registry State"
                 :registry-state
                 {}
                 {}
                 [:create-register :update-register :get-register :delete-register]
                 "Global register registry state")
                
                ;; Higher Order Function States
                (->SystemState
                 "function-composition-state"
                 "Function Composition State"
                 :composition-state
                 {}
                 {}
                 [:compose :pipe :partial-apply :memoize]
                 "Current function composition state")
                
                (->SystemState
                 "memoization-cache-state"
                 "Memoization Cache State"
                 :cache-state
                 {}
                 {}
                 [:cache-put :cache-get :cache-invalidate :cache-cleanup]
                 "Memoization cache state")
                
                ;; Advanced Functional Pattern States
                (->SystemState
                 "transducer-state"
                 "Transducer State"
                 :processor-state
                 {}
                 {}
                 [:create-transducer :process-data :transform-data :reduce-data]
                 "Current transducer processing state")
                
                (->SystemState
                 "lens-state"
                 "Lens State"
                 :manipulator-state
                 {}
                 {}
                 [:create-lens :get-lens :set-lens :update-lens]
                 "Current lens manipulation state")
                
                ;; Memoization and Data-Driven States
                (->SystemState
                 "dataflow-state"
                 "Data Flow State"
                 :flow-state
                 {}
                 {}
                 [:create-flow :execute-flow :step-flow :complete-flow]
                 "Current data flow execution state")
                
                (->SystemState
                 "intelligent-cache-state"
                 "Intelligent Cache State"
                 :cache-state
                 {}
                 {}
                 [:cache-put :cache-get :cache-invalidate :cache-cleanup :cache-stats]
                 "Intelligent cache state")
                ]]
    
    (doseq [state states]
      (register-state state))
    
    states))

;; =============================================================================
;; INVENTORY COLLECTION
;; =============================================================================

(defn collect-complete-inventory
  "Collect complete system inventory"
  []
  (let [symbols (collect-all-symbols)
        components (define-core-components)
        routes (define-system-routes)
        actions (define-system-actions)
        states (define-system-states)]
    
    {:symbols symbols
     :components components
     :routes routes
     :actions actions
     :states states
     :summary {:total-symbols (reduce + (map #(count (:public-symbols %)) (vals symbols)))
               :total-components (count components)
               :total-routes (count routes)
               :total-actions (count actions)
               :total-states (count states)}}))

;; =============================================================================
;; INVENTORY DISPLAY FUNCTIONS
;; =============================================================================

(defn display-symbols
  "Display all symbols in the system"
  [inventory]
  (println "=== SYSTEM SYMBOLS ===")
  (doseq [[namespace symbols] (:symbols inventory)]
    (println (str "\n📦 " namespace))
    (when (:public-symbols symbols)
      (println "  Public Symbols:")
      (doseq [symbol (:public-symbols symbols)]
        (println (str "    • " (:name symbol) " (" (:type symbol) ")"))
        (when (:doc symbol)
          (println (str "      " (:doc symbol))))))
    (when (:internal-symbols symbols)
      (println "  Internal Symbols:")
      (doseq [symbol (:internal-symbols symbols)]
        (println (str "    • " (:name symbol) " (" (:type symbol) ")"))))))

(defn display-components
  "Display all system components"
  [inventory]
  (println "\n=== SYSTEM COMPONENTS ===")
  (doseq [component (:components inventory)]
    (println (str "\n🔧 " (:name component)))
    (println (str "   ID: " (:id component)))
    (println (str "   Type: " (:type component)))
    (println (str "   Namespace: " (:namespace component)))
    (println (str "   Description: " (:description component)))
    (when (seq (:dependencies component))
      (println (str "   Dependencies: " (str/join ", " (:dependencies component)))))
    (when (seq (:metadata component))
      (println (str "   Metadata: " (:metadata component))))))

(defn display-routes
  "Display all system routes"
  [inventory]
  (println "\n=== SYSTEM ROUTES ===")
  (doseq [route (:routes inventory)]
    (println (str "\n🛣️  " (:name route)))
    (println (str "   ID: " (:id route)))
    (println (str "   Path: " (:path route)))
    (println (str "   Method: " (:method route)))
    (println (str "   Handler: " (:handler route)))
    (when (seq (:parameters route))
      (println (str "   Parameters: " (:parameters route))))
    (println (str "   Description: " (:description route)))))

(defn display-actions
  "Display all system actions"
  [inventory]
  (println "\n=== SYSTEM ACTIONS ===")
  (doseq [action (:actions inventory)]
    (println (str "\n⚡ " (:name action)))
    (println (str "   ID: " (:id action)))
    (println (str "   Function: " (:function action)))
    (when (seq (:inputs action))
      (println (str "   Inputs: " (str/join ", " (:inputs action)))))
    (when (seq (:outputs action))
      (println (str "   Outputs: " (str/join ", " (:outputs action)))))
    (when (seq (:side-effects action))
      (println (str "   Side Effects: " (str/join ", " (:side-effects action)))))
    (println (str "   Description: " (:description action)))))

(defn display-states
  "Display all system states"
  [inventory]
  (println "\n=== SYSTEM STATES ===")
  (doseq [state (:states inventory)]
    (println (str "\n🏛️  " (:name state)))
    (println (str "   ID: " (:id state)))
    (println (str "   Type: " (:type state)))
    (println (str "   Initial Value: " (:initial-value state)))
    (println (str "   Current Value: " (:current-value state)))
    (when (seq (:transitions state))
      (println (str "   Transitions: " (str/join ", " (:transitions state)))))
    (println (str "   Description: " (:description state)))))

(defn display-summary
  "Display system inventory summary"
  [inventory]
  (let [summary (:summary inventory)]
    (println "\n=== SYSTEM INVENTORY SUMMARY ===")
    (println (str "📊 Total Symbols: " (:total-symbols summary)))
    (println (str "🔧 Total Components: " (:total-components summary)))
    (println (str "🛣️  Total Routes: " (:total-routes summary)))
    (println (str "⚡ Total Actions: " (:total-actions summary)))
    (println (str "🏛️  Total States: " (:total-states summary)))
    (println (str "\n📈 Total System Elements: " 
                 (+ (:total-symbols summary)
                    (:total-components summary)
                    (:total-routes summary)
                    (:total-actions summary)
                    (:total-states summary))))))

(defn display-complete-inventory
  "Display complete system inventory"
  []
  (let [inventory (collect-complete-inventory)]
    (println "🎯 === ACTORS CLOJURE SYSTEM COMPLETE INVENTORY ===")
    (display-summary inventory)
    (display-symbols inventory)
    (display-components inventory)
    (display-routes inventory)
    (display-actions inventory)
    (display-states inventory)
    (println "\n🎉 === INVENTORY COMPLETE ===")))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-symbol-collection
  "Demonstrate symbol collection"
  []
  (println "=== Symbol Collection Demo ===")
  (let [symbols (collect-all-symbols)]
    (doseq [[namespace symbols] symbols]
      (println (str "\n📦 " namespace))
      (if (:error symbols)
        (println (str "   Error: " (:error symbols)))
        (do
          (println (str "   Public symbols: " (count (:public-symbols symbols))))
          (println (str "   Internal symbols: " (count (:internal-symbols symbols)))))))))

(defn demo-component-registration
  "Demonstrate component registration"
  []
  (println "=== Component Registration Demo ===")
  (let [components (define-core-components)]
    (println (str "Registered " (count components) " components"))
    (doseq [component (take 5 components)]
      (println (str "• " (:name component) " (" (:type component) ")")))))

(defn demo-route-definition
  "Demonstrate route definition"
  []
  (println "=== Route Definition Demo ===")
  (let [routes (define-system-routes)]
    (println (str "Defined " (count routes) " routes"))
    (doseq [route (take 5 routes)]
      (println (str "• " (:name route) " " (:method route) " " (:path route))))))

(defn demo-action-definition
  "Demonstrate action definition"
  []
  (println "=== Action Definition Demo ===")
  (let [actions (define-system-actions)]
    (println (str "Defined " (count actions) " actions"))
    (doseq [action (take 5 actions)]
      (println (str "• " (:name action) " -> " (:function action))))))

(defn demo-state-definition
  "Demonstrate state definition"
  []
  (println "=== State Definition Demo ===")
  (let [states (define-system-states)]
    (println (str "Defined " (count states) " states"))
    (doseq [state (take 5 states)]
      (println (str "• " (:name state) " (" (:type state) ")")))))

(defn run-all-inventory-demos
  "Run all inventory demonstrations"
  []
  (println "🎯 === ACTORS System Inventory Comprehensive Demo ===")
  (println)
  (demo-symbol-collection)
  (println)
  (demo-component-registration)
  (println)
  (demo-route-definition)
  (println)
  (demo-action-definition)
  (println)
  (demo-state-definition)
  (println)
  (display-complete-inventory)
  (println)
  (println "🎉 === All Inventory Demos Complete ==="))

(defn -main
  "Main entry point for system inventory demo"
  [& args]
  (display-complete-inventory))
