#!/usr/bin/env python3
"""
Database Configuration for ACTORS
DuckDB setup for financial trading data
"""

import os
from pathlib import Path

# Database configuration
DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "actors.duckdb"

# Ensure data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# Database settings
DB_CONFIG = {
    "database": str(DB_PATH),
    "read_only": False,
    "access_mode": "automatic",
}

# Table schemas
MARKET_DATA_SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_market_data START 1;
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_market_data'),
    symbol VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

PORTFOLIO_POSITIONS_SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_portfolio_positions START 1;
CREATE TABLE IF NOT EXISTS portfolio_positions (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_portfolio_positions'),
    portfolio_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    quantity DOUBLE NOT NULL,
    entry_price DOUBLE NOT NULL,
    current_price DOUBLE,
    position_type VARCHAR NOT NULL,
    opened_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
"""

TRADE_HISTORY_SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_trade_history START 1;
CREATE TABLE IF NOT EXISTS trade_history (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_trade_history'),
    order_id VARCHAR UNIQUE NOT NULL,
    portfolio_id VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    side VARCHAR NOT NULL,
    quantity DOUBLE NOT NULL,
    price DOUBLE NOT NULL,
    order_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
"""

AGENT_METRICS_SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_agent_metrics START 1;
CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_agent_metrics'),
    agent_id VARCHAR NOT NULL,
    agent_type VARCHAR NOT NULL,
    metric_name VARCHAR NOT NULL,
    metric_value DOUBLE NOT NULL,
    dimension VARCHAR,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
"""

RISK_METRICS_SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_risk_metrics START 1;
CREATE TABLE IF NOT EXISTS risk_metrics (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_risk_metrics'),
    portfolio_id VARCHAR NOT NULL,
    metric_type VARCHAR NOT NULL,
    metric_value DOUBLE NOT NULL,
    confidence_level DOUBLE,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);
"""

# All schemas to create
ALL_SCHEMAS = [
    MARKET_DATA_SCHEMA,
    PORTFOLIO_POSITIONS_SCHEMA,
    TRADE_HISTORY_SCHEMA,
    AGENT_METRICS_SCHEMA,
    RISK_METRICS_SCHEMA,
]

# Index definitions for performance
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_portfolio_positions_portfolio_id ON portfolio_positions(portfolio_id);",
    "CREATE INDEX IF NOT EXISTS idx_trade_history_portfolio_id ON trade_history(portfolio_id);",
    "CREATE INDEX IF NOT EXISTS idx_trade_history_symbol ON trade_history(symbol);",
    "CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_id ON agent_metrics(agent_id);",
    "CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_risk_metrics_portfolio_id ON risk_metrics(portfolio_id);",
]
