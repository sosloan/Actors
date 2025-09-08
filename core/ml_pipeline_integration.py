#!/usr/bin/env python3
"""
ML Pipeline Integration for Speech-to-Trading System
Integrates machine learning pipelines with audio-driven trading
"""

import asyncio
import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import pickle
import hashlib

# Import our speech-to-trading components
from speech_to_trading_connector import (
    SpeechToTradingConnector, TradingSignal, AudioTranscription,
    FinancialEntity, SentimentAnalysis, TradingSignalType, AudioSource
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelType(Enum):
    SENTIMENT_ENHANCER = "sentiment_enhancer"
    ENTITY_CLASSIFIER = "entity_classifier"
    SIGNAL_PREDICTOR = "signal_predictor"
    RISK_ASSESSOR = "risk_assessor"
    MARKET_PREDICTOR = "market_predictor"
    PORTFOLIO_OPTIMIZER = "portfolio_optimizer"

@dataclass
class MLModelConfig:
    """Configuration for ML models"""
    model_type: MLModelType
    version: str
    accuracy_threshold: float
    retrain_frequency: int  # hours
    last_trained: datetime
    performance_metrics: Dict[str, float]

@dataclass
class MLPrediction:
    """ML model prediction result"""
    model_type: MLModelType
    prediction: Any
    confidence: float
    features_used: List[str]
    timestamp: datetime
    model_version: str

@dataclass
class EnhancedTradingSignal:
    """Enhanced trading signal with ML predictions"""
    base_signal: TradingSignal
    ml_predictions: List[MLPrediction]
    enhanced_confidence: float
    risk_score: float
    market_impact_prediction: float
    execution_priority: int  # 1-10, higher = more urgent

@dataclass
class MLPipelineMetrics:
    """Metrics for ML pipeline performance"""
    total_predictions: int
    accuracy_score: float
    latency_ms: float
    model_health_scores: Dict[MLModelType, float]
    cache_hit_rate: float
    last_updated: datetime

class SentimentEnhancerModel:
    """Enhanced sentiment analysis using ML"""
    
    def __init__(self):
        self.model_type = MLModelType.SENTIMENT_ENHANCER
        self.version = "1.0.0"
        self.weights = {
            'positive_words': 0.3,
            'negative_words': 0.3,
            'context_analysis': 0.2,
            'market_phrases': 0.2
        }
        self.performance_history = deque(maxlen=1000)
    
    async def predict(self, transcription: AudioTranscription) -> MLPrediction:
        """Enhanced sentiment prediction"""
        start_time = time.time()
        
        # Extract features
        features = self._extract_features(transcription)
        
        # Apply ML-enhanced sentiment analysis
        enhanced_sentiment = self._calculate_enhanced_sentiment(features, transcription)
        
        # Calculate confidence based on feature quality
        confidence = self._calculate_confidence(features)
        
        latency = (time.time() - start_time) * 1000
        
        return MLPrediction(
            model_type=self.model_type,
            prediction=enhanced_sentiment,
            confidence=confidence,
            features_used=list(features.keys()),
            timestamp=datetime.now(),
            model_version=self.version
        )
    
    def _extract_features(self, transcription: AudioTranscription) -> Dict[str, float]:
        """Extract features for sentiment analysis"""
        text = transcription.text.lower()
        
        # Enhanced feature extraction
        features = {
            'positive_intensity': self._calculate_word_intensity(text, ['strong', 'excellent', 'outstanding', 'surge', 'beat']),
            'negative_intensity': self._calculate_word_intensity(text, ['weak', 'poor', 'disappoint', 'miss', 'decline']),
            'uncertainty_level': self._calculate_word_intensity(text, ['might', 'could', 'possibly', 'uncertain', 'volatile']),
            'market_impact_phrases': self._calculate_word_intensity(text, ['market moving', 'significant', 'major', 'breaking']),
            'financial_confidence': self._calculate_word_intensity(text, ['confident', 'certain', 'guaranteed', 'assured']),
            'time_sensitivity': self._calculate_word_intensity(text, ['urgent', 'immediate', 'now', 'today', 'soon']),
            'entity_count': len(transcription.entities),
            'text_length': len(transcription.text),
            'source_credibility': self._get_source_credibility(transcription.source)
        }
        
        return features
    
    def _calculate_word_intensity(self, text: str, words: List[str]) -> float:
        """Calculate intensity of specific words in text"""
        count = sum(1 for word in words if word in text)
        return min(count / len(words), 1.0)
    
    def _get_source_credibility(self, source: AudioSource) -> float:
        """Get credibility score for audio source"""
        credibility_scores = {
            AudioSource.EARNINGS_CALL: 0.95,
            AudioSource.FED_SPEECH: 0.90,
            AudioSource.ANALYST_CALL: 0.85,
            AudioSource.FINANCIAL_NEWS: 0.80,
            AudioSource.SOCIAL_MEDIA: 0.60
        }
        return credibility_scores.get(source, 0.70)
    
    def _calculate_enhanced_sentiment(self, features: Dict[str, float], transcription: AudioTranscription) -> Dict[str, float]:
        """Calculate enhanced sentiment using ML features"""
        # Base sentiment from original analysis
        base_sentiment = transcription.sentiment.overall_sentiment if transcription.sentiment else 0.0
        
        # Apply ML enhancements
        positive_boost = features['positive_intensity'] * 0.3
        negative_boost = features['negative_intensity'] * -0.3
        uncertainty_penalty = features['uncertainty_level'] * -0.2
        credibility_multiplier = features['source_credibility']
        
        # Calculate enhanced sentiment
        enhanced_sentiment = (base_sentiment + positive_boost + negative_boost + uncertainty_penalty) * credibility_multiplier
        
        # Ensure sentiment stays within bounds
        enhanced_sentiment = max(-1.0, min(1.0, enhanced_sentiment))
        
        return {
            'enhanced_sentiment': enhanced_sentiment,
            'sentiment_change': enhanced_sentiment - base_sentiment,
            'confidence_boost': credibility_multiplier,
            'uncertainty_factor': features['uncertainty_level']
        }
    
    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence based on feature quality"""
        # Higher confidence for more complete feature sets
        feature_completeness = len([f for f in features.values() if f > 0]) / len(features)
        
        # Higher confidence for credible sources
        source_confidence = features['source_credibility']
        
        # Higher confidence for longer, more detailed text
        text_confidence = min(features['text_length'] / 200.0, 1.0)
        
        # Combine factors
        confidence = (feature_completeness * 0.4 + source_confidence * 0.4 + text_confidence * 0.2)
        
        return min(confidence, 1.0)

class EntityClassifierModel:
    """Enhanced entity classification using ML"""
    
    def __init__(self):
        self.model_type = MLModelType.ENTITY_CLASSIFIER
        self.version = "1.0.0"
        self.entity_weights = {
            'stock': 1.0,
            'option': 0.9,
            'currency': 0.8,
            'commodity': 0.7,
            'crypto': 0.6,
            'term': 0.5
        }
    
    async def predict(self, transcription: AudioTranscription) -> MLPrediction:
        """Enhanced entity classification"""
        start_time = time.time()
        
        # Extract entity features
        features = self._extract_entity_features(transcription)
        
        # Classify and enhance entities
        enhanced_entities = self._classify_entities(features, transcription.entities)
        
        # Calculate confidence
        confidence = self._calculate_entity_confidence(enhanced_entities)
        
        latency = (time.time() - start_time) * 1000
        
        return MLPrediction(
            model_type=self.model_type,
            prediction=enhanced_entities,
            confidence=confidence,
            features_used=list(features.keys()),
            timestamp=datetime.now(),
            model_version=self.version
        )
    
    def _extract_entity_features(self, transcription: AudioTranscription) -> Dict[str, float]:
        """Extract features for entity classification"""
        text = transcription.text.lower()
        
        features = {
            'stock_mentions': self._count_entity_type(text, ['stock', 'shares', 'equity', 'ticker']),
            'option_mentions': self._count_entity_type(text, ['option', 'call', 'put', 'strike']),
            'currency_mentions': self._count_entity_type(text, ['dollar', 'euro', 'yen', 'currency']),
            'commodity_mentions': self._count_entity_type(text, ['gold', 'oil', 'silver', 'commodity']),
            'crypto_mentions': self._count_entity_type(text, ['bitcoin', 'crypto', 'blockchain', 'ethereum']),
            'financial_terms': self._count_entity_type(text, ['earnings', 'revenue', 'profit', 'dividend']),
            'market_indicators': self._count_entity_type(text, ['market', 'index', 'sector', 'industry']),
            'time_references': self._count_entity_type(text, ['quarter', 'year', 'month', 'week'])
        }
        
        return features
    
    def _count_entity_type(self, text: str, keywords: List[str]) -> float:
        """Count mentions of entity type keywords"""
        count = sum(1 for keyword in keywords if keyword in text)
        return min(count / len(keywords), 1.0)
    
    def _classify_entities(self, features: Dict[str, float], entities: List[FinancialEntity]) -> List[Dict[str, Any]]:
        """Classify and enhance entities"""
        enhanced_entities = []
        
        for entity in entities:
            # Get base classification
            entity_type = entity.entity_type
            
            # Apply ML enhancements
            type_confidence = self.entity_weights.get(entity_type, 0.5)
            
            # Calculate market relevance
            market_relevance = self._calculate_market_relevance(entity, features)
            
            # Calculate trading potential
            trading_potential = self._calculate_trading_potential(entity, features)
            
            enhanced_entity = {
                'original_entity': asdict(entity),
                'enhanced_type': entity_type,
                'type_confidence': type_confidence,
                'market_relevance': market_relevance,
                'trading_potential': trading_potential,
                'ml_confidence': min(entity.confidence * type_confidence, 1.0)
            }
            
            enhanced_entities.append(enhanced_entity)
        
        return enhanced_entities
    
    def _calculate_market_relevance(self, entity: FinancialEntity, features: Dict[str, float]) -> float:
        """Calculate market relevance score"""
        relevance = 0.5  # Base relevance
        
        # Higher relevance for stocks
        if entity.entity_type == 'stock':
            relevance += 0.3
        
        # Higher relevance for financial terms
        if entity.entity_type == 'term':
            relevance += features['financial_terms'] * 0.2
        
        return min(relevance, 1.0)
    
    def _calculate_trading_potential(self, entity: FinancialEntity, features: Dict[str, float]) -> float:
        """Calculate trading potential score"""
        potential = 0.5  # Base potential
        
        # Higher potential for stocks
        if entity.entity_type == 'stock':
            potential += 0.4
        
        # Higher potential with market indicators
        potential += features['market_indicators'] * 0.2
        
        return min(potential, 1.0)
    
    def _calculate_entity_confidence(self, enhanced_entities: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for entity classification"""
        if not enhanced_entities:
            return 0.0
        
        total_confidence = sum(entity['ml_confidence'] for entity in enhanced_entities)
        return total_confidence / len(enhanced_entities)

class SignalPredictorModel:
    """ML model for predicting trading signal success"""
    
    def __init__(self):
        self.model_type = MLModelType.SIGNAL_PREDICTOR
        self.version = "1.0.0"
        self.signal_history = deque(maxlen=10000)
        self.success_rates = defaultdict(list)
    
    async def predict(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> MLPrediction:
        """Predict signal success probability"""
        start_time = time.time()
        
        # Extract signal features
        features = self._extract_signal_features(signal, ml_predictions)
        
        # Predict success probability
        success_probability = self._predict_success(features)
        
        # Calculate confidence
        confidence = self._calculate_signal_confidence(features)
        
        latency = (time.time() - start_time) * 1000
        
        return MLPrediction(
            model_type=self.model_type,
            prediction={
                'success_probability': success_probability,
                'expected_return': self._predict_expected_return(features),
                'risk_level': self._predict_risk_level(features),
                'time_horizon': self._predict_time_horizon(features)
            },
            confidence=confidence,
            features_used=list(features.keys()),
            timestamp=datetime.now(),
            model_version=self.version
        )
    
    def _extract_signal_features(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> Dict[str, float]:
        """Extract features for signal prediction"""
        features = {
            'signal_confidence': signal.confidence,
            'signal_type_score': 1.0 if signal.signal_type == TradingSignalType.BUY else 0.5,
            'source_credibility': self._get_source_score(signal.source),
            'risk_level_score': self._get_risk_score(signal.risk_level),
            'time_since_signal': (datetime.now() - signal.timestamp).total_seconds() / 3600.0,  # hours
        }
        
        # Add ML prediction features
        for pred in ml_predictions:
            if pred.model_type == MLModelType.SENTIMENT_ENHANCER:
                sentiment_data = pred.prediction
                features['enhanced_sentiment'] = sentiment_data.get('enhanced_sentiment', 0.0)
                features['sentiment_confidence'] = pred.confidence
            elif pred.model_type == MLModelType.ENTITY_CLASSIFIER:
                features['entity_confidence'] = pred.confidence
                features['entity_count'] = len(pred.prediction)
        
        return features
    
    def _get_source_score(self, source: AudioSource) -> float:
        """Get source credibility score"""
        scores = {
            AudioSource.EARNINGS_CALL: 0.95,
            AudioSource.FED_SPEECH: 0.90,
            AudioSource.ANALYST_CALL: 0.85,
            AudioSource.FINANCIAL_NEWS: 0.80,
            AudioSource.SOCIAL_MEDIA: 0.60
        }
        return scores.get(source, 0.70)
    
    def _get_risk_score(self, risk_level: str) -> float:
        """Convert risk level to numeric score"""
        scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        return scores.get(risk_level, 0.5)
    
    def _predict_success(self, features: Dict[str, float]) -> float:
        """Predict signal success probability"""
        # Simple ML model (in production, this would be a trained model)
        base_probability = 0.5
        
        # Adjust based on features
        confidence_boost = features['signal_confidence'] * 0.3
        source_boost = features['source_credibility'] * 0.2
        sentiment_boost = abs(features.get('enhanced_sentiment', 0.0)) * 0.2
        entity_boost = features.get('entity_confidence', 0.5) * 0.1
        
        # Time decay
        time_decay = max(0.0, 1.0 - features['time_since_signal'] * 0.1)
        
        success_probability = (base_probability + confidence_boost + source_boost + 
                             sentiment_boost + entity_boost) * time_decay
        
        return min(success_probability, 1.0)
    
    def _predict_expected_return(self, features: Dict[str, float]) -> float:
        """Predict expected return percentage"""
        base_return = 0.02  # 2% base return
        
        # Adjust based on signal strength
        signal_strength = features['signal_confidence'] * features.get('enhanced_sentiment', 0.0)
        return base_return + (signal_strength * 0.05)  # Up to 5% additional return
    
    def _predict_risk_level(self, features: Dict[str, float]) -> str:
        """Predict risk level"""
        risk_score = features['risk_level_score']
        
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _predict_time_horizon(self, features: Dict[str, float]) -> int:
        """Predict optimal time horizon in hours"""
        # Shorter horizon for high-confidence signals
        base_horizon = 24  # 24 hours
        confidence_factor = 1.0 - features['signal_confidence'] * 0.5
        
        return int(base_horizon * confidence_factor)
    
    def _calculate_signal_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in signal prediction"""
        # Combine multiple confidence factors
        confidence_factors = [
            features['signal_confidence'],
            features['source_credibility'],
            features.get('sentiment_confidence', 0.5),
            features.get('entity_confidence', 0.5)
        ]
        
        return sum(confidence_factors) / len(confidence_factors)

class MLPipelineManager:
    """Manages ML models and integrates with speech-to-trading system"""
    
    def __init__(self):
        self.models = {
            MLModelType.SENTIMENT_ENHANCER: SentimentEnhancerModel(),
            MLModelType.ENTITY_CLASSIFIER: EntityClassifierModel(),
            MLModelType.SIGNAL_PREDICTOR: SignalPredictorModel(),
        }
        self.model_configs = {}
        self.prediction_cache = {}
        self.metrics = MLPipelineMetrics(
            total_predictions=0,
            accuracy_score=0.0,
            latency_ms=0.0,
            model_health_scores={},
            cache_hit_rate=0.0,
            last_updated=datetime.now()
        )
        self.is_active = False
        
        # Initialize model configurations
        self._initialize_model_configs()
    
    def _initialize_model_configs(self):
        """Initialize model configurations"""
        for model_type, model in self.models.items():
            self.model_configs[model_type] = MLModelConfig(
                model_type=model_type,
                version=model.version,
                accuracy_threshold=0.7,
                retrain_frequency=24,  # hours
                last_trained=datetime.now(),
                performance_metrics={}
            )
    
    async def initialize(self):
        """Initialize the ML pipeline"""
        logger.info("Initializing ML Pipeline Manager...")
        
        # Initialize all models
        for model_type, model in self.models.items():
            logger.info(f"Initialized {model_type.value} model v{model.version}")
        
        self.is_active = True
        logger.info("ML Pipeline Manager initialized successfully")
    
    async def enhance_trading_signal(self, signal: TradingSignal, transcription: AudioTranscription) -> EnhancedTradingSignal:
        """Enhance trading signal with ML predictions"""
        if not self.is_active:
            logger.warning("ML Pipeline not active, returning base signal")
            return self._create_basic_enhanced_signal(signal, [])
        
        start_time = time.time()
        
        # Generate ML predictions
        ml_predictions = await self._generate_ml_predictions(signal, transcription)
        
        # Calculate enhanced confidence
        enhanced_confidence = self._calculate_enhanced_confidence(signal, ml_predictions)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(signal, ml_predictions)
        
        # Predict market impact
        market_impact = self._predict_market_impact(signal, ml_predictions)
        
        # Calculate execution priority
        execution_priority = self._calculate_execution_priority(signal, ml_predictions)
        
        # Update metrics
        latency = (time.time() - start_time) * 1000
        self._update_metrics(latency)
        
        return EnhancedTradingSignal(
            base_signal=signal,
            ml_predictions=ml_predictions,
            enhanced_confidence=enhanced_confidence,
            risk_score=risk_score,
            market_impact_prediction=market_impact,
            execution_priority=execution_priority
        )
    
    async def _generate_ml_predictions(self, signal: TradingSignal, transcription: AudioTranscription) -> List[MLPrediction]:
        """Generate ML predictions for signal and transcription"""
        predictions = []
        
        # Generate predictions in parallel
        tasks = []
        
        # Sentiment enhancement
        if MLModelType.SENTIMENT_ENHANCER in self.models:
            tasks.append(self.models[MLModelType.SENTIMENT_ENHANCER].predict(transcription))
        
        # Entity classification
        if MLModelType.ENTITY_CLASSIFIER in self.models:
            tasks.append(self.models[MLModelType.ENTITY_CLASSIFIER].predict(transcription))
        
        # Wait for predictions
        if tasks:
            prediction_results = await asyncio.gather(*tasks)
            predictions.extend(prediction_results)
        
        # Signal prediction (depends on other predictions)
        if MLModelType.SIGNAL_PREDICTOR in self.models and predictions:
            signal_prediction = await self.models[MLModelType.SIGNAL_PREDICTOR].predict(signal, predictions)
            predictions.append(signal_prediction)
        
        return predictions
    
    def _calculate_enhanced_confidence(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> float:
        """Calculate enhanced confidence using ML predictions"""
        base_confidence = signal.confidence
        
        # Get ML confidence boosts
        ml_confidence_boost = 0.0
        for prediction in ml_predictions:
            ml_confidence_boost += prediction.confidence * 0.1  # 10% boost per prediction
        
        enhanced_confidence = min(base_confidence + ml_confidence_boost, 1.0)
        return enhanced_confidence
    
    def _calculate_risk_score(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> float:
        """Calculate enhanced risk score"""
        base_risk = {'low': 0.2, 'medium': 0.5, 'high': 0.8}.get(signal.risk_level, 0.5)
        
        # Adjust based on ML predictions
        risk_adjustment = 0.0
        for prediction in ml_predictions:
            if prediction.model_type == MLModelType.SIGNAL_PREDICTOR:
                pred_data = prediction.prediction
                predicted_risk = pred_data.get('risk_level', 'medium')
                predicted_risk_score = {'low': 0.2, 'medium': 0.5, 'high': 0.8}.get(predicted_risk, 0.5)
                risk_adjustment = (predicted_risk_score - base_risk) * 0.3
        
        return max(0.0, min(1.0, base_risk + risk_adjustment))
    
    def _predict_market_impact(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> float:
        """Predict market impact of the signal"""
        base_impact = 0.1  # 10% base impact
        
        # Adjust based on signal strength and ML predictions
        signal_strength = signal.confidence
        for prediction in ml_predictions:
            if prediction.model_type == MLModelType.SENTIMENT_ENHANCER:
                sentiment_data = prediction.prediction
                sentiment_impact = abs(sentiment_data.get('enhanced_sentiment', 0.0))
                base_impact += sentiment_impact * 0.2
        
        return min(base_impact, 1.0)
    
    def _calculate_execution_priority(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> int:
        """Calculate execution priority (1-10)"""
        base_priority = 5  # Medium priority
        
        # Increase priority for high-confidence signals
        if signal.confidence > 0.8:
            base_priority += 2
        elif signal.confidence > 0.6:
            base_priority += 1
        
        # Increase priority for high-impact predictions
        for prediction in ml_predictions:
            if prediction.model_type == MLModelType.SIGNAL_PREDICTOR:
                pred_data = prediction.prediction
                success_prob = pred_data.get('success_probability', 0.5)
                if success_prob > 0.8:
                    base_priority += 2
                elif success_prob > 0.6:
                    base_priority += 1
        
        return max(1, min(10, base_priority))
    
    def _create_basic_enhanced_signal(self, signal: TradingSignal, ml_predictions: List[MLPrediction]) -> EnhancedTradingSignal:
        """Create basic enhanced signal when ML pipeline is not active"""
        return EnhancedTradingSignal(
            base_signal=signal,
            ml_predictions=ml_predictions,
            enhanced_confidence=signal.confidence,
            risk_score={'low': 0.2, 'medium': 0.5, 'high': 0.8}.get(signal.risk_level, 0.5),
            market_impact_prediction=0.1,
            execution_priority=5
        )
    
    def _update_metrics(self, latency_ms: float):
        """Update pipeline metrics"""
        self.metrics.total_predictions += 1
        self.metrics.latency_ms = (self.metrics.latency_ms + latency_ms) / 2  # Running average
        self.metrics.last_updated = datetime.now()
        
        # Update model health scores
        for model_type in self.models.keys():
            self.metrics.model_health_scores[model_type] = 1.0  # All models healthy
    
    async def get_pipeline_health(self) -> Dict[str, Any]:
        """Get pipeline health status"""
        return {
            'is_active': self.is_active,
            'total_models': len(self.models),
            'active_models': len([m for m in self.models.values() if hasattr(m, 'is_healthy')]),
            'metrics': asdict(self.metrics),
            'model_configs': {k.value: asdict(v) for k, v in self.model_configs.items()}
        }

class MLEnhancedSpeechToTradingSystem:
    """Complete ML-enhanced speech-to-trading system"""
    
    def __init__(self):
        self.speech_connector = SpeechToTradingConnector()
        self.ml_pipeline = MLPipelineManager()
        self.enhanced_signals = []
        
    async def initialize(self):
        """Initialize the complete system"""
        logger.info("Initializing ML-Enhanced Speech-to-Trading System...")
        
        # Initialize ML pipeline
        await self.ml_pipeline.initialize()
        
        logger.info("System initialized successfully")
    
    async def process_audio_with_ml(self, audio_data: Dict[str, Any]) -> List[EnhancedTradingSignal]:
        """Process audio with ML enhancement"""
        # Generate base trading signals
        base_signals = await self.speech_connector.process_audio_transcription(audio_data)
        
        # Enhance signals with ML
        enhanced_signals = []
        for signal in base_signals:
            # Get transcription for ML processing
            transcription = await self._get_transcription_for_signal(signal, audio_data)
            
            # Enhance with ML
            enhanced_signal = await self.ml_pipeline.enhance_trading_signal(signal, transcription)
            enhanced_signals.append(enhanced_signal)
        
        # Store enhanced signals
        self.enhanced_signals.extend(enhanced_signals)
        
        return enhanced_signals
    
    async def _get_transcription_for_signal(self, signal: TradingSignal, audio_data: Dict[str, Any]) -> AudioTranscription:
        """Get transcription data for ML processing"""
        # Create a mock transcription with proper sentiment data
        from speech_to_trading_connector import SentimentAnalysis
        
        # Create basic sentiment analysis
        sentiment = SentimentAnalysis(
            overall_sentiment=0.5,  # Neutral sentiment
            confidence=0.8,
            key_phrases=[],
            market_impact=0.1
        )
        
        return AudioTranscription(
            text=audio_data.get('text', ''),
            confidence=0.95,
            duration=audio_data.get('duration', 30.0),
            source=signal.source,
            timestamp=signal.timestamp,
            entities=[],  # Will be populated by entity extractor
            sentiment=sentiment
        )
    
    def get_enhanced_signals(self, limit: int = 10) -> List[EnhancedTradingSignal]:
        """Get recent enhanced signals"""
        return sorted(self.enhanced_signals, key=lambda x: x.base_signal.timestamp, reverse=True)[:limit]
    
    def get_signals_by_priority(self, min_priority: int = 7) -> List[EnhancedTradingSignal]:
        """Get high-priority signals"""
        return [s for s in self.enhanced_signals if s.execution_priority >= min_priority]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        pipeline_health = await self.ml_pipeline.get_pipeline_health()
        
        return {
            'system_active': True,
            'total_enhanced_signals': len(self.enhanced_signals),
            'high_priority_signals': len(self.get_signals_by_priority()),
            'ml_pipeline_health': pipeline_health,
            'last_updated': datetime.now().isoformat()
        }

# Example usage and testing
async def main():
    """Example usage of ML-Enhanced Speech-to-Trading System"""
    
    # Initialize system
    system = MLEnhancedSpeechToTradingSystem()
    await system.initialize()
    
    # Test audio data
    test_audio_data = [
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
    
    print("🤖➡️📈 ML-Enhanced Speech-to-Trading System Demo")
    print("=" * 60)
    
    # Process audio with ML enhancement
    for i, audio_data in enumerate(test_audio_data, 1):
        print(f"\n🎤 Processing Audio Source {i}: {audio_data['source']}")
        print(f"Text: {audio_data['text']}")
        
        # Process with ML enhancement
        enhanced_signals = await system.process_audio_with_ml(audio_data)
        
        if enhanced_signals:
            print(f"✅ Generated {len(enhanced_signals)} ML-enhanced signals:")
            for signal in enhanced_signals:
                base = signal.base_signal
                print(f"   • {base.signal_type.value.upper()} {base.symbol}")
                print(f"     Base Confidence: {base.confidence:.2f}")
                print(f"     Enhanced Confidence: {signal.enhanced_confidence:.2f}")
                print(f"     Risk Score: {signal.risk_score:.2f}")
                print(f"     Execution Priority: {signal.execution_priority}/10")
                print(f"     Market Impact: {signal.market_impact_prediction:.2f}")
                print(f"     ML Predictions: {len(signal.ml_predictions)}")
                
                # Show ML prediction details
                for pred in signal.ml_predictions:
                    print(f"       - {pred.model_type.value}: {pred.confidence:.2f} confidence")
        else:
            print("❌ No enhanced signals generated")
    
    # System status
    print(f"\n📊 System Status:")
    status = await system.get_system_status()
    print(f"   • Total Enhanced Signals: {status['total_enhanced_signals']}")
    print(f"   • High Priority Signals: {status['high_priority_signals']}")
    print(f"   • ML Pipeline Active: {status['ml_pipeline_health']['is_active']}")
    print(f"   • Total Models: {status['ml_pipeline_health']['total_models']}")
    
    # High priority signals
    high_priority = system.get_signals_by_priority(min_priority=7)
    if high_priority:
        print(f"\n🚀 High Priority Signals ({len(high_priority)}):")
        for signal in high_priority:
            base = signal.base_signal
            print(f"   • {base.signal_type.value.upper()} {base.symbol} (Priority: {signal.execution_priority})")

if __name__ == "__main__":
    asyncio.run(main())
