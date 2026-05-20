(ns actors.financial-test
  (:require [clojure.test :refer :all]
            [actors.financial :refer :all]))

(deftest test-calculate-var
  (testing "Value at Risk calculation"
    (let [returns [-0.05 -0.03 -0.01 0.01 0.03 0.05 -0.04 0.02 -0.02 0.04]]
      (is (> (calculate-var returns 0.95) 0))
      (is (> (calculate-var returns 0.99) (calculate-var returns 0.95)))))

  (testing "VaR with single return"
    (let [returns [-0.10]]
      (is (= 0.10 (calculate-var returns 0.95))))))

(deftest test-calculate-sharpe-ratio
  (testing "Sharpe ratio with positive returns"
    (let [returns [0.01 0.02 0.015 0.018 0.012]]
      (is (> (calculate-sharpe-ratio returns 0.0) 0))))

  (testing "Sharpe ratio with zero volatility returns constant value"
    (let [returns [0.01 0.01 0.01 0.01]]
      (is (= 0 (calculate-sharpe-ratio returns 0.01))))))

(deftest test-optimize-portfolio
  (testing "Portfolio optimization returns expected structure"
    (let [positions [{:symbol "AAPL" :quantity 100 :price 150.0 :market-value 15000.0}
                     {:symbol "GOOGL" :quantity 50 :price 200.0 :market-value 10000.0}]
          result (optimize-portfolio positions 0.05)]
      (is (contains? result :positions))
      (is (contains? result :weights))
      (is (contains? result :total-value))
      (is (contains? result :target-return))
      (is (= 2 (count (:weights result))))
      (is (= 25000.0 (:total-value result)))))

  (testing "Portfolio weights sum to approximately 1"
    (let [positions [{:symbol "AAPL" :quantity 100 :price 150.0 :market-value 15000.0}
                     {:symbol "GOOGL" :quantity 50 :price 200.0 :market-value 10000.0}]
          result (optimize-portfolio positions 0.05)
          weight-sum (reduce + (:weights result))]
      (is (< (Math/abs (- weight-sum 1.0)) 0.0001)))))
