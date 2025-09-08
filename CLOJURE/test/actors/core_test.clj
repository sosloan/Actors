(ns actors.core-test
  (:require [clojure.test :refer :all]
            [actors.core :as core]
            [clojure.java-time :as time]))

(deftest test-market-data-creation
  (testing "Market data creation and access"
    (let [market-data (core/->MarketData "AAPL" 150.25 1000000 (time/instant) 0.18)]
      (is (= "AAPL" (:symbol market-data)))
      (is (= 150.25 (core/price market-data)))
      (is (= 0.18 (core/volatility market-data)))
      (is (= {:volatility 0.18 :volume 1000000} (core/risk-metrics market-data))))))

(deftest test-trading-signal-creation
  (testing "Trading signal creation and access"
    (let [signal (core/->TradingSignal :buy 0.85 (time/instant) {:strategy "ma"})]
      (is (= :buy (core/signal-type signal)))
      (is (= 0.85 (core/confidence signal)))
      (is (not (nil? (core/timestamp signal)))))))

(deftest test-returns-calculation
  (testing "Returns calculation"
    (let [prices [100.0 105.0 110.0 108.0 115.0]
          returns (core/calculate-returns prices)]
      (is (= 4 (count returns)))
      (is (= 0.05 (nth returns 0)))
      (is (= 0.047619047619047616 (nth returns 1)))
      (is (= -0.01818181818181818 (nth returns 2)))
      (is (= 0.06481481481481481 (nth returns 3))))))

(deftest test-volatility-calculation
  (testing "Volatility calculation"
    (let [returns [0.05 0.03 -0.02 0.04 0.01]
          volatility (core/calculate-volatility returns)]
      (is (number? volatility))
      (is (> volatility 0)))))

(deftest test-sharpe-ratio-calculation
  (testing "Sharpe ratio calculation"
    (let [returns [0.05 0.03 -0.02 0.04 0.01]
          risk-free-rate 0.02
          sharpe (core/calculate-sharpe-ratio returns risk-free-rate)]
      (is (number? sharpe)))))

(deftest test-state-management
  (testing "Immutable state management"
    (let [initial-state (core/create-state)
          updated-state (core/update-state initial-state {:market-data {"AAPL" {:price 150.25}}})]
      (is (not= initial-state updated-state))
      (is (= {"AAPL" {:price 150.25}} (:market-data updated-state)))
      (is (not (nil? (:timestamp updated-state)))))))

(deftest test-data-transformations
  (testing "Functional data transformations"
    (let [market-data {"AAPL" {:price 150.25 :volume 1000000}
                       "GOOGL" {:price 2800.00 :volume 500000}}
          transformed (core/map-market-data market-data #(assoc % :processed true))]
      (is (= true (:processed (get transformed "AAPL"))))
      (is (= true (:processed (get transformed "GOOGL")))))))

(deftest test-signal-filtering
  (testing "Signal filtering"
    (let [signals [(core/->TradingSignal :buy 0.9 (time/instant) {})
                   (core/->TradingSignal :sell 0.3 (time/instant) {})
                   (core/->TradingSignal :hold 0.8 (time/instant) {})]
          filtered (core/filter-signals signals #(> (core/confidence %) 0.5))]
      (is (= 2 (count filtered)))
      (is (= :buy (core/signal-type (first filtered))))
      (is (= :hold (core/signal-type (second filtered)))))))

(deftest test-channel-creation
  (testing "Channel creation"
    (let [market-channel (core/create-market-data-channel)
          signal-channel (core/create-signal-channel)]
      (is (not (nil? market-channel)))
      (is (not (nil? signal-channel))))))

(deftest test-system-initialization
  (testing "System initialization"
    (let [system (core/initialize-system)]
      (is (not (nil? (:state system))))
      (is (not (nil? (:channels system))))
      (is (not (nil? (:integration system)))))))

(deftest test-pattern-matching
  (testing "Pattern matching on signal types"
    (let [buy-signal (core/->TradingSignal :buy 0.8 (time/instant) {})
          sell-signal (core/->TradingSignal :sell 0.7 (time/instant) {})
          hold-signal (core/->TradingSignal :hold 0.6 (time/instant) {})]
      (is (clojure.string/includes? (core/match-signal-type buy-signal) "BUY"))
      (is (clojure.string/includes? (core/match-signal-type sell-signal) "SELL"))
      (is (clojure.string/includes? (core/match-signal-type hold-signal) "HOLD")))))

(deftest test-destructuring
  (testing "Market data destructuring"
    (let [market-data {:symbol "AAPL" :price 150.25 :volume 1000000 :timestamp (time/instant)}
          result (core/destructure-market-data market-data)]
      (is (= "AAPL" (:symbol result)))
      (is (= :high (:price-change result)))
      (is (= :high (:volume-category result))))))

(deftest test-higher-order-functions
  (testing "Higher-order function creation"
    (let [processor (core/create-signal-processor {:min-confidence 0.7
                                                  :filters [(fn [s] (> (core/confidence s) 0.5))]})
          high-confidence-signal (core/->TradingSignal :buy 0.8 (time/instant) {})
          low-confidence-signal (core/->TradingSignal :buy 0.6 (time/instant) {})]
      (is (not (nil? (processor high-confidence-signal))))
      (is (nil? (processor low-confidence-signal))))))

(deftest test-risk-calculator
  (testing "Risk calculator creation"
    (let [calculator (core/create-risk-calculator {:var-confidence 0.05
                                                  :max-position-size 10000})
          positions [{:size 5000 :returns [0.01 0.02 -0.01 0.03]}
                     {:size 8000 :returns [0.02 0.01 0.02 -0.02]}]]
      (is (not (nil? (calculator positions)))))))

(deftest test-system-lifecycle
  (testing "System start and shutdown"
    (let [system (core/initialize-system)
          started-system (core/start-system system)
          shutdown-system (core/shutdown-system started-system)]
      (is (= :shutdown (:status shutdown-system))))))
