#!/usr/bin/env python3
"""
⏰ Time Management API Server
RESTful API for advanced time management and scheduling
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import our time management system
from advanced_time_manager import (
    AdvancedTimeManager, TimeEvent, TimeEventType, TimeZone, 
    ScheduleFrequency, TimeExecution, TimeAnalytics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global time manager instance
time_manager = None

def initialize_time_manager():
    """Initialize the global time manager"""
    global time_manager
    try:
        time_manager = AdvancedTimeManager()
        asyncio.run(time_manager.initialize())
        logger.info("✅ Advanced Time Manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize time manager: {e}")
        return False

# ============================================================================
# HEALTH AND STATUS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Time Management API',
        'timestamp': time.time(),
        'time_manager_active': time_manager is not None
    })

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get detailed system status"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        analytics = time_manager.get_analytics()
        market_status = time_manager.get_market_status()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'analytics': {
                'total_events': analytics.total_events,
                'active_events': analytics.active_events,
                'completed_executions': analytics.completed_executions,
                'failed_executions': analytics.failed_executions,
                'execution_success_rate': analytics.execution_success_rate,
                'average_execution_time_ms': analytics.average_execution_time_ms
            },
            'market_status': market_status,
            'scheduler_running': time_manager.is_running
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# EVENT MANAGEMENT
# ============================================================================

async def create_event():
    """Create a new time event"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'event_type', 'scheduled_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create event
        event = await time_manager.create_event(data)
        
        return jsonify({
            'message': 'Event created successfully',
            'event': {
                'id': event.id,
                'name': event.name,
                'event_type': event.event_type.value,
                'scheduled_time': event.scheduled_time.isoformat(),
                'timezone': event.timezone.value,
                'frequency': event.frequency.value,
                'priority': event.priority,
                'is_active': event.is_active,
                'is_recurring': event.is_recurring,
                'next_execution': event.next_execution.isoformat() if event.next_execution else None,
                'created_at': event.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Create event error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get events with optional filters"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        # Get query parameters for filtering
        event_type = request.args.get('event_type')
        frequency = request.args.get('frequency')
        is_active = request.args.get('is_active')
        priority = request.args.get('priority', type=int)
        
        # Build filters
        filters = {}
        if event_type:
            filters['event_type'] = TimeEventType(event_type)
        if frequency:
            filters['frequency'] = ScheduleFrequency(frequency)
        if is_active is not None:
            filters['is_active'] = is_active.lower() == 'true'
        if priority is not None:
            filters['priority'] = priority
        
        # Get events
        events = time_manager.get_events(filters)
        
        # Format events
        formatted_events = []
        for event in events:
            formatted_events.append({
                'id': event.id,
                'name': event.name,
                'event_type': event.event_type.value,
                'scheduled_time': event.scheduled_time.isoformat(),
                'timezone': event.timezone.value,
                'frequency': event.frequency.value,
                'cron_expression': event.cron_expression,
                'callback_function': event.callback_function,
                'parameters': event.parameters,
                'priority': event.priority,
                'is_active': event.is_active,
                'is_recurring': event.is_recurring,
                'max_executions': event.max_executions,
                'execution_count': event.execution_count,
                'last_execution': event.last_execution.isoformat() if event.last_execution else None,
                'next_execution': event.next_execution.isoformat() if event.next_execution else None,
                'created_at': event.created_at.isoformat(),
                'updated_at': event.updated_at.isoformat()
            })
        
        return jsonify({
            'events': formatted_events,
            'total_events': len(formatted_events),
            'filters_applied': filters
        })
        
    except Exception as e:
        logger.error(f"❌ Get events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        event = time_manager.get_event(event_id)
        
        if not event:
            return jsonify({'error': f'Event with ID "{event_id}" not found'}), 404
        
        return jsonify({
            'event': {
                'id': event.id,
                'name': event.name,
                'event_type': event.event_type.value,
                'scheduled_time': event.scheduled_time.isoformat(),
                'timezone': event.timezone.value,
                'frequency': event.frequency.value,
                'cron_expression': event.cron_expression,
                'callback_function': event.callback_function,
                'parameters': event.parameters,
                'priority': event.priority,
                'is_active': event.is_active,
                'is_recurring': event.is_recurring,
                'max_executions': event.max_executions,
                'execution_count': event.execution_count,
                'last_execution': event.last_execution.isoformat() if event.last_execution else None,
                'next_execution': event.next_execution.isoformat() if event.next_execution else None,
                'created_at': event.created_at.isoformat(),
                'updated_at': event.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get event error: {e}")
        return jsonify({'error': str(e)}), 500

async def update_event(event_id):
    """Update an existing event"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        data = request.get_json()
        
        # Update event
        event = await time_manager.update_event(event_id, data)
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': {
                'id': event.id,
                'name': event.name,
                'event_type': event.event_type.value,
                'scheduled_time': event.scheduled_time.isoformat(),
                'timezone': event.timezone.value,
                'frequency': event.frequency.value,
                'cron_expression': event.cron_expression,
                'callback_function': event.callback_function,
                'parameters': event.parameters,
                'priority': event.priority,
                'is_active': event.is_active,
                'is_recurring': event.is_recurring,
                'max_executions': event.max_executions,
                'execution_count': event.execution_count,
                'last_execution': event.last_execution.isoformat() if event.last_execution else None,
                'next_execution': event.next_execution.isoformat() if event.next_execution else None,
                'created_at': event.created_at.isoformat(),
                'updated_at': event.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Update event error: {e}")
        return jsonify({'error': str(e)}), 500

async def delete_event(event_id):
    """Delete an event"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        success = await time_manager.delete_event(event_id)
        
        if not success:
            return jsonify({'error': f'Event with ID "{event_id}" not found'}), 404
        
        return jsonify({
            'message': 'Event deleted successfully',
            'event_id': event_id
        })
        
    except Exception as e:
        logger.error(f"❌ Delete event error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SCHEDULING AND EXECUTION
# ============================================================================

@app.route('/api/events/upcoming', methods=['GET'])
def get_upcoming_events():
    """Get upcoming events"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 10, type=int)
        
        upcoming = time_manager.get_upcoming_events(limit)
        
        # Format events
        formatted_events = []
        for event in upcoming:
            formatted_events.append({
                'id': event.id,
                'name': event.name,
                'event_type': event.event_type.value,
                'next_execution': event.next_execution.isoformat(),
                'priority': event.priority,
                'is_recurring': event.is_recurring,
                'execution_count': event.execution_count
            })
        
        return jsonify({
            'upcoming_events': formatted_events,
            'total_upcoming': len(formatted_events),
            'limit': limit
        })
        
    except Exception as e:
        logger.error(f"❌ Get upcoming events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/executions', methods=['GET'])
def get_execution_history():
    """Get execution history"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        event_id = request.args.get('event_id')
        limit = request.args.get('limit', 100, type=int)
        
        executions = time_manager.get_execution_history(event_id, limit)
        
        # Format executions
        formatted_executions = []
        for execution in executions:
            formatted_executions.append({
                'event_id': execution.event_id,
                'execution_time': execution.execution_time.isoformat(),
                'duration_ms': execution.duration_ms,
                'status': execution.status,
                'result': execution.result,
                'error_message': execution.error_message,
                'metadata': execution.metadata
            })
        
        return jsonify({
            'executions': formatted_executions,
            'total_executions': len(formatted_executions),
            'filters': {
                'event_id': event_id,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get execution history error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MARKET HOURS AND TIMEZONE
# ============================================================================

@app.route('/api/market/status', methods=['GET'])
def get_market_status():
    """Get current market status"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        market_status = time_manager.get_market_status()
        
        return jsonify({
            'market_status': market_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get market status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/timezones', methods=['GET'])
def get_available_timezones():
    """Get available timezones"""
    timezones = [
        {'value': tz.value, 'name': tz.value, 'description': f'{tz.value} timezone'}
        for tz in TimeZone
    ]
    
    return jsonify({
        'timezones': timezones,
        'total_timezones': len(timezones)
    })

@app.route('/api/event-types', methods=['GET'])
def get_available_event_types():
    """Get available event types"""
    event_types = [
        {'value': et.value, 'name': et.value.replace('_', ' ').title(), 'description': f'{et.value} event'}
        for et in TimeEventType
    ]
    
    return jsonify({
        'event_types': event_types,
        'total_event_types': len(event_types)
    })

@app.route('/api/frequencies', methods=['GET'])
def get_available_frequencies():
    """Get available schedule frequencies"""
    frequencies = [
        {'value': freq.value, 'name': freq.value.replace('_', ' ').title(), 'description': f'{freq.value} frequency'}
        for freq in ScheduleFrequency
    ]
    
    return jsonify({
        'frequencies': frequencies,
        'total_frequencies': len(frequencies)
    })

# ============================================================================
# ANALYTICS AND REPORTING
# ============================================================================

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get time management analytics"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        analytics = time_manager.get_analytics()
        
        return jsonify({
            'analytics': {
                'total_events': analytics.total_events,
                'active_events': analytics.active_events,
                'completed_executions': analytics.completed_executions,
                'failed_executions': analytics.failed_executions,
                'average_execution_time_ms': analytics.average_execution_time_ms,
                'events_by_type': analytics.events_by_type,
                'events_by_frequency': analytics.events_by_frequency,
                'execution_success_rate': analytics.execution_success_rate,
                'last_updated': analytics.last_updated.isoformat()
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get analytics error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/performance', methods=['GET'])
def get_performance_metrics():
    """Get performance metrics"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        analytics = time_manager.get_analytics()
        recent_executions = time_manager.get_execution_history(limit=50)
        
        # Calculate performance metrics
        total_executions = len(recent_executions)
        successful_executions = len([e for e in recent_executions if e.status == "success"])
        failed_executions = len([e for e in recent_executions if e.status == "failed"])
        
        avg_duration = 0.0
        if recent_executions:
            avg_duration = sum(e.duration_ms for e in recent_executions) / len(recent_executions)
        
        # Calculate success rate by event type
        success_by_type = {}
        for execution in recent_executions:
            event = time_manager.get_event(execution.event_id)
            if event:
                event_type = event.event_type.value
                if event_type not in success_by_type:
                    success_by_type[event_type] = {'success': 0, 'total': 0}
                success_by_type[event_type]['total'] += 1
                if execution.status == "success":
                    success_by_type[event_type]['success'] += 1
        
        # Calculate success rates
        for event_type in success_by_type:
            total = success_by_type[event_type]['total']
            success = success_by_type[event_type]['success']
            success_by_type[event_type]['success_rate'] = success / total if total > 0 else 0.0
        
        return jsonify({
            'performance_metrics': {
                'total_recent_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': successful_executions / total_executions if total_executions > 0 else 0.0,
                'average_duration_ms': avg_duration,
                'success_by_event_type': success_by_type
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get performance metrics error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DEMO AND TESTING
# ============================================================================

async def create_sample_events():
    """Create sample events for demonstration"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        sample_events = [
            {
                'name': 'Daily Market Data Refresh',
                'event_type': 'data_refresh',
                'scheduled_time': datetime.now() + timedelta(minutes=1),
                'timezone': 'UTC',
                'frequency': 'custom_cron',
                'cron_expression': '0 */4 * * *',  # Every 4 hours
                'callback_function': 'data_refresh_handler',
                'priority': 7,
                'is_recurring': True
            },
            {
                'name': 'Weekly Portfolio Rebalance',
                'event_type': 'portfolio_rebalance',
                'scheduled_time': datetime.now() + timedelta(days=1),
                'timezone': 'US/Eastern',
                'frequency': 'weekly',
                'callback_function': 'portfolio_rebalance_handler',
                'priority': 8,
                'is_recurring': True
            },
            {
                'name': 'Monthly ML Model Retrain',
                'event_type': 'ml_model_retrain',
                'scheduled_time': datetime.now() + timedelta(days=7),
                'timezone': 'UTC',
                'frequency': 'monthly',
                'callback_function': 'ml_retrain_handler',
                'priority': 6,
                'is_recurring': True
            },
            {
                'name': 'Risk Check Every 2 Hours',
                'event_type': 'risk_check',
                'scheduled_time': datetime.now() + timedelta(minutes=30),
                'timezone': 'US/Eastern',
                'frequency': 'custom_cron',
                'cron_expression': '0 */2 * * *',  # Every 2 hours
                'callback_function': 'risk_check_handler',
                'priority': 9,
                'is_recurring': True
            }
        ]
        
        created_events = []
        for event_data in sample_events:
            try:
                event = await time_manager.create_event(event_data)
                created_events.append({
                    'id': event.id,
                    'name': event.name,
                    'event_type': event.event_type.value,
                    'next_execution': event.next_execution.isoformat() if event.next_execution else None
                })
            except Exception as e:
                logger.error(f"❌ Failed to create sample event: {e}")
        
        return jsonify({
            'message': f'Created {len(created_events)} sample events',
            'created_events': created_events,
            'total_requested': len(sample_events)
        })
        
    except Exception as e:
        logger.error(f"❌ Create sample events error: {e}")
        return jsonify({'error': str(e)}), 500

async def run_test():
    """Run a test event execution"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        # Create a test event
        test_event_data = {
            'name': 'Test Event',
            'event_type': 'scheduled_task',
            'scheduled_time': datetime.now() + timedelta(seconds=5),
            'timezone': 'UTC',
            'frequency': 'once',
            'callback_function': 'data_refresh_handler',
            'priority': 5,
            'is_recurring': False
        }
        
        event = await time_manager.create_event(test_event_data)
        
        return jsonify({
            'message': 'Test event created successfully',
            'event': {
                'id': event.id,
                'name': event.name,
                'scheduled_time': event.scheduled_time.isoformat(),
                'next_execution': event.next_execution.isoformat() if event.next_execution else None
            },
            'note': 'Event will execute in 5 seconds'
        })
        
    except Exception as e:
        logger.error(f"❌ Run test error: {e}")
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
app.route('/api/events', methods=['POST'])(async_route(create_event))
app.route('/api/events/<event_id>', methods=['PUT'])(async_route(update_event))
app.route('/api/events/<event_id>', methods=['DELETE'])(async_route(delete_event))
app.route('/api/demo/create-sample-events', methods=['POST'])(async_route(create_sample_events))
app.route('/api/demo/run-test', methods=['POST'])(async_route(run_test))

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("⏰ Starting Time Management API Server...")
    
    # Initialize time manager
    if not initialize_time_manager():
        print("❌ Failed to initialize time manager. Exiting.")
        exit(1)
    
    print("✅ Time manager initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/status - System status")
    print("  GET  /api/analytics - Analytics overview")
    print("  GET  /api/analytics/performance - Performance metrics")
    print("")
    print("  📅 Event Management:")
    print("  POST /api/events - Create event")
    print("  GET  /api/events - Get events")
    print("  GET  /api/events/<id> - Get specific event")
    print("  PUT  /api/events/<id> - Update event")
    print("  DELETE /api/events/<id> - Delete event")
    print("")
    print("  ⏰ Scheduling:")
    print("  GET  /api/events/upcoming - Get upcoming events")
    print("  GET  /api/executions - Get execution history")
    print("")
    print("  📈 Market & Time:")
    print("  GET  /api/market/status - Market status")
    print("  GET  /api/timezones - Available timezones")
    print("  GET  /api/event-types - Available event types")
    print("  GET  /api/frequencies - Available frequencies")
    print("")
    print("  🎯 Demo Endpoints:")
    print("  POST /api/demo/create-sample-events - Create sample events")
    print("  POST /api/demo/run-test - Run test event")
    
    # Start the server
    app.run(host='0.0.0.0', port=5004, debug=True)
