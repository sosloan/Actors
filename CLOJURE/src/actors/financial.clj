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

;; ── FIRE (Financial Independence, Retire Early) functions ─────────────────────

(defn calculate-fire-number
  "Calculate the FI number (required portfolio) for a given annual expense
  level and safe-withdrawal rate.

  Uses the standard formula: fi-number = annual-expenses / withdrawal-rate.
  Throws when withdrawal-rate is not in (0, 1]."
  [annual-expenses withdrawal-rate]
  (when-not (and (pos? withdrawal-rate) (<= withdrawal-rate 1.0))
    (throw (ex-info "withdrawal-rate must be in (0, 1]"
                    {:withdrawal-rate withdrawal-rate})))
  (/ annual-expenses withdrawal-rate))

(defn calculate-coast-fire
  "Calculate the CoastFIRE number: the lump-sum needed today so that,
  with no further contributions, it compounds to fi-number in
  years-to-retirement years at annual-return.

  Formula: coast-fi = fi-number / (1 + annual-return)^years"
  [fi-number years-to-retirement annual-return]
  (when (neg? years-to-retirement)
    (throw (ex-info "years-to-retirement must be non-negative"
                    {:years years-to-retirement})))
  (/ fi-number (Math/pow (+ 1.0 annual-return) years-to-retirement)))

(defn calculate-time-to-fire
  "Estimate the number of months to reach fi-number, starting from
  current-savings, adding monthly-savings each month, compounding at
  annual-return.

  Returns nil when the target is unreachable (e.g. zero savings rate
  and current savings below target), or the number of months as a long."
  [current-savings monthly-savings fi-number annual-return]
  (cond
    (>= current-savings fi-number) 0
    (and (<= monthly-savings 0) (< current-savings fi-number)) nil
    :else
    (let [monthly-return (/ annual-return 12.0)]
      (if (< (Math/abs monthly-return) 1e-10)
        ;; Linear accumulation – no compounding
        (long (Math/ceil (/ (- fi-number current-savings) monthly-savings)))
        ;; Binary search for n such that FV(n) >= fi-number (capped at 1200 months)
        (let [fv (fn [n]
                   (let [factor (Math/pow (+ 1.0 monthly-return) n)]
                     (+ (* current-savings factor)
                        (* monthly-savings (/ (- factor 1.0) monthly-return)))))]
          (if (< (fv 1200) fi-number)
            nil  ;; Cannot reach within 100 years
            (loop [lo 0 hi 1200]
              (if (>= lo hi)
                (long lo)
                (let [mid (+ lo (quot (- hi lo) 2))]
                  (if (>= (fv mid) fi-number)
                    (recur lo mid)
                    (recur (inc mid) hi)))))))))))

(defn calculate-swr-scenarios
  "Generate a sequence of SWR scenario maps for the given annual-expenses
  at withdrawal rates of 3%, 3.5%, 4%, 4.5%, and 5%.

  Each map contains:
    :withdrawal-rate      – annual withdrawal rate (fraction)
    :required-portfolio   – portfolio size needed at this rate
    :annual-withdrawal    – equals annual-expenses
    :monthly-withdrawal   – annual-expenses / 12"
  [annual-expenses]
  (for [rate [0.03 0.035 0.04 0.045 0.05]]
    {:withdrawal-rate    rate
     :required-portfolio (/ annual-expenses rate)
     :annual-withdrawal  annual-expenses
     :monthly-withdrawal (/ annual-expenses 12.0)}))

(defn fire-savings-rate
  "Calculate the savings rate as a percentage of gross income.

  savings-rate = (monthly-savings / monthly-income) * 100

  Returns nil when monthly-income is zero."
  [monthly-savings monthly-income]
  (when (pos? monthly-income)
    (* 100.0 (/ monthly-savings monthly-income))))

(defn classify-fire-progress
  "Classify a saver's current FIRE progress stage based on their
  current-savings relative to their fi-number and coast-fi-number.

  Returns one of:
    :accumulation   – below CoastFIRE threshold
    :coast          – at or above CoastFIRE, below 70% of FI number
    :barista        – 70–99% of FI number (part-time work covers gap)
    :fi             – at or above the full FI number"
  [current-savings fi-number coast-fi-number]
  (cond
    (>= current-savings fi-number)          :fi
    (>= current-savings (* 0.70 fi-number)) :barista
    (>= current-savings coast-fi-number)    :coast
    :else                                   :accumulation))
