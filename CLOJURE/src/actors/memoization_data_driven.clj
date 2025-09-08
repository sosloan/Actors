(ns actors.memoization-data-driven
  "Advanced Memoization and Data-Driven Programming System"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.data.json :as json]
            [clojure.set :as set]
            [clojure.math.numeric-tower :as math]
            [actors.simple-higher-order-functions :as hof]
            [actors.advanced-functional-patterns :as afp]))

;; =============================================================================
;; ADVANCED MEMOIZATION STRATEGIES
;; =============================================================================

(defprotocol MemoizationStrategy
  "Protocol for different memoization strategies"
  (should-cache? [this args result] "Determine if result should be cached")
  (cache-key [this args] "Generate cache key from arguments")
  (cache-value [this result] "Transform result for caching")
  (retrieve-value [this cached-value] "Transform cached value back to result"))

(defrecord LRUMemoizationStrategy [max-size ttl-ms]
  MemoizationStrategy
  (should-cache? [_ args result]
    (and (not (nil? result))
         (not (instance? Exception result))))
  
  (cache-key [_ args]
    (hash args))
  
  (cache-value [_ result]
    {:value result
     :timestamp (System/currentTimeMillis)
     :access-count 0})
  
  (retrieve-value [_ cached-value]
    (update cached-value :access-count inc)))

(defrecord TimeBasedMemoizationStrategy [ttl-ms]
  MemoizationStrategy
  (should-cache? [_ args result]
    (and (not (nil? result))
         (not (instance? Exception result))))
  
  (cache-key [_ args]
    (hash args))
  
  (cache-value [_ result]
    {:value result
     :timestamp (System/currentTimeMillis)})
  
  (retrieve-value [_ cached-value]
    cached-value))

(defrecord SizeBasedMemoizationStrategy [max-size]
  MemoizationStrategy
  (should-cache? [_ args result]
    (and (not (nil? result))
         (not (instance? Exception result))
         (< (count (str result)) 1000))) ; Only cache small results
  
  (cache-key [_ args]
    (hash args))
  
  (cache-value [_ result]
    {:value result
     :size (count (str result))})
  
  (retrieve-value [_ cached-value]
    cached-value))

(defn create-advanced-memoizer
  "Create advanced memoizer with custom strategy"
  [f strategy]
  (let [cache (atom {})
        access-order (atom [])]
    (fn [& args]
      (let [key (cache-key strategy args)
            now (System/currentTimeMillis)
            cached (get @cache key)]
        
        (if (and cached
                 (case (type strategy)
                   actors.memoization_data_driven.LRUMemoizationStrategy
                   (and (< (- now (:timestamp cached)) (:ttl-ms strategy))
                        (< (count @cache) (:max-size strategy)))
                   
                   actors.memoization_data_driven.TimeBasedMemoizationStrategy
                   (< (- now (:timestamp cached)) (:ttl-ms strategy))
                   
                   actors.memoization_data_driven.SizeBasedMemoizationStrategy
                   (< (count @cache) (:max-size strategy))
                   
                   true))
          (do
            (swap! access-order #(conj (remove #{key} %) key))
            (retrieve-value strategy cached))
          (let [result (apply f args)]
            (when (should-cache? strategy args result)
              (let [cached-value (cache-value strategy result)]
                (swap! cache assoc key cached-value)
                (swap! access-order #(conj (remove #{key} %) key))
                
                ;; Cleanup for LRU
                (when (and (instance? actors.memoization_data_driven.LRUMemoizationStrategy strategy)
                           (> (count @cache) (:max-size strategy)))
                  (let [oldest-key (first @access-order)]
                    (swap! cache dissoc oldest-key)
                    (swap! access-order rest)))))
            result)))))

;; =============================================================================
;; DATA-DRIVEN FUNCTION COMPOSITION
;; =============================================================================

(defrecord FunctionDefinition
  [id
   name
   function
   dependencies
   inputs
   outputs
   metadata])

(defrecord DataFlow
  [id
   name
   steps
   inputs
   outputs
   metadata])

(defrecord ExecutionContext
  [data
   functions
   cache
   metadata])

(def ^:private function-registry (atom {}))
(def ^:private dataflow-registry (atom {}))

(defn register-function
  "Register a function definition"
  [function-def]
  (swap! function-registry assoc (:id function-def) function-def)
  function-def)

(defn register-dataflow
  "Register a data flow definition"
  [dataflow]
  (swap! dataflow-registry assoc (:id dataflow) dataflow)
  dataflow)

(defn create-function-definition
  "Create a function definition"
  [id name function & {:keys [dependencies inputs outputs metadata]
                       :or {dependencies [] inputs [] outputs [] metadata {}}}]
  (->FunctionDefinition
   id
   name
   function
   dependencies
   inputs
   outputs
   metadata))

(defn create-dataflow
  "Create a data flow definition"
  [id name steps & {:keys [inputs outputs metadata]
                    :or {inputs [] outputs [] metadata {}}}]
  (->DataFlow
   id
   name
   steps
   inputs
   outputs
   metadata))

(defn execute-dataflow
  "Execute a data flow with caching and dependency resolution"
  [dataflow-id input-data]
  (let [dataflow (get @dataflow-registry dataflow-id)
        context (->ExecutionContext input-data @function-registry (atom {}) {})]
    (if dataflow
      (loop [steps (:steps dataflow)
             current-data input-data
             results []]
        (if (empty? steps)
          {:data current-data
           :results results
           :cache @(:cache context)}
          (let [step (first steps)
                function-id (:function step)
                function-def (get @function-registry function-id)
                step-inputs (or (:inputs step) (:inputs dataflow))
                step-outputs (or (:outputs step) (:outputs dataflow))]
            
            (if function-def
              (let [function (:function function-def)
                    step-data (if step-inputs
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
                (println "Function not found:" function-id)
                (recur (rest steps) current-data results)))))
      (do
        (println "Data flow not found:" dataflow-id)
        nil))))

;; =============================================================================
;; INTELLIGENT CACHING SYSTEM
;; =============================================================================

(defrecord CacheEntry
  [key
   value
   timestamp
   access-count
   dependencies
   metadata])

(defrecord CacheManager
  [cache
   strategies
   cleanup-interval
   max-size])

(defn create-cache-manager
  "Create intelligent cache manager"
  [& {:keys [max-size cleanup-interval]
      :or {max-size 1000 cleanup-interval 60000}}]
  (->CacheManager
   (atom {})
   (atom {})
   cleanup-interval
   max-size))

(defn cache-get
  "Get value from cache with intelligent retrieval"
  [cache-manager key]
  (let [entry (get @(:cache cache-manager) key)]
    (if entry
      (do
        (swap! (:cache cache-manager)
               (fn [cache]
                 (assoc cache key (update entry :access-count inc))))
        (:value entry))
      nil)))

(defn cache-put
  "Put value in cache with intelligent storage"
  [cache-manager key value & {:keys [dependencies ttl-ms]
                              :or {dependencies [] ttl-ms 300000}}]
  (let [entry (->CacheEntry
               key
               value
               (System/currentTimeMillis)
               1
               dependencies
               {:ttl-ms ttl-ms})]
    (swap! (:cache cache-manager) assoc key entry)
    
    ;; Cleanup if needed
    (when (> (count @(:cache cache-manager)) (:max-size cache-manager))
      (let [entries (sort-by (fn [[_ entry]] (:access-count entry))
                             <
                             @(:cache cache-manager))
            to-remove (take (- (count entries) (:max-size cache-manager))
                            (keys entries))]
        (swap! (:cache cache-manager)
               (fn [cache]
                 (apply dissoc cache to-remove)))))))

(defn cache-invalidate
  "Invalidate cache entries based on dependencies"
  [cache-manager dependency]
  (swap! (:cache cache-manager)
         (fn [cache]
           (into {} (remove (fn [[_ entry]]
                              (contains? (:dependencies entry) dependency))
                            cache)))))

(defn cache-cleanup
  "Clean up expired cache entries"
  [cache-manager]
  (let [now (System/currentTimeMillis)]
    (swap! (:cache cache-manager)
           (fn [cache]
             (into {} (remove (fn [[_ entry]]
                                (let [ttl (get-in entry [:metadata :ttl-ms] 300000)]
                                  (> (- now (:timestamp entry)) ttl)))
                              cache))))))

;; =============================================================================
;; DATA-DRIVEN FINANCIAL FUNCTIONS
;; =============================================================================

(defn create-financial-function-registry
  "Create registry of financial functions"
  []
  (let [functions [
                   ;; Price functions
                   (create-function-definition
                    "normalize-price"
                    "Normalize Price"
                    (fn [data]
                      (let [price (:price data)
                            min-price (:min-price data 100)
                            max-price (:max-price data 200)]
                        (/ (- price min-price) (- max-price min-price))))
                    :inputs [:price :min-price :max-price]
                    :outputs [:normalized-price])
                   
                   (create-function-definition
                    "denormalize-price"
                    "Denormalize Price"
                    (fn [data]
                      (let [normalized (:normalized-price data)
                            min-price (:min-price data 100)
                            max-price (:max-price data 200)]
                        (+ min-price (* normalized (- max-price min-price)))))
                    :inputs [:normalized-price :min-price :max-price]
                    :outputs [:denormalized-price])
                   
                   ;; Technical analysis functions
                   (create-function-definition
                    "calculate-rsi"
                    "Calculate RSI"
                    (fn [data]
                      (let [prices (:prices data)
                            period (:period data 14)]
                        (hof/calculate-rsi prices period)))
                    :inputs [:prices :period]
                    :outputs [:rsi])
                   
                   (create-function-definition
                    "calculate-ema"
                    "Calculate EMA"
                    (fn [data]
                      (let [prices (:prices data)
                            period (:period data 12)]
                        (hof/calculate-ema prices period)))
                    :inputs [:prices :period]
                    :outputs [:ema])
                   
                   ;; Signal generation functions
                   (create-function-definition
                    "generate-buy-signal"
                    "Generate Buy Signal"
                    (fn [data]
                      (let [rsi (:rsi data)
                            ema (:ema data)
                            price (:price data)]
                        (cond
                          (and (< rsi 30) (> price ema)) :strong-buy
                          (and (< rsi 50) (> price ema)) :buy
                          :else :hold)))
                    :inputs [:rsi :ema :price]
                    :outputs [:signal])
                   
                   (create-function-definition
                    "generate-sell-signal"
                    "Generate Sell Signal"
                    (fn [data]
                      (let [rsi (:rsi data)
                            ema (:ema data)
                            price (:price data)]
                        (cond
                          (and (> rsi 70) (< price ema)) :strong-sell
                          (and (> rsi 50) (< price ema)) :sell
                          :else :hold)))
                    :inputs [:rsi :ema :price]
                    :outputs [:signal])
                   
                   ;; Portfolio functions
                   (create-function-definition
                    "calculate-portfolio-value"
                    "Calculate Portfolio Value"
                    (fn [data]
                      (let [portfolio (:portfolio data)]
                        (hof/calculate-portfolio-value portfolio)))
                    :inputs [:portfolio]
                    :outputs [:portfolio-value])
                   
                   (create-function-definition
                    "calculate-portfolio-weights"
                    "Calculate Portfolio Weights"
                    (fn [data]
                      (let [portfolio (:portfolio data)]
                        (hof/calculate-portfolio-weights portfolio)))
                    :inputs [:portfolio]
                    :outputs [:portfolio-weights])
                   ]]
    
    (doseq [func functions]
      (register-function func))
    
    functions))

(defn create-financial-dataflows
  "Create financial data flows"
  []
  (let [dataflows [
                   ;; Price analysis flow
                   (create-dataflow
                    "price-analysis"
                    "Price Analysis Flow"
                    [{:function "normalize-price"}
                     {:function "denormalize-price"}]
                    :inputs [:price :min-price :max-price]
                    :outputs [:denormalized-price])
                   
                   ;; Technical analysis flow
                   (create-dataflow
                    "technical-analysis"
                    "Technical Analysis Flow"
                    [{:function "calculate-rsi"}
                     {:function "calculate-ema"}
                     {:function "generate-buy-signal"}]
                    :inputs [:prices :period :price]
                    :outputs [:signal])
                   
                   ;; Portfolio analysis flow
                   (create-dataflow
                    "portfolio-analysis"
                    "Portfolio Analysis Flow"
                    [{:function "calculate-portfolio-value"}
                     {:function "calculate-portfolio-weights"}]
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
  (let [cache-manager (create-cache-manager :max-size 5000 :cleanup-interval 30000)
        lru-strategy (->LRUMemoizationStrategy 1000 300000)
        time-strategy (->TimeBasedMemoizationStrategy 600000)
        
        ;; Memoized RSI calculation
        memoized-rsi (create-advanced-memoizer
                      (fn [prices period]
                        (hof/calculate-rsi prices period))
                      lru-strategy)
        
        ;; Memoized EMA calculation
        memoized-ema (create-advanced-memoizer
                      (fn [prices period]
                        (hof/calculate-ema prices period))
                      time-strategy)
        
        ;; Memoized portfolio value calculation
        memoized-portfolio-value (create-advanced-memoizer
                                  (fn [portfolio]
                                    (hof/calculate-portfolio-value portfolio))
                                  lru-strategy)
        
        ;; Memoized portfolio weights calculation
        memoized-portfolio-weights (create-advanced-memoizer
                                    (fn [portfolio]
                                      (hof/calculate-portfolio-weights portfolio))
                                    lru-strategy)]
    
    {:cache-manager cache-manager
     :memoized-rsi memoized-rsi
     :memoized-ema memoized-ema
     :memoized-portfolio-value memoized-portfolio-value
     :memoized-portfolio-weights memoized-portfolio-weights}))

;; =============================================================================
;; DATA-DRIVEN TRADING SYSTEM
;; =============================================================================

(defn create-data-driven-trading-system
  "Create data-driven trading system"
  []
  (let [function-registry (create-financial-function-registry)
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

(defn demo-advanced-memoization
  "Demonstrate advanced memoization strategies"
  []
  (println "=== Advanced Memoization Demo ===")
  
  ;; LRU Memoization
  (let [lru-strategy (->LRUMemoizationStrategy 3 1000)
        expensive-function (fn [x] (Thread/sleep 100) (* x x))
        memoized-lru (create-advanced-memoizer expensive-function lru-strategy)
        test-values [5 5 6 7 5 8 9]]
    
    (println "1. LRU Memoization (max 3 entries):")
    (let [start-time (System/currentTimeMillis)]
      (doseq [val test-values]
        (let [result (memoized-lru val)
              time-taken (- (System/currentTimeMillis) start-time)]
          (println "   Input:" val "-> Result:" result "Time:" time-taken "ms")))))
  
  ;; Time-based Memoization
  (let [time-strategy (->TimeBasedMemoizationStrategy 2000)
        memoized-time (create-advanced-memoizer #(* % %) time-strategy)
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
  (create-financial-function-registry)
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
    (cache-put cache-manager "AAPL" 150.25 :dependencies ["stocks"] :ttl-ms 5000)
    (cache-put cache-manager "GOOGL" 2800.50 :dependencies ["stocks"] :ttl-ms 5000)
    (cache-put cache-manager "MSFT" 300.75 :dependencies ["stocks"] :ttl-ms 5000)
    
    (println "   Cached AAPL, GOOGL, MSFT")
    
    ;; Get values
    (let [aapl (cache-get cache-manager "AAPL")
          googl (cache-get cache-manager "GOOGL")]
      (println "   Retrieved AAPL:" aapl)
      (println "   Retrieved GOOGL:" googl))
    
    ;; Invalidate by dependency
    (cache-invalidate cache-manager "stocks")
    (let [aapl-after (cache-get cache-manager "AAPL")]
      (println "   After invalidating 'stocks' dependency, AAPL:" aapl-after))
    
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

(defn run-all-memoization-data-driven-demos
  "Run all memoization and data-driven programming demonstrations"
  []
  (println "🎯 === ACTORS Memoization and Data-Driven Programming Comprehensive Demo ===")
  (println)
  (demo-advanced-memoization)
  (println)
  (demo-data-driven-programming)
  (println)
  (demo-intelligent-caching)
  (println)
  (demo-memoized-financial-calculations)
  (println)
  (demo-data-driven-trading-system)
  (println)
  (println "🎉 === All Memoization and Data-Driven Programming Demos Complete ==="))

(defn -main
  "Main entry point for memoization and data-driven programming demo"
  [& args]
  (run-all-memoization-data-driven-demos))
