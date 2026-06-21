#!/usr/bin/env python3
"""
🎭 HARPER HENRY HARMONY API
API endpoints for Advanced AI-driven Portfolio Optimization with Cultural Exchange Harmony
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
from datetime import datetime
import sys
import os

# Add core module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.harper_henry_harmony import (
    HarperHenryHarmony,
    HarmonyEngine as EngineType
)

app = Flask(__name__)
CORS(app)

# Initialize the Harper Henry Harmony engine
harmony_engine = HarperHenryHarmony()


@app.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'harper-henry-harmony-api',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/v1/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """
    Optimize portfolio using Harper Henry Harmony engine
    
    Request body:
    {
        "portfolio_value": 100000,
        "harmony_types": ["Family", "Cultural", "Farm", "Urban", "Religious", "Artistic", "Academic", "Healing"],
        "optimization_target": 0.90,
        "cultural_weight": 0.3,
        "economic_weight": 0.4,
        "sustainability_weight": 0.3
    }
    """
    try:
        data = request.get_json()
        
        # Extract parameters with defaults
        portfolio_value = data.get('portfolio_value', 100000)
        harmony_types = data.get('harmony_types', [
            "Family", "Cultural", "Farm", "Urban", 
            "Religious", "Artistic", "Academic", "Healing"
        ])
        optimization_target = data.get('optimization_target', 0.90)
        cultural_weight = data.get('cultural_weight', 0.3)
        economic_weight = data.get('economic_weight', 0.4)
        sustainability_weight = data.get('sustainability_weight', 0.3)
        
        # Build portfolio data
        portfolio_data = {
            'total_value': portfolio_value,
            'harmony_types': harmony_types,
            'optimization_target': optimization_target,
            'weights': {
                'cultural': cultural_weight,
                'economic': economic_weight,
                'sustainability': sustainability_weight
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Run optimization asynchronously
        result = asyncio.run(harmony_engine.optimize_harmony_portfolio(portfolio_data))
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/v1/portfolio/status', methods=['GET'])
def get_portfolio_status():
    """
    Get current portfolio status and metrics
    """
    try:
        # Mock data for now - would be retrieved from database in production
        status = {
            'total_value': 100000,
            'cultural_impact_score': 0.91,
            'economic_velocity': 0.79,
            'sustainability_score': 0.86,
            'harmony_score': 0.90,
            'optimization_confidence': 0.93,
            'active_builders': 2,
            'total_harmony_types': 8,
            'traditional_crafts_count': 3,
            'last_optimization': datetime.utcnow().isoformat(),
            'assets': [
                {
                    'id': '1',
                    'name': '🏡 Family Homestay Portfolio',
                    'type': 'homestay',
                    'harmony_type': 'Family',
                    'weight': 0.15,
                    'value': 15000,
                    'cultural_score': 0.92,
                    'economic_score': 0.78,
                    'sustainability_score': 0.88,
                    'harmony_score': 0.94
                },
                {
                    'id': '2',
                    'name': '🎭 Cultural Exchange Portfolio',
                    'type': 'cultural',
                    'harmony_type': 'Cultural',
                    'weight': 0.20,
                    'value': 20000,
                    'cultural_score': 0.98,
                    'economic_score': 0.72,
                    'sustainability_score': 0.90,
                    'harmony_score': 0.96
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/v1/harmony/builders', methods=['GET'])
def get_harmony_builders():
    """
    Get information about active harmony builders
    """
    try:
        builders = [
            {
                'id': 'builder-1',
                'name': 'Primary Harmony Builder',
                'builder_type': 'standard',
                'optimization_target': 0.90,
                'current_value': 0.87,
                'is_optimized': False,
                'slots_used': 6,
                'max_slots': 9,
                'harmony_types': ['Family', 'Cultural', 'Farm', 'Urban', 'Artistic', 'Academic']
            },
            {
                'id': 'builder-2',
                'name': 'Elite BÏG Builder',
                'builder_type': 'elite',
                'optimization_target': 0.95,
                'current_value': 0.92,
                'is_optimized': True,
                'slots_used': 9,
                'max_slots': 9,
                'harmony_types': ['Family', 'Cultural', 'Farm', 'Urban', 'Religious', 'Artistic', 'Academic', 'Healing']
            }
        ]
        
        return jsonify({
            'success': True,
            'builders': builders,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/v1/traditional-crafts', methods=['GET'])
def get_traditional_crafts():
    """
    Get information about traditional crafts in the portfolio
    """
    try:
        crafts = [
            {
                'id': 'craft-1',
                'craft_name': 'Japanese Pottery',
                'craft_type': 'ceramic',
                'difficulty_level': 0.75,
                'cultural_significance': 0.95,
                'learning_duration_hours': 120,
                'materials_available': 0.85,
                'master_artisan_available': True,
                'cultural_story_score': 0.98,
                'economic_value_score': 0.82,
                'sustainability_score': 0.90,
                'community_impact_score': 0.88
            },
            {
                'id': 'craft-2',
                'craft_name': 'Indian Textile Weaving',
                'craft_type': 'textile',
                'difficulty_level': 0.68,
                'cultural_significance': 0.92,
                'learning_duration_hours': 80,
                'materials_available': 0.90,
                'master_artisan_available': True,
                'cultural_story_score': 0.94,
                'economic_value_score': 0.78,
                'sustainability_score': 0.88,
                'community_impact_score': 0.92
            },
            {
                'id': 'craft-3',
                'craft_name': 'Mexican Woodcarving',
                'craft_type': 'wood',
                'difficulty_level': 0.72,
                'cultural_significance': 0.88,
                'learning_duration_hours': 100,
                'materials_available': 0.80,
                'master_artisan_available': True,
                'cultural_story_score': 0.90,
                'economic_value_score': 0.85,
                'sustainability_score': 0.82,
                'community_impact_score': 0.86
            }
        ]
        
        return jsonify({
            'success': True,
            'crafts': crafts,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/v1/optimization/engines', methods=['GET'])
def get_optimization_engines():
    """
    Get information about optimization engines and their results
    """
    try:
        engines = [
            {
                'id': 'opt-1',
                'timestamp': datetime.utcnow().isoformat(),
                'engine': 'harper_henry_harmony',
                'score': 0.92,
                'confidence': 0.95,
                'cultural_impact': 0.94,
                'economic_velocity': 0.82,
                'sustainability': 0.88,
                'harmony': 0.93
            },
            {
                'id': 'opt-2',
                'timestamp': datetime.utcnow().isoformat(),
                'engine': 'portfolio_optimization',
                'score': 0.89,
                'confidence': 0.90,
                'cultural_impact': 0.90,
                'economic_velocity': 0.85,
                'sustainability': 0.86,
                'harmony': 0.88
            },
            {
                'id': 'opt-3',
                'timestamp': datetime.utcnow().isoformat(),
                'engine': 'value_creation',
                'score': 0.87,
                'confidence': 0.88,
                'cultural_impact': 0.92,
                'economic_velocity': 0.78,
                'sustainability': 0.85,
                'harmony': 0.86
            }
        ]
        
        return jsonify({
            'success': True,
            'engines': engines,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """
    Get real-time system metrics
    """
    try:
        import random
        
        metrics = {
            'total_value': 100000,
            'cultural_impact_score': 0.91 + (random.random() - 0.5) * 0.05,
            'economic_velocity': 0.79 + (random.random() - 0.5) * 0.05,
            'sustainability_score': 0.86 + (random.random() - 0.5) * 0.03,
            'harmony_score': 0.90 + (random.random() - 0.5) * 0.02,
            'optimization_confidence': 0.93,
            'active_builders': 2,
            'total_harmony_types': 8,
            'traditional_crafts_count': 3,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


if __name__ == '__main__':
    import os
    
    print("🎭 Starting Harper Henry Harmony API...")
    print("📊 Mathematical precision meets cultural exchange harmony")
    print("🌐 API Server running on http://localhost:5002")
    print("\nAvailable endpoints:")
    print("  GET  /healthz                         - Health check")
    print("  POST /api/v1/portfolio/optimize       - Optimize portfolio")
    print("  GET  /api/v1/portfolio/status         - Portfolio status")
    print("  GET  /api/v1/harmony/builders         - Harmony builders")
    print("  GET  /api/v1/traditional-crafts       - Traditional crafts")
    print("  GET  /api/v1/optimization/engines     - Optimization engines")
    print("  GET  /api/v1/metrics                  - Real-time metrics")
    
    # Only enable debug mode in development environment
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    # Use localhost for local development, configure host via environment for production
    # SECURITY NOTE: In production, use a proper WSGI server (gunicorn, uwsgi) with 
    # authentication/authorization instead of the Flask development server
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    
    app.run(host=host, port=5002, debug=debug_mode)
