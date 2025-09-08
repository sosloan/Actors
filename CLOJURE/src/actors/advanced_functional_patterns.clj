(ns actors.advanced-functional-patterns
  "Advanced Functional Programming Patterns - Transducers, Lenses, and Stream Processing"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.math.numeric-tower :as math]
            [actors.simple-higher-order-functions :as hof]))

;; =============================================================================
;; TRANSDUCERS - EFFICIENT COMPOSITION FOR LARGE DATA SETS
;; =============================================================================

(defn price-transducer
  "Transducer for price processing pipeline"
  []
  (comp
   (filter #(not (nil? %)))
   (map #(* % 1.1))
   (filter #(> % 100))
   (map #(Math/round (double %)))))

(defn signal-transducer
  "Transducer for signal processing pipeline"
  []
  (comp
   (map #(hof/calculate-rsi % 14))
   (filter #(and (> % 30) (< % 70)))
   (map #(cond
           (< % 40) :strong-buy
           (< % 50) :buy
           (> % 60) :sell
           :else :hold))))

(defn portfolio-transducer
  "Transducer for portfolio processing pipeline"
  []
  (comp
   (map (fn [[symbol quantity]]
          [symbol (* quantity (hof/get-current-price symbol))]))
   (filter #(> (second %) 1000))
   (map (fn [[symbol value]]
          {:symbol symbol :value value :weight 0}))))

(defn process-with-transducer
  "Process data with transducer"
  [transducer data]
  (into [] transducer data))

(defn process-large-dataset
  "Process large dataset efficiently with transducers"
  [data]
  (let [prices (take 10000 (repeatedly #(rand 200)))
        processed (process-with-transducer (price-transducer) prices)]
    {:original-count (count prices)
     :processed-count (count processed)
     :sample-results (take 10 processed)}))

;; =============================================================================
;; LENSES/OPTICS - FUNCTIONAL NESTED DATA MANIPULATION
;; =============================================================================

(defprotocol Lens
  "Lens protocol for functional data manipulation"
  (get-lens [this data] "Get value through lens")
  (set-lens [this data value] "Set value through lens")
  (update-lens [this data f] "Update value through lens"))

(defrecord SimpleLens [getter setter]
  Lens
  (get-lens [_ data] (getter data))
  (set-lens [_ data value] (setter data value))
  (update-lens [_ data f] (setter data (f (getter data)))))

(defn lens
  "Create a simple lens"
  [getter setter]
  (->SimpleLens getter setter))

(defn compose-lenses
  "Compose multiple lenses"
  [& lenses]
  (lens
   (fn [data]
     (reduce (fn [acc lens] (get-lens lens acc)) data lenses))
   (fn [data value]
     (reduce (fn [acc lens] (set-lens lens acc value)) data (reverse lenses)))))

;; Financial data lenses
(def portfolio-value-lens
  (lens
   #(get % :value)
   #(assoc %1 :value %2)))

(def position-lens
  (lens
   #(get % :positions)
   #(assoc %1 :positions %2)))

(def symbol-position-lens
  (lens
   #(get-in % [:positions :AAPL])
   #(assoc-in %1 [:positions :AAPL] %2)))

(defn update-portfolio-value
  "Update portfolio value using lens"
  [portfolio new-value]
  (update-lens portfolio-value-lens portfolio (constantly new-value)))

(defn update-aapl-position
  "Update AAPL position using lens"
  [portfolio new-quantity]
  (update-lens symbol-position-lens portfolio (constantly new-quantity)))

;; =============================================================================
;; STREAM PROCESSING - REAL-TIME MARKET DATA STREAMS
;; =============================================================================

(defrecord MarketDataStream
  [symbol
   price-stream
   volume-stream
   timestamp-stream
   subscribers])

(defn create-market-data-stream
  "Create a market data stream"
  [symbol]
  (->MarketDataStream
   symbol
   (async/chan 1000)
   (async/chan 1000)
   (async/chan 1000)
   (atom #{})))

(defn subscribe-to-stream
  "Subscribe to market data stream"
  [stream subscriber-fn]
  (swap! (:subscribers stream) conj subscriber-fn))

(defn publish-price-update
  "Publish price update to stream"
  [stream price]
  (go
    (>! (:price-stream stream) price)
    (doseq [subscriber @(:subscribers stream)]
      (subscriber {:type :price-update :symbol (:symbol stream) :price price}))))

(defn publish-volume-update
  "Publish volume update to stream"
  [stream volume]
  (go
    (>! (:volume-stream stream) volume)
    (doseq [subscriber @(:subscribers stream)]
      (subscriber {:type :volume-update :symbol (:symbol stream) :volume volume}))))

(defn stream-processor
  "Process market data stream with functional pipeline"
  [stream]
  (go-loop []
    (when-let [price (<! (:price-stream stream))]
      (let [processed-price (-> price
                                (* 1.1)
                                (Math/round)
                                (double))]
        (publish-price-update stream processed-price))
      (recur))))

(defn create-streaming-trading-system
  "Create streaming trading system"
  [symbols]
  (let [streams (into {} (map (fn [symbol]
                                [symbol (create-market-data-stream symbol)])
                              symbols))
        processors (map stream-processor (vals streams))]
    {:streams streams
     :processors processors}))

;; =============================================================================
;; PARALLEL PROCESSING - LEVERAGE FUNCTIONAL PURITY
;; =============================================================================

(defn parallel-map
  "Parallel map using futures"
  [f coll]
  (let [futures (map #(future (f %)) coll)]
    (map deref futures)))

(defn parallel-filter
  "Parallel filter using futures"
  [pred coll]
  (let [futures (map #(future (pred %)) coll)
        results (map deref futures)]
    (map first (filter second (map vector coll results)))))

(defn parallel-reduce
  "Parallel reduce using partition and merge"
  [f init coll]
  (let [partitions (partition-all 1000 coll)
        futures (map #(future (reduce f init %)) partitions)
        results (map deref futures)]
    (reduce f init results)))

(defn parallel-portfolio-analysis
  "Parallel portfolio analysis"
  [portfolios]
  (let [analysis-fn (fn [portfolio]
                      {:symbol (first (keys portfolio))
                       :value (hof/calculate-portfolio-value portfolio)
                       :weights (hof/calculate-portfolio-weights portfolio)
                       :risk (Math/sqrt (rand))})]
    (parallel-map analysis-fn portfolios)))

;; =============================================================================
;; PROPERTY-BASED TESTING - VERIFY FUNCTIONAL PROPERTIES
;; =============================================================================

(defn test-composition-associativity
  "Test associativity of function composition"
  [f g h test-data]
  (let [composed-left (hof/compose f (hof/compose g h))
        composed-right (hof/compose (hof/compose f g) h)]
    (every? #(= (composed-left %) (composed-right %)) test-data)))

(defn test-composition-identity
  "Test identity property of function composition"
  [f test-data]
  (let [composed-with-identity (hof/compose f identity)
        composed-identity-with (hof/compose identity f)]
    (and (every? #(= (f %) (composed-with-identity %)) test-data)
         (every? #(= (f %) (composed-identity-with %)) test-data))))

(defn test-partial-application-equivalence
  "Test equivalence of partial application"
  [f args test-data]
  (let [partial-fn (apply hof/partial-apply f args)
        full-fn (fn [x] (apply f (concat args [x])))]
    (every? #(= (partial-fn %) (full-fn %)) test-data)))

(defn test-memoization-idempotency
  "Test idempotency of memoization"
  [f test-data ttl]
  (let [memoized-fn (hof/memoize-with-ttl f ttl)]
    (every? #(= (memoized-fn %) (memoized-fn %)) test-data)))

(defn run-property-tests
  "Run all property-based tests"
  []
  (let [test-data (range 1 100)
        f #(* % 2)
        g #(+ % 1)
        h #(- % 1)]
    {:composition-associativity (test-composition-associativity f g h test-data)
     :composition-identity (test-composition-identity f test-data)
     :partial-application-equivalence (test-partial-application-equivalence + [5] test-data)
     :memoization-idempotency (test-memoization-idempotency #(* % %) test-data 1000)}))

;; =============================================================================
;; ADVANCED FUNCTIONAL COMPOSITION
;; =============================================================================

(defn create-adaptive-pipeline
  "Create adaptive pipeline that changes based on data"
  [adapters]
  (fn [data]
    (let [adapter (first (filter #((:predicate %) data) adapters))
          pipeline (if adapter (:pipeline adapter) identity)]
      (pipeline data))))

(defn create-feedback-loop
  "Create feedback loop for continuous improvement"
  [process-fn feedback-fn]
  (let [state (atom {:iterations 0 :last-result nil})]
    (fn [input]
      (let [result (process-fn input)
            feedback (feedback-fn result)
            new-state (swap! state (fn [s]
                                     {:iterations (inc (:iterations s))
                                      :last-result result}))]
        {:result result
         :feedback feedback
         :state new-state}))))

(defn create-conditional-composition
  "Create conditional composition based on runtime conditions"
  [conditions functions]
  (fn [& args]
    (let [condition (first (filter #((:predicate %) args) conditions))
          function (if condition (:function condition) identity)]
      (apply function args))))

;; =============================================================================
;; FINANCIAL STREAM PROCESSING EXAMPLES
;; =============================================================================

(defn create-real-time-trading-pipeline
  "Create real-time trading pipeline"
  [symbol]
  (let [stream (create-market-data-stream symbol)
        price-transducer (price-transducer)
        signal-transducer (signal-transducer)]
    
    ;; Subscribe to price updates
    (subscribe-to-stream stream
                        (fn [data]
                          (when (= (:type data) :price-update)
                            (let [processed-price (process-with-transducer price-transducer [(:price data)])
                                  signal (process-with-transducer signal-transducer [(:price data)])]
                              (println "Processed price:" (first processed-price))
                              (println "Signal:" (first signal))))))
    
    stream))

(defn create-portfolio-monitoring-system
  "Create portfolio monitoring system"
  [portfolios]
  (let [monitoring-stream (async/chan 1000)
        portfolio-transducer (portfolio-transducer)]
    
    (go-loop []
      (when-let [portfolio (<! monitoring-stream)]
        (let [processed (process-with-transducer portfolio-transducer [portfolio])]
          (println "Portfolio processed:" processed))
        (recur)))
    
    {:monitoring-stream monitoring-stream
     :add-portfolio (fn [portfolio] (go (>! monitoring-stream portfolio)))}))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-transducers
  "Demonstrate transducers for efficient data processing"
  []
  (println "=== Transducers Demo ===")
  
  (let [large-dataset (process-large-dataset [])]
    (println "1. Large dataset processing:")
    (println "   Original count:" (:original-count large-dataset))
    (println "   Processed count:" (:processed-count large-dataset))
    (println "   Sample results:" (:sample-results large-dataset)))
  
  (let [prices [100 105 110 108 115 120 118 125 130 128]
        processed (process-with-transducer (price-transducer) prices)]
    (println "2. Price processing with transducer:")
    (println "   Input prices:" prices)
    (println "   Processed prices:" processed)))

(defn demo-lenses
  "Demonstrate lenses for nested data manipulation"
  []
  (println "=== Lenses Demo ===")
  
  (let [portfolio {:value 100000 :positions {:AAPL 100 :GOOGL 50}}]
    (println "1. Original portfolio:" portfolio)
    
    (let [updated-value (update-portfolio-value portfolio 150000)]
      (println "2. Updated value:" updated-value))
    
    (let [updated-position (update-aapl-position portfolio 200)]
      (println "3. Updated AAPL position:" updated-position))))

(defn demo-stream-processing
  "Demonstrate stream processing"
  []
  (println "=== Stream Processing Demo ===")
  
  (let [trading-system (create-streaming-trading-system ["AAPL" "GOOGL"])
        aapl-stream (get-in trading-system [:streams "AAPL"])]
    
    (println "1. Created streaming trading system for AAPL and GOOGL")
    
    ;; Subscribe to AAPL stream
    (subscribe-to-stream aapl-stream
                        (fn [data]
                          (println "   Received data:" data)))
    
    ;; Publish some updates
    (publish-price-update aapl-stream 150.25)
    (publish-volume-update aapl-stream 1000000)
    
    (Thread/sleep 100)
    (println "2. Published price and volume updates")))

(defn demo-parallel-processing
  "Demonstrate parallel processing"
  []
  (println "=== Parallel Processing Demo ===")
  
  (let [portfolios [{"AAPL" 100}
                    {"GOOGL" 50}
                    {"MSFT" 75}]
        start-time (System/currentTimeMillis)
        results (parallel-portfolio-analysis portfolios)
        end-time (System/currentTimeMillis)]
    
    (println "1. Parallel portfolio analysis:")
    (println "   Processing time:" (- end-time start-time) "ms")
    (doseq [result results]
      (println "   " (:symbol result) "-> Value:" (:value result) "Risk:" (format "%.2f" (:risk result))))))

(defn demo-property-testing
  "Demonstrate property-based testing"
  []
  (println "=== Property-Based Testing Demo ===")
  
  (let [test-results (run-property-tests)]
    (println "1. Functional property tests:")
    (doseq [[property result] test-results]
      (println "   " property ":" (if result "✅ PASS" "❌ FAIL")))))

(defn demo-advanced-composition
  "Demonstrate advanced functional composition"
  []
  (println "=== Advanced Functional Composition Demo ===")
  
  ;; Adaptive pipeline
  (let [adapters [{:predicate #(> % 100) :pipeline #(* % 1.1)}
                  {:predicate #(<= % 100) :pipeline #(* % 0.9)}]
        adaptive-pipeline (create-adaptive-pipeline adapters)
        test-values [50 150 75 200]]
    
    (println "1. Adaptive pipeline:")
    (doseq [val test-values]
      (println "   Input:" val "-> Output:" (adaptive-pipeline val))))
  
  ;; Feedback loop
  (let [process-fn #(* % 2)
        feedback-fn #(if (> % 100) :high :low)
        feedback-loop (create-feedback-loop process-fn feedback-fn)
        test-value 75]
    
    (println "2. Feedback loop:")
    (let [result (feedback-loop test-value)]
      (println "   Input:" test-value)
      (println "   Result:" (:result result))
      (println "   Feedback:" (:feedback result))
      (println "   Iterations:" (:iterations (:state result))))))

(defn run-all-advanced-functional-pattern-demos
  "Run all advanced functional pattern demonstrations"
  []
  (println "🎯 === ACTORS Advanced Functional Patterns Comprehensive Demo ===")
  (println)
  (demo-transducers)
  (println)
  (demo-lenses)
  (println)
  (demo-stream-processing)
  (println)
  (demo-parallel-processing)
  (println)
  (demo-property-testing)
  (println)
  (demo-advanced-composition)
  (println)
  (println "🎉 === All Advanced Functional Pattern Demos Complete ==="))

(defn -main
  "Main entry point for advanced functional pattern demo"
  [& args]
  (run-all-advanced-functional-pattern-demos))
