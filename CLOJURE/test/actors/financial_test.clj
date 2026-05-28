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

;; ── FIRE function tests ───────────────────────────────────────────────────────

(deftest test-calculate-fire-number
  (testing "Classic 4% rule: $80k/year → $2M"
    (is (< (Math/abs (- (calculate-fire-number 80000.0 0.04) 2000000.0)) 1.0)))

  (testing "3% SWR gives a larger portfolio target than 4%"
    (is (> (calculate-fire-number 80000.0 0.03)
           (calculate-fire-number 80000.0 0.04))))

  (testing "Invalid withdrawal rate throws"
    (is (thrown? clojure.lang.ExceptionInfo (calculate-fire-number 80000.0 0.0)))
    (is (thrown? clojure.lang.ExceptionInfo (calculate-fire-number 80000.0 -0.01)))
    (is (thrown? clojure.lang.ExceptionInfo (calculate-fire-number 80000.0 1.1)))))

(deftest test-calculate-coast-fire
  (testing "Zero years to retirement → coast equals FI number"
    (let [fi 1000000.0
          coast (calculate-coast-fire fi 0.0 0.07)]
      (is (< (Math/abs (- coast fi)) 1.0))))

  (testing "Longer horizon → smaller coast number"
    (let [fi 1000000.0
          coast-10 (calculate-coast-fire fi 10.0 0.07)
          coast-20 (calculate-coast-fire fi 20.0 0.07)]
      (is (> coast-10 coast-20))
      (is (<= coast-10 fi))))

  (testing "Negative years throws"
    (is (thrown? clojure.lang.ExceptionInfo (calculate-coast-fire 1000000.0 -1.0 0.07)))))

(deftest test-calculate-time-to-fire
  (testing "Already at FI → 0 months"
    (is (= 0 (calculate-time-to-fire 1000000.0 1000.0 500000.0 0.07))))

  (testing "Linear accumulation with zero return"
    ;; $0 savings, $1k/month, need $12k → 12 months
    (is (= 12 (calculate-time-to-fire 0.0 1000.0 12000.0 0.0))))

  (testing "With positive return, fewer months than linear"
    (let [linear  (calculate-time-to-fire 0.0 1000.0 120000.0 0.0)
          with-r  (calculate-time-to-fire 0.0 1000.0 120000.0 0.07)]
      (is (< with-r linear))))

  (testing "Zero savings rate → nil (unreachable)"
    (is (nil? (calculate-time-to-fire 0.0 0.0 1000000.0 0.07)))))

(deftest test-calculate-swr-scenarios
  (testing "Returns exactly 5 scenarios"
    (is (= 5 (count (calculate-swr-scenarios 80000.0)))))

  (testing "Rates are ascending"
    (let [rates (map :withdrawal-rate (calculate-swr-scenarios 80000.0))]
      (is (apply < rates))))

  (testing "Lower rate → higher required portfolio"
    (let [portfolios (map :required-portfolio (calculate-swr-scenarios 80000.0))]
      (is (apply > portfolios))))

  (testing "4% scenario for $40k/year → $1M portfolio"
    (let [scenarios (calculate-swr-scenarios 40000.0)
          four-pct  (first (filter #(< (Math/abs (- (:withdrawal-rate %) 0.04)) 1e-10) scenarios))]
      (is (< (Math/abs (- (:required-portfolio four-pct) 1000000.0)) 1.0))
      (is (< (Math/abs (- (:monthly-withdrawal four-pct) (/ 40000.0 12.0))) 0.01)))))

(deftest test-fire-savings-rate
  (testing "Standard savings rate calculation"
    (is (< (Math/abs (- (fire-savings-rate 3000.0 10000.0) 30.0)) 0.001)))

  (testing "Zero income returns nil"
    (is (nil? (fire-savings-rate 1000.0 0.0))))

  (testing "100% savings rate"
    (is (< (Math/abs (- (fire-savings-rate 5000.0 5000.0) 100.0)) 0.001))))

(deftest test-classify-fire-progress
  (let [fi 1000000.0
        coast 400000.0]
    (testing "Full FI"
      (is (= :fi (classify-fire-progress 1000000.0 fi coast))))

    (testing "BaristaFIRE (70-99% of FI)"
      (is (= :barista (classify-fire-progress 750000.0 fi coast))))

    (testing "CoastFIRE (at coast number, below 70%)"
      (is (= :coast (classify-fire-progress 500000.0 fi coast))))

    (testing "Accumulation phase (below coast)"
      (is (= :accumulation (classify-fire-progress 100000.0 fi coast))))))
