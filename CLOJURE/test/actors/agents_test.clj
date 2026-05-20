(ns actors.agents-test
  (:require [clojure.test :refer :all]
            [actors.agents :refer :all]))

(deftest test-create-market-data-agent
  (testing "Market data agent creation"
    (let [agent (create-market-data-agent "AAPL")]
      (is (= :market-data (:type agent)))
      (is (= "AAPL" (:symbol agent)))
      (is (contains? agent :id))
      (is (= :idle (:status agent))))))

(deftest test-create-trading-agent
  (testing "Trading agent creation"
    (let [agent (create-trading-agent "TSLA")]
      (is (= :trading (:type agent)))
      (is (= "TSLA" (:symbol agent)))
      (is (contains? agent :id))
      (is (= :idle (:status agent))))))

(deftest test-create-risk-agent
  (testing "Risk management agent creation"
    (let [agent (create-risk-agent "portfolio-1")]
      (is (= :risk-management (:type agent)))
      (is (= "portfolio-1" (:symbol agent)))
      (is (contains? agent :id)))))

(deftest test-process-agent-message
  (testing "Processing a message updates the agent"
    (let [agent (create-trading-agent "AAPL")
          message {:type :signal :data "buy"}
          updated (process-agent-message agent message)]
      (is (= message (:last-message updated)))
      (is (contains? updated :last-processed)))))

(deftest test-get-agent-status
  (testing "Getting status returns agent status keyword"
    (let [agent (create-market-data-agent "GOOGL")]
      (is (= :idle (get-agent-status agent))))))

(deftest test-update-agent-config
  (testing "Updating agent configuration"
    (let [agent (create-trading-agent "MSFT")
          config {:strategy :ma :risk-level :low}
          updated (update-agent-config agent config)]
      (is (= config (:config updated))))))
