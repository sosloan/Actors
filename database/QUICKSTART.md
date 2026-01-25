# Quick Start Guide - RTS Database

## 5-Minute Quick Start

### Installation
```bash
pip install numpy lz4 duckdb redis
```

### Basic Usage (L0 + L1)
```python
from database import HotStateBuffer, RollbackBuffer, DatabaseConfig
import numpy as np

# Initialize
config = DatabaseConfig.default()
hot_state = HotStateBuffer(config.l0)
rollback = RollbackBuffer(config.l1)

# Setup arrays
hot_state.register_array("x", np.dtype('float32'))
hot_state.register_array("y", np.dtype('float32'))
hot_state.register_array("health", np.dtype('float32'))

# Add entities
for i in range(1000):
    hot_state.add_entity(x=float(i), y=float(i), health=100.0)

# Game loop
for tick in range(60):
    # Update entities (SIMD)
    x = hot_state.get_array("x")
    y = hot_state.get_array("y")
    x[:] += 1.0  # Move all entities
    
    # Snapshot and store
    hot_state.tick()
    tick_id, snapshot = hot_state.snapshot()
    rollback.store_snapshot(tick_id, snapshot)

# Rollback if needed
snapshot_30 = rollback.get_snapshot(30)
hot_state.restore(snapshot_30)
```

### Analytics (L2)
```python
from database import AnalyticsStore
from database.config import L2Config

# Initialize
config = L2Config(duckdb_path="game.duckdb")
analytics = AnalyticsStore(config)

# Store match
analytics.create_match("match_001", {"map": "arena"})

# Store telemetry
entities = [
    {'entity_id': i, 'x': i*1.0, 'y': i*2.0, 'health': 100.0}
    for i in range(100)
]
analytics.store_entity_telemetry("match_001", tick=0, entities=entities)

# Query
stats = analytics.get_match_statistics("match_001")
print(f"Ticks: {stats['tick_count']}")

# Export
parquet_file = analytics.export_to_parquet("match_001")
```

### Multiplayer Sync (L3)
```python
from database import GlobalSynchronizer
from database.config import L3Config

# Initialize
config = L3Config(redis_host="localhost")
sync = GlobalSynchronizer(config)

# Submit command
cmd_id = sync.submit_command(
    player_id="player_1",
    command_type="move",
    payload={"x": 10, "y": 20}
)

# Get commands for tick
tick = sync.get_current_tick()
commands = sync.get_commands_for_tick(tick)

# Execute and advance
for cmd in commands:
    # Execute command
    pass

sync.advance_tick()
```

### F´ Component Pattern
```python
from database import DatabaseComponent

# Create component
db_comp = DatabaseComponent("GAME_DB")
db_comp.initialize()
db_comp.start()

# Monitor health
health = db_comp.get_health()  # Returns ComponentHealth.HEALTHY

# Get telemetry
telemetry = db_comp.get_telemetry()

# Stop
db_comp.stop()
```

## Common Patterns

### Pattern 1: Game Loop with Rollback
```python
hot_state = HotStateBuffer(config.l0)
rollback = RollbackBuffer(config.l1)

for tick in range(1000):
    # Update game state
    update_physics(hot_state)
    
    # Save state
    hot_state.tick()
    tick_id, snapshot = hot_state.snapshot()
    rollback.store_snapshot(tick_id, snapshot)
    
    # Can rollback last 120 ticks
```

### Pattern 2: Multiplayer Lockstep
```python
sync = GlobalSynchronizer(config.l3)

while game_running:
    tick = sync.get_current_tick()
    
    # Lock tick
    if sync.lock_tick(tick):
        # Get all player commands
        commands = sync.get_commands_for_tick(tick)
        
        # Execute deterministically
        for cmd in sorted(commands, key=lambda c: c.command_id):
            execute_command(cmd)
        
        # Advance
        sync.advance_tick()
        sync.unlock_tick(tick)
```

### Pattern 3: Post-Game Analytics
```python
analytics = AnalyticsStore(config.l2)

# After match ends
analytics.create_match("match_123")

# Store all telemetry
for tick_id, entities in match_data:
    analytics.store_entity_telemetry("match_123", tick_id, entities)

# Export for analysis
parquet_file = analytics.export_to_parquet("match_123")

# Query stats
stats = analytics.get_match_statistics("match_123")
```

## Performance Tips

1. **Use SIMD operations**: Get full arrays, not individual attributes
   ```python
   # ✓ Good (SIMD)
   x = buffer.get_array("x")
   x[:] += velocity * dt
   
   # ✗ Bad (slow)
   for i in range(n):
       x_i = buffer.get_attribute(i, "x")
       buffer.set_attribute(i, "x", x_i + velocity * dt)
   ```

2. **Batch operations**: Group telemetry writes
   ```python
   # ✓ Good (batch)
   analytics.store_entity_telemetry(match_id, tick, all_entities)
   
   # ✗ Bad (one-by-one)
   for entity in entities:
       analytics.store_entity_telemetry(match_id, tick, [entity])
   ```

3. **Enable compression**: Reduces memory by 5x
   ```python
   config = L1Config(compression_enabled=True, compression_level=1)
   ```

4. **Use memory-mapped files**: Crash recovery
   ```python
   config = L0Config(use_mmap=True, mmap_file_path="/game/state.mmap")
   ```

## Troubleshooting

### Redis Not Available
```python
# L3 gracefully degrades
sync = GlobalSynchronizer(config.l3)
if not sync.connected:
    print("Running in single-player mode")
```

### DuckDB Not Available
```python
# L2 gracefully degrades
analytics = AnalyticsStore(config.l2)
if not analytics.conn:
    print("Analytics disabled")
```

### Memory Issues
```python
# Reduce max entities
config = L0Config(max_entities=5000)

# Reduce buffer size
config = L1Config(tick_buffer_size=60)
```

## Examples

Run the provided examples:

```bash
# Detailed tier demonstrations
python database_demo.py

# Complete game loop
python database_example.py

# Run tests
pytest tests/test_database.py -v
```

## Documentation

- **README.md** - Full documentation
- **ARCHITECTURE.md** - Architecture diagrams
- **IMPLEMENTATION_SUMMARY.md** - Implementation details

## Support

For issues or questions:
- See documentation in `database/`
- Run examples: `database_demo.py`, `database_example.py`
- Check tests: `tests/test_database.py`
