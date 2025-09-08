(ns actors.simple-test
  "Simple test to verify basic Clojure functionality"
  (:require [clojure.core.async :as async]))

(defn hello-world
  "Simple hello world function"
  []
  (println "Hello from ACTORS Clojure System!"))

(defn test-basic-functionality
  "Test basic Clojure functionality"
  []
  (println "Testing basic functionality...")
  (println "1 + 1 =" (+ 1 1))
  (println "Vector creation:" [1 2 3 4 5])
  (println "Map creation:" {:name "ACTORS" :type "Clojure"})
  (println "Channel creation:" (async/chan))
  (println "Basic test completed successfully!"))

(defn -main
  "Main entry point for simple test"
  [& args]
  (hello-world)
  (test-basic-functionality))
