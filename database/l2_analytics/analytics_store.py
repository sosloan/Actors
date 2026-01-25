"""
L2: Analytics Store - DuckDB/Parquet Integration

This module provides long-term storage and analytics capabilities
using DuckDB for efficient columnar queries and Parquet for persistence.

Key Features:
- DuckDB in-process OLAP database
- Parquet file format support
- Complex SQL queries on simulation data
- Match history and telemetry storage
- Replay analysis

Target Latency: < 10ms
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

from ..config import L2Config


class AnalyticsStore:
    """
    L2 Analytics Store - Long-term storage and analytics.
    
    Uses DuckDB for in-process columnar queries and Parquet for
    efficient storage. Optimized for post-game analysis and telemetry.
    """
    
    def __init__(self, config: Optional[L2Config] = None):
        """Initialize analytics store"""
        self.config = config or L2Config()
        self.conn = None
        
        if DUCKDB_AVAILABLE:
            self._init_database()
        else:
            print("Warning: DuckDB not available. Analytics features disabled.")
    
    def _init_database(self):
        """Initialize DuckDB database"""
        # Create database directory if needed
        db_dir = os.path.dirname(self.config.duckdb_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Connect to DuckDB
        self.conn = duckdb.connect(self.config.duckdb_path)
        
        # Create core tables
        self._create_tables()
        
        # Create export directory
        if not os.path.exists(self.config.parquet_export_path):
            os.makedirs(self.config.parquet_export_path, exist_ok=True)
    
    def _create_tables(self):
        """Create database schema"""
        if not self.conn:
            return
        
        # Match metadata table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id VARCHAR PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds DOUBLE,
                num_players INTEGER,
                map_name VARCHAR,
                game_mode VARCHAR,
                metadata JSON
            )
        """)
        
        # Tick snapshots table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tick_snapshots (
                snapshot_id BIGINT PRIMARY KEY,
                match_id VARCHAR,
                tick_id BIGINT,
                timestamp TIMESTAMP,
                entity_count INTEGER,
                snapshot_data BLOB,
                crc64_checksum VARCHAR,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        # Entity telemetry table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_telemetry (
                telemetry_id BIGINT PRIMARY KEY,
                match_id VARCHAR,
                tick_id BIGINT,
                entity_id INTEGER,
                entity_type VARCHAR,
                x_coord DOUBLE,
                y_coord DOUBLE,
                velocity_x DOUBLE,
                velocity_y DOUBLE,
                health DOUBLE,
                attributes JSON,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        # Unit statistics table (aggregated)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS unit_statistics (
                stat_id BIGINT PRIMARY KEY,
                match_id VARCHAR,
                entity_id INTEGER,
                entity_type VARCHAR,
                total_distance_moved DOUBLE,
                max_velocity DOUBLE,
                avg_health DOUBLE,
                time_alive_seconds DOUBLE,
                damage_dealt DOUBLE,
                damage_taken DOUBLE,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        # Create indexes for common queries
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_tick_match ON tick_snapshots(match_id, tick_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_match ON entity_telemetry(match_id, tick_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_stats_match ON unit_statistics(match_id)")
    
    def create_match(self, match_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create new match record.
        
        Args:
            match_id: Unique match identifier
            metadata: Optional match metadata
        
        Returns:
            True if successful
        """
        if not self.conn:
            return False
        
        import json
        
        try:
            self.conn.execute("""
                INSERT INTO matches (match_id, start_time, metadata)
                VALUES (?, ?, ?)
            """, [match_id, datetime.now(), json.dumps(metadata or {})])
            return True
        except Exception as e:
            print(f"Error creating match: {e}")
            return False
    
    def store_tick_snapshot(
        self,
        match_id: str,
        tick_id: int,
        entity_count: int,
        snapshot_data: bytes,
        crc64_checksum: Optional[str] = None
    ) -> bool:
        """Store tick snapshot"""
        if not self.conn:
            return False
        
        try:
            snapshot_id = (hash(match_id) * 1000000 + tick_id) % (2**63)
            
            self.conn.execute("""
                INSERT INTO tick_snapshots 
                (snapshot_id, match_id, tick_id, timestamp, entity_count, snapshot_data, crc64_checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                snapshot_id,
                match_id,
                tick_id,
                datetime.now(),
                entity_count,
                snapshot_data,
                crc64_checksum
            ])
            return True
        except Exception as e:
            print(f"Error storing snapshot: {e}")
            return False
    
    def store_entity_telemetry(
        self,
        match_id: str,
        tick_id: int,
        entities: List[Dict[str, Any]]
    ) -> bool:
        """
        Store entity telemetry data in batch.
        
        Args:
            match_id: Match identifier
            tick_id: Tick identifier
            entities: List of entity data dictionaries
        
        Returns:
            True if successful
        """
        if not self.conn or not entities:
            return False
        
        import json
        
        try:
            # Prepare batch insert
            values = []
            for entity in entities:
                telemetry_id = (hash(match_id) * 1000000 + tick_id * 10000 + entity.get('entity_id', 0)) % (2**63)
                values.append([
                    telemetry_id,
                    match_id,
                    tick_id,
                    entity.get('entity_id'),
                    entity.get('entity_type'),
                    entity.get('x', 0.0),
                    entity.get('y', 0.0),
                    entity.get('velocity_x', 0.0),
                    entity.get('velocity_y', 0.0),
                    entity.get('health', 100.0),
                    json.dumps(entity.get('attributes', {}))
                ])
            
            # Batch insert
            self.conn.executemany("""
                INSERT INTO entity_telemetry 
                (telemetry_id, match_id, tick_id, entity_id, entity_type, 
                 x_coord, y_coord, velocity_x, velocity_y, health, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            
            return True
        except Exception as e:
            print(f"Error storing telemetry: {e}")
            return False
    
    def query_ticks(self, match_id: str, start_tick: int, end_tick: int) -> List[Dict]:
        """Query tick snapshots in range"""
        if not self.conn:
            return []
        
        result = self.conn.execute("""
            SELECT tick_id, timestamp, entity_count, crc64_checksum
            FROM tick_snapshots
            WHERE match_id = ? AND tick_id BETWEEN ? AND ?
            ORDER BY tick_id
        """, [match_id, start_tick, end_tick]).fetchall()
        
        return [
            {
                'tick_id': row[0],
                'timestamp': row[1],
                'entity_count': row[2],
                'crc64_checksum': row[3]
            }
            for row in result
        ]
    
    def export_to_parquet(self, match_id: str, table: str = 'entity_telemetry') -> Optional[str]:
        """
        Export match data to Parquet file.
        
        Args:
            match_id: Match to export
            table: Table to export
        
        Returns:
            Path to exported file or None
        """
        if not self.conn:
            return None
        
        try:
            filename = f"{match_id}_{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            filepath = os.path.join(self.config.parquet_export_path, filename)
            
            # Export to Parquet with compression
            self.conn.execute(f"""
                COPY (SELECT * FROM {table} WHERE match_id = ?)
                TO '{filepath}' (FORMAT PARQUET, COMPRESSION '{self.config.compression_type}')
            """, [match_id])
            
            return filepath
        except Exception as e:
            print(f"Error exporting to Parquet: {e}")
            return None
    
    def get_match_statistics(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match statistics"""
        if not self.conn:
            return None
        
        result = self.conn.execute("""
            SELECT 
                COUNT(DISTINCT tick_id) as tick_count,
                COUNT(*) as total_snapshots,
                AVG(entity_count) as avg_entities_per_tick,
                MIN(timestamp) as first_tick,
                MAX(timestamp) as last_tick
            FROM tick_snapshots
            WHERE match_id = ?
        """, [match_id]).fetchone()
        
        if not result:
            return None
        
        return {
            'tick_count': result[0],
            'total_snapshots': result[1],
            'avg_entities_per_tick': result[2],
            'first_tick': result[3],
            'last_tick': result[4]
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __del__(self):
        """Cleanup"""
        self.close()
