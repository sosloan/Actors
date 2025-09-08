(ns actors.simple-procedures
  "Simplified procedures for ACTORS system operations"
  (:require [actors.simple-core :as core]))

;; =============================================================================
;; Procedure Framework
;; =============================================================================

(defn create-procedure-result
  "Create a procedure result"
  [status data & {:keys [error]}]
  {:status status
   :data data
   :error error
   :timestamp (System/currentTimeMillis)})

;; =============================================================================
;; Market Data Procedures
;; =============================================================================

(defn fetch-market-data
  "Fetch market data procedure"
  [symbol]
  (let [market-data (core/create-market-data symbol 150.25 1000000 0.18)]
    (create-procedure-result :success market-data)))

(defn validate-market-data
  "Validate market data procedure"
  [market-data]
  (let [valid? (and (not (nil? (:symbol market-data)))
                    (> (:price market-data) 0)
                    (> (:volume market-data) 0)
                    (>= (:volatility market-data) 0))]
    (create-procedure-result (if valid? :success :error) 
                            {:valid valid? :data market-data})))

(defn transform-market-data
  "Transform market data procedure"
  [market-data]
  (let [transformed (assoc market-data 
                          :processed true
                          :timestamp (System/currentTimeMillis)
                          :price-change (if (> (:price market-data) 100) :high :low))]
    (create-procedure-result :success transformed)))

(defn store-market-data
  "Store market data procedure"
  [market-data]
  (let [stored-data (assoc market-data :stored true :storage-id (str "md-" (System/currentTimeMillis)))]
    (create-procedure-result :success stored-data)))

;; =============================================================================
;; Trading Signal Procedures
;; =============================================================================

(defn generate-trading-signal
  "Generate trading signal procedure"
  [market-data]
  (let [price (:price market-data)
        volatility (:volatility market-data)
        signal-type (cond
                     (> price 200) :buy
                     (< price 50) :sell
                     :else :hold)
        confidence (if (> volatility 0.2) 0.8 0.6)
        signal (core/create-trading-signal signal-type confidence {:strategy "price-based"})]
    (create-procedure-result :success signal)))

(defn validate-trading-signal
  "Validate trading signal procedure"
  [signal]
  (let [valid? (and (not (nil? (:type signal)))
                    (>= (:confidence signal) 0.0)
                    (<= (:confidence signal) 1.0)
                    (contains? #{:buy :sell :hold} (:type signal)))]
    (create-procedure-result (if valid? :success :error)
                            {:valid valid? :signal signal})))

(defn process-trading-signal
  "Process trading signal procedure"
  [signal]
  (let [processed-signal (assoc signal 
                               :processed true
                               :processed-at (System/currentTimeMillis)
                               :priority (if (> (:confidence signal) 0.8) :high :normal))]
    (create-procedure-result :success processed-signal)))

(defn execute-trading-signal
  "Execute trading signal procedure"
  [signal]
  (let [execution-result {:signal-id (str "sig-" (System/currentTimeMillis))
                          :executed-at (System/currentTimeMillis)
                          :status :executed
                          :signal signal}]
    (create-procedure-result :success execution-result)))

;; =============================================================================
;; Portfolio Procedures
;; =============================================================================

(defn calculate-portfolio-value
  "Calculate portfolio value procedure"
  [portfolio]
  (let [positions (:positions portfolio)
        total-value (reduce + (map (fn [pos] (* (:quantity pos) (:price pos))) positions))
        result {:portfolio-id (:id portfolio)
                :total-value total-value
                :position-count (count positions)
                :calculated-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn rebalance-portfolio
  "Rebalance portfolio procedure"
  [portfolio]
  (let [target-allocations (:target-allocations portfolio)
        current-positions (:positions portfolio)
        total-value (reduce + (map (fn [pos] (* (:quantity pos) (:price pos))) current-positions))
        rebalanced-positions (map (fn [pos]
                                    (let [target-allocation (get target-allocations (:symbol pos) 0.1)
                                          target-value (* total-value target-allocation)
                                          current-value (* (:quantity pos) (:price pos))
                                          adjustment (- target-value current-value)]
                                      (assoc pos :adjustment adjustment :target-value target-value)))
                                  current-positions)
        result {:portfolio-id (:id portfolio)
                :rebalanced-positions rebalanced-positions
                :total-value total-value
                :rebalanced-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn optimize-portfolio
  "Optimize portfolio procedure"
  [portfolio]
  (let [positions (:positions portfolio)
        optimization-result (loop [iteration 0
                                   best-allocation (repeat (count positions) (/ 1.0 (count positions)))
                                   best-return 0.0]
                              (if (>= iteration 100)
                                {:allocation best-allocation :expected-return best-return}
                                (let [new-allocation (map #(+ % (- (rand 0.1) 0.05)) best-allocation)
                                      normalized-allocation (let [sum (reduce + new-allocation)]
                                                             (map #(/ % sum) new-allocation))
                                      expected-return (* (first normalized-allocation) 0.12)]
                                  (if (> expected-return best-return)
                                    (recur (inc iteration) normalized-allocation expected-return)
                                    (recur (inc iteration) best-allocation best-return)))))
        result {:portfolio-id (:id portfolio)
                :optimization-result optimization-result
                :optimized-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn assess-portfolio-risk
  "Assess portfolio risk procedure"
  [portfolio]
  (let [positions (:positions portfolio)
        total-value (reduce + (map (fn [pos] (* (:quantity pos) (:price pos))) positions))
        risk-metrics {:var-95 (* total-value 0.05)
                      :var-99 (* total-value 0.10)
                      :max-drawdown (* total-value 0.15)
                      :sharpe-ratio 1.2}
        result {:portfolio-id (:id portfolio)
                :risk-metrics risk-metrics
                :total-value total-value
                :assessed-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

;; =============================================================================
;; Risk Management Procedures
;; =============================================================================

(defn calculate-var
  "Calculate Value at Risk procedure"
  [portfolio confidence-level]
  (let [returns (:returns portfolio)
        sorted-returns (sort returns)
        index (int (* confidence-level (count sorted-returns)))
        var-value (nth sorted-returns index)
        result {:var-value var-value
                :confidence-level confidence-level
                :portfolio-id (:id portfolio)
                :calculated-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn stress-test-portfolio
  "Stress test portfolio procedure"
  [portfolio scenarios]
  (let [stress-results (map (fn [scenario]
                              (let [stressed-value (* (:total-value portfolio) (:stress-factor scenario))
                                    loss (- (:total-value portfolio) stressed-value)]
                                {:scenario (:name scenario)
                                 :stressed-value stressed-value
                                 :loss loss
                                 :loss-percentage (/ loss (:total-value portfolio))}))
                            scenarios)
        result {:portfolio-id (:id portfolio)
                :stress-results stress-results
                :stress-tested-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn monitor-portfolio-risk
  "Monitor portfolio risk procedure"
  [portfolio risk-limits]
  (let [current-var (calculate-var portfolio 0.05)
        var-violation? (> (:var-value (:data current-var)) (:var-limit risk-limits))
        alert-level (cond
                     var-violation? :high
                     (> (:var-value (:data current-var)) (* (:var-limit risk-limits) 0.8)) :medium
                     :else :low)
        result {:portfolio-id (:id portfolio)
                :alert-level alert-level
                :var-violation var-violation?
                :monitored-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn generate-risk-alert
  "Generate risk alert procedure"
  [risk-data]
  (let [alert (cond
                (= (:alert-level risk-data) :high)
                {:type :risk-alert
                 :severity :high
                 :message "High risk detected in portfolio"
                 :portfolio-id (:portfolio-id risk-data)
                 :timestamp (System/currentTimeMillis)}
                
                (= (:alert-level risk-data) :medium)
                {:type :risk-warning
                 :severity :medium
                 :message "Medium risk level in portfolio"
                 :portfolio-id (:portfolio-id risk-data)
                 :timestamp (System/currentTimeMillis)}
                
                :else
                {:type :risk-info
                 :severity :low
                 :message "Portfolio risk within normal limits"
                 :portfolio-id (:portfolio-id risk-data)
                 :timestamp (System/currentTimeMillis)})]
    (create-procedure-result :success alert)))

;; =============================================================================
;; System Management Procedures
;; =============================================================================

(defn initialize-system
  "Initialize system procedure"
  [config]
  (let [system (core/initialize-system)
        initialized-system (assoc system 
                                 :config config
                                 :initialized-at (System/currentTimeMillis)
                                 :status :running)]
    (create-procedure-result :success initialized-system)))

(defn health-check-system
  "Health check system procedure"
  [system]
  (let [health-status {:status :healthy
                       :uptime (- (System/currentTimeMillis) (:timestamp system))
                       :components {:core :healthy
                                    :trading :healthy
                                    :risk :healthy}
                       :checked-at (System/currentTimeMillis)}]
    (create-procedure-result :success health-status)))

(defn backup-system
  "Backup system procedure"
  [system]
  (let [backup-id (str "backup-" (System/currentTimeMillis))
        backup-data {:backup-id backup-id
                     :system-state system
                     :backed-up-at (System/currentTimeMillis)
                     :backup-size (count (str system))}]
    (create-procedure-result :success backup-data)))

(defn restore-system
  "Restore system procedure"
  [backup-data]
  (let [restored-system (assoc (:system-state backup-data)
                               :restored-from (:backup-id backup-data)
                               :restored-at (System/currentTimeMillis))]
    (create-procedure-result :success restored-system)))

;; =============================================================================
;; Procedure Workflows
;; =============================================================================

(defn execute-procedure-sequence
  "Execute a sequence of procedures"
  [procedures context]
  (loop [remaining-procedures procedures
         results []
         current-context context]
    (if (seq remaining-procedures)
      (let [procedure (first remaining-procedures)
            result (procedure current-context)]
        (if (= (:status result) :success)
          (recur (rest remaining-procedures)
                 (conj results result)
                 (assoc current-context :last-result result))
          (do
            (println "Procedure failed:" (:error result))
            (conj results result))))
      results)))

(defn create-trading-workflow
  "Create a trading workflow"
  [symbol]
  [(fn [context] (fetch-market-data symbol))
   (fn [context] (validate-market-data (:data (:last-result context))))
   (fn [context] (generate-trading-signal (:data (:last-result context))))
   (fn [context] (validate-trading-signal (:data (:last-result context))))
   (fn [context] (process-trading-signal (:data (:last-result context))))
   (fn [context] (execute-trading-signal (:data (:last-result context))))])

(defn create-portfolio-workflow
  "Create a portfolio workflow"
  [portfolio]
  [(fn [context] (calculate-portfolio-value portfolio))
   (fn [context] (assess-portfolio-risk portfolio))
   (fn [context] (optimize-portfolio portfolio))])

;; =============================================================================
;; Demo Functions
;; =============================================================================

(defn demo-market-data-procedures
  "Demonstrate market data procedures"
  []
  (println "=== Market Data Procedures Demo ===")
  
  (let [symbol "AAPL"]
    
    ;; Fetch market data
    (println "1. Fetching market data...")
    (let [fetch-result (fetch-market-data symbol)]
      (println "   Status:" (:status fetch-result))
      (println "   Data:" (:symbol (:data fetch-result)) "at $" (:price (:data fetch-result))))
    
    ;; Validate market data
    (println "2. Validating market data...")
    (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
          validate-result (validate-market-data market-data)]
      (println "   Status:" (:status validate-result))
      (println "   Valid:" (:valid (:data validate-result))))
    
    ;; Transform market data
    (println "3. Transforming market data...")
    (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
          transform-result (transform-market-data market-data)]
      (println "   Status:" (:status transform-result))
      (println "   Transformed:" (:processed (:data transform-result))))
    
    ;; Store market data
    (println "4. Storing market data...")
    (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
          store-result (store-market-data market-data)]
      (println "   Status:" (:status store-result))
      (println "   Storage ID:" (:storage-id (:data store-result)))))
  
  (println "=== Market Data Procedures Demo Complete ==="))

(defn demo-trading-signal-procedures
  "Demonstrate trading signal procedures"
  []
  (println "=== Trading Signal Procedures Demo ===")
  
  (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)]
    
    ;; Generate signal
    (println "1. Generating trading signal...")
    (let [generate-result (generate-trading-signal market-data)]
      (println "   Status:" (:status generate-result))
      (println "   Signal:" (:type (:data generate-result)) "with confidence" (:confidence (:data generate-result))))
    
    ;; Validate signal
    (println "2. Validating trading signal...")
    (let [signal (core/create-trading-signal :buy 0.85 {:strategy "ma"})
          validate-result (validate-trading-signal signal)]
      (println "   Status:" (:status validate-result))
      (println "   Valid:" (:valid (:data validate-result))))
    
    ;; Process signal
    (println "3. Processing trading signal...")
    (let [signal (core/create-trading-signal :buy 0.85 {:strategy "ma"})
          process-result (process-trading-signal signal)]
      (println "   Status:" (:status process-result))
      (println "   Priority:" (:priority (:data process-result))))
    
    ;; Execute signal
    (println "4. Executing trading signal...")
    (let [signal (core/create-trading-signal :buy 0.85 {:strategy "ma"})
          execute-result (execute-trading-signal signal)]
      (println "   Status:" (:status execute-result))
      (println "   Signal ID:" (:signal-id (:data execute-result)))))
  
  (println "=== Trading Signal Procedures Demo Complete ==="))

(defn demo-portfolio-procedures
  "Demonstrate portfolio procedures"
  []
  (println "=== Portfolio Procedures Demo ===")
  
  (let [portfolio {:id "portfolio-1"
                   :positions [{:symbol "AAPL" :quantity 100 :price 150.25}
                               {:symbol "GOOGL" :quantity 50 :price 2800.00}
                               {:symbol "TSLA" :quantity 200 :price 250.50}]
                   :target-allocations {"AAPL" 0.4 "GOOGL" 0.3 "TSLA" 0.3}}]
    
    ;; Calculate portfolio value
    (println "1. Calculating portfolio value...")
    (let [calc-result (calculate-portfolio-value portfolio)]
      (println "   Status:" (:status calc-result))
      (println "   Total Value: $" (:total-value (:data calc-result))))
    
    ;; Rebalance portfolio
    (println "2. Rebalancing portfolio...")
    (let [rebalance-result (rebalance-portfolio portfolio)]
      (println "   Status:" (:status rebalance-result))
      (println "   Rebalanced positions:" (count (:rebalanced-positions (:data rebalance-result)))))
    
    ;; Optimize portfolio
    (println "3. Optimizing portfolio...")
    (let [optimize-result (optimize-portfolio portfolio)]
      (println "   Status:" (:status optimize-result))
      (println "   Expected Return:" (Math/round (* (:expected-return (:optimization-result (:data optimize-result))) 100)) "%"))
    
    ;; Risk assessment
    (println "4. Risk assessment...")
    (let [risk-result (assess-portfolio-risk portfolio)]
      (println "   Status:" (:status risk-result))
      (println "   VaR 95%: $" (:var-95 (:risk-metrics (:data risk-result))))))
  
  (println "=== Portfolio Procedures Demo Complete ==="))

(defn demo-procedure-workflows
  "Demonstrate procedure workflows"
  []
  (println "=== Procedure Workflows Demo ===")
  
  (let [context {:user-id "demo-user" :session-id "demo-session"}
        
        ;; Create a simple trading workflow
        trading-workflow [(fn [context] (fetch-market-data "AAPL"))
                          (fn [context] (generate-trading-signal (:data (:last-result context))))
                          (fn [context] (execute-trading-signal (:data (:last-result context))))]
        
        ;; Create a portfolio workflow
        portfolio {:id "portfolio-1"
                   :positions [{:symbol "AAPL" :quantity 100 :price 150.25}
                               {:symbol "GOOGL" :quantity 50 :price 2800.00}]}
        portfolio-workflow (create-portfolio-workflow portfolio)]
    
    ;; Execute trading workflow
    (println "1. Executing trading workflow...")
    (let [trading-results (execute-procedure-sequence trading-workflow context)]
      (println "   Workflow steps:" (count trading-results))
      (println "   All successful:" (every? #(= (:status %) :success) trading-results)))
    
    ;; Execute portfolio workflow
    (println "2. Executing portfolio workflow...")
    (let [portfolio-results (execute-procedure-sequence portfolio-workflow context)]
      (println "   Workflow steps:" (count portfolio-results))
      (println "   All successful:" (every? #(= (:status %) :success) portfolio-results))))
  
  (println "=== Procedure Workflows Demo Complete ==="))

(defn run-all-procedure-demos
  "Run all procedure demonstrations"
  []
  (println "🎯 === ACTORS Simple Procedures Comprehensive Demo ===")
  (println)
  (demo-market-data-procedures)
  (println)
  (demo-trading-signal-procedures)
  (println)
  (demo-portfolio-procedures)
  (println)
  (demo-procedure-workflows)
  (println)
  (println "🎉 === All Procedure Demos Complete ==="))

(defn -main
  "Main entry point for procedures demo"
  [& args]
  (run-all-procedure-demos))
