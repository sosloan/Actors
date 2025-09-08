# 🔲 ACTORS Clojure Grid State System

## *Functional Grid Operations with Lambdas and Recursion*

---

## 🌟 **System Overview**

The **ACTORS Clojure Grid State System** provides a comprehensive framework for managing grid-based data structures with functional programming patterns. It includes lambda operations, recursive algorithms, in-place data copying, and specialized financial grid operations.

### **🎯 What's Included**
- ✅ **Grid Creation**: Create grids with dimensions and initial values
- ✅ **Lambda Operations**: Map, filter, reduce with lambda functions
- ✅ **Recursive Operations**: Recursive fill, search, and path finding
- ✅ **In-Place Copying**: Copy data in place with mutable operations
- ✅ **Financial Grids**: Specialized grids for financial data
- ✅ **Grid Analysis**: Pattern analysis and statistics
- ✅ **Functional Composition**: Compose operations using higher-order functions

---

## 🚀 **Quick Start**

### **Start the System with Grid State**
```bash
cd /Users/stevensloan/ACTORS/CLOJURE
./scripts/start-with-grid-state.sh
```

### **Run All Grid Demos**
```clojure
(actors.grid-state/run-all-grid-demos)
```

---

## 📚 **Grid State Framework**

### **Grid Protocol**
```clojure
(defprotocol GridState
  (get-cell [this row col] "Get cell value at position")
  (set-cell [this row col value] "Set cell value at position")
  (get-dimensions [this] "Get grid dimensions")
  (copy-grid [this] "Create a copy of the grid"))
```

### **Grid Record**
```clojure
(defrecord Grid [data rows cols]
  GridState
  (get-cell [this row col] ...)
  (set-cell [this row col value] ...)
  (get-dimensions [this] ...)
  (copy-grid [this] ...))
```

---

## 🔧 **Grid Creation**

### **Basic Grid Creation**
```clojure
;; Create a simple grid
(def grid (create-grid 3 4 :initial-value 0))

;; Create grid from data
(def grid (create-grid-from-data [[1 2 3] [4 5 6] [7 8 9]]))

;; Get dimensions
(get-dimensions grid) ; => {:rows 3, :cols 4}
```

### **Financial Grid Creation**
```clojure
;; Create financial grid
(def symbols ["AAPL" "GOOGL" "TSLA"])
(def periods ["2024-01" "2024-02" "2024-03"])
(def financial-grid (create-financial-grid symbols periods :initial-price 100.0))

;; Create portfolio grid
(def assets ["Stock" "Bond" "Commodity"])
(def strategies ["Conservative" "Moderate" "Aggressive"])
(def portfolio-grid (create-portfolio-grid assets strategies :initial-allocation 0.0))
```

---

## 🎯 **Lambda Operations**

### **Map Operations**
```clojure
;; Map over grid with lambda
(def doubled-grid (map-grid grid #(* % 2)))

;; Map with position information
(def position-grid (map-grid-with-position grid
                                          (fn [value row col]
                                            {:value value :position [row col] :sum (+ row col)})))
```

### **Filter Operations**
```clojure
;; Filter grid cells
(def filtered-cells (filter-grid grid
                                 (fn [cell]
                                   (> cell 5))))

;; Filter with complex conditions
(def financial-filtered (filter-grid financial-grid
                                     (fn [cell]
                                       (> (:price cell) 100))))
```

### **Reduce Operations**
```clojure
;; Reduce grid to single value
(def total (reduce-grid grid + 0))

;; Map-reduce operation
(def result (map-reduce-grid grid
                             (fn [cell row col] (* cell (+ row col)))
                             +
                             0))
```

---

## 🔄 **Recursive Operations**

### **Recursive Fill**
```clojure
;; Recursively fill grid from center
(def filled-grid (recursive-grid-fill grid 2 2
                                     (fn [value row col depth]
                                       (+ value depth))
                                     3))
```

### **Recursive Search**
```clojure
;; Recursively search grid
(def visited (recursive-grid-search grid 0 0
                                   (fn [cell row col]
                                     (< cell 5))
                                   #{}))
```

### **Recursive Path Finding**
```clojure
;; Find path through grid
(def path (recursive-grid-path grid 0 0 2 2
                              (fn [cell row col]
                                [[(inc row) col] [row (inc col)]])))
```

---

## 📋 **In-Place Data Copying**

### **Grid Copying**
```clojure
;; Copy grid (immutable)
(def copied-grid (copy-grid original-grid))

;; Copy grid in place (mutable)
(def in-place-copy (copy-grid-in-place original-grid))

;; Update single cell
(def updated-grid (update-grid-cell grid 0 0 #(* % 2)))

;; Batch update multiple cells
(def batch-updated (batch-update-grid grid
                                      [[0 0 100] [1 1 200] [2 2 300]]))
```

### **Grid Merging**
```clojure
;; Merge two grids
(def merged-grid (merge-grids grid1 grid2
                              (fn [cell1 cell2]
                                (+ cell1 cell2))))
```

---

## 💰 **Financial Grid Operations**

### **Price Grid Updates**
```clojure
;; Update prices with market data function
(def updated-price-grid (update-price-grid price-grid
                                          (fn [symbol period]
                                            (get-market-price symbol period))))
```

### **Portfolio Calculations**
```clojure
;; Calculate portfolio returns
(def returns-grid (calculate-portfolio-returns portfolio-grid
                                              (fn [asset strategy]
                                                (calculate-expected-return asset strategy))))
```

### **Risk Adjustments**
```clojure
;; Apply risk adjustments
(def risk-adjusted-grid (apply-risk-adjustment grid
                                              (fn [asset strategy]
                                                (calculate-risk asset strategy))))
```

### **Portfolio Optimization**
```clojure
;; Optimize allocation recursively
(def optimized-grid (optimize-grid-allocation grid
                                             (fn [cell iteration]
                                               (optimize-allocation cell iteration))
                                             100))
```

---

## 📊 **Grid Analysis**

### **Pattern Analysis**
```clojure
;; Analyze patterns with lambda
(def pattern-grid (analyze-grid-patterns grid
                                        (fn [cell row col grid]
                                          (detect-pattern cell row col grid))))
```

### **Extreme Value Finding**
```clojure
;; Find extreme values
(def extremes (find-grid-extremes grid
                                  (fn [cell]
                                    (if (map? cell) (:price cell) cell))))
```

### **Statistical Analysis**
```clojure
;; Calculate grid statistics
(def stats (calculate-grid-statistics grid
                                     (fn [cell]
                                       (if (map? cell) (:price cell) cell))))
```

---

## 🧪 **Demo Functions**

### **Basic Grid Operations Demo**
```clojure
(actors.grid-state/demo-basic-grid-operations)
```

**Output:**
```
=== Basic Grid Operations Demo ===
1. Created 3x4 grid with initial value 0
   Dimensions: {:rows 3, :cols 4}
2. Set values at (0,0)=10, (1,1)=20, (2,2)=30
   Value at (0,0): 10
   Value at (1,1): 20
3. Doubled all values using lambda
   Value at (0,0): 20
   Value at (1,1): 40
4. Sum of all values: 120
```

### **Financial Grid Demo**
```clojure
(actors.grid-state/demo-financial-grid)
```

**Output:**
```
=== Financial Grid Demo ===
1. Created financial grid:
   Symbols: [AAPL GOOGL TSLA]
   Periods: [2024-01 2024-02 2024-03]
   Dimensions: {:rows 3, :cols 3}
2. Updated prices with multipliers:
   AAPL at 2024-01: 110.0
   GOOGL at 2024-01: 120.0
   TSLA at 2024-01: 90.0
3. Total portfolio value: 960.0
```

### **Recursive Operations Demo**
```clojure
(actors.grid-state/demo-recursive-operations)
```

**Output:**
```
=== Recursive Grid Operations Demo ===
1. Created 5x5 grid
2. Recursively filled from center (2,2) with depth 3
   Center value: 0
   Neighbor value: 0
3. Recursive search for values < 5
   Visited cells: 25
   Visited positions: ([4 3] [2 2] [0 0] [1 0] [2 3])
```

### **Lambda Operations Demo**
```clojure
(actors.grid-state/demo-lambda-operations)
```

**Output:**
```
=== Lambda Operations Demo ===
1. Created 4x4 grid with value 1
2. Mapped with position information
   Cell (0,0): {:value 1, :position [0 0], :sum 0}
   Cell (2,3): {:value 1, :position [2 3], :sum 5}
3. Filtered cells where sum > 3
   Filtered count: 6
4. Map-reduce: value * sum for all cells
   Result: 48
```

### **Grid Copying Demo**
```clojure
(actors.grid-state/demo-grid-copying)
```

**Output:**
```
=== Grid Copying Demo ===
1. Created original 3x3 grid with value 5
2. Copied grid
   Original (0,0): 5
   Copied (0,0): 5
3. Modified copied grid
   Original (0,0): 5
   Modified copy (0,0): 99
4. In-place copy
   In-place copy (0,0): 5
5. Batch updated grid
   (0,0): 100
   (1,1): 200
   (2,2): 300
```

---

## 🎯 **Advanced Examples**

### **Financial Portfolio Grid**
```clojure
;; Create portfolio allocation grid
(def portfolio-grid (create-portfolio-grid 
                     ["AAPL" "GOOGL" "TSLA"]
                     ["Conservative" "Moderate" "Aggressive"]
                     :initial-allocation 0.0))

;; Update allocations with lambda
(def updated-portfolio (map-grid portfolio-grid
                                 (fn [cell]
                                   (let [allocation (case (:strategy cell)
                                                     "Conservative" 0.3
                                                     "Moderate" 0.5
                                                     "Aggressive" 0.7
                                                     0.0)]
                                     (assoc cell :allocation allocation)))))

;; Calculate expected returns
(def returns-grid (calculate-portfolio-returns updated-portfolio
                                              (fn [asset strategy]
                                                (case [asset strategy]
                                                  ["AAPL" "Conservative"] 0.08
                                                  ["GOOGL" "Moderate"] 0.12
                                                  ["TSLA" "Aggressive"] 0.20
                                                  0.05))))
```

### **Risk Matrix Grid**
```clojure
;; Create risk matrix
(def risk-grid (create-grid 5 5 :initial-value 0.0))

;; Apply risk calculation with lambda
(def risk-calculated (map-grid-with-position risk-grid
                                            (fn [value row col]
                                              (let [risk-level (* (+ row col) 0.1)]
                                                {:risk-level risk-level
                                                 :position [row col]
                                                 :category (if (> risk-level 0.5) :high :low)}))))

;; Filter high-risk positions
(def high-risk-positions (filter-grid risk-calculated
                                     (fn [cell]
                                       (= (:category cell) :high))))
```

### **Recursive Grid Search**
```clojure
;; Find connected regions
(def connected-regions (recursive-grid-search grid 0 0
                                             (fn [cell row col]
                                               (> cell 0))
                                             #{}))

;; Recursive path finding
(def optimal-path (recursive-grid-path grid 0 0 4 4
                                      (fn [cell row col]
                                        (if (> cell 0)
                                          [[(inc row) col] [row (inc col)]]
                                          []))))
```

---

## 🔧 **Best Practices**

### **1. Lambda Function Design**
```clojure
;; Good: Clear, single-purpose lambda
(def doubled-grid (map-grid grid #(* % 2)))

;; Good: Named lambda for complex operations
(def complex-transform (fn [cell row col]
                         (if (> cell 0)
                           (* cell (+ row col))
                           cell)))
(def transformed-grid (map-grid-with-position grid complex-transform))
```

### **2. Recursive Function Design**
```clojure
;; Good: Clear termination conditions
(defn recursive-fill [grid row col depth max-depth]
  (if (or (>= depth max-depth) (out-of-bounds? row col))
    grid
    (let [new-value (calculate-value row col depth)]
      (recur (set-cell grid row col new-value)
             (inc row) (inc col) (inc depth) max-depth))))
```

### **3. Grid State Management**
```clojure
;; Good: Immutable operations
(def updated-grid (-> grid
                     (set-cell 0 0 100)
                     (set-cell 1 1 200)
                     (map-grid #(* % 2))))

;; Good: Batch operations for efficiency
(def batch-updated (batch-update-grid grid
                                      [[0 0 100] [1 1 200] [2 2 300]]))
```

### **4. Error Handling**
```clojure
;; Good: Safe grid operations
(defn safe-get-cell [grid row col]
  (try
    (get-cell grid row col)
    (catch Exception e
      (println "Error accessing cell:" row col)
      nil)))
```

---

## 🎉 **Success!**

The ACTORS Clojure Grid State System is now **WORKING** and ready for development! You can:

- ✅ Start the system with `./scripts/start-with-grid-state.sh`
- ✅ Run grid demos with `(actors.grid-state/run-all-grid-demos)`
- ✅ Create grids with `create-grid` and `create-financial-grid`
- ✅ Use lambda operations with `map-grid`, `filter-grid`, `reduce-grid`
- ✅ Implement recursive operations with `recursive-grid-fill`, `recursive-grid-search`
- ✅ Copy data in place with `copy-grid-in-place` and `batch-update-grid`
- ✅ Analyze grids with `analyze-grid-patterns` and `calculate-grid-statistics`
- ✅ Build financial applications with specialized grid operations

**Welcome to functional grid state management! 🔲**
