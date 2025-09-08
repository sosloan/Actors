(ns actors.simple-test
  (:require [clojure.test :refer :all]
            [actors.core :refer :all]))

(deftest test-basic-calculations
  (testing "Basic mathematical operations"
    (is (= 4 (+ 2 2)))
    (is (= 6 (* 2 3)))
    (is (= 2 (/ 6 3)))))

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
        (is (= :active (:status updated-agent)))))))

(deftest test-data-processing
  (testing "Data transformation"
    (let [raw-data [{:price 100 :volume 1000}
                    {:price 101 :volume 1100}
                    {:price 99 :volume 900}]]
      (is (= [100 101 99] (extract-prices raw-data)))
      (is (= [1000 1100 900] (extract-volumes raw-data)))))
  
  (testing "Moving average calculation"
    (let [prices [100 101 102 103 104 105]]
      (is (= 203/2 (moving-average prices 4)))))
  
  (testing "Volatility calculation"
    (let [returns [0.01 -0.02 0.03 -0.01 0.02]]
      (is (> (calculate-volatility returns) 0)))))

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
