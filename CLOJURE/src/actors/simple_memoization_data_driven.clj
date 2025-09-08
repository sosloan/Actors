(ns actors.simple-memoization-data-driven
  "Simplified Memoization and Data-Driven Programming System"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [actors.simple-higher-order-functions :as hof]))

;; =============================================================================
;; SIMPLE MEMOIZATION STRATEGIES
;; =============================================================================

(defn create-lru-memoizer
  "Create LRU memoizer with max size and TTL"
  [f max-size ttl-ms]
  (let [cache (atom {})
        access-order (atom [])]
    (fn [& args]
      (let [key (hash args)
            now (System/currentTimeMillis)
            cached (get @cache key)]
        (if (and cached
                 (< (- now (:timestamp cached)) ttl-ms)
                 (< (count @cache) max-size))
          (do
            (swap! access-order #(conj (remove #{key} %) key))
            (:value cached))
          (let [result (apply f args)]
            (when (not (nil? result))
              (let [cached-value {:value result :timestamp now}]
                (swap! cache assoc key cached-value)
                (swap! access-order #(conj (remove #{key} %) key))
                
                ;; Cleanup for LRU
                (when (> (count @cache) max-size)
                  (let [oldest-key (first @access-order)]
                    (swap! cache dissoc oldest-key)
                    (swap! access-order rest)))))
            result)))))

(defn create-time-based-memoizer
  "Create time-based memoizer with TTL"
  [f ttl-ms]
  (let [cache (atom {})]
    (fn [& args]
      (let [key (hash args)
            now (System/currentTimeMillis)
            cached (get @cache key)]
        (if (and cached (< (- now (:timestamp cached)) ttl-ms))
          (:value cached)
          (let [result (apply f args)]
            (when (not (nil? result))
              (swap! cache assoc key {:value result :timestamp now}))
            result)))))

(defn create-size-based-memoizer
  "Create size-based memoizer with max cache size"
  [f max-size]
  (let [cache (atom {})]
    (fn [& args]
      (let [key (hash args)
            cached (get @cache key)]
        (if cached
          (:value cached)
          (let [result (apply f args)]
            (when (and (not (nil? result)) (< (count @cache) max-size))
              (swap! cache assoc key {:value result}))
            result)))))

;; =============================================================================
;; DATA-DRIVEN FUNCTION COMPOSITION
;; =============================================================================

(defrecord FunctionStep
  [id
   function
   inputs
   outputs])

(defrecord DataFlow
  [id
   name
   steps
   inputs
   outputs])

(def ^:private function-registry (atom {}))
(def ^:private dataflow-registry (atom {}))

(defn register-function
  "Register a function in the registry"
  [id function]
  (swap! function-registry assoc id function)
  function)

(defn register-dataflow
  "Register a data flow in the registry"
  [dataflow]
  (swap! dataflow-registry assoc (:id dataflow) dataflow)
  dataflow)

(defn create-function-step
  "Create a function step"
  [id function & {:keys [inputs outputs] :or {inputs [] outputs []}}]
  (->FunctionStep id function inputs outputs))

(defn create-dataflow
  "Create a data flow"
  [id name steps & {:keys [inputs outputs] :or {inputs [] outputs []}}]
  (->DataFlow id name steps inputs outputs))

(defn execute-dataflow
  "Execute a data flow"
  [dataflow-id input-data]
  (let [dataflow (get @dataflow-registry dataflow-id)]
    (if dataflow
      (loop [steps (:steps dataflow)
             current-data input-data
             results []]
        (if (empty? steps)
          {:data current-data :results results}
          (let [step (first steps)
                function (get @function-registry (:id step))
                step-inputs (or (:inputs step) (:inputs dataflow))
                step-outputs (or (:outputs step) (:outputs dataflow))]
            (if function
              (let [step-data (if step-inputs
                                (select-keys current-data step-inputs)
                                current-data)
                    result (function step-data)
                    new-data (if step-outputs
                               (merge current-data (zipmap step-outputs [result]))
                               (assoc current-data :last-result result))]
                (recur (rest steps)
                       new-data
                       (conj results {:step step :result result})))
              (do
                (println "Function not found:" (:id step))
                (recur (rest steps) current-data results)))))
      (do
        (println "Data flow not found:" dataflow-id)
        nil))))

;; =============================================================================
;; INTELLIGENT CACHING SYSTEM
;; =============================================================================

(defn create-cache-manager
  "Create cache manager"
  [& {:keys [max-size cleanup-interval] :or {max-size 1000 cleanup-interval 60000}}]
  (atom {:cache {}
         :max-size max-size
         :cleanup-interval cleanup-interval}))

(defn cache-get
  "Get value from cache"
  [cache-manager key]
  (let [entry (get-in @cache-manager [:cache key])]
    (if entry
      (do
        (swap! cache-manager
               (fn [state]
                 (update-in state [:cache key :access-count] (fnil inc 0))))
        (:value entry))
      nil)))

(defn cache-put
  "Put value in cache"
  [cache-manager key value & {:keys [ttl-ms] :or {ttl-ms 300000}}]
  (let [entry {:value value
               :timestamp (System/currentTimeMillis)
               :access-count 1
               :ttl-ms ttl-ms}]
    (swap! cache-manager
           (fn [state]
             (let [new-cache (assoc-in state [:cache key] entry)]
               (if (> (count (:cache new-cache)) (:max-size state))
                 (let [entries (sort-by (fn [[_ entry]] (:access-count entry))
                                        <
                                        (:cache new-cache))
                       to-remove (take (- (count entries) (:max-size state))
                                       (keys entries))]
                   (update new-cache :cache #(apply dissoc % to-remove)))
                 new-cache))))))

(defn cache-cleanup
  "Clean up expired cache entries"
  [cache-manager]
  (let [now (System/currentTimeMillis)]
    (swap! cache-manager
           (fn [state]
             (update state :cache
                     (fn [cache]
                       (into {} (remove (fn [[_ entry]]
                                          (> (- now (:timestamp entry))
                                             (:ttl-ms entry)))
                                        cache))))))))

;; =============================================================================
;; FINANCIAL FUNCTIONS
;; =============================================================================

(defn create-financial-functions
  "Create financial functions"
  []
  (let [functions {
                   ;; Price functions
                   :normalize-price (fn [data]
                                      (let [price (:price data)
                                            min-price (:min-price data 100)
                                            max-price (:max-price data 200)]
                                        (/ (- price min-price) (- max-price min-price))))
                   
                   :denormalize-price (fn [data]
                                        (let [normalized (:normalized-price data)
                                              min-price (:min-price data 100)
                                              max-price (:max-price data 200)]
                                          (+ min-price (* normalized (- max-price min-price)))))
                   
                   ;; Technical analysis functions
                   :calculate-rsi (fn [data]
                                    (let [prices (:prices data)
                                          period (:period data 14)]
                                      (hof/calculate-rsi prices period)))
                   
                   :calculate-ema (fn [data]
                                    (let [prices (:prices data)
                                          period (:period data 12)]
                                      (hof/calculate-ema prices period)))
                   
                   ;; Signal generation functions
                   :generate-signal (fn [data]
                                      (let [rsi (:rsi data)
                                            ema (:ema data)
                                            price (:price data)]
                                        (cond
                                          (and (< rsi 30) (> price ema)) :strong-buy
                                          (and (< rsi 50) (> price ema)) :buy
                                          (and (> rsi 70) (< price ema)) :strong-sell
                                          (and (> rsi 50) (< price ema)) :sell
                                          :else :hold)))
                   
                   ;; Portfolio functions
                   :calculate-portfolio-value (fn [data]
                                                (let [portfolio (:portfolio data)]
                                                  (hof/calculate-portfolio-value portfolio)))
                   
                   :calculate-portfolio-weights (fn [data]
                                                  (let [portfolio (:portfolio data)]
                                                    (hof/calculate-portfolio-weights portfolio)))
                   }]
    
    (doseq [[id func] functions]
      (register-function id func))
    
    functions))

(defn create-financial-dataflows
  "Create financial data flows"
  []
  (let [dataflows [
                   ;; Price analysis flow
                   (create-dataflow
                    "price-analysis"
                    "Price Analysis Flow"
                    [(create-function-step :normalize-price :normalize-price)
                     (create-function-step :denormalize-price :denormalize-price)]
                    :inputs [:price :min-price :max-price]
                    :outputs [:denormalized-price])
                   
                   ;; Technical analysis flow
                   (create-dataflow
                    "technical-analysis"
                    "Technical Analysis Flow"
                    [(create-function-step :calculate-rsi :calculate-rsi)
                     (create-function-step :calculate-ema :calculate-ema)
                     (create-function-step :generate-signal :generate-signal)]
                    :inputs [:prices :period :price]
                    :outputs [:signal])
                   
                   ;; Portfolio analysis flow
                   (create-dataflow
                    "portfolio-analysis"
                    "Portfolio Analysis Flow"
                    [(create-function-step :calculate-portfolio-value :calculate-portfolio-value)
                     (create-function-step :calculate-portfolio-weights :calculate-portfolio-weights)]
                    :inputs [:portfolio]
                    :outputs [:portfolio-value :portfolio-weights])
                   ]]
    
    (doseq [dataflow dataflows]
      (register-dataflow dataflow))
    
    dataflows))

;; =============================================================================
;; MEMOIZED FINANCIAL CALCULATIONS
;; =============================================================================

(defn create-memoized-financial-calculator
  "Create memoized financial calculator"
  []
  (let [;; Memoized RSI calculation
        memoized-rsi (create-lru-memoizer
                      (fn [prices period]
                        (hof/calculate-rsi prices period))
                      1000 300000)
        
        ;; Memoized EMA calculation
        memoized-ema (create-time-based-memoizer
                      (fn [prices period]
                        (hof/calculate-ema prices period))
                      600000)
        
        ;; Memoized portfolio value calculation
        memoized-portfolio-value (create-lru-memoizer
                                  (fn [portfolio]
                                    (hof/calculate-portfolio-value portfolio))
                                  1000 300000)
        
        ;; Memoized portfolio weights calculation
        memoized-portfolio-weights (create-lru-memoizer
                                    (fn [portfolio]
                                      (hof/calculate-portfolio-weights portfolio))
                                    1000 300000)]
    
    {:memoized-rsi memoized-rsi
     :memoized-ema memoized-ema
     :memoized-portfolio-value memoized-portfolio-value
     :memoized-portfolio-weights memoized-portfolio-weights}))

;; =============================================================================
;; DATA-DRIVEN TRADING SYSTEM
;; =============================================================================

(defn create-data-driven-trading-system
  "Create data-driven trading system"
  []
  (let [function-registry (create-financial-functions)
        dataflow-registry (create-financial-dataflows)
        calculator (create-memoized-financial-calculator)
        
        ;; Trading decision function
        trading-decision (fn [market-data]
                          (let [price-analysis (execute-dataflow "price-analysis" market-data)
                                technical-analysis (execute-dataflow "technical-analysis" market-data)
                                portfolio-analysis (execute-dataflow "portfolio-analysis" market-data)]
                            {:price-analysis price-analysis
                             :technical-analysis technical-analysis
                             :portfolio-analysis portfolio-analysis
                             :decision (cond
                                         (= (:signal (:data technical-analysis)) :strong-buy) :buy
                                         (= (:signal (:data technical-analysis)) :buy) :buy
                                         (= (:signal (:data technical-analysis)) :strong-sell) :sell
                                         (= (:signal (:data technical-analysis)) :sell) :sell
                                         :else :hold)}))]
    
    {:function-registry function-registry
     :dataflow-registry dataflow-registry
     :calculator calculator
     :trading-decision trading-decision}))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-simple-memoization
  "Demonstrate simple memoization strategies"
  []
  (println "=== Simple Memoization Demo ===")
  
  ;; LRU Memoization
  (let [expensive-function (fn [x] (Thread/sleep 100) (* x x))
        memoized-lru (create-lru-memoizer expensive-function 3 1000)
        test-values [5 5 6 7 5 8 9]]
    
    (println "1. LRU Memoization (max 3 entries):")
    (let [start-time (System/currentTimeMillis)]
      (doseq [val test-values]
        (let [result (memoized-lru val)
              time-taken (- (System/currentTimeMillis) start-time)]
          (println "   Input:" val "-> Result:" result "Time:" time-taken "ms")))))
  
  ;; Time-based Memoization
  (let [memoized-time (create-time-based-memoizer #(* % %) 2000)
        test-values [5 5 6 5]]
    
    (println "2. Time-based Memoization (2s TTL):")
    (doseq [val test-values]
      (let [result (memoized-time val)]
        (println "   Input:" val "-> Result:" result)))
    (Thread/sleep 2500)
    (println "   After TTL expiration:")
    (doseq [val test-values]
      (let [result (memoized-time val)]
        (println "   Input:" val "-> Result:" result)))))

(defn demo-data-driven-programming
  "Demonstrate data-driven programming"
  []
  (println "=== Data-Driven Programming Demo ===")
  
  ;; Create function registry and data flows
  (create-financial-functions)
  (create-financial-dataflows)
  
  ;; Execute price analysis flow
  (let [price-data {:price 150 :min-price 100 :max-price 200}
        price-result (execute-dataflow "price-analysis" price-data)]
    (println "1. Price Analysis Flow:")
    (println "   Input:" price-data)
    (println "   Output:" (:data price-result)))
  
  ;; Execute technical analysis flow
  (let [technical-data {:prices [100 105 110 108 115 120 118 125 130 128]
                        :period 14
                        :price 130}
        technical-result (execute-dataflow "technical-analysis" technical-data)]
    (println "2. Technical Analysis Flow:")
    (println "   Input prices:" (:prices technical-data))
    (println "   RSI:" (get-in technical-result [:data :rsi]))
    (println "   EMA:" (get-in technical-result [:data :ema]))
    (println "   Signal:" (get-in technical-result [:data :signal])))
  
  ;; Execute portfolio analysis flow
  (let [portfolio-data {:portfolio {"AAPL" 100 "GOOGL" 50}}
        portfolio-result (execute-dataflow "portfolio-analysis" portfolio-data)]
    (println "3. Portfolio Analysis Flow:")
    (println "   Input portfolio:" (:portfolio portfolio-data))
    (println "   Portfolio value:" (get-in portfolio-result [:data :portfolio-value]))
    (println "   Portfolio weights:" (get-in portfolio-result [:data :portfolio-weights]))))

(defn demo-intelligent-caching
  "Demonstrate intelligent caching system"
  []
  (println "=== Intelligent Caching Demo ===")
  
  (let [cache-manager (create-cache-manager :max-size 5 :cleanup-interval 10000)]
    (println "1. Cache operations:")
    
    ;; Put some values
    (cache-put cache-manager "AAPL" 150.25 :ttl-ms 5000)
    (cache-put cache-manager "GOOGL" 2800.50 :ttl-ms 5000)
    (cache-put cache-manager "MSFT" 300.75 :ttl-ms 5000)
    
    (println "   Cached AAPL, GOOGL, MSFT")
    
    ;; Get values
    (let [aapl (cache-get cache-manager "AAPL")
          googl (cache-get cache-manager "GOOGL")]
      (println "   Retrieved AAPL:" aapl)
      (println "   Retrieved GOOGL:" googl))
    
    ;; Cleanup
    (cache-cleanup cache-manager)
    (println "   Cache cleaned up")))

(defn demo-memoized-financial-calculations
  "Demonstrate memoized financial calculations"
  []
  (println "=== Memoized Financial Calculations Demo ===")
  
  (let [calculator (create-memoized-financial-calculator)
        prices [100 105 110 108 115 120 118 125 130 128]
        portfolio {"AAPL" 100 "GOOGL" 50}]
    
    (println "1. Memoized RSI calculation:")
    (let [start-time (System/currentTimeMillis)
          rsi1 ((:memoized-rsi calculator) prices 14)
          time1 (- (System/currentTimeMillis) start-time)
          start-time2 (System/currentTimeMillis)
          rsi2 ((:memoized-rsi calculator) prices 14)
          time2 (- (System/currentTimeMillis) start-time2)]
      (println "   First call - RSI:" rsi1 "Time:" time1 "ms")
      (println "   Second call (cached) - RSI:" rsi2 "Time:" time2 "ms"))
    
    (println "2. Memoized portfolio calculations:")
    (let [start-time (System/currentTimeMillis)
          value1 ((:memoized-portfolio-value calculator) portfolio)
          time1 (- (System/currentTimeMillis) start-time)
          start-time2 (System/currentTimeMillis)
          value2 ((:memoized-portfolio-value calculator) portfolio)
          time2 (- (System/currentTimeMillis) start-time2)]
      (println "   First call - Value:" value1 "Time:" time1 "ms")
      (println "   Second call (cached) - Value:" value2 "Time:" time2 "ms"))))

(defn demo-data-driven-trading-system
  "Demonstrate data-driven trading system"
  []
  (println "=== Data-Driven Trading System Demo ===")
  
  (let [trading-system (create-data-driven-trading-system)
        market-data {:price 150
                     :min-price 100
                     :max-price 200
                     :prices [100 105 110 108 115 120 118 125 130 128]
                     :period 14
                     :portfolio {"AAPL" 100 "GOOGL" 50}}]
    
    (println "1. Trading decision based on market data:")
    (let [decision ((:trading-decision trading-system) market-data)]
      (println "   Market data:" market-data)
      (println "   Price analysis:" (:price-analysis decision))
      (println "   Technical analysis:" (:technical-analysis decision))
      (println "   Portfolio analysis:" (:portfolio-analysis decision))
      (println "   Final decision:" (:decision decision)))))

(defn run-all-simple-memoization-data-driven-demos
  "Run all simple memoization and data-driven programming demonstrations"
  []
  (println "🎯 === ACTORS Simple Memoization and Data-Driven Programming Comprehensive Demo ===")
  (println)
  (demo-simple-memoization)
  (println)
  (demo-data-driven-programming)
  (println)
  (demo-intelligent-caching)
  (println)
  (demo-memoized-financial-calculations)
  (println)
  (demo-data-driven-trading-system)
  (println)
  (println "🎉 === All Simple Memoization and Data-Driven Programming Demos Complete ==="))

(defn -main
  "Main entry point for simple memoization and data-driven programming demo"
  [& args]
  (run-all-simple-memoization-data-driven-demos))
