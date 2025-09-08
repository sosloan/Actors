(ns actors.loop-examples
  "Comprehensive while loop examples for ACTORS system"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >!]]
            [actors.simple-core :as core]))

;; =============================================================================
;; Basic While Loop Patterns
;; =============================================================================

(defn simple-while
  "Simple while loop using loop/recur"
  [condition-fn body-fn initial-value]
  (loop [value initial-value]
    (if (condition-fn value)
      (recur (body-fn value))
      value)))

(defn while-with-accumulator
  "While loop with accumulator"
  [condition-fn body-fn initial-value]
  (loop [value initial-value
         accumulator []]
    (if (condition-fn value)
      (recur (body-fn value) (conj accumulator value))
      accumulator)))

;; =============================================================================
;; Financial While Loops
;; =============================================================================

(defn calculate-compound-interest-while
  "Calculate compound interest using while loop"
  [principal rate years]
  (loop [amount principal
         year 0]
    (if (< year years)
      (recur (* amount (+ 1 rate)) (inc year))
      amount)))

(defn find-break-even-while
  "Find break-even point using while loop"
  [initial-cost monthly-revenue monthly-cost]
  (loop [month 0
         cumulative-cost initial-cost
         cumulative-revenue 0.0]
    (if (>= cumulative-revenue cumulative-cost)
      {:month month :break-even true}
      (recur (inc month) 
             (+ cumulative-cost monthly-cost)
             (+ cumulative-revenue monthly-revenue)))))

(defn optimize-portfolio-while
  "Optimize portfolio allocation using while loop"
  [target-return max-iterations]
  (loop [iteration 0
         current-allocation [0.4 0.3 0.3] ; [stocks, bonds, cash]
         best-allocation current-allocation
         best-return 0.0]
    (if (>= iteration max-iterations)
      {:allocation best-allocation :expected-return best-return}
      (let [new-allocation (map #(+ % (- (rand 0.1) 0.05)) current-allocation)
            normalized-allocation (let [sum (reduce + new-allocation)]
                                   (map #(/ % sum) new-allocation))
            expected-return (* (first normalized-allocation) 0.12) ; 12% stock return
            improved? (> expected-return best-return)]
        (recur (inc iteration)
               normalized-allocation
               (if improved? normalized-allocation best-allocation)
               (if improved? expected-return best-return))))))

;; =============================================================================
;; Data Processing While Loops
;; =============================================================================

(defn process-trading-data-while
  "Process trading data while conditions are met"
  [trading-data]
  (loop [remaining-data trading-data
         processed []
         total-volume 0]
    (if (seq remaining-data)
      (let [current-trade (first remaining-data)
            volume (:volume current-trade)
            price (:price current-trade)]
        (if (and (> volume 1000) (< price 1000)) ; Process while volume > 1000 and price < 1000
          (recur (rest remaining-data)
                 (conj processed (assoc current-trade :processed true))
                 (+ total-volume volume))
          (recur (rest remaining-data) processed total-volume)))
      {:processed-trades processed :total-volume total-volume})))

(defn calculate-moving-average-while
  "Calculate moving average using while loop"
  [prices window-size]
  (loop [remaining-prices prices
         moving-averages []]
    (if (< (count remaining-prices) window-size)
      moving-averages
      (let [window (take window-size remaining-prices)
            average (/ (reduce + window) window-size)]
        (recur (rest remaining-prices) (conj moving-averages average))))))

;; =============================================================================
;; Helper Functions
;; =============================================================================

(defn calculate-var
  "Calculate Value at Risk (simplified)"
  [portfolio]
  (* (:volatility portfolio) 1.645)) ; 95% confidence

(defn calculate-max-drawdown
  "Calculate maximum drawdown (simplified)"
  [portfolio]
  (* (:volatility portfolio) 0.5)) ; Simplified calculation

(defn calculate-portfolio-risk
  "Calculate portfolio risk level"
  [portfolio]
  (rand)) ; Simplified - returns random risk level

;; =============================================================================
;; Risk Management While Loops
;; =============================================================================

(defn monitor-risk-while
  "Monitor risk while within limits"
  [portfolio risk-limits]
  (loop [check-count 0
         violations []
         current-portfolio portfolio]
    (let [current-var (calculate-var current-portfolio)
          max-drawdown (calculate-max-drawdown current-portfolio)
          var-violation? (> current-var (:var-limit risk-limits))
          drawdown-violation? (> max-drawdown (:drawdown-limit risk-limits))]
      (if (or var-violation? drawdown-violation?)
        (let [violation {:type (cond var-violation? :var-violation
                                     drawdown-violation? :drawdown-violation)
                         :value (cond var-violation? current-var
                                      drawdown-violation? max-drawdown)
                         :timestamp (System/currentTimeMillis)}]
          (recur (inc check-count) (conj violations violation) current-portfolio))
        {:check-count check-count :violations violations :status :safe}))))

;; =============================================================================
;; Async While Loops
;; =============================================================================

(defn async-data-stream-while
  "Async while loop for data streaming"
  [input-channel output-channel]
  (go-loop [message-count 0]
    (when-let [data (<! input-channel)]
      (let [processed-data (assoc data 
                                  :message-id message-count
                                  :processed-at (System/currentTimeMillis))]
        (>! output-channel processed-data)
        (recur (inc message-count))))))

(defn async-risk-monitoring-while
  "Async while loop for risk monitoring"
  [portfolio-channel alert-channel]
  (go-loop [monitoring-active true]
    (when monitoring-active
      (when-let [portfolio (<! portfolio-channel)]
        (let [risk-level (calculate-portfolio-risk portfolio)]
          (when (> risk-level 0.8) ; High risk threshold
            (>! alert-channel {:type :high-risk
                               :portfolio-id (:id portfolio)
                               :risk-level risk-level
                               :timestamp (System/currentTimeMillis)})))
        (recur true)))))

;; =============================================================================
;; Nested While Loops
;; =============================================================================

(defn analyze-multiple-portfolios-while
  "Nested while loops for analyzing multiple portfolios"
  [portfolios strategies]
  (loop [remaining-portfolios portfolios
         analysis-results []]
    (if (seq remaining-portfolios)
      (let [portfolio (first remaining-portfolios)
            portfolio-analysis (loop [remaining-strategies strategies
                                      strategy-results []]
                                 (if (seq remaining-strategies)
                                   (let [strategy (first remaining-strategies)
                                         result (strategy portfolio)]
                                     (recur (rest remaining-strategies)
                                            (conj strategy-results result)))
                                   strategy-results))]
        (recur (rest remaining-portfolios)
               (conj analysis-results {:portfolio-id (:id portfolio)
                                       :analysis portfolio-analysis})))
      analysis-results)))

;; =============================================================================
;; Infinite While Loops with Termination
;; =============================================================================

(defn market-simulation-while
  "Infinite market simulation with termination condition"
  [initial-price volatility max-price-change]
  (loop [price initial-price
         iteration 0
         price-history [initial-price]
         running true]
    (if (not running)
      price-history
      (let [change (* volatility (- (rand) 0.5))
            new-price (* price (+ 1 change))
            price-change-ratio (/ (Math/abs (- new-price initial-price)) initial-price)
            should-terminate? (or (> price-change-ratio max-price-change)
                                  (> iteration 1000))]
        (recur new-price
               (inc iteration)
               (conj price-history new-price)
               (not should-terminate?))))))

;; =============================================================================
;; Demo Functions
;; =============================================================================

(defn demo-basic-while-loops
  "Demonstrate basic while loop patterns"
  []
  (println "=== Basic While Loops Demo ===")
  
  ;; Simple while loop
  (println "1. Simple while loop (countdown):")
  (let [result (simple-while #(> % 0) dec 5)]
    (println "   Result:" result))
  
  ;; While with accumulator
  (println "2. While loop with accumulator:")
  (let [result (while-with-accumulator #(< % 10) inc 1)]
    (println "   Accumulated values:" result))
  
  ;; Compound interest
  (println "3. Compound interest calculation:")
  (let [result (calculate-compound-interest-while 1000 0.05 10)]
    (println "   $1000 at 5% for 10 years: $" (Math/round (double result))))
  
  ;; Break-even analysis
  (println "4. Break-even analysis:")
  (let [result (find-break-even-while 10000 2000 1500)]
    (println "   Break-even in" (:month result) "months"))
  
  (println "=== Basic While Loops Demo Complete ==="))

(defn demo-financial-while-loops
  "Demonstrate financial while loops"
  []
  (println "=== Financial While Loops Demo ===")
  
  ;; Portfolio optimization
  (println "1. Portfolio optimization:")
  (let [result (optimize-portfolio-while 0.08 100)]
    (println "   Best allocation:" (:allocation result))
    (println "   Expected return:" (Math/round (double (* (:expected-return result) 100))) "%"))
  
  ;; Moving average calculation
  (println "2. Moving average calculation:")
  (let [prices [100 105 110 108 115 120 118 125 130 128]
        moving-averages (calculate-moving-average-while prices 5)]
    (println "   5-period moving averages:" (map #(Math/round (double %)) moving-averages)))
  
  ;; Trading data processing
  (println "3. Trading data processing:")
  (let [trading-data [{:symbol "AAPL" :price 150.25 :volume 2000}
                      {:symbol "GOOGL" :price 2800.00 :volume 500}
                      {:symbol "TSLA" :price 250.50 :volume 3000}]
        result (process-trading-data-while trading-data)]
    (println "   Processed" (count (:processed-trades result)) "trades")
    (println "   Total volume:" (:total-volume result)))
  
  (println "=== Financial While Loops Demo Complete ==="))

(defn demo-async-while-loops
  "Demonstrate async while loops"
  []
  (println "=== Async While Loops Demo ===")
  
  (let [input-channel (chan 10)
        output-channel (chan 10)
        alert-channel (chan 10)]
    
    ;; Start async data streaming
    (async-data-stream-while input-channel output-channel)
    
    ;; Start async risk monitoring
    (async-risk-monitoring-while input-channel alert-channel)
    
    ;; Send test data
    (go
      (doseq [i (range 3)]
        (>! input-channel {:id (str "portfolio-" i) :data (rand)}))
      (async/close! input-channel))
    
    ;; Read results
    (go
      (loop [count 0]
        (when-let [data (<! output-channel)]
          (println "Processed data:" (:message-id data))
          (recur (inc count)))))
    
    (go
      (when-let [alert (<! alert-channel)]
        (println "Risk alert:" (:type alert))))
    
    (println "Async loops started - check output above"))
  
  (println "=== Async While Loops Demo Complete ==="))

(defn demo-infinite-while-loops
  "Demonstrate infinite while loops with termination"
  []
  (println "=== Infinite While Loops Demo ===")
  
  ;; Market simulation
  (println "1. Market simulation:")
  (let [price-history (market-simulation-while 100.0 0.02 0.1)]
    (println "   Simulated" (count price-history) "price points")
    (println "   Price range:" (Math/round (double (apply min price-history))) "-" (Math/round (double (apply max price-history))))
    (println "   Final price:" (Math/round (double (last price-history)))))
  
  (println "=== Infinite While Loops Demo Complete ==="))

(defn run-all-loop-demos
  "Run all while loop demonstrations"
  []
  (println "🎯 === ACTORS While Loops Comprehensive Demo ===")
  (println)
  (demo-basic-while-loops)
  (println)
  (demo-financial-while-loops)
  (println)
  (demo-async-while-loops)
  (println)
  (demo-infinite-while-loops)
  (println)
  (println "🎉 === All While Loop Demos Complete ==="))

(defn -main
  "Main entry point for loop examples"
  [& args]
  (run-all-loop-demos))
