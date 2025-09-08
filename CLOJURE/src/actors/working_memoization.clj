(ns actors.working-memoization
  "Working Memoization and Data-Driven Programming System"
  (:require [actors.simple-higher-order-functions :as hof]))

;; Simple memoization functions
(defn create-simple-memoizer [f ttl-ms]
  (let [cache (atom {})]
    (fn [& args]
      (let [key (hash args)
            now (System/currentTimeMillis)
            cached (get @cache key)]
        (if (and cached (< (- now (:timestamp cached)) ttl-ms))
          (:value cached)
          (let [result (apply f args)]
            (when (not (nil? result))
              (swap! cache assoc key {:value result :timestamp now}))
            result))))))

;; Simple data flow execution
(defn execute-simple-dataflow [steps data]
  (reduce (fn [acc step]
            (if (fn? step)
              (step acc)
              acc))
          data
          steps))

;; Demo functions
(defn demo-simple-memoization []
  (println "=== Simple Memoization Demo ===")
  (let [memoized-fn (create-simple-memoizer #(* % %) 1000)
        test-values [5 5 6 5]]
    (doseq [val test-values]
      (let [result (memoized-fn val)]
        (println (str "Input: " val " -> Result: " result))))))

(defn demo-simple-dataflow []
  (println "=== Simple Data Flow Demo ===")
  (let [steps [#(assoc % :processed true)
               #(assoc % :timestamp (System/currentTimeMillis))]
        data {:input "test"}
        result (execute-simple-dataflow steps data)]
    (println "Input:" data)
    (println "Output:" result)))

(defn run-all-working-demos []
  (println "🎯 === Working Memoization and Data-Driven Demo ===")
  (demo-simple-memoization)
  (demo-simple-dataflow)
  (println "🎉 === Demo Complete ==="))

(defn -main [& args]
  (run-all-working-demos))
