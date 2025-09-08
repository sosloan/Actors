(ns actors.registers-handlers
  "Register and Handler System for Event-Driven Architecture"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.data.json :as json]
            [clojure.set :as set]
            [actors.simple-core :as core]
            [actors.simple-procedures :as procedures]
            [actors.grid-state :as grid]
            [actors.kawpow-consciousness :as kawpow]))

;; =============================================================================
;; CORE DATA MODELS
;; =============================================================================

(defrecord Event
  [id
   type
   data
   timestamp
   source
   target
   priority
   metadata])

(defrecord Handler
  [id
   event-types
   function
   priority
   enabled
   metadata])

(defrecord Register
  [id
   name
   data
   handlers
   last-updated
   version
   metadata])

(defrecord Callback
  [id
   function
   context
   timeout
   retry-count
   max-retries
   metadata])

(defrecord EventChain
  [id
   events
   current-step
   status
   results
   created-at
   completed-at])

;; =============================================================================
;; GLOBAL REGISTRIES
;; =============================================================================

(def ^:private event-registry
  "Global event registry"
  (atom {}))

(def ^:private handler-registry
  "Global handler registry"
  (atom {}))

(def ^:private register-registry
  "Global register registry"
  (atom {}))

(def ^:private callback-registry
  "Global callback registry"
  (atom {}))

(def ^:private event-chain-registry
  "Global event chain registry"
  (atom {}))

(def ^:private event-queue
  "Event processing queue"
  (async/chan 1000))

(def ^:private event-bus
  "Event bus for broadcasting"
  (async/mult event-queue))

;; =============================================================================
;; EVENT CREATION AND MANAGEMENT
;; =============================================================================

(defn create-event
  "Create a new event"
  [type data & {:keys [source target priority metadata]
                :or {source "system" target "all" priority 0 metadata {}}}]
  (->Event
   (str "event_" (System/currentTimeMillis) "_" (rand-int 10000))
   type
   data
   (System/currentTimeMillis)
   source
   target
   priority
   metadata))

(defn register-event
  "Register an event in the global registry"
  [event]
  (swap! event-registry assoc (:id event) event)
  event)

(defn emit-event
  "Emit an event to the event queue"
  [event]
  (go
    (>! event-queue event))
  event)

(defn create-and-emit-event
  "Create and emit an event in one operation"
  [type data & {:keys [source target priority metadata]}]
  (let [event (create-event type data :source source :target target :priority priority :metadata metadata)]
    (register-event event)
    (emit-event event)
    event))

;; =============================================================================
;; HANDLER CREATION AND MANAGEMENT
;; =============================================================================

(defn create-handler
  "Create a new event handler"
  [id event-types function & {:keys [priority enabled metadata]
                              :or {priority 0 enabled true metadata {}}}]
  (->Handler
   id
   (set event-types)
   function
   priority
   enabled
   metadata))

(defn register-handler
  "Register a handler in the global registry"
  [handler]
  (swap! handler-registry assoc (:id handler) handler)
  handler)

(defn unregister-handler
  "Unregister a handler from the global registry"
  [handler-id]
  (swap! handler-registry dissoc handler-id))

(defn get-handlers-for-event-type
  "Get all handlers that can handle a specific event type"
  [event-type]
  (filter (fn [[_ handler]]
            (and (:enabled handler)
                 (contains? (:event-types handler) event-type)))
          @handler-registry))

(defn sort-handlers-by-priority
  "Sort handlers by priority (higher priority first)"
  [handlers]
  (sort-by (fn [[_ handler]] (:priority handler)) > handlers))

;; =============================================================================
;; REGISTER CREATION AND MANAGEMENT
;; =============================================================================

(defn create-register
  "Create a new data register"
  [id name initial-data & {:keys [handlers version metadata]
                           :or {handlers #{} version 1 metadata {}}}]
  (->Register
   id
   name
   initial-data
   handlers
   (System/currentTimeMillis)
   version
   metadata))

(defn register-register
  "Register a register in the global registry"
  [register]
  (swap! register-registry assoc (:id register) register)
  register)

(defn update-register-data
  "Update data in a register"
  [register-id update-fn & args]
  (swap! register-registry
         (fn [registry]
           (if-let [register (get registry register-id)]
             (assoc registry register-id
                    (-> register
                        (update :data #(apply update-fn % args))
                        (assoc :last-updated (System/currentTimeMillis))
                        (update :version inc)))
             registry))))

(defn get-register
  "Get a register by ID"
  [register-id]
  (get @register-registry register-id))

(defn get-register-data
  "Get data from a register"
  [register-id]
  (:data (get-register register-id)))

;; =============================================================================
;; CALLBACK CREATION AND MANAGEMENT
;; =============================================================================

(defn create-callback
  "Create a new callback"
  [id function & {:keys [context timeout retry-count max-retries metadata]
                  :or {context {} timeout 5000 retry-count 0 max-retries 3 metadata {}}}]
  (->Callback
   id
   function
   context
   timeout
   retry-count
   max-retries
   metadata))

(defn register-callback
  "Register a callback in the global registry"
  [callback]
  (swap! callback-registry assoc (:id callback) callback)
  callback)

(defn execute-callback
  "Execute a callback with error handling and retry logic"
  [callback-id & args]
  (if-let [callback (get @callback-registry callback-id)]
    (try
      (let [result (apply (:function callback) args)]
        (swap! callback-registry
               (fn [registry]
                 (assoc-in registry [callback-id :retry-count] 0)))
        result)
      (catch Exception e
        (let [new-retry-count (inc (:retry-count callback))]
          (if (< new-retry-count (:max-retries callback))
            (do
              (swap! callback-registry
                     (fn [registry]
                       (assoc-in registry [callback-id :retry-count] new-retry-count)))
              (Thread/sleep 1000) ; Wait before retry
              (apply execute-callback callback-id args))
            (do
              (println "Callback" callback-id "failed after" (:max-retries callback) "retries:" (.getMessage e))
              nil))))
    (do
      (println "Callback" callback-id "not found")
      nil)))

;; =============================================================================
;; EVENT CHAIN MANAGEMENT
;; =============================================================================

(defn create-event-chain
  "Create a new event chain"
  [id events]
  (->EventChain
   id
   events
   0
   :pending
   []
   (System/currentTimeMillis)
   nil))

(defn register-event-chain
  "Register an event chain in the global registry"
  [event-chain]
  (swap! event-chain-registry assoc (:id event-chain) event-chain)
  event-chain)

(defn execute-event-chain
  "Execute an event chain step by step"
  [chain-id]
  (if-let [chain (get @event-chain-registry chain-id)]
    (let [current-step (:current-step chain)
          events (:events chain)
          current-event (nth events current-step nil)]
      (if current-event
        (do
          ;; Emit the current event
          (emit-event current-event)
          
          ;; Update chain status
          (swap! event-chain-registry
                 (fn [registry]
                   (assoc-in registry [chain-id :current-step] (inc current-step))))
          
          ;; Check if chain is complete
          (if (>= (inc current-step) (count events))
            (swap! event-chain-registry
                   (fn [registry]
                     (assoc-in registry [chain-id :status] :completed)
                     (assoc-in registry [chain-id :completed-at] (System/currentTimeMillis))))
            (swap! event-chain-registry
                   (fn [registry]
                     (assoc-in registry [chain-id :status] :in-progress))))
          
          chain)
        (do
          (println "Event chain" chain-id "has no more events")
          chain)))
    (do
      (println "Event chain" chain-id "not found")
      nil)))

;; =============================================================================
;; EVENT PROCESSING ENGINE
;; =============================================================================

(defn process-event
  "Process a single event by finding and executing appropriate handlers"
  [event]
  (let [handlers (get-handlers-for-event-type (:type event))
        sorted-handlers (sort-handlers-by-priority handlers)]
    
    (doseq [[handler-id handler] sorted-handlers]
      (try
        (when (:enabled handler)
          (let [result ((:function handler) event)]
            (when result
              (swap! event-registry
                     (fn [registry]
                       (assoc-in registry [(:id event) :results handler-id] result))))))
        (catch Exception e
          (println "Handler" handler-id "failed for event" (:id event) ":" (.getMessage e)))))))

(defn start-event-processor
  "Start the event processing loop"
  []
  (go-loop []
    (when-let [event (<! event-queue)]
      (process-event event)
      (recur))))

;; =============================================================================
;; FINANCIAL EVENT HANDLERS
;; =============================================================================

(defn create-market-data-handler
  "Create a handler for market data events"
  [register-id]
  (create-handler
   (str "market_data_handler_" register-id)
   #{:market-data :price-update :volume-update}
   (fn [event]
     (let [data (:data event)
           symbol (:symbol data)
           price (:price data)
           volume (:volume data)]
       
       ;; Update register with market data
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :last-price price
                                     :last-volume volume
                                     :last-update (System/currentTimeMillis))))
       
       ;; Trigger price change event if significant
       (when (> (Math/abs (- price (get current-data :last-price 0))) (* price 0.01))
         (create-and-emit-event :price-change
                               {:symbol symbol
                                :old-price (get current-data :last-price 0)
                                :new-price price
                                :change-percent (* (/ (- price (get current-data :last-price 0)) price) 100)}
                               :source "market-data-handler"))
       
       {:processed true :symbol symbol :price price}))))

(defn create-trading-signal-handler
  "Create a handler for trading signal events"
  [register-id]
  (create-handler
   (str "trading_signal_handler_" register-id)
   #{:trading-signal :signal-generated :signal-executed}
   (fn [event]
     (let [data (:data event)
           signal-type (:signal-type data)
           confidence (:confidence data)
           symbol (:symbol data)]
       
       ;; Update register with signal data
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :last-signal signal-type
                                     :last-confidence confidence
                                     :signal-count (inc (get current-data :signal-count 0))
                                     :last-signal-time (System/currentTimeMillis))))
       
       ;; Trigger portfolio update event for buy/sell signals
       (when (contains? #{:buy :strong-buy :sell :strong-sell} signal-type)
         (create-and-emit-event :portfolio-update
                               {:symbol symbol
                                :action signal-type
                                :confidence confidence
                                :timestamp (System/currentTimeMillis)}
                               :source "trading-signal-handler"))
       
       {:processed true :signal-type signal-type :confidence confidence}))))

(defn create-portfolio-handler
  "Create a handler for portfolio events"
  [register-id]
  (create-handler
   (str "portfolio_handler_" register-id)
   #{:portfolio-update :position-change :rebalance}
   (fn [event]
     (let [data (:data event)
           symbol (:symbol data)
           action (:action data)
           confidence (:confidence data)]
       
       ;; Update register with portfolio data
       (update-register-data register-id
                            (fn [current-data]
                              (let [positions (get current-data :positions {})
                                    current-position (get positions symbol 0)
                                    new-position (case action
                                                  (:buy :strong-buy) (+ current-position 100)
                                                  (:sell :strong-sell) (- current-position 100)
                                                  current-position)]
                                (assoc current-data
                                       :positions (assoc positions symbol new-position)
                                       :last-action action
                                       :last-action-time (System/currentTimeMillis)))))
       
       ;; Trigger risk assessment event
       (create-and-emit-event :risk-assessment
                             {:symbol symbol
                              :action action
                              :confidence confidence}
                             :source "portfolio-handler")
       
       {:processed true :action action :symbol symbol}))))

(defn create-risk-handler
  "Create a handler for risk management events"
  [register-id]
  (create-handler
   (str "risk_handler_" register-id)
   #{:risk-assessment :risk-alert :var-calculation}
   (fn [event]
     (let [data (:data event)
           risk-level (calculate-risk-level data)]
       
       ;; Update register with risk data
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :risk-level risk-level
                                     :last-risk-assessment (System/currentTimeMillis)
                                     :risk-alerts (inc (get current-data :risk-alerts 0)))))
       
       ;; Trigger alert if risk is high
       (when (= risk-level :high)
         (create-and-emit-event :risk-alert
                               {:risk-level risk-level
                                :message "High risk detected"
                                :timestamp (System/currentTimeMillis)}
                               :source "risk-handler"))
       
       {:processed true :risk-level risk-level}))))

(defn calculate-risk-level
  "Calculate risk level based on event data"
  [data]
  (let [confidence (:confidence data 0.5)
        action (:action data)]
    (cond
      (and (contains? #{:strong-buy :strong-sell} action) (< confidence 0.7)) :high
      (and (contains? #{:buy :sell} action) (< confidence 0.8)) :medium
      :else :low)))

;; =============================================================================
;; CONSCIOUSNESS EVENT HANDLERS
;; =============================================================================

(defn create-consciousness-handler
  "Create a handler for consciousness events"
  [register-id]
  (create-handler
   (str "consciousness_handler_" register-id)
   #{:consciousness-breakthrough :mathematical-resonance :tesla-resonance}
   (fn [event]
     (let [data (:data event)
           consciousness-level (:consciousness-level data)
           mathematical-resonance (:mathematical-resonance data)]
       
       ;; Update register with consciousness data
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :consciousness-level consciousness-level
                                     :mathematical-resonance mathematical-resonance
                                     :consciousness-breakthroughs (inc (get current-data :consciousness-breakthroughs 0))
                                     :last-consciousness-update (System/currentTimeMillis))))
       
       ;; Trigger enhanced signal generation for high consciousness
       (when (> consciousness-level 0.9)
         (create-and-emit-event :enhanced-signal-generation
                               {:consciousness-level consciousness-level
                                :mathematical-resonance mathematical-resonance
                                :enhancement-factor 1.5}
                               :source "consciousness-handler"))
       
       {:processed true :consciousness-level consciousness-level}))))

;; =============================================================================
;; GRID STATE EVENT HANDLERS
;; =============================================================================

(defn create-grid-handler
  "Create a handler for grid state events"
  [register-id]
  (create-handler
   (str "grid_handler_" register-id)
   #{:grid-update :grid-analysis :grid-optimization}
   (fn [event]
     (let [data (:data event)
           grid-id (:grid-id data)
           operation (:operation data)]
       
       ;; Update register with grid data
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :last-grid-operation operation
                                     :grid-operations (inc (get current-data :grid-operations 0))
                                     :last-grid-update (System/currentTimeMillis))))
       
       ;; Trigger grid analysis for optimization events
       (when (= operation :optimize)
         (create-and-emit-event :grid-analysis
                               {:grid-id grid-id
                                :analysis-type :optimization
                                :timestamp (System/currentTimeMillis)}
                               :source "grid-handler"))
       
       {:processed true :operation operation :grid-id grid-id}))))

;; =============================================================================
;; SYSTEM INITIALIZATION
;; =============================================================================

(defn initialize-system
  "Initialize the register and handler system"
  []
  (println "🚀 Initializing Register and Handler System...")
  
  ;; Start event processor
  (start-event-processor)
  
  ;; Create system registers
  (let [market-register (create-register "market_data" "Market Data Register" 
                                        {:symbols {} :last-update 0 :price-changes 0})
        trading-register (create-register "trading_signals" "Trading Signals Register"
                                         {:signals [] :last-signal nil :signal-count 0})
        portfolio-register (create-register "portfolio" "Portfolio Register"
                                           {:positions {} :total-value 0 :last-rebalance 0})
        risk-register (create-register "risk_management" "Risk Management Register"
                                      {:risk-level :low :alerts 0 :last-assessment 0})
        consciousness-register (create-register "consciousness" "Consciousness Register"
                                               {:level 0.0 :breakthroughs 0 :last-update 0})
        grid-register (create-register "grid_state" "Grid State Register"
                                      {:grids {} :operations 0 :last-update 0})]
    
    ;; Register all registers
    (doseq [register [market-register trading-register portfolio-register
                     risk-register consciousness-register grid-register]]
      (register-register register))
    
    ;; Create and register handlers
    (let [market-handler (create-market-data-handler "market_data")
          trading-handler (create-trading-signal-handler "trading_signals")
          portfolio-handler (create-portfolio-handler "portfolio")
          risk-handler (create-risk-handler "risk_management")
          consciousness-handler (create-consciousness-handler "consciousness")
          grid-handler (create-grid-handler "grid_state")]
      
      (doseq [handler [market-handler trading-handler portfolio-handler
                      risk-handler consciousness-handler grid-handler]]
        (register-handler handler)))
    
    (println "✅ Register and Handler System Initialized")
    (println "📊 Created" (count @register-registry) "registers")
    (println "🔧 Created" (count @handler-registry) "handlers")
    (println "🎯 Event processor started")))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-event-creation
  "Demonstrate event creation and emission"
  []
  (println "=== Event Creation Demo ===")
  
  ;; Create various types of events
  (let [market-event (create-and-emit-event :market-data
                                           {:symbol "AAPL" :price 150.25 :volume 1000000}
                                           :source "market-feed")
        signal-event (create-and-emit-event :trading-signal
                                           {:symbol "AAPL" :signal-type :buy :confidence 0.85}
                                           :source "signal-generator")
        portfolio-event (create-and-emit-event :portfolio-update
                                              {:symbol "AAPL" :action :buy :quantity 100}
                                              :source "portfolio-manager")]
    
    (println "1. Created market data event:" (:id market-event))
    (println "   Type:" (:type market-event))
    (println "   Data:" (:data market-event))
    
    (println "2. Created trading signal event:" (:id signal-event))
    (println "   Type:" (:type signal-event))
    (println "   Data:" (:data signal-event))
    
    (println "3. Created portfolio update event:" (:id portfolio-event))
    (println "   Type:" (:type portfolio-event))
    (println "   Data:" (:data portfolio-event))
    
    ;; Wait for events to be processed
    (Thread/sleep 1000)
    
    (println "4. Events processed and handlers triggered")))

(defn demo-register-updates
  "Demonstrate register data updates"
  []
  (println "=== Register Updates Demo ===")
  
  ;; Update market data register
  (update-register-data "market_data"
                       (fn [data]
                         (assoc data :AAPL {:price 150.25 :volume 1000000 :last-update (System/currentTimeMillis)})))
  
  ;; Update trading signals register
  (update-register-data "trading_signals"
                       (fn [data]
                         (assoc data :last-signal :buy :last-confidence 0.85 :signal-count 1)))
  
  ;; Update portfolio register
  (update-register-data "portfolio"
                       (fn [data]
                         (assoc data :positions {:AAPL 100 :GOOGL 50} :total-value 50000)))
  
  (println "1. Updated market data register:")
  (println "   AAPL data:" (get-register-data "market_data"))
  
  (println "2. Updated trading signals register:")
  (println "   Signal data:" (get-register-data "trading_signals"))
  
  (println "3. Updated portfolio register:")
  (println "   Portfolio data:" (get-register-data "portfolio")))

(defn demo-callback-execution
  "Demonstrate callback creation and execution"
  []
  (println "=== Callback Execution Demo ===")
  
  ;; Create callbacks
  (let [success-callback (create-callback "success_callback"
                                         (fn [result]
                                           (println "   ✅ Success callback executed with result:" result))
                                         :timeout 5000)
        
        error-callback (create-callback "error_callback"
                                       (fn [error]
                                         (println "   ❌ Error callback executed with error:" error))
                                       :timeout 5000)
        
        retry-callback (create-callback "retry_callback"
                                       (fn [data]
                                         (if (< (rand) 0.5)
                                           (throw (Exception. "Simulated error"))
                                           (println "   🔄 Retry callback succeeded with data:" data)))
                                       :max-retries 3)]
    
    ;; Register callbacks
    (doseq [callback [success-callback error-callback retry-callback]]
      (register-callback callback))
    
    (println "1. Created and registered callbacks")
    
    ;; Execute callbacks
    (println "2. Executing success callback:")
    (execute-callback "success_callback" "Operation completed successfully")
    
    (println "3. Executing error callback:")
    (execute-callback "error_callback" "Operation failed")
    
    (println "4. Executing retry callback (may fail and retry):")
    (execute-callback "retry_callback" "Test data")))

(defn demo-event-chains
  "Demonstrate event chain creation and execution"
  []
  (println "=== Event Chains Demo ===")
  
  ;; Create a sequence of events
  (let [events [(create-event :market-data {:symbol "AAPL" :price 150.25})
                (create-event :trading-signal {:symbol "AAPL" :signal-type :buy})
                (create-event :portfolio-update {:symbol "AAPL" :action :buy})
                (create-event :risk-assessment {:symbol "AAPL" :risk-level :low})]
        
        event-chain (create-event-chain "trading_workflow" events)]
    
    ;; Register event chain
    (register-event-chain event-chain)
    
    (println "1. Created event chain with" (count events) "events")
    (println "   Chain ID:" (:id event-chain))
    (println "   Status:" (:status event-chain))
    
    ;; Execute event chain
    (println "2. Executing event chain...")
    (doseq [step (range (count events))]
      (let [updated-chain (execute-event-chain "trading_workflow")]
        (println "   Step" (inc step) ":" (:status updated-chain))
        (Thread/sleep 500))) ; Small delay between steps
    
    (println "3. Event chain execution completed")))

(defn demo-integrated-workflow
  "Demonstrate integrated workflow with all systems"
  []
  (println "=== Integrated Workflow Demo ===")
  
  ;; Initialize system
  (initialize-system)
  
  (println "1. System initialized with registers and handlers")
  
  ;; Create KawPow consciousness signal
  (let [consciousness-signal (kawpow/generate-signal "AAPL" 
                                                     kawpow/default-highway-101-north 
                                                     kawpow/default-croatian-bowtie 
                                                     kawpow/default-config)]
    
    (println "2. Generated KawPow consciousness signal:")
    (println "   Signal type:" (get kawpow/signal-types (:signal-type consciousness-signal)))
    (println "   Confidence:" (format "%.1f%%" (* (:confidence consciousness-signal) 100)))
    (println "   Consciousness level:" (get kawpow/consciousness-levels (:consciousness-level consciousness-signal)))
    
    ;; Emit consciousness breakthrough event
    (create-and-emit-event :consciousness-breakthrough
                          {:consciousness-level (:consciousness-level consciousness-signal)
                           :mathematical-resonance (:mathematical-resonance consciousness-signal)
                           :tesla-resonance (:tesla-resonance consciousness-signal)}
                          :source "kawpow-consciousness")
    
    ;; Emit trading signal event
    (create-and-emit-event :trading-signal
                          {:symbol "AAPL"
                           :signal-type (:signal-type consciousness-signal)
                           :confidence (:confidence consciousness-signal)}
                          :source "kawpow-consciousness")
    
    ;; Wait for events to be processed
    (Thread/sleep 1000)
    
    (println "3. Events processed by handlers")
    
    ;; Check register updates
    (println "4. Register updates:")
    (println "   Consciousness register:" (get-register-data "consciousness"))
    (println "   Trading signals register:" (get-register-data "trading_signals"))
    (println "   Portfolio register:" (get-register-data "portfolio"))
    
    ;; Create grid update event
    (create-and-emit-event :grid-update
                          {:grid-id "portfolio_grid"
                           :operation :optimize
                           :data {:positions {:AAPL 100 :GOOGL 50}}}
                          :source "grid-optimizer")
    
    (Thread/sleep 500)
    
    (println "5. Grid update processed:")
    (println "   Grid state register:" (get-register-data "grid_state"))))

(defn run-all-register-handler-demos
  "Run all register and handler demonstrations"
  []
  (println "🎯 === ACTORS Register and Handler System Comprehensive Demo ===")
  (println)
  (demo-event-creation)
  (println)
  (demo-register-updates)
  (println)
  (demo-callback-execution)
  (println)
  (demo-event-chains)
  (println)
  (demo-integrated-workflow)
  (println)
  (println "🎉 === All Register and Handler Demos Complete ==="))

(defn -main
  "Main entry point for register and handler demo"
  [& args]
  (run-all-register-handler-demos))
