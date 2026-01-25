# DuckDB Database Setup for ACTORS

This directory contains the DuckDB database setup and management for the ACTORS financial trading system.

## Overview

ACTORS uses DuckDB, a high-performance analytical database, to store and query financial trading data including:

- **Market Data**: Stock prices, volumes, and historical market information
- **Portfolio Positions**: Current holdings and position details
- **Trade History**: Complete record of all executed trades
- **Agent Metrics**: Performance metrics from the distributed agent network
- **Risk Metrics**: Risk analysis and monitoring data

## Features

- ✅ Fast analytical queries with DuckDB
- ✅ Auto-incrementing primary keys using sequences
- ✅ Indexed tables for optimal query performance
- ✅ JSON support for flexible metadata storage
- ✅ Comprehensive test coverage
- ✅ Sample data generation for testing and demos

## Database Schema

### Tables

1. **market_data** - Historical market data
   - `id`: Primary key (auto-increment)
   - `symbol`: Stock/asset symbol
   - `timestamp`: Data timestamp
   - `open`, `high`, `low`, `close`: OHLC prices
   - `volume`: Trading volume
   - `source`: Data source identifier
   - `created_at`: Record creation timestamp

2. **portfolio_positions** - Current portfolio holdings
   - `id`: Primary key (auto-increment)
   - `portfolio_id`: Portfolio identifier
   - `symbol`: Asset symbol
   - `quantity`: Position size
   - `entry_price`: Entry price
   - `current_price`: Current market price
   - `position_type`: 'long' or 'short'
   - `opened_at`: Position open timestamp
   - `updated_at`: Last update timestamp
   - `metadata`: JSON field for additional data

3. **trade_history** - Complete trade records
   - `id`: Primary key (auto-increment)
   - `order_id`: Unique order identifier
   - `portfolio_id`: Portfolio identifier
   - `symbol`: Traded asset
   - `side`: 'buy' or 'sell'
   - `quantity`: Trade size
   - `price`: Execution price
   - `order_type`: 'market', 'limit', or 'stop'
   - `status`: Order status
   - `executed_at`: Execution timestamp
   - `created_at`: Record creation timestamp
   - `metadata`: JSON field for additional data

4. **agent_metrics** - Agent performance tracking
   - `id`: Primary key (auto-increment)
   - `agent_id`: Agent identifier
   - `agent_type`: Type of agent
   - `metric_name`: Metric identifier
   - `metric_value`: Metric value
   - `dimension`: 8D narrative dimension
   - `timestamp`: Metric timestamp
   - `created_at`: Record creation timestamp
   - `metadata`: JSON field for additional data

5. **risk_metrics** - Risk analysis data
   - `id`: Primary key (auto-increment)
   - `portfolio_id`: Portfolio identifier
   - `metric_type`: Type of risk metric
   - `metric_value`: Metric value
   - `confidence_level`: Confidence level
   - `timestamp`: Metric timestamp
   - `created_at`: Record creation timestamp
   - `metadata`: JSON field for additional data

### Indexes

Performance indexes are created on frequently queried columns:
- Market data: `symbol`, `timestamp`
- Portfolio positions: `portfolio_id`
- Trade history: `portfolio_id`, `symbol`
- Agent metrics: `agent_id`, `timestamp`
- Risk metrics: `portfolio_id`

## Installation

1. **Install DuckDB** (already included in requirements.txt):
   ```bash
   pip install duckdb==1.1.3
   ```

2. **Initialize the database**:
   ```bash
   python scripts/init_database.py
   ```

3. **Initialize with sample data**:
   ```bash
   python scripts/init_database.py --sample-data
   ```

## Usage

### Basic Usage

```python
from core.database_manager import get_database_manager

# Get database manager singleton
db = get_database_manager()

# Insert market data
data = {
    'symbol': 'AAPL',
    'timestamp': datetime.now(),
    'open': 150.0,
    'high': 155.0,
    'low': 148.0,
    'close': 152.0,
    'volume': 1000000,
    'source': 'live_feed'
}
record_id = db.insert_market_data(data)

# Query market data
results = db.get_market_data('AAPL', limit=100)

# Insert a trade
trade = {
    'order_id': 'order_001',
    'portfolio_id': 'portfolio_1',
    'symbol': 'GOOGL',
    'side': 'buy',
    'quantity': 100,
    'price': 150.0,
    'order_type': 'market',
    'status': 'executed',
    'executed_at': datetime.now()
}
trade_id = db.insert_trade(trade)

# Get trade history
trades = db.get_trade_history('portfolio_1', limit=50)

# Custom SQL queries
query = "SELECT symbol, COUNT(*) as count FROM market_data GROUP BY symbol"
results = db.execute_query(query)
```

### Advanced Usage

```python
from core.database_manager import DatabaseManager
from datetime import datetime, timedelta

# Create a new database manager with custom path
db = DatabaseManager('/path/to/custom.duckdb')
db.initialize_schema()

# Insert agent metrics
metric = {
    'agent_id': 'market_data_001',
    'agent_type': 'market_data',
    'metric_name': 'accuracy',
    'metric_value': 0.95,
    'dimension': 'SPEED',
    'timestamp': datetime.now()
}
db.insert_agent_metric(metric)

# Get agent metrics
metrics = db.get_agent_metrics('market_data_001', metric_name='accuracy')

# Complex queries with parameters
query = """
    SELECT symbol, AVG(close) as avg_close, SUM(volume) as total_volume
    FROM market_data
    WHERE timestamp > ?
    GROUP BY symbol
    ORDER BY total_volume DESC
"""
cutoff_date = datetime.now() - timedelta(days=7)
results = db.execute_query(query, [cutoff_date])

# Get database statistics
stats = db.get_database_stats()
print(f"Market data records: {stats['market_data_count']}")
print(f"Trade history records: {stats['trade_history_count']}")
```

## Scripts

### Initialize Database
```bash
python scripts/init_database.py [--sample-data]
```
Creates the database schema and optionally adds sample data for testing.

### Demo Database
```bash
python scripts/demo_database.py
```
Runs a comprehensive demo showing database functionality with sample data.

## Testing

Run the database tests:
```bash
pytest tests/test_database.py -v
```

Test coverage includes:
- Database creation and schema initialization
- CRUD operations for all tables
- Query performance
- Data validation
- Index usage
- Custom queries

## File Locations

- **Database File**: `/home/runner/work/Actors/Actors/data/actors.duckdb`
- **Configuration**: `core/database_config.py`
- **Manager**: `core/database_manager.py`
- **Initialization**: `scripts/init_database.py`
- **Demo**: `scripts/demo_database.py`
- **Tests**: `tests/test_database.py`

## Notes

- Database files (*.duckdb, *.duckdb.wal) are excluded from git via `.gitignore`
- The database uses auto-incrementing sequences for primary keys
- All timestamps use the standard Python datetime format
- JSON fields support flexible metadata storage for extensibility
- The singleton pattern ensures a single database connection across the application

## Performance

DuckDB is optimized for analytical workloads and provides:
- Fast aggregations and analytical queries
- Efficient columnar storage
- Parallel query execution
- Low memory footprint
- ACID compliance

## Integration with ACTORS

The database integrates seamlessly with the ACTORS financial trading system:

1. **Market Data Agents** → Insert real-time market data
2. **Execution Agents** → Record trades and update positions
3. **Portfolio Agents** → Query positions and performance
4. **Risk Agents** → Store and analyze risk metrics
5. **ML Pipelines** → Extract features for machine learning models
6. **Analytics Dashboard** → Query data for visualization

## Future Enhancements

Potential future improvements:
- [ ] Add time-series partitioning for market data
- [ ] Implement data retention policies
- [ ] Add materialized views for common queries
- [ ] Support for DuckDB extensions (e.g., parquet, spatial)
- [ ] Real-time streaming ingestion
- [ ] Backup and recovery procedures
- [ ] Query optimization profiling
- [ ] Database migration system

## Support

For issues or questions:
- Check the test files for usage examples
- Run the demo script to see features in action
- Review the database manager source code for API details
- Consult DuckDB documentation: https://duckdb.org/docs/

## License

Part of the ACTORS project - See main LICENSE file for details.
