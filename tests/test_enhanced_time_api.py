#!/usr/bin/env python3
"""
Tests for the Enhanced Time Management API.

Heavy system dependencies (AdvancedTimeManager, EnhancedTimeManager, etc.) are
mocked via sys.modules so the Flask app can be imported and exercised without the
optional third-party libraries being installed.
"""

import sys
import types
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from collections import defaultdict


# ---------------------------------------------------------------------------
# Stub out every import that enhanced_time_api tries to pull in at module-load
# time, before we import the module itself.
# ---------------------------------------------------------------------------

def _make_stub(name):
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


# --- advanced_time_enhancements stubs ------------------------------------

_enh_stub = _make_stub("advanced_time_enhancements")


class _FakeEventDependencyType:
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    THRESHOLD = "threshold"
    MARKET_CONDITION = "market_condition"

    def __init__(self, value):
        self.value = value


class _FakeEventStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_DEPENDENCY = "waiting_dependency"

    def __init__(self, value):
        self.value = value


class _FakeEventDependency:
    def __init__(self, source_event_id, target_event_id, dependency_type,
                 condition=None, timeout_seconds=None, retry_count=0, max_retries=3):
        self.source_event_id = source_event_id
        self.target_event_id = target_event_id
        self.dependency_type = dependency_type
        self.condition = condition
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count
        self.max_retries = max_retries


class _FakeEventExecution:
    def __init__(self, event_id, execution_time, duration_ms, status,
                 result=None, error_message=None, metadata=None,
                 dependencies_satisfied=None, triggered_events=None):
        self.event_id = event_id
        self.execution_time = execution_time
        self.duration_ms = duration_ms
        self.status = status
        self.result = result
        self.error_message = error_message
        self.metadata = metadata or {}
        self.dependencies_satisfied = dependencies_satisfied or []
        self.triggered_events = triggered_events or []


class _FakeSmartScheduleRecommendation:
    def __init__(self, event_id, recommended_time=None, confidence_score=0.85,
                 reasoning="Based on historical data", expected_duration_ms=1500.0,
                 resource_requirements=None, market_conditions=None):
        self.event_id = event_id
        self.recommended_time = recommended_time or datetime.now() + timedelta(hours=1)
        self.confidence_score = confidence_score
        self.reasoning = reasoning
        self.expected_duration_ms = expected_duration_ms
        self.resource_requirements = resource_requirements or {}
        self.market_conditions = market_conditions or {}


class _FakeDependencyManager:
    def __init__(self):
        self.dependencies = defaultdict(list)
        self.dependency_graph = defaultdict(set)

    def remove_dependency(self, source_event_id, target_event_id):
        if target_event_id in self.dependencies:
            self.dependencies[target_event_id] = [
                d for d in self.dependencies[target_event_id]
                if d.source_event_id != source_event_id
            ]
        if source_event_id in self.dependency_graph:
            self.dependency_graph[source_event_id].discard(target_event_id)

    def get_execution_order(self, events):
        return list(events)


class _FakeSmartScheduler:
    def add_execution_history(self, execution):
        pass


class _FakeEnhancedTimeManager:
    def __init__(self):
        self.dependency_manager = _FakeDependencyManager()
        self.execution_history = []
        self.smart_scheduler = _FakeSmartScheduler()

    def add_event_dependency(self, source_event_id, target_event_id,
                             dependency_type, condition=None):
        dep = _FakeEventDependency(source_event_id, target_event_id,
                                   dependency_type, condition)
        self.dependency_manager.dependencies[target_event_id].append(dep)
        self.dependency_manager.dependency_graph[source_event_id].add(target_event_id)

    def get_smart_schedule_recommendation(self, event_id, base_time):
        return _FakeSmartScheduleRecommendation(event_id=event_id,
                                                recommended_time=base_time)

    def predict_optimal_schedule(self, events, time_window):
        return {
            e: _FakeSmartScheduleRecommendation(event_id=e,
                                                recommended_time=time_window[0])
            for e in events
        }

    def get_performance_insights(self, event_id):
        return {"average_duration_ms": 1000.0, "success_rate": 0.95}


_enh_stub.EnhancedTimeManager = _FakeEnhancedTimeManager
_enh_stub.EventDependencyType = _FakeEventDependencyType
_enh_stub.EventStatus = _FakeEventStatus
_enh_stub.SmartScheduleRecommendation = _FakeSmartScheduleRecommendation
_enh_stub.EventExecution = _FakeEventExecution


# --- advanced_time_manager stubs -----------------------------------------

_atm_stub = _make_stub("advanced_time_manager")


class _FakeAnalytics:
    total_events = 0
    active_events = 0
    execution_success_rate = 1.0


class _FakeAdvancedTimeManager:
    is_running = False

    async def initialize(self):
        pass

    def get_analytics(self):
        return _FakeAnalytics()

    def get_events(self, filters=None):
        return []


_atm_stub.AdvancedTimeManager = _FakeAdvancedTimeManager


# --- Now safely import the app -------------------------------------------
import importlib
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import apis.enhanced_time_api as _api_module
from apis.enhanced_time_api import app


# ---------------------------------------------------------------------------
# Helpers / shared fakes
# ---------------------------------------------------------------------------

def _make_enhanced_manager():
    return _FakeEnhancedTimeManager()


def _make_base_manager():
    return _FakeAdvancedTimeManager()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def no_managers(client):
    """Both global managers set to None (uninitialised state)."""
    with (
        patch.object(_api_module, "enhanced_time_manager", None),
        patch.object(_api_module, "base_time_manager", None),
    ):
        yield client


@pytest.fixture()
def managers_up(client):
    """Both global managers set to functional fakes."""
    with (
        patch.object(_api_module, "enhanced_time_manager", _make_enhanced_manager()),
        patch.object(_api_module, "base_time_manager", _make_base_manager()),
    ):
        yield client


# ===========================================================================
# /health
# ===========================================================================

class TestHealthEndpoint:
    def test_health_returns_200(self, no_managers):
        assert no_managers.get("/health").status_code == 200

    def test_health_response_structure(self, no_managers):
        data = no_managers.get("/health").get_json()
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data
        assert "enhanced_manager_active" in data
        assert "base_manager_active" in data

    def test_health_managers_inactive_when_none(self, no_managers):
        data = no_managers.get("/health").get_json()
        assert data["enhanced_manager_active"] is False
        assert data["base_manager_active"] is False

    def test_health_managers_active_when_up(self, managers_up):
        data = managers_up.get("/health").get_json()
        assert data["enhanced_manager_active"] is True
        assert data["base_manager_active"] is True


# ===========================================================================
# /api/status
# ===========================================================================

class TestApiStatus:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.get("/api/status").status_code == 500

    def test_returns_500_error_json_when_uninitialized(self, no_managers):
        data = no_managers.get("/api/status").get_json()
        assert "error" in data

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.get("/api/status").status_code == 200

    def test_status_structure_when_up(self, managers_up):
        data = managers_up.get("/api/status").get_json()
        assert "timestamp" in data
        assert "base_analytics" in data
        assert "enhanced_features" in data
        assert "scheduler_running" in data

    def test_base_analytics_fields(self, managers_up):
        analytics = managers_up.get("/api/status").get_json()["base_analytics"]
        assert "total_events" in analytics
        assert "active_events" in analytics
        assert "execution_success_rate" in analytics

    def test_enhanced_features_fields(self, managers_up):
        features = managers_up.get("/api/status").get_json()["enhanced_features"]
        assert "dependency_graph_size" in features
        assert "total_dependencies" in features
        assert "execution_history_size" in features
        assert "smart_scheduler_active" in features


# ===========================================================================
# POST /api/dependencies
# ===========================================================================

class TestCreateDependency:
    _valid_payload = {
        "source_event_id": "event_a",
        "target_event_id": "event_b",
        "dependency_type": "sequential",
    }

    def test_returns_500_when_uninitialized(self, no_managers):
        resp = no_managers.post("/api/dependencies", json=self._valid_payload)
        assert resp.status_code == 500

    def test_returns_200_with_valid_payload(self, managers_up):
        resp = managers_up.post("/api/dependencies", json=self._valid_payload)
        assert resp.status_code == 200

    def test_response_contains_dependency_info(self, managers_up):
        data = managers_up.post("/api/dependencies",
                                json=self._valid_payload).get_json()
        assert "message" in data
        assert "dependency" in data
        dep = data["dependency"]
        assert dep["source_event_id"] == "event_a"
        assert dep["target_event_id"] == "event_b"
        assert dep["dependency_type"] == "sequential"

    def test_returns_400_when_missing_source_event_id(self, managers_up):
        payload = {"target_event_id": "event_b", "dependency_type": "sequential"}
        resp = managers_up.post("/api/dependencies", json=payload)
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_returns_400_when_missing_target_event_id(self, managers_up):
        payload = {"source_event_id": "event_a", "dependency_type": "sequential"}
        resp = managers_up.post("/api/dependencies", json=payload)
        assert resp.status_code == 400

    def test_returns_400_when_missing_dependency_type(self, managers_up):
        payload = {"source_event_id": "event_a", "target_event_id": "event_b"}
        resp = managers_up.post("/api/dependencies", json=payload)
        assert resp.status_code == 400

    def test_optional_condition_accepted(self, managers_up):
        payload = dict(self._valid_payload, condition={"threshold": 0.8})
        resp = managers_up.post("/api/dependencies", json=payload)
        assert resp.status_code == 200
        assert resp.get_json()["dependency"]["condition"] == {"threshold": 0.8}


# ===========================================================================
# GET /api/dependencies
# ===========================================================================

class TestGetDependencies:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.get("/api/dependencies").status_code == 500

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.get("/api/dependencies").status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.get("/api/dependencies").get_json()
        assert "dependencies" in data
        assert "total_dependencies" in data

    def test_empty_when_no_dependencies_added(self, managers_up):
        data = managers_up.get("/api/dependencies").get_json()
        assert data["dependencies"] == []
        assert data["total_dependencies"] == 0

    def test_dependency_appears_after_creation(self, managers_up):
        managers_up.post("/api/dependencies", json={
            "source_event_id": "src",
            "target_event_id": "tgt",
            "dependency_type": "sequential",
        })
        data = managers_up.get("/api/dependencies").get_json()
        assert data["total_dependencies"] == 1
        dep = data["dependencies"][0]
        assert dep["source_event_id"] == "src"
        assert dep["target_event_id"] == "tgt"


# ===========================================================================
# DELETE /api/dependencies/<source>/<target>
# ===========================================================================

class TestDeleteDependency:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.delete("/api/dependencies/src/tgt").status_code == 500

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.delete("/api/dependencies/src/tgt").status_code == 200

    def test_response_contains_ids(self, managers_up):
        data = managers_up.delete("/api/dependencies/event_a/event_b").get_json()
        assert data["source_event_id"] == "event_a"
        assert data["target_event_id"] == "event_b"
        assert "message" in data

    def test_dependency_removed_after_delete(self, managers_up):
        managers_up.post("/api/dependencies", json={
            "source_event_id": "src",
            "target_event_id": "tgt",
            "dependency_type": "sequential",
        })
        assert managers_up.get("/api/dependencies").get_json()["total_dependencies"] == 1
        managers_up.delete("/api/dependencies/src/tgt")
        assert managers_up.get("/api/dependencies").get_json()["total_dependencies"] == 0


# ===========================================================================
# POST /api/dependencies/execution-order
# ===========================================================================

class TestExecutionOrder:
    def test_returns_500_when_uninitialized(self, no_managers):
        resp = no_managers.post("/api/dependencies/execution-order",
                                json={"events": ["a", "b"]})
        assert resp.status_code == 500

    def test_returns_400_when_events_missing(self, managers_up):
        resp = managers_up.post("/api/dependencies/execution-order", json={})
        assert resp.status_code == 400

    def test_returns_400_when_events_empty(self, managers_up):
        resp = managers_up.post("/api/dependencies/execution-order",
                                json={"events": []})
        assert resp.status_code == 400

    def test_returns_200_with_valid_events(self, managers_up):
        resp = managers_up.post("/api/dependencies/execution-order",
                                json={"events": ["a", "b", "c"]})
        assert resp.status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.post("/api/dependencies/execution-order",
                                json={"events": ["a", "b"]}).get_json()
        assert "execution_order" in data
        assert "total_events" in data
        assert "input_events" in data
        assert data["input_events"] == ["a", "b"]


# ===========================================================================
# POST /api/smart-schedule/recommendation
# ===========================================================================

class TestSmartScheduleRecommendation:
    def test_returns_500_when_uninitialized(self, no_managers):
        resp = no_managers.post("/api/smart-schedule/recommendation",
                                json={"event_id": "ev1"})
        assert resp.status_code == 500

    def test_returns_400_when_event_id_missing(self, managers_up):
        resp = managers_up.post("/api/smart-schedule/recommendation", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_returns_200_with_valid_payload(self, managers_up):
        resp = managers_up.post("/api/smart-schedule/recommendation",
                                json={"event_id": "ev1"})
        assert resp.status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.post(
            "/api/smart-schedule/recommendation",
            json={"event_id": "ev1"}
        ).get_json()
        assert "recommendation" in data
        rec = data["recommendation"]
        for key in ("event_id", "recommended_time", "confidence_score",
                    "reasoning", "expected_duration_ms",
                    "resource_requirements", "market_conditions"):
            assert key in rec

    def test_accepts_base_time_parameter(self, managers_up):
        future = (datetime.now() + timedelta(hours=2)).isoformat()
        resp = managers_up.post(
            "/api/smart-schedule/recommendation",
            json={"event_id": "ev1", "base_time": future}
        )
        assert resp.status_code == 200


# ===========================================================================
# POST /api/smart-schedule/predict-optimal
# ===========================================================================

class TestPredictOptimalSchedule:
    _window_start = (datetime.now()).isoformat()
    _window_end = (datetime.now() + timedelta(hours=4)).isoformat()

    def _valid_payload(self):
        return {
            "events": ["ev1", "ev2"],
            "time_window_start": self._window_start,
            "time_window_end": self._window_end,
        }

    def test_returns_500_when_uninitialized(self, no_managers):
        resp = no_managers.post("/api/smart-schedule/predict-optimal",
                                json=self._valid_payload())
        assert resp.status_code == 500

    def test_returns_400_when_events_missing(self, managers_up):
        payload = {"time_window_start": self._window_start,
                   "time_window_end": self._window_end}
        assert managers_up.post("/api/smart-schedule/predict-optimal",
                                json=payload).status_code == 400

    def test_returns_400_when_window_missing(self, managers_up):
        resp = managers_up.post("/api/smart-schedule/predict-optimal",
                                json={"events": ["ev1"]})
        assert resp.status_code == 400

    def test_returns_200_with_valid_payload(self, managers_up):
        resp = managers_up.post("/api/smart-schedule/predict-optimal",
                                json=self._valid_payload())
        assert resp.status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.post("/api/smart-schedule/predict-optimal",
                                json=self._valid_payload()).get_json()
        assert "recommendations" in data
        assert "total_events" in data
        assert "time_window" in data
        assert data["total_events"] == 2

    def test_each_event_has_recommendation(self, managers_up):
        data = managers_up.post("/api/smart-schedule/predict-optimal",
                                json=self._valid_payload()).get_json()
        for event_id in ["ev1", "ev2"]:
            assert event_id in data["recommendations"]
            rec = data["recommendations"][event_id]
            assert "recommended_time" in rec
            assert "confidence_score" in rec


# ===========================================================================
# GET /api/insights/<event_id>
# ===========================================================================

class TestPerformanceInsights:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.get("/api/insights/ev1").status_code == 500

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.get("/api/insights/ev1").status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.get("/api/insights/ev1").get_json()
        assert "event_id" in data
        assert "insights" in data
        assert "timestamp" in data
        assert data["event_id"] == "ev1"

    def test_insights_contain_expected_fields(self, managers_up):
        insights = managers_up.get("/api/insights/ev1").get_json()["insights"]
        assert "average_duration_ms" in insights
        assert "success_rate" in insights


# ===========================================================================
# GET /api/insights/all
# ===========================================================================

class TestAllPerformanceInsights:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.get("/api/insights/all").status_code == 500

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.get("/api/insights/all").status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.get("/api/insights/all").get_json()
        assert "all_insights" in data
        assert "total_events" in data
        assert "timestamp" in data

    def test_empty_when_no_events(self, managers_up):
        data = managers_up.get("/api/insights/all").get_json()
        assert data["all_insights"] == {}
        assert data["total_events"] == 0


# ===========================================================================
# GET /api/executions/enhanced
# ===========================================================================

class TestEnhancedExecutionHistory:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.get("/api/executions/enhanced").status_code == 500

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.get("/api/executions/enhanced").status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.get("/api/executions/enhanced").get_json()
        assert "executions" in data
        assert "total_executions" in data
        assert "filters" in data

    def test_empty_when_no_history(self, managers_up):
        data = managers_up.get("/api/executions/enhanced").get_json()
        assert data["executions"] == []
        assert data["total_executions"] == 0

    def test_filters_contain_defaults(self, managers_up):
        filters = managers_up.get("/api/executions/enhanced").get_json()["filters"]
        assert "event_id" in filters
        assert "limit" in filters
        assert filters["limit"] == 100

    def test_limit_param_respected(self, managers_up):
        filters = managers_up.get("/api/executions/enhanced?limit=5").get_json()["filters"]
        assert filters["limit"] == 5

    def test_event_id_filter_respected(self, managers_up):
        filters = managers_up.get(
            "/api/executions/enhanced?event_id=ev1"
        ).get_json()["filters"]
        assert filters["event_id"] == "ev1"

    def test_execution_in_history_appears_in_response(self, managers_up):
        fake_status = _FakeEventStatus("completed")
        execution = _FakeEventExecution(
            event_id="ev_test",
            execution_time=datetime.now(),
            duration_ms=500.0,
            status=fake_status,
            result={"ok": True},
        )
        with patch.object(
            _api_module.enhanced_time_manager, "execution_history", [execution]
        ):
            data = managers_up.get("/api/executions/enhanced").get_json()
        assert data["total_executions"] == 1
        record = data["executions"][0]
        assert record["event_id"] == "ev_test"
        assert record["duration_ms"] == 500.0
        assert record["status"] == "completed"


# ===========================================================================
# POST /api/demo/smart-scheduling
# ===========================================================================

class TestDemoSmartScheduling:
    def test_returns_500_when_uninitialized(self, no_managers):
        assert no_managers.post("/api/demo/smart-scheduling").status_code == 500

    def test_returns_200_when_managers_up(self, managers_up):
        assert managers_up.post("/api/demo/smart-scheduling").status_code == 200

    def test_response_structure(self, managers_up):
        data = managers_up.post("/api/demo/smart-scheduling").get_json()
        assert "message" in data
        assert "sample_executions_added" in data
        assert "recommendations" in data

    def test_three_recommendations_returned(self, managers_up):
        recs = managers_up.post("/api/demo/smart-scheduling").get_json()["recommendations"]
        assert len(recs) == 3
        for event_id in ("data_refresh", "ml_analysis", "portfolio_rebalance"):
            assert event_id in recs

    def test_recommendation_fields(self, managers_up):
        recs = managers_up.post("/api/demo/smart-scheduling").get_json()["recommendations"]
        for rec in recs.values():
            assert "recommended_time" in rec
            assert "confidence_score" in rec
            assert "reasoning" in rec
            assert "expected_duration_ms" in rec


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
