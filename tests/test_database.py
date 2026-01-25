#!/usr/bin/env python3
"""
Tests for DuckDB database setup
"""

import pytest
import sys
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import DatabaseManager
from core.database_config import DB_CONFIG


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=True) as f:
        db_path = f.name
    
    # Delete the empty file that was created
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = DatabaseManager(db_path)
    db.initialize_schema()
    
    yield db
    
    # Cleanup
    db.disconnect()
    if os.path.exists(db_path):
        os.remove(db_path)
    # Also clean up WAL file if it exists
    wal_path = db_path + '.wal'
    if os.path.exists(wal_path):
        os.remove(wal_path)


class TestDatabaseSetup:
    """Test database initialization and schema"""
    
    def test_database_creation(self, temp_db):
        """Test that database is created successfully"""
        assert temp_db is not None
        assert temp_db.connection is not None
    
    def test_schema_initialization(self, temp_db):
        """Test that all tables are created"""
        stats = temp_db.get_database_stats()
        
        # Check that all expected tables exist
        assert 'market_data_count' in stats
        assert 'portfolio_positions_count' in stats
        assert 'trade_history_count' in stats
        assert 'agent_metrics_count' in stats
        assert 'risk_metrics_count' in stats
    
    def test_database_stats(self, temp_db):
        """Test database statistics retrieval"""
        stats = temp_db.get_database_stats()
        
        assert isinstance(stats, dict)
        assert 'database_path' in stats
        assert stats['connection_active'] == True


class TestMarketData:
    """Test market data operations"""
    
    def test_insert_market_data(self, temp_db):
        """Test inserting market data"""
        data = {
            'symbol': 'AAPL',
            'timestamp': datetime.now(),
            'open': 150.0,
            'high': 155.0,
            'low': 148.0,
            'close': 152.0,
            'volume': 1000000,
            'source': 'test'
        }
        
        record_id = temp_db.insert_market_data(data)
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_get_market_data(self, temp_db):
        """Test retrieving market data"""
        # Insert test data
        for i in range(5):
            data = {
                'symbol': 'AAPL',
                'timestamp': datetime.now() - timedelta(hours=i),
                'open': 150.0 + i,
                'high': 155.0 + i,
                'low': 148.0 + i,
                'close': 152.0 + i,
                'volume': 1000000,
                'source': 'test'
            }
            temp_db.insert_market_data(data)
        
        # Retrieve data
        results = temp_db.get_market_data('AAPL', limit=10)
        
        assert len(results) == 5
        assert all(r['symbol'] == 'AAPL' for r in results)
    
    def test_market_data_ordering(self, temp_db):
        """Test that market data is ordered by timestamp DESC"""
        # Insert data with different timestamps
        timestamps = []
        for i in range(3):
            ts = datetime.now() - timedelta(hours=i)
            timestamps.append(ts)
            data = {
                'symbol': 'MSFT',
                'timestamp': ts,
                'open': 200.0,
                'high': 205.0,
                'low': 198.0,
                'close': 202.0,
                'volume': 500000,
                'source': 'test'
            }
            temp_db.insert_market_data(data)
        
        results = temp_db.get_market_data('MSFT')
        
        # Check that results are in descending order by timestamp
        assert len(results) == 3
        # Most recent should be first
        assert results[0]['timestamp'] >= results[1]['timestamp']
        assert results[1]['timestamp'] >= results[2]['timestamp']


class TestTradeHistory:
    """Test trade history operations"""
    
    def test_insert_trade(self, temp_db):
        """Test inserting a trade"""
        trade = {
            'order_id': 'test_order_001',
            'portfolio_id': 'test_portfolio',
            'symbol': 'GOOGL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.0,
            'order_type': 'market',
            'status': 'executed',
            'executed_at': datetime.now()
        }
        
        record_id = temp_db.insert_trade(trade)
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_get_trade_history(self, temp_db):
        """Test retrieving trade history"""
        portfolio_id = 'test_portfolio'
        
        # Insert multiple trades
        for i in range(5):
            trade = {
                'order_id': f'order_{i:04d}',
                'portfolio_id': portfolio_id,
                'symbol': 'TSLA',
                'side': 'buy' if i % 2 == 0 else 'sell',
                'quantity': 10 * (i + 1),
                'price': 200.0 + i * 5,
                'order_type': 'limit',
                'status': 'executed',
                'executed_at': datetime.now()
            }
            temp_db.insert_trade(trade)
        
        # Retrieve trades
        results = temp_db.get_trade_history(portfolio_id)
        
        assert len(results) == 5
        assert all(r['portfolio_id'] == portfolio_id for r in results)
    
    def test_trade_unique_order_id(self, temp_db):
        """Test that order_id is unique"""
        trade1 = {
            'order_id': 'duplicate_order',
            'portfolio_id': 'test_portfolio',
            'symbol': 'AMZN',
            'side': 'buy',
            'quantity': 50,
            'price': 100.0,
            'order_type': 'market',
            'status': 'executed',
            'executed_at': datetime.now()
        }
        
        # First insert should succeed
        record_id = temp_db.insert_trade(trade1)
        assert record_id is not None
        
        # Second insert with same order_id should fail
        with pytest.raises(Exception):
            temp_db.insert_trade(trade1)


class TestPortfolioPositions:
    """Test portfolio position operations"""
    
    def test_insert_position(self, temp_db):
        """Test inserting a portfolio position"""
        position = {
            'portfolio_id': 'test_portfolio',
            'symbol': 'AAPL',
            'quantity': 100,
            'entry_price': 150.0,
            'current_price': 155.0,
            'position_type': 'long',
            'opened_at': datetime.now()
        }
        
        record_id = temp_db.insert_portfolio_position(position)
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_get_portfolio_positions(self, temp_db):
        """Test retrieving portfolio positions"""
        portfolio_id = 'test_portfolio'
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        # Insert positions
        for symbol in symbols:
            position = {
                'portfolio_id': portfolio_id,
                'symbol': symbol,
                'quantity': 100,
                'entry_price': 150.0,
                'current_price': 155.0,
                'position_type': 'long',
                'opened_at': datetime.now()
            }
            temp_db.insert_portfolio_position(position)
        
        # Retrieve positions
        results = temp_db.get_portfolio_positions(portfolio_id)
        
        assert len(results) == 3
        assert all(r['portfolio_id'] == portfolio_id for r in results)
        assert set(r['symbol'] for r in results) == set(symbols)


class TestAgentMetrics:
    """Test agent metrics operations"""
    
    def test_insert_agent_metric(self, temp_db):
        """Test inserting agent metrics"""
        metric = {
            'agent_id': 'test_agent_001',
            'agent_type': 'market_data',
            'metric_name': 'accuracy',
            'metric_value': 0.95,
            'dimension': 'SPEED',
            'timestamp': datetime.now()
        }
        
        record_id = temp_db.insert_agent_metric(metric)
        assert record_id is not None
        assert isinstance(record_id, int)
    
    def test_get_agent_metrics(self, temp_db):
        """Test retrieving agent metrics"""
        agent_id = 'test_agent_001'
        
        # Insert multiple metrics
        metrics = ['accuracy', 'latency', 'throughput']
        for metric_name in metrics:
            metric = {
                'agent_id': agent_id,
                'agent_type': 'execution',
                'metric_name': metric_name,
                'metric_value': 0.9,
                'dimension': 'SPEED',
                'timestamp': datetime.now()
            }
            temp_db.insert_agent_metric(metric)
        
        # Retrieve all metrics
        results = temp_db.get_agent_metrics(agent_id)
        assert len(results) == 3
        
        # Retrieve specific metric
        results = temp_db.get_agent_metrics(agent_id, metric_name='accuracy')
        assert len(results) == 1
        assert results[0]['metric_name'] == 'accuracy'
    
    def test_agent_metrics_by_dimension(self, temp_db):
        """Test filtering agent metrics by dimension"""
        agent_id = 'test_agent_002'
        dimensions = ['SPEED', 'LOYALTY', 'PASSION']
        
        for dimension in dimensions:
            metric = {
                'agent_id': agent_id,
                'agent_type': 'risk',
                'metric_name': 'performance',
                'metric_value': 0.85,
                'dimension': dimension,
                'timestamp': datetime.now()
            }
            temp_db.insert_agent_metric(metric)
        
        results = temp_db.get_agent_metrics(agent_id)
        assert len(results) == 3
        assert set(r['dimension'] for r in results) == set(dimensions)


class TestCustomQueries:
    """Test custom query execution"""
    
    def test_execute_custom_query(self, temp_db):
        """Test executing custom SQL queries"""
        # Insert test data
        for i in range(5):
            data = {
                'symbol': 'AAPL',
                'timestamp': datetime.now(),
                'open': 150.0 + i,
                'high': 155.0,
                'low': 148.0,
                'close': 152.0,
                'volume': 1000000,
                'source': 'test'
            }
            temp_db.insert_market_data(data)
        
        # Custom query
        query = "SELECT symbol, COUNT(*) as count FROM market_data GROUP BY symbol"
        results = temp_db.execute_query(query)
        
        assert len(results) > 0
        assert 'symbol' in results[0]
        assert 'count' in results[0]
    
    def test_parametrized_query(self, temp_db):
        """Test parametrized queries"""
        # Insert test data
        data = {
            'symbol': 'TSLA',
            'timestamp': datetime.now(),
            'open': 200.0,
            'high': 205.0,
            'low': 198.0,
            'close': 202.0,
            'volume': 500000,
            'source': 'test'
        }
        temp_db.insert_market_data(data)
        
        # Parametrized query
        query = "SELECT * FROM market_data WHERE symbol = ? AND volume > ?"
        results = temp_db.execute_query(query, ['TSLA', 400000])
        
        assert len(results) == 1
        assert results[0]['symbol'] == 'TSLA'


class TestDatabasePerformance:
    """Test database performance with larger datasets"""
    
    def test_bulk_insert_performance(self, temp_db):
        """Test inserting multiple records"""
        import time
        
        start_time = time.time()
        
        # Insert 100 records
        for i in range(100):
            data = {
                'symbol': f'SYM{i % 10}',
                'timestamp': datetime.now() - timedelta(minutes=i),
                'open': 100.0 + i,
                'high': 105.0 + i,
                'low': 95.0 + i,
                'close': 100.0 + i,
                'volume': 1000000 + i * 1000,
                'source': 'performance_test'
            }
            temp_db.insert_market_data(data)
        
        elapsed_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 5 seconds)
        assert elapsed_time < 5.0
        
        # Verify all records inserted
        stats = temp_db.get_database_stats()
        assert stats['market_data_count'] == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
