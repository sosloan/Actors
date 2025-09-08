(ns actors.agents
  "Agent system for financial intelligence"
  (:require [actors.core :as core]))

(defn create-market-data-agent
  "Create market data agent"
  [symbol]
  (core/create-agent :market-data symbol))

(defn create-trading-agent
  "Create trading agent"
  [symbol]
  (core/create-agent :trading symbol))

(defn create-risk-agent
  "Create risk management agent"
  [portfolio-id]
  (core/create-agent :risk-management portfolio-id))

(defn process-agent-message
  "Process message for agent"
  [agent message]
  (assoc agent :last-message message :last-processed (java.time.Instant/now)))

(defn get-agent-status
  "Get agent status"
  [agent]
  (:status agent))

(defn update-agent-config
  "Update agent configuration"
  [agent config]
  (assoc agent :config config))
