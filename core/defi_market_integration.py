#!/usr/bin/env python3
"""
🔥 DeFi Market Integration Engine
Diversification Across Markets: Traditional and DeFi market integration

Unifies traditional financial instruments (equities, fixed income, commodities)
with decentralized finance protocols (yield farming, liquidity pools, staking)
into a single diversified portfolio framework with unified risk management.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import math

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class MarketType(Enum):
    """High-level market category"""
    TRADITIONAL = "traditional"
    DEFI = "defi"


class TraditionalAssetClass(Enum):
    """Traditional financial asset classes"""
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    COMMODITY = "commodity"
    REAL_ESTATE = "real_estate"
    CASH_EQUIVALENT = "cash_equivalent"
    CURRENCY = "currency"


class DeFiProtocolType(Enum):
    """DeFi protocol categories"""
    YIELD_FARMING = "yield_farming"
    LIQUIDITY_POOL = "liquidity_pool"
    STAKING = "staking"
    LENDING = "lending"
    SYNTHETIC = "synthetic"
    CROSS_CHAIN_BRIDGE = "cross_chain_bridge"


class RiskTier(Enum):
    """Portfolio risk tiers"""
    CONSERVATIVE = "conservative"    # < 0.3 volatility
    MODERATE = "moderate"            # 0.3 – 0.6 volatility
    AGGRESSIVE = "aggressive"        # > 0.6 volatility


class RebalanceSignal(Enum):
    """Portfolio rebalancing signals"""
    HOLD = "hold"
    BUY_TRADITIONAL = "buy_traditional"
    BUY_DEFI = "buy_defi"
    REDUCE_TRADITIONAL = "reduce_traditional"
    REDUCE_DEFI = "reduce_defi"
    REBALANCE = "rebalance"


# ---------------------------------------------------------------------------
# Data classes – Traditional markets
# ---------------------------------------------------------------------------

@dataclass
class TraditionalAsset:
    """A single traditional market instrument"""
    symbol: str
    name: str
    asset_class: TraditionalAssetClass
    current_price: float
    quantity: float
    market_value: float
    expected_annual_return: float       # e.g. 0.08 = 8 %
    volatility: float                   # annualised standard deviation
    dividend_yield: float               # 0.0 if none
    liquidity_score: float              # 0.0 – 1.0 (1 = most liquid)
    beta: float                         # market beta
    correlation_to_market: float        # -1.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TraditionalMarketData:
    """Snapshot of traditional market conditions"""
    market_index: float                 # e.g. S&P 500 level
    market_trend: str                   # "bull", "bear", "sideways"
    vix: float                          # volatility index
    risk_free_rate: float               # e.g. 0.045 = 4.5 %
    inflation_rate: float
    fed_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Data classes – DeFi markets
# ---------------------------------------------------------------------------

@dataclass
class DeFiProtocol:
    """A DeFi protocol position"""
    protocol_id: str
    protocol_name: str
    protocol_type: DeFiProtocolType
    blockchain: str                     # e.g. "ethereum", "solana"
    token_symbol: str
    tvl_usd: float                      # total value locked
    current_apy: float                  # annualised yield (e.g. 0.12 = 12 %)
    position_value_usd: float           # current position value
    smart_contract_risk: float          # 0.0 – 1.0 (1 = highest risk)
    audit_score: float                  # 0.0 – 1.0 (1 = fully audited)
    liquidity_depth: float              # USD available for exit
    gas_cost_usd: float                 # estimated exit transaction cost
    impermanent_loss_risk: float        # 0.0 – 1.0 (relevant for LPs)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class DeFiMarketData:
    """Snapshot of DeFi market conditions"""
    total_defi_tvl: float               # aggregate TVL across all protocols
    average_defi_apy: float
    gas_price_gwei: float
    btc_dominance: float                # 0.0 – 1.0
    defi_fear_greed_index: float        # 0 (fear) – 100 (greed)
    cross_chain_bridge_volume: float    # 24 h USD volume
    timestamp: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------------------------
# Portfolio / result data classes
# ---------------------------------------------------------------------------

@dataclass
class PortfolioAllocation:
    """Target allocation between market types and asset classes"""
    traditional_weight: float           # 0.0 – 1.0
    defi_weight: float                  # 0.0 – 1.0

    # Traditional breakdown
    equity_weight: float = 0.0
    fixed_income_weight: float = 0.0
    commodity_weight: float = 0.0
    real_estate_weight: float = 0.0
    cash_equivalent_weight: float = 0.0

    # DeFi breakdown
    yield_farming_weight: float = 0.0
    liquidity_pool_weight: float = 0.0
    staking_weight: float = 0.0
    lending_weight: float = 0.0

    def validate(self) -> bool:
        """Check weights sum to approximately 1.0"""
        total = self.traditional_weight + self.defi_weight
        return abs(total - 1.0) < 1e-6


@dataclass
class RiskMetrics:
    """Unified risk metrics for the combined portfolio"""
    total_portfolio_value: float
    portfolio_volatility: float         # weighted annualised volatility
    sharpe_ratio: float
    max_drawdown_estimate: float        # 0.0 – 1.0 fraction
    var_95: float                       # Value at Risk (95 %, 1-day, USD)
    traditional_risk_contribution: float  # fraction of total risk from trad.
    defi_risk_contribution: float         # fraction of total risk from DeFi
    smart_contract_risk_score: float    # 0.0 – 1.0
    liquidity_risk_score: float         # 0.0 – 1.0
    correlation_trad_defi: float        # -1.0 to 1.0 (diversification benefit)
    risk_tier: RiskTier


@dataclass
class DiversificationScore:
    """Quantifies diversification across and within market types"""
    overall_score: float                # 0.0 – 1.0 (1 = fully diversified)
    cross_market_score: float           # trad vs. DeFi diversification
    within_traditional_score: float     # diversification within trad. assets
    within_defi_score: float            # diversification within DeFi positions
    asset_count: int
    effective_asset_count: float        # Herfindahl-based effective count
    market_type_count: int


@dataclass
class IntegratedPortfolioResult:
    """Complete result of a combined traditional + DeFi portfolio analysis"""
    portfolio_id: str
    timestamp: datetime
    traditional_assets: List[TraditionalAsset]
    defi_protocols: List[DeFiProtocol]
    current_allocation: PortfolioAllocation
    target_allocation: PortfolioAllocation
    risk_metrics: RiskMetrics
    diversification_score: DiversificationScore
    rebalance_signal: RebalanceSignal
    estimated_annual_yield: float       # blended yield across portfolio
    optimization_notes: List[str]
    next_review: datetime


# ---------------------------------------------------------------------------
# Core engine components
# ---------------------------------------------------------------------------

class TraditionalMarketAnalyzer:
    """Analyzes traditional market positions and risk"""

    def __init__(self):
        self._benchmark_return = 0.10    # 10 % long-run S&P 500

    def calculate_portfolio_metrics(
        self,
        assets: List[TraditionalAsset],
        market_data: TraditionalMarketData,
    ) -> Dict[str, float]:
        """Return weighted volatility, expected return, beta, and yield."""
        if not assets:
            return {"volatility": 0.0, "expected_return": 0.0, "beta": 0.0, "yield": 0.0, "total_value": 0.0}

        total_value = sum(a.market_value for a in assets)
        if total_value == 0:
            return {"volatility": 0.0, "expected_return": 0.0, "beta": 0.0, "yield": 0.0, "total_value": 0.0}

        weighted_vol = 0.0
        weighted_return = 0.0
        weighted_beta = 0.0
        weighted_yield = 0.0

        for asset in assets:
            w = asset.market_value / total_value
            weighted_vol += w * asset.volatility
            weighted_return += w * asset.expected_annual_return
            weighted_beta += w * asset.beta
            weighted_yield += w * asset.dividend_yield

        return {
            "volatility": weighted_vol,
            "expected_return": weighted_return,
            "beta": weighted_beta,
            "yield": weighted_yield,
            "total_value": total_value,
        }

    def assess_liquidity(self, assets: List[TraditionalAsset]) -> float:
        """Return portfolio-weighted average liquidity score (0-1)."""
        if not assets:
            return 1.0
        total_value = sum(a.market_value for a in assets)
        if total_value == 0:
            return 1.0
        return sum((a.market_value / total_value) * a.liquidity_score for a in assets)


class DeFiProtocolAnalyzer:
    """Analyzes DeFi protocol positions and risk"""

    def calculate_portfolio_metrics(
        self,
        protocols: List[DeFiProtocol],
        market_data: DeFiMarketData,
    ) -> Dict[str, float]:
        """Return total value, weighted APY, and weighted risk scores."""
        if not protocols:
            return {
                "total_value": 0.0,
                "weighted_apy": 0.0,
                "smart_contract_risk": 0.0,
                "liquidity_risk": 0.0,
                "impermanent_loss_risk": 0.0,
            }

        total_value = sum(p.position_value_usd for p in protocols)
        if total_value == 0:
            return {
                "total_value": 0.0,
                "weighted_apy": 0.0,
                "smart_contract_risk": 0.0,
                "liquidity_risk": 0.0,
                "impermanent_loss_risk": 0.0,
            }

        weighted_apy = 0.0
        sc_risk = 0.0
        liq_risk = 0.0
        il_risk = 0.0

        for p in protocols:
            w = p.position_value_usd / total_value
            weighted_apy += w * p.current_apy
            sc_risk += w * p.smart_contract_risk
            liq_risk += w * (1.0 - min(p.liquidity_depth / max(p.position_value_usd, 1.0), 1.0))
            il_risk += w * p.impermanent_loss_risk

        return {
            "total_value": total_value,
            "weighted_apy": weighted_apy,
            "smart_contract_risk": sc_risk,
            "liquidity_risk": liq_risk,
            "impermanent_loss_risk": il_risk,
        }

    def estimate_effective_yield(
        self,
        protocols: List[DeFiProtocol],
        gas_budget_usd: float = 50.0,
    ) -> float:
        """Return APY after adjusting for gas costs relative to position size."""
        if not protocols:
            return 0.0
        total_value = sum(p.position_value_usd for p in protocols)
        if total_value == 0:
            return 0.0
        gross_yield_usd = sum(p.position_value_usd * p.current_apy for p in protocols)
        total_gas = sum(p.gas_cost_usd for p in protocols)
        net_yield_usd = max(gross_yield_usd - total_gas, 0.0)
        return net_yield_usd / total_value


class DiversificationCalculator:
    """Computes diversification metrics for the combined portfolio"""

    def calculate(
        self,
        traditional_assets: List[TraditionalAsset],
        defi_protocols: List[DeFiProtocol],
    ) -> DiversificationScore:
        """Compute overall and component diversification scores."""
        trad_value = sum(a.market_value for a in traditional_assets)
        defi_value = sum(p.position_value_usd for p in defi_protocols)
        total_value = trad_value + defi_value
        asset_count = len(traditional_assets) + len(defi_protocols)

        if total_value == 0 or asset_count == 0:
            return DiversificationScore(
                overall_score=0.0,
                cross_market_score=0.0,
                within_traditional_score=0.0,
                within_defi_score=0.0,
                asset_count=0,
                effective_asset_count=0.0,
                market_type_count=0,
            )

        # Cross-market diversification: how close to 50/50?
        trad_w = trad_value / total_value
        defi_w = defi_value / total_value
        cross_market_score = 1.0 - abs(trad_w - defi_w)

        # Within-traditional: Herfindahl index across asset classes
        within_trad = self._herfindahl_score(
            [a.market_value for a in traditional_assets]
        ) if traditional_assets else 0.0

        # Within-DeFi: Herfindahl across protocol types
        within_defi = self._herfindahl_score(
            [p.position_value_usd for p in defi_protocols]
        ) if defi_protocols else 0.0

        # Effective asset count (1 / sum of squared weights)
        all_values = [a.market_value for a in traditional_assets] + \
                     [p.position_value_usd for p in defi_protocols]
        effective_count = self._effective_count(all_values)

        # Market types present
        market_types = 0
        if trad_value > 0:
            market_types += 1
        if defi_value > 0:
            market_types += 1

        overall = (cross_market_score + within_trad + within_defi) / 3.0

        return DiversificationScore(
            overall_score=round(overall, 4),
            cross_market_score=round(cross_market_score, 4),
            within_traditional_score=round(within_trad, 4),
            within_defi_score=round(within_defi, 4),
            asset_count=asset_count,
            effective_asset_count=round(effective_count, 2),
            market_type_count=market_types,
        )

    @staticmethod
    def _herfindahl_score(values: List[float]) -> float:
        """Return 1 – HHI so that higher = more diversified."""
        total = sum(values)
        if total == 0 or not values:
            return 0.0
        hhi = sum((v / total) ** 2 for v in values)
        # Normalize: perfect diversity (N assets) → HHI = 1/N
        n = len(values)
        min_hhi = 1.0 / n if n > 0 else 1.0
        score = 1.0 - (hhi - min_hhi) / (1.0 - min_hhi) if n > 1 else 0.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def _effective_count(values: List[float]) -> float:
        """Return effective number of assets (1 / HHI)."""
        total = sum(values)
        if total == 0:
            return 0.0
        hhi = sum((v / total) ** 2 for v in values)
        return 1.0 / hhi if hhi > 0 else 0.0


class RiskCalculator:
    """Calculates unified risk metrics for the combined portfolio"""

    def calculate(
        self,
        trad_metrics: Dict[str, float],
        defi_metrics: Dict[str, float],
        market_data: TraditionalMarketData,
    ) -> RiskMetrics:
        total_value = trad_metrics["total_value"] + defi_metrics["total_value"]
        if total_value == 0:
            return self._zero_metrics()

        trad_w = trad_metrics["total_value"] / total_value
        defi_w = defi_metrics["total_value"] / total_value

        # DeFi positions carry higher volatility; proxy ~0.6 annualised
        defi_vol = 0.60
        trad_vol = trad_metrics.get("volatility", 0.15)

        # Approximate correlation (trad & DeFi are partially correlated)
        corr_trad_defi = 0.35

        # Two-asset portfolio variance
        port_var = (
            (trad_w ** 2) * (trad_vol ** 2)
            + (defi_w ** 2) * (defi_vol ** 2)
            + 2 * trad_w * defi_w * corr_trad_defi * trad_vol * defi_vol
        )
        port_vol = math.sqrt(max(port_var, 0.0))

        # Risk contributions (marginal variance approach)
        trad_rc = ((trad_w ** 2) * (trad_vol ** 2)) / max(port_var, 1e-10)
        defi_rc = ((defi_w ** 2) * (defi_vol ** 2)) / max(port_var, 1e-10)

        # Blended expected return
        trad_ret = trad_metrics.get("expected_return", 0.08)
        defi_ret = defi_metrics.get("weighted_apy", 0.10)
        port_return = trad_w * trad_ret + defi_w * defi_ret

        rf = market_data.risk_free_rate
        sharpe = (port_return - rf) / port_vol if port_vol > 0 else 0.0

        # Simplified 95 % 1-day VaR (normal distribution)
        daily_vol = port_vol / math.sqrt(252)
        var_95 = total_value * 1.645 * daily_vol

        # Max drawdown estimate (simplistic rule of thumb)
        max_dd = min(port_vol * 2.0, 1.0)

        # Smart contract risk (only from DeFi portion)
        sc_risk = defi_metrics.get("smart_contract_risk", 0.0) * defi_w
        liq_risk = (
            trad_metrics.get("liquidity_risk", 0.0) * trad_w
            + defi_metrics.get("liquidity_risk", 0.0) * defi_w
        )

        if port_vol < 0.30:
            tier = RiskTier.CONSERVATIVE
        elif port_vol < 0.60:
            tier = RiskTier.MODERATE
        else:
            tier = RiskTier.AGGRESSIVE

        return RiskMetrics(
            total_portfolio_value=round(total_value, 2),
            portfolio_volatility=round(port_vol, 4),
            sharpe_ratio=round(sharpe, 4),
            max_drawdown_estimate=round(max_dd, 4),
            var_95=round(var_95, 2),
            traditional_risk_contribution=round(trad_rc, 4),
            defi_risk_contribution=round(defi_rc, 4),
            smart_contract_risk_score=round(sc_risk, 4),
            liquidity_risk_score=round(liq_risk, 4),
            correlation_trad_defi=corr_trad_defi,
            risk_tier=tier,
        )

    @staticmethod
    def _zero_metrics() -> RiskMetrics:
        return RiskMetrics(
            total_portfolio_value=0.0,
            portfolio_volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown_estimate=0.0,
            var_95=0.0,
            traditional_risk_contribution=0.0,
            defi_risk_contribution=0.0,
            smart_contract_risk_score=0.0,
            liquidity_risk_score=0.0,
            correlation_trad_defi=0.0,
            risk_tier=RiskTier.CONSERVATIVE,
        )


class AllocationOptimizer:
    """Recommends target allocations and rebalance signals"""

    # Target ranges (traditional weight) per risk tier
    _TRAD_RANGES = {
        RiskTier.CONSERVATIVE: (0.70, 0.90),
        RiskTier.MODERATE: (0.50, 0.70),
        RiskTier.AGGRESSIVE: (0.30, 0.55),
    }

    def recommend_allocation(
        self,
        risk_tier: RiskTier,
        current: PortfolioAllocation,
        trad_metrics: Dict[str, float],
        defi_metrics: Dict[str, float],
    ) -> Tuple[PortfolioAllocation, RebalanceSignal]:
        """Return (target_allocation, rebalance_signal)."""
        low, high = self._TRAD_RANGES[risk_tier]
        target_trad = (low + high) / 2.0
        target_defi = 1.0 - target_trad

        # Sub-allocations within traditional
        trad_alloc = self._split_traditional(target_trad, risk_tier)
        defi_alloc = self._split_defi(target_defi, risk_tier)

        target = PortfolioAllocation(
            traditional_weight=round(target_trad, 4),
            defi_weight=round(target_defi, 4),
            **trad_alloc,
            **defi_alloc,
        )

        # Determine rebalance signal
        drift = current.traditional_weight - target_trad
        threshold = 0.05  # 5 % drift triggers rebalance
        if abs(drift) < threshold:
            signal = RebalanceSignal.HOLD
        elif drift > threshold:
            signal = RebalanceSignal.REDUCE_TRADITIONAL
        else:
            signal = RebalanceSignal.REDUCE_DEFI

        return target, signal

    @staticmethod
    def _split_traditional(total_trad: float, risk_tier: RiskTier) -> Dict[str, float]:
        if risk_tier == RiskTier.CONSERVATIVE:
            return {
                "equity_weight": round(total_trad * 0.40, 4),
                "fixed_income_weight": round(total_trad * 0.40, 4),
                "commodity_weight": round(total_trad * 0.10, 4),
                "real_estate_weight": round(total_trad * 0.05, 4),
                "cash_equivalent_weight": round(total_trad * 0.05, 4),
            }
        elif risk_tier == RiskTier.MODERATE:
            return {
                "equity_weight": round(total_trad * 0.60, 4),
                "fixed_income_weight": round(total_trad * 0.25, 4),
                "commodity_weight": round(total_trad * 0.10, 4),
                "real_estate_weight": round(total_trad * 0.05, 4),
                "cash_equivalent_weight": 0.0,
            }
        else:  # AGGRESSIVE
            return {
                "equity_weight": round(total_trad * 0.80, 4),
                "fixed_income_weight": round(total_trad * 0.10, 4),
                "commodity_weight": round(total_trad * 0.10, 4),
                "real_estate_weight": 0.0,
                "cash_equivalent_weight": 0.0,
            }

    @staticmethod
    def _split_defi(total_defi: float, risk_tier: RiskTier) -> Dict[str, float]:
        if risk_tier == RiskTier.CONSERVATIVE:
            return {
                "staking_weight": round(total_defi * 0.60, 4),
                "lending_weight": round(total_defi * 0.30, 4),
                "liquidity_pool_weight": round(total_defi * 0.10, 4),
                "yield_farming_weight": 0.0,
            }
        elif risk_tier == RiskTier.MODERATE:
            return {
                "staking_weight": round(total_defi * 0.35, 4),
                "lending_weight": round(total_defi * 0.25, 4),
                "liquidity_pool_weight": round(total_defi * 0.25, 4),
                "yield_farming_weight": round(total_defi * 0.15, 4),
            }
        else:  # AGGRESSIVE
            return {
                "staking_weight": round(total_defi * 0.20, 4),
                "lending_weight": round(total_defi * 0.20, 4),
                "liquidity_pool_weight": round(total_defi * 0.30, 4),
                "yield_farming_weight": round(total_defi * 0.30, 4),
            }


# ---------------------------------------------------------------------------
# Main integration engine
# ---------------------------------------------------------------------------

class DeFiMarketIntegrationEngine:
    """
    Core engine for Traditional + DeFi market integration and diversification.

    Workflow:
        1. Ingest traditional and DeFi positions.
        2. Compute per-segment metrics.
        3. Calculate unified risk and diversification scores.
        4. Recommend target allocation and rebalance signals.
        5. Return a consolidated IntegratedPortfolioResult.
    """

    def __init__(self):
        self._trad_analyzer = TraditionalMarketAnalyzer()
        self._defi_analyzer = DeFiProtocolAnalyzer()
        self._diversification_calc = DiversificationCalculator()
        self._risk_calc = RiskCalculator()
        self._allocator = AllocationOptimizer()
        self._portfolio_history: List[IntegratedPortfolioResult] = []

    async def analyze_portfolio(
        self,
        traditional_assets: List[TraditionalAsset],
        defi_protocols: List[DeFiProtocol],
        trad_market_data: TraditionalMarketData,
        defi_market_data: DeFiMarketData,
        preferred_risk_tier: Optional[RiskTier] = None,
    ) -> IntegratedPortfolioResult:
        """
        Full portfolio analysis combining traditional and DeFi positions.

        Args:
            traditional_assets: List of TraditionalAsset positions.
            defi_protocols: List of DeFiProtocol positions.
            trad_market_data: Current traditional market snapshot.
            defi_market_data: Current DeFi market snapshot.
            preferred_risk_tier: If None, tier is inferred from portfolio.

        Returns:
            IntegratedPortfolioResult with allocation, risk, and signals.
        """
        start = time.time()

        # 1 – Segment metrics
        trad_metrics = self._trad_analyzer.calculate_portfolio_metrics(
            traditional_assets, trad_market_data
        )
        defi_metrics = self._defi_analyzer.calculate_portfolio_metrics(
            defi_protocols, defi_market_data
        )

        # 2 – Unified risk
        risk = self._risk_calc.calculate(trad_metrics, defi_metrics, trad_market_data)
        tier = preferred_risk_tier or risk.risk_tier

        # 3 – Diversification
        diversity = self._diversification_calc.calculate(traditional_assets, defi_protocols)

        # 4 – Current allocation
        total = trad_metrics["total_value"] + defi_metrics["total_value"]
        trad_w = trad_metrics["total_value"] / total if total > 0 else 0.0
        defi_w = defi_metrics["total_value"] / total if total > 0 else 0.0
        current_alloc = PortfolioAllocation(
            traditional_weight=round(trad_w, 4),
            defi_weight=round(defi_w, 4),
        )

        # 5 – Target allocation and rebalance signal
        target_alloc, rebalance_signal = self._allocator.recommend_allocation(
            tier, current_alloc, trad_metrics, defi_metrics
        )

        # 6 – Blended annual yield
        effective_defi_yield = self._defi_analyzer.estimate_effective_yield(defi_protocols)
        trad_yield = trad_metrics.get("yield", 0.0) + trad_metrics.get("expected_return", 0.0)
        blended_yield = trad_w * trad_yield + defi_w * effective_defi_yield

        # 7 – Optimisation notes
        notes = self._generate_notes(
            current_alloc, target_alloc, risk, diversity, trad_metrics, defi_metrics
        )

        portfolio_id = f"portfolio_{int(time.time() * 1000)}"
        result = IntegratedPortfolioResult(
            portfolio_id=portfolio_id,
            timestamp=datetime.now(),
            traditional_assets=traditional_assets,
            defi_protocols=defi_protocols,
            current_allocation=current_alloc,
            target_allocation=target_alloc,
            risk_metrics=risk,
            diversification_score=diversity,
            rebalance_signal=rebalance_signal,
            estimated_annual_yield=round(blended_yield, 4),
            optimization_notes=notes,
            next_review=datetime.now() + timedelta(days=7),
        )

        self._portfolio_history.append(result)
        elapsed = round((time.time() - start) * 1000, 1)
        logger.info(
            "Portfolio analysis complete [%s] in %s ms — value=$%.0f, "
            "yield=%.2f%%, risk=%s, rebalance=%s",
            portfolio_id, elapsed, total,
            blended_yield * 100, tier.value, rebalance_signal.value,
        )
        return result

    # ------------------------------------------------------------------
    # Portfolio history
    # ------------------------------------------------------------------

    def get_history(self, limit: int = 10) -> List[IntegratedPortfolioResult]:
        """Return the most recent portfolio analyses."""
        return self._portfolio_history[-limit:]

    def get_latest(self) -> Optional[IntegratedPortfolioResult]:
        """Return the most recent analysis, or None."""
        return self._portfolio_history[-1] if self._portfolio_history else None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_notes(
        current: PortfolioAllocation,
        target: PortfolioAllocation,
        risk: RiskMetrics,
        diversity: DiversificationScore,
        trad_metrics: Dict[str, float],
        defi_metrics: Dict[str, float],
    ) -> List[str]:
        notes: List[str] = []

        drift = abs(current.traditional_weight - target.traditional_weight)
        if drift > 0.05:
            notes.append(
                f"Traditional allocation drifted {drift * 100:.1f}% from target "
                f"({target.traditional_weight * 100:.0f}%); rebalance recommended."
            )

        if risk.smart_contract_risk_score > 0.40:
            notes.append(
                "Smart-contract risk score is elevated "
                f"({risk.smart_contract_risk_score:.2f}); consider rotating into "
                "audited protocols or reducing DeFi exposure."
            )

        if diversity.overall_score < 0.50:
            notes.append(
                f"Portfolio diversification is below target "
                f"({diversity.overall_score:.2f}); broaden asset coverage across "
                "both traditional and DeFi segments."
            )

        if risk.sharpe_ratio < 0.50 and risk.total_portfolio_value > 0:
            notes.append(
                f"Sharpe ratio ({risk.sharpe_ratio:.2f}) is below 0.5; review "
                "underperforming positions and reduce high-cost DeFi gas drag."
            )

        apy = defi_metrics.get("weighted_apy", 0.0)
        if apy > 0.30:
            notes.append(
                f"DeFi weighted APY of {apy * 100:.1f}% may include unsustainable "
                "emission rewards; verify protocol token economics."
            )

        if not notes:
            notes.append("Portfolio is well-positioned; no immediate action required.")

        return notes


# ---------------------------------------------------------------------------
# Sample data factory (used in demos and tests)
# ---------------------------------------------------------------------------

def build_sample_traditional_assets() -> List[TraditionalAsset]:
    return [
        TraditionalAsset(
            symbol="SPY", name="SPDR S&P 500 ETF",
            asset_class=TraditionalAssetClass.EQUITY,
            current_price=450.00, quantity=100.0, market_value=45_000.0,
            expected_annual_return=0.10, volatility=0.16, dividend_yield=0.015,
            liquidity_score=0.99, beta=1.0, correlation_to_market=0.99,
        ),
        TraditionalAsset(
            symbol="AGG", name="iShares Core US Aggregate Bond ETF",
            asset_class=TraditionalAssetClass.FIXED_INCOME,
            current_price=95.00, quantity=200.0, market_value=19_000.0,
            expected_annual_return=0.04, volatility=0.05, dividend_yield=0.038,
            liquidity_score=0.95, beta=0.10, correlation_to_market=0.05,
        ),
        TraditionalAsset(
            symbol="GLD", name="SPDR Gold Trust",
            asset_class=TraditionalAssetClass.COMMODITY,
            current_price=185.00, quantity=50.0, market_value=9_250.0,
            expected_annual_return=0.06, volatility=0.14, dividend_yield=0.0,
            liquidity_score=0.90, beta=0.05, correlation_to_market=-0.10,
        ),
    ]


def build_sample_defi_protocols() -> List[DeFiProtocol]:
    return [
        DeFiProtocol(
            protocol_id="aave_v3_usdc", protocol_name="Aave v3 USDC",
            protocol_type=DeFiProtocolType.LENDING,
            blockchain="ethereum", token_symbol="aUSDC",
            tvl_usd=5_000_000_000.0, current_apy=0.052,
            position_value_usd=10_000.0,
            smart_contract_risk=0.12, audit_score=0.92,
            liquidity_depth=500_000_000.0, gas_cost_usd=15.0,
            impermanent_loss_risk=0.0,
        ),
        DeFiProtocol(
            protocol_id="uniswap_v3_eth_usdc", protocol_name="Uniswap v3 ETH/USDC LP",
            protocol_type=DeFiProtocolType.LIQUIDITY_POOL,
            blockchain="ethereum", token_symbol="UNI-V3-LP",
            tvl_usd=800_000_000.0, current_apy=0.18,
            position_value_usd=8_000.0,
            smart_contract_risk=0.20, audit_score=0.85,
            liquidity_depth=50_000_000.0, gas_cost_usd=25.0,
            impermanent_loss_risk=0.35,
        ),
        DeFiProtocol(
            protocol_id="lido_eth_staking", protocol_name="Lido ETH Staking",
            protocol_type=DeFiProtocolType.STAKING,
            blockchain="ethereum", token_symbol="stETH",
            tvl_usd=20_000_000_000.0, current_apy=0.042,
            position_value_usd=15_000.0,
            smart_contract_risk=0.15, audit_score=0.90,
            liquidity_depth=1_000_000_000.0, gas_cost_usd=10.0,
            impermanent_loss_risk=0.0,
        ),
    ]


def build_sample_market_data() -> Tuple[TraditionalMarketData, DeFiMarketData]:
    trad = TraditionalMarketData(
        market_index=4_500.0, market_trend="bull",
        vix=18.5, risk_free_rate=0.045,
        inflation_rate=0.032, fed_rate=0.055,
    )
    defi = DeFiMarketData(
        total_defi_tvl=85_000_000_000.0,
        average_defi_apy=0.085,
        gas_price_gwei=25.0,
        btc_dominance=0.48,
        defi_fear_greed_index=62.0,
        cross_chain_bridge_volume=500_000_000.0,
    )
    return trad, defi


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

async def main():
    print("🔥 DeFi Market Integration Engine Demo")
    print("=" * 55)

    engine = DeFiMarketIntegrationEngine()

    trad_assets = build_sample_traditional_assets()
    defi_protocols = build_sample_defi_protocols()
    trad_data, defi_data = build_sample_market_data()

    result = await engine.analyze_portfolio(
        trad_assets, defi_protocols, trad_data, defi_data
    )

    print(f"\n📊 Portfolio ID : {result.portfolio_id}")
    print(f"💰 Total Value  : ${result.risk_metrics.total_portfolio_value:,.2f}")
    print(f"📈 Annual Yield : {result.estimated_annual_yield * 100:.2f}%")
    print(f"⚡ Sharpe Ratio : {result.risk_metrics.sharpe_ratio:.3f}")
    print(f"🎯 Risk Tier    : {result.risk_metrics.risk_tier.value}")
    print(f"🔀 Rebalance    : {result.rebalance_signal.value}")

    print(f"\n📐 Allocation (current → target):")
    print(f"   Traditional : {result.current_allocation.traditional_weight * 100:.1f}% "
          f"→ {result.target_allocation.traditional_weight * 100:.1f}%")
    print(f"   DeFi        : {result.current_allocation.defi_weight * 100:.1f}% "
          f"→ {result.target_allocation.defi_weight * 100:.1f}%")

    print(f"\n🌐 Diversification : {result.diversification_score.overall_score:.3f} "
          f"(effective assets: {result.diversification_score.effective_asset_count:.1f})")

    print(f"\n📝 Optimisation Notes:")
    for note in result.optimization_notes:
        print(f"   • {note}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
