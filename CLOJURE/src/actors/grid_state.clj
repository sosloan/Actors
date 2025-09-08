(ns actors.grid-state
  "Grid state management with functional programming patterns"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >!]]
            [actors.simple-core :as core]))

;; =============================================================================
;; Grid State Framework
;; =============================================================================

(defprotocol GridState
  "Protocol for grid state operations"
  (get-cell [this row col] "Get cell value at position")
  (set-cell [this row col value] "Set cell value at position")
  (get-dimensions [this] "Get grid dimensions")
  (copy-grid [this] "Create a copy of the grid"))

(defrecord Grid [data rows cols]
  GridState
  (get-cell [this row col]
    (when (and (>= row 0) (< row rows) (>= col 0) (< col cols))
      (nth (nth data row) col)))
  
  (set-cell [this row col value]
    (let [new-data (assoc data row 
                          (assoc (nth data row) col value))]
      (->Grid new-data rows cols)))
  
  (get-dimensions [this]
    {:rows rows :cols cols})
  
  (copy-grid [this]
    (->Grid (mapv (fn [row] (mapv identity row)) data) rows cols)))

;; =============================================================================
;; Grid Creation and Manipulation
;; =============================================================================

(defn create-grid
  "Create a new grid with specified dimensions and initial value"
  [rows cols & {:keys [initial-value] :or {initial-value 0}}]
  (->Grid (vec (repeat rows (vec (repeat cols initial-value)))) rows cols))

(defn create-grid-from-data
  "Create a grid from existing data"
  [data]
  (let [rows (count data)
        cols (if (empty? data) 0 (count (first data)))]
    (->Grid (mapv vec data) rows cols)))

(defn create-financial-grid
  "Create a financial grid with symbols and time periods"
  [symbols time-periods & {:keys [initial-price] :or {initial-price 100.0}}]
  (let [rows (count symbols)
        cols (count time-periods)
        grid-data (vec (for [symbol symbols]
                         (vec (for [period time-periods]
                                {:symbol symbol
                                 :period period
                                 :price initial-price
                                 :volume 0
                                 :volatility 0.0}))))]
    (->Grid grid-data rows cols)))

(defn create-portfolio-grid
  "Create a portfolio allocation grid"
  [assets strategies & {:keys [initial-allocation] :or {initial-allocation 0.0}}]
  (let [rows (count assets)
        cols (count strategies)
        grid-data (vec (for [asset assets]
                         (vec (for [strategy strategies]
                                {:asset asset
                                 :strategy strategy
                                 :allocation initial-allocation
                                 :expected-return 0.0
                                 :risk 0.0}))))]
    (->Grid grid-data rows cols)))

;; =============================================================================
;; Grid Operations with Lambdas
;; =============================================================================

(defn map-grid
  "Apply a function to each cell in the grid"
  [grid f]
  (let [{:keys [rows cols]} (get-dimensions grid)
        new-data (vec (for [row (range rows)]
                        (vec (for [col (range cols)]
                               (f (get-cell grid row col))))))]
    (->Grid new-data rows cols)))

(defn map-grid-with-position
  "Apply a function to each cell with row/col position"
  [grid f]
  (let [{:keys [rows cols]} (get-dimensions grid)
        new-data (vec (for [row (range rows)]
                        (vec (for [col (range cols)]
                               (f (get-cell grid row col) row col)))))]
    (->Grid new-data rows cols)))

(defn filter-grid
  "Filter grid cells based on predicate"
  [grid predicate]
  (let [{:keys [rows cols]} (get-dimensions grid)
        filtered-cells (for [row (range rows)
                             col (range cols)
                             :let [cell (get-cell grid row col)]
                             :when (predicate cell)]
                         {:row row :col col :value cell})]
    filtered-cells))

(defn reduce-grid
  "Reduce grid to a single value"
  [grid f initial]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (loop [row 0
           col 0
           acc initial]
      (cond
        (>= row rows) acc
        (>= col cols) (recur (inc row) 0 acc)
        :else (recur row (inc col) (f acc (get-cell grid row col)))))))

(defn map-reduce-grid
  "Map over grid then reduce to single value"
  [grid map-f reduce-f initial]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (loop [row 0
           col 0
           acc initial]
      (cond
        (>= row rows) acc
        (>= col cols) (recur (inc row) 0 acc)
        :else (let [mapped-value (map-f (get-cell grid row col) row col)]
                (recur row (inc col) (reduce-f acc mapped-value)))))))

;; =============================================================================
;; Grid Transformations with Lambdas
;; =============================================================================

(defn transform-grid-cells
  "Transform grid cells using a lambda function"
  [grid transform-fn]
  (map-grid grid transform-fn))

(defn transform-grid-with-context
  "Transform grid with context (neighboring cells)"
  [grid transform-fn]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (map-grid-with-position 
      grid 
      (fn [cell row col]
        (let [context {:cell cell
                       :row row
                       :col col
                       :north (get-cell grid (dec row) col)
                       :south (get-cell grid (inc row) col)
                       :east (get-cell grid row (inc col))
                       :west (get-cell grid row (dec col))
                       :northwest (get-cell grid (dec row) (dec col))
                       :northeast (get-cell grid (dec row) (inc col))
                       :southwest (get-cell grid (inc row) (dec col))
                       :southeast (get-cell grid (inc row) (inc col))}]
          (transform-fn context))))))

(defn apply-grid-kernel
  "Apply a kernel operation to each cell"
  [grid kernel-fn]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (map-grid-with-position
      grid
      (fn [cell row col]
        (let [neighbors (for [dr [-1 0 1]
                              dc [-1 0 1]
                              :let [nr (+ row dr)
                                    nc (+ col dc)]
                              :when (and (>= nr 0) (< nr rows)
                                        (>= nc 0) (< nc cols)
                                        (not (and (= dr 0) (= dc 0))))]
                          (get-cell grid nr nc))]
          (kernel-fn cell neighbors))))))

;; =============================================================================
;; Recursive Grid Operations
;; =============================================================================

(defn recursive-grid-fill
  "Recursively fill grid using a function"
  [grid start-row start-col fill-fn max-depth]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (loop [current-grid grid
           depth 0
           stack [[start-row start-col]]]
      (if (or (empty? stack) (>= depth max-depth))
        current-grid
        (let [[row col] (peek stack)
              new-stack (pop stack)
              current-value (get-cell current-grid row col)
              new-value (fill-fn current-value row col depth)
              updated-grid (set-cell current-grid row col new-value)
              new-positions (for [dr [-1 0 1]
                                  dc [-1 0 1]
                                  :let [nr (+ row dr)
                                        nc (+ col dc)]
                                  :when (and (>= nr 0) (< nr rows)
                                            (>= nc 0) (< nc cols)
                                            (not (and (= dr 0) (= dc 0))))]
                              [nr nc])]
          (recur updated-grid (inc depth) (into new-stack new-positions)))))))

(defn recursive-grid-search
  "Recursively search grid for pattern"
  [grid start-row start-col search-fn visited]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (if (or (< start-row 0) (>= start-row rows)
            (< start-col 0) (>= start-col cols)
            (contains? visited [start-row start-col]))
      visited
      (let [cell (get-cell grid start-row start-col)
            should-continue (search-fn cell start-row start-col)
            new-visited (conj visited [start-row start-col])]
        (if should-continue
          (reduce (fn [acc [dr dc]]
                    (recursive-grid-search grid 
                                          (+ start-row dr) 
                                          (+ start-col dc) 
                                          search-fn acc))
                  new-visited
                  [[-1 0] [1 0] [0 -1] [0 1]])
          new-visited)))))

(defn recursive-grid-path
  "Find recursive path through grid"
  [grid start-row start-col end-row end-col path-fn]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (loop [current-row start-row
           current-col start-col
           path [[start-row start-col]]
           visited #{[start-row start-col]}]
      (cond
        (and (= current-row end-row) (= current-col end-col))
        path
        
        (>= (count path) (* rows cols))
        nil
        
        :else
        (let [current-cell (get-cell grid current-row current-col)
              next-moves (path-fn current-cell current-row current-col)
              valid-moves (filter (fn [[nr nc]]
                                    (and (>= nr 0) (< nr rows)
                                         (>= nc 0) (< nc cols)
                                         (not (contains? visited [nr nc]))))
                                  next-moves)]
          (if (empty? valid-moves)
            nil
            (let [[next-row next-col] (first valid-moves)]
              (recur next-row next-col
                     (conj path [next-row next-col])
                     (conj visited [next-row next-col])))))))))

;; =============================================================================
;; Financial Grid Operations
;; =============================================================================

(defn update-price-grid
  "Update price grid with new market data"
  [price-grid market-data-fn]
  (map-grid price-grid 
            (fn [cell]
              (if (map? cell)
                (assoc cell :price (market-data-fn (:symbol cell) (:period cell)))
                cell))))

(defn calculate-portfolio-returns
  "Calculate portfolio returns using grid operations"
  [portfolio-grid return-fn]
  (map-grid portfolio-grid
            (fn [cell]
              (if (map? cell)
                (let [return (return-fn (:asset cell) (:strategy cell))]
                  (assoc cell :expected-return return))
                cell))))

(defn apply-risk-adjustment
  "Apply risk adjustment to grid cells"
  [grid risk-fn]
  (map-grid grid
            (fn [cell]
              (if (map? cell)
                (let [risk (risk-fn (:asset cell) (:strategy cell))]
                  (assoc cell :risk risk))
                cell))))

(defn optimize-grid-allocation
  "Optimize allocation using recursive grid search"
  [grid optimization-fn max-iterations]
  (loop [current-grid grid
         iteration 0]
    (if (>= iteration max-iterations)
      current-grid
      (let [optimized-grid (map-grid current-grid
                                    (fn [cell]
                                      (if (map? cell)
                                        (optimization-fn cell iteration)
                                        cell)))]
        (recur optimized-grid (inc iteration))))))

;; =============================================================================
;; Grid Analysis with Lambdas
;; =============================================================================

(defn analyze-grid-patterns
  "Analyze patterns in grid using lambda functions"
  [grid pattern-fn]
  (let [{:keys [rows cols]} (get-dimensions grid)]
    (map-grid-with-position
      grid
      (fn [cell row col]
        (let [pattern (pattern-fn cell row col grid)]
          (assoc (if (map? cell) cell {}) :pattern pattern))))))

(defn find-grid-extremes
  "Find extreme values in grid"
  [grid value-fn]
  (let [{:keys [rows cols]} (get-dimensions grid)
        all-values (for [row (range rows)
                         col (range cols)]
                     {:row row :col col :value (value-fn (get-cell grid row col))})
        sorted-values (sort-by :value all-values)]
    {:min (first sorted-values)
     :max (last sorted-values)
     :all-values all-values}))

(defn calculate-grid-statistics
  "Calculate statistics for grid using reduce"
  [grid value-fn]
  (let [values (map-grid grid value-fn)
        stats (reduce-grid values
                          (fn [acc val]
                            {:sum (+ (:sum acc) val)
                             :count (inc (:count acc))
                             :min (min (:min acc) val)
                             :max (max (:max acc) val)})
                          {:sum 0 :count 0 :min Double/MAX_VALUE :max Double/MIN_VALUE})]
    (assoc stats :mean (/ (:sum stats) (:count stats)))))

;; =============================================================================
;; Grid State Management
;; =============================================================================

(defn copy-grid-in-place
  "Copy grid data in place (mutable copy)"
  [grid]
  (let [{:keys [rows cols]} (get-dimensions grid)
        new-data (vec (for [row (range rows)]
                        (vec (for [col (range cols)]
                               (get-cell grid row col)))))]
    (->Grid new-data rows cols)))

(defn update-grid-cell
  "Update a single cell in place"
  [grid row col update-fn]
  (let [current-value (get-cell grid row col)
        new-value (update-fn current-value)]
    (set-cell grid row col new-value)))

(defn batch-update-grid
  "Batch update multiple cells"
  [grid updates]
  (reduce (fn [current-grid [row col value]]
            (set-cell current-grid row col value))
          grid
          updates))

(defn merge-grids
  "Merge two grids using a merge function"
  [grid1 grid2 merge-fn]
  (let [{:keys [rows cols]} (get-dimensions grid1)
        new-data (vec (for [row (range rows)]
                        (vec (for [col (range cols)]
                               (merge-fn (get-cell grid1 row col)
                                        (get-cell grid2 row col))))))]
    (->Grid new-data rows cols)))

;; =============================================================================
;; Demo Functions
;; =============================================================================

(defn demo-basic-grid-operations
  "Demonstrate basic grid operations"
  []
  (println "=== Basic Grid Operations Demo ===")
  
  ;; Create a simple grid
  (let [grid (create-grid 3 4 :initial-value 0)]
    (println "1. Created 3x4 grid with initial value 0")
    (println "   Dimensions:" (get-dimensions grid))
    
    ;; Set some values
    (let [grid-with-values (-> grid
                              (set-cell 0 0 10)
                              (set-cell 1 1 20)
                              (set-cell 2 2 30))]
      (println "2. Set values at (0,0)=10, (1,1)=20, (2,2)=30")
      (println "   Value at (0,0):" (get-cell grid-with-values 0 0))
      (println "   Value at (1,1):" (get-cell grid-with-values 1 1))
      
      ;; Map over grid with lambda
      (let [doubled-grid (map-grid grid-with-values #(* % 2))]
        (println "3. Doubled all values using lambda")
        (println "   Value at (0,0):" (get-cell doubled-grid 0 0))
        (println "   Value at (1,1):" (get-cell doubled-grid 1 1))
        
        ;; Reduce grid to sum
        (let [total (reduce-grid doubled-grid + 0)]
          (println "4. Sum of all values:" total))))))

(defn demo-financial-grid
  "Demonstrate financial grid operations"
  []
  (println "=== Financial Grid Demo ===")
  
  (let [symbols ["AAPL" "GOOGL" "TSLA"]
        periods ["2024-01" "2024-02" "2024-03"]
        grid (create-financial-grid symbols periods :initial-price 100.0)]
    
    (println "1. Created financial grid:")
    (println "   Symbols:" symbols)
    (println "   Periods:" periods)
    (println "   Dimensions:" (get-dimensions grid))
    
    ;; Update prices with lambda
    (let [price-updated-grid (map-grid grid
                                      (fn [cell]
                                        (let [price-multiplier (case (:symbol cell)
                                                                "AAPL" 1.1
                                                                "GOOGL" 1.2
                                                                "TSLA" 0.9
                                                                1.0)]
                                          (assoc cell :price (* (:price cell) price-multiplier)))))]
      (println "2. Updated prices with multipliers:")
      (println "   AAPL at 2024-01:" (:price (get-cell price-updated-grid 0 0)))
      (println "   GOOGL at 2024-01:" (:price (get-cell price-updated-grid 1 0)))
      (println "   TSLA at 2024-01:" (:price (get-cell price-updated-grid 2 0)))
      
      ;; Calculate portfolio value
      (let [portfolio-value (reduce-grid price-updated-grid
                                        (fn [acc cell]
                                          (+ acc (:price cell)))
                                        0)]
        (println "3. Total portfolio value:" portfolio-value)))))

(defn demo-recursive-operations
  "Demonstrate recursive grid operations"
  []
  (println "=== Recursive Grid Operations Demo ===")
  
  (let [grid (create-grid 5 5 :initial-value 0)]
    (println "1. Created 5x5 grid")
    
    ;; Recursive fill
    (let [filled-grid (recursive-grid-fill grid 2 2
                                          (fn [value row col depth]
                                            (+ value depth))
                                          3)]
      (println "2. Recursively filled from center (2,2) with depth 3")
      (println "   Center value:" (get-cell filled-grid 2 2))
      (println "   Neighbor value:" (get-cell filled-grid 1 2))
      
      ;; Recursive search
      (let [visited (recursive-grid-search filled-grid 2 2
                                          (fn [cell row col]
                                            (< cell 5))
                                          #{})]
        (println "3. Recursive search for values < 5")
        (println "   Visited cells:" (count visited))
        (println "   Visited positions:" (take 5 visited))))))

(defn demo-lambda-operations
  "Demonstrate lambda operations on grids"
  []
  (println "=== Lambda Operations Demo ===")
  
  (let [grid (create-grid 4 4 :initial-value 1)]
    (println "1. Created 4x4 grid with value 1")
    
    ;; Map with position
    (let [position-grid (map-grid-with-position grid
                                               (fn [value row col]
                                                 {:value value :position [row col] :sum (+ row col)}))]
      (println "2. Mapped with position information")
      (println "   Cell (0,0):" (get-cell position-grid 0 0))
      (println "   Cell (2,3):" (get-cell position-grid 2 3))
      
      ;; Filter grid
      (let [filtered (filter-grid position-grid
                                 (fn [cell]
                                   (> (:sum cell) 3)))]
        (println "3. Filtered cells where sum > 3")
        (println "   Filtered count:" (count filtered))
        (println "   First filtered:" (first filtered))
        
        ;; Map-reduce
        (let [result (map-reduce-grid position-grid
                                     (fn [cell row col]
                                       (* (:value cell) (:sum cell)))
                                     +
                                     0)]
          (println "4. Map-reduce: value * sum for all cells")
          (println "   Result:" result))))))

(defn demo-grid-copying
  "Demonstrate grid copying operations"
  []
  (println "=== Grid Copying Demo ===")
  
  (let [original-grid (create-grid 3 3 :initial-value 5)]
    (println "1. Created original 3x3 grid with value 5")
    
    ;; Copy grid
    (let [copied-grid (copy-grid original-grid)]
      (println "2. Copied grid")
      (println "   Original (0,0):" (get-cell original-grid 0 0))
      (println "   Copied (0,0):" (get-cell copied-grid 0 0))
      
      ;; Modify copied grid
      (let [modified-copy (set-cell copied-grid 0 0 99)]
        (println "3. Modified copied grid")
        (println "   Original (0,0):" (get-cell original-grid 0 0))
        (println "   Modified copy (0,0):" (get-cell modified-copy 0 0))
        
        ;; In-place copy
        (let [in-place-copy (copy-grid-in-place original-grid)]
          (println "4. In-place copy")
          (println "   In-place copy (0,0):" (get-cell in-place-copy 0 0))
          
          ;; Batch update
          (let [batch-updated (batch-update-grid in-place-copy
                                                [[0 0 100] [1 1 200] [2 2 300]])]
            (println "5. Batch updated grid")
            (println "   (0,0):" (get-cell batch-updated 0 0))
            (println "   (1,1):" (get-cell batch-updated 1 1))
            (println "   (2,2):" (get-cell batch-updated 2 2))))))))

(defn run-all-grid-demos
  "Run all grid demonstrations"
  []
  (println "🎯 === ACTORS Grid State Comprehensive Demo ===")
  (println)
  (demo-basic-grid-operations)
  (println)
  (demo-financial-grid)
  (println)
  (demo-recursive-operations)
  (println)
  (demo-lambda-operations)
  (println)
  (demo-grid-copying)
  (println)
  (println "🎉 === All Grid Demos Complete ==="))

(defn -main
  "Main entry point for grid state demo"
  [& args]
  (run-all-grid-demos))
