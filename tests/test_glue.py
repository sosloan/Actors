#!/usr/bin/env python3
"""
Tests for core.glue — GLUE Core integration layer
==================================================

Covers:
- ServiceRegistry: register, deregister, get, find_by_tag, find_by_type
- EventBus: subscribe, unsubscribe, publish, wildcard, async_dispatch, recent_events
- Pipeline: add_step, run, step skip on None return, error handling
- PipelineManager: register, run, wire_to_bus
- HealthAggregator: probe_service, report, all probe strategies
- DataTransformer: built-in converters, custom converters, can_convert, identity
- GlueCore: composition, status, health_dict, publish/subscribe shortcuts
"""

from __future__ import annotations

import os
import sys
import time
import threading
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.glue import (
    DataTransformer,
    EventBus,
    EventPriority,
    GlueCore,
    GlueEvent,
    HealthAggregator,
    HealthReport,
    Pipeline,
    PipelineManager,
    PipelineStepStatus,
    ServiceDescriptor,
    ServiceRegistry,
    ServiceStatus,
)


# ── ServiceRegistry ───────────────────────────────────────────────────────────

class TestServiceRegistry:
    def test_register_and_get(self):
        reg = ServiceRegistry()
        obj = object()
        reg.register("svc", obj)
        assert reg.get("svc") is obj

    def test_register_returns_descriptor(self):
        reg = ServiceRegistry()
        desc = reg.register("svc", object(), service_type="time", tags=["core"])
        assert isinstance(desc, ServiceDescriptor)
        assert desc.name == "svc"
        assert desc.service_type == "time"

    def test_get_missing_returns_none(self):
        reg = ServiceRegistry()
        assert reg.get("missing") is None

    def test_descriptor_missing_returns_none(self):
        reg = ServiceRegistry()
        assert reg.descriptor("nope") is None

    def test_deregister_existing(self):
        reg = ServiceRegistry()
        reg.register("svc", object())
        assert reg.deregister("svc") is True
        assert reg.get("svc") is None

    def test_deregister_missing_returns_false(self):
        reg = ServiceRegistry()
        assert reg.deregister("ghost") is False

    def test_all_names(self):
        reg = ServiceRegistry()
        reg.register("a", object())
        reg.register("b", object())
        assert set(reg.all_names()) == {"a", "b"}

    def test_len(self):
        reg = ServiceRegistry()
        assert len(reg) == 0
        reg.register("x", object())
        assert len(reg) == 1

    def test_contains(self):
        reg = ServiceRegistry()
        reg.register("x", object())
        assert "x" in reg
        assert "y" not in reg

    def test_find_by_tag(self):
        reg = ServiceRegistry()
        reg.register("a", object(), tags=["core", "trading"])
        reg.register("b", object(), tags=["core"])
        reg.register("c", object(), tags=["ml"])
        results = reg.find_by_tag("core")
        names = {d.name for d in results}
        assert names == {"a", "b"}

    def test_find_by_type(self):
        reg = ServiceRegistry()
        reg.register("t1", object(), service_type="time")
        reg.register("t2", object(), service_type="time")
        reg.register("ml", object(), service_type="ml")
        results = reg.find_by_type("time")
        assert len(results) == 2

    def test_re_register_replaces(self):
        reg = ServiceRegistry()
        obj1, obj2 = object(), object()
        reg.register("svc", obj1)
        reg.register("svc", obj2)
        assert reg.get("svc") is obj2

    def test_thread_safety(self):
        reg = ServiceRegistry()
        errors = []

        def worker(i):
            try:
                reg.register(f"svc_{i}", object())
                _ = reg.get(f"svc_{i}")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []


# ── EventBus ──────────────────────────────────────────────────────────────────

class TestEventBus:
    def test_subscribe_and_receive(self):
        bus = EventBus()
        received = []
        bus.subscribe("topic", lambda e: received.append(e))
        bus.publish("topic", {"data": 42})
        assert len(received) == 1
        assert received[0].payload == {"data": 42}

    def test_publish_returns_event(self):
        bus = EventBus()
        event = bus.publish("t", "hello")
        assert isinstance(event, GlueEvent)
        assert event.topic == "t"
        assert event.payload == "hello"

    def test_event_id_unique(self):
        bus = EventBus()
        e1 = bus.publish("t", 1)
        e2 = bus.publish("t", 2)
        assert e1.event_id != e2.event_id

    def test_wildcard_subscriber(self):
        bus = EventBus()
        received = []
        bus.subscribe("*", lambda e: received.append(e.topic))
        bus.publish("alpha", None)
        bus.publish("beta", None)
        assert "alpha" in received
        assert "beta" in received

    def test_no_subscriber_no_error(self):
        bus = EventBus()
        bus.publish("orphan_topic", "data")  # should not raise

    def test_unsubscribe(self):
        bus = EventBus()
        received = []
        handler = lambda e: received.append(e)
        bus.subscribe("t", handler)
        bus.unsubscribe("t", handler)
        bus.publish("t", "x")
        assert received == []

    def test_unsubscribe_missing_returns_false(self):
        bus = EventBus()
        assert bus.unsubscribe("t", lambda e: None) is False

    def test_handler_exception_does_not_propagate(self):
        bus = EventBus()
        bus.subscribe("boom", lambda e: 1 / 0)
        bus.publish("boom", "trigger")  # must not raise

    def test_multiple_handlers_same_topic(self):
        bus = EventBus()
        results = []
        bus.subscribe("t", lambda e: results.append(1))
        bus.subscribe("t", lambda e: results.append(2))
        bus.publish("t", None)
        assert sorted(results) == [1, 2]

    def test_recent_events(self):
        bus = EventBus()
        bus.publish("a", 1)
        bus.publish("b", 2)
        bus.publish("a", 3)
        all_events = bus.recent_events()
        assert len(all_events) == 3
        a_events = bus.recent_events(topic="a")
        assert len(a_events) == 2

    def test_recent_events_limit(self):
        bus = EventBus()
        for i in range(10):
            bus.publish("t", i)
        assert len(bus.recent_events(limit=5)) == 5

    def test_handler_count(self):
        bus = EventBus()
        bus.subscribe("t", lambda e: None)
        bus.subscribe("t", lambda e: None)
        assert bus.handler_count("t") == 2

    def test_topics(self):
        bus = EventBus()
        bus.subscribe("topic_a", lambda e: None)
        bus.subscribe("topic_b", lambda e: None)
        assert set(bus.topics()) >= {"topic_a", "topic_b"}

    def test_async_dispatch(self):
        bus = EventBus(async_dispatch=True)
        received = []
        lock = threading.Lock()

        def handler(e):
            with lock:
                received.append(e.payload)

        bus.subscribe("t", handler)
        bus.publish("t", "async_value")
        # give threads a moment
        deadline = time.time() + 2.0
        while time.time() < deadline and not received:
            time.sleep(0.01)
        assert received == ["async_value"]

    def test_priority_stored(self):
        bus = EventBus()
        event = bus.publish("t", None, priority=EventPriority.CRITICAL)
        assert event.priority == EventPriority.CRITICAL

    def test_correlation_id_stored(self):
        bus = EventBus()
        event = bus.publish("t", None, correlation_id="abc-123")
        assert event.correlation_id == "abc-123"


# ── Pipeline ──────────────────────────────────────────────────────────────────

class TestPipeline:
    def test_basic_run(self):
        pipe = Pipeline("double")
        pipe.add_step("x2", lambda d: d * 2)
        result = pipe.run(5)
        assert result.output_data == 10
        assert result.succeeded is True

    def test_chained_steps(self):
        pipe = Pipeline("chain")
        pipe.add_step("add1", lambda d: d + 1)
        pipe.add_step("mul2", lambda d: d * 2)
        result = pipe.run(3)
        assert result.output_data == 8  # (3+1)*2

    def test_step_returns_none_halts(self):
        pipe = Pipeline("halt_on_none")
        pipe.add_step("return_none", lambda d: None)
        pipe.add_step("never_reached", lambda d: d + 1)
        result = pipe.run(10)
        assert result.step_statuses["return_none"] == PipelineStepStatus.SKIPPED
        assert "never_reached" not in result.step_statuses

    def test_step_error_halts(self):
        pipe = Pipeline("error")
        pipe.add_step("boom", lambda d: 1 / 0)
        pipe.add_step("never", lambda d: d)
        result = pipe.run(0)
        assert result.succeeded is False
        assert "boom" in result.errors
        assert "never" not in result.step_statuses

    def test_disabled_step_skipped(self):
        pipe = Pipeline("skip")
        pipe.add_step("active", lambda d: d + 1)
        pipe.add_step("skipped", lambda d: d + 100, enabled=False)
        result = pipe.run(0)
        assert result.output_data == 1
        assert result.step_statuses["skipped"] == PipelineStepStatus.SKIPPED

    def test_empty_pipeline(self):
        pipe = Pipeline("empty")
        result = pipe.run("data")
        assert result.output_data == "data"
        assert result.succeeded is True

    def test_duration_recorded(self):
        pipe = Pipeline("timed")
        pipe.add_step("sleep", lambda d: d)
        result = pipe.run(None)
        assert result.duration_ms >= 0

    def test_step_names(self):
        pipe = Pipeline("named")
        pipe.add_step("a", lambda d: d)
        pipe.add_step("b", lambda d: d)
        assert pipe.step_names == ["a", "b"]

    def test_chaining_returns_self(self):
        pipe = Pipeline("chain")
        ret = pipe.add_step("s", lambda d: d)
        assert ret is pipe


# ── PipelineManager ───────────────────────────────────────────────────────────

class TestPipelineManager:
    def test_register_and_run(self):
        pm = PipelineManager()
        pipe = Pipeline("p")
        pipe.add_step("inc", lambda d: d + 1)
        pm.register_pipeline(pipe)
        result = pm.run("p", 4)
        assert result.output_data == 5

    def test_run_missing_raises(self):
        pm = PipelineManager()
        with pytest.raises(KeyError):
            pm.run("ghost", None)

    def test_pipeline_names(self):
        pm = PipelineManager()
        pm.register_pipeline(Pipeline("x"))
        pm.register_pipeline(Pipeline("y"))
        assert set(pm.pipeline_names()) == {"x", "y"}

    def test_wire_to_bus(self):
        bus = EventBus()
        pm = PipelineManager(bus=bus)
        pipe = Pipeline("triple")
        pipe.add_step("x3", lambda d: d * 3)
        pm.register_pipeline(pipe)

        results = []
        bus.subscribe("tripled", lambda e: results.append(e.payload))
        pm.wire_to_bus("triple", "raw_number", result_topic="tripled")

        bus.publish("raw_number", 7)
        assert results == [21]

    def test_wire_without_bus_raises(self):
        pm = PipelineManager(bus=None)
        pm.register_pipeline(Pipeline("p"))
        with pytest.raises(RuntimeError):
            pm.wire_to_bus("p", "topic")


# ── HealthAggregator ──────────────────────────────────────────────────────────

class _HealthyService:
    def health(self):
        return {"status": "healthy", "version": "1.0"}

class _DegradedService:
    def health(self):
        return {"status": "degraded"}

class _UnhealthyService:
    def health(self):
        return {"status": "unhealthy"}

class _BooleanHealthService:
    def is_healthy(self):
        return True

class _BrokenService:
    def health(self):
        raise RuntimeError("DB down")

class _NoHealthService:
    pass


class TestHealthAggregator:
    def _reg_with(self, name, instance, **kwargs):
        reg = ServiceRegistry()
        reg.register(name, instance, **kwargs)
        return reg

    def test_healthy_via_health_dict(self):
        reg = self._reg_with("svc", _HealthyService())
        agg = HealthAggregator(reg)
        sr = agg.probe_service("svc")
        assert sr.status == ServiceStatus.HEALTHY
        assert sr.details.get("version") == "1.0"

    def test_degraded_via_health_dict(self):
        reg = self._reg_with("svc", _DegradedService())
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.DEGRADED

    def test_unhealthy_via_health_dict(self):
        reg = self._reg_with("svc", _UnhealthyService())
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.UNHEALTHY

    def test_healthy_via_is_healthy(self):
        reg = self._reg_with("svc", _BooleanHealthService())
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.HEALTHY

    def test_unhealthy_on_exception(self):
        reg = self._reg_with("svc", _BrokenService())
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.UNHEALTHY
        assert "health_error" in sr.details or "get_health_error" in sr.details or sr.details

    def test_unknown_without_health_interface(self):
        reg = self._reg_with("svc", _NoHealthService())
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.UNKNOWN

    def test_explicit_probe_callable(self):
        reg = ServiceRegistry()
        reg.register("svc", object(), health_probe=lambda: True)
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.HEALTHY

    def test_explicit_probe_callable_failing(self):
        reg = ServiceRegistry()
        reg.register("svc", object(), health_probe=lambda: False)
        sr = HealthAggregator(reg).probe_service("svc")
        assert sr.status == ServiceStatus.UNHEALTHY

    def test_probe_missing_service(self):
        reg = ServiceRegistry()
        sr = HealthAggregator(reg).probe_service("ghost")
        assert sr.status == ServiceStatus.UNKNOWN

    def test_report_all_healthy(self):
        reg = ServiceRegistry()
        reg.register("a", _HealthyService())
        reg.register("b", _HealthyService())
        report = HealthAggregator(reg).report()
        assert report.overall_status == "healthy"
        assert report.healthy_count == 2
        assert report.unhealthy_count == 0

    def test_report_with_unhealthy(self):
        reg = ServiceRegistry()
        reg.register("a", _HealthyService())
        reg.register("b", _UnhealthyService())
        report = HealthAggregator(reg).report()
        assert report.overall_status == "unhealthy"

    def test_report_with_degraded(self):
        reg = ServiceRegistry()
        reg.register("a", _HealthyService())
        reg.register("b", _DegradedService())
        report = HealthAggregator(reg).report()
        assert report.overall_status == "degraded"

    def test_report_empty_registry(self):
        reg = ServiceRegistry()
        report = HealthAggregator(reg).report()
        assert report.overall_status == "healthy"
        assert report.services == []


# ── DataTransformer ───────────────────────────────────────────────────────────

class TestDataTransformer:
    def test_identity_conversion(self):
        dt = DataTransformer()
        obj = {"x": 1}
        assert dt.convert(obj, "dict", "dict") is obj

    def test_builtin_bar_to_dict(self):
        from core.backtest_engine import Bar
        bar = Bar(
            timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
            symbol="AAPL", open=100.0, high=105.0, low=99.0, close=103.0, volume=1000.0,
        )
        dt = DataTransformer()
        d = dt.convert(bar, "bar", "dict")
        assert d["symbol"] == "AAPL"
        assert d["close"] == 103.0

    def test_builtin_dict_to_bar(self):
        dt = DataTransformer()
        d = {"symbol": "TSLA", "open": 200.0, "high": 210.0,
             "low": 195.0, "close": 205.0, "volume": 5000.0}
        result = dt.convert(d, "dict", "bar")
        assert result["symbol"] == "TSLA"
        assert result["close"] == 205.0

    def test_builtin_dict_to_trading_signal(self):
        dt = DataTransformer()
        d = {"symbol": "BTC", "action": "BUY", "confidence": 0.9}
        result = dt.convert(d, "dict", "trading_signal")
        assert result["symbol"] == "BTC"
        assert result["confidence"] == 0.9

    def test_health_report_to_dict(self):
        from core.glue import HealthReport, ServiceHealthReport
        report = HealthReport(
            overall_status="healthy",
            services=[ServiceHealthReport(name="svc", status=ServiceStatus.HEALTHY)],
            healthy_count=1,
        )
        dt = DataTransformer()
        d = dt.convert(report, "health_report", "dict")
        assert d["overall_status"] == "healthy"
        assert d["services"][0]["name"] == "svc"

    def test_custom_converter(self):
        dt = DataTransformer()
        dt.register("raw", "upper", lambda s: s.upper())
        result = dt.convert("hello", "raw", "upper")
        assert result == "HELLO"

    def test_convert_missing_raises(self):
        dt = DataTransformer()
        with pytest.raises(KeyError):
            dt.convert("x", "unknown_a", "unknown_b")

    def test_can_convert_true(self):
        dt = DataTransformer()
        assert dt.can_convert("bar", "dict") is True
        assert dt.can_convert("dict", "dict") is True

    def test_can_convert_false(self):
        dt = DataTransformer()
        assert dt.can_convert("foobar", "bazqux") is False


# ── GlueCore ──────────────────────────────────────────────────────────────────

class TestGlueCore:
    def test_instantiation(self):
        glue = GlueCore()
        assert glue.registry is not None
        assert glue.bus is not None
        assert glue.pipelines is not None
        assert glue.health is not None
        assert glue.transformer is not None

    def test_status_keys(self):
        glue = GlueCore()
        s = glue.status()
        assert "started_at" in s
        assert "uptime_seconds" in s
        assert "registered_services" in s
        assert "registered_pipelines" in s
        assert "event_topics" in s

    def test_uptime_increases(self):
        glue = GlueCore()
        time.sleep(0.05)
        assert glue.status()["uptime_seconds"] >= 0.05

    def test_publish_shortcut(self):
        glue = GlueCore()
        received = []
        glue.subscribe("test", lambda e: received.append(e.payload))
        glue.publish("test", "value")
        assert received == ["value"]

    def test_run_pipeline_shortcut(self):
        glue = GlueCore()
        pipe = Pipeline("double")
        pipe.add_step("x2", lambda d: d * 2)
        glue.pipelines.register_pipeline(pipe)
        result = glue.run_pipeline("double", 6)
        assert result.output_data == 12

    def test_health_dict_empty(self):
        glue = GlueCore()
        hd = glue.health_dict()
        assert hd["overall_status"] == "healthy"
        assert hd["services"] == []

    def test_health_dict_with_services(self):
        glue = GlueCore()
        glue.registry.register("ok", _HealthyService())
        hd = glue.health_dict()
        assert hd["healthy_count"] == 1

    def test_integration_bus_pipeline(self):
        """Events flow through bus → pipeline → result topic."""
        glue = GlueCore()
        pipe = Pipeline("negate")
        pipe.add_step("neg", lambda d: -d)
        glue.pipelines.register_pipeline(pipe)

        results = []
        glue.subscribe("negated", lambda e: results.append(e.payload))
        glue.pipelines.wire_to_bus("negate", "raw_number", result_topic="negated")
        glue.publish("raw_number", 5)

        assert results == [-5]

    def test_status_shows_registered_services(self):
        glue = GlueCore()
        glue.registry.register("my_svc", object())
        assert "my_svc" in glue.status()["registered_services"]

    def test_status_shows_registered_pipelines(self):
        glue = GlueCore()
        glue.pipelines.register_pipeline(Pipeline("my_pipe"))
        assert "my_pipe" in glue.status()["registered_pipelines"]
