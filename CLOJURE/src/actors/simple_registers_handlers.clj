(ns actors.simple-registers-handlers
  "Simplified Register and Handler System for Event-Driven Architecture"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [actors.simple-core :as core]))

;; =============================================================================
;; CORE DATA MODELS
;; =============================================================================

(defrecord Event
  [id
   type
   data
   timestamp
   source
   target])

(defrecord Handler
  [id
   event-types
   function
   priority
   enabled])

(defrecord Register
  [id
   name
   data
   last-updated
   version])

(defrecord Callback
  [id
   function
   context
   timeout
   retry-count
   max-retries])

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

(def ^:private event-queue
  "Event processing queue"
  (async/chan 1000))

;; =============================================================================
;; EVENT CREATION AND MANAGEMENT
;; =============================================================================

(defn create-event
  "Create a new event"
  [type data & {:keys [source target] :or {source "system" target "all"}}]
  (->Event
   (str "event_" (System/currentTimeMillis) "_" (rand-int 10000))
   type
   data
   (System/currentTimeMillis)
   source
   target))

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
  [type data & {:keys [source target]}]
  (let [event (create-event type data :source source :target target)]
    (register-event event)
    (emit-event event)
    event))

;; =============================================================================
;; HANDLER CREATION AND MANAGEMENT
;; =============================================================================

(defn create-handler
  "Create a new event handler"
  [id event-types function & {:keys [priority enabled] :or {priority 0 enabled true}}]
  (->Handler
   id
   (set event-types)
   function
   priority
   enabled))

(defn register-handler
  "Register a handler in the global registry"
  [handler]
  (swap! handler-registry assoc (:id handler) handler)
  handler)

(defn get-handlers-for-event-type
  "Get all handlers that can handle a specific event type"
  [event-type]
  (filter (fn [[_ handler]]
            (and (:enabled handler)
                 (contains? (:event-types handler) event-type)))
          @handler-registry))

;; =============================================================================
;; REGISTER CREATION AND MANAGEMENT
;; =============================================================================

(defn create-register
  "Create a new data register"
  [id name initial-data]
  (->Register
   id
   name
   initial-data
   (System/currentTimeMillis)
   1))

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
  [id function & {:keys [context timeout retry-count max-retries]
                  :or {context {} timeout 5000 retry-count 0 max-retries 3}}]
  (->Callback
   id
   function
   context
   timeout
   retry-count
   max-retries))

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
              (Thread/sleep 1000)
              (apply execute-callback callback-id args))
            (do
              (println "Callback" callback-id "failed after" (:max-retries callback) "retries:" (.getMessage e))
              nil))))
    (do
      (println "Callback" callback-id "not found")
      nil)))

;; =============================================================================
;; EVENT PROCESSING ENGINE
;; =============================================================================

(defn process-event
  "Process a single event by finding and executing appropriate handlers"
  [event]
  (let [handlers (get-handlers-for-event-type (:type event))]
    (doseq [[handler-id handler] handlers]
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

;; =============================================================================
;; SYSTEM INITIALIZATION
;; =============================================================================

(defn initialize-system
  "Initialize the register and handler system"
  []
  (println "🚀 Initializing Simple Register and Handler System...")
  
  ;; Start event processor
  (start-event-processor)
  
  ;; Create system registers
  (let [market-register (create-register "market_data" "Market Data Register" 
                                        {:symbols {} :last-update 0 :price-changes 0})
        trading-register (create-register "trading_signals" "Trading Signals Register"
                                         {:signals [] :last-signal nil :signal-count 0})
        portfolio-register (create-register "portfolio" "Portfolio Register"
                                           {:positions {} :total-value 0 :last-rebalance 0})]
    
    ;; Register all registers
    (doseq [register [market-register trading-register portfolio-register]]
      (register-register register))
    
    ;; Create and register handlers
    (let [market-handler (create-market-data-handler "market_data")
          trading-handler (create-trading-signal-handler "trading_signals")
          portfolio-handler (create-portfolio-handler "portfolio")]
      
      (doseq [handler [market-handler trading-handler portfolio-handler]]
        (register-handler handler)))
    
    (println "✅ Simple Register and Handler System Initialized")
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
                                           (println "   ✅ Success callback executed with result:" result)))
        
        error-callback (create-callback "error_callback"
                                       (fn [error]
                                         (println "   ❌ Error callback executed with error:" error)))
        
        retry-callback (create-callback "retry_callback"
                                       (fn [data]
                                         (if (< (rand) 0.5)
                                           (throw (Exception. "Simulated error"))
                                           (println "   🔄 Retry callback succeeded with data:" data))))]
    
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

(defn demo-integrated-workflow
  "Demonstrate integrated workflow with all systems"
  []
  (println "=== Integrated Workflow Demo ===")
  
  ;; Initialize system
  (initialize-system)
  
  (println "1. System initialized with registers and handlers")
  
  ;; Create market data event
  (create-and-emit-event :market-data
                        {:symbol "AAPL" :price 150.25 :volume 1000000}
                        :source "market-feed")
  
  ;; Create trading signal event
  (create-and-emit-event :trading-signal
                        {:symbol "AAPL" :signal-type :buy :confidence 0.85}
                        :source "signal-generator")
  
  ;; Wait for events to be processed
  (Thread/sleep 1000)
  
  (println "2. Events processed by handlers")
  
  ;; Check register updates
  (println "3. Register updates:")
  (println "   Market data register:" (get-register-data "market_data"))
  (println "   Trading signals register:" (get-register-data "trading_signals"))
  (println "   Portfolio register:" (get-register-data "portfolio")))

(defn run-all-simple-register-handler-demos
  "Run all simple register and handler demonstrations"
  []
  (println "🎯 === ACTORS Simple Register and Handler System Comprehensive Demo ===")
  (println)
  (demo-event-creation)
  (println)
  (demo-register-updates)
  (println)
  (demo-callback-execution)
  (println)
  (demo-integrated-workflow)
  (println)
  (println "🎉 === All Simple Register and Handler Demos Complete ==="))

(defn -main
  "Main entry point for simple register and handler demo"
  [& args]
  (run-all-simple-register-handler-demos))
