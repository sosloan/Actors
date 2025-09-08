#!/usr/bin/env python3
"""
🏭 Production Time Management API
Enterprise-grade patterns: Circuit Breaker, Event Sourcing, Distributed Tracing, Saga
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import our production patterns
from production_time_patterns import (
    ProductionTimeManager, CircuitBreakerState, EventType, TraceContext,
    Saga, CompensationAction
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global production time manager instance
production_manager = None

def initialize_production_manager():
    """Initialize the production time manager"""
    global production_manager
    try:
        production_manager = ProductionTimeManager()
        logger.info("✅ Production Time Manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize production manager: {e}")
        return False

# ============================================================================
# HEALTH AND STATUS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Production Time Management API',
        'timestamp': time.time(),
        'production_manager_active': production_manager is not None
    })

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get detailed system status"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        circuit_breaker_status = production_manager.get_circuit_breaker_status()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'circuit_breakers': circuit_breaker_status,
            'total_circuit_breakers': len(circuit_breaker_status),
            'active_sagas': len([s for s in production_manager.sagas.values() if s.status == "executing"]),
            'total_sagas': len(production_manager.sagas),
            'total_events': len(production_manager.event_store.events),
            'total_spans': len(production_manager.tracer.spans)
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CIRCUIT BREAKER MANAGEMENT
# ============================================================================

@app.route('/api/circuit-breakers', methods=['GET'])
def get_circuit_breakers():
    """Get all circuit breakers status"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        status = production_manager.get_circuit_breaker_status()
        
        return jsonify({
            'circuit_breakers': status,
            'total_services': len(status),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get circuit breakers error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/circuit-breakers/<service_name>', methods=['GET'])
def get_circuit_breaker(service_name):
    """Get specific circuit breaker status"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        circuit_breaker = production_manager.get_circuit_breaker(service_name)
        status = circuit_breaker.get_status()
        
        return jsonify({
            'service_name': service_name,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get circuit breaker error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/circuit-breakers/<service_name>/reset', methods=['POST'])
def reset_circuit_breaker(service_name):
    """Reset circuit breaker to closed state"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        circuit_breaker = production_manager.get_circuit_breaker(service_name)
        circuit_breaker.state = CircuitBreakerState.CLOSED
        circuit_breaker.failure_count = 0
        circuit_breaker.success_count = 0
        circuit_breaker.last_failure_time = None
        
        return jsonify({
            'message': f'Circuit breaker for {service_name} reset successfully',
            'service_name': service_name,
            'new_status': circuit_breaker.get_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Reset circuit breaker error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# EVENT SOURCING
# ============================================================================

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get events from event store"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        aggregate_id = request.args.get('aggregate_id')
        event_type = request.args.get('event_type')
        limit = request.args.get('limit', 100, type=int)
        
        if aggregate_id:
            events = production_manager.get_event_history(aggregate_id)
        else:
            # Get all events
            events = [event.to_dict() for event in production_manager.event_store.events]
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        
        # Apply limit
        events = events[-limit:] if limit else events
        
        return jsonify({
            'events': events,
            'total_events': len(events),
            'filters': {
                'aggregate_id': aggregate_id,
                'event_type': event_type,
                'limit': limit
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<aggregate_id>', methods=['GET'])
def get_aggregate_events(aggregate_id):
    """Get events for specific aggregate"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        events = production_manager.get_event_history(aggregate_id)
        
        return jsonify({
            'aggregate_id': aggregate_id,
            'events': events,
            'total_events': len(events),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get aggregate events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/snapshots/<aggregate_id>', methods=['GET'])
def get_aggregate_snapshot(aggregate_id):
    """Get snapshot for specific aggregate"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        snapshot = production_manager.event_store.get_snapshot(aggregate_id)
        
        if not snapshot:
            return jsonify({'error': f'No snapshot found for aggregate {aggregate_id}'}), 404
        
        return jsonify({
            'aggregate_id': aggregate_id,
            'snapshot': snapshot,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get aggregate snapshot error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DISTRIBUTED TRACING
# ============================================================================

@app.route('/api/traces', methods=['GET'])
def get_traces():
    """Get all traces"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # Get unique trace IDs
        trace_ids = list(set(span.trace_id for span in production_manager.tracer.spans))
        trace_ids = trace_ids[-limit:] if limit else trace_ids
        
        traces = []
        for trace_id in trace_ids:
            summary = production_manager.get_trace_summary(trace_id)
            if summary:
                traces.append(summary)
        
        return jsonify({
            'traces': traces,
            'total_traces': len(traces),
            'limit': limit,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get traces error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/traces/<trace_id>', methods=['GET'])
def get_trace(trace_id):
    """Get specific trace"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        trace_summary = production_manager.get_trace_summary(trace_id)
        
        if not trace_summary:
            return jsonify({'error': f'Trace {trace_id} not found'}), 404
        
        return jsonify({
            'trace': trace_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get trace error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/traces/create', methods=['POST'])
def create_trace():
    """Create new trace context"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        trace_context = TraceContext.create_root()
        
        return jsonify({
            'trace_context': trace_context.to_dict(),
            'message': 'Trace context created successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Create trace error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SAGA MANAGEMENT
# ============================================================================

@app.route('/api/sagas', methods=['GET'])
def get_sagas():
    """Get all sagas"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        status_filter = request.args.get('status')
        
        sagas = []
        for saga in production_manager.sagas.values():
            if not status_filter or saga.status == status_filter:
                sagas.append({
                    'saga_id': saga.saga_id,
                    'name': saga.name,
                    'status': saga.status,
                    'actions_count': len(saga.actions),
                    'executed_actions_count': len(saga.executed_actions),
                    'start_time': saga.start_time.isoformat() if saga.start_time else None,
                    'end_time': saga.end_time.isoformat() if saga.end_time else None,
                    'error': saga.error
                })
        
        return jsonify({
            'sagas': sagas,
            'total_sagas': len(sagas),
            'filter': {'status': status_filter},
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get sagas error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sagas', methods=['POST'])
async def create_saga():
    """Create new saga"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        data = request.get_json()
        
        saga_id = data.get('saga_id', f"saga_{int(time.time())}")
        name = data.get('name', 'Unnamed Saga')
        
        saga = production_manager.create_saga(saga_id, name)
        
        return jsonify({
            'message': 'Saga created successfully',
            'saga': {
                'saga_id': saga.saga_id,
                'name': saga.name,
                'status': saga.status,
                'actions_count': len(saga.actions)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Create saga error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sagas/<saga_id>', methods=['GET'])
def get_saga(saga_id):
    """Get specific saga"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        if saga_id not in production_manager.sagas:
            return jsonify({'error': f'Saga {saga_id} not found'}), 404
        
        saga = production_manager.sagas[saga_id]
        
        return jsonify({
            'saga': {
                'saga_id': saga.saga_id,
                'name': saga.name,
                'status': saga.status,
                'actions': [
                    {
                        'action_id': action.action_id,
                        'action_type': action.action_type,
                        'parameters': action.parameters
                    }
                    for action in saga.actions
                ],
                'executed_actions': saga.executed_actions,
                'start_time': saga.start_time.isoformat() if saga.start_time else None,
                'end_time': saga.end_time.isoformat() if saga.end_time else None,
                'error': saga.error
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get saga error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sagas/<saga_id>/execute', methods=['POST'])
async def execute_saga(saga_id):
    """Execute saga"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        data = request.get_json() or {}
        trace_id = data.get('trace_id')
        
        if trace_id:
            trace_context = TraceContext(trace_id=trace_id, span_id=TraceContext._generate_id())
        else:
            trace_context = TraceContext.create_root()
        
        result = await production_manager.execute_saga(saga_id, trace_context)
        
        return jsonify({
            'message': 'Saga execution completed',
            'saga_id': saga_id,
            'result': 'success' if result else 'failed_with_compensation',
            'trace_id': trace_context.trace_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Execute saga error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DEMO AND TESTING
# ============================================================================

@app.route('/api/demo/circuit-breaker', methods=['POST'])
async def demo_circuit_breaker():
    """Demo circuit breaker functionality"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        service_name = request.json.get('service_name', 'demo_service')
        failure_count = request.json.get('failure_count', 6)
        
        # Create trace context
        trace_context = TraceContext.create_root()
        
        # Simulate failing operation
        async def failing_operation():
            raise Exception("Simulated failure")
        
        # Simulate failures to open circuit breaker
        results = []
        for i in range(failure_count):
            try:
                await production_manager.execute_with_circuit_breaker(
                    service_name, failing_operation, trace_context
                )
                results.append(f"Attempt {i+1}: Success")
            except Exception as e:
                results.append(f"Attempt {i+1}: {str(e)}")
        
        # Get circuit breaker status
        circuit_breaker = production_manager.get_circuit_breaker(service_name)
        status = circuit_breaker.get_status()
        
        return jsonify({
            'message': 'Circuit breaker demo completed',
            'service_name': service_name,
            'results': results,
            'circuit_breaker_status': status,
            'trace_id': trace_context.trace_id
        })
        
    except Exception as e:
        logger.error(f"❌ Circuit breaker demo error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/saga', methods=['POST'])
async def demo_saga():
    """Demo saga pattern functionality"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        # Create trace context
        trace_context = TraceContext.create_root()
        
        # Create demo saga
        saga = production_manager.create_saga("demo_saga", "Demo Saga")
        
        # Add demo actions
        async def action1(params, trace_context):
            return "Action 1 completed"
        
        async def compensate1(params, trace_context):
            return "Action 1 compensated"
        
        async def action2(params, trace_context):
            raise Exception("Action 2 failed!")
        
        async def compensate2(params, trace_context):
            return "Action 2 compensated"
        
        saga.add_action(CompensationAction("action1", "demo", {}, action1, compensate1))
        saga.add_action(CompensationAction("action2", "demo", {}, action2, compensate2))
        
        # Execute saga
        result = await production_manager.execute_saga("demo_saga", trace_context)
        
        return jsonify({
            'message': 'Saga demo completed',
            'saga_id': 'demo_saga',
            'result': 'success' if result else 'failed_with_compensation',
            'saga_status': saga.status,
            'executed_actions': saga.executed_actions,
            'trace_id': trace_context.trace_id
        })
        
    except Exception as e:
        logger.error(f"❌ Saga demo error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/event-sourcing', methods=['POST'])
def demo_event_sourcing():
    """Demo event sourcing functionality"""
    if production_manager is None:
        return jsonify({'error': 'Production manager not initialized'}), 500
    
    try:
        # Create trace context
        trace_context = TraceContext.create_root()
        
        # Store demo events
        aggregate_id = f"demo_aggregate_{int(time.time())}"
        
        production_manager.store_event(
            EventType.EVENT_CREATED, aggregate_id, 
            {"name": "Demo Event", "type": "test"}, trace_context
        )
        
        production_manager.store_event(
            EventType.EVENT_EXECUTED, aggregate_id, 
            {"duration_ms": 1500, "result": "success"}, trace_context
        )
        
        production_manager.store_event(
            EventType.EVENT_FAILED, aggregate_id, 
            {"error": "Demo error", "retry_count": 3}, trace_context
        )
        
        # Get event history
        history = production_manager.get_event_history(aggregate_id)
        
        return jsonify({
            'message': 'Event sourcing demo completed',
            'aggregate_id': aggregate_id,
            'events_stored': len(history),
            'event_history': history,
            'trace_id': trace_context.trace_id
        })
        
    except Exception as e:
        logger.error(f"❌ Event sourcing demo error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# ASYNC ROUTE HANDLERS
# ============================================================================

def async_route(f):
    """Wrapper for async routes"""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    wrapper.__name__ = f.__name__  # Preserve function name
    return wrapper

# Apply async wrapper to async routes
app.route('/api/sagas', methods=['POST'])(async_route(create_saga))
app.route('/api/sagas/<saga_id>/execute', methods=['POST'])(async_route(execute_saga))
app.route('/api/demo/circuit-breaker', methods=['POST'])(async_route(demo_circuit_breaker))
app.route('/api/demo/saga', methods=['POST'])(async_route(demo_saga))

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("🏭 Starting Production Time Management API Server...")
    
    # Initialize production manager
    if not initialize_production_manager():
        print("❌ Failed to initialize production manager. Exiting.")
        exit(1)
    
    print("✅ Production manager initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/status - System status")
    print("")
    print("  🔌 Circuit Breaker Management:")
    print("  GET  /api/circuit-breakers - Get all circuit breakers")
    print("  GET  /api/circuit-breakers/<service> - Get circuit breaker status")
    print("  POST /api/circuit-breakers/<service>/reset - Reset circuit breaker")
    print("")
    print("  📝 Event Sourcing:")
    print("  GET  /api/events - Get events")
    print("  GET  /api/events/<aggregate_id> - Get aggregate events")
    print("  GET  /api/events/snapshots/<aggregate_id> - Get aggregate snapshot")
    print("")
    print("  🔍 Distributed Tracing:")
    print("  GET  /api/traces - Get all traces")
    print("  GET  /api/traces/<trace_id> - Get specific trace")
    print("  POST /api/traces/create - Create new trace")
    print("")
    print("  🔄 Saga Management:")
    print("  GET  /api/sagas - Get all sagas")
    print("  POST /api/sagas - Create saga")
    print("  GET  /api/sagas/<saga_id> - Get specific saga")
    print("  POST /api/sagas/<saga_id>/execute - Execute saga")
    print("")
    print("  🎯 Demo Endpoints:")
    print("  POST /api/demo/circuit-breaker - Demo circuit breaker")
    print("  POST /api/demo/saga - Demo saga pattern")
    print("  POST /api/demo/event-sourcing - Demo event sourcing")
    
    # Start the server
    app.run(host='0.0.0.0', port=5006, debug=True)
