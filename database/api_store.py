"""
API Data Store - DuckDB-backed persistence for ACTORS API layer

Provides API-specific tables on top of the multi-tier database system:
- api_requests       : request/response audit log
- geospatial_queries : geospatial analysis results
- embedding_searches : semantic search results
- time_events        : scheduled and executed time events
- trading_signals    : speech-to-trading signal history
- travel_plans       : travel optimisation results
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

from .config import L2Config


class APIStore:
    """
    Persistent store for ACTORS API data.

    All tables are created inside the same DuckDB file used by the
    analytics store so that a single database holds both RTS engine
    telemetry and API-layer data.
    """

    def __init__(self, config: Optional[L2Config] = None):
        self.config = config or L2Config()
        self.conn = None

        if DUCKDB_AVAILABLE:
            self._init_database()
        else:
            print("Warning: DuckDB not available. API persistence disabled.")

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_database(self):
        db_dir = os.path.dirname(self.config.duckdb_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.conn = duckdb.connect(self.config.duckdb_path)
        self._create_tables()

    def _create_tables(self):
        if not self.conn:
            return

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS api_requests (
                request_id      VARCHAR PRIMARY KEY,
                api_name        VARCHAR NOT NULL,
                endpoint        VARCHAR NOT NULL,
                method          VARCHAR NOT NULL,
                status_code     INTEGER,
                response_time_ms DOUBLE,
                request_data    JSON,
                response_data   JSON,
                created_at      TIMESTAMP DEFAULT current_timestamp
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS geospatial_queries (
                query_id        VARCHAR PRIMARY KEY,
                query_type      VARCHAR NOT NULL,
                file_path       VARCHAR,
                parameters      JSON,
                result_summary  JSON,
                created_at      TIMESTAMP DEFAULT current_timestamp
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embedding_searches (
                search_id       VARCHAR PRIMARY KEY,
                query_text      VARCHAR NOT NULL,
                top_k           INTEGER,
                result_count    INTEGER,
                top_result_id   VARCHAR,
                top_similarity  DOUBLE,
                search_time_ms  DOUBLE,
                created_at      TIMESTAMP DEFAULT current_timestamp
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS time_events (
                event_id        VARCHAR PRIMARY KEY,
                event_type      VARCHAR NOT NULL,
                title           VARCHAR,
                scheduled_time  TIMESTAMP,
                timezone        VARCHAR,
                status          VARCHAR,
                metadata        JSON,
                created_at      TIMESTAMP DEFAULT current_timestamp
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS trading_signals (
                signal_id       VARCHAR PRIMARY KEY,
                signal_type     VARCHAR NOT NULL,
                ticker          VARCHAR,
                confidence      DOUBLE,
                risk_level      VARCHAR,
                price_target    DOUBLE,
                source_text     VARCHAR,
                audio_source    VARCHAR,
                metadata        JSON,
                created_at      TIMESTAMP DEFAULT current_timestamp
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS travel_plans (
                plan_id         VARCHAR PRIMARY KEY,
                origin          VARCHAR,
                destination     VARCHAR,
                travel_class    VARCHAR,
                purpose         VARCHAR,
                estimated_cost  DOUBLE,
                optimization_score DOUBLE,
                plan_data       JSON,
                created_at      TIMESTAMP DEFAULT current_timestamp
            )
        """)

        # Indexes for common queries
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_api_requests_api ON api_requests(api_name, created_at)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_trading_signals_ticker ON trading_signals(ticker, created_at)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_time_events_type ON time_events(event_type, scheduled_time)")

    # ------------------------------------------------------------------
    # api_requests
    # ------------------------------------------------------------------

    def log_request(
        self,
        request_id: str,
        api_name: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
    ) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO api_requests
                    (request_id, api_name, endpoint, method, status_code,
                     response_time_ms, request_data, response_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    request_id, api_name, endpoint, method, status_code,
                    response_time_ms,
                    json.dumps(request_data or {}),
                    json.dumps(response_data or {}),
                ],
            )
            return True
        except Exception as e:
            print(f"Error logging request: {e}")
            return False

    def get_recent_requests(self, api_name: Optional[str] = None, limit: int = 50) -> List[Dict]:
        if not self.conn:
            return []
        if api_name:
            rows = self.conn.execute(
                "SELECT * FROM api_requests WHERE api_name = ? ORDER BY created_at DESC LIMIT ?",
                [api_name, limit],
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM api_requests ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        cols = ["request_id", "api_name", "endpoint", "method", "status_code",
                "response_time_ms", "request_data", "response_data", "created_at"]
        return [dict(zip(cols, r)) for r in rows]

    # ------------------------------------------------------------------
    # geospatial_queries
    # ------------------------------------------------------------------

    def store_geospatial_query(
        self,
        query_id: str,
        query_type: str,
        file_path: Optional[str] = None,
        parameters: Optional[Dict] = None,
        result_summary: Optional[Dict] = None,
    ) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO geospatial_queries
                    (query_id, query_type, file_path, parameters, result_summary)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    query_id, query_type, file_path,
                    json.dumps(parameters or {}),
                    json.dumps(result_summary or {}),
                ],
            )
            return True
        except Exception as e:
            print(f"Error storing geospatial query: {e}")
            return False

    def get_geospatial_history(self, query_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        if not self.conn:
            return []
        if query_type:
            rows = self.conn.execute(
                "SELECT * FROM geospatial_queries WHERE query_type = ? ORDER BY created_at DESC LIMIT ?",
                [query_type, limit],
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM geospatial_queries ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        cols = ["query_id", "query_type", "file_path", "parameters", "result_summary", "created_at"]
        return [dict(zip(cols, r)) for r in rows]

    # ------------------------------------------------------------------
    # embedding_searches
    # ------------------------------------------------------------------

    def store_embedding_search(
        self,
        search_id: str,
        query_text: str,
        top_k: int,
        result_count: int,
        top_result_id: Optional[str] = None,
        top_similarity: Optional[float] = None,
        search_time_ms: Optional[float] = None,
    ) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO embedding_searches
                    (search_id, query_text, top_k, result_count,
                     top_result_id, top_similarity, search_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [search_id, query_text, top_k, result_count,
                 top_result_id, top_similarity, search_time_ms],
            )
            return True
        except Exception as e:
            print(f"Error storing embedding search: {e}")
            return False

    def get_search_history(self, limit: int = 50) -> List[Dict]:
        if not self.conn:
            return []
        rows = self.conn.execute(
            "SELECT * FROM embedding_searches ORDER BY created_at DESC LIMIT ?",
            [limit],
        ).fetchall()
        cols = ["search_id", "query_text", "top_k", "result_count",
                "top_result_id", "top_similarity", "search_time_ms", "created_at"]
        return [dict(zip(cols, r)) for r in rows]

    # ------------------------------------------------------------------
    # time_events
    # ------------------------------------------------------------------

    def store_time_event(
        self,
        event_id: str,
        event_type: str,
        title: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
        timezone: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO time_events
                    (event_id, event_type, title, scheduled_time, timezone, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [event_id, event_type, title, scheduled_time,
                 timezone, status, json.dumps(metadata or {})],
            )
            return True
        except Exception as e:
            print(f"Error storing time event: {e}")
            return False

    def get_time_events(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict]:
        if not self.conn:
            return []
        if event_type:
            rows = self.conn.execute(
                "SELECT * FROM time_events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?",
                [event_type, limit],
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM time_events ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        cols = ["event_id", "event_type", "title", "scheduled_time",
                "timezone", "status", "metadata", "created_at"]
        return [dict(zip(cols, r)) for r in rows]

    # ------------------------------------------------------------------
    # trading_signals
    # ------------------------------------------------------------------

    def store_trading_signal(
        self,
        signal_id: str,
        signal_type: str,
        ticker: Optional[str] = None,
        confidence: Optional[float] = None,
        risk_level: Optional[str] = None,
        price_target: Optional[float] = None,
        source_text: Optional[str] = None,
        audio_source: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO trading_signals
                    (signal_id, signal_type, ticker, confidence, risk_level,
                     price_target, source_text, audio_source, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [signal_id, signal_type, ticker, confidence, risk_level,
                 price_target, source_text, audio_source,
                 json.dumps(metadata or {})],
            )
            return True
        except Exception as e:
            print(f"Error storing trading signal: {e}")
            return False

    def get_trading_signals(self, ticker: Optional[str] = None, limit: int = 50) -> List[Dict]:
        if not self.conn:
            return []
        if ticker:
            rows = self.conn.execute(
                "SELECT * FROM trading_signals WHERE ticker = ? ORDER BY created_at DESC LIMIT ?",
                [ticker, limit],
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM trading_signals ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        cols = ["signal_id", "signal_type", "ticker", "confidence", "risk_level",
                "price_target", "source_text", "audio_source", "metadata", "created_at"]
        return [dict(zip(cols, r)) for r in rows]

    # ------------------------------------------------------------------
    # travel_plans
    # ------------------------------------------------------------------

    def store_travel_plan(
        self,
        plan_id: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        travel_class: Optional[str] = None,
        purpose: Optional[str] = None,
        estimated_cost: Optional[float] = None,
        optimization_score: Optional[float] = None,
        plan_data: Optional[Dict] = None,
    ) -> bool:
        if not self.conn:
            return False
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO travel_plans
                    (plan_id, origin, destination, travel_class, purpose,
                     estimated_cost, optimization_score, plan_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [plan_id, origin, destination, travel_class, purpose,
                 estimated_cost, optimization_score, json.dumps(plan_data or {})],
            )
            return True
        except Exception as e:
            print(f"Error storing travel plan: {e}")
            return False

    def get_travel_plans(self, destination: Optional[str] = None, limit: int = 50) -> List[Dict]:
        if not self.conn:
            return []
        if destination:
            rows = self.conn.execute(
                "SELECT * FROM travel_plans WHERE destination = ? ORDER BY created_at DESC LIMIT ?",
                [destination, limit],
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM travel_plans ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        cols = ["plan_id", "origin", "destination", "travel_class", "purpose",
                "estimated_cost", "optimization_score", "plan_data", "created_at"]
        return [dict(zip(cols, r)) for r in rows]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()
