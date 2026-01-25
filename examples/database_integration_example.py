#!/usr/bin/env python3
"""
Example integration of DuckDB with ACTORS components
Shows how to use the database in the financial trading system
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import get_database_manager


class MarketDataCollector:
    """Example: Collecting and storing market data"""
    
    def __init__(self):
        self.db = get_database_manager()
    
    def store_tick(self, symbol, price, volume):
        """Store a market data tick"""
        data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'open': price,
            'high': price * 1.01,  # Simulated
            'low': price * 0.99,   # Simulated
            'close': price,
            'volume': volume,
            'source': 'live_feed'
        }
        
        record_id = self.db.insert_market_data(data)
        print(f"✅ Stored market data: {symbol} @ ${price:.2f} (ID: {record_id})")
        return record_id
    
    def get_recent_prices(self, symbol, limit=10):
        """Get recent prices for a symbol"""
        data = self.db.get_market_data(symbol, limit=limit)
        return [(d['timestamp'], d['close']) for d in data]


class PortfolioManager:
    """Example: Managing portfolio positions"""
    
    def __init__(self, portfolio_id):
        self.db = get_database_manager()
        self.portfolio_id = portfolio_id
    
    def open_position(self, symbol, quantity, entry_price, position_type='long'):
        """Open a new position"""
        position = {
            'portfolio_id': self.portfolio_id,
            'symbol': symbol,
            'quantity': quantity,
            'entry_price': entry_price,
            'current_price': entry_price,
            'position_type': position_type,
            'opened_at': datetime.now()
        }
        
        position_id = self.db.insert_portfolio_position(position)
        print(f"✅ Opened {position_type} position: {quantity} {symbol} @ ${entry_price:.2f}")
        return position_id
    
    def get_positions(self):
        """Get all current positions"""
        return self.db.get_portfolio_positions(self.portfolio_id)
    
    def calculate_pnl(self):
        """Calculate total P&L"""
        positions = self.get_positions()
        total_pnl = 0
        
        for pos in positions:
            current_price = pos.get('current_price', pos['entry_price'])
            pnl = (current_price - pos['entry_price']) * pos['quantity']
            
            if pos['position_type'] == 'short':
                pnl = -pnl  # Invert for short positions
            
            total_pnl += pnl
        
        return total_pnl


class TradingAgent:
    """Example: Agent that executes trades"""
    
    def __init__(self, portfolio_id, agent_id):
        self.db = get_database_manager()
        self.portfolio_id = portfolio_id
        self.agent_id = agent_id
    
    def execute_trade(self, symbol, side, quantity, price, order_type='market'):
        """Execute a trade"""
        import time
        trade = {
            'order_id': f"{self.agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{int(time.time() * 1000000) % 1000000}",
            'portfolio_id': self.portfolio_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'status': 'executed',
            'executed_at': datetime.now()
        }
        
        trade_id = self.db.insert_trade(trade)
        print(f"✅ Executed: {side.upper()} {quantity} {symbol} @ ${price:.2f}")
        return trade_id
    
    def record_performance(self, metric_name, metric_value, dimension='SPEED'):
        """Record agent performance metric"""
        metric = {
            'agent_id': self.agent_id,
            'agent_type': 'execution',
            'metric_name': metric_name,
            'metric_value': metric_value,
            'dimension': dimension,
            'timestamp': datetime.now()
        }
        
        metric_id = self.db.insert_agent_metric(metric)
        return metric_id


def demo_integration():
    """Demonstrate integrated workflow"""
    print("\n" + "=" * 60)
    print("🦞 ACTORS Database Integration Demo")
    print("=" * 60)
    
    # 1. Market Data Collection
    print("\n📊 Step 1: Collecting Market Data")
    print("-" * 60)
    collector = MarketDataCollector()
    collector.store_tick('AAPL', 150.25, 1000000)
    collector.store_tick('GOOGL', 2800.50, 500000)
    
    recent_prices = collector.get_recent_prices('AAPL', limit=3)
    print(f"\nRecent AAPL prices: {len(recent_prices)} ticks")
    
    # 2. Portfolio Management
    print("\n💼 Step 2: Managing Portfolio")
    print("-" * 60)
    portfolio = PortfolioManager('example_portfolio')
    portfolio.open_position('AAPL', 100, 150.25, 'long')
    portfolio.open_position('GOOGL', 50, 2800.50, 'long')
    
    positions = portfolio.get_positions()
    print(f"\nCurrent positions: {len(positions)}")
    
    pnl = portfolio.calculate_pnl()
    print(f"Total P&L: ${pnl:.2f}")
    
    # 3. Trading Agent
    print("\n🤖 Step 3: Agent Trading Activity")
    print("-" * 60)
    agent = TradingAgent('example_portfolio', 'execution_agent_001')
    agent.execute_trade('AAPL', 'buy', 50, 150.50, 'limit')
    agent.execute_trade('GOOGL', 'sell', 25, 2805.00, 'market')
    
    # Record performance
    agent.record_performance('success_rate', 0.95, 'SPEED')
    agent.record_performance('latency_ms', 12.5, 'SPEED')
    print("✅ Recorded agent performance metrics")
    
    # 4. Analytics Query
    print("\n📈 Step 4: Analytics & Reporting")
    print("-" * 60)
    db = get_database_manager()
    
    # Get trade summary
    query = """
        SELECT 
            symbol,
            side,
            COUNT(*) as trade_count,
            SUM(quantity) as total_quantity,
            AVG(price) as avg_price
        FROM trade_history
        WHERE portfolio_id = ?
        GROUP BY symbol, side
        ORDER BY trade_count DESC
    """
    results = db.execute_query(query, ['example_portfolio'])
    
    print("\nTrade Summary:")
    for result in results:
        print(f"  {result['symbol']} {result['side'].upper()}: "
              f"{result['trade_count']} trades, "
              f"{result['total_quantity']:.0f} shares, "
              f"avg ${result['avg_price']:.2f}")
    
    # Get agent metrics
    metrics = db.get_agent_metrics('execution_agent_001')
    print(f"\nAgent Metrics: {len(metrics)} recorded")
    for metric in metrics:
        print(f"  {metric['metric_name']}: {metric['metric_value']:.2f} ({metric['dimension']})")
    
    print("\n" + "=" * 60)
    print("✅ Integration Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    try:
        demo_integration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
