#!/usr/bin/env python3
"""
Tests for apis/production_time_api.py

Tests the Flask endpoints of the Production Time Management API using mocked
production_time_patterns dependencies.
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

class _CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class _EventType(Enum):
    EVENT_CREATED = "event_created"
    EVENT_EXECUTED = "event_executed"
    EVENT_FAILED = "event_failed"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_SATISFIED = "dependency_satisfied"
    CIRCUIT_BREAKER_OPENED = "circuit_breaker_opened"
    CIRCUIT_BREAKER_CLOSED = "circuit_breaker_closed"
    COMPENSATION_TRIGGERED = "compensation_triggered"
    SAGA_STARTED = "saga_started"
    SAGA_COMPLETED = "saga_completed"
    SAGA_FAILED = "saga_failed"


class _TraceContext:
    def __init__(self, trace_id="trace-123", span_id="span-456", parent_span_id=None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.baggage = {}

    @classmethod
    def create_root(cls):
        return cls(trace_id="trace-root", span_id="span-root")

    @staticmethod
    def _generate_id():
        return "generated-id"

    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "baggage": self.baggage,
        }


_mock_patterns_module = types.ModuleType("production_time_patterns")
_mock_patterns_module.CircuitBreakerState = _CircuitBreakerState
_mock_patterns_module.EventType = _EventType
_mock_patterns_module.TraceContext = _TraceContext
_mock_patterns_module.ProductionTimeManager = MagicMock
_mock_patterns_module.Saga = MagicMock
_mock_patterns_module.CompensationAction = MagicMock

sys.modules.setdefault("production_time_patterns", _mock_patterns_module)

# Add apis/ directory to path so the module can be imported directly
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "apis"))

import production_time_api as api_module
from production_time_api import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_circuit_breaker(state=_CircuitBreakerState.CLOSED, failure_count=0, success_count=0):
    cb = MagicMock()
    cb.state = state
    cb.failure_count = failure_count
    cb.success_count = success_count
    cb.last_failure_time = None
    cb.get_status.return_value = {
        "state": state.value,
        "failure_count": failure_count,
        "success_count": success_count,
        "last_failure_time": None,
        "can_execute": state == _CircuitBreakerState.CLOSED,
    }
    return cb


def _make_saga(saga_id="saga-1", name="Test Saga", status="pending"):
    saga = MagicMock()
    saga.saga_id = saga_id
    saga.name = name
    saga.status = status
    saga.actions = []
    saga.executed_actions = []
    saga.start_time = None
    saga.end_time = None
    saga.error = None
    return saga


def _make_production_manager():
    manager = MagicMock()
    manager.sagas = {}
    manager.event_store = MagicMock()
    manager.event_store.events = []
    manager.tracer = MagicMock()
    manager.tracer.spans = []
    manager.get_circuit_breaker_status.return_value = {}
    return manager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset global production_manager before each test."""
    api_module.production_manager = None
    yield
    api_module.production_manager = None


@pytest.fixture
def manager():
    """Provide a configured mock production manager."""
    mgr = _make_production_manager()
    api_module.production_manager = mgr
    return mgr


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
        assert data["service"] == "Production Time Management API"
        assert "timestamp" in data
        assert "production_manager_active" in data

    def test_health_reflects_uninitialized_manager(self, client):
        data = client.get("/health").get_json()
        assert data["production_manager_active"] is False

    def test_health_reflects_initialized_manager(self, client, manager):
        data = client.get("/health").get_json()
        assert data["production_manager_active"] is True


# ---------------------------------------------------------------------------
# System status
# ---------------------------------------------------------------------------

class TestSystemStatus:
    def test_status_returns_500_when_no_manager(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 500
        assert "error" in resp.get_json()

    def test_status_returns_200_with_manager(self, client, manager):
        resp = client.get("/api/status")
        assert resp.status_code == 200

    def test_status_response_structure(self, client, manager):
        data = client.get("/api/status").get_json()
        assert "timestamp" in data
        assert "circuit_breakers" in data
        assert "total_circuit_breakers" in data
        assert "active_sagas" in data
        assert "total_sagas" in data
        assert "total_events" in data
        assert "total_spans" in data

    def test_status_counts_active_sagas(self, client, manager):
        executing_saga = _make_saga(status="executing")
        pending_saga = _make_saga(saga_id="saga-2", status="pending")
        manager.sagas = {"saga-1": executing_saga, "saga-2": pending_saga}

        data = client.get("/api/status").get_json()
        assert data["active_sagas"] == 1
        assert data["total_sagas"] == 2

    def test_status_returns_500_on_error(self, client, manager):
        manager.get_circuit_breaker_status.side_effect = RuntimeError("boom")
        resp = client.get("/api/status")
        assert resp.status_code == 500
        assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# GET /api/circuit-breakers
# ---------------------------------------------------------------------------

class TestGetCircuitBreakers:
    def test_returns_500_when_no_manager(self, client):
        resp = client.get("/api/circuit-breakers")
        assert resp.status_code == 500

    def test_returns_200_with_manager(self, client, manager):
        resp = client.get("/api/circuit-breakers")
        assert resp.status_code == 200

    def test_response_structure(self, client, manager):
        manager.get_circuit_breaker_status.return_value = {
            "svc_a": {"state": "closed", "failure_count": 0}
        }
        data = client.get("/api/circuit-breakers").get_json()
        assert "circuit_breakers" in data
        assert "total_services" in data
        assert "timestamp" in data
        assert data["total_services"] == 1

    def test_returns_500_on_error(self, client, manager):
        manager.get_circuit_breaker_status.side_effect = RuntimeError("fail")
        resp = client.get("/api/circuit-breakers")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET /api/circuit-breakers/<service_name>
# ---------------------------------------------------------------------------

class TestGetCircuitBreaker:
    def test_returns_500_when_no_manager(self, client):
        resp = client.get("/api/circuit-breakers/my_service")
        assert resp.status_code == 500

    def test_returns_200_with_manager(self, client, manager):
        cb = _make_circuit_breaker()
        manager.get_circuit_breaker.return_value = cb
        resp = client.get("/api/circuit-breakers/my_service")
        assert resp.status_code == 200

    def test_response_contains_service_name(self, client, manager):
        cb = _make_circuit_breaker()
        manager.get_circuit_breaker.return_value = cb
        data = client.get("/api/circuit-breakers/my_service").get_json()
        assert data["service_name"] == "my_service"
        assert "status" in data
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# POST /api/circuit-breakers/<service_name>/reset
# ---------------------------------------------------------------------------

class TestResetCircuitBreaker:
    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/circuit-breakers/my_service/reset")
        assert resp.status_code == 500

    def test_resets_circuit_breaker(self, client, manager):
        cb = _make_circuit_breaker(
            state=_CircuitBreakerState.OPEN, failure_count=7
        )
        manager.get_circuit_breaker.return_value = cb
        resp = client.post("/api/circuit-breakers/my_service/reset")
        assert resp.status_code == 200
        # Verify state was reset
        assert cb.state == _CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.last_failure_time is None

    def test_response_contains_service_name(self, client, manager):
        cb = _make_circuit_breaker()
        manager.get_circuit_breaker.return_value = cb
        data = client.post("/api/circuit-breakers/my_service/reset").get_json()
        assert "my_service" in data["message"]
        assert data["service_name"] == "my_service"


# ---------------------------------------------------------------------------
# GET /api/events
# ---------------------------------------------------------------------------

class TestGetEvents:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/events").status_code == 500

    def test_returns_200_with_manager(self, client, manager):
        manager.event_store.events = []
        assert client.get("/api/events").status_code == 200

    def test_response_structure(self, client, manager):
        manager.event_store.events = []
        data = client.get("/api/events").get_json()
        assert "events" in data
        assert "total_events" in data
        assert "filters" in data
        assert "timestamp" in data

    def test_filters_by_aggregate_id(self, client, manager):
        fake_event = {"event_type": "event_created", "aggregate_id": "agg-1"}
        manager.get_event_history.return_value = [fake_event]
        data = client.get("/api/events?aggregate_id=agg-1").get_json()
        manager.get_event_history.assert_called_once_with("agg-1")
        assert data["filters"]["aggregate_id"] == "agg-1"

    def test_filters_by_event_type(self, client, manager):
        evt = MagicMock()
        evt.to_dict.return_value = {"event_type": "event_created", "aggregate_id": "agg-1"}
        manager.event_store.events = [evt]
        data = client.get("/api/events?event_type=event_created").get_json()
        assert data["filters"]["event_type"] == "event_created"

    def test_applies_limit(self, client, manager):
        events = []
        for i in range(20):
            evt = MagicMock()
            evt.to_dict.return_value = {"event_type": "event_created", "aggregate_id": f"agg-{i}"}
            events.append(evt)
        manager.event_store.events = events
        data = client.get("/api/events?limit=5").get_json()
        assert data["filters"]["limit"] == 5
        assert len(data["events"]) == 5


# ---------------------------------------------------------------------------
# GET /api/events/<aggregate_id>
# ---------------------------------------------------------------------------

class TestGetAggregateEvents:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/events/agg-1").status_code == 500

    def test_returns_200_with_manager(self, client, manager):
        manager.get_event_history.return_value = []
        assert client.get("/api/events/agg-1").status_code == 200

    def test_response_structure(self, client, manager):
        manager.get_event_history.return_value = [{"event_type": "event_created"}]
        data = client.get("/api/events/agg-1").get_json()
        assert data["aggregate_id"] == "agg-1"
        assert "events" in data
        assert data["total_events"] == 1
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# GET /api/events/snapshots/<aggregate_id>
# ---------------------------------------------------------------------------

class TestGetAggregateSnapshot:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/events/snapshots/agg-1").status_code == 500

    def test_returns_404_when_no_snapshot(self, client, manager):
        manager.event_store.get_snapshot.return_value = None
        resp = client.get("/api/events/snapshots/agg-1")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_returns_snapshot(self, client, manager):
        snap = {"aggregate_id": "agg-1", "version": 5}
        manager.event_store.get_snapshot.return_value = snap
        data = client.get("/api/events/snapshots/agg-1").get_json()
        assert data["aggregate_id"] == "agg-1"
        assert data["snapshot"] == snap
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# GET /api/traces
# ---------------------------------------------------------------------------

class TestGetTraces:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/traces").status_code == 500

    def test_returns_200_with_manager(self, client, manager):
        manager.tracer.spans = []
        assert client.get("/api/traces").status_code == 200

    def test_response_structure(self, client, manager):
        manager.tracer.spans = []
        data = client.get("/api/traces").get_json()
        assert "traces" in data
        assert "total_traces" in data
        assert "limit" in data
        assert "timestamp" in data

    def test_fetches_trace_summaries(self, client, manager):
        span = MagicMock()
        span.trace_id = "trace-abc"
        manager.tracer.spans = [span]
        manager.get_trace_summary.return_value = {"trace_id": "trace-abc", "total_spans": 1}

        data = client.get("/api/traces").get_json()
        assert data["total_traces"] == 1
        manager.get_trace_summary.assert_called_once_with("trace-abc")


# ---------------------------------------------------------------------------
# GET /api/traces/<trace_id>
# ---------------------------------------------------------------------------

class TestGetTrace:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/traces/trace-abc").status_code == 500

    def test_returns_404_when_trace_not_found(self, client, manager):
        manager.get_trace_summary.return_value = None
        resp = client.get("/api/traces/trace-abc")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_returns_trace_summary(self, client, manager):
        summary = {"trace_id": "trace-abc", "total_spans": 3}
        manager.get_trace_summary.return_value = summary
        data = client.get("/api/traces/trace-abc").get_json()
        assert data["trace"] == summary
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# POST /api/traces/create
# ---------------------------------------------------------------------------

class TestCreateTrace:
    def test_returns_500_when_no_manager(self, client):
        assert client.post("/api/traces/create").status_code == 500

    def test_returns_200_and_trace_context(self, client, manager):
        data = client.post("/api/traces/create").get_json()
        assert "trace_context" in data
        assert "message" in data
        ctx = data["trace_context"]
        assert "trace_id" in ctx
        assert "span_id" in ctx


# ---------------------------------------------------------------------------
# GET /api/sagas
# ---------------------------------------------------------------------------

class TestGetSagas:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/sagas").status_code == 500

    def test_returns_200_with_manager(self, client, manager):
        assert client.get("/api/sagas").status_code == 200

    def test_returns_empty_list_when_no_sagas(self, client, manager):
        data = client.get("/api/sagas").get_json()
        assert data["sagas"] == []
        assert data["total_sagas"] == 0

    def test_returns_saga_list(self, client, manager):
        manager.sagas = {"saga-1": _make_saga("saga-1", "My Saga", "completed")}
        data = client.get("/api/sagas").get_json()
        assert data["total_sagas"] == 1
        assert data["sagas"][0]["saga_id"] == "saga-1"
        assert data["sagas"][0]["name"] == "My Saga"

    def test_filters_by_status(self, client, manager):
        manager.sagas = {
            "saga-1": _make_saga("saga-1", status="completed"),
            "saga-2": _make_saga("saga-2", status="pending"),
        }
        data = client.get("/api/sagas?status=completed").get_json()
        assert data["total_sagas"] == 1
        assert data["sagas"][0]["status"] == "completed"

    def test_returns_500_on_error(self, client, manager):
        manager.sagas = MagicMock()
        manager.sagas.values.side_effect = RuntimeError("broken")
        resp = client.get("/api/sagas")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /api/sagas
# ---------------------------------------------------------------------------

class TestCreateSaga:
    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/sagas", json={"name": "Test"})
        assert resp.status_code == 500

    def test_creates_saga(self, client, manager):
        saga = _make_saga("saga-new", "New Saga")
        manager.create_saga.return_value = saga
        data = client.post("/api/sagas", json={"saga_id": "saga-new", "name": "New Saga"}).get_json()
        assert "saga" in data
        assert data["saga"]["saga_id"] == "saga-new"
        assert data["saga"]["name"] == "New Saga"

    def test_creates_saga_with_default_id(self, client, manager):
        saga = _make_saga()
        manager.create_saga.return_value = saga
        data = client.post("/api/sagas", json={}).get_json()
        assert "saga" in data


# ---------------------------------------------------------------------------
# GET /api/sagas/<saga_id>
# ---------------------------------------------------------------------------

class TestGetSaga:
    def test_returns_500_when_no_manager(self, client):
        assert client.get("/api/sagas/saga-1").status_code == 500

    def test_returns_404_when_saga_not_found(self, client, manager):
        manager.sagas = {}
        resp = client.get("/api/sagas/saga-1")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_returns_saga_details(self, client, manager):
        saga = _make_saga("saga-1", "My Saga", "completed")
        manager.sagas = {"saga-1": saga}
        data = client.get("/api/sagas/saga-1").get_json()
        s = data["saga"]
        assert s["saga_id"] == "saga-1"
        assert s["name"] == "My Saga"
        assert s["status"] == "completed"
        assert "actions" in s
        assert "executed_actions" in s
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# POST /api/sagas/<saga_id>/execute
# ---------------------------------------------------------------------------

class TestExecuteSaga:
    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/sagas/saga-1/execute", json={})
        assert resp.status_code == 500

    def test_executes_saga_successfully(self, client, manager):
        manager.execute_saga = AsyncMock(return_value=True)
        data = client.post("/api/sagas/saga-1/execute", json={}).get_json()
        assert data["result"] == "success"
        assert data["saga_id"] == "saga-1"
        assert "trace_id" in data

    def test_executes_saga_with_compensation(self, client, manager):
        manager.execute_saga = AsyncMock(return_value=False)
        data = client.post("/api/sagas/saga-1/execute", json={}).get_json()
        assert data["result"] == "failed_with_compensation"

    def test_accepts_trace_id_in_body(self, client, manager):
        manager.execute_saga = AsyncMock(return_value=True)
        resp = client.post("/api/sagas/saga-1/execute", json={"trace_id": "trace-provided"})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/demo/circuit-breaker
# ---------------------------------------------------------------------------

class TestDemoCircuitBreaker:
    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/demo/circuit-breaker", json={})
        assert resp.status_code == 500

    def test_runs_demo(self, client, manager):
        cb = _make_circuit_breaker()
        manager.get_circuit_breaker.return_value = cb
        manager.execute_with_circuit_breaker = AsyncMock(side_effect=Exception("Simulated failure"))
        data = client.post(
            "/api/demo/circuit-breaker",
            json={"service_name": "demo_svc", "failure_count": 3},
        ).get_json()
        assert "results" in data
        assert len(data["results"]) == 3
        assert data["service_name"] == "demo_svc"
        assert "circuit_breaker_status" in data
        assert "trace_id" in data


# ---------------------------------------------------------------------------
# POST /api/demo/event-sourcing
# ---------------------------------------------------------------------------

class TestDemoEventSourcing:
    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/demo/event-sourcing")
        assert resp.status_code == 500

    def test_runs_demo(self, client, manager):
        manager.get_event_history.return_value = [
            {"event_type": "event_created"},
            {"event_type": "event_executed"},
            {"event_type": "event_failed"},
        ]
        data = client.post("/api/demo/event-sourcing").get_json()
        assert data["events_stored"] == 3
        assert "aggregate_id" in data
        assert "event_history" in data
        assert "trace_id" in data

    def test_stores_three_events(self, client, manager):
        manager.get_event_history.return_value = [
            {"event_type": "event_created"},
            {"event_type": "event_executed"},
            {"event_type": "event_failed"},
        ]
        client.post("/api/demo/event-sourcing")
        assert manager.store_event.call_count == 3


# ---------------------------------------------------------------------------
# POST /api/demo/saga
# ---------------------------------------------------------------------------

class TestDemoSaga:
    def test_returns_500_when_no_manager(self, client):
        resp = client.post("/api/demo/saga")
        assert resp.status_code == 500

    def test_runs_demo_saga(self, client, manager):
        demo_saga = _make_saga("demo_saga", "Demo Saga", "failed")
        demo_saga.executed_actions = ["action1"]
        manager.create_saga.return_value = demo_saga
        manager.execute_saga = AsyncMock(return_value=False)

        data = client.post("/api/demo/saga").get_json()
        assert "saga_id" in data
        assert "result" in data
        assert "trace_id" in data


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

class TestErrorHandlers:
    def test_404_returns_json_error(self, client):
        resp = client.get("/this/endpoint/does/not/exist")
        assert resp.status_code == 404
        assert "error" in resp.get_json()

    def test_404_error_message(self, client):
        data = client.get("/no_such_route").get_json()
        assert data["error"] == "Endpoint not found"
