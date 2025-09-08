(defproject actors-clojure "0.1.0-SNAPSHOT"
  :description "ACTORS Clojure Functional System for Financial Intelligence"
  :url "https://github.com/sosloan/Actors"
  :license {:name "MIT License"
            :url "https://opensource.org/licenses/MIT"}
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [org.clojure/core.async "1.6.681"]
                 [org.clojure/data.json "2.4.0"]
                 [org.clojure/math.numeric-tower "0.0.5"]
                 [clj-time "0.15.2"]
                 [compojure "1.7.0"]
                 [ring/ring-core "1.10.0"]
                 [ring/ring-jetty-adapter "1.10.0"]
                 [ring/ring-json "0.5.1"]
                 [cheshire "5.11.0"]
                 [clj-http "3.12.3"]
                 [environ "1.2.0"]
                 [mount "0.1.16"]]
  
  :plugins [[lein-environ "1.2.0"]
            [lein-cloverage "1.2.4"]
            [lein-kibit "0.1.8"]
            [lein-bikeshed "0.5.2"]]
  
  :main ^:skip-aot actors.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all
                       :jvm-opts ["-Dclojure.compiler.direct-linking=true"]}
             :dev {:dependencies [[org.clojure/test.check "1.1.1"]
                                  [midje "1.10.9"]
                                  [eftest "0.6.0"]]
                   :plugins [[lein-midje "3.2.2"]
                             [lein-eftest "0.6.0"]]}
             :test {:dependencies [[org.clojure/test.check "1.1.1"]
                                   [midje "1.10.9"]
                                   [eftest "0.6.0"]]}}
  
  :test-paths ["test"]
  :resource-paths ["resources"]
  
  :jvm-opts ["-Xmx2g" "-server"]
  
  :aliases {"test" ["eftest"]
            "test-all" ["do" ["clean"] ["test"] ["midje"]]
            "lint" ["do" ["kibit"] ["bikeshed"]]
            "coverage" ["cloverage" "--runner" ":eftest"]
            "benchmark" ["run" "-m" "actors.benchmark"]}
  
  :repl-options {:init-ns actors.core
                 :timeout 120000}
  
  :global-vars {*warn-on-reflection* true
                *assert* true}
  
  :clean-targets [:target-path
                  "pom.xml"
                  "checkouts"]
  
  :deploy-repositories [["releases" :clojars]
                        ["snapshots" :clojars]])
