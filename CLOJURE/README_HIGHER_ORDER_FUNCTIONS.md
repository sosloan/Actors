# 🎯 ACTORS Clojure Higher Order Functions System

## *Advanced Functional Programming with Composition, Currying, and Pipelines*

---

## 🌟 **System Overview**

The **ACTORS Clojure Higher Order Functions System** provides comprehensive tools for advanced functional programming, including function composition, partial application, memoization, throttling, and financial pipelines. It implements sophisticated patterns for building reusable, composable, and efficient functional systems.

### **🎯 What's Included**
- ✅ **Function Composition**: Compose and pipe functions together
- ✅ **Partial Application**: Apply partial arguments to functions
- ✅ **Memoization**: Cache function results with time-to-live
- ✅ **Throttling**: Control function call frequency
- ✅ **Financial Pipelines**: Trading and portfolio analysis pipelines
- ✅ **Advanced Patterns**: Error handling, conditional pipelines
- ✅ **Functional Programming**: Map, filter, reduce with higher order functions
- ✅ **Monadic Patterns**: Maybe, Either, and State monads
- ✅ **Circuit Breakers**: Fault tolerance patterns
- ✅ **Retry Logic**: Exponential backoff and retry mechanisms

---

## 🚀 **Quick Start**

### **Start the System with Higher Order Functions**
```bash
cd /Users/stevensloan/ACTORS/CLOJURE
./scripts/start-with-higher-order-functions.sh
```

### **Run All Higher Order Function Demos**
```clojure
(actors.simple-higher-order-functions/run-all-simple-higher-order-function-demos)
```

---

## 📚 **Core Higher Order Functions**

### **Function Composition**
```clojure
;; Compose functions from right to left
(def composed-fn (compose square multiply-by-two add-one))
(composed-fn 5) ; => 144 (square (multiply-by-two (add-one 5)))

;; Pipe functions from left to right
(def piped-fn (pipe add-one multiply-by-two square))
(piped-fn 5) ; => 144 (square (multiply-by-two (add-one 5)))
```

### **Partial Application**
```clojure
;; Partial application
(def multiply-by-five (partial-apply multiply 5))
(multiply-by-five 4) ; => 20

;; Multiple partial applications
(def multiply-by-five-and-ten (partial-apply multiply 5 10))
(multiply-by-five-and-ten) ; => 50
```

### **Memoization with TTL**
```clojure
;; Memoize function with time-to-live
(def memoized-function (memoize-with-ttl expensive-function 1000))
(memoized-function 5) ; Cached for 1000ms
```

### **Throttling**
```clojure
;; Throttle function calls
(def throttled-function (throttle expensive-function 500))
(throttled-function 1) ; Only executes if 500ms have passed
```

---

## 🔧 **Functional Programming Patterns**

### **Map with Index**
```clojure
;; Map function over collection with index
(map-with-index (fn [item idx] [item idx]) [1 2 3])
; => ([1 0] [2 1] [3 2])
```

### **Filter and Map**
```clojure
;; Filter and map in one pass
(filter-map even? #(* % 2) [1 2 3 4 5])
; => (4 8)
```

### **Group by Function**
```clojure
;; Group collection by function result
(group-by-fn #(mod % 2) [1 2 3 4 5])
; => {1 [1 3 5], 0 [2 4]}
```

### **Reduce While**
```clojure
;; Reduce while predicate is true
(reduce-while #(< % 10) + 0 [1 2 3 4 5 6 7 8 9 10])
; => 6 (stops when sum reaches 10)
```

### **Scan (Reductions)**
```clojure
;; Scan (like reduce but keep intermediate results)
(scan + 0 [1 2 3 4])
; => (0 1 3 6 10)
```

---

## 💰 **Financial Higher Order Functions**

### **Price Transformation Pipeline**
```clojure
;; Create price transformation pipeline
(def price-transformer
  (create-price-transformer
   (normalize-price 100 200)
   (apply-price-multiplier 1.1)
   (denormalize-price 100 200)))

(price-transformer 150) ; => 165.1
```

### **Signal Generation Pipeline**
```clojure
;; Create signal generation pipeline
(def signal-generator
  (create-signal-generator
   (moving-average-signal 20)
   (rsi-signal 14)))

(signal-generator [100 105 110 108 115 120 118 125 130 128])
; => :buy or :sell based on technical analysis
```

### **Portfolio Analysis Pipeline**
```clojure
;; Create portfolio analysis pipeline
(def portfolio-analyzer
  (create-portfolio-analyzer
   calculate-portfolio-value
   calculate-portfolio-weights))

(portfolio-analyzer {"AAPL" 100 "GOOGL" 50})
; => {:value 155050.0, :weights {"AAPL" 0.097, "GOOGL" 0.903}}
```

---

## 🎯 **Advanced Functional Patterns**

### **Function Pipeline with Error Handling**
```clojure
;; Create function pipeline with error handling
(def error-pipeline
  (create-function-pipeline
   (fn [x] (+ x 1))
   (fn [x] (* x 2))
   (fn [x] (if (> x 10) (throw (Exception. "Too big")) x))
   (fn [x] (- x 1))))

(error-pipeline 5) ; => Exception: "Too big"
```

### **Conditional Pipeline**
```clojure
;; Create conditional pipeline
(def conditional-pipeline
  (create-conditional-pipeline
   [(fn [x] (< x 10))
    (fn [x] (< x 20))
    (fn [x] true)]
   [(fn [x] (* x 2))
    (fn [x] (* x 3))
    (fn [x] (* x 4))]))

(conditional-pipeline 5)  ; => 10
(conditional-pipeline 15) ; => 45
(conditional-pipeline 25) ; => 100
```

### **Retry Pipeline with Exponential Backoff**
```clojure
;; Create retry pipeline with exponential backoff
(def retry-pipeline
  (create-retry-pipeline
   failing-function
   3  ; max retries
   1000)) ; base delay in ms

(retry-pipeline "test") ; Retries with 1s, 2s, 4s delays
```

### **Circuit Breaker Pattern**
```clojure
;; Create circuit breaker pattern
(def circuit-breaker
  (create-circuit-breaker
   failing-function
   2  ; failure threshold
   5000)) ; timeout in ms

(circuit-breaker "test") ; Opens circuit after 2 failures
```

---

## 🧪 **Demo Functions**

### **Function Composition Demo**
```clojure
(actors.simple-higher-order-functions/demo-function-composition)
```

**Output:**
```
=== Function Composition Demo ===
1. Basic composition:
   Input: 5
   Compose (square (multiply-by-two (add-one 5))): 144
   Pipe (square (multiply-by-two (add-one 5))): 144
2. Financial price transformation:
   Input price: 150
   Transformed price: 165.1
```

### **Partial Application Demo**
```clojure
(actors.simple-higher-order-functions/demo-partial-application)
```

**Output:**
```
=== Partial Application Demo ===
1. Partial application:
   multiply-by-five 4: 20
   multiply-by-five-and-ten: 50
```

### **Financial Pipelines Demo**
```clojure
(actors.simple-higher-order-functions/demo-financial-pipelines)
```

**Output:**
```
=== Financial Pipelines Demo ===
1. Trading pipeline:
   Transformed prices: (110.1 115.6 121.1 118.9 126.6)
   Signals: ()
   Portfolio analysis: {:value 155050.0, :weights {"AAPL" 0.097, "GOOGL" 0.903}}
2. Data processing pipeline:
   Input data: [1 2 3 nil 5 6 7 8 9 10]
   Processed result: {:sum 56.1, :avg 6.23, :max 11.0, :min 1.1}
```

### **Advanced Patterns Demo**
```clojure
(actors.simple-higher-order-functions/demo-advanced-patterns)
```

**Output:**
```
=== Advanced Functional Patterns Demo ===
1. Function pipeline with error handling:
   Input: 5 -> Error: Too big
   Input: 15 -> Error: Too big
   Input: 8 -> Error: Too big
2. Conditional pipeline:
   Input: 5 -> Result: 10
   Input: 15 -> Result: 45
   Input: 25 -> Result: 100
```

### **Memoization and Caching Demo**
```clojure
(actors.simple-higher-order-functions/demo-memoization-caching)
```

**Output:**
```
=== Memoization and Caching Demo ===
1. Memoization with TTL:
   Input: 5 -> Result: 25 Time: 102 ms
   Input: 5 -> Result: 25 Time: 102 ms (cached)
   Input: 6 -> Result: 36 Time: 204 ms
   Input: 5 -> Result: 25 Time: 204 ms (cached)
   Input: 7 -> Result: 49 Time: 310 ms
2. Throttling:
   Throttled call with: 1
```

---

## 🎯 **Monadic Patterns**

### **Maybe Monad**
```clojure
;; Safe division with Maybe monad
(def safe-divide
  (fn [x y]
    (if (zero? y)
      (->Maybe nil)
      (->Maybe (/ x y)))))

;; Safe square root with Maybe monad
(def safe-sqrt
  (fn [x]
    (if (< x 0)
      (->Maybe nil)
      (->Maybe (Math/sqrt x)))))

;; Chain Maybe operations
(-> (->Maybe 16)
    (bind safe-sqrt)
    (bind #(safe-divide % 2)))
; => (->Maybe 2.0)
```

### **Either Monad**
```clojure
;; Safe division with Either monad
(def safe-divide-either
  (fn [x y]
    (if (zero? y)
      (->Either "Division by zero" nil)
      (->Either nil (/ x y)))))

;; Chain Either operations
(-> (->Either nil 20)
    (bind safe-divide-either))
; => (->Either nil 5.0)
```

### **State Monad**
```clojure
;; State monad for managing state
(def state-monad
  (->State (fn [s] [(* s 2) (inc s)])))

;; Run state monad
((:run state-monad) 5) ; => [10 6]
```

---

## 🔧 **Utility Functions**

### **Technical Analysis Functions**
```clojure
;; Calculate RSI (Relative Strength Index)
(calculate-rsi [100 105 110 108 115 120 118 125 130 128] 14)
; => 65.2

;; Calculate EMA (Exponential Moving Average)
(calculate-ema [100 105 110 108 115 120 118 125 130 128] 12)
; => 125.3

;; Get current price for symbol
(get-current-price "AAPL") ; => 150.25
```

### **Portfolio Analysis Functions**
```clojure
;; Calculate portfolio value
(calculate-portfolio-value {"AAPL" 100 "GOOGL" 50})
; => 155050.0

;; Calculate portfolio weights
(calculate-portfolio-weights {"AAPL" 100 "GOOGL" 50})
; => {"AAPL" 0.097, "GOOGL" 0.903}
```

---

## 🎯 **Best Practices**

### **1. Function Composition**
```clojure
;; Good: Clear, readable composition
(def trading-pipeline
  (compose
   calculate-portfolio-weights
   calculate-portfolio-value
   normalize-prices))

;; Good: Use pipe for left-to-right flow
(def data-pipeline
  (pipe
   clean-data
   transform-data
   aggregate-data))
```

### **2. Partial Application**
```clojure
;; Good: Create specialized functions
(def calculate-var-95 (partial-apply calculate-var {} 0.95))
(def calculate-var-99 (partial-apply calculate-var {} 0.99))

;; Good: Use for configuration
(def process-aapl (partial-apply process-stock "AAPL"))
(def process-googl (partial-apply process-stock "GOOGL"))
```

### **3. Memoization**
```clojure
;; Good: Memoize expensive calculations
(def memoized-rsi (memoize-with-ttl calculate-rsi 5000))
(def memoized-portfolio-value (memoize-with-ttl calculate-portfolio-value 1000))

;; Good: Use appropriate TTL
(def short-term-cache (memoize-with-ttl fast-function 1000))
(def long-term-cache (memoize-with-ttl slow-function 300000))
```

### **4. Error Handling**
```clojure
;; Good: Use function pipelines with error handling
(def safe-pipeline
  (create-function-pipeline
   validate-input
   process-data
   handle-errors))

;; Good: Use circuit breakers for external services
(def api-circuit-breaker
  (create-circuit-breaker
   call-external-api
   3  ; failure threshold
   10000)) ; timeout
```

### **5. Financial Pipelines**
```clojure
;; Good: Create reusable financial pipelines
(def price-analysis-pipeline
  (create-price-transformer
   (normalize-price 0 1000)
   (apply-price-multiplier 1.05)
   (denormalize-price 0 1000)))

;; Good: Combine multiple pipelines
(def trading-system
  (compose
   price-analysis-pipeline
   signal-generation-pipeline
   portfolio-analysis-pipeline))
```

---

## 🎉 **Success!**

The ACTORS Clojure Higher Order Functions System is now **WORKING** and ready for development! You can:

- ✅ Start the system with `./scripts/start-with-higher-order-functions.sh`
- ✅ Run higher order function demos with `(actors.simple-higher-order-functions/run-all-simple-higher-order-function-demos)`
- ✅ Compose functions with `compose` and `pipe`
- ✅ Apply partial arguments with `partial-apply`
- ✅ Cache function results with `memoize-with-ttl`
- ✅ Throttle function calls with `throttle`
- ✅ Create financial pipelines for trading and portfolio analysis
- ✅ Implement advanced patterns like circuit breakers and retry logic
- ✅ Use monadic patterns for safe computation
- ✅ Build sophisticated functional programming systems

**Welcome to advanced functional programming with higher order functions! 🎯**
