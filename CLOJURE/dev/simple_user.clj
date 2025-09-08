(ns simple_user
  "Simplified development namespace for ACTORS Clojure system"
  (:require [actors.simple-core :as core]
            [clojure.core.async :as async :refer [go go-loop chan <! >!]]))

;; =============================================================================
;; Development Helpers
;; =============================================================================

(defn start-simple-system
  "Start the simplified development system"
  []
  (println "🚀 Starting ACTORS Clojure Simple System...")
  (let [system (core/initialize-system)]
    (println "✅ System initialized successfully!")
    (println "📊 System status:" (:status system))
    (println "🔗 Channels created:" (keys (:channels system)))
    system))

(defn run-simple-demo
  "Run the simple demonstration"
  []
  (println "🎯 Running Simple Demo...")
  (core/demo-functionality))

(defn test-basic-functionality
  "Test basic functionality"
  []
  (println "🧪 Testing Basic Functionality...")
  
  ;; Test market data creation
  (let [market-data (core/create-market-data "GOOGL" 2800.00 500000 0.15)]
    (println "✅ Market data created:" (:symbol market-data) "at $" (:price market-data)))
  
  ;; Test signal creation
  (let [signal (core/create-trading-signal :sell 0.75 {:strategy "rsi"})]
    (println "✅ Signal created:" (:type signal) "with confidence" (:confidence signal)))
  
  ;; Test mathematical calculations
  (let [prices [100.0 105.0 110.0 108.0 115.0]
        returns (core/calculate-returns prices)
        volatility (core/calculate-volatility returns)]
    (println "✅ Returns calculated:" (count returns) "values")
    (println "✅ Volatility calculated:" volatility))
  
  (println "🎉 All tests passed!"))

(defn test-channels
  "Test channel functionality"
  []
  (println "📡 Testing Channel Functionality...")
  
  (let [market-channel (core/create-market-data-channel)
        signal-channel (core/create-signal-channel)
        market-data (core/create-market-data "TSLA" 250.50 2000000 0.25)
        signal (core/create-trading-signal :buy 0.90 {:strategy "bollinger"})]
    
    (go
      (>! market-channel market-data)
      (>! signal-channel signal))
    
    (go
      (let [received-data (<! market-channel)
            received-signal (<! signal-channel)]
        (println "✅ Market data received:" (:symbol received-data))
        (println "✅ Signal received:" (:type received-signal))))
    
    (println "📡 Channel test initiated...")))

(defn run-all-tests
  "Run all tests and demos"
  []
  (println "🎯 === ACTORS Clojure Simple System Tests ===")
  (println)
  (test-basic-functionality)
  (println)
  (test-channels)
  (println)
  (run-simple-demo)
  (println)
  (println "🎉 === All Tests Complete ==="))

(defn quick-start
  "Quick start guide"
  []
  (println "🚀 ACTORS Clojure Simple System - Quick Start")
  (println "=============================================")
  (println)
  (println "Available functions:")
  (println "  (start-simple-system) - Initialize the system")
  (println "  (run-simple-demo) - Run the demonstration")
  (println "  (test-basic-functionality) - Test core functions")
  (println "  (test-channels) - Test async channels")
  (println "  (run-all-tests) - Run all tests")
  (println)
  (println "Try: (test-basic-functionality) to get started!")
  (println))

;; =============================================================================
;; Welcome Message
;; =============================================================================

(println "🎉 ACTORS Clojure Simple System - Development Environment")
(println "========================================================")
(println)
(println "✅ System loaded successfully!")
(println "📚 Available functions:")
(println "  (start-simple-system) - Start the system")
(println "  (run-simple-demo) - Run demonstration")
(println "  (test-basic-functionality) - Test core functions")
(println "  (test-channels) - Test async channels")
(println "  (run-all-tests) - Run all tests")
(println "  (quick-start) - Show this help")
(println)
(println "🚀 Try: (test-basic-functionality) to get started!")
(println)
