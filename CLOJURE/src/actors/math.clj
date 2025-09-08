(ns actors.math
  "Mathematical utilities for financial calculations"
  (:require [clojure.math.numeric-tower :as math]))

(defn mean
  "Calculate mean of numbers"
  [numbers]
  (/ (reduce + numbers) (count numbers)))

(defn standard-deviation
  "Calculate standard deviation"
  [numbers]
  (let [avg (mean numbers)
        variance (/ (reduce + (map #(math/expt (- % avg) 2) numbers)) (count numbers))]
    (math/sqrt variance)))

(defn correlation
  "Calculate correlation between two datasets"
  [x y]
  (let [n (count x)
        sum-x (reduce + x)
        sum-y (reduce + y)
        sum-xy (reduce + (map * x y))
        sum-x2 (reduce + (map #(* % %) x))
        sum-y2 (reduce + (map #(* % %) y))
        numerator (- (* n sum-xy) (* sum-x sum-y))
        denominator (math/sqrt (* (- (* n sum-x2) (* sum-x sum-x))
                                  (- (* n sum-y2) (* sum-y sum-y))))]
    (if (zero? denominator) 0 (/ numerator denominator))))

(defn linear-regression
  "Simple linear regression"
  [x y]
  (let [n (count x)
        sum-x (reduce + x)
        sum-y (reduce + y)
        sum-xy (reduce + (map * x y))
        sum-x2 (reduce + (map #(* % %) x))
        slope (/ (- (* n sum-xy) (* sum-x sum-y))
                 (- (* n sum-x2) (* sum-x sum-x)))
        intercept (/ (- sum-y (* slope sum-x)) n)]
    {:slope slope :intercept intercept}))
