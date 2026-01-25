"""
Database Configuration for RTS Engine Persistence Layer

Defines latency targets, buffer sizes, and storage parameters
for the multi-tier database system.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class L0Config:
    """Hot State Buffer Configuration (< 0.1ms latency)"""
    max_entities: int = 10000
    chunk_size: int = 1024  # For SIMD operations
    use_mmap: bool = True
    mmap_file_path: str = "/tmp/rts_hot_state.mmap"
    enable_crc64: bool = True


@dataclass
class L1Config:
    """Rollback Buffer Configuration (< 1.0ms latency)"""
    tick_buffer_size: int = 120  # Store last 120 ticks
    compression_enabled: bool = True
    compression_level: int = 1  # LZ4 fast compression
    tick_rate_ms: float = 16.6  # 60 FPS (16.6ms per tick)


@dataclass
class L2Config:
    """Analytics Store Configuration (< 10ms latency)"""
    duckdb_path: str = "/tmp/rts_analytics.duckdb"
    parquet_export_path: str = "/tmp/rts_exports"
    batch_size: int = 1000
    enable_compression: bool = True
    compression_type: str = "snappy"


@dataclass
class L3Config:
    """Global Synchronization Configuration (20-50ms latency)"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    command_timeout_ms: int = 50
    enable_persistence: bool = True
    tick_sequence_key: str = "rts:tick:sequence"


@dataclass
class DatabaseConfig:
    """Complete Database Configuration"""
    l0: L0Config
    l1: L1Config
    l2: L2Config
    l3: L3Config
    
    @classmethod
    def default(cls) -> "DatabaseConfig":
        """Create default configuration"""
        return cls(
            l0=L0Config(),
            l1=L1Config(),
            l2=L2Config(),
            l3=L3Config()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "l0": {
                "max_entities": self.l0.max_entities,
                "chunk_size": self.l0.chunk_size,
                "use_mmap": self.l0.use_mmap,
                "mmap_file_path": self.l0.mmap_file_path,
                "enable_crc64": self.l0.enable_crc64,
            },
            "l1": {
                "tick_buffer_size": self.l1.tick_buffer_size,
                "compression_enabled": self.l1.compression_enabled,
                "compression_level": self.l1.compression_level,
                "tick_rate_ms": self.l1.tick_rate_ms,
            },
            "l2": {
                "duckdb_path": self.l2.duckdb_path,
                "parquet_export_path": self.l2.parquet_export_path,
                "batch_size": self.l2.batch_size,
                "enable_compression": self.l2.enable_compression,
                "compression_type": self.l2.compression_type,
            },
            "l3": {
                "redis_host": self.l3.redis_host,
                "redis_port": self.l3.redis_port,
                "redis_db": self.l3.redis_db,
                "command_timeout_ms": self.l3.command_timeout_ms,
                "enable_persistence": self.l3.enable_persistence,
                "tick_sequence_key": self.l3.tick_sequence_key,
            }
        }
