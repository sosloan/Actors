(ns actors.higher-order-functions
  "Higher Order Functions for Advanced Functional Programming"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.data.json :as json]
            [clojure.set :as set]
            [clojure.math.numeric-tower :as math]
            [actors.simple-core :as core]
            [actors.simple-procedures :as procedures]
            [actors.grid-state :as grid]
            [actors.kawpow-consciousness :as kawpow]
            [actors.minimal-registers-handlers :as registers]))

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

(defn curry
  "Curry a function of n arguments"
  [f]
  (fn [& args]
    (if (>= (count args) (-> f meta :arglists first count))
      (apply f args)
      (fn [& more-args]
        (apply curry (apply f (concat args more-args)))))))

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

(defn debounce
  "Debounce function calls"
  [f delay-ms]
  (let [timeout-id (atom nil)]
    (fn [& args]
      (when @timeout-id
        (.cancel @timeout-id))
      (reset! timeout-id
              (future
                (Thread/sleep delay-ms)
                (apply f args))))))

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

(defn unfold
  "Unfold function (opposite of fold)"
  [f init]
  (lazy-seq
   (let [result (f init)]
     (if result
       (cons (first result) (unfold f (second result)))
       nil))))

;; =============================================================================
;; MONADIC PATTERNS
;; =============================================================================

(defprotocol Monad
  "Monad protocol for functional programming"
  (unit [this value] "Lift value into monad")
  (bind [this f] "Bind function to monad"))

(defrecord Maybe [value]
  Monad
  (unit [_ v] (->Maybe v))
  (bind [_ f] (if (nil? value) (->Maybe nil) (f value))))

(defrecord Either [left right]
  Monad
  (unit [_ v] (->Either nil v))
  (bind [_ f] (if left (->Either left nil) (f right))))

(defrecord State [run]
  Monad
  (unit [_ v] (->State (fn [s] [v s])))
  (bind [_ f] (->State (fn [s]
                         (let [[a s'] (run s)]
                           ((:run (f a)) s'))))))

(defn maybe
  "Create Maybe monad"
  [value]
  (->Maybe value))

(defn either
  "Create Either monad"
  [left right]
  (->Either left right))

(defn state
  "Create State monad"
  [run-fn]
  (->State run-fn))

(defn fmap
  "Functor map"
  [f monad]
  (case (type monad)
    actors.higher_order_functions.Maybe
    (if (:value monad)
      (->Maybe (f (:value monad)))
      (->Maybe nil))
    
    actors.higher_order_functions.Either
    (if (:left monad)
      monad
      (->Either nil (f (:right monad))))
    
    actors.higher_order_functions.State
    (->State (fn [s]
               (let [[a s'] ((:run monad) s)]
                 [(f a) s'])))
    
    monad))

(defn applicative
  "Applicative functor apply"
  [f-monad value-monad]
  (case (type f-monad)
    actors.higher_order_functions.Maybe
    (if (and (:value f-monad) (:value value-monad))
      (->Maybe ((:value f-monad) (:value value-monad)))
      (->Maybe nil))
    
    actors.higher_order_functions.Either
    (if (:left f-monad)
      f-monad
      (if (:left value-monad)
        value-monad
        (->Either nil ((:right f-monad) (:right value-monad)))))
    
    actors.higher_order_functions.State
    (->State (fn [s]
               (let [[f s'] ((:run f-monad) s)
                     [v s''] ((:run value-monad) s')]
                 [(f v) s''])))
    
    value-monad))

;; =============================================================================
;; UTILITY FUNCTIONS
;; =============================================================================

(defn calculate-ema
  "Calculate Exponential Moving Average"
  [prices period]
  (let [alpha (/ 2.0 (+ period 1))
        ema (atom (first prices))]
    (doseq [price (rest prices)]
      (reset! ema (+ (* alpha price) (* (- 1 alpha) @ema))))
    @ema))

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

(defn calculate-macd
  "Calculate MACD"
  [prices fast-period slow-period signal-period]
  (let [fast-ema (calculate-ema prices fast-period)
        slow-ema (calculate-ema prices slow-period)
        macd-line (- fast-ema slow-ema)
        signal-line (calculate-ema (repeat signal-period macd-line) signal-period)]
    (- macd-line signal-line)))

(defn get-current-price
  "Get current price for symbol"
  [symbol]
  (case symbol
    "AAPL" 150.25
    "GOOGL" 2800.50
    "MSFT" 300.75
    "TSLA" 800.00
    100.00))

(defn get-covariance-matrix
  "Get covariance matrix for symbols"
  [symbols]
  (let [covariances (atom {})]
    (doseq [s1 symbols]
      (doseq [s2 symbols]
        (swap! covariances assoc-in [s1 s2]
               (if (= s1 s2)
                 0.04
                 0.02))))
    @covariances))

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

(defn create-risk-calculator
  "Create risk calculation pipeline"
  [& calculators]
  (apply pipe calculators))

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

(defn macd-signal
  "Generate MACD signal"
  [fast-period slow-period signal-period]
  (fn [prices]
    (let [macd (calculate-macd prices fast-period slow-period signal-period)]
      (if (> macd 0)
        :buy
        :sell))))

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

(defn calculate-portfolio-risk
  "Calculate portfolio risk"
  [portfolio]
  (let [weights (calculate-portfolio-weights portfolio)
        covariance-matrix (get-covariance-matrix (keys weights))]
    (Math/sqrt (reduce + (map (fn [[symbol1 weight1]]
                                (reduce + (map (fn [[symbol2 weight2]]
                                                 (* weight1 weight2
                                                    (get-in covariance-matrix [symbol1 symbol2])))
                                               weights)))
                              weights)))))

;; Risk calculation functions
(defn calculate-var
  "Calculate Value at Risk"
  [portfolio confidence-level]
  (fn [returns]
    (let [sorted-returns (sort returns)
          index (int (* (- 1 confidence-level) (count sorted-returns)))]
      (nth sorted-returns index))))

(defn calculate-expected-shortfall
  "Calculate Expected Shortfall (CVaR)"
  [portfolio confidence-level]
  (fn [returns]
    (let [var-fn (calculate-var portfolio confidence-level)
          var-value (var-fn returns)
          tail-returns (filter #(< % var-value) returns)]
      (if (empty? tail-returns)
        var-value
        (/ (reduce + tail-returns) (count tail-returns))))))

(defn calculate-maximum-drawdown
  "Calculate maximum drawdown"
  [portfolio]
  (fn [values]
    (let [peak (atom (first values))
          max-dd (atom 0)]
      (doseq [value values]
        (when (> value @peak)
          (reset! peak value))
        (let [dd (- @peak value)]
          (when (> dd @max-dd)
            (reset! max-dd dd))))
      @max-dd)))

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
                    (apply f result)
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

(defn create-retry-pipeline
  "Create retry pipeline with exponential backoff"
  [f max-retries base-delay]
  (fn [& args]
    (loop [attempt 0]
      (if (>= attempt max-retries)
        (throw (Exception. (str "Function failed after " max-retries " attempts")))
        (try
          (apply f args)
          (catch Exception e
            (if (< attempt (dec max-retries))
              (do
                (Thread/sleep (* base-delay (Math/pow 2 attempt)))
                (recur (inc attempt)))
              (throw e))))))))

(defn create-circuit-breaker
  "Create circuit breaker pattern"
  [f failure-threshold timeout-ms]
  (let [failure-count (atom 0)
        last-failure-time (atom 0)
        state (atom :closed)] ; :closed, :open, :half-open
    (fn [& args]
      (let [now (System/currentTimeMillis)]
        (case @state
          :closed
          (try
            (let [result (apply f args)]
              (reset! failure-count 0)
              result)
            (catch Exception e
              (swap! failure-count inc)
              (reset! last-failure-time now)
              (when (>= @failure-count failure-threshold)
                (reset! state :open))
              (throw e)))
          
          :open
          (if (>= (- now @last-failure-time) timeout-ms)
            (do
              (reset! state :half-open)
              (try
                (let [result (apply f args)]
                  (reset! state :closed)
                  (reset! failure-count 0)
                  result)
                (catch Exception e
                  (reset! last-failure-time now)
                  (throw e))))
            (throw (Exception. "Circuit breaker is open")))
          
          :half-open
          (try
            (let [result (apply f args)]
              (reset! state :closed)
              (reset! failure-count 0)
              result)
            (catch Exception e
              (reset! state :open)
              (reset! last-failure-time now)
              (throw e))))))))

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
                         (rsi-signal 14)
                         (macd-signal 12 26 9))
        
        portfolio-analyzer (create-portfolio-analyzer
                           calculate-portfolio-value
                           calculate-portfolio-weights
                           calculate-portfolio-risk)
        
        risk-calculator (create-risk-calculator
                        (calculate-var {} 0.95)
                        (calculate-expected-shortfall {} 0.95)
                        (calculate-maximum-drawdown {}))]
    
    (fn [market-data]
      (let [transformed-prices (map price-transformer (:prices market-data))
            signals (map signal-generator (partition 20 transformed-prices))
            portfolio-analysis (portfolio-analyzer (:portfolio market-data))
            risk-analysis (risk-calculator (:returns market-data))]
        {:transformed-prices transformed-prices
         :signals signals
         :portfolio-analysis portfolio-analysis
         :risk-analysis risk-analysis}))))

(defn create-data-processing-pipeline
  "Create data processing pipeline"
  []
  (let [data-cleaner (fn [data]
                       (filter #(not (nil? %)) data))
        
        data-transformer (fn [data]
                           (map #(* % 1.1) data))
        
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

(defn demo-currying-partial
  "Demonstrate currying and partial application"
  []
  (println "=== Currying and Partial Application Demo ===")
  
  ;; Currying
  (let [add-three (fn [x y z] (+ x y z))
        curried-add (curry add-three)
        add-five-and-ten (curried-add 5 10)]
    
    (println "1. Currying:")
    (println "   Original function: (fn [x y z] (+ x y z))")
    (println "   Curried with 5 and 10:" (add-five-and-ten 3))
    
    ;; Partial application
    (let [multiply (fn [x y] (* x y))
          multiply-by-five (partial-apply multiply 5)
          multiply-by-five-and-ten (partial-apply multiply 5 10)]
      
      (println "2. Partial application:")
      (println "   multiply-by-five 4:" (multiply-by-five 4))
      (println "   multiply-by-five-and-ten:" (multiply-by-five-and-ten))))

(defn demo-monadic-patterns
  "Demonstrate monadic patterns"
  []
  (println "=== Monadic Patterns Demo ===")
  
  ;; Maybe monad
  (let [safe-divide (fn [x y]
                      (if (zero? y)
                        (->Maybe nil)
                        (->Maybe (/ x y))))
        
        safe-sqrt (fn [x]
                    (if (< x 0)
                      (->Maybe nil)
                      (->Maybe (Math/sqrt x))))
        
        maybe-result (-> (->Maybe 16)
                         (bind safe-sqrt)
                         (bind #(safe-divide % 2)))]
    
    (println "1. Maybe monad:")
    (println "   sqrt(16) / 2:" (:value maybe-result))
    
    ;; Either monad
    (let [safe-divide-either (fn [x y]
                               (if (zero? y)
                                 (->Either "Division by zero" nil)
                                 (->Either nil (/ x y))))
          
          either-result (-> (->Either nil 20)
                            (bind safe-divide-either))]
      
      (println "2. Either monad:")
      (println "   20 / 4:" (:right either-result))
      (println "   20 / 0:" (:left (safe-divide-either 20 0))))))

(defn demo-financial-pipelines
  "Demonstrate financial pipelines"
  []
  (println "=== Financial Pipelines Demo ===")
  
  ;; Trading pipeline
  (let [trading-pipeline (create-trading-pipeline)
        market-data {:prices [100 105 110 108 115 120 118 125 130 128]
                     :portfolio {"AAPL" 100 "GOOGL" 50}
                     :returns [0.05 0.047 0.018 0.065 0.043 0.017 0.059 0.04 0.015]}]
    
    (println "1. Trading pipeline:")
    (let [result (trading-pipeline market-data)]
      (println "   Transformed prices:" (take 5 (:transformed-prices result)))
      (println "   Signals:" (take 3 (:signals result)))
      (println "   Portfolio analysis:" (:portfolio-analysis result))
      (println "   Risk analysis:" (:risk-analysis result))))
  
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
      (println "   Input:" val "-> Result:" (conditional-pipeline val))))
  
  ;; Circuit breaker
  (let [failing-function (fn [x] (if (< x 5) x (throw (Exception. "Function failed"))))
        circuit-breaker (create-circuit-breaker failing-function 2 1000)
        test-values [1 2 3 6 7 8]]
    
    (println "3. Circuit breaker pattern:")
    (doseq [val test-values]
      (try
        (let [result (circuit-breaker val)]
          (println "   Input:" val "-> Result:" result))
        (catch Exception e
          (println "   Input:" val "-> Error:" (.getMessage e)))))))

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

(defn run-all-higher-order-function-demos
  "Run all higher order function demonstrations"
  []
  (println "🎯 === ACTORS Higher Order Functions Comprehensive Demo ===")
  (println)
  (demo-function-composition)
  (println)
  (demo-currying-partial)
  (println)
  (demo-monadic-patterns)
  (println)
  (demo-financial-pipelines)
  (println)
  (demo-advanced-patterns)
  (println)
  (demo-memoization-caching)
  (println)
  (println "🎉 === All Higher Order Function Demos Complete ==="))

(defn -main
  "Main entry point for higher order function demo"
  [& args]
  (run-all-higher-order-function-demos))
