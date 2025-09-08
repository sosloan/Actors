(ns actors.simple-core
  "Simplified core functional system for ACTORS"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >!]]
            [clojure.data.json :as json]))

;; =============================================================================
;; Simple Data Structures
;; =============================================================================

(defn create-market-data
  "Create market data map"
  [symbol price volume volatility]
  {:symbol symbol
   :price price
   :volume volume
   :volatility volatility
   :timestamp (System/currentTimeMillis)})

(defn create-trading-signal
  "Create trading signal map"
  [type confidence data]
  {:type type
   :confidence confidence
   :data data
   :timestamp (System/currentTimeMillis)})

;; =============================================================================
;; Mathematical Operations
;; =============================================================================

(defn calculate-returns
  "Calculate returns from price series"
  [prices]
  (->> prices
       (partition 2 1)
       (map (fn [[prev curr]] (/ (- curr prev) prev)))))

(defn calculate-volatility
  "Calculate volatility from returns"
  [returns]
  (let [mean (double (/ (reduce + returns) (count returns)))
        variance (/ (reduce + (map #(Math/pow (- % mean) 2) returns)) (count returns))]
    (Math/sqrt variance)))

(defn calculate-sharpe-ratio
  "Calculate Sharpe ratio"
  [returns risk-free-rate]
  (let [excess-returns (map #(- % risk-free-rate) returns)
        mean-excess (double (/ (reduce + excess-returns) (count excess-returns)))
        volatility (calculate-volatility returns)]
    (if (zero? volatility) 0 (/ mean-excess volatility))))

;; =============================================================================
;; Simple Moving Average
;; =============================================================================

(defn simple-moving-average
  "Calculate simple moving average"
  [prices period]
  (let [window (take-last period prices)]
    (/ (reduce + window) (count window))))

;; =============================================================================
;; Channel Operations
;; =============================================================================

(defn create-market-data-channel
  "Create a channel for market data streaming"
  []
  (chan 1000))

(defn create-signal-channel
  "Create a channel for trading signals"
  []
  (chan 100))

;; =============================================================================
;; System Functions
;; =============================================================================

(defn initialize-system
  "Initialize the simple system"
  []
  {:status :initialized
   :channels {:market-data (create-market-data-channel)
              :signals (create-signal-channel)}
   :timestamp (System/currentTimeMillis)})

(defn demo-functionality
  "Demonstrate basic functionality"
  []
  (println "=== ACTORS Simple Core Demo ===")
  
  ;; Create market data
  (let [market-data (create-market-data "AAPL" 150.25 1000000 0.18)]
    (println "Market Data:" market-data))
  
  ;; Create trading signal
  (let [signal (create-trading-signal :buy 0.85 {:strategy "ma"})]
    (println "Trading Signal:" signal))
  
  ;; Calculate returns and volatility
  (let [prices [145.50 147.20 149.80 150.25 152.10]
        returns (calculate-returns prices)
        volatility (calculate-volatility returns)
        sharpe (calculate-sharpe-ratio returns 0.02)]
    (println "Returns:" returns)
    (println "Volatility:" volatility)
    (println "Sharpe Ratio:" sharpe))
  
  ;; Calculate moving average
  (let [prices [145.50 147.20 149.80 150.25 152.10 151.80 153.40 155.20]
        sma (simple-moving-average prices 5)]
    (println "5-period SMA:" sma))
  
  ;; Initialize system
  (let [system (initialize-system)]
    (println "System initialized:" system))
  
  (println "=== Demo Complete ==="))

(defn -main
  "Main entry point"
  [& args]
  (demo-functionality))
