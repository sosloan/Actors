#!/usr/bin/env python3
"""
🔗 GLUE Core — General Layer for Unified Execution
===================================================

Central integration layer for the ACTORS ecosystem.  It knits together the
independent subsystems (time management, ML pipeline, DeFi integration,
portfolio optimisation, backtest engine, database, geospatial, embeddings)
into a cohesive runtime without forcing them into a monolith.

Key components
--------------
- :class:`ServiceRegistry`   – register, discover, and deregister subsystem handles
- :class:`EventBus`          – in-process publish/subscribe for cross-component events
- :class:`PipelineManager`   – declarative data-transformation pipelines
- :class:`HealthAggregator`  – roll-up health across every registered service
- :class:`DataTransformer`   – canonical format conversions between component schemas
- :class:`GlueCore`          – master orchestrator; composes all of the above

Usage (minimal)
---------------
    from core.glue import GlueCore

    glue = GlueCore()
    glue.registry.register("time_manager", my_time_manager)
    glue.registry.register("ml_pipeline", my_ml_pipeline)

    # subscribe to cross-cutting events
    glue.bus.subscribe("trade_signal", handle_signal)

    # publish from any subsystem
    glue.bus.publish("trade_signal", {"symbol": "AAPL", "action": "BUY"})

    # check roll-up health
    report = glue.health.report()
    print(report.overall_status)   # "healthy" | "degraded" | "unhealthy"
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── Enumerations ──────────────────────────────────────────────────────────────

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class PipelineStepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class ServiceDescriptor:
    """Metadata stored alongside each registered service handle."""
    name: str
    instance: Any
    service_type: str = "generic"
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    health_probe: Optional[Callable[[], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GlueEvent:
    """An in-process event envelope."""
    topic: str
    payload: Any
    source: str = "unknown"
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = ""
    correlation_id: str = ""

    def __post_init__(self) -> None:
        if not self.event_id:
            import uuid
            self.event_id = str(uuid.uuid4())


@dataclass
class PipelineStep:
    """A single named transform inside a :class:`Pipeline`."""
    name: str
    transform: Callable[[Any], Any]
    enabled: bool = True
    description: str = ""


@dataclass
class PipelineResult:
    """The outcome of executing a :class:`Pipeline`."""
    pipeline_name: str
    input_data: Any
    output_data: Any
    step_statuses: Dict[str, PipelineStepStatus] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    duration_ms: float = 0.0
    succeeded: bool = True
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ServiceHealthReport:
    """Per-service health snapshot."""
    name: str
    status: ServiceStatus
    latency_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class HealthReport:
    """System-wide health roll-up."""
    overall_status: str  # "healthy" | "degraded" | "unhealthy"
    services: List[ServiceHealthReport] = field(default_factory=list)
    healthy_count: int = 0
    degraded_count: int = 0
    unhealthy_count: int = 0
    unknown_count: int = 0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ── ServiceRegistry ───────────────────────────────────────────────────────────

class ServiceRegistry:
    """Register and discover ACTORS subsystem handles.

    Thread-safe.  Services may expose an optional ``health_probe`` callable
    (``() -> bool``) that :class:`HealthAggregator` calls when building
    a health report.
    """

    def __init__(self) -> None:
        self._services: Dict[str, ServiceDescriptor] = {}
        self._lock = threading.RLock()

    # ── public API ────────────────────────────────────────────────────────────

    def register(
        self,
        name: str,
        instance: Any,
        *,
        service_type: str = "generic",
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        health_probe: Optional[Callable[[], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ServiceDescriptor:
        """Register *instance* under *name*.

        Re-registering an existing name replaces the old entry.
        """
        desc = ServiceDescriptor(
            name=name,
            instance=instance,
            service_type=service_type,
            version=version,
            tags=tags or [],
            health_probe=health_probe,
            metadata=metadata or {},
        )
        with self._lock:
            self._services[name] = desc
        logger.info("🔗 [Registry] registered service '%s' (type=%s)", name, service_type)
        return desc

    def deregister(self, name: str) -> bool:
        """Remove a service by name.  Returns *True* if it existed."""
        with self._lock:
            if name in self._services:
                del self._services[name]
                logger.info("🔗 [Registry] deregistered service '%s'", name)
                return True
        return False

    def get(self, name: str) -> Any:
        """Return the raw service instance, or *None* if not found."""
        with self._lock:
            desc = self._services.get(name)
        return desc.instance if desc else None

    def descriptor(self, name: str) -> Optional[ServiceDescriptor]:
        """Return the full :class:`ServiceDescriptor`, or *None*."""
        with self._lock:
            return self._services.get(name)

    def all_names(self) -> List[str]:
        """Return names of every registered service."""
        with self._lock:
            return list(self._services.keys())

    def find_by_tag(self, tag: str) -> List[ServiceDescriptor]:
        """Return all descriptors whose tag list contains *tag*."""
        with self._lock:
            return [d for d in self._services.values() if tag in d.tags]

    def find_by_type(self, service_type: str) -> List[ServiceDescriptor]:
        """Return all descriptors with matching *service_type*."""
        with self._lock:
            return [d for d in self._services.values() if d.service_type == service_type]

    def __len__(self) -> int:
        with self._lock:
            return len(self._services)

    def __contains__(self, name: str) -> bool:
        with self._lock:
            return name in self._services


# ── EventBus ──────────────────────────────────────────────────────────────────

class EventBus:
    """Lightweight in-process publish/subscribe bus.

    Handlers are called synchronously in the publisher's thread unless
    *async_dispatch* is *True*, in which case each handler is dispatched in its
    own :class:`threading.Thread`.

    Example::

        bus = EventBus()
        bus.subscribe("trade_signal", lambda e: print(e.payload))
        bus.publish("trade_signal", {"symbol": "AAPL", "action": "BUY"})
    """

    def __init__(self, async_dispatch: bool = False) -> None:
        self._handlers: Dict[str, List[Callable[[GlueEvent], None]]] = defaultdict(list)
        self._wildcard: List[Callable[[GlueEvent], None]] = []
        self._lock = threading.RLock()
        self._async_dispatch = async_dispatch
        self._event_log: List[GlueEvent] = []
        self._max_log_size: int = 1_000

    # ── subscriptions ────────────────────────────────────────────────────────

    def subscribe(
        self,
        topic: str,
        handler: Callable[[GlueEvent], None],
    ) -> None:
        """Subscribe *handler* to *topic*.

        Use ``topic="*"`` to receive every event (wildcard).
        """
        with self._lock:
            if topic == "*":
                self._wildcard.append(handler)
            else:
                self._handlers[topic].append(handler)
        logger.debug("🔗 [EventBus] subscribed handler to topic '%s'", topic)

    def unsubscribe(
        self,
        topic: str,
        handler: Callable[[GlueEvent], None],
    ) -> bool:
        """Remove *handler* from *topic*.  Returns *True* if it was registered."""
        with self._lock:
            target = self._wildcard if topic == "*" else self._handlers.get(topic, [])
            if handler in target:
                target.remove(handler)
                return True
        return False

    # ── publishing ───────────────────────────────────────────────────────────

    def publish(
        self,
        topic: str,
        payload: Any,
        *,
        source: str = "unknown",
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str = "",
    ) -> GlueEvent:
        """Publish *payload* on *topic* and invoke all matching handlers.

        Returns the :class:`GlueEvent` that was dispatched.
        """
        event = GlueEvent(
            topic=topic,
            payload=payload,
            source=source,
            priority=priority,
            correlation_id=correlation_id,
        )
        with self._lock:
            handlers = list(self._handlers.get(topic, [])) + list(self._wildcard)
            self._event_log.append(event)
            if len(self._event_log) > self._max_log_size:
                self._event_log = self._event_log[-self._max_log_size:]

        self._dispatch(event, handlers)
        return event

    def _dispatch(
        self,
        event: GlueEvent,
        handlers: List[Callable[[GlueEvent], None]],
    ) -> None:
        for handler in handlers:
            if self._async_dispatch:
                t = threading.Thread(
                    target=self._safe_call,
                    args=(handler, event),
                    daemon=True,
                )
                t.start()
            else:
                self._safe_call(handler, event)

    @staticmethod
    def _safe_call(
        handler: Callable[[GlueEvent], None],
        event: GlueEvent,
    ) -> None:
        try:
            handler(event)
        except Exception as exc:
            logger.error(
                "🔗 [EventBus] handler %s raised on topic '%s': %s",
                handler,
                event.topic,
                exc,
                exc_info=True,
            )

    # ── introspection ────────────────────────────────────────────────────────

    def recent_events(self, topic: Optional[str] = None, limit: int = 50) -> List[GlueEvent]:
        """Return the most recent events, optionally filtered by *topic*."""
        with self._lock:
            events = list(self._event_log)
        if topic:
            events = [e for e in events if e.topic == topic]
        return events[-limit:]

    def handler_count(self, topic: str) -> int:
        """Return the number of handlers registered on *topic*."""
        with self._lock:
            return len(self._handlers.get(topic, []))

    def topics(self) -> List[str]:
        """Return all topics that have at least one subscriber."""
        with self._lock:
            return [t for t, h in self._handlers.items() if h]


# ── Pipeline ──────────────────────────────────────────────────────────────────

class Pipeline:
    """An ordered sequence of named transforms applied to data.

    Steps returning *None* halt execution of subsequent steps (the last
    non-None value is propagated instead).

    Example::

        pipe = Pipeline("normalise_signal")
        pipe.add_step("parse",    lambda d: d.strip())
        pipe.add_step("validate", lambda d: d if d else None)
        result = pipe.run(raw_data)
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: List[PipelineStep] = []

    def add_step(
        self,
        name: str,
        transform: Callable[[Any], Any],
        *,
        enabled: bool = True,
        description: str = "",
    ) -> "Pipeline":
        """Append a step.  Returns *self* for chaining."""
        self._steps.append(
            PipelineStep(name=name, transform=transform, enabled=enabled, description=description)
        )
        return self

    def run(self, data: Any) -> PipelineResult:
        """Execute all enabled steps in order and return a :class:`PipelineResult`."""
        start = time.perf_counter()
        statuses: Dict[str, PipelineStepStatus] = {}
        errors: Dict[str, str] = {}
        current = data

        for step in self._steps:
            if not step.enabled:
                statuses[step.name] = PipelineStepStatus.SKIPPED
                continue
            statuses[step.name] = PipelineStepStatus.RUNNING
            try:
                result = step.transform(current)
                if result is None:
                    statuses[step.name] = PipelineStepStatus.SKIPPED
                    logger.debug(
                        "🔗 [Pipeline:%s] step '%s' returned None — skipping remainder",
                        self.name, step.name,
                    )
                    break
                current = result
                statuses[step.name] = PipelineStepStatus.SUCCESS
            except Exception as exc:
                statuses[step.name] = PipelineStepStatus.FAILED
                errors[step.name] = str(exc)
                logger.error(
                    "🔗 [Pipeline:%s] step '%s' failed: %s",
                    self.name, step.name, exc, exc_info=True,
                )
                break

        duration_ms = (time.perf_counter() - start) * 1_000
        succeeded = all(
            s in (PipelineStepStatus.SUCCESS, PipelineStepStatus.SKIPPED)
            for s in statuses.values()
        )
        return PipelineResult(
            pipeline_name=self.name,
            input_data=data,
            output_data=current,
            step_statuses=statuses,
            errors=errors,
            duration_ms=round(duration_ms, 3),
            succeeded=succeeded,
        )

    @property
    def step_names(self) -> List[str]:
        return [s.name for s in self._steps]


# ── PipelineManager ───────────────────────────────────────────────────────────

class PipelineManager:
    """Registry and executor for named :class:`Pipeline` objects.

    Pipelines can be wired to :class:`EventBus` topics so that a published
    event automatically triggers the relevant pipeline.
    """

    def __init__(self, bus: Optional["EventBus"] = None) -> None:
        self._pipelines: Dict[str, Pipeline] = {}
        self._lock = threading.RLock()
        self._bus = bus

    def register_pipeline(self, pipeline: Pipeline) -> None:
        """Add or replace a pipeline."""
        with self._lock:
            self._pipelines[pipeline.name] = pipeline
        logger.info("🔗 [PipelineManager] registered pipeline '%s'", pipeline.name)

    def get_pipeline(self, name: str) -> Optional[Pipeline]:
        with self._lock:
            return self._pipelines.get(name)

    def run(self, name: str, data: Any) -> PipelineResult:
        """Execute the named pipeline.  Raises *KeyError* if not found."""
        pipeline = self.get_pipeline(name)
        if pipeline is None:
            raise KeyError(f"Pipeline '{name}' not found in PipelineManager")
        logger.debug("🔗 [PipelineManager] running pipeline '%s'", name)
        return pipeline.run(data)

    def wire_to_bus(
        self,
        pipeline_name: str,
        topic: str,
        result_topic: Optional[str] = None,
    ) -> None:
        """Subscribe *pipeline_name* to *topic* on the event bus.

        When an event arrives the pipeline is run with ``event.payload`` as
        input.  If *result_topic* is given, the pipeline output is published
        back to the bus on that topic.
        """
        if self._bus is None:
            raise RuntimeError("PipelineManager has no EventBus configured")

        def _handler(event: GlueEvent) -> None:
            result = self.run(pipeline_name, event.payload)
            if result_topic and result.succeeded:
                self._bus.publish(
                    result_topic,
                    result.output_data,
                    source=f"pipeline:{pipeline_name}",
                )

        self._bus.subscribe(topic, _handler)
        logger.info(
            "🔗 [PipelineManager] wired pipeline '%s' → topic '%s'",
            pipeline_name, topic,
        )

    def pipeline_names(self) -> List[str]:
        with self._lock:
            return list(self._pipelines.keys())


# ── HealthAggregator ──────────────────────────────────────────────────────────

class HealthAggregator:
    """Probe every registered service and roll up a system-wide health report.

    Services expose health either through:
    1. The ``health_probe`` callable stored in :class:`ServiceDescriptor`, or
    2. A ``health()`` / ``is_healthy()`` / ``get_health()`` method on the
       service instance itself.

    Any service without a detectable health interface is reported as UNKNOWN.
    """

    def __init__(self, registry: ServiceRegistry) -> None:
        self._registry = registry

    # ── public API ────────────────────────────────────────────────────────────

    def probe_service(self, name: str) -> ServiceHealthReport:
        """Return a :class:`ServiceHealthReport` for a single service."""
        desc = self._registry.descriptor(name)
        if desc is None:
            return ServiceHealthReport(name=name, status=ServiceStatus.UNKNOWN)

        start = time.perf_counter()
        status, details = self._check(desc)
        latency_ms = (time.perf_counter() - start) * 1_000

        return ServiceHealthReport(
            name=name,
            status=status,
            latency_ms=round(latency_ms, 3),
            details=details,
        )

    def report(self) -> HealthReport:
        """Probe all services and return a rolled-up :class:`HealthReport`."""
        service_reports: List[ServiceHealthReport] = []
        counts: Dict[ServiceStatus, int] = defaultdict(int)

        for name in self._registry.all_names():
            sr = self.probe_service(name)
            service_reports.append(sr)
            counts[sr.status] += 1

        healthy = counts[ServiceStatus.HEALTHY]
        degraded = counts[ServiceStatus.DEGRADED]
        unhealthy = counts[ServiceStatus.UNHEALTHY]
        unknown = counts[ServiceStatus.UNKNOWN]

        if unhealthy > 0:
            overall = "unhealthy"
        elif degraded > 0 or unknown > 0:
            overall = "degraded"
        else:
            overall = "healthy"

        return HealthReport(
            overall_status=overall,
            services=service_reports,
            healthy_count=healthy,
            degraded_count=degraded,
            unhealthy_count=unhealthy,
            unknown_count=unknown,
        )

    # ── internals ────────────────────────────────────────────────────────────

    @staticmethod
    def _check(desc: ServiceDescriptor) -> Tuple[ServiceStatus, Dict[str, Any]]:
        details: Dict[str, Any] = {}

        # 1. Explicit probe callable
        if desc.health_probe is not None:
            try:
                ok = desc.health_probe()
                return (ServiceStatus.HEALTHY if ok else ServiceStatus.UNHEALTHY), details
            except Exception as exc:
                details["probe_error"] = str(exc)
                return ServiceStatus.UNHEALTHY, details

        instance = desc.instance
        if instance is None:
            return ServiceStatus.UNKNOWN, details

        # 2. health() method
        for method_name in ("health", "get_health"):
            method = getattr(instance, method_name, None)
            if callable(method):
                try:
                    result = method()
                    if isinstance(result, bool):
                        return (ServiceStatus.HEALTHY if result else ServiceStatus.UNHEALTHY), details
                    if isinstance(result, dict):
                        details.update(result)
                        raw_status = result.get("status", "")
                        if raw_status in ("healthy", "ok", "up"):
                            return ServiceStatus.HEALTHY, details
                        if raw_status in ("degraded", "warning"):
                            return ServiceStatus.DEGRADED, details
                        if raw_status in ("unhealthy", "error", "down"):
                            return ServiceStatus.UNHEALTHY, details
                        return ServiceStatus.UNKNOWN, details
                except Exception as exc:
                    details[f"{method_name}_error"] = str(exc)
                    return ServiceStatus.UNHEALTHY, details

        # 3. is_healthy() boolean
        is_healthy = getattr(instance, "is_healthy", None)
        if callable(is_healthy):
            try:
                ok = is_healthy()
                return (ServiceStatus.HEALTHY if ok else ServiceStatus.UNHEALTHY), details
            except Exception as exc:
                details["is_healthy_error"] = str(exc)
                return ServiceStatus.UNHEALTHY, details

        return ServiceStatus.UNKNOWN, details


# ── DataTransformer ───────────────────────────────────────────────────────────

class DataTransformer:
    """Canonical conversions between ACTORS component data formats.

    Custom converters are registered as ``(source_type, target_type)`` pairs.
    Built-in converters handle the most common cross-component translations.
    """

    def __init__(self) -> None:
        self._converters: Dict[Tuple[str, str], Callable[[Any], Any]] = {}
        self._register_builtins()

    # ── public API ────────────────────────────────────────────────────────────

    def register(
        self,
        source_type: str,
        target_type: str,
        converter: Callable[[Any], Any],
    ) -> None:
        """Register a custom converter for ``(source_type, target_type)``."""
        self._converters[(source_type, target_type)] = converter
        logger.debug(
            "🔗 [DataTransformer] registered converter %s → %s", source_type, target_type
        )

    def convert(self, data: Any, source_type: str, target_type: str) -> Any:
        """Convert *data* from *source_type* to *target_type*.

        Raises :class:`KeyError` if no converter is registered for the pair.
        """
        if source_type == target_type:
            return data
        key = (source_type, target_type)
        converter = self._converters.get(key)
        if converter is None:
            raise KeyError(
                f"No converter registered for ({source_type!r} → {target_type!r}). "
                f"Available: {[f'{s}→{t}' for s, t in self._converters]}"
            )
        return converter(data)

    def can_convert(self, source_type: str, target_type: str) -> bool:
        """Return *True* if a converter exists for the given pair."""
        return (source_type, target_type) in self._converters or source_type == target_type

    # ── built-in converters ───────────────────────────────────────────────────

    def _register_builtins(self) -> None:
        # trading_signal → dict
        self.register("trading_signal", "dict", self._trading_signal_to_dict)
        # dict → trading_signal stub (minimal round-trip)
        self.register("dict", "trading_signal", self._dict_to_trading_signal)
        # bar → dict
        self.register("bar", "dict", self._bar_to_dict)
        # dict → bar
        self.register("dict", "bar", self._dict_to_bar)
        # health_report → dict
        self.register("health_report", "dict", self._health_report_to_dict)

    @staticmethod
    def _trading_signal_to_dict(signal: Any) -> Dict[str, Any]:
        if hasattr(signal, "__dict__"):
            return {
                k: (v.value if isinstance(v, Enum) else v)
                for k, v in signal.__dict__.items()
            }
        if hasattr(signal, "_asdict"):
            return dict(signal._asdict())
        return dict(signal) if isinstance(signal, dict) else {"raw": str(signal)}

    @staticmethod
    def _dict_to_trading_signal(data: Dict[str, Any]) -> Dict[str, Any]:
        # Return a normalised dict usable as a lightweight trading signal stub.
        return {
            "symbol": data.get("symbol", ""),
            "action": data.get("action", data.get("signal_type", "HOLD")),
            "confidence": float(data.get("confidence", 0.5)),
            "timestamp": data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "metadata": data.get("metadata", {}),
        }

    @staticmethod
    def _bar_to_dict(bar: Any) -> Dict[str, Any]:
        keys = ("timestamp", "symbol", "open", "high", "low", "close", "volume")
        if hasattr(bar, "__dict__"):
            return {k: getattr(bar, k, None) for k in keys}
        return dict(bar) if isinstance(bar, dict) else {"raw": str(bar)}

    @staticmethod
    def _dict_to_bar(data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "timestamp": data.get("timestamp", datetime.now(timezone.utc)),
            "symbol": data.get("symbol", ""),
            "open": float(data.get("open", 0.0)),
            "high": float(data.get("high", 0.0)),
            "low": float(data.get("low", 0.0)),
            "close": float(data.get("close", 0.0)),
            "volume": float(data.get("volume", 0.0)),
        }

    @staticmethod
    def _health_report_to_dict(report: HealthReport) -> Dict[str, Any]:
        return {
            "overall_status": report.overall_status,
            "healthy_count": report.healthy_count,
            "degraded_count": report.degraded_count,
            "unhealthy_count": report.unhealthy_count,
            "unknown_count": report.unknown_count,
            "generated_at": report.generated_at.isoformat(),
            "services": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "latency_ms": s.latency_ms,
                    "details": s.details,
                }
                for s in report.services
            ],
        }


# ── GlueCore ──────────────────────────────────────────────────────────────────

class GlueCore:
    """Master orchestrator for the ACTORS integration layer.

    Composes :class:`ServiceRegistry`, :class:`EventBus`,
    :class:`PipelineManager`, :class:`HealthAggregator`, and
    :class:`DataTransformer` into a single cohesive runtime object.

    Typical life-cycle::

        glue = GlueCore()

        # Register subsystems
        glue.registry.register("time_manager",  tm, service_type="time")
        glue.registry.register("ml_pipeline",   mlp, service_type="ml")
        glue.registry.register("defi_engine",   defi, service_type="defi")

        # Wire up cross-cutting pipelines
        pipe = Pipeline("enrich_signal")
        pipe.add_step("normalise", normalise_fn)
        pipe.add_step("ml_score",  ml_score_fn)
        glue.pipelines.register_pipeline(pipe)
        glue.pipelines.wire_to_bus("enrich_signal", "raw_signal", result_topic="enriched_signal")

        # Publish events from any subsystem
        glue.bus.publish("raw_signal", signal_data, source="speech_connector")

        # Health roll-up
        report = glue.health.report()
    """

    def __init__(self, async_dispatch: bool = False) -> None:
        self.registry = ServiceRegistry()
        self.bus = EventBus(async_dispatch=async_dispatch)
        self.pipelines = PipelineManager(bus=self.bus)
        self.health = HealthAggregator(self.registry)
        self.transformer = DataTransformer()
        self._started_at: datetime = datetime.now(timezone.utc)

        logger.info("🔗 GlueCore initialised (async_dispatch=%s)", async_dispatch)

    # ── convenience helpers ───────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Return a lightweight status snapshot (no health probes)."""
        return {
            "started_at": self._started_at.isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - self._started_at).total_seconds(),
            "registered_services": self.registry.all_names(),
            "registered_pipelines": self.pipelines.pipeline_names(),
            "event_topics": self.bus.topics(),
        }

    def health_dict(self) -> Dict[str, Any]:
        """Run full health probes and return a plain dict (JSON-serialisable)."""
        report = self.health.report()
        return self.transformer.convert(report, "health_report", "dict")

    def publish(
        self,
        topic: str,
        payload: Any,
        *,
        source: str = "glue",
        priority: EventPriority = EventPriority.NORMAL,
    ) -> GlueEvent:
        """Shortcut for :meth:`EventBus.publish`."""
        return self.bus.publish(topic, payload, source=source, priority=priority)

    def subscribe(self, topic: str, handler: Callable[[GlueEvent], None]) -> None:
        """Shortcut for :meth:`EventBus.subscribe`."""
        self.bus.subscribe(topic, handler)

    def run_pipeline(self, name: str, data: Any) -> PipelineResult:
        """Shortcut for :meth:`PipelineManager.run`."""
        return self.pipelines.run(name, data)
