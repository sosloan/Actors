#!/usr/bin/env python3
"""
🚀 Enhanced Time Management API
Advanced features: event dependencies, smart scheduling, predictive optimization
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import our enhanced time management systems
from advanced_time_manager import AdvancedTimeManager
from advanced_time_enhancements import (
    EnhancedTimeManager, EventDependencyType, EventStatus,
    SmartScheduleRecommendation, EventExecution
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global enhanced time manager instance
enhanced_time_manager = None
base_time_manager = None

def initialize_enhanced_time_manager():
    """Initialize the enhanced time manager"""
    global enhanced_time_manager, base_time_manager
    try:
        # Initialize base time manager
        base_time_manager = AdvancedTimeManager()
        asyncio.run(base_time_manager.initialize())
        
        # Initialize enhanced time manager
        enhanced_time_manager = EnhancedTimeManager()
        
        logger.info("✅ Enhanced Time Manager initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize enhanced time manager: {e}")
        return False

# ============================================================================
# HEALTH AND STATUS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced Time Management API',
        'timestamp': time.time(),
        'enhanced_manager_active': enhanced_time_manager is not None,
        'base_manager_active': base_time_manager is not None
    })

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get detailed system status"""
    if enhanced_time_manager is None or base_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        # Get base analytics
        base_analytics = base_time_manager.get_analytics()
        
        # Get enhanced insights
        enhanced_insights = {
            'dependency_graph_size': len(enhanced_time_manager.dependency_manager.dependency_graph),
            'total_dependencies': sum(len(deps) for deps in enhanced_time_manager.dependency_manager.dependencies.values()),
            'execution_history_size': len(enhanced_time_manager.execution_history),
            'smart_scheduler_active': True
        }
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'base_analytics': {
                'total_events': base_analytics.total_events,
                'active_events': base_analytics.active_events,
                'execution_success_rate': base_analytics.execution_success_rate
            },
            'enhanced_features': enhanced_insights,
            'scheduler_running': base_time_manager.is_running
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# EVENT DEPENDENCIES
# ============================================================================

@app.route('/api/dependencies', methods=['POST'])
def create_dependency():
    """Create a dependency between events"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['source_event_id', 'target_event_id', 'dependency_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create dependency
        enhanced_time_manager.add_event_dependency(
            source_event_id=data['source_event_id'],
            target_event_id=data['target_event_id'],
            dependency_type=EventDependencyType(data['dependency_type']),
            condition=data.get('condition')
        )
        
        return jsonify({
            'message': 'Dependency created successfully',
            'dependency': {
                'source_event_id': data['source_event_id'],
                'target_event_id': data['target_event_id'],
                'dependency_type': data['dependency_type'],
                'condition': data.get('condition')
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Create dependency error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dependencies', methods=['GET'])
def get_dependencies():
    """Get all dependencies"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        dependencies = []
        
        for target_event_id, deps in enhanced_time_manager.dependency_manager.dependencies.items():
            for dep in deps:
                dependencies.append({
                    'source_event_id': dep.source_event_id,
                    'target_event_id': dep.target_event_id,
                    'dependency_type': dep.dependency_type.value,
                    'condition': dep.condition,
                    'timeout_seconds': dep.timeout_seconds,
                    'retry_count': dep.retry_count,
                    'max_retries': dep.max_retries
                })
        
        return jsonify({
            'dependencies': dependencies,
            'total_dependencies': len(dependencies)
        })
        
    except Exception as e:
        logger.error(f"❌ Get dependencies error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dependencies/<source_event_id>/<target_event_id>', methods=['DELETE'])
def delete_dependency(source_event_id, target_event_id):
    """Delete a dependency"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        enhanced_time_manager.dependency_manager.remove_dependency(source_event_id, target_event_id)
        
        return jsonify({
            'message': 'Dependency deleted successfully',
            'source_event_id': source_event_id,
            'target_event_id': target_event_id
        })
        
    except Exception as e:
        logger.error(f"❌ Delete dependency error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dependencies/execution-order', methods=['POST'])
def get_execution_order():
    """Get optimal execution order for events considering dependencies"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        data = request.get_json()
        events = data.get('events', [])
        
        if not events:
            return jsonify({'error': 'Events list is required'}), 400
        
        execution_order = enhanced_time_manager.dependency_manager.get_execution_order(events)
        
        return jsonify({
            'execution_order': execution_order,
            'total_events': len(execution_order),
            'input_events': events
        })
        
    except Exception as e:
        logger.error(f"❌ Get execution order error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SMART SCHEDULING
# ============================================================================

@app.route('/api/smart-schedule/recommendation', methods=['POST'])
def get_smart_schedule_recommendation():
    """Get smart scheduling recommendation for an event"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        data = request.get_json()
        
        event_id = data.get('event_id')
        base_time_str = data.get('base_time')
        
        if not event_id:
            return jsonify({'error': 'event_id is required'}), 400
        
        if base_time_str:
            base_time = datetime.fromisoformat(base_time_str.replace('Z', '+00:00'))
        else:
            base_time = datetime.now() + timedelta(hours=1)
        
        recommendation = enhanced_time_manager.get_smart_schedule_recommendation(event_id, base_time)
        
        return jsonify({
            'recommendation': {
                'event_id': recommendation.event_id,
                'recommended_time': recommendation.recommended_time.isoformat(),
                'confidence_score': recommendation.confidence_score,
                'reasoning': recommendation.reasoning,
                'expected_duration_ms': recommendation.expected_duration_ms,
                'resource_requirements': recommendation.resource_requirements,
                'market_conditions': recommendation.market_conditions
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get smart schedule recommendation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/smart-schedule/predict-optimal', methods=['POST'])
def predict_optimal_schedule():
    """Predict optimal schedule for multiple events"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        data = request.get_json()
        
        events = data.get('events', [])
        time_window_start = data.get('time_window_start')
        time_window_end = data.get('time_window_end')
        
        if not events:
            return jsonify({'error': 'events list is required'}), 400
        
        if not time_window_start or not time_window_end:
            return jsonify({'error': 'time_window_start and time_window_end are required'}), 400
        
        time_window = (
            datetime.fromisoformat(time_window_start.replace('Z', '+00:00')),
            datetime.fromisoformat(time_window_end.replace('Z', '+00:00'))
        )
        
        recommendations = enhanced_time_manager.predict_optimal_schedule(events, time_window)
        
        formatted_recommendations = {}
        for event_id, recommendation in recommendations.items():
            formatted_recommendations[event_id] = {
                'recommended_time': recommendation.recommended_time.isoformat(),
                'confidence_score': recommendation.confidence_score,
                'reasoning': recommendation.reasoning,
                'expected_duration_ms': recommendation.expected_duration_ms,
                'resource_requirements': recommendation.resource_requirements,
                'market_conditions': recommendation.market_conditions
            }
        
        return jsonify({
            'recommendations': formatted_recommendations,
            'total_events': len(formatted_recommendations),
            'time_window': {
                'start': time_window[0].isoformat(),
                'end': time_window[1].isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Predict optimal schedule error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PERFORMANCE INSIGHTS
# ============================================================================

@app.route('/api/insights/<event_id>', methods=['GET'])
def get_performance_insights(event_id):
    """Get performance insights for an event"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        insights = enhanced_time_manager.get_performance_insights(event_id)
        
        return jsonify({
            'event_id': event_id,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get performance insights error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/insights/all', methods=['GET'])
def get_all_performance_insights():
    """Get performance insights for all events"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        # Get all events from base manager
        events = base_time_manager.get_events()
        
        all_insights = {}
        for event in events:
            insights = enhanced_time_manager.get_performance_insights(event.id)
            all_insights[event.id] = insights
        
        return jsonify({
            'all_insights': all_insights,
            'total_events': len(all_insights),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get all performance insights error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# EXECUTION HISTORY
# ============================================================================

@app.route('/api/executions/enhanced', methods=['GET'])
def get_enhanced_execution_history():
    """Get enhanced execution history with dependency tracking"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 100, type=int)
        event_id = request.args.get('event_id')
        
        executions = enhanced_time_manager.execution_history
        
        if event_id:
            executions = [e for e in executions if e.event_id == event_id]
        
        # Sort by execution time (most recent first)
        executions.sort(key=lambda x: x.execution_time, reverse=True)
        executions = executions[:limit]
        
        # Format executions
        formatted_executions = []
        for execution in executions:
            formatted_executions.append({
                'event_id': execution.event_id,
                'execution_time': execution.execution_time.isoformat(),
                'duration_ms': execution.duration_ms,
                'status': execution.status.value,
                'result': execution.result,
                'error_message': execution.error_message,
                'metadata': execution.metadata,
                'dependencies_satisfied': execution.dependencies_satisfied,
                'triggered_events': execution.triggered_events
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
        logger.error(f"❌ Get enhanced execution history error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DEMO AND TESTING
# ============================================================================

@app.route('/api/demo/create-dependency-chain', methods=['POST'])
async def create_dependency_chain():
    """Create a sample dependency chain for demonstration"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        # Create sample events first
        sample_events = [
            {
                'id': 'data_refresh',
                'name': 'Data Refresh',
                'event_type': 'data_refresh',
                'scheduled_time': datetime.now() + timedelta(minutes=1),
                'timezone': 'UTC',
                'frequency': 'once',
                'callback_function': 'data_refresh_handler',
                'priority': 7
            },
            {
                'id': 'ml_analysis',
                'name': 'ML Analysis',
                'event_type': 'ml_model_retrain',
                'scheduled_time': datetime.now() + timedelta(minutes=2),
                'timezone': 'UTC',
                'frequency': 'once',
                'callback_function': 'ml_retrain_handler',
                'priority': 6
            },
            {
                'id': 'portfolio_rebalance',
                'name': 'Portfolio Rebalance',
                'event_type': 'portfolio_rebalance',
                'scheduled_time': datetime.now() + timedelta(minutes=3),
                'timezone': 'UTC',
                'frequency': 'once',
                'callback_function': 'portfolio_rebalance_handler',
                'priority': 8
            },
            {
                'id': 'risk_check',
                'name': 'Risk Check',
                'event_type': 'risk_check',
                'scheduled_time': datetime.now() + timedelta(minutes=4),
                'timezone': 'UTC',
                'frequency': 'once',
                'callback_function': 'risk_check_handler',
                'priority': 9
            }
        ]
        
        # Create events in base manager
        created_events = []
        for event_data in sample_events:
            try:
                event = await base_time_manager.create_event(event_data)
                created_events.append(event.id)
            except Exception as e:
                logger.error(f"❌ Failed to create sample event: {e}")
        
        # Create dependency chain
        dependencies = [
            ('data_refresh', 'ml_analysis', EventDependencyType.SEQUENTIAL),
            ('ml_analysis', 'portfolio_rebalance', EventDependencyType.CONDITIONAL),
            ('portfolio_rebalance', 'risk_check', EventDependencyType.SEQUENTIAL)
        ]
        
        created_dependencies = []
        for source, target, dep_type in dependencies:
            enhanced_time_manager.add_event_dependency(source, target, dep_type)
            created_dependencies.append({
                'source': source,
                'target': target,
                'type': dep_type.value
            })
        
        return jsonify({
            'message': 'Dependency chain created successfully',
            'created_events': created_events,
            'created_dependencies': created_dependencies,
            'execution_order': enhanced_time_manager.dependency_manager.get_execution_order(created_events)
        })
        
    except Exception as e:
        logger.error(f"❌ Create dependency chain error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/smart-scheduling', methods=['POST'])
def demo_smart_scheduling():
    """Demo smart scheduling capabilities"""
    if enhanced_time_manager is None:
        return jsonify({'error': 'Enhanced time manager not initialized'}), 500
    
    try:
        # Simulate some execution history for learning
        sample_executions = [
            EventExecution(
                event_id='data_refresh',
                execution_time=datetime.now() - timedelta(hours=2),
                duration_ms=1500,
                status=EventStatus.COMPLETED,
                result={'records_updated': 1000}
            ),
            EventExecution(
                event_id='ml_analysis',
                execution_time=datetime.now() - timedelta(hours=1),
                duration_ms=3000,
                status=EventStatus.COMPLETED,
                result={'models_updated': 3}
            ),
            EventExecution(
                event_id='portfolio_rebalance',
                execution_time=datetime.now() - timedelta(minutes=30),
                duration_ms=2000,
                status=EventStatus.COMPLETED,
                result={'positions_adjusted': 15}
            )
        ]
        
        # Add to smart scheduler
        for execution in sample_executions:
            enhanced_time_manager.smart_scheduler.add_execution_history(execution)
        
        # Get smart recommendations
        base_time = datetime.now() + timedelta(hours=1)
        recommendations = {}
        
        for event_id in ['data_refresh', 'ml_analysis', 'portfolio_rebalance']:
            recommendation = enhanced_time_manager.get_smart_schedule_recommendation(event_id, base_time)
            recommendations[event_id] = {
                'recommended_time': recommendation.recommended_time.isoformat(),
                'confidence_score': recommendation.confidence_score,
                'reasoning': recommendation.reasoning,
                'expected_duration_ms': recommendation.expected_duration_ms
            }
        
        return jsonify({
            'message': 'Smart scheduling demo completed',
            'sample_executions_added': len(sample_executions),
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"❌ Smart scheduling demo error: {e}")
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
app.route('/api/demo/create-dependency-chain', methods=['POST'])(async_route(create_dependency_chain))

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Enhanced Time Management API Server...")
    
    # Initialize enhanced time manager
    if not initialize_enhanced_time_manager():
        print("❌ Failed to initialize enhanced time manager. Exiting.")
        exit(1)
    
    print("✅ Enhanced time manager initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/status - System status")
    print("")
    print("  🔗 Event Dependencies:")
    print("  POST /api/dependencies - Create dependency")
    print("  GET  /api/dependencies - Get all dependencies")
    print("  DELETE /api/dependencies/<source>/<target> - Delete dependency")
    print("  POST /api/dependencies/execution-order - Get execution order")
    print("")
    print("  🤖 Smart Scheduling:")
    print("  POST /api/smart-schedule/recommendation - Get smart recommendation")
    print("  POST /api/smart-schedule/predict-optimal - Predict optimal schedule")
    print("")
    print("  📊 Performance Insights:")
    print("  GET  /api/insights/<event_id> - Get event insights")
    print("  GET  /api/insights/all - Get all insights")
    print("")
    print("  📋 Execution History:")
    print("  GET  /api/executions/enhanced - Get enhanced execution history")
    print("")
    print("  🎯 Demo Endpoints:")
    print("  POST /api/demo/create-dependency-chain - Create dependency chain")
    print("  POST /api/demo/smart-scheduling - Demo smart scheduling")
    
    # Start the server
    app.run(host='0.0.0.0', port=5005, debug=True)
