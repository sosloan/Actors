#!/usr/bin/env python3
"""
Tests for DuckDB database setup
Comprehensive tests for the RTS Database Persistence Layer

Tests all four storage tiers:
- L0: Hot State Buffer (In-Memory Columnar)
- L1: Rollback Buffer (Ring Buffer with LZ4)
- L2: Analytics Store (DuckDB/Parquet)
- L3: Global Synchronizer (Redis)
"""

import pytest
import sys
import os
import struct
import tempfile
import zlib
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from unittest.mock import Mock, patch

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
from database import (
    HotStateBuffer,
    RollbackBuffer,
    AnalyticsStore,
    GlobalSynchronizer,
    DatabaseComponent,
    DatabaseConfig,
    L0Config,
    L1Config,
    L2Config,
    L3Config,
)


class TestL0HotStateBuffer:
    """Test L0: Hot State Buffer - In-Memory Columnar Storage"""
    
    def test_initialization(self):
        """Test hot state buffer initialization"""
        config = L0Config(max_entities=1000, use_mmap=False)
        buffer = HotStateBuffer(config)
        
        assert buffer.entity_count == 0
        assert buffer.tick_id == 0
        assert len(buffer.arrays) == 0
    
    def test_register_array(self):
        """Test columnar array registration"""
        buffer = HotStateBuffer(L0Config(use_mmap=False))
        
        buffer.register_array("x", np.dtype('float32'))
        buffer.register_array("y", np.dtype('float32'))
        
        assert "x" in buffer.arrays
        assert "y" in buffer.arrays
        assert buffer.arrays["x"].dtype == np.dtype('float32')
    
    def test_add_entity(self):
        """Test adding entities"""
        buffer = HotStateBuffer(L0Config(use_mmap=False))
        
        # Add entities
        for i in range(100):
            entity_id = buffer.add_entity(
                x=float(i),
                y=float(i * 2),
                health=100.0
            )
            assert entity_id == i
        
        assert buffer.entity_count == 100
    
    def test_get_set_attribute(self):
        """Test getting and setting entity attributes"""
        buffer = HotStateBuffer(L0Config(use_mmap=False))
        
        entity_id = buffer.add_entity(x=10.0, y=20.0, health=100.0)
        
        # Get attributes
        assert buffer.get_attribute(entity_id, "x") == 10.0
        assert buffer.get_attribute(entity_id, "y") == 20.0
        
        # Set attributes
        buffer.set_attribute(entity_id, "x", 15.0)
        assert buffer.get_attribute(entity_id, "x") == 15.0
    
    def test_get_array(self):
        """Test getting full columnar arrays for SIMD"""
        buffer = HotStateBuffer(L0Config(use_mmap=False))
        
        for i in range(10):
            buffer.add_entity(x=float(i), y=float(i * 2))
        
        x_array = buffer.get_array("x")
        y_array = buffer.get_array("y")
        
        assert len(x_array) == 10
        assert len(y_array) == 10
        assert np.allclose(x_array, np.arange(10, dtype=np.float32))
    
    def test_snapshot_and_restore(self):
        """Test snapshot creation and restoration"""
        buffer = HotStateBuffer(L0Config(use_mmap=False, enable_crc64=True))
        
        # Add entities
        for i in range(50):
            buffer.add_entity(x=float(i), y=float(i * 2), health=100.0)
        
        # Create snapshot
        tick_id, snapshot_data = buffer.snapshot()
        
        assert tick_id == 0
        assert len(snapshot_data) > 0
        
        # Modify state
        buffer.set_attribute(0, "x", 999.0)
        buffer.tick()
        
        # Restore snapshot
        buffer.restore(snapshot_data)
        
        # Verify restoration
        assert buffer.get_attribute(0, "x") == 0.0
        assert buffer.tick_id == 0
        assert buffer.entity_count == 50

    def test_snapshot_checksum_matches_serialized_payload(self):
        """Test snapshots include a checksum for anti-cheat verification"""
        buffer = HotStateBuffer(L0Config(use_mmap=False, enable_crc64=True))
        buffer.add_entity(x=10.0, y=20.0, health=100.0)

        _, snapshot_data = buffer.snapshot()

        stored_checksum = struct.unpack('I', snapshot_data[:4])[0]
        payload = snapshot_data[4:]

        assert stored_checksum == zlib.crc32(payload) & 0xffffffff

    def test_restore_rejects_corrupted_snapshot_checksum(self):
        """Test corrupted snapshots fail checksum validation"""
        buffer = HotStateBuffer(L0Config(use_mmap=False, enable_crc64=True))
        buffer.add_entity(x=10.0, y=20.0, health=100.0)

        _, snapshot_data = buffer.snapshot()
        corrupted_snapshot = bytearray(snapshot_data)
        corrupted_snapshot[-1] ^= 0x01

        with pytest.raises(ValueError, match="snapshot corrupted"):
            buffer.restore(bytes(corrupted_snapshot))
    
    def test_tick_advancement(self):
        """Test tick advancement"""
        buffer = HotStateBuffer(L0Config(use_mmap=False))
        
        assert buffer.tick_id == 0
        buffer.tick()
        assert buffer.tick_id == 1
        buffer.tick()
        assert buffer.tick_id == 2
    
    def test_clear(self):
        """Test clearing buffer"""
        buffer = HotStateBuffer(L0Config(use_mmap=False))
        
        buffer.add_entity(x=1.0, y=2.0)
        buffer.add_entity(x=3.0, y=4.0)
        buffer.tick()
        
        buffer.clear()
        
        assert buffer.entity_count == 0
        assert buffer.tick_id == 0


class TestL1RollbackBuffer:
    """Test L1: Rollback Buffer - Ring Buffer with LZ4"""
    
    def test_initialization(self):
        """Test rollback buffer initialization"""
        config = L1Config(tick_buffer_size=10, compression_enabled=False)
        buffer = RollbackBuffer(config)
        
        assert len(buffer.snapshots) == 0
        assert buffer.current_tick == 0
    
    def test_store_snapshot(self):
        """Test storing snapshots"""
        buffer = RollbackBuffer(L1Config(compression_enabled=False))
        
        # Store snapshots
        for i in range(10):
            snapshot_data = f"snapshot_{i}".encode()
            result = buffer.store_snapshot(i, snapshot_data)
            assert result is True
        
        assert len(buffer.snapshots) == 10
        assert buffer.current_tick == 9
    
    def test_get_snapshot(self):
        """Test retrieving snapshots"""
        buffer = RollbackBuffer(L1Config(compression_enabled=False))
        
        # Store snapshot
        original_data = b"test_snapshot_data"
        buffer.store_snapshot(5, original_data)
        
        # Retrieve snapshot
        retrieved_data = buffer.get_snapshot(5)
        assert retrieved_data == original_data
    
    def test_ring_buffer_overflow(self):
        """Test ring buffer overflow behavior"""
        buffer = RollbackBuffer(L1Config(tick_buffer_size=5, compression_enabled=False))
        
        # Store more snapshots than buffer size
        for i in range(10):
            buffer.store_snapshot(i, f"snapshot_{i}".encode())
        
        # Should only keep last 5
        assert len(buffer.snapshots) == 5
        assert buffer.snapshots[0].tick_id == 5
        assert buffer.snapshots[-1].tick_id == 9
    
    def test_rollback_to(self):
        """Test rollback functionality"""
        buffer = RollbackBuffer(L1Config(compression_enabled=False))
        
        # Store snapshots
        for i in range(10):
            buffer.store_snapshot(i, f"snapshot_{i}".encode())
        
        # Rollback to tick 5
        data = buffer.rollback_to(5)
        assert data == b"snapshot_5"
    
    def test_get_available_ticks(self):
        """Test getting available tick IDs"""
        buffer = RollbackBuffer(L1Config(compression_enabled=False))
        
        for i in [0, 5, 10, 15]:
            buffer.store_snapshot(i, b"data")
        
        ticks = buffer.get_available_ticks()
        assert ticks == [0, 5, 10, 15]
    
    def test_get_tick_range(self):
        """Test getting tick range"""
        buffer = RollbackBuffer(L1Config(compression_enabled=False))
        
        for i in range(10, 20):
            buffer.store_snapshot(i, b"data")
        
        oldest, newest = buffer.get_tick_range()
        assert oldest == 10
        assert newest == 19
    
    def test_buffer_stats(self):
        """Test buffer statistics"""
        buffer = RollbackBuffer(L1Config(tick_buffer_size=100, compression_enabled=False))
        
        for i in range(10):
            buffer.store_snapshot(i, b"test_data")
        
        stats = buffer.get_buffer_stats()
        
        assert stats['snapshot_count'] == 10
        assert stats['buffer_capacity'] == 100
        assert stats['current_tick'] == 9
        assert stats['oldest_tick'] == 0
        assert stats['newest_tick'] == 9


class TestL2AnalyticsStore:
    """Test L2: Analytics Store - DuckDB/Parquet"""
    
    def test_initialization(self):
        """Test analytics store initialization"""
        import tempfile
        import os
        
        # Use temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=True) as temp_file:
            temp_db = temp_file.name
        # File is deleted when context exits, DuckDB can create it fresh
        config = L2Config(duckdb_path=temp_db)
        
        try:
            store = AnalyticsStore(config)
            
            if store.conn:
                assert store.conn is not None
                store.close()
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
    
    def test_create_match(self):
        """Test creating match record"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=True) as temp_file:
            temp_db = temp_file.name
        # File is deleted when context exits, DuckDB can create it fresh
        config = L2Config(duckdb_path=temp_db)
        
        try:
            store = AnalyticsStore(config)
            
            if store.conn:
                result = store.create_match("match_001", {"map": "test_map"})
                assert result is True
                store.close()
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
    
    def test_store_tick_snapshot(self):
        """Test storing tick snapshot"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=True) as temp_file:
            temp_db = temp_file.name
        # File is deleted when context exits, DuckDB can create it fresh
        config = L2Config(duckdb_path=temp_db)
        
        try:
            store = AnalyticsStore(config)
            
            if store.conn:
                store.create_match("match_001")
                
                result = store.store_tick_snapshot(
                    match_id="match_001",
                    tick_id=0,
                    entity_count=100,
                    snapshot_data=b"test_snapshot",
                    crc64_checksum="abc123"
                )
                
                assert result is True
                store.close()
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)


class TestL3GlobalSynchronizer:
    """Test L3: Global Synchronizer - Redis"""
    
    def test_initialization_without_redis(self):
        """Test synchronizer initialization (without Redis)"""
        config = L3Config(redis_host="invalid_host")
        sync = GlobalSynchronizer(config)
        
        # Should handle gracefully when Redis unavailable
        assert sync.connected == False
    
    def test_command_creation(self):
        """Test command object creation"""
        from database.l3_global import Command
        
        cmd = Command(
            command_id="cmd_001",
            player_id="player_001",
            tick_id=10,
            command_type="move",
            payload={"x": 10, "y": 20}
        )
        
        assert cmd.command_id == "cmd_001"
        assert cmd.player_id == "player_001"
        assert cmd.tick_id == 10
        assert cmd.command_type == "move"
        
        # Test serialization
        cmd_dict = cmd.to_dict()
        assert cmd_dict['command_id'] == "cmd_001"
        
        # Test deserialization
        cmd2 = Command.from_dict(cmd_dict)
        assert cmd2.command_id == cmd.command_id


class TestFPrimeComponent:
    """Test NASA F´ Component Pattern"""
    
    def test_component_initialization(self):
        """Test component initialization"""
        component = DatabaseComponent("TEST_DB")
        
        assert component.component_id == "TEST_DB"
        assert component.component_name == "Database Component"
        assert component.initialized == False
        assert component.running == False
    
    def test_port_registration(self):
        """Test port registration"""
        from database.fprime_component import Port, PortType
        
        component = DatabaseComponent()
        
        # Check pre-registered ports
        assert "snapshot_in" in component.ports
        assert "snapshot_out" in component.ports
        assert component.ports["snapshot_in"].port_type == PortType.INPUT
        assert component.ports["snapshot_out"].port_type == PortType.OUTPUT
    
    def test_component_lifecycle(self):
        """Test component lifecycle"""
        component = DatabaseComponent()
        
        # Initialize
        result = component.initialize()
        assert result is True
        assert component.initialized == True
        
        # Start
        result = component.start()
        assert result is True
        assert component.running == True
        
        # Stop
        result = component.stop()
        assert result is True
        assert component.running == False
    
    def test_telemetry(self):
        """Test telemetry updates"""
        component = DatabaseComponent()
        
        component.update_telemetry("test_metric", 42.0)
        
        telemetry = component.get_telemetry()
        assert "test_metric" in telemetry
        assert telemetry["test_metric"]["value"] == 42.0
    
    def test_event_logging(self):
        """Test event logging"""
        component = DatabaseComponent()
        
        component._log_event("TEST_EVENT", {"data": "test"})
        
        assert len(component.events) > 0
        assert component.events[-1].event_type == "TEST_EVENT"


class TestDatabaseConfig:
    """Test database configuration"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = DatabaseConfig.default()
        
        assert config.l0.max_entities == 10000
        assert config.l1.tick_buffer_size == 120
        assert config.l2.batch_size == 1000
        assert config.l3.redis_port == 6379
    
    def test_config_to_dict(self):
        """Test configuration serialization"""
        config = DatabaseConfig.default()
        config_dict = config.to_dict()
        
        assert "l0" in config_dict
        assert "l1" in config_dict
        assert "l2" in config_dict
        assert "l3" in config_dict
        
        assert config_dict["l0"]["max_entities"] == 10000
    
    def test_custom_config(self):
        """Test custom configuration"""
        l0_config = L0Config(max_entities=50000, chunk_size=2048)
        config = DatabaseConfig(
            l0=l0_config,
            l1=L1Config(),
            l2=L2Config(),
            l3=L3Config()
        )
        
        assert config.l0.max_entities == 50000
        assert config.l0.chunk_size == 2048


class TestIntegration:
    """Integration tests for multi-tier system"""
    
    def test_full_pipeline(self):
        """Test full data pipeline through all tiers"""
        # L0: Create hot state
        hot_state = HotStateBuffer(L0Config(use_mmap=False, enable_crc64=True))
        
        # Add entities
        for i in range(100):
            hot_state.add_entity(
                x=float(i),
                y=float(i * 2),
                velocity_x=1.0,
                velocity_y=0.5,
                health=100.0
            )
        
        # Create snapshot
        tick_id, snapshot_data = hot_state.snapshot()
        
        # L1: Store in rollback buffer
        rollback = RollbackBuffer(L1Config(compression_enabled=False))
        result = rollback.store_snapshot(tick_id, snapshot_data)
        assert result is True
        
        # Verify rollback
        retrieved_data = rollback.get_snapshot(tick_id)
        assert retrieved_data == snapshot_data
        
        # L0: Restore from snapshot
        hot_state.restore(retrieved_data)
        assert hot_state.entity_count == 100
        assert hot_state.tick_id == tick_id
    
    def test_performance_benchmark(self):
        """Benchmark performance of hot state operations"""
        import time
        
        config = L0Config(max_entities=10000, use_mmap=False)
        buffer = HotStateBuffer(config)
        
        # Benchmark entity creation
        start = time.time()
        for i in range(1000):
            buffer.add_entity(x=float(i), y=float(i), health=100.0)
        creation_time = time.time() - start
        
        # Benchmark snapshot
        start = time.time()
        tick_id, snapshot_data = buffer.snapshot()
        snapshot_time = time.time() - start
        
        # Performance assertions
        assert creation_time < 0.1  # Should be < 100ms for 1000 entities
        assert snapshot_time < 0.01  # Should be < 10ms for snapshot
        
        print(f"\nPerformance:")
        print(f"  Entity creation: {creation_time*1000:.2f}ms for 1000 entities")
        print(f"  Snapshot: {snapshot_time*1000:.2f}ms")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
