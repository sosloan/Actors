(ns actors.core
  "Core namespace for ACTORS Clojure functional system"
  (:require [clojure.data.json :as json]
            [clojure.core.async :as async]
            [clj-time.core :as time]
            [clj-time.format :as time-format]))

(defn calculate-portfolio-value
  "Calculate total portfolio value from positions"
  [positions]
  (reduce + (map #(* (:quantity %) (:price %)) positions)))

(defn calculate-pnl
  "Calculate profit and loss for a position"
  [position]
  (* (:quantity position) (- (:current-price position) (:avg-price position))))

(defn calculate-position-weight
  "Calculate position weight in portfolio"
  [position total-value]
  (/ (:market-value position) total-value))

(defn create-agent
  "Create a new agent with specified type and symbol"
  [type symbol]
  {:id (str (java.util.UUID/randomUUID))
   :type type
   :symbol symbol
   :status :idle
   :created-at (time/now)})

(defn update-agent-status
  "Update agent status"
  [agent new-status]
  (assoc agent :status new-status))

(defn extract-prices
  "Extract prices from market data"
  [data]
  (map :price data))

(defn extract-volumes
  "Extract volumes from market data"
  [data]
  (map :volume data))

(defn moving-average
  "Calculate moving average of prices"
  [prices window]
  (let [sum (reduce + (take window prices))
        count (min window (count prices))]
    (/ sum count)))

(defn calculate-volatility
  "Calculate volatility from returns"
  [returns]
  (let [mean (/ (reduce + returns) (count returns))
        variance (/ (reduce + (map #(Math/pow (- % mean) 2) returns)) (count returns))]
    (Math/sqrt variance)))

(defn add-position
  "Add position to portfolio state"
  [state position]
  (-> state
      (update :positions assoc (:symbol position) position)
      (update :cash - (* (:quantity position) (:price position)))))

(defn process-data-async
  "Process data asynchronously"
  [data]
  (future (reduce + data)))

(defn process-in-parallel
  "Process data in parallel"
  [data f]
  (pmap f data))

(defn safe-divide
  "Safe division that returns 0 for division by zero"
  [a b]
  (if (zero? b) 0 (/ a b)))

(defn valid-price?
  "Check if price is valid"
  [price]
  (and (number? price) (pos? price)))

(defn with-error-handling
  "Execute function with error handling"
  [f]
  (try
    {:status :success :result (f)}
    (catch Exception e
      {:status :error :message (.getMessage e)})))

(defn process-large-dataset
  "Process large dataset efficiently"
  [data]
  (map inc data))

(defn get-memory-usage
  "Get current memory usage"
  []
  (let [runtime (Runtime/getRuntime)]
    (- (.totalMemory runtime) (.freeMemory runtime))))

(defn run-workflow
  "Run end-to-end workflow"
  [market-data agents]
  {:processed-data (map #(assoc % :processed true) market-data)
   :agent-results (map #(assoc % :result "processed") agents)})
