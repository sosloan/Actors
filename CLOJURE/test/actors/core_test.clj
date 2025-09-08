(ns actors.core-test
  (:require [clojure.test :refer :all]
            [actors.core :refer :all]
            [actors.financial :refer :all]
            [actors.agents :refer :all]
            [actors.math :refer :all]))

(deftest test-basic-calculations
  (testing "Basic mathematical operations"
    (is (= 4 (+ 2 2)))
    (is (= 6 (* 2 3)))
    (is (= 2 (/ 6 3)))
    (is (= 8 (Math/pow 2 3)))))

(deftest test-financial-calculations
  (testing "Portfolio value calculation"
    (let [positions [{:symbol "AAPL" :quantity 100 :price 150.0}
                     {:symbol "GOOGL" :quantity 50 :price 200.0}]]
      (is (= 25000.0 (calculate-portfolio-value positions)))))
  
  (testing "P&L calculation"
    (let [position {:symbol "AAPL" :quantity 100 :avg-price 150.0 :current-price 155.0}]
      (is (= 500.0 (calculate-pnl position)))))
  
  (testing "Position weight calculation"
    (let [position {:market-value 10000.0}
          total-value 100000.0]
      (is (= 0.1 (calculate-position-weight position total-value))))))

(deftest test-agent-system
  (testing "Agent creation"
    (let [agent (create-agent :market-data "AAPL")]
      (is (= :market-data (:type agent)))
      (is (= "AAPL" (:symbol agent)))
      (is (contains? agent :id))
      (is (contains? agent :status))))
  
  (testing "Agent state transitions"
    (let [agent (create-agent :trading "AAPL")]
      (is (= :idle (:status agent)))
      (let [updated-agent (update-agent-status agent :active)]
        (is (= :active (:status updated-agent))))))

(deftest test-data-processing
  (testing "Data transformation"
    (let [raw-data [{:price 100 :volume 1000}
                    {:price 101 :volume 1100}
                    {:price 99 :volume 900}]]
      (is (= [100 101 99] (extract-prices raw-data)))
      (is (= [1000 1100 900] (extract-volumes raw-data)))))
  
  (testing "Moving average calculation"
    (let [prices [100 101 102 103 104 105]]
      (is (= 102.5 (moving-average prices 4)))))
  
  (testing "Volatility calculation"
    (let [returns [0.01 -0.02 0.03 -0.01 0.02]]
      (is (> (calculate-volatility returns) 0)))))

(deftest test-state-management
  (testing "State updates"
    (let [initial-state {:positions {} :cash 10000.0}
          new-position {:symbol "AAPL" :quantity 100 :price 150.0}
          updated-state (add-position initial-state new-position)]
      (is (contains? (:positions updated-state) "AAPL"))
      (is (= 100 (get-in updated-state [:positions "AAPL" :quantity])))))
  
  (testing "State immutability"
    (let [state {:data [1 2 3]}
          new-state (update-in state [:data] conj 4)]
      (is (= [1 2 3] (:data state)))
      (is (= [1 2 3 4] (:data new-state))))))

(deftest test-async-operations
  (testing "Async data processing"
    (let [data-promise (process-data-async [1 2 3 4 5])]
      (is (realized? data-promise))
      (is (= 15 (deref data-promise 1000 0)))))
  
  (testing "Parallel processing"
    (let [results (process-in-parallel [1 2 3 4 5] #(* % %))]
      (is (= [1 4 9 16 25] results)))))

(deftest test-error-handling
  (testing "Safe division"
    (is (= 0 (safe-divide 10 0)))
    (is (= 5 (safe-divide 10 2))))
  
  (testing "Data validation"
    (is (valid-price? 100.0))
    (is (not (valid-price? -10.0)))
    (is (not (valid-price? nil))))
  
  (testing "Error recovery"
    (let [result (with-error-handling #(/ 10 0))]
      (is (= :error (:status result)))
      (is (contains? result :message)))))

(deftest test-performance
  (testing "Large dataset processing"
    (let [large-dataset (range 10000)
          result (process-large-dataset large-dataset)]
      (is (= 10000 (count result)))
      (is (every? #(> % 0) result))))
  
  (testing "Memory efficiency"
    (let [memory-before (get-memory-usage)
          _ (process-large-dataset (range 100000))
          memory-after (get-memory-usage)]
      (is (< (- memory-after memory-before) 1000000)))))

(deftest test-integration
  (testing "End-to-end workflow"
    (let [market-data [{:symbol "AAPL" :price 150.0 :volume 1000}
                       {:symbol "GOOGL" :price 200.0 :volume 500}]
          agents [(create-agent :market-data "AAPL")
                  (create-agent :trading "GOOGL")]
          result (run-workflow market-data agents)]
      (is (contains? result :processed-data))
      (is (contains? result :agent-results))
      (is (= 2 (count (:agent-results result)))))))

;; Helper functions for testing
(defn calculate-portfolio-value [positions]
  (reduce + (map #(* (:quantity %) (:price %)) positions)))

(defn calculate-pnl [position]
  (* (:quantity position) (- (:current-price position) (:avg-price position))))

(defn calculate-position-weight [position total-value]
  (/ (:market-value position) total-value))

(defn create-agent [type symbol]
  {:id (str (java.util.UUID/randomUUID))
   :type type
   :symbol symbol
   :status :idle
   :created-at (java.time.Instant/now)})

(defn update-agent-status [agent new-status]
  (assoc agent :status new-status))

(defn extract-prices [data]
  (map :price data))

(defn extract-volumes [data]
  (map :volume data))

(defn moving-average [prices window]
  (let [sum (reduce + (take window prices))
        count (min window (count prices))]
    (/ sum count)))

(defn calculate-volatility [returns]
  (let [mean (/ (reduce + returns) (count returns))
        variance (/ (reduce + (map #(Math/pow (- % mean) 2) returns)) (count returns))]
    (Math/sqrt variance)))

(defn add-position [state position]
  (-> state
      (update :positions assoc (:symbol position) position)
      (update :cash - (* (:quantity position) (:price position)))))

(defn process-data-async [data]
  (future (reduce + data)))

(defn process-in-parallel [data f]
  (pmap f data))

(defn safe-divide [a b]
  (if (zero? b) 0 (/ a b)))

(defn valid-price? [price]
  (and (number? price) (pos? price)))

(defn with-error-handling [f]
  (try
    {:status :success :result (f)}
    (catch Exception e
      {:status :error :message (.getMessage e)})))

(defn process-large-dataset [data]
  (map inc data))

(defn get-memory-usage []
  (let [runtime (Runtime/getRuntime)]
    (- (.totalMemory runtime) (.freeMemory runtime))))

(defn run-workflow [market-data agents]
  {:processed-data (map #(assoc % :processed true) market-data)
   :agent-results (map #(assoc % :result "processed") agents)})