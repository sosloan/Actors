# 🛠️ ACTORS v2 – Enhanced Configuration Layer & Cultural Intelligence

## Overview

ACTORS v2 introduces a powerful configuration layer combined with Harper Henry behavioral guardrails, enabling **dynamic portfolio management** that integrates both financial and cultural objectives.

## Key Features

### 1. 🔧 Configuration Layer

The configuration layer allows **dynamic tuning of system behavior** through a centralized YAML configuration file:

- **Agent Configuration**: Configure portfolio, execution, DeFi, and risk agents
- **Metrics Settings**: Enable/disable rich metrics tracking and export formats
- **Guardrails Settings**: Set ethical, cultural, and social risk constraints
- **Festival Calendar**: Define regional festivals and tilt factors
- **Export Settings**: Configure output formats and destinations

### 2. 🛡️ Harper Henry Behavioral Guardrails

Enforce **ethical, cultural, and behavioral limits** in portfolio and trading agents:

| Guardrail           | Function                                                    |
| ------------------- | ----------------------------------------------------------- |
| Ethical Investment  | Avoids high-risk, socially harmful investments              |
| Cultural Alignment  | Ensures minimum exposure to local/regional cultural assets  |
| Max Social Risk     | Limits speculative trades impacting communities             |
| Festival Tilt       | Dynamically favors sectors linked to local festivals/events |
| Min Cultural Weight | Guarantees baseline investment in culturally aligned assets |

### 3. 📊 Richer Metrics & Export

Expanded metrics track **cultural, ethical, and festival-aware performance**:

| Metric Category    | Metrics Tracked                                   |
| ------------------ | ------------------------------------------------- |
| Cultural           | Exposure, asset count, diversity score            |
| Festival           | Tilt impact, aligned assets, period status        |
| Ethical            | Compliance percentage, ethical asset ratio        |
| Social Risk        | Risk score, high-risk asset count, impact score   |
| Financial          | VaR, Sharpe, volatility, drawdowns, returns       |

**Export Formats**: CSV, JSON, Parquet

### 4. 🎉 Festival-Aware Portfolio Tilt

- Uses **regional festival calendar** (e.g., Guadalajara cultural events)
- Dynamically biases portfolio allocations toward **local cultural industries, tech, and artisanal sectors**
- Adjustable via **tilt_factor** in configuration

## Quick Start

### 1. Configuration

Create or modify `config.yaml` in the project root:

```yaml
agents:
  portfolio_agent:
    max_risk: 0.15
    min_cultural_weight: 0.1
    festival_tilt: true

metrics:
  enable_rich_metrics: true
  export_formats: ["csv", "json", "parquet"]
  track_cultural_exposure: true
  track_festival_impact: true

harper_henry_guardrails:
  ethical_investment: true
  max_social_risk: 0.2
  cultural_alignment_min: 0.2
  min_cultural_weight: 0.1

festival_calendar:
  enabled: true
  region: "Guadalajara"
  tilt_factor: 1.2
  festivals:
    - name: "Fiestas de Octubre"
      start_date: "2024-10-01"
      end_date: "2024-10-31"
      related_sectors: ["cultural_events", "artisan_crafts"]
      tilt_factor: 1.3
```

### 2. Basic Usage

```python
from core.config_loader import get_config
from core.harper_henry_guardrails import HarperHenryGuardrails, Asset, Portfolio
from core.festival_calendar import FestivalCalendar
from core.metrics_tracker import MetricsTracker
from core.metrics_exporter import MetricsExporter

# Load configuration
config = get_config("config.yaml")

# Initialize components
guardrails_config = config.get_guardrails_config()
guardrails = HarperHenryGuardrails(guardrails_config)

calendar_config = config.get_festival_calendar_config()
calendar = FestivalCalendar(calendar_config)

metrics_config = config.get_metrics_config()
tracker = MetricsTracker(
    track_cultural_exposure=metrics_config.track_cultural_exposure,
    track_festival_impact=metrics_config.track_festival_impact
)

# Create portfolio
portfolio = Portfolio(
    id="my-portfolio",
    name="Cultural Harmony Portfolio",
    assets=[
        Asset(
            id="asset-1",
            name="Cultural Exchange Fund",
            weight=0.3,
            is_cultural=True,
            is_festival_aligned=True,
            is_ethical=True,
            social_risk=0.05
        ),
        # ... more assets
    ]
)

# Enforce guardrails
portfolio = guardrails.enforce(portfolio, festival_tilt_factor=1.2)

# Calculate metrics
festival_context = calendar.get_festival_impact_report()
metrics = tracker.calculate_metrics(portfolio, festival_context=festival_context)

# Export metrics
exporter = MetricsExporter(output_directory="exports")
exporter.export_portfolio_metrics(metrics, formats=["csv", "json"])
```

### 3. Run the Demo

```bash
python examples/actors_v2_demo.py
```

This demonstrates:
- ✅ Configuration loading
- ✅ Harper Henry guardrail enforcement
- ✅ Festival-aware portfolio management
- ✅ Enhanced metrics tracking
- ✅ Multi-format export

## Architecture

### Component Interaction

```
┌─────────────────┐
│  config.yaml    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ConfigLoader    │
└────────┬────────┘
         │
         ├──────────────────────────────┬────────────────────┐
         ▼                              ▼                    ▼
┌──────────────────┐        ┌────────────────────┐  ┌──────────────┐
│Harper Henry      │        │Festival Calendar   │  │Metrics       │
│Guardrails        │        │                    │  │Tracker       │
└─────────┬────────┘        └─────────┬──────────┘  └──────┬───────┘
          │                           │                    │
          └───────────┬───────────────┘                    │
                      ▼                                    ▼
              ┌────────────────┐                  ┌────────────────┐
              │  Portfolio     │                  │  Metrics       │
              │  (Adjusted)    │                  │  Exporter      │
              └────────────────┘                  └────────────────┘
```

## API Reference

### ConfigLoader

```python
from core.config_loader import get_config

config = get_config("config.yaml")

# Get specific configurations
agent_config = config.get_agent_config("portfolio_agent")
metrics_config = config.get_metrics_config()
guardrails_config = config.get_guardrails_config()
calendar_config = config.get_festival_calendar_config()
```

### HarperHenryGuardrails

```python
from core.harper_henry_guardrails import HarperHenryGuardrails

guardrails = HarperHenryGuardrails(guardrails_config)

# Enforce guardrails on portfolio
portfolio = guardrails.enforce(portfolio, festival_tilt_factor=1.2)

# Check compliance without enforcement
compliance = guardrails.check_compliance(portfolio)

# Get violations
violations = guardrails.get_violations()
```

### FestivalCalendar

```python
from core.festival_calendar import FestivalCalendar

calendar = FestivalCalendar(calendar_config)

# Get active festivals
active_festivals = calendar.get_active_festivals()

# Get sector tilt factor
tilt_factor = calendar.get_sector_tilt_factor("cultural_events")

# Apply festival tilt to portfolio
portfolio = calendar.apply_festival_tilt(portfolio)

# Get impact report
report = calendar.get_festival_impact_report()
```

### MetricsTracker

```python
from core.metrics_tracker import MetricsTracker

tracker = MetricsTracker(
    track_cultural_exposure=True,
    track_festival_impact=True,
    track_ethical_compliance=True,
    track_social_risk=True
)

# Calculate metrics
metrics = tracker.calculate_metrics(
    portfolio,
    returns=[0.02, -0.01, 0.03],
    festival_context=festival_context
)

# Get latest metrics
latest = tracker.get_latest_metrics()

# Get metrics history
history = tracker.get_metrics_history(limit=10)
```

### MetricsExporter

```python
from core.metrics_exporter import MetricsExporter

exporter = MetricsExporter(
    output_directory="exports",
    compression=False,
    include_metadata=True
)

# Export to single format
path = exporter.export_metrics(metrics_dict, format="csv")

# Export to multiple formats
results = exporter.export_multiple_formats(
    metrics_dict,
    formats=["csv", "json", "parquet"]
)

# Export PortfolioMetrics objects
results = exporter.export_portfolio_metrics(metrics, formats=["csv", "json"])
```

## Testing

Run the comprehensive test suite:

```bash
# Run all ACTORS v2 tests
pytest tests/test_config_guardrails.py -v

# Run specific test class
pytest tests/test_config_guardrails.py::TestHarperHenryGuardrails -v

# Run with coverage
pytest tests/test_config_guardrails.py --cov=core --cov-report=html
```

All 22 tests validate:
- ✅ Configuration loading and validation
- ✅ Harper Henry guardrail enforcement
- ✅ Festival calendar functionality
- ✅ Metrics tracking and calculation
- ✅ Multi-format export
- ✅ Integration between components

## Configuration Reference

### Agent Configuration

```yaml
agents:
  portfolio_agent:
    max_risk: 0.15              # Maximum portfolio risk (0-1)
    min_cultural_weight: 0.1    # Minimum cultural asset weight (0-1)
    festival_tilt: true         # Enable festival tilt
    enabled: true               # Enable agent
```

### Metrics Configuration

```yaml
metrics:
  enable_rich_metrics: true           # Enable enhanced metrics
  export_formats: ["csv", "json"]     # Export formats
  export_frequency: "daily"           # Export frequency
  track_cultural_exposure: true       # Track cultural metrics
  track_festival_impact: true         # Track festival impact
  track_ethical_compliance: true      # Track ethical metrics
  track_social_risk: true             # Track social risk
```

### Guardrails Configuration

```yaml
harper_henry_guardrails:
  ethical_investment: true            # Enforce ethical constraints
  max_social_risk: 0.2                # Maximum social risk (0-1)
  cultural_alignment_min: 0.2         # Minimum cultural alignment (0-1)
  festival_tilt_enabled: true         # Enable festival tilt
  min_cultural_weight: 0.1            # Minimum cultural weight (0-1)
  enforce_on_portfolio: true          # Enable enforcement
```

### Festival Calendar Configuration

```yaml
festival_calendar:
  enabled: true
  region: "Guadalajara"
  tilt_factor: 1.2                    # Default tilt factor
  festivals:
    - name: "Festival Name"
      start_date: "2024-10-01"        # YYYY-MM-DD format
      end_date: "2024-10-31"
      related_sectors:
        - cultural_events
        - artisan_crafts
      tilt_factor: 1.3                # Festival-specific tilt
```

## Best Practices

### 1. Configuration Management

- **Version Control**: Store `config.yaml` in version control
- **Environment-Specific**: Use different configs for dev/prod
- **Validation**: Always validate config after changes
- **Backup**: Keep backups of working configurations

### 2. Guardrail Tuning

- **Start Conservative**: Begin with stricter constraints
- **Monitor Violations**: Track and analyze guardrail violations
- **Gradual Relaxation**: Relax constraints gradually based on data
- **Regular Review**: Review and adjust guardrails monthly

### 3. Festival Calendar

- **Keep Updated**: Regularly update festival dates
- **Regional Accuracy**: Ensure festivals match target region
- **Sector Mapping**: Accurately map festivals to sectors
- **Test Impact**: Monitor actual portfolio impact

### 4. Metrics Export

- **Regular Exports**: Export metrics at consistent intervals
- **Multiple Formats**: Use appropriate format for each use case
- **Cleanup**: Periodically remove old export files
- **Validation**: Verify exported data integrity

## Troubleshooting

### Configuration Not Loading

```python
# Check if config file exists
from pathlib import Path
config_path = Path("config.yaml")
print(f"Config exists: {config_path.exists()}")

# Validate YAML syntax
import yaml
with open(config_path) as f:
    config_data = yaml.safe_load(f)
    print("YAML is valid")
```

### Guardrails Not Enforcing

```python
# Check if enforcement is enabled
guardrails_config = config.get_guardrails_config()
print(f"Enforcement enabled: {guardrails_config.enforce_on_portfolio}")

# Check for violations
violations = guardrails.get_violations()
for v in violations:
    print(f"{v.rule}: {v.message}")
```

### Metrics Export Failing

```python
# Check pandas availability
try:
    import pandas as pd
    print("pandas available")
except ImportError:
    print("Install pandas: pip install pandas")

# Check pyarrow for Parquet
try:
    import pyarrow
    print("pyarrow available")
except ImportError:
    print("Install pyarrow: pip install pyarrow")
```

## Future Enhancements

- [ ] Real-time guardrail monitoring dashboard
- [ ] Machine learning-based guardrail optimization
- [ ] Multi-region festival calendar support
- [ ] Advanced festival impact prediction
- [ ] Automated compliance reporting
- [ ] Integration with external data sources
- [ ] GraphQL API for configuration management

## Support

- **Documentation**: See main [README.md](../README.md)
- **Issues**: [GitHub Issues](https://github.com/sosloan/Actors/issues)
- **Examples**: See `examples/actors_v2_demo.py`
- **Tests**: See `tests/test_config_guardrails.py`

---

*"Where financial optimization meets cultural harmony and ethical responsibility."* 🎭⚖️🎉
