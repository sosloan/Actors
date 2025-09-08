#!/usr/bin/env python3
"""
Speech-to-Trading Connector
Integrates open-batch-transcription with ACTORS financial derivatives system
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingSignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    HEDGE = "hedge"

class AudioSource(Enum):
    EARNINGS_CALL = "earnings_call"
    FED_SPEECH = "fed_speech"
    FINANCIAL_NEWS = "financial_news"
    ANALYST_CALL = "analyst_call"
    SOCIAL_MEDIA = "social_media"

@dataclass
class FinancialEntity:
    """Represents a financial entity extracted from audio"""
    symbol: str
    entity_type: str  # "stock", "option", "currency", "commodity"
    confidence: float
    context: str

@dataclass
class SentimentAnalysis:
    """Sentiment analysis results from audio transcription"""
    overall_sentiment: float  # -1.0 to 1.0
    confidence: float
    key_phrases: List[str]
    market_impact: float  # 0.0 to 1.0

@dataclass
class TradingSignal:
    """Trading signal generated from audio analysis"""
    signal_type: TradingSignalType
    symbol: str
    confidence: float
    reasoning: str
    source: AudioSource
    timestamp: datetime
    risk_level: str  # "low", "medium", "high"

@dataclass
class AudioTranscription:
    """Audio transcription result"""
    text: str
    confidence: float
    duration: float
    source: AudioSource
    timestamp: datetime
    entities: List[FinancialEntity]
    sentiment: SentimentAnalysis

class FinancialEntityExtractor:
    """Extracts financial entities from transcribed text"""
    
    def __init__(self):
        # Common financial symbols and terms
        self.stock_symbols = {
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'TQQQ', 'SQQQ'
        }
        
        self.financial_terms = {
            'earnings', 'revenue', 'profit', 'loss', 'dividend', 'buyback',
            'merger', 'acquisition', 'ipo', 'bankruptcy', 'recession',
            'inflation', 'interest rate', 'fed', 'fomc', 'quantitative easing'
        }
    
    def extract_entities(self, text: str) -> List[FinancialEntity]:
        """Extract financial entities from text"""
        entities = []
        text_upper = text.upper()
        text_lower = text.lower()
        
        logger.info(f"Extracting entities from text: {text}")
        logger.info(f"Looking for symbols: {list(self.stock_symbols)[:5]}...")
        
        # Extract stock symbols
        for symbol in self.stock_symbols:
            if symbol in text_upper:
                confidence = 0.9
                logger.info(f"Found stock symbol: {symbol}")
                entities.append(FinancialEntity(
                    symbol=symbol,
                    entity_type="stock",
                    confidence=confidence,
                    context=self._get_context(text, symbol)
                ))
        
        # Extract financial terms
        for term in self.financial_terms:
            if term.lower() in text_lower:
                logger.info(f"Found financial term: {term}")
                entities.append(FinancialEntity(
                    symbol=term.upper(),
                    entity_type="term",
                    confidence=0.8,
                    context=self._get_context(text, term)
                ))
        
        logger.info(f"Extracted {len(entities)} entities")
        return entities
    
    def _get_context(self, text: str, entity: str) -> str:
        """Get context around an entity in the text"""
        words = text.split()
        try:
            # Find the entity (case-insensitive)
            index = next(i for i, word in enumerate(words) if word.upper() == entity.upper())
            start = max(0, index - 3)
            end = min(len(words), index + 4)
            return ' '.join(words[start:end])
        except (ValueError, StopIteration):
            return text[:100] + "..." if len(text) > 100 else text

class SentimentAnalyzer:
    """Analyzes sentiment from transcribed text"""
    
    def __init__(self):
        self.positive_words = {
            'bullish', 'positive', 'growth', 'increase', 'rise', 'gain',
            'strong', 'excellent', 'outperform', 'beat', 'exceed', 'surge'
        }
        
        self.negative_words = {
            'bearish', 'negative', 'decline', 'decrease', 'fall', 'loss',
            'weak', 'poor', 'underperform', 'miss', 'disappoint', 'crash'
        }
        
        self.market_impact_phrases = {
            'market moving', 'significant impact', 'major announcement',
            'breaking news', 'urgent', 'critical', 'game changer'
        }
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment from text"""
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate overall sentiment
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            overall_sentiment = 0.0
            confidence = 0.1  # Give some baseline confidence
        else:
            overall_sentiment = (positive_count - negative_count) / total_sentiment_words
            confidence = min(total_sentiment_words / 5.0, 1.0)  # Higher confidence multiplier
        
        # Extract key phrases
        key_phrases = []
        for phrase in self.market_impact_phrases:
            if phrase in text_lower:
                key_phrases.append(phrase)
        
        # Calculate market impact
        market_impact = min(len(key_phrases) * 0.3, 1.0)
        
        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            confidence=confidence,
            key_phrases=key_phrases,
            market_impact=market_impact
        )

class TradingSignalGenerator:
    """Generates trading signals from audio analysis"""
    
    def __init__(self):
        self.signal_threshold = 0.3  # Lower threshold for demo
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
    
    def generate_signals(self, transcription: AudioTranscription) -> List[TradingSignal]:
        """Generate trading signals from transcription"""
        signals = []
        
        # Generate signals for each financial entity
        for entity in transcription.entities:
            if entity.entity_type == "stock":
                signal = self._generate_stock_signal(entity, transcription)
                if signal:
                    signals.append(signal)
        
        return signals
    
    def _generate_stock_signal(self, entity: FinancialEntity, transcription: AudioTranscription) -> Optional[TradingSignal]:
        """Generate trading signal for a stock entity"""
        sentiment = transcription.sentiment.overall_sentiment
        confidence = min(entity.confidence * transcription.sentiment.confidence, 1.0)
        
        logger.info(f"Generating signal for {entity.symbol}: sentiment={sentiment:.2f}, confidence={confidence:.2f}, threshold={self.signal_threshold}")
        
        # Only generate signals above threshold
        if confidence < self.signal_threshold:
            logger.info(f"Signal confidence {confidence:.2f} below threshold {self.signal_threshold}")
            return None
        
        # Determine signal type based on sentiment
        if sentiment > 0.3:
            signal_type = TradingSignalType.BUY
        elif sentiment < -0.3:
            signal_type = TradingSignalType.SELL
        else:
            signal_type = TradingSignalType.HOLD
        
        # Determine risk level
        risk_level = "low"
        if transcription.sentiment.market_impact > self.risk_thresholds['high']:
            risk_level = "high"
        elif transcription.sentiment.market_impact > self.risk_thresholds['medium']:
            risk_level = "medium"
        
        # Generate reasoning
        reasoning = self._generate_reasoning(entity, transcription, signal_type)
        
        logger.info(f"Generated {signal_type.value} signal for {entity.symbol}")
        
        return TradingSignal(
            signal_type=signal_type,
            symbol=entity.symbol,
            confidence=confidence,
            reasoning=reasoning,
            source=transcription.source,
            timestamp=transcription.timestamp,
            risk_level=risk_level
        )
    
    def _generate_reasoning(self, entity: FinancialEntity, transcription: AudioTranscription, signal_type: TradingSignalType) -> str:
        """Generate reasoning for trading signal"""
        sentiment_score = transcription.sentiment.overall_sentiment
        key_phrases = ', '.join(transcription.sentiment.key_phrases)
        
        reasoning = f"Signal based on {transcription.source.value} analysis. "
        reasoning += f"Sentiment: {sentiment_score:.2f}, "
        reasoning += f"Confidence: {transcription.sentiment.confidence:.2f}. "
        
        if key_phrases:
            reasoning += f"Key phrases: {key_phrases}. "
        
        reasoning += f"Context: {entity.context}"
        
        return reasoning

class SpeechToTradingConnector:
    """Main connector between speech transcription and trading system"""
    
    def __init__(self):
        self.entity_extractor = FinancialEntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.signal_generator = TradingSignalGenerator()
        self.trading_signals = []
        
    async def process_audio_transcription(self, audio_data: Dict[str, Any]) -> List[TradingSignal]:
        """Process audio transcription and generate trading signals"""
        try:
            # Simulate transcription (in real implementation, this would call Modal)
            transcription = await self._simulate_transcription(audio_data)
            
            # Extract financial entities
            entities = self.entity_extractor.extract_entities(transcription.text)
            transcription.entities = entities
            
            # Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze_sentiment(transcription.text)
            transcription.sentiment = sentiment
            
            # Generate trading signals
            signals = self.signal_generator.generate_signals(transcription)
            
            # Store signals
            self.trading_signals.extend(signals)
            
            logger.info(f"Generated {len(signals)} trading signals from {transcription.source.value}")
            
            return signals
            
        except Exception as e:
            logger.error(f"Error processing audio transcription: {e}")
            return []
    
    async def _simulate_transcription(self, audio_data: Dict[str, Any]) -> AudioTranscription:
        """Simulate audio transcription (replace with actual Modal integration)"""
        # This would be replaced with actual Modal transcription call
        simulated_text = audio_data.get('text', 'AAPL earnings beat expectations with strong revenue growth')
        source = AudioSource(audio_data.get('source', 'earnings_call'))
        
        return AudioTranscription(
            text=simulated_text,
            confidence=0.95,
            duration=audio_data.get('duration', 30.0),
            source=source,
            timestamp=datetime.now(),
            entities=[],  # Will be populated by entity extractor
            sentiment=None  # Will be populated by sentiment analyzer
        )
    
    def get_recent_signals(self, limit: int = 10) -> List[TradingSignal]:
        """Get recent trading signals"""
        return sorted(self.trading_signals, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_signals_by_symbol(self, symbol: str) -> List[TradingSignal]:
        """Get trading signals for a specific symbol"""
        return [signal for signal in self.trading_signals if signal.symbol == symbol]
    
    def get_signals_by_source(self, source: AudioSource) -> List[TradingSignal]:
        """Get trading signals from a specific source"""
        return [signal for signal in self.trading_signals if signal.source == source]

class TradingExecutor:
    """Executes trading signals (integrates with Derivatives Gateway)"""
    
    def __init__(self, connector: SpeechToTradingConnector):
        self.connector = connector
        self.execution_threshold = 0.3  # Lower threshold for demo
        self.max_position_size = 1000  # Maximum position size per signal
        
    async def execute_signals(self, signals: List[TradingSignal]) -> List[Dict[str, Any]]:
        """Execute trading signals"""
        executed_trades = []
        
        for signal in signals:
            if signal.confidence >= self.execution_threshold:
                trade_result = await self._execute_signal(signal)
                executed_trades.append(trade_result)
        
        return executed_trades
    
    async def _execute_signal(self, signal: TradingSignal) -> Dict[str, Any]:
        """Execute a single trading signal"""
        # This would integrate with the actual Derivatives Gateway
        # For now, we'll simulate the execution
        
        trade_result = {
            'signal_id': f"{signal.symbol}_{signal.timestamp.isoformat()}",
            'symbol': signal.symbol,
            'action': signal.signal_type.value,
            'confidence': signal.confidence,
            'execution_time': datetime.now().isoformat(),
            'status': 'executed',
            'reasoning': signal.reasoning
        }
        
        logger.info(f"Executed trade: {signal.signal_type.value} {signal.symbol} "
                   f"(confidence: {signal.confidence:.2f})")
        
        return trade_result

# Example usage and testing
async def main():
    """Example usage of the Speech-to-Trading Connector"""
    
    # Initialize connector
    connector = SpeechToTradingConnector()
    executor = TradingExecutor(connector)
    
    # Simulate audio data from different sources
    test_audio_data = [
        {
            'text': 'AAPL earnings beat expectations with strong revenue growth in Q4',
            'source': 'earnings_call',
            'duration': 45.0
        },
        {
            'text': 'Fed signals potential interest rate cuts due to economic concerns',
            'source': 'fed_speech',
            'duration': 60.0
        },
        {
            'text': 'TSLA stock surges on positive analyst upgrade and strong delivery numbers',
            'source': 'financial_news',
            'duration': 30.0
        }
    ]
    
    print("🎤➡️📈 Speech-to-Trading Connector Demo")
    print("=" * 50)
    
    # Process each audio source
    for i, audio_data in enumerate(test_audio_data, 1):
        print(f"\n📊 Processing Audio Source {i}: {audio_data['source']}")
        print(f"Text: {audio_data['text']}")
        
        # Process transcription and generate signals
        signals = await connector.process_audio_transcription(audio_data)
        
        if signals:
            print(f"✅ Generated {len(signals)} trading signals:")
            for signal in signals:
                print(f"   • {signal.signal_type.value.upper()} {signal.symbol} "
                      f"(confidence: {signal.confidence:.2f}, risk: {signal.risk_level})")
                print(f"     Reasoning: {signal.reasoning}")
        else:
            print("❌ No trading signals generated")
    
    # Execute high-confidence signals
    print(f"\n🚀 Executing High-Confidence Signals...")
    all_signals = connector.get_recent_signals()
    executed_trades = await executor.execute_signals(all_signals)
    
    if executed_trades:
        print(f"✅ Executed {len(executed_trades)} trades:")
        for trade in executed_trades:
            print(f"   • {trade['action'].upper()} {trade['symbol']} "
                  f"(confidence: {trade['confidence']:.2f})")
    else:
        print("❌ No trades executed (insufficient confidence)")
    
    # Summary statistics
    print(f"\n📈 Summary Statistics:")
    print(f"   • Total signals generated: {len(connector.trading_signals)}")
    print(f"   • Trades executed: {len(executed_trades)}")
    print(f"   • Success rate: {len(executed_trades)/max(len(connector.trading_signals), 1)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
