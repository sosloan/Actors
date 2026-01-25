"""
High-Performance Database Persistence Layer for Lockstep RTS Engine

This module provides a multi-tier storage system optimized for:
- Zero-drift determinism
- Sub-millisecond snapshotting
- Columnar Structure of Arrays (SoA)
- XPBD physics integration
- NASA F' component patterns

Storage Tiers:
- L0: Simulation (Hot State Buffer) - < 0.1ms
- L1: Rollback (Ring Buffer with LZ4) - < 1.0ms
- L2: Analytics (DuckDB/Parquet) - < 10ms
- L3: Global (Redis/Redict) - 20-50ms
"""

from .l0_hot_state import HotStateBuffer, ColumnarArray
from .l1_rollback import RollbackBuffer, RollbackSnapshot
from .l2_analytics import AnalyticsStore
from .l3_global import GlobalSynchronizer, Command
from .fprime_component import DatabaseComponent, FPrimeComponent
from .config import DatabaseConfig, L0Config, L1Config, L2Config, L3Config

__version__ = "1.0.0"
__all__ = [
    "HotStateBuffer",
    "ColumnarArray",
    "RollbackBuffer",
    "RollbackSnapshot",
    "AnalyticsStore",
    "GlobalSynchronizer",
    "Command",
    "FPrimeComponent",
    "DatabaseComponent",
    "DatabaseConfig",
    "L0Config",
    "L1Config",
    "L2Config",
    "L3Config",
]
