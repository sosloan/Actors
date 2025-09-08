(ns actors.loops
  "While loops and iteration patterns for ACTORS system"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >!]]
            [actors.simple-core :as core]))

;; =============================================================================
;; Traditional While Loop Patterns (using loop/recur)
;; =============================================================================

(defn while-loop-example
  "Traditional while loop using loop/recur"
  [condition-fn body-fn initial-value]
  (loop [value initial-value]
    (if (condition-fn value)
      (recur (body-fn value))
      value)))

(defn countdown-while
  "Countdown using while loop pattern"
  [start]
  (loop [n start
         result []]
    (if (> n 0)
      (recur (dec n) (conj result n))
      result)))

(defn accumulate-while
  "Accumulate values while condition is true"
  [condition-fn value-fn initial-value]
  (loop [value initial-value
         result []]
    (if (condition-fn value)
      (recur (value-fn value) (conj result value))
      result)))

;; =============================================================================
;; Market Data Processing Loops
;; =============================================================================

(defn process-market-data-while
  "Process market data while price is above threshold"
  [market-data threshold]
  (loop [data market-data
         processed []]
    (if (and (seq data) (> (:price (first data)) threshold))
      (let [current (first data)
            updated (assoc current :processed true :timestamp (System/currentTimeMillis))]
        (recur (rest data) (conj processed updated)))
      processed)))

(defn calculate-returns-while
  "Calculate returns using while loop pattern"
  [prices]
  (loop [remaining prices
         returns []]
    (if (< (count remaining) 2)
      returns
      (let [current (first remaining)
            next-price (second remaining)
            return (/ (- next-price current) current)]
        (recur (rest remaining) (conj returns return))))))

(defn filter-signals-while
  "Filter trading signals while confidence is above threshold"
  [signals min-confidence]
  (loop [remaining signals
         filtered []]
    (if (seq remaining)
      (let [signal (first remaining)]
        (if (>= (:confidence signal) min-confidence)
          (recur (rest remaining) (conj filtered signal))
          (recur (rest remaining) filtered)))
      filtered)))

;; =============================================================================
;; Portfolio Management Loops
;; =============================================================================

(defn rebalance-portfolio-while
  "Rebalance portfolio while positions are out of target allocation"
  [positions target-allocations tolerance]
  (loop [current-positions positions
         adjustments []]
    (let [total-value (reduce + (map :value current-positions))
          needs-adjustment (some (fn [pos]
                                   (let [target-allocation (get target-allocations (:symbol pos) 0)
                                         current-allocation (/ (:value pos) total-value)
                                         difference (Math/abs (- current-allocation target-allocation))]
                                     (> difference tolerance)))
                                 current-positions)]
      (if needs-adjustment
        (let [adjusted-positions (map (fn [pos]
                                        (let [target-allocation (get target-allocations (:symbol pos) 0)
                                              target-value (* total-value target-allocation)
                                              current-value (:value pos)
                                              adjustment (- target-value current-value)]
                                          (assoc pos :adjustment adjustment)))
                                      current-positions)]
          (recur adjusted-positions (conj adjustments (first adjusted-positions))))
        adjustments))))

(defn calculate-portfolio-value-while
  "Calculate portfolio value while processing positions"
  [positions]
  (loop [remaining positions
         total-value 0.0]
    (if (seq remaining)
      (let [position (first remaining)
            position-value (* (:quantity position) (:price position))]
        (recur (rest remaining) (+ total-value position-value)))
      total-value)))

;; =============================================================================
;; Risk Management Loops
;; =============================================================================

(defn calculate-var-while
  "Calculate Value at Risk using while loop"
  [returns confidence-level]
  (let [sorted-returns (sort returns)
        index (int (* confidence-level (count sorted-returns)))]
    (loop [i 0
           result nil]
      (if (< i (count sorted-returns))
        (if (= i index)
          (recur (inc i) (nth sorted-returns i))
          (recur (inc i) result))
        result))))

(defn stress-test-while
  "Perform stress testing while scenarios remain"
  [portfolio scenarios]
  (loop [remaining-scenarios scenarios
         results []]
    (if (seq remaining-scenarios)
      (let [scenario (first remaining-scenarios)
            stressed-portfolio (map (fn [position]
                                      (let [stress-factor (:stress-factor scenario)
                                            stressed-price (* (:price position) stress-factor)]
                                        (assoc position :stressed-price stressed-price)))
                                    (:positions portfolio))
            portfolio-value (calculate-portfolio-value-while stressed-portfolio)
            result {:scenario (:name scenario)
                    :original-value (:total-value portfolio)
                    :stressed-value portfolio-value
                    :loss (- (:total-value portfolio) portfolio-value)}]
        (recur (rest remaining-scenarios) (conj results result)))
      results)))

;; =============================================================================
;; Async While Loops
;; =============================================================================

(defn async-market-data-loop
  "Async while loop for processing market data"
  [market-channel output-channel]
  (go-loop [processed-count 0]
    (when-let [market-data (<! market-channel)]
      (let [processed-data (assoc market-data 
                                  :processed true 
                                  :processed-count processed-count
                                  :timestamp (System/currentTimeMillis))]
        (>! output-channel processed-data)
        (recur (inc processed-count))))))

(defn async-signal-processing-loop
  "Async while loop for processing trading signals"
  [signal-channel processor-fn]
  (go-loop [signal-count 0]
    (when-let [signal (<! signal-channel)]
      (let [processed-signal (processor-fn signal signal-count)]
        (println "Processed signal" signal-count ":" (:type processed-signal))
        (recur (inc signal-count))))))

;; =============================================================================
;; Infinite While Loops (with termination conditions)
;; =============================================================================

(defn infinite-market-simulation
  "Infinite while loop for market simulation (with termination condition)"
  [initial-price volatility max-iterations]
  (loop [price initial-price
         iteration 0
         price-history [initial-price]]
    (if (>= iteration max-iterations)
      price-history
      (let [random-change (* volatility (- (rand) 0.5))
            new-price (* price (+ 1 random-change))]
        (recur new-price (inc iteration) (conj price-history new-price))))))

(defn continuous-risk-monitoring
  "Continuous risk monitoring with while loop"
  [portfolio risk-limits max-checks]
  (loop [check-count 0
         violations []]
    (if (>= check-count max-checks)
      violations
      (let [current-var (calculate-var-while (:returns portfolio) 0.05)
            violation (if (> current-var (:var-limit risk-limits))
                        {:type :var-violation
                         :value current-var
                         :limit (:var-limit risk-limits)
                         :timestamp (System/currentTimeMillis)}
                        nil)]
        (recur (inc check-count) 
               (if violation (conj violations violation) violations))))))

;; =============================================================================
;; Nested While Loops
;; =============================================================================

(defn nested-portfolio-analysis
  "Nested while loops for portfolio analysis"
  [portfolios strategies]
  (loop [remaining-portfolios portfolios
         results []]
    (if (seq remaining-portfolios)
      (let [portfolio (first remaining-portfolios)
            portfolio-results (loop [remaining-strategies strategies
                                     strategy-results []]
                                (if (seq remaining-strategies)
                                  (let [strategy (first remaining-strategies)
                                        result (strategy portfolio)]
                                    (recur (rest remaining-strategies) 
                                           (conj strategy-results result)))
                                  strategy-results))]
        (recur (rest remaining-portfolios) 
               (conj results {:portfolio (:name portfolio) 
                              :results portfolio-results})))
      results)))

;; =============================================================================
;; Demo Functions
;; =============================================================================

(defn demo-while-loops
  "Demonstrate various while loop patterns"
  []
  (println "=== ACTORS While Loops Demo ===")
  
  ;; Basic while loop
  (println "1. Countdown while loop:")
  (let [countdown (countdown-while 5)]
    (println "   Countdown from 5:" countdown))
  
  ;; Market data processing
  (println "2. Market data processing while loop:")
  (let [market-data [(core/create-market-data "AAPL" 150.25 1000000 0.18)
                     (core/create-market-data "GOOGL" 2800.00 500000 0.15)
                     (core/create-market-data "TSLA" 250.50 2000000 0.25)]
        processed (process-market-data-while market-data 200.0)]
    (println "   Processed" (count processed) "market data entries above $200"))
  
  ;; Returns calculation
  (println "3. Returns calculation while loop:")
  (let [prices [100.0 105.0 110.0 108.0 115.0]
        returns (calculate-returns-while prices)]
    (println "   Returns:" returns))
  
  ;; Signal filtering
  (println "4. Signal filtering while loop:")
  (let [signals [(core/create-trading-signal :buy 0.9 {:strategy "ma"})
                 (core/create-trading-signal :sell 0.3 {:strategy "rsi"})
                 (core/create-trading-signal :hold 0.8 {:strategy "bollinger"})]
        filtered (filter-signals-while signals 0.5)]
    (println "   Filtered" (count filtered) "signals with confidence >= 0.5"))
  
  ;; Portfolio value calculation
  (println "5. Portfolio value calculation while loop:")
  (let [positions [{:symbol "AAPL" :quantity 100 :price 150.25}
                   {:symbol "GOOGL" :quantity 50 :price 2800.00}
                   {:symbol "TSLA" :quantity 200 :price 250.50}]
        total-value (calculate-portfolio-value-while positions)]
    (println "   Total portfolio value: $" total-value))
  
  ;; Market simulation
  (println "6. Market simulation while loop:")
  (let [price-history (infinite-market-simulation 100.0 0.02 10)]
    (println "   Simulated prices:" (take 5 price-history) "...")
    (println "   Final price:" (last price-history)))
  
  (println "=== While Loops Demo Complete ==="))

(defn demo-async-loops
  "Demonstrate async while loops"
  []
  (println "=== ACTORS Async While Loops Demo ===")
  
  (let [market-channel (chan 10)
        output-channel (chan 10)
        signal-channel (chan 10)]
    
    ;; Start async market data processing
    (async-market-data-loop market-channel output-channel)
    
    ;; Start async signal processing
    (async-signal-processing-loop signal-channel 
                                  (fn [signal count] 
                                    (assoc signal :processed-count count)))
    
    ;; Send some test data
    (go
      (doseq [i (range 3)]
        (>! market-channel (core/create-market-data "AAPL" (+ 150 i) 1000000 0.18))
        (>! signal-channel (core/create-trading-signal :buy 0.8 {:strategy "ma"})))
      
      ;; Close channels
      (async/close! market-channel)
      (async/close! signal-channel))
    
    ;; Read results
    (go
      (loop [count 0]
        (when-let [data (<! output-channel)]
          (println "Received processed market data:" (:symbol data) "count:" (:processed-count data))
          (recur (inc count)))))
    
    (println "Async loops started - check output above"))
  
  (println "=== Async Loops Demo Complete ==="))

(defn -main
  "Main entry point for loops demo"
  [& args]
  (demo-while-loops)
  (println)
  (demo-async-loops))
