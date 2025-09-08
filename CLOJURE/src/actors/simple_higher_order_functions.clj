(ns actors.simple-higher-order-functions
  "Simplified Higher Order Functions for Advanced Functional Programming"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.math.numeric-tower :as math]))

;; =============================================================================
;; CORE HIGHER ORDER FUNCTIONS
;; =============================================================================

(defn compose
  "Compose multiple functions from right to left"
  [& fns]
  (if (empty? fns)
    identity
    (let [fns (reverse fns)]
      (fn [& args]
        (reduce (fn [result f]
                  (if (coll? result)
                    (apply f result)
                    (f result)))
                (apply (first fns) args)
                (rest fns))))))

(defn pipe
  "Pipe multiple functions from left to right"
  [& fns]
  (if (empty? fns)
    identity
    (fn [& args]
      (reduce (fn [result f]
                (if (coll? result)
                  (apply f result)
                  (f result)))
              (apply (first fns) args)
              (rest fns)))))

(defn partial-apply
  "Partial application with better error handling"
  [f & args]
  (fn [& more-args]
    (try
      (apply f (concat args more-args))
      (catch Exception e
        (println "Partial application error:" (.getMessage e))
        nil))))

(defn memoize-with-ttl
  "Memoize function with time-to-live"
  [f ttl-ms]
  (let [cache (atom {})]
    (fn [& args]
      (let [key (hash args)
            now (System/currentTimeMillis)
            cached (get @cache key)]
        (if (and cached (< (- now (:timestamp cached)) ttl-ms))
          (:value cached)
          (let [result (apply f args)]
            (swap! cache assoc key {:value result :timestamp now})
            result))))))

(defn throttle
  "Throttle function calls"
  [f delay-ms]
  (let [last-call (atom 0)]
    (fn [& args]
      (let [now (System/currentTimeMillis)]
        (when (>= (- now @last-call) delay-ms)
          (reset! last-call now)
          (apply f args))))))

;; =============================================================================
;; FUNCTIONAL PROGRAMMING PATTERNS
;; =============================================================================

(defn map-with-index
  "Map function over collection with index"
  [f coll]
  (map-indexed (fn [idx item] (f item idx)) coll))

(defn filter-map
  "Filter and map in one pass"
  [pred f coll]
  (->> coll
       (filter pred)
       (map f)))

(defn group-by-fn
  "Group collection by function result"
  [f coll]
  (group-by f coll))

(defn partition-by-fn
  "Partition collection by function result"
  [f coll]
  (partition-by f coll))

(defn reduce-while
  "Reduce while predicate is true"
  [pred f init coll]
  (loop [acc init
         remaining coll]
    (if (and (seq remaining) (pred acc))
      (recur (f acc (first remaining)) (rest remaining))
      acc)))

(defn scan
  "Scan (like reduce but keep intermediate results)"
  [f init coll]
  (reductions f init coll))

;; =============================================================================
;; UTILITY FUNCTIONS
;; =============================================================================

(defn calculate-rsi
  "Calculate Relative Strength Index"
  [prices period]
  (let [gains (map #(max 0 %) (map - (rest prices) prices))
        losses (map #(max 0 %) (map - prices (rest prices)))
        avg-gain (/ (reduce + (take-last period gains)) period)
        avg-loss (/ (reduce + (take-last period losses)) period)]
    (if (zero? avg-loss)
      100
      (- 100 (/ 100 (+ 1 (/ avg-gain avg-loss)))))))

(defn get-current-price
  "Get current price for symbol"
  [symbol]
  (case symbol
    "AAPL" 150.25
    "GOOGL" 2800.50
    "MSFT" 300.75
    "TSLA" 800.00
    100.00))

;; =============================================================================
;; FINANCIAL HIGHER ORDER FUNCTIONS
;; =============================================================================

(defn create-price-transformer
  "Create price transformation pipeline"
  [& transformations]
  (apply compose transformations))

(defn create-signal-generator
  "Create signal generation pipeline"
  [& generators]
  (apply pipe generators))

(defn create-portfolio-analyzer
  "Create portfolio analysis pipeline"
  [& analyzers]
  (apply compose analyzers))

;; Price transformation functions
(defn normalize-price
  "Normalize price to 0-1 range"
  [min-price max-price]
  (fn [price]
    (/ (- price min-price) (- max-price min-price))))

(defn denormalize-price
  "Denormalize price from 0-1 range"
  [min-price max-price]
  (fn [normalized-price]
    (+ min-price (* normalized-price (- max-price min-price)))))

(defn apply-price-multiplier
  "Apply price multiplier"
  [multiplier]
  (fn [price]
    (* price multiplier)))

(defn apply-price-offset
  "Apply price offset"
  [offset]
  (fn [price]
    (+ price offset)))

;; Signal generation functions
(defn moving-average-signal
  "Generate moving average signal"
  [period]
  (fn [prices]
    (let [avg (apply + (take-last period prices))]
      (if (> (last prices) avg)
        :buy
        :sell))))

(defn rsi-signal
  "Generate RSI signal"
  [period]
  (fn [prices]
    (let [rsi (calculate-rsi prices period)]
      (cond
        (< rsi 30) :strong-buy
        (< rsi 50) :buy
        (> rsi 70) :strong-sell
        (> rsi 50) :sell
        :else :hold))))

;; Portfolio analysis functions
(defn calculate-portfolio-value
  "Calculate total portfolio value"
  [portfolio]
  (reduce + (map (fn [[symbol quantity]]
                   (* quantity (get-current-price symbol)))
                 portfolio)))

(defn calculate-portfolio-weights
  "Calculate portfolio weights"
  [portfolio]
  (let [total-value (calculate-portfolio-value portfolio)]
    (into {} (map (fn [[symbol quantity]]
                    [symbol (/ (* quantity (get-current-price symbol)) total-value)])
                  portfolio))))

;; =============================================================================
;; ADVANCED FUNCTIONAL PATTERNS
;; =============================================================================

(defn create-function-pipeline
  "Create a function pipeline with error handling"
  [& fns]
  (fn [& args]
    (reduce (fn [result f]
              (if (instance? Exception result)
                result
                (try
                  (if (coll? result)
                    (f result)
                    (f result))
                  (catch Exception e
                    e))))
            (apply (first fns) args)
            (rest fns))))

(defn create-conditional-pipeline
  "Create conditional pipeline"
  [predicates functions]
  (fn [& args]
    (loop [preds predicates
           fns functions]
      (if (empty? preds)
        nil
        (if (apply (first preds) args)
          (apply (first fns) args)
          (recur (rest preds) (rest fns)))))))

;; =============================================================================
;; FUNCTIONAL COMPOSITION EXAMPLES
;; =============================================================================

(defn create-trading-pipeline
  "Create complete trading pipeline"
  []
  (let [price-transformer (create-price-transformer
                           (normalize-price 100 200)
                           (apply-price-multiplier 1.1)
                           (denormalize-price 100 200))
        
        signal-generator (create-signal-generator
                         (moving-average-signal 20)
                         (rsi-signal 14))
        
        portfolio-analyzer (fn [portfolio]
                            {:value (calculate-portfolio-value portfolio)
                             :weights (calculate-portfolio-weights portfolio)})]
    
    (fn [market-data]
      (let [transformed-prices (map price-transformer (:prices market-data))
            signals (map signal-generator (partition 20 transformed-prices))
            portfolio-analysis (portfolio-analyzer (:portfolio market-data))]
        {:transformed-prices transformed-prices
         :signals signals
         :portfolio-analysis portfolio-analysis}))))

(defn create-data-processing-pipeline
  "Create data processing pipeline"
  []
  (let [data-cleaner (fn [data]
                       (filter #(not (nil? %)) data))
        
        data-transformer (fn [data]
                           (if (coll? data)
                             (map #(* % 1.1) data)
                             (* data 1.1)))
        
        data-aggregator (fn [data]
                          {:sum (reduce + data)
                           :avg (/ (reduce + data) (count data))
                           :max (apply max data)
                           :min (apply min data)})]
    
    (create-function-pipeline
     data-cleaner
     data-transformer
     data-aggregator)))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-function-composition
  "Demonstrate function composition"
  []
  (println "=== Function Composition Demo ===")
  
  ;; Basic composition
  (let [add-one (fn [x] (+ x 1))
        multiply-by-two (fn [x] (* x 2))
        square (fn [x] (* x x))
        
        composed-fn (compose square multiply-by-two add-one)
        piped-fn (pipe add-one multiply-by-two square)]
    
    (println "1. Basic composition:")
    (println "   Input: 5")
    (println "   Compose (square (multiply-by-two (add-one 5))):" (composed-fn 5))
    (println "   Pipe (square (multiply-by-two (add-one 5))):" (piped-fn 5))
    
    ;; Financial composition
    (let [price-transformer (create-price-transformer
                             (normalize-price 100 200)
                             (apply-price-multiplier 1.1)
                             (denormalize-price 100 200))
          test-price 150]
      
      (println "2. Financial price transformation:")
      (println "   Input price:" test-price)
      (println "   Transformed price:" (price-transformer test-price)))))

(defn demo-partial-application
  "Demonstrate partial application"
  []
  (println "=== Partial Application Demo ===")
  
  ;; Partial application
  (let [multiply (fn [x y] (* x y))
        multiply-by-five (partial-apply multiply 5)
        multiply-by-five-and-ten (partial-apply multiply 5 10)]
    
    (println "1. Partial application:")
    (println "   multiply-by-five 4:" (multiply-by-five 4))
    (println "   multiply-by-five-and-ten:" (multiply-by-five-and-ten))))

(defn demo-financial-pipelines
  "Demonstrate financial pipelines"
  []
  (println "=== Financial Pipelines Demo ===")
  
  ;; Trading pipeline
  (let [trading-pipeline (create-trading-pipeline)
        market-data {:prices [100 105 110 108 115 120 118 125 130 128]
                     :portfolio {"AAPL" 100 "GOOGL" 50}}]
    
    (println "1. Trading pipeline:")
    (let [result (trading-pipeline market-data)]
      (println "   Transformed prices:" (take 5 (:transformed-prices result)))
      (println "   Signals:" (take 3 (:signals result)))
      (println "   Portfolio analysis:" (:portfolio-analysis result))))
  
  ;; Data processing pipeline
  (let [data-pipeline (create-data-processing-pipeline)
        test-data [1 2 3 nil 5 6 7 8 9 10]]
    
    (println "2. Data processing pipeline:")
    (println "   Input data:" test-data)
    (println "   Processed result:" (data-pipeline test-data))))

(defn demo-advanced-patterns
  "Demonstrate advanced functional patterns"
  []
  (println "=== Advanced Functional Patterns Demo ===")
  
  ;; Function pipeline with error handling
  (let [error-pipeline (create-function-pipeline
                        (fn [x] (+ x 1))
                        (fn [x] (* x 2))
                        (fn [x] (if (> x 10) (throw (Exception. "Too big")) x))
                        (fn [x] (- x 1)))
        
        test-values [5 15 8]]
    
    (println "1. Function pipeline with error handling:")
    (doseq [val test-values]
      (let [result (error-pipeline val)]
        (if (instance? Exception result)
          (println "   Input:" val "-> Error:" (.getMessage result))
          (println "   Input:" val "-> Result:" result)))))
  
  ;; Conditional pipeline
  (let [conditional-pipeline (create-conditional-pipeline
                              [(fn [x] (< x 10))
                               (fn [x] (< x 20))
                               (fn [x] true)]
                              [(fn [x] (* x 2))
                               (fn [x] (* x 3))
                               (fn [x] (* x 4))])
        
        test-values [5 15 25]]
    
    (println "2. Conditional pipeline:")
    (doseq [val test-values]
      (println "   Input:" val "-> Result:" (conditional-pipeline val)))))

(defn demo-memoization-caching
  "Demonstrate memoization and caching"
  []
  (println "=== Memoization and Caching Demo ===")
  
  ;; Memoization with TTL
  (let [expensive-function (fn [x]
                             (Thread/sleep 100)
                             (* x x))
        
        memoized-function (memoize-with-ttl expensive-function 1000)
        
        test-values [5 5 6 5 7]]
    
    (println "1. Memoization with TTL:")
    (let [start-time (System/currentTimeMillis)]
      (doseq [val test-values]
        (let [result (memoized-function val)
              time-taken (- (System/currentTimeMillis) start-time)]
          (println "   Input:" val "-> Result:" result "Time:" time-taken "ms")))))
  
  ;; Throttling
  (let [throttled-function (throttle (fn [x] (println "   Throttled call with:" x)) 500)
        test-values [1 2 3 4 5]]
    
    (println "2. Throttling:")
    (doseq [val test-values]
      (throttled-function val)
      (Thread/sleep 100))))

(defn run-all-simple-higher-order-function-demos
  "Run all simple higher order function demonstrations"
  []
  (println "🎯 === ACTORS Simple Higher Order Functions Comprehensive Demo ===")
  (println)
  (demo-function-composition)
  (println)
  (demo-partial-application)
  (println)
  (demo-financial-pipelines)
  (println)
  (demo-advanced-patterns)
  (println)
  (demo-memoization-caching)
  (println)
  (println "🎉 === All Simple Higher Order Function Demos Complete ==="))

(defn -main
  "Main entry point for simple higher order function demo"
  [& args]
  (run-all-simple-higher-order-function-demos))
