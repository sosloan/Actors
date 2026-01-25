#!/usr/bin/env python3
"""
🎭 HARPER HENRY HARMONY
Globally Optimized, AI-Driven Investment Frontier

Tagline: "Where precision finance meets cultural intelligence."

Core Concept
------------
HARPER HENRY HARMONY leverages cutting-edge AI and portfolio optimization to create
a globally aware investment platform. It combines:

1. Local Insight + Global Reach
   • Focused on Mexico and Guadalajara's emerging markets, tech hubs, and cultural enterprises.
   • Seamlessly integrates regional economic indicators with global market trends.

2. AI-Driven Portfolio Optimization
   • Dynamically infers asset allocation strategies using real-time data.
   • Incorporates risk-adjusted models, scenario simulation, and async AI builders
     to maximize efficiency.

3. Cultural Exchange Harmony
   • Evaluates investments not just for returns, but social, cultural, and economic impact.
   • Prioritizes ventures that boost local innovation, heritage, and sustainable growth.

Guadalajara & Mexico Focus
--------------------------
• Tech & Innovation Hub: Harness AI to identify high-growth startups, fintech, and
  hardware clusters in Guadalajara.
• Cultural Metrics Integration: Measure impact of investments on local communities,
  festivals, and creative industries.
• Dynamic Local–Global Optimization: Adjust allocations in real-time based on
  Mexican macro indicators, startup performance, and global market shifts.

Vision Statement
----------------
HARPER HENRY HARMONY transforms Guadalajara and Mexican markets into a globally
optimized, AI-driven investment frontier—where mathematical precision, cultural
intelligence, and financial opportunity converge.
"""

import asyncio
import csv
import json
import time
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import math
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# MEXICO / GUADALAJARA EDITION – ENUMS & DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class MexicanAssetClass(Enum):
    """Mexican market asset classes for value creation."""
    EQUITIES = "equities"
    BONDS = "bonds"
    REAL_ESTATE = "real_estate"
    FINTECH = "fintech"
    STARTUP_EQUITY = "startup_equity"
    ARTISANAL = "artisanal"
    CULTURAL_ENTERPRISE = "cultural_enterprise"


class GuadalajaraCluster(Enum):
    """Guadalajara tech and innovation clusters."""
    IT_SOFTWARE = "it_software"
    AI_ML = "ai_ml"
    HARDWARE_ELECTRONICS = "hardware_electronics"
    FINTECH = "fintech"
    CREATIVE_TECH = "creative_tech"
    HEALTH_TECH = "health_tech"


class HarmonyEngineMexico(Enum):
    """Mexico edition harmony engine types."""
    VALUE_CREATION_MEXICO = "value_creation_mexico"
    CONCRETE_TYPE_ASYNC_GDL = "concrete_type_async_gdl"
    PORTFOLIO_OPTIMIZATION_CULTURAL = "portfolio_optimization_cultural"
    GUADALAJARA_TECH_HUB = "guadalajara_tech_hub"
    CULTURAL_EXCHANGE_METRICS = "cultural_exchange_metrics"
    MARKET_SIMULATION_ENGINE = "market_simulation_engine"
    HARPER_HENRY_HARMONY_MEXICO = "harper_henry_harmony_mexico"


@dataclass
class JaliscoIndicator:
    """Regional economic indicator for Jalisco/Guadalajara."""
    id: str
    name: str
    value: float
    unit: str
    trend: float  # yoy or mom growth rate
    category: str  # gdp, industrial_cluster, startup_growth, employment, etc.
    source: str
    updated_at: datetime


@dataclass
class MexicanAsset:
    """Single Mexican market asset for portfolio allocation."""
    id: str
    asset_class: MexicanAssetClass
    name: str
    symbol: Optional[str]
    region: str  # national, jalisco, guadalajara
    expected_return: float
    volatility: float
    cultural_harmony_score: float
    sustainability_score: float
    liquidity_score: float
    weight: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GuadalajaraStartup:
    """High-potential startup in Guadalajara tech hub."""
    id: str
    name: str
    cluster: GuadalajaraCluster
    stage: str  # seed, series_a, series_b, growth
    valuation_estimate: float
    growth_rate: float
    exit_potential: float
    regional_impact_score: float
    cultural_impact_score: float
    employment_contribution: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CulturalHarmonyMetric:
    """Cultural exchange and harmony metric for portfolio alignment."""
    id: str
    name: str
    category: str  # social_sentiment, community_engagement, cultural_impact, festival_cycle, commerce_cycle
    value: float
    weight_in_optimization: float
    description: str
    region: str
    updated_at: datetime


@dataclass
class LocalDataFeed:
    """Local data feed for async builders (sentiment, media, financial)."""
    id: str
    feed_type: str  # social, financial, local_media, startup_news
    source_name: str
    sentiment_score: float  # -1 to 1
    relevance_to_gdl: float
    raw_signal: float
    processed_at: datetime


@dataclass
class MexicoPortfolioAllocation:
    """Inferred optimal allocation for Mexico/Guadalajara portfolio."""
    asset_id: str
    asset_class: MexicanAssetClass
    weight: float
    rationale: str
    risk_adjusted_return: float
    cultural_harmony_contribution: float
    inferred_at: datetime


@dataclass
class MarketSimulationScenario:
    """Single scenario from the market simulation engine."""
    scenario_id: str
    name: str
    mexican_macro_trend: float
    guadalajara_indicator_trend: float
    ai_inferred_behavior: float
    sentiment_factor: float
    portfolio_return_estimate: float
    risk_level: str  # low, medium, high
    created_at: datetime


@dataclass
class MexicoOptimizationConfig:
    """Configuration for Mexico/Guadalajara optimization run."""
    currency_volatility: float = 0.08
    regulation_risk: float = 0.1
    min_cultural_weight: float = 0.10  # Minimum combined weight for artisanal + cultural_enterprise
    festival_tilt_month: Optional[int] = None  # 1-12: boost artisanal/cultural (e.g. 11 = Día de Muertos)
    n_simulation_scenarios: int = 5
    include_simulation: bool = True
    apply_behavioral_guardrails: bool = True  # Harper Henry: emotion/cool-down checks


@dataclass
class BehavioralGuardrailResult:
    """Output of Harper Henry behavioral layer (Psychology of Speculation)."""
    behavioral_risk_score: float  # 0 = calm, 1 = high panic/greed signal
    cool_down_suggested: bool
    rationale: str
    suggested_max_volatility: Optional[float] = None
    resonance_check_passed: bool = True


# ═══════════════════════════════════════════════════════════════════════════════
# ACTORS v2 – CONFIGURATION LAYER (YAML-like schema)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PortfolioAgentConfig:
    max_risk: float = 0.15
    min_cultural_weight: float = 0.10
    festival_tilt: bool = True


@dataclass
class ExecutionAgentConfig:
    slippage_limit: float = 0.01
    hedge_enabled: bool = True


@dataclass
class AgentsConfig:
    portfolio_agent: PortfolioAgentConfig = field(default_factory=PortfolioAgentConfig)
    execution_agent: ExecutionAgentConfig = field(default_factory=ExecutionAgentConfig)


@dataclass
class MetricsConfig:
    enable_rich_metrics: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json", "parquet"])


@dataclass
class HarperHenryGuardrailsConfig:
    ethical_investment: bool = True
    max_social_risk: float = 0.2
    cultural_alignment_min: float = 0.20
    festival_tilt_factor: float = 1.2


@dataclass
class FestivalCalendarConfig:
    enabled: bool = True
    region: str = "Guadalajara"
    tilt_factor: float = 1.2


@dataclass
class LoggingConfig:
    level: str = "INFO"
    export_logs: bool = True


@dataclass
class ACTORSConfig:
    """ACTORS v2 full configuration (maps to example config.yaml)."""
    agents: AgentsConfig = field(default_factory=AgentsConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    harper_henry_guardrails: HarperHenryGuardrailsConfig = field(default_factory=HarperHenryGuardrailsConfig)
    festival_calendar: FestivalCalendarConfig = field(default_factory=FestivalCalendarConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ACTORSConfig":
        """Load config from a dict (e.g. from YAML)."""
        agents = AgentsConfig(
            portfolio_agent=PortfolioAgentConfig(
                max_risk=float(d.get("agents", {}).get("portfolio_agent", {}).get("max_risk", 0.15)),
                min_cultural_weight=float(d.get("agents", {}).get("portfolio_agent", {}).get("min_cultural_weight", 0.1)),
                festival_tilt=bool(d.get("agents", {}).get("portfolio_agent", {}).get("festival_tilt", True)),
            ),
            execution_agent=ExecutionAgentConfig(
                slippage_limit=float(d.get("agents", {}).get("execution_agent", {}).get("slippage_limit", 0.01)),
                hedge_enabled=bool(d.get("agents", {}).get("execution_agent", {}).get("hedge_enabled", True)),
            ),
        )
        metrics = MetricsConfig(
            enable_rich_metrics=bool(d.get("metrics", {}).get("enable_rich_metrics", True)),
            export_formats=list(d.get("metrics", {}).get("export_formats", ["csv", "json", "parquet"])),
        )
        hh = d.get("harper_henry_guardrails", {})
        guardrails = HarperHenryGuardrailsConfig(
            ethical_investment=bool(hh.get("ethical_investment", True)),
            max_social_risk=float(hh.get("max_social_risk", 0.2)),
            cultural_alignment_min=float(hh.get("cultural_alignment_min", 0.2)),
            festival_tilt_factor=float(hh.get("festival_tilt", 1.0) if isinstance(hh.get("festival_tilt"), (int, float)) else 1.2),
        )
        fc = d.get("festival_calendar", {})
        festival = FestivalCalendarConfig(
            enabled=bool(fc.get("enabled", True)),
            region=str(fc.get("region", "Guadalajara")),
            tilt_factor=float(fc.get("tilt_factor", 1.2)),
        )
        log = d.get("logging", {})
        logging_cfg = LoggingConfig(
            level=str(log.get("level", "INFO")),
            export_logs=bool(log.get("export_logs", True)),
        )
        return cls(
            agents=agents,
            metrics=metrics,
            harper_henry_guardrails=guardrails,
            festival_calendar=festival,
            logging=logging_cfg,
        )

    @classmethod
    def default_config(cls) -> "ACTORSConfig":
        """Return default config (equivalent to example config.yaml)."""
        return cls.from_dict({})


def load_config_from_yaml(path: Union[str, Path]) -> ACTORSConfig:
    """Load ACTORSConfig from a YAML file. Requires PyYAML."""
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML required for load_config_from_yaml. pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return ACTORSConfig.from_dict(data)


# ═══════════════════════════════════════════════════════════════════════════════
# FESTIVAL CALENDAR (Guadalajara)
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_festival_date(s: str) -> date:
    """Parse YYYY-MM-DD or MM-DD (year from today)."""
    parts = s.split("-")
    if len(parts) == 2:
        mo, day = int(parts[0]), int(parts[1])
        return date(date.today().year, mo, day)
    return date.fromisoformat(s)


GUADALAJARA_FESTIVAL_CALENDAR: List[Dict[str, Any]] = [
    {"name": "Día de Muertos", "start": "10-28", "end": "11-02", "related_sectors": ["artisanal", "cultural_enterprise", "creative_tech"], "tilt_factor": 1.25},
    {"name": "Feria Internacional del Libro Guadalajara", "start": "11-23", "end": "12-01", "related_sectors": ["cultural_enterprise", "creative_tech"], "tilt_factor": 1.2},
    {"name": "Feria de Octubre GDL", "start": "10-01", "end": "10-15", "related_sectors": ["artisanal", "cultural_enterprise"], "tilt_factor": 1.2},
    {"name": "Día de la Candelaria / Carnaval", "start": "02-01", "end": "02-15", "related_sectors": ["artisanal", "cultural_enterprise"], "tilt_factor": 1.15},
    {"name": "Semana Santa", "start": "03-24", "end": "04-01", "related_sectors": ["artisanal", "cultural_enterprise", "real_estate"], "tilt_factor": 1.1},
]


def get_active_festivals(calendar: List[Dict[str, Any]], on_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """Return festivals active on the given date (default today)."""
    on_date = on_date or date.today()
    active = []
    for f in calendar:
        start_s, end_s = f["start"], f["end"]
        start_d = _parse_festival_date(start_s)
        end_d = _parse_festival_date(end_s)
        if end_d < start_d:
            end_d = end_d.replace(year=end_d.year + 1)
        if start_d <= on_date <= end_d:
            active.append(f)
    return active


def apply_festival_tilt(
    allocations: List[Any],
    assets_by_id: Dict[str, Any],
    festival_calendar: List[Dict[str, Any]],
    on_date: Optional[date] = None,
    tilt_factor_override: Optional[float] = None,
) -> List[Any]:
    """
    Apply festival tilt to allocation weights. Sectors in related_sectors get weight *= tilt_factor.
    Returns new list of allocations with updated weights (renormalized).
    """
    if not allocations:
        return allocations
    active = get_active_festivals(festival_calendar, on_date)
    if not active:
        return allocations
    related = set()
    for f in active:
        related.update(f.get("related_sectors", []))
    factor = tilt_factor_override or max((f.get("tilt_factor", 1.0) for f in active), default=1.0)

    def is_festival_aligned(alloc: Any, aid: str) -> bool:
        asset = assets_by_id.get(aid)
        if asset is None:
            return False
        sector = getattr(asset, "asset_class", None)
        if sector is not None:
            sector_str = sector.value if hasattr(sector, "value") else str(sector)
            if sector_str in related:
                return True
        meta = getattr(asset, "metadata", None) or {}
        if meta.get("festival_commerce_aligned") or meta.get("tequila_ceramic_textile"):
            return True
        return False

    new_weights = [(a, getattr(a, "weight", 0.0) * (factor if is_festival_aligned(a, getattr(a, "asset_id", "")) else 1.0)) for a in allocations]
    total = sum(w for _, w in new_weights)
    if total <= 0:
        return allocations
    out = []
    for a, w in new_weights:
        w_norm = w / total
        if hasattr(a, "__dataclass_fields__"):
            d = {f: getattr(a, f) for f in a.__dataclass_fields__}
            d["weight"] = w_norm
            if "cultural_harmony_contribution" in d and hasattr(a, "cultural_harmony_contribution"):
                old_w = getattr(a, "weight", 1.0)
                d["cultural_harmony_contribution"] = (w_norm / old_w) * (a.cultural_harmony_contribution or 0) if old_w > 1e-9 else 0
            out.append(type(a)(**d))
        else:
            out.append(a)
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# HARPER HENRY GUARDRAILS (enforce on portfolio)
# ═══════════════════════════════════════════════════════════════════════════════

class HarperHenryGuardrails:
    """Enforces ethical, cultural, and behavioral limits on portfolio allocations."""

    def __init__(self, config: Union[Dict[str, Any], HarperHenryGuardrailsConfig, ACTORSConfig]):
        if isinstance(config, ACTORSConfig):
            c = config.harper_henry_guardrails
        elif isinstance(config, HarperHenryGuardrailsConfig):
            c = config
        else:
            c = HarperHenryGuardrailsConfig(
                ethical_investment=bool(config.get("ethical_investment", True)),
                max_social_risk=float(config.get("max_social_risk", 0.2)),
                cultural_alignment_min=float(config.get("cultural_alignment_min", 0.2)),
                festival_tilt_factor=float(config.get("festival_tilt", 1.0) if isinstance(config.get("festival_tilt"), (int, float)) else 1.2),
            )
        self.ethical_investment = c.ethical_investment
        self.max_social_risk = c.max_social_risk
        self.min_cultural_weight = c.cultural_alignment_min
        self.festival_tilt_factor = c.festival_tilt_factor

    def _is_cultural(self, asset_class: Any) -> bool:
        ac = getattr(asset_class, "value", str(asset_class))
        return ac in ("artisanal", "cultural_enterprise")

    def _is_festival_aligned(self, asset: Any) -> bool:
        if getattr(asset, "metadata", None):
            if asset.metadata.get("festival_commerce_aligned") or asset.metadata.get("tequila_ceramic_textile"):
                return True
        return self._is_cultural(getattr(asset, "asset_class", ""))

    def enforce(
        self,
        allocations: List[Any],
        assets_by_id: Dict[str, Any],
    ) -> List[Any]:
        """Enforce minimum cultural weight and apply festival tilt factor. Returns new list of allocations."""
        if not allocations:
            return allocations
        total_weight = sum(getattr(a, "weight", 0.0) for a in allocations)
        if total_weight <= 0:
            total_weight = 1.0
        cultural_ids = set()
        for aid, asset in assets_by_id.items():
            if asset and self._is_cultural(getattr(asset, "asset_class", "")):
                cultural_ids.add(aid)
        weights = []
        for a in allocations:
            w = getattr(a, "weight", 0.0)
            aid = getattr(a, "asset_id", None)
            asset = assets_by_id.get(aid) if aid else None
            if self._is_festival_aligned(asset) if asset else (aid in cultural_ids):
                w *= self.festival_tilt_factor
            weights.append((a, w, aid in cultural_ids))
        total = sum(w for _, w, _ in weights)
        if total <= 0:
            total = 1.0
        cultural_weight = sum(w for _, w, is_cult in weights if is_cult) / total
        if cultural_weight < self.min_cultural_weight and cultural_ids:
            n_cult = sum(1 for _, _, is_cult in weights if is_cult)
            n_other = len(weights) - n_cult
            if n_cult > 0 and n_other > 0:
                shortfall = self.min_cultural_weight * total - sum(w for _, w, is_cult in weights if is_cult)
                new_weights = []
                for (a, w, is_cult), _ in zip(weights, range(len(weights))):
                    if is_cult:
                        w = w + shortfall / n_cult
                    else:
                        w = w - shortfall / n_other
                    new_weights.append((a, max(0.0, w)))
                total = sum(w for _, w in new_weights) or 1.0
                weights = [(a, w / total, getattr(a, "asset_id", "") in cultural_ids) for a, w in new_weights]
        total = sum(w for _, w, _ in weights) or 1.0
        out = []
        for a, w, _ in weights:
            w_norm = w / total
            if hasattr(a, "__dataclass_fields__"):
                d = {f: getattr(a, f) for f in a.__dataclass_fields__}
                d["weight"] = w_norm
                if "cultural_harmony_contribution" in d:
                    old_w = getattr(a, "weight", 1.0)
                    d["cultural_harmony_contribution"] = (w_norm / old_w) * getattr(a, "cultural_harmony_contribution", 0) if old_w > 1e-9 else 0
                out.append(type(a)(**d))
            else:
                out.append(a)
        return out


# ═══════════════════════════════════════════════════════════════════════════════
# RICH METRICS & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RichMetrics:
    """Richer metrics: cultural, ethical, festival-aware, and financial."""
    cultural_exposure_pct: float = 0.0
    festival_tilt_impact: float = 0.0
    ethical_compliance_pct: float = 0.0
    social_risk: float = 0.0
    portfolio_sharpe_approx: float = 0.0
    diversification_score: float = 0.0
    var_95_approx: Optional[float] = None
    liquidity_score: float = 0.0
    timestamp: Optional[datetime] = None


def compute_rich_metrics(
    allocations: List[Any],
    assets_by_id: Dict[str, Any],
    portfolio_sharpe: float = 0.0,
    diversification_score: float = 0.0,
    festival_active: bool = False,
    festival_tilt_factor_used: float = 1.0,
) -> RichMetrics:
    """Compute rich metrics from allocations and asset lookup."""
    cultural_pct = 0.0
    ethical_pct = 0.0
    social_risk = 0.0
    liq = 0.0
    for a in allocations:
        w = getattr(a, "weight", 0.0)
        asset = assets_by_id.get(getattr(a, "asset_id", ""))
        if asset:
            ac = getattr(asset, "asset_class", None)
            ac_str = ac.value if hasattr(ac, "value") else str(ac) if ac else ""
            if ac_str in ("artisanal", "cultural_enterprise"):
                cultural_pct += w
            sust = getattr(asset, "sustainability_score", 0.5)
            ethical_pct += w * (0.3 + 0.7 * sust)
            if ac_str not in ("artisanal", "cultural_enterprise") and getattr(asset, "volatility", 0) > 0.2:
                social_risk += w * 0.5
            liq += w * getattr(asset, "liquidity_score", 0.5)
    festival_impact = (festival_tilt_factor_used - 1.0) * 0.02 if festival_active else 0.0
    return RichMetrics(
        cultural_exposure_pct=cultural_pct,
        festival_tilt_impact=festival_impact,
        ethical_compliance_pct=min(1.0, ethical_pct),
        social_risk=min(1.0, social_risk),
        portfolio_sharpe_approx=portfolio_sharpe,
        diversification_score=diversification_score,
        liquidity_score=liq,
        timestamp=datetime.now(),
    )


def _metrics_to_rows(metrics: Union[Dict[str, Any], RichMetrics, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Normalize metrics to list of flat dicts for export."""
    if isinstance(metrics, list):
        return [dict(m) for m in metrics]
    if hasattr(metrics, "__dataclass_fields__"):
        d = {k: getattr(metrics, k) for k in metrics.__dataclass_fields__}
        for k, v in d.items():
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        return [d]
    return [dict(metrics)]


def export_metrics(
    metrics: Union[Dict[str, Any], RichMetrics, List[Dict[str, Any]]],
    format: str = "json",
    filename: str = "metrics",
    path: Optional[Union[str, Path]] = None,
) -> str:
    """Export metrics to file (csv, json, or parquet). Returns the path of the written file."""
    path = path or Path.cwd()
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    rows = _metrics_to_rows(metrics)
    if not rows:
        raise ValueError("No metrics to export")
    if format.lower() == "csv":
        fp = path / f"{filename}.csv"
        with open(fp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return str(fp)
    if format.lower() == "json":
        fp = path / f"{filename}.json"
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, default=str)
        return str(fp)
    if format.lower() == "parquet":
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas required for Parquet export. pip install pandas pyarrow")
        fp = path / f"{filename}.parquet"
        df = pd.DataFrame(rows)
        df.to_parquet(fp, index=False)
        return str(fp)
    raise ValueError(f"Unsupported format: {format}. Use csv, json, or parquet.")


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT (with rich_metrics)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HarperHenryHarmonyMexicoResult:
    """Result of Mexico/Guadalajara edition optimization."""
    id: str
    engine_types_used: List[HarmonyEngineMexico]
    total_value_created: float
    optimization_score: float
    cultural_harmony_score: float
    allocations: List[MexicoPortfolioAllocation]
    guadalajara_startups_included: List[GuadalajaraStartup]
    jalisco_indicators: List[JaliscoIndicator]
    cultural_metrics: List[CulturalHarmonyMetric]
    simulation_scenarios: List[MarketSimulationScenario]
    final_risk_adjusted_return: float
    optimization_time: float
    harmony_achieved: bool
    created_at: datetime
    # Enhanced metrics
    portfolio_sharpe_approx: float = 0.0
    diversification_score: float = 0.0  # 1 / Herfindahl of weights
    behavioral_guardrail: Optional[BehavioralGuardrailResult] = None
    config_used: Optional[MexicoOptimizationConfig] = None
    rich_metrics: Optional[RichMetrics] = None

    def to_dict(self) -> Dict[str, Any]:
        """Export result to a JSON-serializable dict (e.g. for APIs or dashboards)."""
        return _result_to_serializable(self)

    def export_json(self, indent: Optional[int] = 2) -> str:
        """Export result as JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC BUILDERS – Local data feeds & AI-inferred allocations
# ═══════════════════════════════════════════════════════════════════════════════

async def async_builder_mexican_assets(
    jalisco_indicators: List[JaliscoIndicator],
    cultural_metrics: List[CulturalHarmonyMetric],
) -> List[MexicanAsset]:
    """Infer concrete Mexican asset set for allocation from regional indicators and cultural metrics."""
    await asyncio.sleep(0.05)  # Simulate async I/O
    gdp = next((i for i in jalisco_indicators if "gdp" in i.category.lower()), None)
    startup = next((i for i in jalisco_indicators if "startup" in i.category.lower()), None)
    cultural_avg = np.mean([m.value for m in cultural_metrics]) if cultural_metrics else 0.5
    assets = [
        MexicanAsset(
            id="mx_equity_1", asset_class=MexicanAssetClass.EQUITIES, name="Bolsa Mexicana Blue Chip", symbol="MEXBOL",
            region="national", expected_return=0.08, volatility=0.18, cultural_harmony_score=0.6,
            sustainability_score=0.5, liquidity_score=0.95, metadata={"jalisco_tied": False},
        ),
        MexicanAsset(
            id="mx_bond_1", asset_class=MexicanAssetClass.BONDS, name="CETES", symbol="CETES",
            region="national", expected_return=0.11, volatility=0.05, cultural_harmony_score=0.5,
            sustainability_score=0.6, liquidity_score=0.9, metadata={"duration": "28d"},
        ),
        MexicanAsset(
            id="gdl_real_estate_1", asset_class=MexicanAssetClass.REAL_ESTATE, name="Guadalajara Tech Corridor", symbol=None,
            region="guadalajara", expected_return=0.07 + (gdp.trend * 0.1 if gdp else 0),
            volatility=0.12, cultural_harmony_score=0.85, sustainability_score=0.7, liquidity_score=0.4,
            metadata={"cluster": "tech_corridor"},
        ),
        MexicanAsset(
            id="gdl_fintech_1", asset_class=MexicanAssetClass.FINTECH, name="GDL Fintech Hub ETF", symbol=None,
            region="guadalajara", expected_return=0.12, volatility=0.22, cultural_harmony_score=0.75,
            sustainability_score=0.65, liquidity_score=0.6, metadata={"jalisco_fintech": True},
        ),
        MexicanAsset(
            id="gdl_artisanal_1", asset_class=MexicanAssetClass.ARTISANAL, name="Jalisco Artisanal Fund", symbol=None,
            region="jalisco", expected_return=0.05, volatility=0.15, cultural_harmony_score=0.95,
            sustainability_score=0.9, liquidity_score=0.3, metadata={"tequila_ceramic_textile": True},
        ),
        MexicanAsset(
            id="gdl_cultural_1", asset_class=MexicanAssetClass.CULTURAL_ENTERPRISE, name="Cultural Enterprise Fund GDL", symbol=None,
            region="guadalajara", expected_return=0.04, volatility=0.14, cultural_harmony_score=0.98,
            sustainability_score=0.85, liquidity_score=0.25, metadata={"festival_commerce_aligned": True},
        ),
    ]
    return assets


async def async_builder_local_sentiment_feeds() -> List[LocalDataFeed]:
    """Process local market sentiment from social, financial, and local media sources."""
    await asyncio.sleep(0.03)
    now = datetime.now()
    return [
        LocalDataFeed("feed_1", "social", "GDL Tech Twitter", 0.35, 0.9, 0.4, now),
        LocalDataFeed("feed_2", "financial", "BMV Sentiment", 0.2, 0.7, 0.25, now),
        LocalDataFeed("feed_3", "local_media", "Mural GDL", 0.5, 0.95, 0.45, now),
        LocalDataFeed("feed_4", "startup_news", "Startup GDL Index", 0.6, 0.98, 0.55, now),
    ]


async def async_builder_guadalajara_startups(
    feeds: List[LocalDataFeed],
    jalisco_indicators: List[JaliscoIndicator],
) -> List[GuadalajaraStartup]:
    """AI-driven identification of high-potential Guadalajara startups for dynamic weightings."""
    await asyncio.sleep(0.04)
    sentiment = np.mean([f.sentiment_score for f in feeds]) if feeds else 0.0
    startup_growth = next((i for i in jalisco_indicators if "startup" in i.category.lower()), None)
    growth_factor = (startup_growth.value / 100.0) if startup_growth else 0.15
    return [
        GuadalajaraStartup("s1", "TechSoft GDL", GuadalajaraCluster.IT_SOFTWARE, "series_a", 8e6, 0.4 + sentiment * 0.1, 0.7, 0.8, 0.6, 25.0, {}),
        GuadalajaraStartup("s2", "AI Jalisco", GuadalajaraCluster.AI_ML, "seed", 2e6, 0.6 + growth_factor * 0.2, 0.85, 0.9, 0.75, 12.0, {}),
        GuadalajaraStartup("s3", "Hardware Labs GDL", GuadalajaraCluster.HARDWARE_ELECTRONICS, "series_b", 25e6, 0.35, 0.65, 0.7, 0.5, 50.0, {}),
        GuadalajaraStartup("s4", "FinTech Jalisco", GuadalajaraCluster.FINTECH, "series_a", 12e6, 0.5, 0.75, 0.85, 0.7, 30.0, {}),
        GuadalajaraStartup("s5", "Creativa GDL", GuadalajaraCluster.CREATIVE_TECH, "seed", 1.5e6, 0.55, 0.8, 0.75, 0.85, 8.0, {}),
    ]


async def async_builder_cultural_harmony_metrics(region: str = "guadalajara") -> List[CulturalHarmonyMetric]:
    """Build cultural exchange metrics (social sentiment, community engagement, cultural impact) for optimization."""
    await asyncio.sleep(0.02)
    now = datetime.now()
    return [
        CulturalHarmonyMetric("ch1", "Social Sentiment GDL", "social_sentiment", 0.72, 0.25, "Local social sentiment index", region, now),
        CulturalHarmonyMetric("ch2", "Community Engagement", "community_engagement", 0.68, 0.25, "Community and civic engagement", region, now),
        CulturalHarmonyMetric("ch3", "Cultural Impact Index", "cultural_impact", 0.81, 0.3, "Festivals, arts, heritage impact", region, now),
        CulturalHarmonyMetric("ch4", "Festival & Commerce Cycle", "festival_cycle", 0.65, 0.2, "Alignment with local festivals and commerce", region, now),
    ]


async def async_builder_jalisco_indicators() -> List[JaliscoIndicator]:
    """Fetch and normalize Jalisco/Guadalajara regional economic indicators."""
    await asyncio.sleep(0.03)
    now = datetime.now()
    return [
        JaliscoIndicator("j1", "Jalisco GDP Growth", 3.2, "percent", 0.4, "gdp", "INEGI", now),
        JaliscoIndicator("j2", "Industrial Cluster Index", 112.0, "index", 2.1, "industrial_cluster", "State", now),
        JaliscoIndicator("j3", "Startup Growth GDL", 18.0, "percent", 5.0, "startup_growth", "Startup GDL", now),
        JaliscoIndicator("j4", "Employment Tech Sector", 8.5, "percent", 1.2, "employment", "IMSS", now),
        JaliscoIndicator("j5", "FDI Jalisco", 1.8, "percent of GDP", 0.3, "fdi", "SE", now),
        JaliscoIndicator("j6", "Remittances Inflow", 4.2, "percent yoy", 2.0, "remittances", "Banxico", now),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# HARPER HENRY BEHAVIORAL GUARDRAIL (Psychology of Speculation)
# ═══════════════════════════════════════════════════════════════════════════════

def harper_henry_behavioral_check(
    allocations: List[MexicoPortfolioAllocation],
    assets_by_id: Dict[str, MexicanAsset],
    volatility_tolerance: float = 0.20,
) -> BehavioralGuardrailResult:
    """
    Behavioral Superego: detect greed (over-concentration in high-vol),
    panic (flight to single safe asset), and suggest cool-down if needed.
    """
    if not allocations:
        return BehavioralGuardrailResult(
            behavioral_risk_score=0.0,
            cool_down_suggested=False,
            rationale="No allocations to evaluate.",
            resonance_check_passed=True,
        )
    weights = np.array([a.weight for a in allocations])
    vols = np.array([
        assets_by_id.get(a.asset_id)
        for a in allocations
    ])
    # Resolve volatility from allocations' asset_class if no asset lookup
    vol_list = []
    for a in allocations:
        ax = next((x for x in assets_by_id.values() if x.id == a.asset_id), None)
        vol_list.append(ax.volatility if ax else 0.15)
    vol_arr = np.array(vol_list)

    portfolio_vol = np.sqrt(np.dot(weights**2, vol_arr**2) + 2 * np.mean(vol_arr) * 0.1 * (1 - (weights**2).sum()))
    portfolio_vol = float(np.clip(portfolio_vol, 0.05, 0.5))
    max_single_weight = float(weights.max())
    herfindahl = float(np.dot(weights, weights))

    # Greed: very high weight in high-vol assets
    high_vol_share = float(np.dot(weights, (vol_arr > 0.18).astype(float)))
    # Panic: everything in one basket
    concentration_risk = max_single_weight > 0.45 or herfindahl > 0.35

    behavioral_risk = 0.0
    rationale_parts = []

    if portfolio_vol > volatility_tolerance:
        behavioral_risk += 0.3
        rationale_parts.append("Portfolio volatility above tolerance (possible overreach).")
    if concentration_risk:
        behavioral_risk += 0.4
        rationale_parts.append("High concentration—consider diversifying (Harper: avoid tickeritis).")
    if high_vol_share > 0.5:
        behavioral_risk += 0.2
        rationale_parts.append("Large allocation to high-volatility assets.")

    cool_down = behavioral_risk >= 0.5
    if cool_down:
        rationale_parts.append("Cool-down suggested: reduce size or volatility before adding risk.")
    rationale = " ".join(rationale_parts) if rationale_parts else "Resonance check passed: allocation aligned with long-term goals."

    return BehavioralGuardrailResult(
        behavioral_risk_score=min(1.0, behavioral_risk),
        cool_down_suggested=cool_down,
        rationale=rationale,
        suggested_max_volatility=volatility_tolerance if cool_down else None,
        resonance_check_passed=not cool_down,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO OPTIMIZATION WITH CULTURAL HARMONY
# ═══════════════════════════════════════════════════════════════════════════════

def _risk_adjusted_weight(
    asset: MexicanAsset,
    cultural_metrics: List[CulturalHarmonyMetric],
    currency_vol_factor: float = 1.0,
    regulation_risk: float = 0.1,
) -> float:
    """Weights asset by return, volatility, cultural harmony, and regional risk."""
    ret = asset.expected_return
    vol = max(asset.volatility, 0.01) + regulation_risk * 0.05
    sharpe = (ret - 0.05) / vol
    cultural_avg = np.mean([m.value for m in cultural_metrics]) if cultural_metrics else 0.5
    harmony = asset.cultural_harmony_score * 0.4 + cultural_avg * 0.3 + asset.sustainability_score * 0.3
    return max(0.0, sharpe * 0.5 + harmony * 0.5 - currency_vol_factor * 0.05)


def _festival_tilt_weights(assets: List[MexicanAsset], month: Optional[int]) -> Dict[str, float]:
    """Return per-asset-id multiplier >= 1 for artisanal/cultural in festival months."""
    if month is None:
        return {}
    # Día de Muertos / Feria GDL / year-end: boost artisanal and cultural
    tilt_months = (10, 11, 12)  # Oct–Dec
    if month not in tilt_months:
        return {}
    boost = 1.25
    return {
        a.id: boost
        for a in assets
        if a.asset_class in (MexicanAssetClass.ARTISANAL, MexicanAssetClass.CULTURAL_ENTERPRISE)
    }


def optimize_mexico_portfolio_cultural(
    assets: List[MexicanAsset],
    cultural_metrics: List[CulturalHarmonyMetric],
    currency_volatility: float = 0.08,
    regulation_risk: float = 0.1,
    min_cultural_weight: float = 0.10,
    festival_tilt_month: Optional[int] = None,
) -> List[MexicoPortfolioAllocation]:
    """
    Optimize portfolio weights subject to cultural harmony and regional risk.
    Enforces a minimum combined weight on artisanal + cultural_enterprise.
    Optional festival_tilt_month (1–12) boosts those in relevant months.
    """
    tilt = _festival_tilt_weights(assets, festival_tilt_month)
    weights_raw = [
        _risk_adjusted_weight(a, cultural_metrics, currency_volatility, regulation_risk)
        * tilt.get(a.id, 1.0)
        for a in assets
    ]
    total = sum(weights_raw)
    weights = [w / total if total > 0 else 1.0 / len(assets) for w in weights_raw]

    # Enforce min_cultural_weight on artisanal + cultural_enterprise
    cultural_ids = {
        a.id for a in assets
        if a.asset_class in (MexicanAssetClass.ARTISANAL, MexicanAssetClass.CULTURAL_ENTERPRISE)
    }
    cultural_weight = sum(w for a, w in zip(assets, weights) if a.id in cultural_ids)
    n_cultural = len(cultural_ids)
    n_other = len(assets) - n_cultural
    if cultural_weight < min_cultural_weight and n_cultural > 0 and n_other > 0:
        shortfall = min_cultural_weight - cultural_weight
        for i, a in enumerate(assets):
            if a.id in cultural_ids:
                weights[i] += shortfall / n_cultural
            else:
                weights[i] -= shortfall / n_other
        weights = [max(0.0, w) for w in weights]
        total = sum(weights)
        weights = [w / total for w in weights]

    now = datetime.now()
    allocations = []
    for a, w in zip(assets, weights):
        allocations.append(MexicoPortfolioAllocation(
            asset_id=a.id,
            asset_class=a.asset_class,
            weight=w,
            rationale=f"Risk-adjusted + cultural harmony; region={a.region}",
            risk_adjusted_return=a.expected_return - 0.5 * a.volatility ** 2,
            cultural_harmony_contribution=a.cultural_harmony_score * w,
            inferred_at=now,
        ))
    return allocations


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def run_market_simulation(
    allocations: List[MexicoPortfolioAllocation],
    jalisco_indicators: List[JaliscoIndicator],
    feeds: List[LocalDataFeed],
    n_scenarios: int = 5,
) -> List[MarketSimulationScenario]:
    """Simulate scenarios combining Mexican macro, Guadalajara indicators, and AI-inferred behaviors."""
    rng = np.random.default_rng(42)
    scenarios = []
    macro_trends = rng.uniform(0.0, 0.05, n_scenarios)
    gdl_trends = rng.uniform(0.01, 0.06, n_scenarios)
    ai_behaviors = rng.uniform(0.0, 0.04, n_scenarios)
    sentiment = np.mean([f.sentiment_score for f in feeds]) if feeds else 0.0
    sentiment_factors = sentiment + rng.uniform(-0.1, 0.1, n_scenarios)

    portfolio_ret = sum(
        a.weight * (0.06 + 0.5 * (a.risk_adjusted_return or 0))
        for a in allocations
    ) if allocations else 0.06

    for i in range(n_scenarios):
        est_return = portfolio_ret + 0.3 * macro_trends[i] + 0.3 * gdl_trends[i] + 0.2 * ai_behaviors[i] + 0.2 * sentiment_factors[i]
        risk = "high" if (macro_trends[i] + gdl_trends[i]) < 0.02 else ("medium" if est_return < 0.08 else "low")
        scenarios.append(MarketSimulationScenario(
            scenario_id=f"sc_{i+1}",
            name=f"Scenario Mexico-GDL {i+1}",
            mexican_macro_trend=float(macro_trends[i]),
            guadalajara_indicator_trend=float(gdl_trends[i]),
            ai_inferred_behavior=float(ai_behaviors[i]),
            sentiment_factor=float(sentiment_factors[i]),
            portfolio_return_estimate=float(est_return),
            risk_level=risk,
            created_at=datetime.now(),
        ))
    return scenarios


def _portfolio_sharpe_and_diversification(
    allocations: List[MexicoPortfolioAllocation],
    assets_by_id: Dict[str, MexicanAsset],
    risk_free: float = 0.05,
) -> Tuple[float, float]:
    """Return (Sharpe ratio approx, diversification score = 1/Herfindahl)."""
    if not allocations:
        return 0.0, 0.0
    weights = np.array([a.weight for a in allocations])
    rets = np.array([a.risk_adjusted_return for a in allocations])
    vols = np.array([
        (assets_by_id[a.asset_id].volatility if assets_by_id.get(a.asset_id) else 0.15)
        for a in allocations
    ])
    port_ret = float(np.dot(weights, rets))
    port_vol = float(np.sqrt(np.maximum(np.dot(weights**2, vols**2), 1e-8)))
    sharpe = (port_ret - risk_free) / port_vol if port_vol > 1e-6 else 0.0
    herfindahl = float(np.dot(weights, weights))
    diversification = 1.0 / herfindahl if herfindahl > 1e-8 else 0.0
    return sharpe, diversification


def _result_to_serializable(obj: Any) -> Any:
    """Convert result components to JSON-serializable form."""
    if obj is None:
        return None
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _result_to_serializable(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_result_to_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _result_to_serializable(v) for k, v in obj.items()}
    return obj


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR – Harper Henry Harmony Mexico / Guadalajara
# ═══════════════════════════════════════════════════════════════════════════════

class HarperHenryHarmonyMexico:
    """
    Mexico / Guadalajara Edition: AI-driven portfolio optimization with cultural
    exchange harmony. Integrates Guadalajara tech hub, Jalisco indicators,
    cultural metrics, and market simulation.
    """

    def __init__(self):
        self.allocations_cache: List[MexicoPortfolioAllocation] = []
        self.simulation_cache: List[MarketSimulationScenario] = []

    async def optimize_mexico_portfolio(
        self,
        currency_volatility: float = 0.08,
        regulation_risk: float = 0.1,
        include_simulation: bool = True,
        n_simulation_scenarios: int = 5,
        min_cultural_weight: float = 0.10,
        festival_tilt_month: Optional[int] = None,
        apply_behavioral_guardrails: bool = True,
        config: Optional[MexicoOptimizationConfig] = None,
    ) -> HarperHenryHarmonyMexicoResult:
        """
        Run full Mexico/Guadalajara optimization pipeline with async builders.
        Pass config= to use MexicoOptimizationConfig; otherwise individual params apply.
        """
        if config is not None:
            currency_volatility = config.currency_volatility
            regulation_risk = config.regulation_risk
            min_cultural_weight = config.min_cultural_weight
            festival_tilt_month = config.festival_tilt_month
            n_simulation_scenarios = config.n_simulation_scenarios
            include_simulation = config.include_simulation
            apply_behavioral_guardrails = config.apply_behavioral_guardrails
        else:
            config = MexicoOptimizationConfig(
                currency_volatility=currency_volatility,
                regulation_risk=regulation_risk,
                min_cultural_weight=min_cultural_weight,
                festival_tilt_month=festival_tilt_month,
                n_simulation_scenarios=n_simulation_scenarios,
                include_simulation=include_simulation,
                apply_behavioral_guardrails=apply_behavioral_guardrails,
            )

        start = time.time()
        engines_used = []

        # 1) Regional indicators & cultural metrics (async)
        jalisco_indicators = await async_builder_jalisco_indicators()
        cultural_metrics = await async_builder_cultural_harmony_metrics("guadalajara")
        engines_used.append(HarmonyEngineMexico.CULTURAL_EXCHANGE_METRICS)

        # 2) Mexican assets (inferred from indicators + cultural)
        assets = await async_builder_mexican_assets(jalisco_indicators, cultural_metrics)
        engines_used.append(HarmonyEngineMexico.VALUE_CREATION_MEXICO)

        # 3) Local sentiment feeds
        feeds = await async_builder_local_sentiment_feeds()
        engines_used.append(HarmonyEngineMexico.CONCRETE_TYPE_ASYNC_GDL)

        # 4) Guadalajara startups for dynamic weightings
        startups = await async_builder_guadalajara_startups(feeds, jalisco_indicators)
        engines_used.append(HarmonyEngineMexico.GUADALAJARA_TECH_HUB)

        # 5) Portfolio optimization with cultural harmony (min cultural weight + optional festival tilt)
        allocations = optimize_mexico_portfolio_cultural(
            assets,
            cultural_metrics,
            currency_volatility=currency_volatility,
            regulation_risk=regulation_risk,
            min_cultural_weight=min_cultural_weight,
            festival_tilt_month=festival_tilt_month,
        )
        self.allocations_cache = allocations
        engines_used.append(HarmonyEngineMexico.PORTFOLIO_OPTIMIZATION_CULTURAL)

        # 6) Market simulation
        simulation_scenarios = []
        if include_simulation:
            simulation_scenarios = run_market_simulation(
                allocations, jalisco_indicators, feeds, n_simulation_scenarios
            )
            self.simulation_cache = simulation_scenarios
            engines_used.append(HarmonyEngineMexico.MARKET_SIMULATION_ENGINE)

        # 7) Harper Henry behavioral guardrail (Psychology of Speculation)
        assets_by_id = {a.id: a for a in assets}
        behavioral_guardrail = None
        if apply_behavioral_guardrails:
            behavioral_guardrail = harper_henry_behavioral_check(
                allocations, assets_by_id, volatility_tolerance=0.20
            )

        # 8) Sharpe & diversification metrics
        portfolio_sharpe, diversification_score = _portfolio_sharpe_and_diversification(
            allocations, assets_by_id
        )

        # 9) Rich metrics (cultural exposure, ethical compliance, social risk, festival impact)
        festival_active = bool(get_active_festivals(GUADALAJARA_FESTIVAL_CALENDAR))
        tilt_used = 1.25 if festival_active else 1.0
        rich_metrics = compute_rich_metrics(
            allocations,
            assets_by_id,
            portfolio_sharpe=portfolio_sharpe,
            diversification_score=diversification_score,
            festival_active=festival_active,
            festival_tilt_factor_used=tilt_used,
        )

        engines_used.append(HarmonyEngineMexico.HARPER_HENRY_HARMONY_MEXICO)

        total_value = sum(a.weight * (1.0 + a.risk_adjusted_return) for a in allocations)
        opt_score = min(1.0, total_value / 1.15)
        cultural_score = sum(a.cultural_harmony_contribution for a in allocations)
        risk_adj_ret = sum(a.weight * a.risk_adjusted_return for a in allocations)
        avg_sim_ret = np.mean([s.portfolio_return_estimate for s in simulation_scenarios]) if simulation_scenarios else risk_adj_ret
        harmony_achieved = cultural_score >= 0.5 and opt_score >= 0.7

        return HarperHenryHarmonyMexicoResult(
            id=f"mexico_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            engine_types_used=engines_used,
            total_value_created=float(total_value),
            optimization_score=float(opt_score),
            cultural_harmony_score=float(cultural_score),
            allocations=allocations,
            guadalajara_startups_included=startups,
            jalisco_indicators=jalisco_indicators,
            cultural_metrics=cultural_metrics,
            simulation_scenarios=simulation_scenarios,
            final_risk_adjusted_return=float(avg_sim_ret),
            optimization_time=time.time() - start,
            harmony_achieved=harmony_achieved,
            created_at=datetime.now(),
            portfolio_sharpe_approx=float(portfolio_sharpe),
            diversification_score=float(diversification_score),
            behavioral_guardrail=behavioral_guardrail,
            config_used=config,
            rich_metrics=rich_metrics,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FULL AI-DRIVEN SYSTEM ARCHITECTURE – Investor-ready (Mexico / Guadalajara)
# ═══════════════════════════════════════════════════════════════════════════════

def print_guadalajara_architecture() -> str:
    """Print the full AI-driven system architecture: local ingestion, global alignment,
    async builders, optimization engine, and cultural impact feedback loops."""
    diagram = r"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🎭 HARPER HENRY HARMONY — Globally Optimized, AI-Driven Investment Frontier         ║
║  "Where precision finance meets cultural intelligence."                              ║
║  Full system architecture: Local + Global → Async AI → Optimization → Feedback       ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

 ┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
 │  LOCAL DATA INGESTION               │     │  GLOBAL MARKET ALIGNMENT             │
 │  Mexico / Guadalajara               │     │  Cross-border signals                │
 ├─────────────────────────────────────┤     ├─────────────────────────────────────┤
 │  • Jalisco GDP, industrial clusters │     │  • Global equity / FX / rates        │
 │  • Startup growth & valuations      │     │  • EM indices (Mexico, LATAM)        │
 │  • Social sentiment (GDL tech)      │     │  • Risk-on/risk-off regimes          │
 │  • Local media (e.g. Mural)         │     │  • Macro trend overlays              │
 │  • BMV / Fintech sentiment          │     │  • Real-time feed merge                    │
 │  • Festival & commerce cycles       │     └──────────────┬─────────────────┘
 └──────────────┬──────────────────────┘                    │
                │                                               │
                ▼                                               ▼
 ┌───────────────────────────────────────────────────────────────────────────────────┐
 │                     ASYNC AI BUILDERS (Infer concrete types)                       │
 ├───────────────────────────────────────────────────────────────────────────────────┤
 │  • Mexican Assets Builder     → Equities, bonds, real estate, fintech, artisanal   │
 │  • Guadalajara Startups       → IT, AI/ML, hardware, fintech clusters              │
 │  • Jalisco Indicators         → Normalized regional economic indicators            │
 │  • Cultural Harmony Metrics   → Social sentiment, community, festivals, heritage   │
 │  • Local–global fusion        → Align regional opportunities with global trends    │
 └───────────────────────────────────────────┬───────────────────────────────────────┘
                                             │
                                             ▼
 ┌───────────────────────────────────────────────────────────────────────────────────┐
 │                     PORTFOLIO OPTIMIZATION ENGINE                                  │
 ├───────────────────────────────────────────────────────────────────────────────────┤
 │  • Risk-adjusted allocation (volatility, currency, regulation)                     │
 │  • Scenario simulation (Mexican macro + GDL indicators + AI-inferred behavior)     │
 │  • Dynamic weightings: startup performance, exit potential, real-time sentiment    │
 │  • Cultural harmony constraint: sustainable tech, artisanal, cultural enterprises  │
 │  • Output: Optimal weights, expected return, risk level, cultural contribution     │
 └───────────────────────────────────────────┬───────────────────────────────────────┘
                                             │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         │                                   ▼                                   │
         │  ┌─────────────────────────────────────────────────────────────────┐  │
         │  │           CULTURAL IMPACT FEEDBACK LOOPS                         │  │
         │  ├─────────────────────────────────────────────────────────────────┤  │
         │  │  • Local communities & festivals  ──► Cultural impact index      │  │
         │  │  • Heritage & creative industries ──► Re-weight artisanal / GDL   │  │
         │  │  • Regional development outcomes ──► Adjust allocation priorities │  │
         │  │  • Social sentiment & engagement  ──► Refine scenario assumptions │  │
         └──┼──►  (Feedback into Async AI Builders & Optimization Engine)  ────┼──┘
            │  └─────────────────────────────────────────────────────────────────┘
            │                                    │
            │                                    ▼
            │  ┌─────────────────────────────────────────────────────────────────┐
            │  │           HARPER HENRY HARMONY OUTPUT                            │
            │  ├─────────────────────────────────────────────────────────────────┤
            │  │  Allocations  │  Startup inclusions  │  Cultural score           │
            │  │  Risk-adj return  │  Scenario band  │  Harmony achieved  ✓       │
            │  └─────────────────────────────────────────────────────────────────┘
            │
            └── Global market alignment can refresh and re-run optimization (real-time)

 Vision: HARPER HENRY HARMONY transforms Guadalajara and Mexican markets into a
         globally optimized, AI-driven investment frontier—where mathematical
         precision, cultural intelligence, and financial opportunity converge.
"""
    print(diagram)
    return diagram


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════════════════

async def run_mexico_edition_demo() -> None:
    """Run the Mexico/Guadalajara edition demo and print architecture."""
    print_guadalajara_architecture()
    print("\n" + "=" * 70)
    print("Running Mexico / Guadalajara optimization pipeline...")
    print("=" * 70 + "\n")

    engine = HarperHenryHarmonyMexico()
    result = await engine.optimize_mexico_portfolio(
        currency_volatility=0.08,
        regulation_risk=0.1,
        include_simulation=True,
        n_simulation_scenarios=5,
    )

    print("📊 JALISCO INDICATORS:")
    for ind in result.jalisco_indicators:
        print(f"   • {ind.name}: {ind.value} {ind.unit} (trend: {ind.trend})")

    print("\n📈 ALLOCATIONS (risk-adjusted + cultural harmony):")
    for a in result.allocations:
        print(f"   • {a.asset_id} ({a.asset_class.value}): weight={a.weight:.2%}  risk-adj ret={a.risk_adjusted_return:.2%}  culture={a.cultural_harmony_contribution:.2%}")

    print("\n🚀 GUADALAJARA STARTUPS (included for dynamic weightings):")
    for s in result.guadalajara_startups_included:
        print(f"   • {s.name} ({s.cluster.value}) stage={s.stage} growth={s.growth_rate:.1%} exit_potential={s.exit_potential:.2}")

    print("\n🎭 CULTURAL HARMONY METRICS:")
    for m in result.cultural_metrics:
        print(f"   • {m.name}: {m.value:.2} (weight in opt: {m.weight_in_optimization:.2})")

    print("\n📉 SIMULATION SCENARIOS:")
    for sc in result.simulation_scenarios:
        print(f"   • {sc.name}: est. return={sc.portfolio_return_estimate:.2%} risk={sc.risk_level}")

    print(f"\n📐 ENHANCED METRICS:")
    print(f"   • Portfolio Sharpe (approx): {result.portfolio_sharpe_approx:.3f}")
    print(f"   • Diversification score (1/HHI): {result.diversification_score:.2f}")

    if result.rich_metrics:
        rm = result.rich_metrics
        print(f"\n📊 RICH METRICS (ACTORS v2):")
        print(f"   • Cultural exposure: {rm.cultural_exposure_pct:.1%}  Ethical compliance: {rm.ethical_compliance_pct:.1%}")
        print(f"   • Social risk: {rm.social_risk:.2f}  Festival tilt impact: {rm.festival_tilt_impact:.2%}  Liquidity: {rm.liquidity_score:.2f}")

    if result.behavioral_guardrail:
        bg = result.behavioral_guardrail
        print(f"\n🧠 HARPER HENRY BEHAVIORAL GUARDRAIL (Psychology of Speculation):")
        print(f"   • Behavioral risk score: {bg.behavioral_risk_score:.2f} (0=calm, 1=high)")
        print(f"   • Cool-down suggested: {bg.cool_down_suggested}")
        print(f"   • Resonance check passed: {bg.resonance_check_passed}")
        print(f"   • Rationale: {bg.rationale}")

    print(f"\n✅ RESULT: optimization_score={result.optimization_score:.2%}  cultural_harmony_score={result.cultural_harmony_score:.2%}")
    print(f"   final_risk_adjusted_return={result.final_risk_adjusted_return:.2%}  harmony_achieved={result.harmony_achieved}")
    print(f"   optimization_time={result.optimization_time:.3f}s")

    print(f"\n💾 Export: result.to_dict() / result.export_json() available ({len(result.export_json())} chars).")
    if result.rich_metrics:
        try:
            export_metrics(result.rich_metrics, format="json", filename="harper_henry_mexico_metrics", path=Path.cwd())
            print("   Rich metrics written to harper_henry_mexico_metrics.json")
        except Exception as e:
            print(f"   (export_metrics skipped: {e})")
    print("\n" + "=" * 70)


async def run_mexico_edition_with_festival_tilt() -> None:
    """Run optimization with festival tilt (e.g. Nov = Día de Muertos / Feria) boosting artisanal & cultural."""
    print("\n🎭 Mexico edition with FESTIVAL TILT (month=11) — higher weight to artisanal/cultural\n")
    engine = HarperHenryHarmonyMexico()
    config = MexicoOptimizationConfig(
        festival_tilt_month=11,
        min_cultural_weight=0.20,
        apply_behavioral_guardrails=True,
    )
    result = await engine.optimize_mexico_portfolio(config=config)
    cultural_weight = sum(
        a.weight for a in result.allocations
        if a.asset_class.value in ("artisanal", "cultural_enterprise")
    )
    print(f"   Combined artisanal + cultural weight: {cultural_weight:.2%}")
    print(f"   Sharpe: {result.portfolio_sharpe_approx:.3f}  Diversification: {result.diversification_score:.2f}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# HYPER-HEURISTIC SMART CONTRACT — MULTI-PROTOCOL / MULTI-CHAIN INTEGRATION PLAN
# ═══════════════════════════════════════════════════════════════════════════════
# Structured platform integration for on-chain adaptability, gas efficiency,
# and auditability. Phases 0–5 with dependencies and actionable steps.
# ═══════════════════════════════════════════════════════════════════════════════

class IntegrationPhase(Enum):
    """Phases of the hyper-heuristic platform integration plan."""
    PHASE_0_PRELIMINARY = "phase_0_preliminary"
    PHASE_1_ABSTRACTION = "phase_1_cross_platform_abstraction"
    PHASE_2_PROTOCOL = "phase_2_protocol_specific"
    PHASE_3_DEPLOYMENT = "phase_3_deployment_testing"
    PHASE_4_MONITORING = "phase_4_monitoring_management"
    PHASE_5_IMPROVEMENT = "phase_5_continuous_improvement"


class TargetPlatform(Enum):
    """Target blockchains for deployment."""
    ETHEREUM_L1 = "ethereum_l1"
    POLYGON = "polygon"
    BSC = "bsc"
    AVALANCHE = "avalanche"


class TargetProtocol(Enum):
    """Target DeFi protocol categories."""
    DEX_UNISWAP_SUSHISWAP = "dex_uniswap_sushiswap"
    DEX_CURVE_BALANCER = "dex_curve_balancer"
    LENDING_AAVE_COMPOUND = "lending_aave_compound"


HYPER_HEURISTIC_PLATFORM_INTEGRATION_PLAN: Dict[str, Any] = {
    "phase_0_preliminary": {
        "name": "Preliminary Assessment",
        "platform_mapping": [
            "Identify target blockchains: Ethereum L1, Polygon, BSC, Avalanche, etc.",
            "Identify target DeFi protocols per platform: Uniswap/Sushiswap, Aave/Compound, Curve, Balancer.",
            "Document differences in EVM versions, gas model, and oracle access.",
        ],
        "heuristic_library_audit": [
            "Review existing low-level heuristics for compatibility with each protocol.",
            "Identify protocol-specific parameters (e.g., slippage, LTV, collateral types).",
        ],
        "state_feature_analysis": [
            "Map required on-chain features per platform: gas price, pool reserves, oracle lag, token volatility, etc.",
            "Determine availability and cost of fetching features on-chain or via trusted oracles.",
        ],
    },
    "phase_1_abstraction": {
        "name": "Cross-Platform Abstraction Layer",
        "contract_wrapper": [
            "Implement thin abstraction layer standardizing: feature extraction, oracle reading, heuristic dispatch, logging.",
        ],
        "state_normalization": [
            "Standardize feature vectors across platforms: scale gas prices, normalize LTV ranges, bucket volatility.",
            "Ensure high-level controller operates consistently across blockchains.",
        ],
        "decision_policy_serialization": [
            "Compile RL policy into platform-agnostic decision tree or lookup table.",
            "Enable deployment on EVM-compatible chains without modifying policy logic.",
        ],
    },
    "phase_2_protocol": {
        "name": "Protocol-Specific Integration",
        "dex_integration": [
            "Wrap swap functions with hyper-heuristic controller: Uniswap/Sushiswap (slippage, routing), Curve/Balancer (pool allocation).",
            "Implement event logging for trade success/failure and gas consumption.",
        ],
        "lending_integration": [
            "Wrap lending/borrowing with adaptive LTV and interest rate heuristics: Aave/Compound (collateral factor, liquidation thresholds).",
            "Maintain protocol-specific safety margins to prevent liquidation cascades.",
        ],
        "oracle_layer": [
            "Integrate Chainlink or custom on-chain feeds per platform; ensure fallback mechanisms for missing or delayed data.",
        ],
    },
    "phase_3_deployment": {
        "name": "Deployment & Testing",
        "testnet_deployment": [
            "Deploy on testnets: Ethereum→Goerli, Polygon→Mumbai, BSC→Testnet.",
            "Validate: gas cost per heuristic selection, decision correctness, logging and audit trail.",
        ],
        "simulation": [
            "Replay historical transactions per platform; verify tx success improvement, gas efficiency, stress-test under volatility.",
        ],
        "security_audit": [
            "Formal verification for decision logic and low-level heuristics; penetration testing; fallback heuristics if RL policy fails.",
        ],
    },
    "phase_4_monitoring": {
        "name": "Cross-Platform Monitoring and Management",
        "metric_collection": [
            "Centralized off-chain dashboard: transaction success rates, gas consumption, heuristic utilization, risk exposure.",
        ],
        "adaptive_updates": [
            "Optional: federated RL or meta-learning across platforms; verifiable off-chain updates with zkSNARK validation on-chain.",
        ],
        "compliance_explainability": [
            "Export explainability logs per platform: SHAP-like contributions, heuristic choice metadata; MiCA/regulatory audit trail.",
        ],
    },
    "phase_5_improvement": {
        "name": "Continuous Improvement",
        "policy_retraining": [
            "Periodically retrain RL controller with updated transaction data; recompile decision tree and redeploy with minimal disruption.",
        ],
        "heuristic_expansion": [
            "Add new rules for emerging protocols or market conditions; ensure backward compatibility with existing state vectors.",
        ],
        "cross_protocol_coordination": [
            "Optional: arbitrage or liquidity-balancing heuristics across platforms; monitor cross-chain state for consistent rule application.",
        ],
    },
    "deliverables_per_platform": [
        "Hyper-heuristic smart contract deployed on-chain",
        "Serialized RL decision policy (decision tree)",
        "Protocol-specific low-level heuristic library",
        "Logging and explainability modules",
        "Off-chain dashboard for metrics, monitoring, and optional federated updates",
    ],
}


def get_hyper_heuristic_integration_plan_doc() -> str:
    """Return the full narrative platform integration plan (Phase 0–5 and deliverables) for docs or export."""
    return r"""
HYPER-HEURISTIC SMART CONTRACT — MULTI-PROTOCOL / MULTI-CHAIN PLATFORM INTEGRATION PLAN
Support for multi-protocol and multi-chain deployment while preserving on-chain adaptability,
gas efficiency, and auditability.

——— Phase 0: Preliminary Assessment ———
• Platform Mapping: Identify target blockchains (Ethereum L1, Polygon, BSC, Avalanche);
  target DeFi protocols per platform (Uniswap/Sushiswap, Aave/Compound, Curve, Balancer);
  document EVM versions, gas model, oracle access.
• Heuristic Library Audit: Review low-level heuristics for protocol compatibility;
  identify protocol-specific parameters (slippage, LTV, collateral types).
• State Feature Analysis: Map on-chain features per platform (gas price, pool reserves,
  oracle lag, token volatility); determine availability and cost (on-chain vs oracles).

——— Phase 1: Cross-Platform Abstraction Layer ———
• Contract Wrapper: Thin abstraction for feature extraction, oracle reading, heuristic dispatch, logging.
• State Normalization Module: Standardize feature vectors (scale gas, normalize LTV, bucket volatility)
  so the high-level controller operates consistently across blockchains.
• Decision Policy Serialization: Compile RL policy into platform-agnostic decision tree or lookup table;
  deploy on EVM-compatible chains without changing policy logic.

——— Phase 2: Protocol-Specific Integration ———
• DEX Integration: Wrap swaps with hyper-heuristic controller — Uniswap/Sushiswap (slippage, routing),
  Curve/Balancer (pool allocation); event logging for success/failure and gas.
• Lending/Borrowing Integration: Wrap with adaptive LTV and interest rate heuristics —
  Aave/Compound (collateral factor, liquidation thresholds); protocol-specific safety margins.
• Oracle Layer: Chainlink or custom feeds per platform; fallbacks for missing or delayed data.

——— Phase 3: Deployment & Testing ———
• Testnet Deployment: Deploy on each testnet (Ethereum→Goerli, Polygon→Mumbai, BSC→Testnet);
  validate gas per heuristic, decision correctness, logging and audit trail.
• Simulation with Historical Data: Replay historical tx per platform; verify success and gas gains;
  stress-test under simulated volatility.
• Security Audit: Formal verification of decision logic and heuristics; penetration testing;
  fallback heuristics if RL policy fails.

——— Phase 4: Cross-Platform Monitoring and Management ———
• Metric Collection: Off-chain dashboard — tx success rates, gas, heuristic utilization, risk exposure.
• Adaptive Policy Updates: Optional federated RL or meta-learning; verifiable off-chain updates
  with zkSNARK validation on-chain.
• Compliance & Explainability: Export explainability logs per platform (SHAP-like, heuristic metadata);
  regulatory audit trail (e.g. MiCA).

——— Phase 5: Continuous Improvement ———
• Policy Re-Training: Periodic retrain with updated data; recompile decision tree and redeploy.
• Heuristic Expansion: New rules for new protocols or conditions; backward compatibility with state vectors.
• Cross-Protocol Coordination: Optional arbitrage or liquidity-balancing across platforms;
  monitor cross-chain state for consistent rules.

——— Deliverables per platform ———
• Hyper-heuristic smart contract deployed on-chain
• Serialized RL decision policy (decision tree)
• Protocol-specific low-level heuristic library
• Logging and explainability modules
• Off-chain dashboard for metrics, monitoring, and optional federated updates
"""


def get_festival_aware_hyper_heuristic_summary() -> str:
    """Return the concise summary and integration checklist for the Festival-Aware Adaptive
    Hyper-Heuristic Smart Contract (six layers, integration steps, reward, deployment, benefits).
    Aligns with Festival_Aware_HyperHeuristic_DeFi_Integration.md §11."""
    return r"""
FESTIVAL-AWARE ADAPTIVE HYPER-HEURISTIC — CONCISE SUMMARY & INTEGRATION CHECKLIST

——— Layered Architecture (6 layers) ———
• Config Layer: Dynamic weights (α–ε), w_cultural_min, guardrails, festival flags.
  On-chain for thresholds; off-chain for RL tuning and federated updates.
• State Extraction: Gas, slippage, LTV, volatility, behavioral, cultural features;
  includes CulturalEvent_t and w_cultural(S_t, r_i).
• Feature Encoding: Normalize & embed all features; preserve numeric scale and categorical festivals.
• Harper-Henry Guardrails: Filter heuristics violating ethics/market rules or cultural thresholds.
  Hard constraint for r_i selection; logs for auditability.
• Policy Lookup (π): Hyper-heuristic controller selects r* from filtered candidates.
  RL reward modulated by guardrail compliance & cultural adherence.
• Execution + Metrics/Export: Execute on-chain; record financial, behavioral, cultural, system metrics.
  Export to CSV/JSON or zkSNARK-friendly proofs; supports federated meta-RL.

——— Integration Steps ———
1. Define Festival/Cultural Embeddings — map events/holidays to one-hot or embedding vectors; align with w_cultural(S_t, r_i).
2. Implement Guardrail Engine — pre-filter: slippage ≤ max_slippage, no negative externalities, w_cultural ≥ w_cultural_min; log for MiCA.
3. Policy Controller Adaptation — feed only filtered heuristics into π(S_t); RL: +ve for compliance, −ve for violations.
4. Execution Layer — apply r* on EVM; capture financial, behavioral, cultural metrics; structured logs.
5. Export Layer — CSV/JSON for dashboards; zkSNARK-friendly proofs; optional federated sharing for meta-RL.
6. Config Layer Dynamic Tuning — α–ε adjustable; w_cultural_min and festival flags for specialized biases.

——— Reward ———
R_t = α U_transaction + β U_gas + γ U_volatility + δ U_user + ε U_cultural
U_cultural: w_cultural_min, guardrail compliance, optional festival alignment. Dynamic ε for live cultural weighting.

——— Deployment ———
• On-chain: guardrail checks & r_i filtering (deterministic). Off-chain: RL retraining with verified signed updates.
• Gas: only filtered heuristics evaluated; precomputed festival/cultural embeddings.
• Auditability: every guardrail evaluation, selection, execution logged; export layer = structured, verifiable metrics.

——— Benefits ———
Determinism and gas efficiency; adaptive festival/cultural awareness; strong Harper-Henry guardrails;
rich metrics and explainable audit trails; multi-objective reward shaping via config layer.
"""


if __name__ == "__main__":
    asyncio.run(run_mexico_edition_demo())
