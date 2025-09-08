# 🔧 ACTORS Clojure Register and Handler System

## *Event-Driven Architecture with Registers, Handlers, and Callbacks*

---

## 🌟 **System Overview**

The **ACTORS Clojure Register and Handler System** provides a comprehensive event-driven architecture for managing data registers, event handlers, and callback execution. It implements asynchronous event processing with financial handlers, register management, and callback systems.

### **🎯 What's Included**
- ✅ **Event Creation**: Create and emit events with data and metadata
- ✅ **Handler Registration**: Register event handlers with functions and priorities
- ✅ **Register Management**: Create and update data registers with versioning
- ✅ **Callback Execution**: Execute callbacks with error handling and retry logic
- ✅ **Event Processing**: Process events through handler chains asynchronously
- ✅ **Financial Handlers**: Market data, trading signals, portfolio updates
- ✅ **Event-Driven Architecture**: Asynchronous event processing with queues
- ✅ **Data Updates**: Real-time data updates through event triggers

---

## 🚀 **Quick Start**

### **Start the System with Registers and Handlers**
```bash
cd /Users/stevensloan/ACTORS/CLOJURE
./scripts/start-with-registers-handlers.sh
```

### **Run All Register and Handler Demos**
```clojure
(actors.minimal-registers-handlers/run-all-minimal-register-handler-demos)
```

---

## 📚 **Core Data Models**

### **Event Model**
```clojure
(defrecord Event
  [id          ; Unique event identifier
   type        ; Event type (keyword)
   data        ; Event data (map)
   timestamp   ; Creation timestamp
   source])    ; Event source
```

### **Handler Model**
```clojure
(defrecord Handler
  [id          ; Handler identifier
   event-types ; Set of event types this handler can process
   function    ; Function to execute when event is processed
   enabled])   ; Whether handler is enabled
```

### **Register Model**
```clojure
(defrecord Register
  [id           ; Register identifier
   name         ; Human-readable name
   data         ; Register data (map)
   last-updated ; Last update timestamp
   version])    ; Version number for tracking changes
```

### **Callback Model**
```clojure
(defrecord Callback
  [id        ; Callback identifier
   function  ; Function to execute
   context]) ; Context data for the callback
```

---

## 🔧 **Event Creation and Management**

### **Creating Events**
```clojure
;; Create a simple event
(def event (create-event :market-data
                        {:symbol "AAPL" :price 150.25 :volume 1000000}
                        :source "market-feed"))

;; Create and emit event in one operation
(create-and-emit-event :trading-signal
                       {:symbol "AAPL" :signal-type :buy :confidence 0.85}
                       :source "signal-generator")
```

### **Event Registration**
```clojure
;; Register event in global registry
(register-event event)

;; Emit event to processing queue
(emit-event event)
```

---

## 🎯 **Handler Creation and Management**

### **Creating Handlers**
```clojure
;; Create a market data handler
(def market-handler
  (create-handler "market_data_handler"
                  #{:market-data :price-update}
                  (fn [event]
                    (let [data (:data event)
                          symbol (:symbol data)
                          price (:price data)]
                      (println "Processing market data for" symbol "at $" price)))
                  :enabled true))

;; Register handler
(register-handler market-handler)
```

### **Handler Types**
```clojure
;; Market data handler
(def market-handler (create-market-data-handler "market_data"))

;; Trading signal handler
(def trading-handler (create-trading-signal-handler "trading_signals"))

;; Portfolio handler
(def portfolio-handler (create-portfolio-handler "portfolio"))
```

---

## 📋 **Register Management**

### **Creating Registers**
```clojure
;; Create a market data register
(def market-register
  (create-register "market_data"
                   "Market Data Register"
                   {:symbols {} :last-update 0 :price-changes 0}))

;; Register the register
(register-register market-register)
```

### **Updating Register Data**
```clojure
;; Update register data with a function
(update-register-data "market_data"
                     (fn [current-data]
                       (assoc current-data
                              :AAPL {:price 150.25 :volume 1000000}
                              :last-update (System/currentTimeMillis))))

;; Get register data
(get-register-data "market_data")
```

---

## 🔄 **Callback Execution**

### **Creating Callbacks**
```clojure
;; Create success callback
(def success-callback
  (create-callback "success_callback"
                   (fn [result]
                     (println "✅ Success:" result))))

;; Create error callback
(def error-callback
  (create-callback "error_callback"
                   (fn [error]
                     (println "❌ Error:" error))))

;; Register callbacks
(register-callback success-callback)
(register-callback error-callback)
```

### **Executing Callbacks**
```clojure
;; Execute callback with arguments
(execute-callback "success_callback" "Operation completed successfully")
(execute-callback "error_callback" "Operation failed")
```

---

## 🧪 **Demo Functions**

### **Event Creation Demo**
```clojure
(actors.minimal-registers-handlers/demo-event-creation)
```

**Output:**
```
=== Event Creation Demo ===
1. Created market data event: event_1757291306743_8376
   Type: :market-data
   Data: {:symbol AAPL, :price 150.25, :volume 1000000}
2. Created trading signal event: event_1757291306745_7786
   Type: :trading-signal
   Data: {:symbol AAPL, :signal-type :buy, :confidence 0.85}
3. Events processed and handlers triggered
```

### **Register Updates Demo**
```clojure
(actors.minimal-registers-handlers/demo-register-updates)
```

**Output:**
```
=== Register Updates Demo ===
1. Updated market data register:
   AAPL data: {:symbols {}, :last-update 1757291337037, :last-price 150.25}
2. Updated trading signals register:
   Signal data: {:signals [], :last-signal :buy, :signal-count 1, :last-confidence 0.85}
```

### **Callback Execution Demo**
```clojure
(actors.minimal-registers-handlers/demo-callback-execution)
```

**Output:**
```
=== Callback Execution Demo ===
1. Created and registered callbacks
2. Executing success callback:
   ✅ Success callback executed with result: Operation completed successfully
3. Executing error callback:
   ❌ Error callback executed with error: Operation failed
```

### **Integrated Workflow Demo**
```clojure
(actors.minimal-registers-handlers/demo-integrated-workflow)
```

**Output:**
```
=== Integrated Workflow Demo ===
🚀 Initializing Minimal Register and Handler System...
✅ Minimal Register and Handler System Initialized
📊 Created 2 registers
🔧 Created 2 handlers
🎯 Event processor started
1. System initialized with registers and handlers
   📊 Market data updated for AAPL at $ 150.25
   📈 Trading signal processed: :buy for AAPL with confidence 0.85
2. Events processed by handlers
3. Register updates:
   Market data register: {:symbols {}, :last-update 1757291349186, :last-price 150.25}
   Trading signals register: {:signals [], :last-signal :buy, :signal-count 2, :last-confidence 0.85}
```

---

## 🎯 **Financial Event Handlers**

### **Market Data Handler**
```clojure
(defn create-market-data-handler
  "Create a handler for market data events"
  [register-id]
  (create-handler
   (str "market_data_handler_" register-id)
   #{:market-data :price-update}
   (fn [event]
     (let [data (:data event)
           symbol (:symbol data)
           price (:price data)]
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :last-price price
                                     :last-update (System/currentTimeMillis))))
       (println "📊 Market data updated for" symbol "at $" price)))))
```

### **Trading Signal Handler**
```clojure
(defn create-trading-signal-handler
  "Create a handler for trading signal events"
  [register-id]
  (create-handler
   (str "trading_signal_handler_" register-id)
   #{:trading-signal :signal-generated}
   (fn [event]
     (let [data (:data event)
           signal-type (:signal-type data)
           confidence (:confidence data)
           symbol (:symbol data)]
       (update-register-data register-id
                            (fn [current-data]
                              (assoc current-data
                                     :last-signal signal-type
                                     :last-confidence confidence
                                     :signal-count (inc (get current-data :signal-count 0)))))
       (println "📈 Trading signal processed:" signal-type "for" symbol "with confidence" confidence)))))
```

---

## 🔧 **Event Processing Engine**

### **Event Processing Loop**
```clojure
(defn start-event-processor
  "Start the event processing loop"
  []
  (go-loop []
    (when-let [event (<! event-queue)]
      (process-event event)
      (recur))))
```

### **Event Processing**
```clojure
(defn process-event
  "Process a single event by finding and executing appropriate handlers"
  [event]
  (let [handlers (get-handlers-for-event-type (:type event))]
    (doseq [[handler-id handler] handlers]
      (try
        (when (:enabled handler)
          ((:function handler) event))
        (catch Exception e
          (println "Handler" handler-id "failed for event" (:id event) ":" (.getMessage e)))))))
```

---

## 🎯 **Advanced Examples**

### **Custom Event Handler**
```clojure
;; Create custom handler for risk assessment
(def risk-handler
  (create-handler "risk_assessment_handler"
                  #{:risk-assessment :risk-alert}
                  (fn [event]
                    (let [data (:data event)
                          risk-level (:risk-level data)
                          symbol (:symbol data)]
                      (when (= risk-level :high)
                        (create-and-emit-event :risk-alert
                                              {:symbol symbol
                                               :risk-level risk-level
                                               :message "High risk detected"}
                                              :source "risk-handler"))
                      (println "⚠️ Risk assessment:" risk-level "for" symbol)))))

(register-handler risk-handler)
```

### **Event Chain Processing**
```clojure
;; Create a sequence of related events
(def event-chain
  [(create-event :market-data {:symbol "AAPL" :price 150.25})
   (create-event :trading-signal {:symbol "AAPL" :signal-type :buy})
   (create-event :portfolio-update {:symbol "AAPL" :action :buy})
   (create-event :risk-assessment {:symbol "AAPL" :risk-level :low})])

;; Process events in sequence
(doseq [event event-chain]
  (emit-event event)
  (Thread/sleep 500)) ; Small delay between events
```

### **Register Data Analysis**
```clojure
;; Analyze register data over time
(defn analyze-register-history
  [register-id]
  (let [register (get-register register-id)
        data (:data register)
        last-update (:last-update register)]
    {:register-id register-id
     :data-keys (keys data)
     :last-update last-update
     :age-minutes (/ (- (System/currentTimeMillis) last-update) 60000)}))

;; Analyze all registers
(defn analyze-all-registers
  []
  (map analyze-register-history (keys @register-registry)))
```

---

## 🔧 **Best Practices**

### **1. Event Design**
```clojure
;; Good: Clear event structure
(def market-event
  (create-event :market-data
                {:symbol "AAPL"
                 :price 150.25
                 :volume 1000000
                 :timestamp (System/currentTimeMillis)}
                :source "market-feed"))

;; Good: Consistent event types
(def event-types #{:market-data :trading-signal :portfolio-update :risk-assessment})
```

### **2. Handler Design**
```clojure
;; Good: Single responsibility handlers
(defn create-specialized-handler
  [event-type processing-fn]
  (create-handler (str event-type "_handler")
                  #{event-type}
                  processing-fn))

;; Good: Error handling in handlers
(defn safe-handler
  [event]
  (try
    (process-event-data event)
    (catch Exception e
      (println "Handler error:" (.getMessage e))
      (create-and-emit-event :handler-error
                            {:event-id (:id event)
                             :error (.getMessage e)}
                            :source "error-handler"))))
```

### **3. Register Management**
```clojure
;; Good: Atomic register updates
(defn atomic-register-update
  [register-id update-fn]
  (swap! register-registry
         (fn [registry]
           (if-let [register (get registry register-id)]
             (assoc registry register-id
                    (-> register
                        (update :data update-fn)
                        (assoc :last-updated (System/currentTimeMillis))
                        (update :version inc)))
             registry))))

;; Good: Register validation
(defn validate-register-data
  [register-id required-keys]
  (let [data (get-register-data register-id)]
    (every? #(contains? data %) required-keys)))
```

### **4. Callback Management**
```clojure
;; Good: Callback with timeout
(defn create-timeout-callback
  [id function timeout-ms]
  (create-callback id
                   (fn [& args]
                     (let [future-result (future (apply function args))]
                       (deref future-result timeout-ms :timeout)))
                   :timeout timeout-ms))

;; Good: Callback chaining
(defn chain-callbacks
  [callbacks]
  (fn [& args]
    (reduce (fn [result callback-id]
              (execute-callback callback-id result))
            args
            callbacks)))
```

---

## 🎉 **Success!**

The ACTORS Clojure Register and Handler System is now **WORKING** and ready for development! You can:

- ✅ Start the system with `./scripts/start-with-registers-handlers.sh`
- ✅ Run register/handler demos with `(actors.minimal-registers-handlers/run-all-minimal-register-handler-demos)`
- ✅ Create and emit events with `create-and-emit-event`
- ✅ Register event handlers with `register-handler`
- ✅ Manage data registers with `create-register` and `update-register-data`
- ✅ Execute callbacks with `execute-callback`
- ✅ Process events asynchronously through handler chains
- ✅ Implement financial event handlers for market data and trading signals
- ✅ Build event-driven architectures with real-time data updates

**Welcome to event-driven architecture with registers and handlers! 🔧**
