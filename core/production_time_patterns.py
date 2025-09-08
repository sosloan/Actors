#!/usr/bin/env python3
"""
🏭 Production-Grade Time Management Patterns
Circuit Breaker, Event Sourcing, Distributed Tracing, and Saga Pattern
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics
import hashlib
import pickle
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery

class EventType(Enum):
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

@dataclass
class CircuitBreaker:
    """Circuit Breaker pattern for failure isolation"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    success_count: int = 0
    half_open_max_calls: int = 3
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info("🔄 Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return self.success_count < self.half_open_max_calls
        
        return False
    
    def record_success(self):
        """Record successful execution"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("✅ Circuit breaker CLOSED - service recovered")
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"⚠️ Circuit breaker OPENED after {self.failure_count} failures")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'can_execute': self.can_execute()
        }

@dataclass
class Event:
    """Immutable event for event sourcing"""
    id: str
    event_type: EventType
    aggregate_id: str
    timestamp: datetime
    data: Dict[str, Any]
    version: int
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'aggregate_id': self.aggregate_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'version': self.version,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id
        }

@dataclass
class EventStore:
    """Event store for event sourcing pattern"""
    events: List[Event] = field(default_factory=list)
    snapshots: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    snapshot_interval: int = 100  # Create snapshot every N events
    
    def append(self, event: Event):
        """Append event to store"""
        self.events.append(event)
        
        # Create snapshot if needed
        if len(self.events) % self.snapshot_interval == 0:
            self._create_snapshot(event.aggregate_id)
        
        logger.debug(f"📝 Event stored: {event.event_type.value} for {event.aggregate_id}")
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for an aggregate"""
        return [
            event for event in self.events
            if event.aggregate_id == aggregate_id and event.version >= from_version
        ]
    
    def get_snapshot(self, aggregate_id: str) -> Optional[Dict[str, Any]]:
        """Get latest snapshot for an aggregate"""
        return self.snapshots.get(aggregate_id)
    
    def _create_snapshot(self, aggregate_id: str):
        """Create snapshot of current state"""
        events = self.get_events(aggregate_id)
        if not events:
            return
        
        # Create snapshot from events
        snapshot = {
            'aggregate_id': aggregate_id,
            'version': events[-1].version,
            'timestamp': datetime.now().isoformat(),
            'state': self._reconstruct_state(events)
        }
        
        self.snapshots[aggregate_id] = snapshot
        logger.info(f"📸 Snapshot created for {aggregate_id} at version {snapshot['version']}")
    
    def _reconstruct_state(self, events: List[Event]) -> Dict[str, Any]:
        """Reconstruct state from events"""
        state = {}
        
        for event in events:
            if event.event_type == EventType.EVENT_CREATED:
                state.update(event.data)
            elif event.event_type == EventType.EVENT_EXECUTED:
                state['last_execution'] = event.data
                state['execution_count'] = state.get('execution_count', 0) + 1
            elif event.event_type == EventType.EVENT_FAILED:
                state['last_failure'] = event.data
                state['failure_count'] = state.get('failure_count', 0) + 1
        
        return state

@dataclass
class TraceContext:
    """Distributed tracing context"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create_root(cls) -> 'TraceContext':
        """Create root trace context"""
        return cls(
            trace_id=cls._generate_id(),
            span_id=cls._generate_id()
        )
    
    @classmethod
    def create_child(cls, parent: 'TraceContext') -> 'TraceContext':
        """Create child trace context"""
        return cls(
            trace_id=parent.trace_id,
            span_id=cls._generate_id(),
            parent_span_id=parent.span_id,
            baggage=parent.baggage.copy()
        )
    
    @staticmethod
    def _generate_id() -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'baggage': self.baggage
        }

@dataclass
class Span:
    """Tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    
    def finish(self, error: Optional[str] = None):
        """Finish span"""
        self.end_time = datetime.now()
        if error:
            self.error = error
            self.tags['error'] = True
    
    def add_tag(self, key: str, value: Any):
        """Add tag to span"""
        self.tags[key] = value
    
    def add_log(self, message: str, **kwargs):
        """Add log to span"""
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            **kwargs
        })
    
    def get_duration_ms(self) -> float:
        """Get span duration in milliseconds"""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds() * 1000

class Tracer:
    """Distributed tracer"""
    
    def __init__(self):
        self.spans: List[Span] = []
        self.active_spans: Dict[str, Span] = {}
    
    @contextmanager
    def start_span(self, operation_name: str, trace_context: TraceContext, **tags):
        """Start a new span"""
        span = Span(
            trace_id=trace_context.trace_id,
            span_id=trace_context.span_id,
            parent_span_id=trace_context.parent_span_id,
            operation_name=operation_name,
            start_time=datetime.now(),
            tags=tags
        )
        
        self.spans.append(span)
        self.active_spans[trace_context.span_id] = span
        
        try:
            yield span
        except Exception as e:
            span.finish(error=str(e))
            raise
        finally:
            span.finish()
            self.active_spans.pop(trace_context.span_id, None)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace"""
        return [span for span in self.spans if span.trace_id == trace_id]
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get trace summary"""
        spans = self.get_trace(trace_id)
        if not spans:
            return {}
        
        root_spans = [s for s in spans if s.parent_span_id is None]
        total_duration = max(s.get_duration_ms() for s in spans)
        
        return {
            'trace_id': trace_id,
            'total_spans': len(spans),
            'root_spans': len(root_spans),
            'total_duration_ms': total_duration,
            'has_errors': any(s.error for s in spans),
            'spans': [
                {
                    'span_id': s.span_id,
                    'operation_name': s.operation_name,
                    'duration_ms': s.get_duration_ms(),
                    'error': s.error,
                    'tags': s.tags
                }
                for s in spans
            ]
        }

@dataclass
class CompensationAction:
    """Compensation action for saga pattern"""
    action_id: str
    action_type: str
    parameters: Dict[str, Any]
    execute_func: Callable
    compensate_func: Callable
    
    async def execute(self, trace_context: TraceContext) -> Any:
        """Execute the action"""
        result = await self.execute_func(self.parameters, trace_context)
        return result
    
    async def compensate(self, trace_context: TraceContext) -> Any:
        """Compensate the action"""
        result = await self.compensate_func(self.parameters, trace_context)
        return result

@dataclass
class Saga:
    """Saga pattern for distributed transactions"""
    saga_id: str
    name: str
    actions: List[CompensationAction] = field(default_factory=list)
    executed_actions: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, executing, completed, failed, compensating
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    def add_action(self, action: CompensationAction):
        """Add action to saga"""
        self.actions.append(action)
    
    async def execute(self, trace_context: TraceContext) -> bool:
        """Execute saga"""
        self.status = "executing"
        self.start_time = datetime.now()
        
        try:
            for action in self.actions:
                # Execute action
                result = await action.execute(trace_context)
                self.executed_actions.append(action.action_id)
                
                logger.info(f"✅ Saga {self.saga_id}: Action {action.action_id} executed")
            
            self.status = "completed"
            self.end_time = datetime.now()
            logger.info(f"🎉 Saga {self.saga_id} completed successfully")
            return True
            
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"❌ Saga {self.saga_id} failed: {e}")
            
            # Start compensation
            await self.compensate(trace_context)
            return False
    
    async def compensate(self, trace_context: TraceContext):
        """Compensate saga (rollback)"""
        self.status = "compensating"
        
        # Compensate in reverse order
        for action_id in reversed(self.executed_actions):
            action = next(a for a in self.actions if a.action_id == action_id)
            try:
                await action.compensate(trace_context)
                logger.info(f"🔄 Saga {self.saga_id}: Action {action_id} compensated")
            except Exception as e:
                logger.error(f"❌ Saga {self.saga_id}: Failed to compensate {action_id}: {e}")
        
        self.status = "compensated"
        self.end_time = datetime.now()
        logger.info(f"🔄 Saga {self.saga_id} compensation completed")

class ProductionTimeManager:
    """Production-grade time manager with advanced patterns"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.event_store = EventStore()
        self.tracer = Tracer()
        self.sagas: Dict[str, Saga] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        
        # Register default event handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default event handlers"""
        self.event_handlers[EventType.CIRCUIT_BREAKER_OPENED].append(self._handle_circuit_breaker_opened)
        self.event_handlers[EventType.SAGA_FAILED].append(self._handle_saga_failed)
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    async def execute_with_circuit_breaker(self, service_name: str, operation: Callable, 
                                         trace_context: TraceContext, *args, **kwargs) -> Any:
        """Execute operation with circuit breaker protection"""
        circuit_breaker = self.get_circuit_breaker(service_name)
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker OPEN for service {service_name}")
        
        with self.tracer.start_span(f"circuit_breaker_execute", trace_context, 
                                   service=service_name) as span:
            try:
                result = await operation(*args, **kwargs)
                circuit_breaker.record_success()
                span.add_tag("success", True)
                return result
            except Exception as e:
                circuit_breaker.record_failure()
                span.add_tag("success", False)
                span.add_tag("error", str(e))
                raise
    
    def store_event(self, event_type: EventType, aggregate_id: str, data: Dict[str, Any], 
                   trace_context: TraceContext, correlation_id: str = None):
        """Store event in event store"""
        event = Event(
            id=str(uuid.uuid4()),
            event_type=event_type,
            aggregate_id=aggregate_id,
            timestamp=datetime.now(),
            data=data,
            version=len(self.event_store.get_events(aggregate_id)) + 1,
            correlation_id=correlation_id or trace_context.trace_id,
            causation_id=trace_context.span_id
        )
        
        self.event_store.append(event)
        
        # Trigger event handlers
        for handler in self.event_handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"❌ Event handler failed: {e}")
    
    def create_saga(self, saga_id: str, name: str) -> Saga:
        """Create new saga"""
        saga = Saga(saga_id=saga_id, name=name)
        self.sagas[saga_id] = saga
        return saga
    
    async def execute_saga(self, saga_id: str, trace_context: TraceContext) -> bool:
        """Execute saga"""
        if saga_id not in self.sagas:
            raise ValueError(f"Saga {saga_id} not found")
        
        saga = self.sagas[saga_id]
        
        with self.tracer.start_span(f"saga_execute", trace_context, 
                                   saga_id=saga_id, saga_name=saga.name) as span:
            try:
                result = await saga.execute(trace_context)
                span.add_tag("saga_result", "success" if result else "failed")
                return result
            except Exception as e:
                span.add_tag("saga_result", "error")
                span.add_tag("error", str(e))
                raise
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get trace summary"""
        return self.tracer.get_trace_summary(trace_id)
    
    def get_event_history(self, aggregate_id: str) -> List[Dict[str, Any]]:
        """Get event history for aggregate"""
        events = self.event_store.get_events(aggregate_id)
        return [event.to_dict() for event in events]
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            service: breaker.get_status()
            for service, breaker in self.circuit_breakers.items()
        }
    
    # Event handlers
    def _handle_circuit_breaker_opened(self, event: Event):
        """Handle circuit breaker opened event"""
        logger.warning(f"🚨 Circuit breaker opened for {event.aggregate_id}")
        # Could trigger alerts, notifications, etc.
    
    def _handle_saga_failed(self, event: Event):
        """Handle saga failed event"""
        logger.error(f"💥 Saga failed: {event.data.get('saga_id')}")
        # Could trigger compensation, alerts, etc.

# Example usage and integration
async def main():
    """Demo of production patterns"""
    
    manager = ProductionTimeManager()
    
    print("🏭 Production Time Management Patterns Demo")
    print("=" * 60)
    
    # Create root trace context
    trace_context = TraceContext.create_root()
    
    # Demo Circuit Breaker
    print("\n🔌 Circuit Breaker Demo:")
    
    async def failing_operation():
        raise Exception("Simulated failure")
    
    async def successful_operation():
        return "Success!"
    
    # Simulate failures to open circuit breaker
    for i in range(6):
        try:
            await manager.execute_with_circuit_breaker("test_service", failing_operation, trace_context)
        except Exception as e:
            print(f"   Attempt {i+1}: {e}")
    
    # Check circuit breaker status
    status = manager.get_circuit_breaker("test_service").get_status()
    print(f"   Circuit Breaker Status: {status['state']}")
    print(f"   Can Execute: {status['can_execute']}")
    
    # Demo Event Sourcing
    print("\n📝 Event Sourcing Demo:")
    
    # Store some events
    manager.store_event(EventType.EVENT_CREATED, "event_123", {"name": "Test Event"}, trace_context)
    manager.store_event(EventType.EVENT_EXECUTED, "event_123", {"duration_ms": 1500}, trace_context)
    manager.store_event(EventType.EVENT_FAILED, "event_123", {"error": "Test error"}, trace_context)
    
    # Get event history
    history = manager.get_event_history("event_123")
    print(f"   Event History: {len(history)} events")
    for event in history:
        print(f"     - {event['event_type']}: {event['data']}")
    
    # Demo Saga Pattern
    print("\n🔄 Saga Pattern Demo:")
    
    # Create saga
    saga = manager.create_saga("demo_saga", "Demo Saga")
    
    # Add actions
    async def action1(params, trace_context):
        print("   Executing Action 1...")
        return "Action 1 completed"
    
    async def compensate1(params, trace_context):
        print("   Compensating Action 1...")
        return "Action 1 compensated"
    
    async def action2(params, trace_context):
        print("   Executing Action 2...")
        raise Exception("Action 2 failed!")
    
    async def compensate2(params, trace_context):
        print("   Compensating Action 2...")
        return "Action 2 compensated"
    
    saga.add_action(CompensationAction("action1", "test", {}, action1, compensate1))
    saga.add_action(CompensationAction("action2", "test", {}, action2, compensate2))
    
    # Execute saga
    result = await manager.execute_saga("demo_saga", trace_context)
    print(f"   Saga Result: {'Success' if result else 'Failed with compensation'}")
    
    # Demo Distributed Tracing
    print("\n🔍 Distributed Tracing Demo:")
    
    trace_summary = manager.get_trace_summary(trace_context.trace_id)
    print(f"   Trace ID: {trace_summary['trace_id']}")
    print(f"   Total Spans: {trace_summary['total_spans']}")
    print(f"   Total Duration: {trace_summary['total_duration_ms']:.2f}ms")
    print(f"   Has Errors: {trace_summary['has_errors']}")
    
    print(f"\n✅ Production Patterns Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())
