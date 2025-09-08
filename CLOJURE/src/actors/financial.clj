(ns actors.financial
  "Financial calculations and portfolio management"
  (:require [actors.core :as core]))

(defn calculate-var
  "Calculate Value at Risk"
  [returns confidence-level]
  (let [sorted-returns (sort returns)
        index (int (* (- 1 confidence-level) (count sorted-returns)))
        var-index (max 0 (min index (dec (count sorted-returns))))]
    (- (nth sorted-returns var-index))))

(defn calculate-sharpe-ratio
  "Calculate Sharpe ratio"
  [returns risk-free-rate]
  (let [avg-return (/ (reduce + returns) (count returns))
        volatility (core/calculate-volatility returns)]
    (if (zero? volatility)
      0
      (/ (- avg-return risk-free-rate) volatility))))

(defn optimize-portfolio
  "Simple portfolio optimization"
  [positions target-return]
  (let [total-value (core/calculate-portfolio-value positions)
        weights (map #(/ (:market-value %) total-value) positions)]
    {:positions positions
     :weights weights
     :total-value total-value
     :target-return target-return}))
