(ns actors.procedures
  "Comprehensive procedures for ACTORS system operations"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >!]]
            [actors.simple-core :as core]))

;; =============================================================================
;; Procedure Framework
;; =============================================================================

(defprotocol Procedure
  "Protocol for defining procedures"
  (execute [this context] "Execute the procedure with given context")
  (validate [this context] "Validate the procedure context")
  (rollback [this context] "Rollback the procedure if needed"))

(defrecord ProcedureResult [status data error timestamp]
  Procedure
  (execute [this context] this)
  (validate [this context] (nil? (:error this)))
  (rollback [this context] this))

(defn create-procedure-result
  "Create a procedure result"
  [status data & {:keys [error]}]
  (->ProcedureResult status data error (System/currentTimeMillis)))

;; =============================================================================
;; Market Data Procedure Functions
;; =============================================================================

(defn fetch-market-data-procedure
  "Fetch market data procedure"
  [symbol context]
  (let [market-data (core/create-market-data symbol 150.25 1000000 0.18)]
    (create-procedure-result :success market-data)))

(defn validate-market-data-procedure
  "Validate market data procedure"
  [market-data context]
  (let [valid? (and (not (nil? (:symbol market-data)))
                    (> (:price market-data) 0)
                    (> (:volume market-data) 0)
                    (>= (:volatility market-data) 0))]
    (create-procedure-result (if valid? :success :error) 
                            {:valid valid? :data market-data})))

(defn transform-market-data-procedure
  "Transform market data procedure"
  [market-data context]
  (let [transformed (assoc market-data 
                          :processed true
                          :timestamp (System/currentTimeMillis)
                          :price-change (if (> (:price market-data) 100) :high :low))]
    (create-procedure-result :success transformed)))

(defn store-market-data-procedure
  "Store market data procedure"
  [market-data context]
  (let [stored-data (assoc market-data :stored true :storage-id (str "md-" (System/currentTimeMillis)))]
    (create-procedure-result :success stored-data)))

;; =============================================================================
;; Market Data Procedures
;; =============================================================================

(defrecord MarketDataProcedure [operation data]
  Procedure
  (execute [this context]
    (try
      (case (:operation this)
        :fetch (fetch-market-data-procedure (:data this) context)
        :validate (validate-market-data-procedure (:data this) context)
        :transform (transform-market-data-procedure (:data this) context)
        :store (store-market-data-procedure (:data this) context)
        (create-procedure-result :error nil :error "Unknown operation"))
      (catch Exception e
        (create-procedure-result :error nil :error (.getMessage e)))))
  
  (validate [this context]
    (and (contains? #{:fetch :validate :transform :store} (:operation this))
         (not (nil? (:data this)))))
  
  (rollback [this context]
    (create-procedure-result :rolled-back nil)))

;; =============================================================================
;; Trading Signal Procedure Functions
;; =============================================================================

(defn generate-signal-procedure
  "Generate trading signal procedure"
  [market-data context]
  (let [price (:price market-data)
        volatility (:volatility market-data)
        signal-type (cond
                     (> price 200) :buy
                     (< price 50) :sell
                     :else :hold)
        confidence (if (> volatility 0.2) 0.8 0.6)
        signal (core/create-trading-signal signal-type confidence {:strategy "price-based"})]
    (create-procedure-result :success signal)))

(defn validate-signal-procedure
  "Validate trading signal procedure"
  [signal context]
  (let [valid? (and (not (nil? (:type signal)))
                    (>= (:confidence signal) 0.0)
                    (<= (:confidence signal) 1.0)
                    (contains? #{:buy :sell :hold} (:type signal)))]
    (create-procedure-result (if valid? :success :error)
                            {:valid valid? :signal signal})))

(defn process-signal-procedure
  "Process trading signal procedure"
  [signal context]
  (let [processed-signal (assoc signal 
                               :processed true
                               :processed-at (System/currentTimeMillis)
                               :priority (if (> (:confidence signal) 0.8) :high :normal))]
    (create-procedure-result :success processed-signal)))

(defn execute-signal-procedure
  "Execute trading signal procedure"
  [signal context]
  (let [execution-result {:signal-id (str "sig-" (System/currentTimeMillis))
                          :executed-at (System/currentTimeMillis)
                          :status :executed
                          :signal signal}]
    (create-procedure-result :success execution-result)))

;; =============================================================================
;; Trading Signal Procedures
;; =============================================================================

(defrecord TradingSignalProcedure [operation data]
  Procedure
  (execute [this context]
    (try
      (case (:operation this)
        :generate (generate-signal-procedure (:data this) context)
        :validate (validate-signal-procedure (:data this) context)
        :process (process-signal-procedure (:data this) context)
        :execute (execute-signal-procedure (:data this) context)
        (create-procedure-result :error nil :error "Unknown operation"))
      (catch Exception e
        (create-procedure-result :error nil :error (.getMessage e)))))
  
  (validate [this context]
    (and (contains? #{:generate :validate :process :execute} (:operation this))
         (not (nil? (:data this)))))
  
  (rollback [this context]
    (create-procedure-result :rolled-back nil)))

(defn generate-signal-procedure
  "Generate trading signal procedure"
  [market-data context]
  (let [price (:price market-data)
        volatility (:volatility market-data)
        signal-type (cond
                     (> price 200) :buy
                     (< price 50) :sell
                     :else :hold)
        confidence (if (> volatility 0.2) 0.8 0.6)
        signal (core/create-trading-signal signal-type confidence {:strategy "price-based"})]
    (create-procedure-result :success signal)))

(defn validate-signal-procedure
  "Validate trading signal procedure"
  [signal context]
  (let [valid? (and (not (nil? (:type signal)))
                    (>= (:confidence signal) 0.0)
                    (<= (:confidence signal) 1.0)
                    (contains? #{:buy :sell :hold} (:type signal)))]
    (create-procedure-result (if valid? :success :error)
                            {:valid valid? :signal signal})))

(defn process-signal-procedure
  "Process trading signal procedure"
  [signal context]
  (let [processed-signal (assoc signal 
                               :processed true
                               :processed-at (System/currentTimeMillis)
                               :priority (if (> (:confidence signal) 0.8) :high :normal))]
    (create-procedure-result :success processed-signal)))

(defn execute-signal-procedure
  "Execute trading signal procedure"
  [signal context]
  (let [execution-result {:signal-id (str "sig-" (System/currentTimeMillis))
                          :executed-at (System/currentTimeMillis)
                          :status :executed
                          :signal signal}]
    (create-procedure-result :success execution-result)))

;; =============================================================================
;; Portfolio Management Procedures
;; =============================================================================

(defrecord PortfolioProcedure [operation data]
  Procedure
  (execute [this context]
    (try
      (case (:operation this)
        :calculate-value (calculate-portfolio-value-procedure (:data this) context)
        :rebalance (rebalance-portfolio-procedure (:data this) context)
        :optimize (optimize-portfolio-procedure (:data this) context)
        :risk-assessment (risk-assessment-procedure (:data this) context)
        (create-procedure-result :error nil :error "Unknown operation"))
      (catch Exception e
        (create-procedure-result :error nil :error (.getMessage e)))))
  
  (validate [this context]
    (and (contains? #{:calculate-value :rebalance :optimize :risk-assessment} (:operation this))
         (not (nil? (:data this)))))
  
  (rollback [this context]
    (create-procedure-result :rolled-back nil)))

(defn calculate-portfolio-value-procedure
  "Calculate portfolio value procedure"
  [portfolio context]
  (let [positions (:positions portfolio)
        total-value (reduce + (map (fn [pos] (* (:quantity pos) (:price pos))) positions))
        result {:portfolio-id (:id portfolio)
                :total-value total-value
                :position-count (count positions)
                :calculated-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn rebalance-portfolio-procedure
  "Rebalance portfolio procedure"
  [portfolio context]
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

(defn optimize-portfolio-procedure
  "Optimize portfolio procedure"
  [portfolio context]
  (let [positions (:positions portfolio)
        optimization-result (loop [iteration 0
                                   best-allocation (map #(/ 1.0 (count positions)) positions)
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

(defn risk-assessment-procedure
  "Risk assessment procedure"
  [portfolio context]
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

(defrecord RiskManagementProcedure [operation data]
  Procedure
  (execute [this context]
    (try
      (case (:operation this)
        :calculate-var (calculate-var-procedure (:data this) context)
        :stress-test (stress-test-procedure (:data this) context)
        :monitor-risk (monitor-risk-procedure (:data this) context)
        :generate-alert (generate-alert-procedure (:data this) context)
        (create-procedure-result :error nil :error "Unknown operation"))
      (catch Exception e
        (create-procedure-result :error nil :error (.getMessage e)))))
  
  (validate [this context]
    (and (contains? #{:calculate-var :stress-test :monitor-risk :generate-alert} (:operation this))
         (not (nil? (:data this)))))
  
  (rollback [this context]
    (create-procedure-result :rolled-back nil)))

(defn calculate-var-procedure
  "Calculate Value at Risk procedure"
  [portfolio context]
  (let [returns (:returns portfolio)
        confidence-level (:confidence-level context 0.05)
        sorted-returns (sort returns)
        index (int (* confidence-level (count sorted-returns)))
        var-value (nth sorted-returns index)
        result {:var-value var-value
                :confidence-level confidence-level
                :portfolio-id (:id portfolio)
                :calculated-at (System/currentTimeMillis)}]
    (create-procedure-result :success result)))

(defn stress-test-procedure
  "Stress test procedure"
  [portfolio context]
  (let [scenarios (:scenarios context [{:name "2008-crisis" :stress-factor 0.7}
                                       {:name "dot-com-bubble" :stress-factor 0.6}
                                       {:name "covid-19" :stress-factor 0.8}])
        stress-results (map (fn [scenario]
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

(defn monitor-risk-procedure
  "Monitor risk procedure"
  [portfolio context]
  (let [risk-limits (:risk-limits context {:var-limit 0.05 :drawdown-limit 0.20})
        current-var (calculate-var-procedure portfolio context)
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

(defn generate-alert-procedure
  "Generate alert procedure"
  [risk-data context]
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

(defrecord SystemProcedure [operation data]
  Procedure
  (execute [this context]
    (try
      (case (:operation this)
        :initialize (initialize-system-procedure (:data this) context)
        :health-check (health-check-procedure (:data this) context)
        :backup (backup-system-procedure (:data this) context)
        :restore (restore-system-procedure (:data this) context)
        (create-procedure-result :error nil :error "Unknown operation"))
      (catch Exception e
        (create-procedure-result :error nil :error (.getMessage e)))))
  
  (validate [this context]
    (and (contains? #{:initialize :health-check :backup :restore} (:operation this))
         (not (nil? (:data this)))))
  
  (rollback [this context]
    (create-procedure-result :rolled-back nil)))

(defn initialize-system-procedure
  "Initialize system procedure"
  [config context]
  (let [system (core/initialize-system)
        initialized-system (assoc system 
                                 :config config
                                 :initialized-at (System/currentTimeMillis)
                                 :status :running)]
    (create-procedure-result :success initialized-system)))

(defn health-check-procedure
  "Health check procedure"
  [system context]
  (let [health-status {:status :healthy
                       :uptime (- (System/currentTimeMillis) (:timestamp system))
                       :components {:core :healthy
                                    :trading :healthy
                                    :risk :healthy}
                       :checked-at (System/currentTimeMillis)}]
    (create-procedure-result :success health-status)))

(defn backup-system-procedure
  "Backup system procedure"
  [system context]
  (let [backup-id (str "backup-" (System/currentTimeMillis))
        backup-data {:backup-id backup-id
                     :system-state system
                     :backed-up-at (System/currentTimeMillis)
                     :backup-size (count (str system))}]
    (create-procedure-result :success backup-data)))

(defn restore-system-procedure
  "Restore system procedure"
  [backup-data context]
  (let [restored-system (assoc (:system-state backup-data)
                               :restored-from (:backup-id backup-data)
                               :restored-at (System/currentTimeMillis))]
    (create-procedure-result :success restored-system)))

;; =============================================================================
;; Procedure Orchestration
;; =============================================================================

(defn execute-procedure-sequence
  "Execute a sequence of procedures"
  [procedures context]
  (loop [remaining-procedures procedures
         results []
         current-context context]
    (if (seq remaining-procedures)
      (let [procedure (first remaining-procedures)
            result (execute procedure current-context)]
        (if (= (:status result) :success)
          (recur (rest remaining-procedures)
                 (conj results result)
                 (assoc current-context :last-result result))
          (do
            (println "Procedure failed:" (:error result))
            (conj results result))))
      results)))

(defn execute-procedure-parallel
  "Execute procedures in parallel"
  [procedures context]
  (let [results (pmap #(execute % context) procedures)]
    results))

(defn create-procedure-workflow
  "Create a procedure workflow"
  [name procedures]
  {:name name
   :procedures procedures
   :created-at (System/currentTimeMillis)})

(defn execute-workflow
  "Execute a procedure workflow"
  [workflow context]
  (let [start-time (System/currentTimeMillis)
        results (execute-procedure-sequence (:procedures workflow) context)
        end-time (System/currentTimeMillis)
        workflow-result {:workflow-name (:name workflow)
                         :results results
                         :execution-time (- end-time start-time)
                         :completed-at end-time}]
    (create-procedure-result :success workflow-result)))

;; =============================================================================
;; Demo Functions
;; =============================================================================

(defn demo-market-data-procedures
  "Demonstrate market data procedures"
  []
  (println "=== Market Data Procedures Demo ===")
  
  (let [symbol "AAPL"
        context {:user-id "demo-user" :session-id "demo-session"}]
    
    ;; Fetch market data
    (println "1. Fetching market data...")
    (let [fetch-proc (->MarketDataProcedure :fetch symbol)
          fetch-result (execute fetch-proc context)]
      (println "   Status:" (:status fetch-result))
      (println "   Data:" (:symbol (:data fetch-result)) "at $" (:price (:data fetch-result))))
    
    ;; Validate market data
    (println "2. Validating market data...")
    (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
          validate-proc (->MarketDataProcedure :validate market-data)
          validate-result (execute validate-proc context)]
      (println "   Status:" (:status validate-result))
      (println "   Valid:" (:valid (:data validate-result))))
    
    ;; Transform market data
    (println "3. Transforming market data...")
    (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
          transform-proc (->MarketDataProcedure :transform market-data)
          transform-result (execute transform-proc context)]
      (println "   Status:" (:status transform-result))
      (println "   Transformed:" (:processed (:data transform-result))))
    
    ;; Store market data
    (println "4. Storing market data...")
    (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
          store-proc (->MarketDataProcedure :store market-data)
          store-result (execute store-proc context)]
      (println "   Status:" (:status store-result))
      (println "   Storage ID:" (:storage-id (:data store-result)))))
  
  (println "=== Market Data Procedures Demo Complete ==="))

(defn demo-trading-signal-procedures
  "Demonstrate trading signal procedures"
  []
  (println "=== Trading Signal Procedures Demo ===")
  
  (let [market-data (core/create-market-data "AAPL" 150.25 1000000 0.18)
        context {:user-id "demo-user" :session-id "demo-session"}]
    
    ;; Generate signal
    (println "1. Generating trading signal...")
    (let [generate-proc (->TradingSignalProcedure :generate market-data)
          generate-result (execute generate-proc context)]
      (println "   Status:" (:status generate-result))
      (println "   Signal:" (:type (:data generate-result)) "with confidence" (:confidence (:data generate-result))))
    
    ;; Validate signal
    (println "2. Validating trading signal...")
    (let [signal (core/create-trading-signal :buy 0.85 {:strategy "ma"})
          validate-proc (->TradingSignalProcedure :validate signal)
          validate-result (execute validate-proc context)]
      (println "   Status:" (:status validate-result))
      (println "   Valid:" (:valid (:data validate-result))))
    
    ;; Process signal
    (println "3. Processing trading signal...")
    (let [signal (core/create-trading-signal :buy 0.85 {:strategy "ma"})
          process-proc (->TradingSignalProcedure :process signal)
          process-result (execute process-proc context)]
      (println "   Status:" (:status process-result))
      (println "   Priority:" (:priority (:data process-result))))
    
    ;; Execute signal
    (println "4. Executing trading signal...")
    (let [signal (core/create-trading-signal :buy 0.85 {:strategy "ma"})
          execute-proc (->TradingSignalProcedure :execute signal)
          execute-result (execute execute-proc context)]
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
                   :target-allocations {"AAPL" 0.4 "GOOGL" 0.3 "TSLA" 0.3}}
        context {:user-id "demo-user" :session-id "demo-session"}]
    
    ;; Calculate portfolio value
    (println "1. Calculating portfolio value...")
    (let [calc-proc (->PortfolioProcedure :calculate-value portfolio)
          calc-result (execute calc-proc context)]
      (println "   Status:" (:status calc-result))
      (println "   Total Value: $" (:total-value (:data calc-result))))
    
    ;; Rebalance portfolio
    (println "2. Rebalancing portfolio...")
    (let [rebalance-proc (->PortfolioProcedure :rebalance portfolio)
          rebalance-result (execute rebalance-proc context)]
      (println "   Status:" (:status rebalance-result))
      (println "   Rebalanced positions:" (count (:rebalanced-positions (:data rebalance-result)))))
    
    ;; Optimize portfolio
    (println "3. Optimizing portfolio...")
    (let [optimize-proc (->PortfolioProcedure :optimize portfolio)
          optimize-result (execute optimize-proc context)]
      (println "   Status:" (:status optimize-result))
      (println "   Expected Return:" (Math/round (* (:expected-return (:optimization-result (:data optimize-result))) 100)) "%"))
    
    ;; Risk assessment
    (println "4. Risk assessment...")
    (let [risk-proc (->PortfolioProcedure :risk-assessment portfolio)
          risk-result (execute risk-proc context)]
      (println "   Status:" (:status risk-result))
      (println "   VaR 95%: $" (:var-95 (:risk-metrics (:data risk-result))))))
  
  (println "=== Portfolio Procedures Demo Complete ==="))

(defn demo-procedure-workflows
  "Demonstrate procedure workflows"
  []
  (println "=== Procedure Workflows Demo ===")
  
  (let [context {:user-id "demo-user" :session-id "demo-session"}
        
        ;; Create a trading workflow
        trading-workflow (create-procedure-workflow
                          "Trading Workflow"
                          [(->MarketDataProcedure :fetch "AAPL")
                           (->MarketDataProcedure :validate nil)
                           (->TradingSignalProcedure :generate nil)
                           (->TradingSignalProcedure :validate nil)
                           (->TradingSignalProcedure :execute nil)])
        
        ;; Create a portfolio workflow
        portfolio-workflow (create-procedure-workflow
                            "Portfolio Workflow"
                            [(->PortfolioProcedure :calculate-value {:id "portfolio-1" :positions []})
                             (->PortfolioProcedure :risk-assessment {:id "portfolio-1" :positions []})
                             (->PortfolioProcedure :optimize {:id "portfolio-1" :positions []})])]
    
    ;; Execute trading workflow
    (println "1. Executing trading workflow...")
    (let [trading-result (execute-workflow trading-workflow context)]
      (println "   Workflow:" (:workflow-name (:data trading-result)))
      (println "   Execution time:" (:execution-time (:data trading-result)) "ms")
      (println "   Results count:" (count (:results (:data trading-result)))))
    
    ;; Execute portfolio workflow
    (println "2. Executing portfolio workflow...")
    (let [portfolio-result (execute-workflow portfolio-workflow context)]
      (println "   Workflow:" (:workflow-name (:data portfolio-result)))
      (println "   Execution time:" (:execution-time (:data portfolio-result)) "ms")
      (println "   Results count:" (count (:results (:data portfolio-result))))))
  
  (println "=== Procedure Workflows Demo Complete ==="))

(defn run-all-procedure-demos
  "Run all procedure demonstrations"
  []
  (println "🎯 === ACTORS Procedures Comprehensive Demo ===")
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
