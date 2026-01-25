#!/usr/bin/env python3
"""
Database Manager for ACTORS
DuckDB connection and query management
"""

import duckdb
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

from .database_config import (
    DB_CONFIG,
    ALL_SCHEMAS,
    INDEXES,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """DuckDB database manager for ACTORS financial trading system"""
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_path: Path to DuckDB file. If None, uses default from config.
        """
        self.db_path = database_path or DB_CONFIG["database"]
        self.connection = None
        logger.info(f"🗄️  Database Manager initialized with path: {self.db_path}")
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """
        Connect to DuckDB database
        
        Returns:
            DuckDB connection object
        """
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path, read_only=False)
            logger.info(f"✅ Connected to database: {self.db_path}")
        return self.connection
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("🔌 Disconnected from database")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        
        Yields:
            DuckDB connection
        """
        conn = self.connect()
        try:
            yield conn
        finally:
            pass  # Keep connection alive for reuse
    
    def initialize_schema(self):
        """Create all database tables and indexes"""
        with self.get_connection() as conn:
            # Create tables
            for schema in ALL_SCHEMAS:
                conn.execute(schema)
                logger.info(f"✅ Created/verified table schema")
            
            # Create indexes
            for index in INDEXES:
                conn.execute(index)
                logger.info(f"✅ Created/verified index")
            
            logger.info("🏗️  Database schema initialized successfully")
    
    def insert_market_data(self, data: Dict[str, Any]) -> int:
        """
        Insert market data record
        
        Args:
            data: Market data dictionary with keys: symbol, timestamp, open, high, low, close, volume, source
            
        Returns:
            ID of inserted record
            
        Raises:
            ValueError: If required fields are missing
            Exception: If database insertion fails
        """
        # Validate required fields
        required_fields = ['symbol', 'timestamp']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        try:
            with self.get_connection() as conn:
                result = conn.execute("""
                    INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                """, [
                    data['symbol'],
                    data['timestamp'],
                    data.get('open'),
                    data.get('high'),
                    data.get('low'),
                    data.get('close'),
                    data.get('volume'),
                    data.get('source', 'unknown')
                ]).fetchone()
                
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to insert market data for {data.get('symbol', 'unknown')}: {e}")
            raise
    
    def insert_trade(self, trade: Dict[str, Any]) -> int:
        """
        Insert trade record
        
        Args:
            trade: Trade dictionary with required keys: order_id, portfolio_id, symbol, side, quantity, price, order_type, status
            
        Returns:
            ID of inserted record
            
        Raises:
            ValueError: If required fields are missing
            Exception: If database insertion fails
        """
        # Validate required fields
        required_fields = ['order_id', 'portfolio_id', 'symbol', 'side', 'quantity', 'price', 'order_type', 'status']
        for field in required_fields:
            if field not in trade:
                raise ValueError(f"Missing required field: {field}")
        
        try:
            with self.get_connection() as conn:
                result = conn.execute("""
                    INSERT INTO trade_history (order_id, portfolio_id, symbol, side, quantity, price, order_type, status, executed_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                """, [
                    trade['order_id'],
                    trade['portfolio_id'],
                    trade['symbol'],
                    trade['side'],
                    trade['quantity'],
                    trade['price'],
                    trade['order_type'],
                    trade['status'],
                    trade.get('executed_at'),
                    None  # metadata as JSON
                ]).fetchone()
                
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to insert trade {trade.get('order_id', 'unknown')}: {e}")
            raise
    
    def insert_portfolio_position(self, position: Dict[str, Any]) -> int:
        """
        Insert portfolio position
        
        Args:
            position: Position dictionary with keys: portfolio_id, symbol, quantity, entry_price, current_price, position_type, opened_at
            
        Returns:
            ID of inserted record
        """
        with self.get_connection() as conn:
            result = conn.execute("""
                INSERT INTO portfolio_positions (portfolio_id, symbol, quantity, entry_price, current_price, position_type, opened_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, [
                position['portfolio_id'],
                position['symbol'],
                position['quantity'],
                position['entry_price'],
                position.get('current_price'),
                position['position_type'],
                position['opened_at'],
                None  # metadata as JSON
            ]).fetchone()
            
            return result[0] if result else None
    
    def insert_agent_metric(self, metric: Dict[str, Any]) -> int:
        """
        Insert agent performance metric
        
        Args:
            metric: Metric dictionary with keys: agent_id, agent_type, metric_name, metric_value, dimension, timestamp
            
        Returns:
            ID of inserted record
        """
        with self.get_connection() as conn:
            result = conn.execute("""
                INSERT INTO agent_metrics (agent_id, agent_type, metric_name, metric_value, dimension, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, [
                metric['agent_id'],
                metric['agent_type'],
                metric['metric_name'],
                metric['metric_value'],
                metric.get('dimension'),
                metric['timestamp'],
                None  # metadata as JSON
            ]).fetchone()
            
            return result[0] if result else None
    
    def get_market_data(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get market data for a symbol
        
        Args:
            symbol: Stock/asset symbol
            limit: Maximum number of records to return
            
        Returns:
            List of market data records
        """
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT * FROM market_data
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, [symbol, limit]).fetchall()
            
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
    
    def get_portfolio_positions(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """
        Get all positions for a portfolio
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            List of position records
        """
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT * FROM portfolio_positions
                WHERE portfolio_id = ?
                ORDER BY updated_at DESC
            """, [portfolio_id]).fetchall()
            
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
    
    def get_trade_history(self, portfolio_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get trade history for a portfolio
        
        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of records to return
            
        Returns:
            List of trade records
        """
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT * FROM trade_history
                WHERE portfolio_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, [portfolio_id, limit]).fetchall()
            
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
    
    def get_agent_metrics(self, agent_id: str, metric_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get agent performance metrics
        
        Args:
            agent_id: Agent identifier
            metric_name: Optional specific metric name to filter
            limit: Maximum number of records to return
            
        Returns:
            List of metric records
        """
        with self.get_connection() as conn:
            if metric_name:
                result = conn.execute("""
                    SELECT * FROM agent_metrics
                    WHERE agent_id = ? AND metric_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, [agent_id, metric_name, limit]).fetchall()
            else:
                result = conn.execute("""
                    SELECT * FROM agent_metrics
                    WHERE agent_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, [agent_id, limit]).fetchall()
            
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
    
    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict[str, Any]]:
        """
        Execute custom SQL query
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.get_connection() as conn:
            if params:
                result = conn.execute(query, params).fetchall()
            else:
                result = conn.execute(query).fetchall()
            
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with table counts and database info
        """
        with self.get_connection() as conn:
            stats = {}
            
            # Get table counts - using validated table names from schema
            # Table names are hardcoded from schema to prevent SQL injection
            validated_tables = ['market_data', 'portfolio_positions', 'trade_history', 'agent_metrics', 'risk_metrics']
            
            for table in validated_tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[f"{table}_count"] = count
            
            # Get database size
            stats['database_path'] = self.db_path
            stats['connection_active'] = self.connection is not None
            
            return stats


# Singleton instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize_schema()
    return _db_manager
