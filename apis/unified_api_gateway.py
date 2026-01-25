#!/usr/bin/env python3
"""
🚀 ACTORS Unified API Gateway
Comprehensive API gateway integrating all ACTORS systems
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from pathlib import Path

# Import all our systems
from embedding_search import EmbeddingSearchEngine
from ml_pipeline_integration import MLEnhancedSpeechToTradingSystem
from speech_to_trading_connector import SpeechToTradingConnector, AudioSource
from advanced_time_manager import AdvancedTimeManager
from geospatial_engine import GeospatialEngine, GDAL_AVAILABLE
from database.config import GeospatialConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global system instances
search_engine = None
ml_speech_system = None
speech_connector = None
time_manager = None
geospatial_engine = None

def initialize_systems():
    """Initialize all ACTORS systems"""
    global search_engine, ml_speech_system, speech_connector, time_manager, geospatial_engine
    
    success_count = 0
    total_systems = 5
    
    # Initialize Embedding Search Engine
    try:
        search_engine = EmbeddingSearchEngine("md_embeddings.jsonl")
        search_engine.load_embeddings()
        logger.info("✅ Embedding search engine initialized")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize search engine: {e}")
    
    # Initialize ML-Enhanced Speech-to-Trading System
    try:
        ml_speech_system = MLEnhancedSpeechToTradingSystem()
        asyncio.run(ml_speech_system.initialize())
        logger.info("✅ ML-Enhanced Speech-to-Trading system initialized")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML speech system: {e}")
    
    # Initialize Speech-to-Trading Connector
    try:
        speech_connector = SpeechToTradingConnector()
        logger.info("✅ Speech-to-Trading connector initialized")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize speech connector: {e}")
    
    # Initialize Advanced Time Manager
    try:
        time_manager = AdvancedTimeManager()
        asyncio.run(time_manager.initialize())
        logger.info("✅ Advanced Time Manager initialized")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize time manager: {e}")
    
    # Initialize Geospatial Engine
    try:
        if GDAL_AVAILABLE:
            config = GeospatialConfig()
            geospatial_engine = GeospatialEngine(cache_dir=config.cache_dir)
            asyncio.run(geospatial_engine.initialize())
            logger.info("✅ Geospatial engine initialized")
            success_count += 1
        else:
            logger.warning("⚠️  GDAL not available - Geospatial features disabled")
    except Exception as e:
        logger.error(f"❌ Failed to initialize geospatial engine: {e}")
    
    return success_count == total_systems

# ============================================================================
# SYSTEM HEALTH AND STATUS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check for all systems"""
    systems_status = {
        'embedding_search': search_engine is not None,
        'ml_speech_system': ml_speech_system is not None,
        'speech_connector': speech_connector is not None,
        'time_manager': time_manager is not None,
        'geospatial_engine': geospatial_engine is not None
    }
    
    overall_health = all(systems_status.values())
    
    return jsonify({
        'status': 'healthy' if overall_health else 'degraded',
        'service': 'ACTORS Unified API Gateway',
        'timestamp': time.time(),
        'systems': systems_status,
        'gdal_available': GDAL_AVAILABLE,
        'uptime': time.time() - start_time if 'start_time' in globals() else 0
    })

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get detailed system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'systems': {}
    }
    
    # Embedding Search Engine Status
    if search_engine:
        try:
            stats = search_engine.get_statistics()
            status['systems']['embedding_search'] = {
                'status': 'healthy',
                'total_embeddings': stats.get('total_embeddings', 0),
                'average_similarity': stats.get('average_similarity', 0),
                'last_updated': stats.get('last_updated', 'unknown')
            }
        except Exception as e:
            status['systems']['embedding_search'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        status['systems']['embedding_search'] = {'status': 'not_initialized'}
    
    # ML Speech System Status
    if ml_speech_system:
        try:
            ml_status = asyncio.run(ml_speech_system.get_system_status())
            status['systems']['ml_speech_system'] = {
                'status': 'healthy',
                'total_enhanced_signals': ml_status.get('total_enhanced_signals', 0),
                'high_priority_signals': ml_status.get('high_priority_signals', 0),
                'ml_pipeline_active': ml_status.get('ml_pipeline_health', {}).get('is_active', False)
            }
        except Exception as e:
            status['systems']['ml_speech_system'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        status['systems']['ml_speech_system'] = {'status': 'not_initialized'}
    
    # Speech Connector Status
    if speech_connector:
        try:
            recent_signals = speech_connector.get_recent_signals(limit=5)
            status['systems']['speech_connector'] = {
                'status': 'healthy',
                'total_signals': len(speech_connector.trading_signals),
                'recent_signals': len(recent_signals)
            }
        except Exception as e:
            status['systems']['speech_connector'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        status['systems']['speech_connector'] = {'status': 'not_initialized'}
    
    return jsonify(status)

# ============================================================================
# EMBEDDING SEARCH API
# ============================================================================

@app.route('/api/embeddings/search', methods=['POST'])
def search_embeddings():
    """Search embeddings by text query"""
    if search_engine is None:
        return jsonify({'error': 'Embedding search engine not initialized'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"🔍 Searching embeddings for: '{query}' (top_k={top_k})")
        start_time = time.time()
        
        results = search_engine.search_by_text(query, top_k)
        
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata['id'],
                'path': metadata['path'],
                'chunk_index': metadata['chunk_index'],
                'similarity': result['similarity'],
                'filename': Path(metadata['path']).name
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_time_ms': round(search_time * 1000, 2)
        })
        
    except Exception as e:
        logger.error(f"❌ Embedding search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/similar/<embedding_id>', methods=['GET'])
def find_similar_embeddings(embedding_id):
    """Find embeddings similar to a specific embedding ID"""
    if search_engine is None:
        return jsonify({'error': 'Embedding search engine not initialized'}), 500
    
    try:
        top_k = request.args.get('top_k', 10, type=int)
        
        logger.info(f"🔍 Finding similar embeddings to ID: '{embedding_id}' (top_k={top_k})")
        start_time = time.time()
        
        results = search_engine.find_similar_to_id(embedding_id, top_k)
        
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'id': metadata['id'],
                'path': metadata['path'],
                'chunk_index': metadata['chunk_index'],
                'similarity': result['similarity'],
                'filename': Path(metadata['path']).name
            })
        
        return jsonify({
            'target_id': embedding_id,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_time_ms': round(search_time * 1000, 2)
        })
        
    except Exception as e:
        logger.error(f"❌ Similar embedding search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/stats', methods=['GET'])
def get_embedding_stats():
    """Get embedding statistics"""
    if search_engine is None:
        return jsonify({'error': 'Embedding search engine not initialized'}), 500
    
    try:
        stats = search_engine.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"❌ Embedding stats error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SPEECH-TO-TRADING API
# ============================================================================

async def process_audio():
    """Process audio for trading signals"""
    if speech_connector is None:
        return jsonify({'error': 'Speech connector not initialized'}), 500
    
    try:
        data = request.get_json()
        audio_text = data.get('text', '').strip()
        audio_source = data.get('source', 'financial_news')
        duration = data.get('duration', 30.0)
        
        if not audio_text:
            return jsonify({'error': 'Audio text is required'}), 400
        
        # Validate audio source
        try:
            source = AudioSource(audio_source)
        except ValueError:
            return jsonify({'error': f'Invalid audio source: {audio_source}'}), 400
        
        logger.info(f"🎤 Processing audio from {audio_source}: '{audio_text[:50]}...'")
        
        # Create audio data
        audio_data = {
            'text': audio_text,
            'source': audio_source,
            'duration': duration
        }
        
        # Process with speech connector
        signals = await speech_connector.process_audio_transcription(audio_data)
        
        # Format results
        formatted_signals = []
        for signal in signals:
            formatted_signals.append({
                'signal_type': signal.signal_type.value,
                'symbol': signal.symbol,
                'confidence': signal.confidence,
                'reasoning': signal.reasoning,
                'source': signal.source.value,
                'timestamp': signal.timestamp.isoformat(),
                'risk_level': signal.risk_level
            })
        
        return jsonify({
            'audio_text': audio_text,
            'source': audio_source,
            'signals': formatted_signals,
            'total_signals': len(formatted_signals)
        })
        
    except Exception as e:
        logger.error(f"❌ Audio processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/speech/signals', methods=['GET'])
def get_trading_signals():
    """Get recent trading signals"""
    if speech_connector is None:
        return jsonify({'error': 'Speech connector not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 10, type=int)
        symbol = request.args.get('symbol', None)
        source = request.args.get('source', None)
        
        # Get signals based on filters
        if symbol:
            signals = speech_connector.get_signals_by_symbol(symbol)
        elif source:
            try:
                source_enum = AudioSource(source)
                signals = speech_connector.get_signals_by_source(source_enum)
            except ValueError:
                return jsonify({'error': f'Invalid source: {source}'}), 400
        else:
            signals = speech_connector.get_recent_signals(limit)
        
        # Format results
        formatted_signals = []
        for signal in signals:
            formatted_signals.append({
                'signal_type': signal.signal_type.value,
                'symbol': signal.symbol,
                'confidence': signal.confidence,
                'reasoning': signal.reasoning,
                'source': signal.source.value,
                'timestamp': signal.timestamp.isoformat(),
                'risk_level': signal.risk_level
            })
        
        return jsonify({
            'signals': formatted_signals,
            'total_signals': len(formatted_signals),
            'filters': {
                'symbol': symbol,
                'source': source,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get signals error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ML-ENHANCED SPEECH-TO-TRADING API
# ============================================================================

async def process_audio_with_ml():
    """Process audio with ML enhancement"""
    if ml_speech_system is None:
        return jsonify({'error': 'ML speech system not initialized'}), 500
    
    try:
        data = request.get_json()
        audio_text = data.get('text', '').strip()
        audio_source = data.get('source', 'financial_news')
        duration = data.get('duration', 30.0)
        
        if not audio_text:
            return jsonify({'error': 'Audio text is required'}), 400
        
        logger.info(f"🤖 Processing audio with ML from {audio_source}: '{audio_text[:50]}...'")
        
        # Create audio data
        audio_data = {
            'text': audio_text,
            'source': audio_source,
            'duration': duration
        }
        
        # Process with ML enhancement
        enhanced_signals = await ml_speech_system.process_audio_with_ml(audio_data)
        
        # Format results
        formatted_signals = []
        for signal in enhanced_signals:
            base = signal.base_signal
            formatted_signals.append({
                'base_signal': {
                    'signal_type': base.signal_type.value,
                    'symbol': base.symbol,
                    'confidence': base.confidence,
                    'reasoning': base.reasoning,
                    'source': base.source.value,
                    'timestamp': base.timestamp.isoformat(),
                    'risk_level': base.risk_level
                },
                'ml_enhancement': {
                    'enhanced_confidence': signal.enhanced_confidence,
                    'risk_score': signal.risk_score,
                    'market_impact_prediction': signal.market_impact_prediction,
                    'execution_priority': signal.execution_priority,
                    'ml_predictions_count': len(signal.ml_predictions)
                },
                'ml_predictions': [
                    {
                        'model_type': pred.model_type.value,
                        'confidence': pred.confidence,
                        'features_used': pred.features_used,
                        'timestamp': pred.timestamp.isoformat(),
                        'model_version': pred.model_version
                    }
                    for pred in signal.ml_predictions
                ]
            })
        
        return jsonify({
            'audio_text': audio_text,
            'source': audio_source,
            'enhanced_signals': formatted_signals,
            'total_signals': len(formatted_signals)
        })
        
    except Exception as e:
        logger.error(f"❌ ML audio processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-speech/signals', methods=['GET'])
def get_enhanced_signals():
    """Get ML-enhanced trading signals"""
    if ml_speech_system is None:
        return jsonify({'error': 'ML speech system not initialized'}), 500
    
    try:
        limit = request.args.get('limit', 10, type=int)
        min_priority = request.args.get('min_priority', None, type=int)
        
        # Get signals based on filters
        if min_priority:
            signals = ml_speech_system.get_signals_by_priority(min_priority)
        else:
            signals = ml_speech_system.get_enhanced_signals(limit)
        
        # Format results
        formatted_signals = []
        for signal in signals:
            base = signal.base_signal
            formatted_signals.append({
                'base_signal': {
                    'signal_type': base.signal_type.value,
                    'symbol': base.symbol,
                    'confidence': base.confidence,
                    'reasoning': base.reasoning,
                    'source': base.source.value,
                    'timestamp': base.timestamp.isoformat(),
                    'risk_level': base.risk_level
                },
                'ml_enhancement': {
                    'enhanced_confidence': signal.enhanced_confidence,
                    'risk_score': signal.risk_score,
                    'market_impact_prediction': signal.market_impact_prediction,
                    'execution_priority': signal.execution_priority
                }
            })
        
        return jsonify({
            'enhanced_signals': formatted_signals,
            'total_signals': len(formatted_signals),
            'filters': {
                'limit': limit,
                'min_priority': min_priority
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get enhanced signals error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYTICS AND INSIGHTS API
# ============================================================================

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get comprehensive analytics overview"""
    try:
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'systems': {}
        }
        
        # Embedding Search Analytics
        if search_engine:
            try:
                stats = search_engine.get_statistics()
                analytics['systems']['embedding_search'] = {
                    'total_embeddings': stats.get('total_embeddings', 0),
                    'average_similarity': stats.get('average_similarity', 0),
                    'status': 'healthy'
                }
            except Exception as e:
                analytics['systems']['embedding_search'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Speech-to-Trading Analytics
        if speech_connector:
            try:
                recent_signals = speech_connector.get_recent_signals(limit=100)
                signal_types = {}
                sources = {}
                
                for signal in recent_signals:
                    # Count signal types
                    signal_type = signal.signal_type.value
                    signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
                    
                    # Count sources
                    source = signal.source.value
                    sources[source] = sources.get(source, 0) + 1
                
                analytics['systems']['speech_trading'] = {
                    'total_signals': len(speech_connector.trading_signals),
                    'recent_signals': len(recent_signals),
                    'signal_types': signal_types,
                    'sources': sources,
                    'status': 'healthy'
                }
            except Exception as e:
                analytics['systems']['speech_trading'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # ML-Enhanced System Analytics
        if ml_speech_system:
            try:
                ml_status = asyncio.run(ml_speech_system.get_system_status())
                enhanced_signals = ml_speech_system.get_enhanced_signals(limit=100)
                high_priority = ml_speech_system.get_signals_by_priority(min_priority=7)
                
                analytics['systems']['ml_enhanced'] = {
                    'total_enhanced_signals': ml_status.get('total_enhanced_signals', 0),
                    'high_priority_signals': len(high_priority),
                    'ml_pipeline_active': ml_status.get('ml_pipeline_health', {}).get('is_active', False),
                    'recent_enhanced_signals': len(enhanced_signals),
                    'status': 'healthy'
                }
            except Exception as e:
                analytics['systems']['ml_enhanced'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"❌ Analytics overview error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/performance', methods=['GET'])
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'performance': {}
        }
        
        # Calculate performance metrics for each system
        if search_engine:
            try:
                # Simulate performance test
                start_time = time.time()
                test_results = search_engine.search_by_text("test query", 5)
                search_time = (time.time() - start_time) * 1000
                
                metrics['performance']['embedding_search'] = {
                    'search_latency_ms': round(search_time, 2),
                    'status': 'healthy'
                }
            except Exception as e:
                metrics['performance']['embedding_search'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        if speech_connector:
            try:
                # Get signal processing metrics
                total_signals = len(speech_connector.trading_signals)
                recent_signals = speech_connector.get_recent_signals(limit=10)
                
                metrics['performance']['speech_trading'] = {
                    'total_signals_processed': total_signals,
                    'recent_signals': len(recent_signals),
                    'status': 'healthy'
                }
            except Exception as e:
                metrics['performance']['speech_trading'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        if ml_speech_system:
            try:
                ml_status = asyncio.run(ml_speech_system.get_system_status())
                ml_health = ml_status.get('ml_pipeline_health', {})
                
                metrics['performance']['ml_enhanced'] = {
                    'ml_pipeline_active': ml_health.get('is_active', False),
                    'total_models': ml_health.get('total_models', 0),
                    'status': 'healthy'
                }
            except Exception as e:
                metrics['performance']['ml_enhanced'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"❌ Performance metrics error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# TIME MANAGEMENT API
# ============================================================================

@app.route('/api/time/events', methods=['GET'])
def get_time_events():
    """Get time events"""
    if time_manager is None:
        return jsonify({'error': 'Time manager not initialized'}), 500
    
    try:
        # Get query parameters for filtering
        event_type = request.args.get('event_type')
        is_active = request.args.get('is_active')
        
        # Build filters
        filters = {}
        if event_type:
            from advanced_time_manager import TimeEventType
            filters['event_type'] = TimeEventType(event_type)
        if is_active is not None:
            filters['is_active'] = is_active.lower() == 'true'
        
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
                'priority': event.priority,
                'is_active': event.is_active,
                'is_recurring': event.is_recurring,
                'next_execution': event.next_execution.isoformat() if event.next_execution else None,
                'execution_count': event.execution_count
            })
        
        return jsonify({
            'events': formatted_events,
            'total_events': len(formatted_events)
        })
        
    except Exception as e:
        logger.error(f"❌ Get time events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/time/upcoming', methods=['GET'])
def get_upcoming_time_events():
    """Get upcoming time events"""
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
                'is_recurring': event.is_recurring
            })
        
        return jsonify({
            'upcoming_events': formatted_events,
            'total_upcoming': len(formatted_events)
        })
        
    except Exception as e:
        logger.error(f"❌ Get upcoming time events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/time/market-status', methods=['GET'])
def get_market_status():
    """Get market status"""
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

@app.route('/api/time/analytics', methods=['GET'])
def get_time_analytics():
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
                'execution_success_rate': analytics.execution_success_rate,
                'average_execution_time_ms': analytics.average_execution_time_ms,
                'events_by_type': analytics.events_by_type,
                'events_by_frequency': analytics.events_by_frequency
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Get time analytics error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DEMO AND TESTING ENDPOINTS
# ============================================================================

async def demo_speech_trading():
    """Demo speech-to-trading functionality"""
    if speech_connector is None:
        return jsonify({'error': 'Speech connector not initialized'}), 500
    
    try:
        # Demo audio data
        demo_audio_data = [
            {
                'text': 'AAPL earnings beat expectations with strong revenue growth in Q4',
                'source': 'earnings_call',
                'duration': 45.0
            },
            {
                'text': 'TSLA stock surges on positive analyst upgrade and strong delivery numbers',
                'source': 'financial_news',
                'duration': 30.0
            }
        ]
        
        results = []
        for audio_data in demo_audio_data:
            signals = await speech_connector.process_audio_transcription(audio_data)
            
            formatted_signals = []
            for signal in signals:
                formatted_signals.append({
                    'signal_type': signal.signal_type.value,
                    'symbol': signal.symbol,
                    'confidence': signal.confidence,
                    'reasoning': signal.reasoning,
                    'source': signal.source.value,
                    'timestamp': signal.timestamp.isoformat(),
                    'risk_level': signal.risk_level
                })
            
            results.append({
                'audio_data': audio_data,
                'signals': formatted_signals
            })
        
        return jsonify({
            'demo_results': results,
            'total_audio_sources': len(demo_audio_data),
            'total_signals': sum(len(r['signals']) for r in results)
        })
        
    except Exception as e:
        logger.error(f"❌ Speech trading demo error: {e}")
        return jsonify({'error': str(e)}), 500

async def demo_ml_enhanced():
    """Demo ML-enhanced speech-to-trading functionality"""
    if ml_speech_system is None:
        return jsonify({'error': 'ML speech system not initialized'}), 500
    
    try:
        # Demo audio data
        demo_audio_data = [
            {
                'text': 'AAPL earnings beat expectations with strong revenue growth in Q4',
                'source': 'earnings_call',
                'duration': 45.0
            },
            {
                'text': 'TSLA stock surges on positive analyst upgrade and strong delivery numbers',
                'source': 'financial_news',
                'duration': 30.0
            }
        ]
        
        results = []
        for audio_data in demo_audio_data:
            enhanced_signals = await ml_speech_system.process_audio_with_ml(audio_data)
            
            formatted_signals = []
            for signal in enhanced_signals:
                base = signal.base_signal
                formatted_signals.append({
                    'base_signal': {
                        'signal_type': base.signal_type.value,
                        'symbol': base.symbol,
                        'confidence': base.confidence,
                        'reasoning': base.reasoning,
                        'source': base.source.value,
                        'timestamp': base.timestamp.isoformat(),
                        'risk_level': base.risk_level
                    },
                    'ml_enhancement': {
                        'enhanced_confidence': signal.enhanced_confidence,
                        'risk_score': signal.risk_score,
                        'market_impact_prediction': signal.market_impact_prediction,
                        'execution_priority': signal.execution_priority,
                        'ml_predictions_count': len(signal.ml_predictions)
                    }
                })
            
            results.append({
                'audio_data': audio_data,
                'enhanced_signals': formatted_signals
            })
        
        return jsonify({
            'demo_results': results,
            'total_audio_sources': len(demo_audio_data),
            'total_enhanced_signals': sum(len(r['enhanced_signals']) for r in results)
        })
        
    except Exception as e:
        logger.error(f"❌ ML enhanced demo error: {e}")
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
app.route('/api/speech/process', methods=['POST'])(async_route(process_audio))
app.route('/api/ml-speech/process', methods=['POST'])(async_route(process_audio_with_ml))
app.route('/api/demo/speech-trading', methods=['POST'])(async_route(demo_speech_trading))
app.route('/api/demo/ml-enhanced', methods=['POST'])(async_route(demo_ml_enhanced))

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting ACTORS Unified API Gateway...")
    
    # Record start time
    start_time = time.time()
    
    # Initialize all systems
    if not initialize_systems():
        print("❌ Failed to initialize all systems. Some features may not be available.")
    
    print("✅ Systems initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/status - System status")
    print("  GET  /api/analytics/overview - Analytics overview")
    print("  GET  /api/analytics/performance - Performance metrics")
    print("")
    print("  📚 Embedding Search:")
    print("  POST /api/embeddings/search - Search embeddings")
    print("  GET  /api/embeddings/similar/<id> - Find similar embeddings")
    print("  GET  /api/embeddings/stats - Embedding statistics")
    print("")
    print("  🎤 Speech-to-Trading:")
    print("  POST /api/speech/process - Process audio for trading signals")
    print("  GET  /api/speech/signals - Get trading signals")
    print("")
    print("  🤖 ML-Enhanced Speech-to-Trading:")
    print("  POST /api/ml-speech/process - Process audio with ML enhancement")
    print("  GET  /api/ml-speech/signals - Get ML-enhanced signals")
    print("")
    print("  ⏰ Time Management:")
    print("  GET  /api/time/events - Get time events")
    print("  GET  /api/time/upcoming - Get upcoming events")
    print("  GET  /api/time/market-status - Get market status")
    print("  GET  /api/time/analytics - Get time analytics")
    print("")
    print("  🎯 Demo Endpoints:")
    print("  POST /api/demo/speech-trading - Demo speech-to-trading")
    print("  POST /api/demo/ml-enhanced - Demo ML-enhanced system")
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True)
