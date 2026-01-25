#!/usr/bin/env python3
"""
Demo script for DuckDB database functionality
Demonstrates basic CRUD operations and queries
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import get_database_manager


def demo_market_data():
    """Demo market data operations"""
    print("\n📊 Market Data Demo")
    print("=" * 60)
    
    db = get_database_manager()
    
    # Get market data for AAPL
    print("\nFetching market data for AAPL...")
    data = db.get_market_data('AAPL', limit=5)
    
    if data:
        print(f"Found {len(data)} records:")
        for record in data:
            print(f"  {record['timestamp']}: Open=${record['open']:.2f}, Close=${record['close']:.2f}, Volume={record['volume']:,}")
    else:
        print("No data found")


def demo_portfolio_positions():
    """Demo portfolio position operations"""
    print("\n💼 Portfolio Positions Demo")
    print("=" * 60)
    
    db = get_database_manager()
    
    # Get portfolio positions
    print("\nFetching portfolio positions...")
    positions = db.get_portfolio_positions('demo_portfolio_1')
    
    if positions:
        print(f"Found {len(positions)} positions:")
        total_value = 0
        for pos in positions:
            position_value = pos['quantity'] * pos.get('current_price', pos['entry_price'])
            pnl = (pos.get('current_price', pos['entry_price']) - pos['entry_price']) * pos['quantity']
            total_value += position_value
            
            print(f"\n  {pos['symbol']}:")
            print(f"    Type: {pos['position_type']}")
            print(f"    Quantity: {pos['quantity']}")
            print(f"    Entry Price: ${pos['entry_price']:.2f}")
            print(f"    Current Price: ${pos.get('current_price', 0):.2f}")
            print(f"    Position Value: ${position_value:.2f}")
            print(f"    P&L: ${pnl:.2f} ({(pnl/position_value*100):.2f}%)")
        
        print(f"\n  Total Portfolio Value: ${total_value:.2f}")
    else:
        print("No positions found")


def demo_trade_history():
    """Demo trade history operations"""
    print("\n📈 Trade History Demo")
    print("=" * 60)
    
    db = get_database_manager()
    
    # Get trade history
    print("\nFetching trade history...")
    trades = db.get_trade_history('demo_portfolio_1', limit=10)
    
    if trades:
        print(f"Found {len(trades)} trades:")
        
        # Calculate statistics
        buy_trades = [t for t in trades if t['side'] == 'buy']
        sell_trades = [t for t in trades if t['side'] == 'sell']
        executed_trades = [t for t in trades if t['status'] == 'executed']
        
        print(f"\nStatistics:")
        print(f"  Total Trades: {len(trades)}")
        print(f"  Buy Orders: {len(buy_trades)}")
        print(f"  Sell Orders: {len(sell_trades)}")
        print(f"  Executed: {len(executed_trades)}")
        
        print(f"\nRecent trades:")
        for trade in trades[:5]:
            print(f"  {trade['order_id']}: {trade['side'].upper()} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f} - {trade['status']}")
    else:
        print("No trades found")


def demo_agent_metrics():
    """Demo agent metrics operations"""
    print("\n🤖 Agent Metrics Demo")
    print("=" * 60)
    
    db = get_database_manager()
    
    # Get all agent types
    print("\nFetching agent metrics...")
    query = """
        SELECT agent_type, COUNT(*) as count, AVG(metric_value) as avg_value
        FROM agent_metrics
        GROUP BY agent_type
        ORDER BY count DESC
    """
    stats = db.execute_query(query)
    
    if stats:
        print(f"Found {len(stats)} agent types:")
        for stat in stats:
            print(f"  {stat['agent_type']}: {stat['count']} metrics, avg value: {stat['avg_value']:.3f}")
        
        # Get metrics by dimension
        print("\nMetrics by dimension:")
        query = """
            SELECT dimension, COUNT(*) as count, AVG(metric_value) as avg_value
            FROM agent_metrics
            WHERE dimension IS NOT NULL
            GROUP BY dimension
            ORDER BY avg_value DESC
        """
        dimension_stats = db.execute_query(query)
        
        for stat in dimension_stats:
            print(f"  {stat['dimension']}: {stat['count']} metrics, avg value: {stat['avg_value']:.3f}")
    else:
        print("No agent metrics found")


def demo_custom_analytics():
    """Demo custom analytics queries"""
    print("\n📊 Custom Analytics Demo")
    print("=" * 60)
    
    db = get_database_manager()
    
    # Top traded symbols
    print("\nTop traded symbols:")
    query = """
        SELECT symbol, COUNT(*) as trade_count, SUM(quantity) as total_quantity
        FROM trade_history
        GROUP BY symbol
        ORDER BY trade_count DESC
        LIMIT 5
    """
    results = db.execute_query(query)
    
    if results:
        for result in results:
            print(f"  {result['symbol']}: {result['trade_count']} trades, {result['total_quantity']:.0f} shares")
    
    # Market data summary
    print("\nMarket data summary by symbol:")
    query = """
        SELECT 
            symbol,
            COUNT(*) as records,
            MIN(low) as min_price,
            MAX(high) as max_price,
            AVG(close) as avg_close,
            SUM(volume) as total_volume
        FROM market_data
        GROUP BY symbol
        ORDER BY total_volume DESC
        LIMIT 5
    """
    results = db.execute_query(query)
    
    if results:
        for result in results:
            print(f"\n  {result['symbol']}:")
            print(f"    Records: {result['records']}")
            print(f"    Price Range: ${result['min_price']:.2f} - ${result['max_price']:.2f}")
            print(f"    Avg Close: ${result['avg_close']:.2f}")
            print(f"    Total Volume: {result['total_volume']:,}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("🦞 ACTORS DuckDB Database Demo")
    print("=" * 60)
    
    try:
        demo_market_data()
        demo_portfolio_positions()
        demo_trade_history()
        demo_agent_metrics()
        demo_custom_analytics()
        
        # Database stats
        print("\n" + "=" * 60)
        print("📈 Database Statistics")
        print("=" * 60)
        
        db = get_database_manager()
        stats = db.get_database_stats()
        
        print(f"\nDatabase Path: {stats['database_path']}")
        print(f"Connection Active: {stats['connection_active']}")
        print(f"\nTable Record Counts:")
        print(f"  Market Data: {stats['market_data_count']}")
        print(f"  Portfolio Positions: {stats['portfolio_positions_count']}")
        print(f"  Trade History: {stats['trade_history_count']}")
        print(f"  Agent Metrics: {stats['agent_metrics_count']}")
        print(f"  Risk Metrics: {stats['risk_metrics_count']}")
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
