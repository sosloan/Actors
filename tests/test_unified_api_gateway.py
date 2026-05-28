#!/usr/bin/env python3
"""
Tests for the ACTORS Unified API Gateway.

All heavy system dependencies (EmbeddingSearchEngine, MLEnhancedSpeechToTradingSystem,
etc.) are mocked via sys.modules so the Flask app can be imported and exercised
without the optional third-party libraries being installed.
"""

import json
import sys
import types
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


# ---------------------------------------------------------------------------
# Stub out every import that unified_api_gateway tries to pull in at
# module-load time, before we import the module itself.
# ---------------------------------------------------------------------------

def _make_stub(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


# Geospatial stubs --------------------------------------------------------
_geo_stub = _make_stub("geospatial_engine")
_geo_stub.GDAL_AVAILABLE = False

class _FakeGeospatialEngine:
    pass

_geo_stub.GeospatialEngine = _FakeGeospatialEngine

_db_config_stub = _make_stub("database")
_db_config_sub = _make_stub("database.config")

class _FakeGeospatialConfig:
    cache_dir = "/tmp/geo_cache"

_db_config_sub.GeospatialConfig = _FakeGeospatialConfig
_db_config_stub.config = _db_config_sub

# Embedding search stub ---------------------------------------------------
_emb_stub = _make_stub("embedding_search")

class _FakeEmbeddingSearchEngine:
    def __init__(self, *a, **kw):
        pass
    def load_embeddings(self):
        pass
    def search_by_text(self, query, top_k):
        return []
    def find_similar_to_id(self, eid, top_k):
        return []
    def get_statistics(self):
        return {"total_embeddings": 0, "average_similarity": 0.0, "last_updated": "now"}

_emb_stub.EmbeddingSearchEngine = _FakeEmbeddingSearchEngine

# ML pipeline stub --------------------------------------------------------
_ml_stub = _make_stub("ml_pipeline_integration")

class _FakeMLSystem:
    async def initialize(self):
        pass
    async def get_system_status(self):
        return {"total_enhanced_signals": 0, "high_priority_signals": 0,
                "ml_pipeline_health": {"is_active": False, "total_models": 0}}
    def get_enhanced_signals(self, limit=10):
        return []
    def get_signals_by_priority(self, min_priority=7):
        return []

_ml_stub.MLEnhancedSpeechToTradingSystem = _FakeMLSystem

# Speech-to-trading connector stub ----------------------------------------
_speech_stub = _make_stub("speech_to_trading_connector")

_VALID_AUDIO_SOURCES = {"financial_news", "earnings_call", "analyst_report", "social_media"}

class _FakeAudioSource:
    def __init__(self, value):
        if value not in _VALID_AUDIO_SOURCES:
            raise ValueError(f"'{value}' is not a valid AudioSource")
        self.value = value

_speech_stub.AudioSource = _FakeAudioSource

class _FakeSpeechConnector:
    trading_signals = []
    def get_recent_signals(self, limit=10):
        return []
    def get_signals_by_symbol(self, symbol):
        return []
    def get_signals_by_source(self, source):
        return []

_speech_stub.SpeechToTradingConnector = _FakeSpeechConnector

# Advanced time manager stub ----------------------------------------------
_time_stub = _make_stub("advanced_time_manager")

class _FakeTimeManager:
    async def initialize(self):
        pass
    def get_events(self, filters=None):
        return []
    def get_upcoming_events(self, limit=10):
        return []
    def get_market_status(self):
        return {"is_open": False, "session": "closed"}
    def get_analytics(self):
        a = MagicMock()
        a.total_events = 0
        a.active_events = 0
        a.completed_executions = 0
        a.failed_executions = 0
        a.execution_success_rate = 1.0
        a.average_execution_time_ms = 0.0
        a.events_by_type = {}
        a.events_by_frequency = {}
        return a

_time_stub.AdvancedTimeManager = _FakeTimeManager

class _FakeTimeEventType:
    def __init__(self, value):
        self.value = value

_time_stub.TimeEventType = _FakeTimeEventType

# Now we can safely import the app
import importlib
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import apis.unified_api_gateway as _gw_module
from apis.unified_api_gateway import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def no_systems(client):
    """All global system instances set to None (uninitialised state)."""
    with (
        patch.object(_gw_module, "search_engine", None),
        patch.object(_gw_module, "ml_speech_system", None),
        patch.object(_gw_module, "speech_connector", None),
        patch.object(_gw_module, "time_manager", None),
        patch.object(_gw_module, "geospatial_engine", None),
    ):
        yield client


@pytest.fixture()
def systems_up(client):
    """All global system instances set to functional fakes."""
    with (
        patch.object(_gw_module, "search_engine", _FakeEmbeddingSearchEngine()),
        patch.object(_gw_module, "ml_speech_system", _FakeMLSystem()),
        patch.object(_gw_module, "speech_connector", _FakeSpeechConnector()),
        patch.object(_gw_module, "time_manager", _FakeTimeManager()),
        patch.object(_gw_module, "geospatial_engine", None),
    ):
        yield client


# ===========================================================================
# /health
# ===========================================================================

class TestHealthEndpoint:
    def test_health_returns_200(self, no_systems):
        resp = no_systems.get("/health")
        assert resp.status_code == 200

    def test_health_response_structure(self, no_systems):
        data = no_systems.get("/health").get_json()
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "systems" in data
        assert "gdal_available" in data

    def test_health_degraded_when_no_systems(self, no_systems):
        data = no_systems.get("/health").get_json()
        assert data["status"] == "degraded"

    def test_health_systems_dict_keys(self, no_systems):
        data = no_systems.get("/health").get_json()
        for key in ("embedding_search", "ml_speech_system", "speech_connector",
                    "time_manager", "geospatial_engine"):
            assert key in data["systems"]


# ===========================================================================
# /api/status
# ===========================================================================

class TestApiStatus:
    def test_status_200(self, no_systems):
        assert no_systems.get("/api/status").status_code == 200

    def test_status_structure(self, no_systems):
        data = no_systems.get("/api/status").get_json()
        assert "timestamp" in data
        assert "systems" in data

    def test_status_not_initialized_when_no_systems(self, no_systems):
        data = no_systems.get("/api/status").get_json()
        assert data["systems"]["embedding_search"]["status"] == "not_initialized"
        assert data["systems"]["ml_speech_system"]["status"] == "not_initialized"
        assert data["systems"]["speech_connector"]["status"] == "not_initialized"

    def test_status_healthy_when_systems_up(self, systems_up):
        data = systems_up.get("/api/status").get_json()
        assert data["systems"]["embedding_search"]["status"] == "healthy"
        assert data["systems"]["speech_connector"]["status"] == "healthy"


# ===========================================================================
# /api/embeddings/search
# ===========================================================================

class TestEmbeddingSearchEndpoint:
    def test_returns_500_when_no_engine(self, no_systems):
        resp = no_systems.post(
            "/api/embeddings/search",
            json={"query": "test"},
            content_type="application/json",
        )
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_400_when_empty_query(self, systems_up):
        resp = systems_up.post(
            "/api/embeddings/search",
            json={"query": ""},
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_returns_200_with_valid_query(self, systems_up):
        resp = systems_up.post(
            "/api/embeddings/search",
            json={"query": "test query", "top_k": 5},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["query"] == "test query"
        assert "results" in data
        assert "total_results" in data
        assert "search_time_ms" in data

    def test_default_top_k(self, systems_up):
        resp = systems_up.post(
            "/api/embeddings/search",
            json={"query": "hello"},
            content_type="application/json",
        )
        assert resp.status_code == 200


# ===========================================================================
# /api/embeddings/similar/<id>
# ===========================================================================

class TestSimilarEmbeddingsEndpoint:
    def test_returns_500_when_no_engine(self, no_systems):
        resp = no_systems.get("/api/embeddings/similar/doc1")
        assert resp.status_code == 500

    def test_returns_200_when_engine_up(self, systems_up):
        resp = systems_up.get("/api/embeddings/similar/doc1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["target_id"] == "doc1"
        assert "results" in data
        assert "total_results" in data
        assert "search_time_ms" in data

    def test_respects_top_k_param(self, systems_up):
        resp = systems_up.get("/api/embeddings/similar/doc1?top_k=3")
        assert resp.status_code == 200


# ===========================================================================
# /api/embeddings/stats
# ===========================================================================

class TestEmbeddingStatsEndpoint:
    def test_returns_500_when_no_engine(self, no_systems):
        assert no_systems.get("/api/embeddings/stats").status_code == 500

    def test_returns_stats_when_engine_up(self, systems_up):
        resp = systems_up.get("/api/embeddings/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_embeddings" in data


# ===========================================================================
# /api/speech/signals
# ===========================================================================

class TestSpeechSignalsEndpoint:
    def test_returns_500_when_no_connector(self, no_systems):
        assert no_systems.get("/api/speech/signals").status_code == 500

    def test_returns_200_with_connector(self, systems_up):
        resp = systems_up.get("/api/speech/signals")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "signals" in data
        assert "total_signals" in data
        assert "filters" in data

    def test_invalid_source_returns_400(self, systems_up):
        resp = systems_up.get("/api/speech/signals?source=INVALID_SOURCE")
        assert resp.status_code == 400

    def test_limit_param_forwarded(self, systems_up):
        resp = systems_up.get("/api/speech/signals?limit=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["filters"]["limit"] == 5


# ===========================================================================
# /api/ml-speech/signals
# ===========================================================================

class TestMlSpeechSignalsEndpoint:
    def test_returns_500_when_no_ml_system(self, no_systems):
        assert no_systems.get("/api/ml-speech/signals").status_code == 500

    def test_returns_200_with_ml_system(self, systems_up):
        resp = systems_up.get("/api/ml-speech/signals")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "enhanced_signals" in data
        assert "total_signals" in data
        assert "filters" in data


# ===========================================================================
# /api/analytics/overview
# ===========================================================================

class TestAnalyticsOverview:
    def test_returns_200_always(self, no_systems):
        resp = no_systems.get("/api/analytics/overview")
        assert resp.status_code == 200

    def test_structure(self, no_systems):
        data = no_systems.get("/api/analytics/overview").get_json()
        assert "timestamp" in data
        assert "systems" in data

    def test_with_systems_up(self, systems_up):
        data = systems_up.get("/api/analytics/overview").get_json()
        assert data["systems"]["embedding_search"]["status"] == "healthy"
        assert data["systems"]["speech_trading"]["status"] == "healthy"


# ===========================================================================
# /api/analytics/performance
# ===========================================================================

class TestAnalyticsPerformance:
    def test_returns_200(self, no_systems):
        assert no_systems.get("/api/analytics/performance").status_code == 200

    def test_structure(self, no_systems):
        data = no_systems.get("/api/analytics/performance").get_json()
        assert "timestamp" in data
        assert "performance" in data

    def test_with_systems_up(self, systems_up):
        data = systems_up.get("/api/analytics/performance").get_json()
        assert data["performance"]["embedding_search"]["status"] == "healthy"


# ===========================================================================
# /api/time/events
# ===========================================================================

class TestTimeEventsEndpoint:
    def test_returns_500_when_no_manager(self, no_systems):
        assert no_systems.get("/api/time/events").status_code == 500

    def test_returns_200_with_manager(self, systems_up):
        resp = systems_up.get("/api/time/events")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "events" in data
        assert "total_events" in data

    def test_returns_empty_list(self, systems_up):
        data = systems_up.get("/api/time/events").get_json()
        assert data["events"] == []
        assert data["total_events"] == 0


# ===========================================================================
# /api/time/upcoming
# ===========================================================================

class TestUpcomingTimeEventsEndpoint:
    def test_returns_500_when_no_manager(self, no_systems):
        assert no_systems.get("/api/time/upcoming").status_code == 500

    def test_returns_200_with_manager(self, systems_up):
        resp = systems_up.get("/api/time/upcoming")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "upcoming_events" in data
        assert "total_upcoming" in data


# ===========================================================================
# /api/time/market-status
# ===========================================================================

class TestMarketStatusEndpoint:
    def test_returns_500_when_no_manager(self, no_systems):
        assert no_systems.get("/api/time/market-status").status_code == 500

    def test_returns_200_with_manager(self, systems_up):
        resp = systems_up.get("/api/time/market-status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "market_status" in data
        assert "timestamp" in data


# ===========================================================================
# /api/time/analytics
# ===========================================================================

class TestTimeAnalyticsEndpoint:
    def test_returns_500_when_no_manager(self, no_systems):
        assert no_systems.get("/api/time/analytics").status_code == 500

    def test_returns_200_with_manager(self, systems_up):
        resp = systems_up.get("/api/time/analytics")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "analytics" in data
        assert "timestamp" in data
        analytics = data["analytics"]
        for key in ("total_events", "active_events", "completed_executions",
                    "failed_executions", "execution_success_rate",
                    "average_execution_time_ms", "events_by_type",
                    "events_by_frequency"):
            assert key in analytics


# ===========================================================================
# Error handlers
# ===========================================================================

class TestErrorHandlers:
    def test_404_returns_json(self, client):
        resp = client.get("/nonexistent_route_xyz")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data
        assert data["error"] == "Endpoint not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
