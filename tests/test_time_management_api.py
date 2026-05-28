#!/usr/bin/env python3
"""
Tests for apis/time_management_api.py

Tests the Flask endpoints of the Time Management API using mocked
advanced_time_manager dependency.
"""

import sys
import types
import json
import pytest
from enum import Enum
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch


# ---------------------------------------------------------------------------
# Inject mock modules so the API can be imported without real dependencies
# ---------------------------------------------------------------------------

class _TimeEventType(Enum):
    SCHEDULED_TASK = "scheduled_task"
    MARKET_OPEN = "market_open"
    MARKET_CLOSE = "market_close"
    EARNINGS_ANNOUNCEMENT = "earnings_announcement"
    FED_MEETING = "fed_meeting"
    DATA_REFRESH = "data_refresh"
    ML_MODEL_RETRAIN = "ml_model_retrain"
    PORTFOLIO_REBALANCE = "portfolio_rebalance"
    RISK_CHECK = "risk_check"
    AUDIO_PROCESSING = "audio_processing"
    EMBEDDING_UPDATE = "embedding_update"
    SYSTEM_MAINTENANCE = "system_maintenance"


class _TimeZone(Enum):
    UTC = "UTC"
    EST = "US/Eastern"
    PST = "US/Pacific"
    GMT = "Europe/London"
    JST = "Asia/Tokyo"
    CET = "Europe/Paris"


class _ScheduleFrequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM_CRON = "custom_cron"
    MARKET_HOURS = "market_hours"
    BUSINESS_HOURS = "business_hours"


_mock_atm_module = types.ModuleType("advanced_time_manager")
_mock_atm_module.AdvancedTimeManager = MagicMock
_mock_atm_module.TimeEvent = MagicMock
_mock_atm_module.TimeEventType = _TimeEventType
_mock_atm_module.TimeZone = _TimeZone
_mock_atm_module.ScheduleFrequency = _ScheduleFrequency
_mock_atm_module.TimeExecution = MagicMock
_mock_atm_module.TimeAnalytics = MagicMock

sys.modules.setdefault("advanced_time_manager", _mock_atm_module)

import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "apis"))

import time_management_api as api_module
from time_management_api import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2024, 6, 1, 12, 0, 0)
_LATER = _NOW + timedelta(hours=1)


def _make_analytics(total=5, active=4, completed=10, failed=1,
                    avg_ms=50.0, success_rate=0.91):
    a = MagicMock()
    a.total_events = total
    a.active_events = active
    a.completed_executions = completed
    a.failed_executions = failed
    a.execution_success_rate = success_rate
    a.average_execution_time_ms = avg_ms
    a.events_by_type = {"scheduled_task": 3, "data_refresh": 2}
    a.events_by_frequency = {"daily": 3, "once": 2}
    a.last_updated = _NOW
    return a


def _make_event(event_id="evt_1", name="Test Event",
                event_type=_TimeEventType.SCHEDULED_TASK,
                timezone=_TimeZone.UTC,
                frequency=_ScheduleFrequency.ONCE,
                priority=5, is_active=True, is_recurring=False,
                cron_expression=None, max_executions=None,
                execution_count=0, last_execution=None,
                next_execution=None):
    e = MagicMock()
    e.id = event_id
    e.name = name
    e.event_type = event_type
    e.scheduled_time = _NOW
    e.timezone = timezone
    e.frequency = frequency
    e.cron_expression = cron_expression
    e.callback_function = "data_refresh_handler"
    e.parameters = {}
    e.priority = priority
    e.is_active = is_active
    e.is_recurring = is_recurring
    e.max_executions = max_executions
    e.execution_count = execution_count
    e.last_execution = last_execution
    e.next_execution = next_execution or _LATER
    e.created_at = _NOW
    e.updated_at = _NOW
    return e


def _make_execution(event_id="evt_1", status="success", duration_ms=42.0):
    ex = MagicMock()
    ex.event_id = event_id
    ex.execution_time = _NOW
    ex.duration_ms = duration_ms
    ex.status = status
    ex.result = {"ok": True}
    ex.error_message = None
    ex.metadata = {}
    return ex


def _make_time_manager():
    tm = MagicMock()
    tm.is_running = True
    tm.get_analytics.return_value = _make_analytics()
    tm.get_market_status.return_value = {
        "NYSE": {"is_open": False, "next_open": _LATER.isoformat(), "next_close": None},
        "CRYPTO": {"is_open": True, "next_open": None, "next_close": _LATER.isoformat()},
    }
    tm.get_events.return_value = [_make_event()]
    tm.get_event.return_value = _make_event()
    tm.get_upcoming_events.return_value = [_make_event()]
    tm.get_execution_history.return_value = [_make_execution()]
    tm.create_event = AsyncMock(return_value=_make_event())
    tm.update_event = AsyncMock(return_value=_make_event(name="Updated"))
    tm.delete_event = AsyncMock(return_value=True)
    return tm


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global time_manager before and after each test."""
    api_module.time_manager = None
    yield
    api_module.time_manager = None


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_response_structure(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "Time Management API"
        assert "timestamp" in data
        assert "time_manager_active" in data

    def test_health_reflects_uninitialized_manager(self, client):
        data = client.get("/health").get_json()
        assert data["time_manager_active"] is False

    def test_health_reflects_initialized_manager(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/health").get_json()
        assert data["time_manager_active"] is True


# ---------------------------------------------------------------------------
# System status
# ---------------------------------------------------------------------------

class TestSystemStatus:
    def test_status_returns_500_when_no_manager(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 500

    def test_status_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/status").status_code == 200

    def test_status_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/status").get_json()
        assert "timestamp" in data
        assert "analytics" in data
        assert "market_status" in data
        assert "scheduler_running" in data

    def test_status_analytics_fields(self, client):
        api_module.time_manager = _make_time_manager()
        analytics = client.get("/api/status").get_json()["analytics"]
        for field in ("total_events", "active_events", "completed_executions",
                      "failed_executions", "execution_success_rate",
                      "average_execution_time_ms"):
            assert field in analytics

    def test_status_analytics_values(self, client):
        api_module.time_manager = _make_time_manager()
        analytics = client.get("/api/status").get_json()["analytics"]
        assert analytics["total_events"] == 5
        assert analytics["active_events"] == 4

    def test_status_scheduler_running(self, client):
        tm = _make_time_manager()
        tm.is_running = True
        api_module.time_manager = tm
        data = client.get("/api/status").get_json()
        assert data["scheduler_running"] is True

    def test_status_handles_error(self, client):
        tm = MagicMock()
        tm.get_analytics.side_effect = RuntimeError("db error")
        api_module.time_manager = tm
        resp = client.get("/api/status")
        assert resp.status_code == 500
        assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# GET /api/events
# ---------------------------------------------------------------------------

class TestGetEvents:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/events").status_code == 500

    def test_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/events").status_code == 200

    def test_response_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/events").get_json()
        assert "events" in data
        assert "total_events" in data
        assert "filters_applied" in data

    def test_event_fields(self, client):
        api_module.time_manager = _make_time_manager()
        event = client.get("/api/events").get_json()["events"][0]
        for field in ("id", "name", "event_type", "scheduled_time", "timezone",
                      "frequency", "priority", "is_active", "is_recurring",
                      "execution_count", "created_at", "updated_at"):
            assert field in event

    def test_filter_by_is_active(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/events?is_active=true")
        call_filters = tm.get_events.call_args[0][0]
        assert call_filters.get("is_active") is True

    def test_filter_by_priority(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/events?priority=7")
        call_filters = tm.get_events.call_args[0][0]
        assert call_filters.get("priority") == 7

    def test_no_filters_calls_with_empty_dict(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/events")
        tm.get_events.assert_called_once_with({})

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_events.side_effect = RuntimeError("fail")
        api_module.time_manager = tm
        resp = client.get("/api/events")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/events/<event_id>
# ---------------------------------------------------------------------------

class TestGetEvent:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/events/evt_1").status_code == 500

    def test_returns_event(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/events/evt_1").get_json()
        assert "event" in data
        assert data["event"]["id"] == "evt_1"

    def test_returns_404_for_missing_event(self, client):
        tm = _make_time_manager()
        tm.get_event.return_value = None
        api_module.time_manager = tm
        resp = client.get("/api/events/nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_event_fields(self, client):
        api_module.time_manager = _make_time_manager()
        event = client.get("/api/events/evt_1").get_json()["event"]
        for field in ("id", "name", "event_type", "scheduled_time", "timezone",
                      "frequency", "cron_expression", "callback_function",
                      "parameters", "priority", "is_active", "is_recurring",
                      "max_executions", "execution_count", "last_execution",
                      "next_execution", "created_at", "updated_at"):
            assert field in event

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_event.side_effect = RuntimeError("boom")
        api_module.time_manager = tm
        resp = client.get("/api/events/evt_1")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/events  (create)
# ---------------------------------------------------------------------------

class TestCreateEvent:
    def _payload(self):
        return {
            "name": "My Event",
            "event_type": "scheduled_task",
            "scheduled_time": _NOW.isoformat(),
        }

    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/events", json=self._payload())
        assert resp.status_code == 500

    def test_returns_missing_field_400(self, client):
        api_module.time_manager = _make_time_manager()
        resp = client.post("/api/events", json={"name": "x"})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_creates_event_successfully(self, client):
        api_module.time_manager = _make_time_manager()
        resp = client.post("/api/events", json=self._payload())
        assert resp.status_code == 200
        data = resp.get_json()
        assert "message" in data
        assert "event" in data

    def test_created_event_has_required_fields(self, client):
        api_module.time_manager = _make_time_manager()
        event = client.post("/api/events", json=self._payload()).get_json()["event"]
        for field in ("id", "name", "event_type", "scheduled_time", "timezone",
                      "frequency", "priority", "is_active", "is_recurring",
                      "next_execution", "created_at"):
            assert field in event

    def test_handles_create_error(self, client):
        tm = _make_time_manager()
        tm.create_event = AsyncMock(side_effect=ValueError("duplicate id"))
        api_module.time_manager = tm
        resp = client.post("/api/events", json=self._payload())
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# PUT /api/events/<event_id>  (update)
# ---------------------------------------------------------------------------

class TestUpdateEvent:
    def test_returns_500_when_no_manager(self, client):
        resp = client.put("/api/events/evt_1", json={"name": "New"})
        assert resp.status_code == 500

    def test_updates_event_successfully(self, client):
        api_module.time_manager = _make_time_manager()
        resp = client.put("/api/events/evt_1", json={"name": "Updated"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "message" in data
        assert "event" in data

    def test_handles_update_error(self, client):
        tm = _make_time_manager()
        tm.update_event = AsyncMock(side_effect=ValueError("not found"))
        api_module.time_manager = tm
        resp = client.put("/api/events/evt_1", json={"name": "x"})
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# DELETE /api/events/<event_id>
# ---------------------------------------------------------------------------

class TestDeleteEvent:
    def test_returns_500_when_no_manager(self, client):
        resp = client.delete("/api/events/evt_1")
        assert resp.status_code == 500

    def test_deletes_event_successfully(self, client):
        api_module.time_manager = _make_time_manager()
        resp = client.delete("/api/events/evt_1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["event_id"] == "evt_1"

    def test_returns_404_for_missing_event(self, client):
        tm = _make_time_manager()
        tm.delete_event = AsyncMock(return_value=False)
        api_module.time_manager = tm
        resp = client.delete("/api/events/nonexistent")
        assert resp.status_code == 404

    def test_handles_delete_error(self, client):
        tm = _make_time_manager()
        tm.delete_event = AsyncMock(side_effect=RuntimeError("db fail"))
        api_module.time_manager = tm
        resp = client.delete("/api/events/evt_1")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/events/upcoming
# ---------------------------------------------------------------------------

class TestGetUpcomingEvents:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/events/upcoming").status_code == 500

    def test_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/events/upcoming").status_code == 200

    def test_response_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/events/upcoming").get_json()
        assert "upcoming_events" in data
        assert "total_upcoming" in data
        assert "limit" in data

    def test_default_limit_is_10(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/events/upcoming")
        tm.get_upcoming_events.assert_called_once_with(10)

    def test_custom_limit(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/events/upcoming?limit=5")
        tm.get_upcoming_events.assert_called_once_with(5)

    def test_event_fields(self, client):
        api_module.time_manager = _make_time_manager()
        event = client.get("/api/events/upcoming").get_json()["upcoming_events"][0]
        for field in ("id", "name", "event_type", "next_execution",
                      "priority", "is_recurring", "execution_count"):
            assert field in event

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_upcoming_events.side_effect = RuntimeError("fail")
        api_module.time_manager = tm
        resp = client.get("/api/events/upcoming")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/executions
# ---------------------------------------------------------------------------

class TestGetExecutionHistory:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/executions").status_code == 500

    def test_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/executions").status_code == 200

    def test_response_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/executions").get_json()
        assert "executions" in data
        assert "total_executions" in data
        assert "filters" in data

    def test_execution_fields(self, client):
        api_module.time_manager = _make_time_manager()
        execution = client.get("/api/executions").get_json()["executions"][0]
        for field in ("event_id", "execution_time", "duration_ms",
                      "status", "result", "error_message", "metadata"):
            assert field in execution

    def test_filter_by_event_id(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/executions?event_id=evt_1")
        tm.get_execution_history.assert_called_once_with("evt_1", 100)

    def test_default_limit_is_100(self, client):
        tm = _make_time_manager()
        api_module.time_manager = tm
        client.get("/api/executions")
        tm.get_execution_history.assert_called_once_with(None, 100)

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_execution_history.side_effect = RuntimeError("fail")
        api_module.time_manager = tm
        resp = client.get("/api/executions")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/market/status
# ---------------------------------------------------------------------------

class TestGetMarketStatus:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/market/status").status_code == 500

    def test_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/market/status").status_code == 200

    def test_response_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/market/status").get_json()
        assert "market_status" in data
        assert "timestamp" in data

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_market_status.side_effect = RuntimeError("fail")
        api_module.time_manager = tm
        resp = client.get("/api/market/status")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/timezones
# ---------------------------------------------------------------------------

class TestGetTimezones:
    def test_returns_200(self, client):
        assert client.get("/api/timezones").status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/timezones").get_json()
        assert "timezones" in data
        assert "total_timezones" in data

    def test_timezones_have_value_and_name(self, client):
        timezones = client.get("/api/timezones").get_json()["timezones"]
        assert len(timezones) > 0
        for tz in timezones:
            assert "value" in tz
            assert "name" in tz

    def test_utc_is_present(self, client):
        timezones = client.get("/api/timezones").get_json()["timezones"]
        values = [tz["value"] for tz in timezones]
        assert "UTC" in values


# ---------------------------------------------------------------------------
# GET /api/event-types
# ---------------------------------------------------------------------------

class TestGetEventTypes:
    def test_returns_200(self, client):
        assert client.get("/api/event-types").status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/event-types").get_json()
        assert "event_types" in data
        assert "total_event_types" in data

    def test_event_types_have_value_and_name(self, client):
        event_types = client.get("/api/event-types").get_json()["event_types"]
        assert len(event_types) > 0
        for et in event_types:
            assert "value" in et
            assert "name" in et

    def test_scheduled_task_is_present(self, client):
        event_types = client.get("/api/event-types").get_json()["event_types"]
        values = [et["value"] for et in event_types]
        assert "scheduled_task" in values


# ---------------------------------------------------------------------------
# GET /api/frequencies
# ---------------------------------------------------------------------------

class TestGetFrequencies:
    def test_returns_200(self, client):
        assert client.get("/api/frequencies").status_code == 200

    def test_response_structure(self, client):
        data = client.get("/api/frequencies").get_json()
        assert "frequencies" in data
        assert "total_frequencies" in data

    def test_frequencies_have_value_and_name(self, client):
        frequencies = client.get("/api/frequencies").get_json()["frequencies"]
        assert len(frequencies) > 0
        for freq in frequencies:
            assert "value" in freq
            assert "name" in freq

    def test_daily_is_present(self, client):
        frequencies = client.get("/api/frequencies").get_json()["frequencies"]
        values = [f["value"] for f in frequencies]
        assert "daily" in values


# ---------------------------------------------------------------------------
# GET /api/analytics
# ---------------------------------------------------------------------------

class TestGetAnalytics:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/analytics").status_code == 500

    def test_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/analytics").status_code == 200

    def test_response_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/analytics").get_json()
        assert "analytics" in data
        assert "timestamp" in data

    def test_analytics_fields(self, client):
        api_module.time_manager = _make_time_manager()
        analytics = client.get("/api/analytics").get_json()["analytics"]
        for field in ("total_events", "active_events", "completed_executions",
                      "failed_executions", "average_execution_time_ms",
                      "events_by_type", "events_by_frequency",
                      "execution_success_rate", "last_updated"):
            assert field in analytics

    def test_analytics_values(self, client):
        api_module.time_manager = _make_time_manager()
        analytics = client.get("/api/analytics").get_json()["analytics"]
        assert analytics["total_events"] == 5
        assert analytics["execution_success_rate"] == pytest.approx(0.91)

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_analytics.side_effect = RuntimeError("fail")
        api_module.time_manager = tm
        resp = client.get("/api/analytics")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/analytics/performance
# ---------------------------------------------------------------------------

class TestGetPerformanceMetrics:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/analytics/performance").status_code == 500

    def test_returns_200_with_manager(self, client):
        api_module.time_manager = _make_time_manager()
        assert client.get("/api/analytics/performance").status_code == 200

    def test_response_structure(self, client):
        api_module.time_manager = _make_time_manager()
        data = client.get("/api/analytics/performance").get_json()
        assert "performance_metrics" in data
        assert "timestamp" in data

    def test_performance_metrics_fields(self, client):
        api_module.time_manager = _make_time_manager()
        metrics = client.get("/api/analytics/performance").get_json()["performance_metrics"]
        for field in ("total_recent_executions", "successful_executions",
                      "failed_executions", "success_rate",
                      "average_duration_ms", "success_by_event_type"):
            assert field in metrics

    def test_success_rate_for_single_successful_execution(self, client):
        tm = _make_time_manager()
        tm.get_execution_history.return_value = [_make_execution(status="success")]
        tm.get_event.return_value = _make_event()
        api_module.time_manager = tm
        metrics = client.get("/api/analytics/performance").get_json()["performance_metrics"]
        assert metrics["success_rate"] == pytest.approx(1.0)
        assert metrics["successful_executions"] == 1
        assert metrics["failed_executions"] == 0

    def test_success_rate_with_mixed_executions(self, client):
        tm = _make_time_manager()
        executions = [
            _make_execution(status="success"),
            _make_execution(status="failed"),
        ]
        tm.get_execution_history.return_value = executions
        tm.get_event.return_value = _make_event()
        api_module.time_manager = tm
        metrics = client.get("/api/analytics/performance").get_json()["performance_metrics"]
        assert metrics["success_rate"] == pytest.approx(0.5)

    def test_empty_executions_gives_zero_success_rate(self, client):
        tm = _make_time_manager()
        tm.get_execution_history.return_value = []
        api_module.time_manager = tm
        metrics = client.get("/api/analytics/performance").get_json()["performance_metrics"]
        assert metrics["success_rate"] == pytest.approx(0.0)
        assert metrics["total_recent_executions"] == 0

    def test_handles_error(self, client):
        tm = MagicMock()
        tm.get_analytics.side_effect = RuntimeError("fail")
        api_module.time_manager = tm
        resp = client.get("/api/analytics/performance")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# 404 error handler
# ---------------------------------------------------------------------------

class TestErrorHandlers:
    def test_unknown_route_returns_404_json(self, client):
        resp = client.get("/api/does_not_exist_xyz")
        assert resp.status_code == 404
        assert "error" in resp.get_json()
