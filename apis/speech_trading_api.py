#!/usr/bin/env python3
"""
🎤➡️📈 Speech-to-Trading API Server
RESTful API for audio-driven trading signal generation
"""

import asyncio
import hashlib
import functools
import json
import time
import uuid
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
from api_database import get_api_store

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
# SIGNAL FORMATTERS
# ============================================================================

_CONFIDENCE_MULTIPLIER = 6
_MIN_URGENCY = 1
_MAX_URGENCY = 10
_RISK_WEIGHT = {'high': 4, 'medium': 2, 'low': 1}
_RISK_LEVEL_EXPIRY_MINUTES = {'high': 5, 'medium': 30, 'low': 120}


def _format_signal(signal) -> Dict[str, Any]:
    """Format a TradingSignal with enhanced fields"""
    confidence = signal.confidence
    risk_level = signal.risk_level
    signal_type = signal.signal_type.value

    if confidence >= 0.75:
        confidence_tier = "high"
    elif confidence >= 0.4:
        confidence_tier = "medium"
    else:
        confidence_tier = "low"

    risk_weight = _RISK_WEIGHT.get(risk_level, 1)
    urgency_score = min(_MAX_URGENCY, max(_MIN_URGENCY, int(confidence * _CONFIDENCE_MULTIPLIER + risk_weight)))

    if signal_type == 'buy':
        recommended_action = "Strong Buy" if confidence >= 0.75 else "Buy"
    elif signal_type == 'sell':
        recommended_action = "Strong Sell" if confidence >= 0.75 else "Sell"
    elif signal_type == 'hedge':
        recommended_action = "Hedge"
    else:
        recommended_action = "Hold"

    expiry_minutes = _RISK_LEVEL_EXPIRY_MINUTES.get(risk_level, 30)
    expires_at = (signal.timestamp + timedelta(minutes=expiry_minutes)).isoformat()

    raw = f"{signal.symbol}:{signal_type}:{signal.timestamp.isoformat()}"
    signal_id = hashlib.sha256(raw.encode()).hexdigest()[:12]

    return {
        'signal_id': signal_id,
        'signal_type': signal_type,
        'symbol': signal.symbol,
        'confidence': confidence,
        'confidence_tier': confidence_tier,
        'urgency_score': urgency_score,
        'recommended_action': recommended_action,
        'reasoning': signal.reasoning,
        'source': signal.source.value,
        'timestamp': signal.timestamp.isoformat(),
        'expires_at': expires_at,
        'risk_level': risk_level
    }


def _format_enhanced_signal(signal, include_predictions: bool = False) -> Dict[str, Any]:
    """Format an EnhancedTradingSignal with enhanced fields"""
    base = signal.base_signal
    formatted_base = _format_signal(base)

    confidence_delta = round(signal.enhanced_confidence - base.confidence, 4)

    ml_consensus = True
    if signal.ml_predictions:
        supporting = sum(1 for p in signal.ml_predictions if p.confidence >= 0.5)
        ml_consensus = supporting >= len(signal.ml_predictions) / 2

    priority = signal.execution_priority
    if priority >= 8:
        priority_label = "Critical"
    elif priority >= 6:
        priority_label = "High"
    elif priority >= 4:
        priority_label = "Normal"
    else:
        priority_label = "Low"

    result = {
        'base_signal': formatted_base,
        'ml_enhancement': {
            'enhanced_confidence': signal.enhanced_confidence,
            'confidence_delta': confidence_delta,
            'risk_score': signal.risk_score,
            'market_impact_prediction': signal.market_impact_prediction,
            'execution_priority': signal.execution_priority,
            'priority_label': priority_label,
            'ml_consensus': ml_consensus,
            'ml_predictions_count': len(signal.ml_predictions)
        }
    }

    if include_predictions:
        result['ml_predictions'] = [
            {
                'model_type': pred.model_type.value,
                'confidence': pred.confidence,
                'features_used': pred.features_used,
                'timestamp': pred.timestamp.isoformat(),
                'model_version': pred.model_version
            }
            for pred in signal.ml_predictions
        ]

    return result


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

        if duration is not None and duration <= 0:
            return jsonify({'error': 'Duration must be a positive number'}), 400

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
        formatted_signals = [_format_signal(s) for s in signals]

        # Persist each signal to the database
        db = get_api_store()
        for raw, fmt in zip(signals, formatted_signals):
            tickers = getattr(raw, 'tickers', None) or []
            db.store_trading_signal(
                signal_id=str(uuid.uuid4()),
                signal_type=raw.signal_type.value if hasattr(raw.signal_type, 'value') else str(raw.signal_type),
                ticker=tickers[0] if tickers else None,
                confidence=getattr(raw, 'confidence', None),
                risk_level=getattr(raw, 'risk_level', None),
                price_target=getattr(raw, 'price_target', None),
                source_text=audio_text[:500],
                audio_source=audio_source,
                metadata={"urgency": fmt.get("urgency"), "confidence_tier": fmt.get("confidence_tier")},
            )

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

@app.route('/api/signals/sources', methods=['GET'])
def get_signal_sources():
    """Get all available audio source types"""
    return jsonify({
        'sources': [s.value for s in AudioSource],
        'total': len(AudioSource)
    })

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
            signals = speech_connector.get_signals_by_symbol(symbol)[:limit]
        elif source:
            try:
                source_enum = AudioSource(source)
                signals = speech_connector.get_signals_by_source(source_enum)[:limit]
            except ValueError:
                return jsonify({'error': f'Invalid source: {source}'}), 400
        else:
            signals = speech_connector.get_recent_signals(limit)
        
        # Format results
        formatted_signals = [_format_signal(s) for s in signals]
        
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

        if duration is not None and duration <= 0:
            return jsonify({'error': 'Duration must be a positive number'}), 400

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
        formatted_signals = [_format_enhanced_signal(s, include_predictions=True) for s in enhanced_signals]
        
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
        formatted_signals = [_format_enhanced_signal(s) for s in signals]
        
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
                
                avg_confidence = (
                    sum(s.confidence for s in recent_signals) / len(recent_signals)
                    if recent_signals else 0.0
                )
                analytics['systems']['speech_trading'] = {
                    'total_signals': len(speech_connector.trading_signals),
                    'recent_signals': len(recent_signals),
                    'signal_types': signal_types,
                    'sources': sources,
                    'average_confidence': round(avg_confidence, 4),
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
                
                ml_avg_confidence = (
                    sum(s.enhanced_confidence for s in enhanced_signals) / len(enhanced_signals)
                    if enhanced_signals else 0.0
                )
                analytics['systems']['ml_enhanced'] = {
                    'total_enhanced_signals': ml_status.get('total_enhanced_signals', 0),
                    'high_priority_signals': len(high_priority),
                    'ml_pipeline_active': ml_status.get('ml_pipeline_health', {}).get('is_active', False),
                    'recent_enhanced_signals': len(enhanced_signals),
                    'average_confidence': round(ml_avg_confidence, 4),
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
                avg_confidence = (
                    sum(s.confidence for s in recent_signals) / len(recent_signals)
                    if recent_signals else 0.0
                )
                metrics['performance']['speech_trading'] = {
                    'total_signals_processed': total_signals,
                    'recent_signals': len(recent_signals),
                    'average_confidence': round(avg_confidence, 4),
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
            results.append({
                'audio_data': audio_data,
                'signals': [_format_signal(s) for s in signals]
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
            results.append({
                'audio_data': audio_data,
                'enhanced_signals': [_format_enhanced_signal(s) for s in enhanced_signals]
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

@app.route('/api/signals/db/history', methods=['GET'])
def db_signal_history():
    """Retrieve trading signal history from the database"""
    try:
        ticker = request.args.get('ticker')
        limit = request.args.get('limit', 50, type=int)
        records = get_api_store().get_trading_signals(ticker=ticker, limit=limit)
        return jsonify({'count': len(records), 'records': records})
    except Exception as e:
        logger.error(f"❌ DB signal history error: {e}")
        return jsonify({'error': 'Failed to retrieve signal history'}), 500

# ============================================================================
# ASYNC ROUTE HANDLERS
# ============================================================================

def async_route(f):
    """Wrapper for async routes"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
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
