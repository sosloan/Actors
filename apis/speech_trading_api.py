#!/usr/bin/env python3
"""
🎤➡️📈 Speech-to-Trading API Server
RESTful API for audio-driven trading signal generation
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Import our speech-to-trading systems
from speech_to_trading_connector import (
    SpeechToTradingConnector, TradingSignal, AudioTranscription,
    FinancialEntity, SentimentAnalysis, TradingSignalType, AudioSource
)
from ml_pipeline_integration import MLEnhancedSpeechToTradingSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global system instances
speech_connector = None
ml_speech_system = None

def initialize_systems():
    """Initialize speech-to-trading systems"""
    global speech_connector, ml_speech_system
    success_count = 0
    
    # Initialize basic speech connector
    try:
        speech_connector = SpeechToTradingConnector()
        logger.info("✅ Speech-to-Trading connector initialized")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize speech connector: {e}")
    
    # Initialize ML-enhanced system
    try:
        ml_speech_system = MLEnhancedSpeechToTradingSystem()
        asyncio.run(ml_speech_system.initialize())
        logger.info("✅ ML-Enhanced Speech-to-Trading system initialized")
        success_count += 1
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML speech system: {e}")
    
    return success_count == 2

# ============================================================================
# HEALTH AND STATUS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Speech-to-Trading API',
        'timestamp': time.time(),
        'speech_connector_active': speech_connector is not None,
        'ml_system_active': ml_speech_system is not None
    })

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get detailed system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'systems': {}
    }
    
    # Speech Connector Status
    if speech_connector:
        try:
            recent_signals = speech_connector.get_recent_signals(limit=10)
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
    
    # ML-Enhanced System Status
    if ml_speech_system:
        try:
            ml_status = asyncio.run(ml_speech_system.get_system_status())
            status['systems']['ml_enhanced'] = {
                'status': 'healthy',
                'total_enhanced_signals': ml_status.get('total_enhanced_signals', 0),
                'high_priority_signals': ml_status.get('high_priority_signals', 0),
                'ml_pipeline_active': ml_status.get('ml_pipeline_health', {}).get('is_active', False)
            }
        except Exception as e:
            status['systems']['ml_enhanced'] = {
                'status': 'error',
                'error': str(e)
            }
    else:
        status['systems']['ml_enhanced'] = {'status': 'not_initialized'}
    
    return jsonify(status)

# ============================================================================
# BASIC SPEECH-TO-TRADING
# ============================================================================

async def process_audio():
    """Process audio for basic trading signals"""
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
            'total_signals': len(formatted_signals),
            'processing_type': 'basic'
        })
        
    except Exception as e:
        logger.error(f"❌ Audio processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals', methods=['GET'])
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
# ML-ENHANCED SPEECH-TO-TRADING
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
            'total_signals': len(formatted_signals),
            'processing_type': 'ml_enhanced'
        })
        
    except Exception as e:
        logger.error(f"❌ ML audio processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml/signals', methods=['GET'])
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
# ANALYTICS AND INSIGHTS
# ============================================================================

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get comprehensive analytics overview"""
    try:
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'systems': {}
        }
        
        # Basic Speech-to-Trading Analytics
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
        
        # Speech-to-Trading Performance
        if speech_connector:
            try:
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
        
        # ML-Enhanced Performance
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
# DEMO ENDPOINTS
# ============================================================================

async def demo_basic_speech_trading():
    """Demo basic speech-to-trading functionality"""
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
            },
            {
                'text': 'Fed signals potential interest rate cuts due to economic concerns',
                'source': 'fed_speech',
                'duration': 60.0
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
            'total_signals': sum(len(r['signals']) for r in results),
            'demo_type': 'basic_speech_trading'
        })
        
    except Exception as e:
        logger.error(f"❌ Basic speech trading demo error: {e}")
        return jsonify({'error': str(e)}), 500

async def demo_ml_enhanced_speech_trading():
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
            'total_enhanced_signals': sum(len(r['enhanced_signals']) for r in results),
            'demo_type': 'ml_enhanced_speech_trading'
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
app.route('/api/audio/process', methods=['POST'])(async_route(process_audio))
app.route('/api/ml/process', methods=['POST'])(async_route(process_audio_with_ml))
app.route('/api/demo/basic', methods=['POST'])(async_route(demo_basic_speech_trading))
app.route('/api/demo/ml-enhanced', methods=['POST'])(async_route(demo_ml_enhanced_speech_trading))

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("🎤➡️📈 Starting Speech-to-Trading API Server...")
    
    # Initialize systems
    if not initialize_systems():
        print("❌ Failed to initialize all systems. Some features may not be available.")
    
    print("✅ Systems initialized successfully")
    print("📊 Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /api/status - System status")
    print("  GET  /api/analytics/overview - Analytics overview")
    print("  GET  /api/analytics/performance - Performance metrics")
    print("")
    print("  🎤 Basic Speech-to-Trading:")
    print("  POST /api/audio/process - Process audio for trading signals")
    print("  GET  /api/signals - Get trading signals")
    print("")
    print("  🤖 ML-Enhanced Speech-to-Trading:")
    print("  POST /api/ml/process - Process audio with ML enhancement")
    print("  GET  /api/ml/signals - Get ML-enhanced signals")
    print("")
    print("  🎯 Demo Endpoints:")
    print("  POST /api/demo/basic - Demo basic speech-to-trading")
    print("  POST /api/demo/ml-enhanced - Demo ML-enhanced system")
    
    # Start the server
    app.run(host='0.0.0.0', port=5003, debug=True)
