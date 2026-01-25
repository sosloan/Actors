#!/usr/bin/env python3
"""
Database initialization script for ACTORS
Sets up DuckDB with schema and sample data
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import get_database_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database(add_sample_data: bool = False):
    """
    Initialize the ACTORS database
    
    Args:
        add_sample_data: Whether to add sample data for testing
    """
    logger.info("🚀 Starting database initialization...")
    
    # Get database manager (this will create schema)
    db = get_database_manager()
    
    logger.info("✅ Database schema created successfully")
    
    if add_sample_data:
        logger.info("📊 Adding sample data...")
        add_sample_trading_data(db)
        logger.info("✅ Sample data added successfully")
    
    # Print database stats
    stats = db.get_database_stats()
    logger.info("📈 Database Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("🎉 Database initialization complete!")


def add_sample_trading_data(db):
    """Add sample trading data for demonstration"""
    
    # Sample symbols
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    # Add market data
    logger.info("Adding sample market data...")
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(100):
        for symbol in symbols:
            data = {
                'symbol': symbol,
                'timestamp': base_time + timedelta(hours=i),
                'open': 100 + random.uniform(-10, 10),
                'high': 105 + random.uniform(-5, 10),
                'low': 95 + random.uniform(-10, 5),
                'close': 100 + random.uniform(-10, 10),
                'volume': random.randint(1000000, 10000000),
                'source': 'demo_data'
            }
            db.insert_market_data(data)
    
    logger.info(f"Added {100 * len(symbols)} market data records")
    
    # Add portfolio positions
    logger.info("Adding sample portfolio positions...")
    portfolio_id = 'demo_portfolio_1'
    
    for symbol in symbols[:3]:  # Add positions for 3 symbols
        position = {
            'portfolio_id': portfolio_id,
            'symbol': symbol,
            'quantity': random.randint(10, 100),
            'entry_price': 100 + random.uniform(-20, 20),
            'current_price': 100 + random.uniform(-20, 20),
            'position_type': random.choice(['long', 'short']),
            'opened_at': datetime.now() - timedelta(days=random.randint(1, 30))
        }
        db.insert_portfolio_position(position)
    
    logger.info("Added 3 portfolio positions")
    
    # Add trade history
    logger.info("Adding sample trade history...")
    
    for i in range(20):
        trade = {
            'order_id': f'order_{i+1:04d}',
            'portfolio_id': portfolio_id,
            'symbol': random.choice(symbols),
            'side': random.choice(['buy', 'sell']),
            'quantity': random.randint(10, 100),
            'price': 100 + random.uniform(-20, 20),
            'order_type': random.choice(['market', 'limit', 'stop']),
            'status': random.choice(['executed', 'pending', 'cancelled']),
            'executed_at': datetime.now() - timedelta(days=random.randint(0, 30))
        }
        db.insert_trade(trade)
    
    logger.info("Added 20 trade records")
    
    # Add agent metrics
    logger.info("Adding sample agent metrics...")
    agent_types = ['market_data', 'technical_analysis', 'sentiment', 'portfolio', 'execution', 'risk']
    # 8D Narrative Space dimensions from ACTORS project:
    # Each dimension represents a different aspect of agent behavior and system performance
    # SPEED: High-frequency execution, LOYALTY: Long-term consistency, PASSION: Innovation/Risk-taking
    # SACRED: Risk management/preservation, COURAGE: Volatility handling, WISDOM: Analysis depth
    # LOVE: Social impact focus, TRUTH: Market microstructure accuracy
    dimensions = ['SPEED', 'LOYALTY', 'PASSION', 'SACRED', 'COURAGE', 'WISDOM', 'LOVE', 'TRUTH']
    
    for agent_type in agent_types:
        for i in range(10):
            metric = {
                'agent_id': f'{agent_type}_agent_{i+1:03d}',
                'agent_type': agent_type,
                'metric_name': random.choice(['accuracy', 'latency', 'throughput', 'success_rate']),
                'metric_value': random.uniform(0.5, 1.0),
                'dimension': random.choice(dimensions),
                'timestamp': datetime.now() - timedelta(hours=random.randint(0, 72))
            }
            db.insert_agent_metric(metric)
    
    logger.info(f"Added {10 * len(agent_types)} agent metrics")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ACTORS DuckDB database')
    parser.add_argument(
        '--sample-data',
        action='store_true',
        help='Add sample data for testing and demonstration'
    )
    
    args = parser.parse_args()
    
    try:
        initialize_database(add_sample_data=args.sample_data)
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
