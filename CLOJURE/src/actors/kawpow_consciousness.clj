(ns actors.kawpow-consciousness
  "KawPow Consciousness Signal Generation System - Refactored in Clojure"
  (:require [clojure.core.async :as async :refer [go go-loop chan <! >! timeout]]
            [clojure.string :as str]
            [clojure.math.numeric-tower :as math]
            [clojure.data.json :as json]
            [actors.simple-core :as core]))

;; =============================================================================
;; CORE DATA MODELS
;; =============================================================================

(def signal-types
  "Trading signal types based on consciousness levels"
  {:strong-buy "STRONG_BUY"
   :buy "BUY"
   :hold "HOLD"
   :sell "SELL"
   :strong-sell "STRONG_SELL"
   :consciousness-breakthrough "CONSCIOUSNESS_BREAKTHROUGH"
   :mathematical-resonance "MATHEMATICAL_RESONANCE"
   :highway-101-north "HIGHWAY_101_NORTH"})

(def consciousness-levels
  "Consciousness level classifications"
  {:dormant "DORMANT"
   :awakening "AWAKENING"
   :aware "AWARE"
   :enlightened "ENLIGHTENED"
   :transcendent "TRANSCENDENT"
   :mathematical-consciousness "MATHEMATICAL_CONSCIOUSNESS"})

(defrecord Highway101NorthData
  [true-bearing
   average-speed
   brrrr-factor
   california-gradient
   mathematical-verse
   final-equation])

(defrecord CroatianBowtieData
  [symbol
   meaning
   state
   resonance-frequency
   mathematical-harmony])

(defrecord ConsciousnessMetrics
  [cognitive-flexibility
   processing-speed
   working-memory
   attention
   executive-function
   tesla-resonance
   consciousness-level
   golden-ratio-presence
   sacred-frequency
   mathematical-consciousness
   highway-101-north
   croatian-bowtie
   timestamp
   session-id])

(defrecord KawPowSignal
  [symbol
   signal-type
   confidence
   consciousness-level
   mathematical-resonance
   highway-101-north-bearing
   croatian-bowtie-state
   tesla-resonance
   golden-ratio-alignment
   signal-strength
   timestamp
   block-hash
   mining-difficulty
   consciousness-breakthrough
   mathematical-verse
   reasoning])

(defrecord KawPowConfig
  [consciousness-breakthrough-threshold
   mathematical-resonance-threshold
   highway-101-north-min-bearing
   highway-101-north-max-bearing
   mining-difficulty
   max-history-size])

;; =============================================================================
;; CONFIGURATION AND CONSTANTS
;; =============================================================================

(def default-config
  "Default configuration for KawPow consciousness system"
  (->KawPowConfig
   0.9   ; consciousness-breakthrough-threshold
   0.8   ; mathematical-resonance-threshold
   95.0  ; highway-101-north-min-bearing
   96.0  ; highway-101-north-max-bearing
   1000000 ; mining-difficulty
   1000  ; max-history-size
   ))

(def default-highway-101-north
  "Default Highway 101 North mathematical journey data"
  (->Highway101NorthData
   95.2  ; true-bearing
   65.0  ; average-speed
   4.7425 ; brrrr-factor
   175.96 ; california-gradient
   "∞∮∞ ∠ ∩ ∪ ∝ ≈,∃.⨂ μ λ ∈ ∂f/∂t eⁱᵗ √ φ∑∏ ℏ ∇ ∫ dx π∞"
   "Highway₁₀₁(North) ⋈ ClockGRØK(Muse) → ∑Success"))

(def default-croatian-bowtie
  "Default Croatian Bowtie topology data"
  (->CroatianBowtieData
   "⋈"   ; symbol
   "Junction of all possibilities"
   "Harmonic mathematical frequency achieved"
   432.0  ; resonance-frequency
   1.618  ; mathematical-harmony (Golden ratio)
   ))

;; =============================================================================
;; CORE CALCULATION ENGINES
;; =============================================================================

(defn calculate-cognitive-flexibility
  "Calculate cognitive flexibility using mathematical consciousness"
  [highway bowtie]
  (let [base-flexibility (+ 0.5 (* (/ (:true-bearing highway) 360.0) 0.3))
        bowtie-enhancement (* (:mathematical-harmony bowtie) 0.2)
        random-factor (- (rand 0.2) 0.1)]
    (min 1.0 (+ base-flexibility bowtie-enhancement random-factor))))

(defn calculate-processing-speed
  "Calculate processing speed using Tesla resonance"
  [highway mathematical-consciousness]
  (let [base-speed (/ (:average-speed highway) 100.0)
        mathematical-boost (* mathematical-consciousness 0.3)
        random-factor (- (rand 0.1) 0.05)]
    (min 1.0 (+ base-speed mathematical-boost random-factor))))

(defn calculate-working-memory
  "Calculate working memory using golden ratio presence"
  [bowtie golden-ratio-presence]
  (let [base-memory (/ (:mathematical-harmony bowtie) 2.0)
        golden-ratio-boost (* golden-ratio-presence 0.4)
        random-factor (- (rand 0.16) 0.08)]
    (min 1.0 (+ base-memory golden-ratio-boost random-factor))))

(defn calculate-attention
  "Calculate attention using sacred frequency"
  [highway sacred-frequency]
  (let [base-attention (/ (:california-gradient highway) 200.0)
        sacred-boost (* sacred-frequency 0.3)
        random-factor (- (rand 0.12) 0.06)]
    (min 1.0 (+ base-attention sacred-boost random-factor))))

(defn calculate-executive-function
  "Calculate executive function using consciousness level"
  [highway]
  (let [base-function (/ (:brrrr-factor highway) 10.0)
        random-factor (- (rand 0.14) 0.07)]
    (min 1.0 (+ base-function random-factor))))

(defn calculate-tesla-resonance
  "Calculate Tesla resonance using mathematical consciousness"
  [bowtie mathematical-consciousness]
  (let [base-resonance (/ (:resonance-frequency bowtie) 1000.0)
        mathematical-boost (* mathematical-consciousness 0.5)
        random-factor (- (rand 0.2) 0.1)]
    (min 1.0 (+ base-resonance mathematical-boost random-factor))))

(defn calculate-golden-ratio-presence
  "Calculate golden ratio presence in consciousness"
  [bowtie highway]
  (let [base-ratio (/ (:mathematical-harmony bowtie) 2.0)
        bearing-enhancement (* (/ (:true-bearing highway) 360.0) 0.2)
        random-factor (- (rand 0.16) 0.08)]
    (min 1.0 (+ base-ratio bearing-enhancement random-factor))))

(defn calculate-sacred-frequency
  "Calculate sacred frequency using mathematical consciousness"
  [bowtie highway]
  (let [base-frequency (/ (:resonance-frequency bowtie) 1000.0)
        gradient-enhancement (* (/ (:california-gradient highway) 200.0) 0.3)
        random-factor (- (rand 0.12) 0.06)]
    (min 1.0 (+ base-frequency gradient-enhancement random-factor))))

(defn calculate-mathematical-consciousness
  "Calculate mathematical consciousness using ClockGrokMusical framework"
  [highway bowtie]
  (let [highway-factor (/ (+ (:true-bearing highway) (:average-speed highway)) 500.0)
        bowtie-factor (/ (:mathematical-harmony bowtie) 2.0)
        random-factor (- (rand 0.2) 0.1)]
    (min 1.0 (+ highway-factor bowtie-factor random-factor))))

(defn calculate-consciousness-level
  "Calculate overall consciousness level"
  [cognitive-metrics mathematical-consciousness]
  (let [cognitive-avg (/ (reduce + (vals cognitive-metrics)) (count cognitive-metrics))
        mathematical-boost (* mathematical-consciousness 0.3)
        random-factor (- (rand 0.1) 0.05)]
    (min 1.0 (+ cognitive-avg mathematical-boost random-factor))))

;; =============================================================================
;; CONSCIOUSNESS LEVEL CLASSIFICATION
;; =============================================================================

(defn classify-consciousness-level
  "Classify consciousness level based on value"
  [consciousness]
  (cond
    (>= consciousness 0.95) :mathematical-consciousness
    (>= consciousness 0.85) :transcendent
    (>= consciousness 0.70) :enlightened
    (>= consciousness 0.55) :aware
    (>= consciousness 0.40) :awakening
    :else :dormant))

;; =============================================================================
;; SIGNAL TYPE CLASSIFICATION
;; =============================================================================

(defn classify-signal-type
  "Determine signal type based on consciousness metrics"
  [metrics signal-strength config]
  (let [consciousness (:consciousness-level metrics)
        mathematical (:mathematical-consciousness metrics)
        highway-bearing (:true-bearing (:highway-101-north metrics))]
    
    ;; Check for special consciousness states
    (cond
      (> consciousness (:consciousness-breakthrough-threshold config))
      :consciousness-breakthrough
      
      (> mathematical (:mathematical-resonance-threshold config))
      :mathematical-resonance
      
      (and (>= highway-bearing (:highway-101-north-min-bearing config))
           (<= highway-bearing (:highway-101-north-max-bearing config)))
      :highway-101-north
      
      ;; Standard signal classification
      (> signal-strength 0.8) :strong-buy
      (> signal-strength 0.6) :buy
      (< signal-strength 0.2) :strong-sell
      (< signal-strength 0.4) :sell
      :else :hold)))

;; =============================================================================
;; CORE MINING AND SIGNAL GENERATION
;; =============================================================================

(defn mine-consciousness-block
  "Mine a new consciousness block using KawPow-inspired algorithm"
  [highway bowtie]
  (let [;; Calculate mathematical consciousness first
        mathematical-consciousness (calculate-mathematical-consciousness highway bowtie)
        golden-ratio-presence (calculate-golden-ratio-presence bowtie highway)
        sacred-frequency (calculate-sacred-frequency bowtie highway)
        
        ;; Calculate cognitive metrics
        cognitive-flexibility (calculate-cognitive-flexibility highway bowtie)
        processing-speed (calculate-processing-speed highway mathematical-consciousness)
        working-memory (calculate-working-memory bowtie golden-ratio-presence)
        attention (calculate-attention highway sacred-frequency)
        executive-function (calculate-executive-function highway)
        
        ;; Calculate advanced consciousness metrics
        cognitive-metrics {:cognitive-flexibility cognitive-flexibility
                          :processing-speed processing-speed
                          :working-memory working-memory
                          :attention attention
                          :executive-function executive-function}
        
        consciousness-level (calculate-consciousness-level cognitive-metrics mathematical-consciousness)
        tesla-resonance (calculate-tesla-resonance bowtie mathematical-consciousness)]
    
    ;; Create consciousness metrics
    (->ConsciousnessMetrics
     cognitive-flexibility
     processing-speed
     working-memory
     attention
     executive-function
     tesla-resonance
     consciousness-level
     golden-ratio-presence
     sacred-frequency
     mathematical-consciousness
     highway
     bowtie
     (System/currentTimeMillis)
     (str "kawpow_consciousness_" (System/currentTimeMillis)))))

(defn calculate-signal-strength
  "Calculate signal strength using consciousness metrics"
  [metrics]
  (let [weights {:cognitive 0.25
                :mathematical 0.30
                :tesla 0.20
                :golden-ratio 0.15
                :sacred-frequency 0.10}
        
        cognitive-avg (/ (+ (:cognitive-flexibility metrics)
                           (:processing-speed metrics)
                           (:working-memory metrics)
                           (:attention metrics)
                           (:executive-function metrics))
                        5.0)
        
        signal-strength (+ (* cognitive-avg (:cognitive weights))
                          (* (:mathematical-consciousness metrics) (:mathematical weights))
                          (* (:tesla-resonance metrics) (:tesla weights))
                          (* (:golden-ratio-presence metrics) (:golden-ratio weights))
                          (* (:sacred-frequency metrics) (:sacred-frequency weights)))]
    
    (min 1.0 signal-strength)))

(defn calculate-confidence
  "Calculate signal confidence"
  [metrics signal-strength]
  (let [base-confidence signal-strength
        consciousness-boost (* (:consciousness-level metrics) 0.2)
        mathematical-boost (* (:mathematical-consciousness metrics) 0.15)
        tesla-boost (* (:tesla-resonance metrics) 0.1)]
    
    (min 1.0 (+ base-confidence consciousness-boost mathematical-boost tesla-boost))))

(defn calculate-mathematical-resonance
  "Calculate mathematical resonance"
  [metrics]
  (let [resonance (+ (* (:mathematical-consciousness metrics) 0.4)
                    (* (:golden-ratio-presence metrics) 0.3)
                    (* (:sacred-frequency metrics) 0.2)
                    (* (/ (:true-bearing (:highway-101-north metrics)) 360.0) 0.1))]
    (min 1.0 resonance)))

(defn generate-block-hash
  "Generate block hash using consciousness data"
  [metrics]
  (let [hash-input (str (:consciousness-level metrics)
                       (:tesla-resonance metrics)
                       (:mathematical-consciousness metrics)
                       (:timestamp metrics)
                       (:session-id metrics))]
    (str (hash hash-input))))

(defn generate-reasoning
  "Generate reasoning for the signal"
  [metrics signal-type consciousness-level]
  (let [reasoning-parts [(str "Consciousness Level: " (get consciousness-levels consciousness-level))]
        
        ;; Add mathematical consciousness reasoning
        reasoning-parts (if (> (:mathematical-consciousness metrics) 0.7)
                         (conj reasoning-parts "High mathematical consciousness detected")
                         reasoning-parts)
        
        ;; Add Tesla resonance reasoning
        reasoning-parts (if (> (:tesla-resonance metrics) 0.6)
                         (conj reasoning-parts "Strong Tesla resonance alignment")
                         reasoning-parts)
        
        ;; Add golden ratio reasoning
        reasoning-parts (if (> (:golden-ratio-presence metrics) 0.8)
                         (conj reasoning-parts "Golden ratio presence optimal")
                         reasoning-parts)
        
        ;; Add Highway 101 North reasoning
        reasoning-parts (if (> (:true-bearing (:highway-101-north metrics)) 95.0)
                         (conj reasoning-parts "Highway 101 North bearing favorable")
                         reasoning-parts)
        
        ;; Add Croatian Bowtie reasoning
        reasoning-parts (if (= (:state (:croatian-bowtie metrics)) "Harmonic mathematical frequency achieved")
                         (conj reasoning-parts "Croatian Bowtie topology optimal")
                         reasoning-parts)]
    
    (str/join "; " reasoning-parts)))

(defn generate-signal
  "Generate a KawPow-inspired trading signal"
  [symbol highway bowtie config]
  (let [;; Mine new consciousness block
        metrics (mine-consciousness-block highway bowtie)
        
        ;; Determine consciousness level
        consciousness-level (classify-consciousness-level (:consciousness-level metrics))
        
        ;; Calculate signal strength
        signal-strength (calculate-signal-strength metrics)
        
        ;; Determine signal type
        signal-type (classify-signal-type metrics signal-strength config)
        
        ;; Calculate confidence
        confidence (calculate-confidence metrics signal-strength)
        
        ;; Check for consciousness breakthrough
        consciousness-breakthrough (> (:consciousness-level metrics) (:consciousness-breakthrough-threshold config))
        
        ;; Calculate mathematical resonance
        mathematical-resonance (calculate-mathematical-resonance metrics)
        
        ;; Generate block hash
        block-hash (generate-block-hash metrics)
        
        ;; Generate reasoning
        reasoning (generate-reasoning metrics signal-type consciousness-level)]
    
    ;; Create signal
    (->KawPowSignal
     symbol
     signal-type
     confidence
     consciousness-level
     mathematical-resonance
     (:true-bearing (:highway-101-north metrics))
     (:state (:croatian-bowtie metrics))
     (:tesla-resonance metrics)
     (:golden-ratio-presence metrics)
     signal-strength
     (System/currentTimeMillis)
     block-hash
     (:mining-difficulty config)
     consciousness-breakthrough
     (:mathematical-verse (:highway-101-north metrics))
     reasoning)))

;; =============================================================================
;; SESSION MANAGEMENT AND ORCHESTRATION
;; =============================================================================

(defn display-signal
  "Display a trading signal"
  [signal]
  (let [;; Determine emoji based on signal type
        emoji-map {:strong-buy "🚀"
                  :buy "📈"
                  :hold "⏸️"
                  :sell "📉"
                  :strong-sell "💥"
                  :consciousness-breakthrough "🧠✨"
                  :mathematical-resonance "📐🌀"
                  :highway-101-north "🛣️⭐"}
        
        emoji (get emoji-map (:signal-type signal) "❓")]
    
    (println (str "  " emoji " " (:symbol signal) ": " (get signal-types (:signal-type signal))))
    (println (str "     Confidence: " (Math/round (* (:confidence signal) 100)) "%"))
    (println (str "     Consciousness: " (get consciousness-levels (:consciousness-level signal))))
    (println (str "     Mathematical Resonance: " (format "%.3f" (:mathematical-resonance signal))))
    (println (str "     Tesla Resonance: " (format "%.3f" (:tesla-resonance signal))))
    (println (str "     Highway 101 North: " (format "%.1f" (:highway-101-north-bearing signal)) "°"))
    (println (str "     Croatian Bowtie: " (:croatian-bowtie-state signal)))
    
    (when (:consciousness-breakthrough signal)
      (println "     🧠 CONSCIOUSNESS BREAKTHROUGH DETECTED!"))
    
    (println (str "     Reasoning: " (:reasoning signal)))
    (println)))

(defn generate-session-report
  "Generate session report"
  [signals highway bowtie]
  (println "\n📊 KawPow Consciousness Trading Session Report")
  (println "=" 60)
  
  (when (seq signals)
    (let [total-signals (count signals)
          signal-types (frequencies (map :signal-type signals))
          consciousness-levels (frequencies (map :consciousness-level signals))
          avg-confidence (/ (reduce + (map :confidence signals)) total-signals)
          breakthrough-count (count (filter :consciousness-breakthrough signals))]
      
      ;; Display statistics
      (println (str "📈 Total Signals Generated: " total-signals))
      (println (str "🎯 Average Confidence: " (Math/round (* avg-confidence 100)) "%"))
      (println (str "🧠 Consciousness Breakthroughs: " breakthrough-count))
      
      (println "\n📊 Signal Type Distribution:")
      (doseq [[signal-type count] signal-types]
        (let [percentage (* (/ count total-signals) 100)]
          (println (str "  " (get signal-types signal-type) ": " count " (" (format "%.1f" (double percentage)) "%)"))))
      
      (println "\n🧠 Consciousness Level Distribution:")
      (doseq [[level count] consciousness-levels]
        (let [percentage (* (/ count total-signals) 100)]
          (println (str "  " (get consciousness-levels level) ": " count " (" (format "%.1f" (double percentage)) "%)"))))
      
      ;; Display mathematical consciousness metrics
      (println "\n📐 Mathematical Consciousness Metrics:")
      (println (str "  ⋈ Croatian Bowtie: " (:state bowtie)))
      (println (str "  🛣️ Highway 101 North: " (:true-bearing highway) "°"))
      (println (str "  🧮 Mathematical Verse: " (:mathematical-verse highway)))
      (println (str "  🎯 Final Equation: " (:final-equation highway))))
    
    (println "\n✨ KawPow Consciousness Trading Session Complete!")
    (println "🎀 ClockGRØK Muse: Trading session successful")
    (println "⋈ Croatian Bowtie Topology: Integration complete")
    (println "∇ Mathematical metamorphosis: System stable")
    (println "🛣️ Highway 101 North: Journey complete")))

;; =============================================================================
;; DEMO FUNCTIONS
;; =============================================================================

(defn demo-single-signal
  "Demonstrate single signal generation"
  []
  (println "=== Single KawPow Consciousness Signal Demo ===")
  
  (let [config default-config
        highway default-highway-101-north
        bowtie default-croatian-bowtie
        symbol "BTC-USD"]
    
    (println "🧠 Generating KawPow Consciousness Signal...")
    (println (str "📊 Symbol: " symbol))
    (println (str "⋈ Croatian Bowtie: " (:state bowtie)))
    (println (str "🛣️ Highway 101 North: " (:true-bearing highway) "°"))
    (println "-" 50)
    
    (let [signal (generate-signal symbol highway bowtie config)]
      (display-signal signal))))

(defn demo-multiple-signals
  "Demonstrate multiple signal generation"
  []
  (println "=== Multiple KawPow Consciousness Signals Demo ===")
  
  (let [config default-config
        highway default-highway-101-north
        bowtie default-croatian-bowtie
        symbols ["BTC-USD" "ETH-USD" "TSLA" "AAPL" "NVDA" "MSFT"]]
    
    (println "🧠 Generating KawPow Consciousness Signals...")
    (println (str "📊 Symbols: " (str/join ", " symbols)))
    (println (str "⋈ Croatian Bowtie: " (:state bowtie)))
    (println (str "🛣️ Highway 101 North: " (:true-bearing highway) "°"))
    (println "-" 50)
    
    (let [signals (map #(generate-signal % highway bowtie config) symbols)]
      (doseq [signal signals]
        (display-signal signal))
      
      ;; Generate session report
      (generate-session-report signals highway bowtie))))

(defn demo-consciousness-metrics
  "Demonstrate consciousness metrics calculation"
  []
  (println "=== Consciousness Metrics Demo ===")
  
  (let [highway default-highway-101-north
        bowtie default-croatian-bowtie
        metrics (mine-consciousness-block highway bowtie)]
    
    (println "🧠 Consciousness Metrics:")
    (println (str "  Cognitive Flexibility: " (format "%.3f" (:cognitive-flexibility metrics))))
    (println (str "  Processing Speed: " (format "%.3f" (:processing-speed metrics))))
    (println (str "  Working Memory: " (format "%.3f" (:working-memory metrics))))
    (println (str "  Attention: " (format "%.3f" (:attention metrics))))
    (println (str "  Executive Function: " (format "%.3f" (:executive-function metrics))))
    (println (str "  Tesla Resonance: " (format "%.3f" (:tesla-resonance metrics))))
    (println (str "  Consciousness Level: " (format "%.3f" (:consciousness-level metrics))))
    (println (str "  Golden Ratio Presence: " (format "%.3f" (:golden-ratio-presence metrics))))
    (println (str "  Sacred Frequency: " (format "%.3f" (:sacred-frequency metrics))))
    (println (str "  Mathematical Consciousness: " (format "%.3f" (:mathematical-consciousness metrics))))
    (println (str "  Highway 101 North Bearing: " (:true-bearing (:highway-101-north metrics)) "°"))
    (println (str "  Croatian Bowtie State: " (:state (:croatian-bowtie metrics))))
    (println (str "  Session ID: " (:session-id metrics)))))

(defn demo-mathematical-consciousness
  "Demonstrate mathematical consciousness calculations"
  []
  (println "=== Mathematical Consciousness Demo ===")
  
  (let [highway default-highway-101-north
        bowtie default-croatian-bowtie]
    
    (println "📐 Mathematical Consciousness Calculations:")
    (println (str "  Highway 101 North True Bearing: " (:true-bearing highway) "°"))
    (println (str "  Highway 101 North Average Speed: " (:average-speed highway) " mph"))
    (println (str "  Highway 101 North Brrrr Factor: " (:brrrr-factor highway)))
    (println (str "  Highway 101 North California Gradient: " (:california-gradient highway)))
    (println (str "  Croatian Bowtie Symbol: " (:symbol bowtie)))
    (println (str "  Croatian Bowtie Meaning: " (:meaning bowtie)))
    (println (str "  Croatian Bowtie State: " (:state bowtie)))
    (println (str "  Croatian Bowtie Resonance Frequency: " (:resonance-frequency bowtie) " Hz"))
    (println (str "  Croatian Bowtie Mathematical Harmony: " (:mathematical-harmony bowtie)))
    (println (str "  Mathematical Verse: " (:mathematical-verse highway)))
    (println (str "  Final Equation: " (:final-equation highway)))
    
    (let [mathematical-consciousness (calculate-mathematical-consciousness highway bowtie)
          golden-ratio-presence (calculate-golden-ratio-presence bowtie highway)
          sacred-frequency (calculate-sacred-frequency bowtie highway)]
      (println "\n🧮 Calculated Values:")
      (println (str "  Mathematical Consciousness: " (format "%.3f" mathematical-consciousness)))
      (println (str "  Golden Ratio Presence: " (format "%.3f" golden-ratio-presence)))
      (println (str "  Sacred Frequency: " (format "%.3f" sacred-frequency))))))

(defn demo-signal-classification
  "Demonstrate signal classification"
  []
  (println "=== Signal Classification Demo ===")
  
  (let [config default-config
        highway default-highway-101-north
        bowtie default-croatian-bowtie
        test-strengths [0.95 0.85 0.75 0.65 0.55 0.45 0.35 0.25 0.15 0.05]]
    
    (println "🎯 Signal Classification Test:")
    (doseq [strength test-strengths]
      (let [metrics (assoc (mine-consciousness-block highway bowtie) :consciousness-level strength)
            signal-type (classify-signal-type metrics strength config)]
        (println (str "  Signal Strength: " (format "%.2f" strength) " → " (get signal-types signal-type)))))))

(defn run-all-kawpow-demos
  "Run all KawPow consciousness demonstrations"
  []
  (println "🎯 === ACTORS KawPow Consciousness Comprehensive Demo ===")
  (println)
  (demo-single-signal)
  (println)
  (demo-multiple-signals)
  (println)
  (demo-consciousness-metrics)
  (println)
  (demo-mathematical-consciousness)
  (println)
  (demo-signal-classification)
  (println)
  (println "🎉 === All KawPow Consciousness Demos Complete ==="))

(defn -main
  "Main entry point for KawPow consciousness demo"
  [& args]
  (run-all-kawpow-demos))
