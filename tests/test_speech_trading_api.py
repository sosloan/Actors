#!/usr/bin/env python3
"""
Tests for apis/speech_trading_api.py

Tests the Flask endpoints of the Speech-to-Trading API using mocked
speech connector and ML system dependencies.
"""

import sys
import types
import json
import pytest
from enum import Enum
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch


# ---------------------------------------------------------------------------
# Inject mock modules so the API can be imported without real dependencies
# ---------------------------------------------------------------------------

class _TradingSignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    HEDGE = "hedge"


class _AudioSource(Enum):
    EARNINGS_CALL = "earnings_call"
    FED_SPEECH = "fed_speech"
    FINANCIAL_NEWS = "financial_news"
    ANALYST_CALL = "analyst_call"
    SOCIAL_MEDIA = "social_media"


_mock_connector_module = types.ModuleType("speech_to_trading_connector")
_mock_connector_module.TradingSignalType = _TradingSignalType
_mock_connector_module.AudioSource = _AudioSource
_mock_connector_module.SpeechToTradingConnector = MagicMock
_mock_connector_module.TradingSignal = MagicMock
_mock_connector_module.AudioTranscription = MagicMock
_mock_connector_module.FinancialEntity = MagicMock
_mock_connector_module.SentimentAnalysis = MagicMock

_mock_ml_module = types.ModuleType("ml_pipeline_integration")
_mock_ml_module.MLEnhancedSpeechToTradingSystem = MagicMock

sys.modules.setdefault("speech_to_trading_connector", _mock_connector_module)
sys.modules.setdefault("ml_pipeline_integration", _mock_ml_module)

# Add apis/ directory to path so the module can be imported directly
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "apis"))

import speech_trading_api as api_module
from speech_trading_api import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_signal(symbol="AAPL", signal_type=_TradingSignalType.BUY, source=_AudioSource.FINANCIAL_NEWS):
    sig = MagicMock()
    sig.signal_type = signal_type
    sig.symbol = symbol
    sig.confidence = 0.85
    sig.reasoning = "Strong earnings beat"
    sig.source = source
    sig.timestamp = datetime(2024, 1, 15, 10, 30, 0)
    sig.risk_level = "medium"
    return sig


def _make_enhanced_signal(base_signal=None):
    base = base_signal or _make_signal()
    pred = MagicMock()
    pred.model_type = MagicMock()
    pred.model_type.value = "sentiment_enhancer"
    pred.confidence = 0.9
    pred.features_used = ["sentiment", "volume"]
    pred.timestamp = datetime(2024, 1, 15, 10, 30, 0)
    pred.model_version = "1.0"

    enhanced = MagicMock()
    enhanced.base_signal = base
    enhanced.enhanced_confidence = 0.92
    enhanced.risk_score = 0.3
    enhanced.market_impact_prediction = 0.7
    enhanced.execution_priority = 8
    enhanced.ml_predictions = [pred]
    return enhanced


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global system instances before each test."""
    api_module.speech_connector = None
    api_module.ml_speech_system = None
    yield
    api_module.speech_connector = None
    api_module.ml_speech_system = None


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_response_structure(self, client):
        data = resp = client.get("/health").get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "Speech-to-Trading API"
        assert "timestamp" in data
        assert "speech_connector_active" in data
        assert "ml_system_active" in data

    def test_health_reflects_uninitialized_systems(self, client):
        data = client.get("/health").get_json()
        assert data["speech_connector_active"] is False
        assert data["ml_system_active"] is False

    def test_health_reflects_initialized_systems(self, client):
        api_module.speech_connector = MagicMock()
        api_module.ml_speech_system = MagicMock()
        data = client.get("/health").get_json()
        assert data["speech_connector_active"] is True
        assert data["ml_system_active"] is True


# ---------------------------------------------------------------------------
# System status
# ---------------------------------------------------------------------------

class TestSystemStatus:
    def test_status_returns_200(self, client):
        assert client.get("/api/status").status_code == 200

    def test_status_structure(self, client):
        data = client.get("/api/status").get_json()
        assert "timestamp" in data
        assert "systems" in data

    def test_status_shows_not_initialized_when_no_systems(self, client):
        data = client.get("/api/status").get_json()
        assert data["systems"]["speech_connector"]["status"] == "not_initialized"
        assert data["systems"]["ml_enhanced"]["status"] == "not_initialized"

    def test_status_with_healthy_speech_connector(self, client):
        connector = MagicMock()
        connector.trading_signals = [_make_signal()]
        connector.get_recent_signals.return_value = [_make_signal()]
        api_module.speech_connector = connector

        data = client.get("/api/status").get_json()
        sc = data["systems"]["speech_connector"]
        assert sc["status"] == "healthy"
        assert sc["total_signals"] == 1

    def test_status_with_healthy_ml_system(self, client):
        ml = MagicMock()
        ml.get_system_status = AsyncMock(return_value={
            "total_enhanced_signals": 5,
            "high_priority_signals": 2,
            "ml_pipeline_health": {"is_active": True}
        })
        api_module.ml_speech_system = ml

        data = client.get("/api/status").get_json()
        mls = data["systems"]["ml_enhanced"]
        assert mls["status"] == "healthy"
        assert mls["total_enhanced_signals"] == 5

    def test_status_handles_speech_connector_error(self, client):
        connector = MagicMock()
        connector.get_recent_signals.side_effect = RuntimeError("connector down")
        api_module.speech_connector = connector

        data = client.get("/api/status").get_json()
        assert data["systems"]["speech_connector"]["status"] == "error"

    def test_status_handles_ml_system_error(self, client):
        ml = MagicMock()
        ml.get_system_status = AsyncMock(side_effect=RuntimeError("ml down"))
        api_module.ml_speech_system = ml

        data = client.get("/api/status").get_json()
        assert data["systems"]["ml_enhanced"]["status"] == "error"


# ---------------------------------------------------------------------------
# GET /api/signals
# ---------------------------------------------------------------------------

class TestGetTradingSignals:
    def test_returns_500_when_no_connector(self, client):
        resp = client.get("/api/signals")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_signals_list(self, client):
        connector = MagicMock()
        connector.get_recent_signals.return_value = [_make_signal()]
        api_module.speech_connector = connector

        data = client.get("/api/signals").get_json()
        assert "signals" in data
        assert data["total_signals"] == 1

    def test_signal_fields(self, client):
        connector = MagicMock()
        connector.get_recent_signals.return_value = [_make_signal()]
        api_module.speech_connector = connector

        sig = client.get("/api/signals").get_json()["signals"][0]
        for field in ("signal_type", "symbol", "confidence", "reasoning", "source", "timestamp", "risk_level"):
            assert field in sig

    def test_filters_by_symbol(self, client):
        connector = MagicMock()
        connector.get_signals_by_symbol.return_value = [_make_signal(symbol="TSLA")]
        api_module.speech_connector = connector

        data = client.get("/api/signals?symbol=TSLA").get_json()
        connector.get_signals_by_symbol.assert_called_once_with("TSLA")
        assert data["filters"]["symbol"] == "TSLA"

    def test_filters_by_valid_source(self, client):
        connector = MagicMock()
        connector.get_signals_by_source.return_value = []
        api_module.speech_connector = connector

        resp = client.get("/api/signals?source=earnings_call")
        assert resp.status_code == 200

    def test_invalid_source_returns_400(self, client):
        api_module.speech_connector = MagicMock()
        resp = client.get("/api/signals?source=invalid_source_xyz")
        assert resp.status_code == 400

    def test_limit_parameter(self, client):
        connector = MagicMock()
        connector.get_recent_signals.return_value = []
        api_module.speech_connector = connector

        client.get("/api/signals?limit=5")
        connector.get_recent_signals.assert_called_with(5)

    def test_default_limit(self, client):
        connector = MagicMock()
        connector.get_recent_signals.return_value = []
        api_module.speech_connector = connector

        client.get("/api/signals")
        connector.get_recent_signals.assert_called_with(10)


# ---------------------------------------------------------------------------
# GET /api/ml/signals
# ---------------------------------------------------------------------------

class TestGetEnhancedSignals:
    def test_returns_500_when_no_ml_system(self, client):
        resp = client.get("/api/ml/signals")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_returns_enhanced_signals(self, client):
        ml = MagicMock()
        ml.get_enhanced_signals.return_value = [_make_enhanced_signal()]
        api_module.ml_speech_system = ml

        data = client.get("/api/ml/signals").get_json()
        assert "enhanced_signals" in data
        assert data["total_signals"] == 1

    def test_enhanced_signal_fields(self, client):
        ml = MagicMock()
        ml.get_enhanced_signals.return_value = [_make_enhanced_signal()]
        api_module.ml_speech_system = ml

        sig = client.get("/api/ml/signals").get_json()["enhanced_signals"][0]
        assert "base_signal" in sig
        assert "ml_enhancement" in sig

    def test_filters_by_min_priority(self, client):
        ml = MagicMock()
        ml.get_signals_by_priority.return_value = [_make_enhanced_signal()]
        api_module.ml_speech_system = ml

        data = client.get("/api/ml/signals?min_priority=7").get_json()
        ml.get_signals_by_priority.assert_called_once_with(7)
        assert data["filters"]["min_priority"] == 7

    def test_no_min_priority_uses_get_enhanced_signals(self, client):
        ml = MagicMock()
        ml.get_enhanced_signals.return_value = []
        api_module.ml_speech_system = ml

        client.get("/api/ml/signals")
        ml.get_enhanced_signals.assert_called()


# ---------------------------------------------------------------------------
# GET /api/analytics/overview
# ---------------------------------------------------------------------------

class TestAnalyticsOverview:
    def test_returns_200_without_systems(self, client):
        resp = client.get("/api/analytics/overview")
        assert resp.status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/analytics/overview").get_json()
        assert "timestamp" in data
        assert "systems" in data

    def test_includes_speech_trading_analytics(self, client):
        connector = MagicMock()
        connector.trading_signals = [_make_signal()]
        connector.get_recent_signals.return_value = [_make_signal()]
        api_module.speech_connector = connector

        data = client.get("/api/analytics/overview").get_json()
        assert "speech_trading" in data["systems"]
        assert data["systems"]["speech_trading"]["status"] == "healthy"

    def test_includes_ml_analytics(self, client):
        ml = MagicMock()
        ml.get_system_status = AsyncMock(return_value={
            "total_enhanced_signals": 3,
            "ml_pipeline_health": {"is_active": True}
        })
        ml.get_enhanced_signals.return_value = []
        ml.get_signals_by_priority.return_value = []
        api_module.ml_speech_system = ml

        data = client.get("/api/analytics/overview").get_json()
        assert "ml_enhanced" in data["systems"]
        assert data["systems"]["ml_enhanced"]["status"] == "healthy"

    def test_speech_connector_error_does_not_crash(self, client):
        connector = MagicMock()
        connector.get_recent_signals.side_effect = RuntimeError("boom")
        api_module.speech_connector = connector

        resp = client.get("/api/analytics/overview")
        assert resp.status_code == 200
        assert resp.get_json()["systems"]["speech_trading"]["status"] == "error"


# ---------------------------------------------------------------------------
# GET /api/analytics/performance
# ---------------------------------------------------------------------------

class TestAnalyticsPerformance:
    def test_returns_200(self, client):
        assert client.get("/api/analytics/performance").status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/analytics/performance").get_json()
        assert "timestamp" in data
        assert "performance" in data

    def test_includes_speech_trading_performance(self, client):
        connector = MagicMock()
        connector.trading_signals = []
        connector.get_recent_signals.return_value = []
        api_module.speech_connector = connector

        data = client.get("/api/analytics/performance").get_json()
        assert "speech_trading" in data["performance"]
        assert data["performance"]["speech_trading"]["status"] == "healthy"

    def test_includes_ml_performance(self, client):
        ml = MagicMock()
        ml.get_system_status = AsyncMock(return_value={
            "ml_pipeline_health": {"is_active": True, "total_models": 3}
        })
        api_module.ml_speech_system = ml

        data = client.get("/api/analytics/performance").get_json()
        assert "ml_enhanced" in data["performance"]
        assert data["performance"]["ml_enhanced"]["status"] == "healthy"


# ---------------------------------------------------------------------------
# POST /api/audio/process
# ---------------------------------------------------------------------------

class TestProcessAudio:
    def test_returns_500_when_no_connector(self, client):
        resp = client.post("/api/audio/process", json={"text": "AAPL up"})
        assert resp.status_code == 500

    def test_missing_text_returns_400(self, client):
        api_module.speech_connector = MagicMock()
        resp = client.post("/api/audio/process", json={"source": "financial_news"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_empty_text_returns_400(self, client):
        api_module.speech_connector = MagicMock()
        resp = client.post("/api/audio/process", json={"text": "   "})
        assert resp.status_code == 400

    def test_invalid_source_returns_400(self, client):
        api_module.speech_connector = MagicMock()
        resp = client.post("/api/audio/process", json={"text": "AAPL up", "source": "bad_source"})
        assert resp.status_code == 400

    def test_valid_request_returns_200(self, client):
        connector = MagicMock()
        connector.process_audio_transcription = AsyncMock(return_value=[_make_signal()])
        api_module.speech_connector = connector

        resp = client.post("/api/audio/process", json={
            "text": "AAPL earnings beat expectations",
            "source": "earnings_call",
            "duration": 30.0
        })
        assert resp.status_code == 200

    def test_valid_response_structure(self, client):
        connector = MagicMock()
        connector.process_audio_transcription = AsyncMock(return_value=[_make_signal()])
        api_module.speech_connector = connector

        data = client.post("/api/audio/process", json={
            "text": "TSLA surges on delivery data",
            "source": "financial_news"
        }).get_json()

        assert "audio_text" in data
        assert "signals" in data
        assert "total_signals" in data
        assert data["processing_type"] == "basic"

    def test_default_source_is_financial_news(self, client):
        connector = MagicMock()
        connector.process_audio_transcription = AsyncMock(return_value=[])
        api_module.speech_connector = connector

        data = client.post("/api/audio/process", json={"text": "market update"}).get_json()
        assert data["source"] == "financial_news"


# ---------------------------------------------------------------------------
# POST /api/ml/process
# ---------------------------------------------------------------------------

class TestProcessAudioWithML:
    def test_returns_500_when_no_ml_system(self, client):
        resp = client.post("/api/ml/process", json={"text": "AAPL up"})
        assert resp.status_code == 500

    def test_missing_text_returns_400(self, client):
        api_module.ml_speech_system = MagicMock()
        resp = client.post("/api/ml/process", json={})
        assert resp.status_code == 400

    def test_empty_text_returns_400(self, client):
        api_module.ml_speech_system = MagicMock()
        resp = client.post("/api/ml/process", json={"text": ""})
        assert resp.status_code == 400

    def test_valid_request_returns_200(self, client):
        ml = MagicMock()
        ml.process_audio_with_ml = AsyncMock(return_value=[_make_enhanced_signal()])
        api_module.ml_speech_system = ml

        resp = client.post("/api/ml/process", json={
            "text": "AAPL strong earnings",
            "source": "earnings_call"
        })
        assert resp.status_code == 200

    def test_valid_response_structure(self, client):
        ml = MagicMock()
        ml.process_audio_with_ml = AsyncMock(return_value=[_make_enhanced_signal()])
        api_module.ml_speech_system = ml

        data = client.post("/api/ml/process", json={
            "text": "TSLA upgrade by analyst",
            "source": "analyst_call"
        }).get_json()

        assert "audio_text" in data
        assert "enhanced_signals" in data
        assert "total_signals" in data
        assert data["processing_type"] == "ml_enhanced"

    def test_enhanced_signal_fields_in_response(self, client):
        ml = MagicMock()
        ml.process_audio_with_ml = AsyncMock(return_value=[_make_enhanced_signal()])
        api_module.ml_speech_system = ml

        data = client.post("/api/ml/process", json={"text": "market news"}).get_json()
        sig = data["enhanced_signals"][0]
        assert "base_signal" in sig
        assert "ml_enhancement" in sig
        assert "ml_predictions" in sig


# ---------------------------------------------------------------------------
# POST /api/demo/basic
# ---------------------------------------------------------------------------

class TestDemoBasic:
    def test_returns_500_when_no_connector(self, client):
        resp = client.post("/api/demo/basic")
        assert resp.status_code == 500

    def test_returns_200_with_connector(self, client):
        connector = MagicMock()
        connector.process_audio_transcription = AsyncMock(return_value=[_make_signal()])
        api_module.speech_connector = connector

        resp = client.post("/api/demo/basic")
        assert resp.status_code == 200

    def test_response_has_demo_results(self, client):
        connector = MagicMock()
        connector.process_audio_transcription = AsyncMock(return_value=[_make_signal()])
        api_module.speech_connector = connector

        data = client.post("/api/demo/basic").get_json()
        assert "demo_results" in data
        assert "total_audio_sources" in data
        assert "total_signals" in data
        assert data["demo_type"] == "basic_speech_trading"

    def test_demo_processes_multiple_audio_sources(self, client):
        connector = MagicMock()
        connector.process_audio_transcription = AsyncMock(return_value=[_make_signal()])
        api_module.speech_connector = connector

        data = client.post("/api/demo/basic").get_json()
        assert data["total_audio_sources"] == 3


# ---------------------------------------------------------------------------
# POST /api/demo/ml-enhanced
# ---------------------------------------------------------------------------

class TestDemoMLEnhanced:
    def test_returns_500_when_no_ml_system(self, client):
        resp = client.post("/api/demo/ml-enhanced")
        assert resp.status_code == 500

    def test_returns_200_with_ml_system(self, client):
        ml = MagicMock()
        ml.process_audio_with_ml = AsyncMock(return_value=[_make_enhanced_signal()])
        api_module.ml_speech_system = ml

        resp = client.post("/api/demo/ml-enhanced")
        assert resp.status_code == 200

    def test_response_has_demo_results(self, client):
        ml = MagicMock()
        ml.process_audio_with_ml = AsyncMock(return_value=[_make_enhanced_signal()])
        api_module.ml_speech_system = ml

        data = client.post("/api/demo/ml-enhanced").get_json()
        assert "demo_results" in data
        assert "total_audio_sources" in data
        assert "total_enhanced_signals" in data
        assert data["demo_type"] == "ml_enhanced_speech_trading"

    def test_demo_processes_multiple_audio_sources(self, client):
        ml = MagicMock()
        ml.process_audio_with_ml = AsyncMock(return_value=[_make_enhanced_signal()])
        api_module.ml_speech_system = ml

        data = client.post("/api/demo/ml-enhanced").get_json()
        assert data["total_audio_sources"] == 2


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

class TestErrorHandlers:
    def test_404_returns_json_error(self, client):
        resp = client.get("/api/nonexistent_endpoint_xyz")
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "Endpoint not found"

    def test_404_content_type_is_json(self, client):
        resp = client.get("/api/nonexistent_endpoint_xyz")
        assert "application/json" in resp.content_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
