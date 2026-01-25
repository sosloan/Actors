#!/usr/bin/env python3
"""
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
import numpy as np
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            assert result == True
        
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
        temp_db = tempfile.mktemp(suffix='.duckdb')
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
        
        temp_db = tempfile.mktemp(suffix='.duckdb')
        config = L2Config(duckdb_path=temp_db)
        
        try:
            store = AnalyticsStore(config)
            
            if store.conn:
                result = store.create_match("match_001", {"map": "test_map"})
                assert result == True
                store.close()
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
    
    def test_store_tick_snapshot(self):
        """Test storing tick snapshot"""
        import tempfile
        import os
        
        temp_db = tempfile.mktemp(suffix='.duckdb')
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
                
                assert result == True
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
        assert result == True
        assert component.initialized == True
        
        # Start
        result = component.start()
        assert result == True
        assert component.running == True
        
        # Stop
        result = component.stop()
        assert result == True
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
        assert result == True
        
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
