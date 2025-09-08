# 🔄 ACTORS Clojure While Loops System

## *Functional Programming with While Loops for Financial Intelligence*

---

## 🌟 **System Overview**

The **ACTORS Clojure While Loops System** extends the core functional system with comprehensive while loop patterns and examples. In Clojure, we use `loop` and `recur` for iteration instead of traditional while loops, providing powerful and efficient iteration patterns for financial applications.

### **🎯 What's Included**
- ✅ **Basic While Loop Patterns**: Simple iteration with `loop/recur`
- ✅ **Financial While Loops**: Market data processing, portfolio optimization
- ✅ **Async While Loops**: Concurrent processing with `go-loop`
- ✅ **Nested While Loops**: Complex multi-level iteration
- ✅ **Infinite While Loops**: Continuous processing with termination conditions
- ✅ **Risk Management Loops**: Real-time risk monitoring and calculation

---

## 🚀 **Quick Start**

### **Start the System with While Loops**
```bash
cd /Users/stevensloan/ACTORS/CLOJURE
./scripts/start-with-loops.sh
```

### **Run All While Loop Demos**
```clojure
(actors.loop-examples/run-all-loop-demos)
```

---

## 📚 **While Loop Modules**

### **🔄 actors.loops**
Basic while loop patterns and financial applications:

**Key Functions:**
```clojure
;; Basic while loop pattern
(while-loop-example condition-fn body-fn initial-value)

;; Countdown while loop
(countdown-while 5) ; => [5 4 3 2 1]

;; Market data processing
(process-market-data-while market-data threshold)

;; Returns calculation
(calculate-returns-while prices)

;; Signal filtering
(filter-signals-while signals min-confidence)
```

### **🔄 actors.loop-examples**
Comprehensive while loop examples with demos:

**Key Functions:**
```clojure
;; Basic while loops
(demo-basic-while-loops)

;; Financial while loops
(demo-financial-while-loops)

;; Async while loops
(demo-async-while-loops)

;; Infinite while loops
(demo-infinite-while-loops)

;; Run all demos
(run-all-loop-demos)
```

---

## 🎯 **While Loop Patterns**

### **1. Basic While Loop Pattern**
```clojure
(defn simple-while
  "Simple while loop using loop/recur"
  [condition-fn body-fn initial-value]
  (loop [value initial-value]
    (if (condition-fn value)
      (recur (body-fn value))
      value)))

;; Example: Countdown
(simple-while #(> % 0) dec 5) ; => 0
```

### **2. While Loop with Accumulator**
```clojure
(defn while-with-accumulator
  "While loop with accumulator"
  [condition-fn body-fn initial-value]
  (loop [value initial-value
         accumulator []]
    (if (condition-fn value)
      (recur (body-fn value) (conj accumulator value))
      accumulator)))

;; Example: Accumulate values
(while-with-accumulator #(< % 10) inc 1) ; => [1 2 3 4 5 6 7 8 9]
```

### **3. Financial While Loops**
```clojure
;; Compound interest calculation
(defn calculate-compound-interest-while
  [principal rate years]
  (loop [amount principal
         year 0]
    (if (< year years)
      (recur (* amount (+ 1 rate)) (inc year))
      amount)))

;; Portfolio optimization
(defn optimize-portfolio-while
  [target-return max-iterations]
  (loop [iteration 0
         current-allocation [0.4 0.3 0.3]
         best-allocation current-allocation
         best-return 0.0]
    (if (>= iteration max-iterations)
      {:allocation best-allocation :expected-return best-return}
      ;; ... optimization logic
      )))
```

### **4. Async While Loops**
```clojure
;; Async data processing
(defn async-market-data-loop
  [market-channel output-channel]
  (go-loop [processed-count 0]
    (when-let [market-data (<! market-channel)]
      (let [processed-data (assoc market-data 
                                  :processed true 
                                  :processed-count processed-count)]
        (>! output-channel processed-data)
        (recur (inc processed-count))))))
```

### **5. Nested While Loops**
```clojure
;; Analyze multiple portfolios with multiple strategies
(defn analyze-multiple-portfolios-while
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
```

### **6. Infinite While Loops with Termination**
```clojure
;; Market simulation with termination conditions
(defn market-simulation-while
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
```

---

## 🧪 **Demo Examples**

### **Basic While Loops Demo**
```clojure
(actors.loop-examples/demo-basic-while-loops)
```

**Output:**
```
=== Basic While Loops Demo ===
1. Simple while loop (countdown):
   Result: 0
2. While loop with accumulator:
   Accumulated values: [1 2 3 4 5 6 7 8 9]
3. Compound interest calculation:
   $1000 at 5% for 10 years: $ 1629
4. Break-even analysis:
   Break-even in 20 months
=== Basic While Loops Demo Complete ===
```

### **Financial While Loops Demo**
```clojure
(actors.loop-examples/demo-financial-while-loops)
```

**Output:**
```
=== Financial While Loops Demo ===
1. Portfolio optimization:
   Best allocation: (0.6590768495257746 0.7039148846022586 -0.36299173412803337)
   Expected return: 8 %
2. Moving average calculation:
   5-period moving averages: (108 112 114 117 122 124)
3. Trading data processing:
   Processed 2 trades
   Total volume: 5000
=== Financial While Loops Demo Complete ===
```

### **Infinite While Loops Demo**
```clojure
(actors.loop-examples/demo-infinite-while-loops)
```

**Output:**
```
=== Infinite While Loops Demo ===
1. Market simulation:
   Simulated 100 price points
   Price range: 90 - 100
   Final price: 90
=== Infinite While Loops Demo Complete ===
```

---

## 🔧 **Financial Applications**

### **Market Data Processing**
```clojure
;; Process market data while price is above threshold
(defn process-market-data-while
  [market-data threshold]
  (loop [data market-data
         processed []]
    (if (and (seq data) (> (:price (first data)) threshold))
      (let [current (first data)
            updated (assoc current :processed true)]
        (recur (rest data) (conj processed updated)))
      processed)))
```

### **Portfolio Optimization**
```clojure
;; Optimize portfolio allocation using while loop
(defn optimize-portfolio-while
  [target-return max-iterations]
  (loop [iteration 0
         current-allocation [0.4 0.3 0.3]
         best-allocation current-allocation
         best-return 0.0]
    (if (>= iteration max-iterations)
      {:allocation best-allocation :expected-return best-return}
      ;; ... optimization logic
      )))
```

### **Risk Monitoring**
```clojure
;; Monitor risk while within limits
(defn monitor-risk-while
  [portfolio risk-limits]
  (loop [check-count 0
         violations []
         current-portfolio portfolio]
    (let [current-var (calculate-var current-portfolio)
          var-violation? (> current-var (:var-limit risk-limits))]
      (if var-violation?
        (let [violation {:type :var-violation
                         :value current-var
                         :timestamp (System/currentTimeMillis)}]
          (recur (inc check-count) (conj violations violation) current-portfolio))
        {:check-count check-count :violations violations :status :safe}))))
```

---

## 🚀 **Async While Loops**

### **Data Streaming**
```clojure
;; Async while loop for data streaming
(defn async-data-stream-while
  [input-channel output-channel]
  (go-loop [message-count 0]
    (when-let [data (<! input-channel)]
      (let [processed-data (assoc data 
                                  :message-id message-count
                                  :processed-at (System/currentTimeMillis))]
        (>! output-channel processed-data)
        (recur (inc message-count))))))
```

### **Risk Monitoring**
```clojure
;; Async while loop for risk monitoring
(defn async-risk-monitoring-while
  [portfolio-channel alert-channel]
  (go-loop [monitoring-active true]
    (when monitoring-active
      (when-let [portfolio (<! portfolio-channel)]
        (let [risk-level (calculate-portfolio-risk portfolio)]
          (when (> risk-level 0.8)
            (>! alert-channel {:type :high-risk
                               :portfolio-id (:id portfolio)
                               :risk-level risk-level})))
        (recur true)))))
```

---

## 🎯 **Best Practices**

### **1. Use `loop/recur` for Iteration**
```clojure
;; Good: Use loop/recur
(loop [value initial-value]
  (if (condition value)
    (recur (transform value))
    value))

;; Avoid: Don't use while loops (not idiomatic in Clojure)
```

### **2. Accumulate Results Efficiently**
```clojure
;; Good: Use vectors for accumulation
(loop [remaining items
       result []]
  (if (seq remaining)
    (recur (rest remaining) (conj result (process (first remaining))))
    result))
```

### **3. Handle Termination Conditions**
```clojure
;; Good: Clear termination conditions
(loop [iteration 0
       max-iterations 1000]
  (if (>= iteration max-iterations)
    result
    (recur (inc iteration))))
```

### **4. Use Async Loops for Concurrency**
```clojure
;; Good: Use go-loop for async processing
(go-loop [count 0]
  (when-let [data (<! input-channel)]
    (process-data data)
    (recur (inc count))))
```

---

## 🧪 **Testing While Loops**

### **Run Individual Demos**
```clojure
;; Test basic while loops
(actors.loop-examples/demo-basic-while-loops)

;; Test financial while loops
(actors.loop-examples/demo-financial-while-loops)

;; Test async while loops
(actors.loop-examples/demo-async-while-loops)

;; Test infinite while loops
(actors.loop-examples/demo-infinite-while-loops)
```

### **Run All Demos**
```clojure
;; Run comprehensive demo
(actors.loop-examples/run-all-loop-demos)
```

---

## 🎉 **Success!**

The ACTORS Clojure While Loops System is now **WORKING** and ready for development! You can:

- ✅ Start the system with `./scripts/start-with-loops.sh`
- ✅ Run while loop demos with `(actors.loop-examples/run-all-loop-demos)`
- ✅ Use basic while loop patterns for iteration
- ✅ Implement financial while loops for market data processing
- ✅ Create async while loops for concurrent processing
- ✅ Build nested while loops for complex analysis
- ✅ Design infinite while loops with termination conditions

**Welcome to functional programming with while loops for financial intelligence! 🔄**
