"""
L1: Rollback Buffer - Ring Buffer with LZ4 Compression

This module implements a ring buffer for storing recent simulation ticks
to enable rollback and desync recovery in lockstep multiplayer.

Key Features:
- Ring buffer for last N ticks (default: 120)
- LZ4 compression for memory efficiency
- Fast snapshot storage and retrieval
- Deterministic state recovery

Target Latency: < 1.0ms
"""

from collections import deque
from typing import Optional, Tuple, List
import time

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

from ..config import L1Config


class RollbackSnapshot:
    """Single tick snapshot with metadata"""
    
    def __init__(self, tick_id: int, data: bytes, compressed: bool = False):
        self.tick_id = tick_id
        self.data = data
        self.compressed = compressed
        self.timestamp = time.time()
        self.size = len(data)


class RollbackBuffer:
    """
    L1 Rollback Buffer - Stores recent ticks for desync recovery.
    
    Uses a ring buffer to maintain the last N ticks of simulation state.
    Implements LZ4 compression for memory efficiency while maintaining
    sub-millisecond access times.
    """
    
    def __init__(self, config: Optional[L1Config] = None):
        """Initialize rollback buffer"""
        self.config = config or L1Config()
        
        # Ring buffer for snapshots
        self.snapshots: deque[RollbackSnapshot] = deque(
            maxlen=self.config.tick_buffer_size
        )
        
        # Current tick tracking
        self.current_tick = 0
        
        # Performance metrics
        self.total_snapshots = 0
        self.total_compressed_size = 0
        self.total_uncompressed_size = 0
    
    def store_snapshot(self, tick_id: int, snapshot_data: bytes) -> bool:
        """
        Store snapshot for given tick.
        
        Args:
            tick_id: Simulation tick ID
            snapshot_data: Serialized snapshot data
        
        Returns:
            True if successfully stored
        """
        compressed = False
        data = snapshot_data
        
        # Compress if enabled and LZ4 is available
        if self.config.compression_enabled and LZ4_AVAILABLE:
            try:
                data = lz4.frame.compress(
                    snapshot_data,
                    compression_level=self.config.compression_level
                )
                compressed = True
            except Exception as e:
                # Fall back to uncompressed if compression fails
                print(f"Warning: LZ4 compression failed: {e}")
                data = snapshot_data
        
        # Create and store snapshot
        snapshot = RollbackSnapshot(tick_id, data, compressed)
        self.snapshots.append(snapshot)
        
        # Update metrics
        self.total_snapshots += 1
        self.total_uncompressed_size += len(snapshot_data)
        self.total_compressed_size += len(data)
        self.current_tick = tick_id
        
        return True
    
    def get_snapshot(self, tick_id: int) -> Optional[bytes]:
        """
        Retrieve snapshot for given tick.
        
        Args:
            tick_id: Simulation tick ID to retrieve
        
        Returns:
            Snapshot data or None if not found
        """
        # Search for snapshot (linear search is fine for small buffer)
        for snapshot in self.snapshots:
            if snapshot.tick_id == tick_id:
                data = snapshot.data
                
                # Decompress if needed
                if snapshot.compressed and LZ4_AVAILABLE:
                    data = lz4.frame.decompress(data)
                
                return data
        
        return None
    
    def get_latest_snapshot(self) -> Optional[Tuple[int, bytes]]:
        """
        Get the most recent snapshot.
        
        Returns:
            Tuple of (tick_id, snapshot_data) or None
        """
        if not self.snapshots:
            return None
        
        snapshot = self.snapshots[-1]
        data = snapshot.data
        
        if snapshot.compressed and LZ4_AVAILABLE:
            data = lz4.frame.decompress(data)
        
        return snapshot.tick_id, data
    
    def rollback_to(self, tick_id: int) -> Optional[bytes]:
        """
        Rollback to specific tick.
        
        Args:
            tick_id: Target tick to rollback to
        
        Returns:
            Snapshot data for the tick, or None if not available
        """
        return self.get_snapshot(tick_id)
    
    def get_available_ticks(self) -> List[int]:
        """Get list of all available tick IDs"""
        return [snapshot.tick_id for snapshot in self.snapshots]
    
    def get_tick_range(self) -> Tuple[int, int]:
        """
        Get range of available ticks.
        
        Returns:
            Tuple of (oldest_tick, newest_tick)
        """
        if not self.snapshots:
            return (0, 0)
        
        return (self.snapshots[0].tick_id, self.snapshots[-1].tick_id)
    
    def get_compression_ratio(self) -> float:
        """Calculate compression ratio"""
        if self.total_uncompressed_size == 0:
            return 1.0
        
        return self.total_uncompressed_size / self.total_compressed_size
    
    def get_buffer_stats(self) -> dict:
        """Get buffer statistics"""
        return {
            'snapshot_count': len(self.snapshots),
            'buffer_capacity': self.config.tick_buffer_size,
            'current_tick': self.current_tick,
            'total_snapshots': self.total_snapshots,
            'compression_enabled': self.config.compression_enabled,
            'compression_ratio': self.get_compression_ratio(),
            'uncompressed_size_bytes': self.total_uncompressed_size,
            'compressed_size_bytes': self.total_compressed_size,
            'oldest_tick': self.snapshots[0].tick_id if self.snapshots else None,
            'newest_tick': self.snapshots[-1].tick_id if self.snapshots else None,
        }
    
    def clear(self):
        """Clear all snapshots"""
        self.snapshots.clear()
        self.current_tick = 0
        self.total_snapshots = 0
        self.total_compressed_size = 0
        self.total_uncompressed_size = 0
    
    def can_rollback_to(self, tick_id: int) -> bool:
        """Check if rollback to tick is possible"""
        return any(s.tick_id == tick_id for s in self.snapshots)
    
    def get_memory_usage(self) -> int:
        """Get approximate memory usage in bytes"""
        return sum(s.size for s in self.snapshots)
