#!/usr/bin/env python3
"""
🤖 AI-DRIVEN INVESTMENT STRATEGY ENGINE
Automated Investment Strategies: AI-driven portfolio optimization and execution

"Where machine intelligence meets financial precision to create optimal outcomes"
"""

import asyncio
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ── Enumerations ─────────────────────────────────────────────────────────────

class InvestmentStrategy(Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    FACTOR_INVESTING = "factor_investing"
    PAIRS_TRADING = "pairs_trading"
    TREND_FOLLOWING = "trend_following"
    VOLATILITY_ARBITRAGE = "volatility_arbitrage"
    CARRY_TRADE = "carry_trade"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"


class PortfolioOptimizationMethod(Enum):
    MEAN_VARIANCE = "mean_variance"          # Markowitz Mean-Variance
    BLACK_LITTERMAN = "black_litterman"      # Black-Litterman with views
    RISK_PARITY = "risk_parity"             # Equal Risk Contribution
    KELLY_CRITERION = "kelly_criterion"      # Full / fractional Kelly
    MINIMUM_VARIANCE = "minimum_variance"    # Min-variance frontier
    MAXIMUM_SHARPE = "maximum_sharpe"        # Tangency portfolio


class ExecutionAlgorithm(Enum):
    MARKET = "market"
    LIMIT = "limit"
    TWAP = "twap"       # Time-Weighted Average Price
    VWAP = "vwap"       # Volume-Weighted Average Price
    IS = "is"           # Implementation Shortfall
    ADAPTIVE = "adaptive"


class RebalanceTrigger(Enum):
    CALENDAR = "calendar"       # Time-based (e.g. monthly)
    THRESHOLD = "threshold"     # Drift > N%
    SIGNAL = "signal"           # Strategy signal triggered
    RISK = "risk"               # Risk limit breach


# ── Core Data Structures ─────────────────────────────────────────────────────

@dataclass
class AssetAllocation:
    symbol: str
    target_weight: float        # 0.0 – 1.0
    current_weight: float
    expected_return: float      # annualised
    volatility: float           # annualised
    beta: float
    liquidity_score: float      # 0.0 – 1.0


@dataclass
class OptimizationConstraints:
    min_weight: float = 0.0
    max_weight: float = 1.0
    max_concentration: float = 0.40     # single-asset cap
    max_sector_concentration: float = 0.60
    target_volatility: Optional[float] = None   # annualised vol target
    min_return: Optional[float] = None          # floor on expected return
    max_turnover: float = 1.0                   # fraction of portfolio
    long_only: bool = True
    leverage_limit: float = 1.0                 # 1.0 = no leverage


@dataclass
class StrategySignal:
    symbol: str
    strategy: InvestmentStrategy
    direction: str              # "long", "short", "neutral"
    confidence: float           # 0.0 – 1.0
    expected_return: float
    time_horizon_days: int
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    method: PortfolioOptimizationMethod
    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_estimate: float
    diversification_ratio: float
    convergence_iterations: int
    optimization_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionPlan:
    id: str
    symbol: str
    target_quantity: float
    algorithm: ExecutionAlgorithm
    slices: List[Dict[str, Any]]
    estimated_market_impact_bps: float  # basis points
    estimated_completion_time: datetime
    risk_limits: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BacktestResult:
    strategy: InvestmentStrategy
    start_date: datetime
    end_date: datetime
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_return: float
    equity_curve: List[float]
    drawdown_series: List[float]


@dataclass
class PortfolioRebalanceOrder:
    symbol: str
    action: str                 # "buy", "sell", "hold"
    current_weight: float
    target_weight: float
    drift: float
    estimated_value: float
    execution_algorithm: ExecutionAlgorithm
    priority: int               # 1 = highest


# ── Financial Math Utilities ─────────────────────────────────────────────────

class FinancialMath:
    """Pure financial mathematics — no external dependencies beyond numpy."""

    @staticmethod
    def covariance_matrix(returns: np.ndarray) -> np.ndarray:
        """Annualised covariance matrix from daily returns (T × N array)."""
        return np.cov(returns.T) * 252

    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free: float = 0.04) -> float:
        if returns.std() == 0:
            return 0.0
        excess = returns.mean() * 252 - risk_free
        return excess / (returns.std() * math.sqrt(252))

    @staticmethod
    def sortino_ratio(returns: np.ndarray, risk_free: float = 0.04,
                      mar: float = 0.0) -> float:
        """Sortino ratio using downside deviation below MAR."""
        downside = returns[returns < mar]
        if len(downside) == 0 or downside.std() == 0:
            return 0.0
        downside_dev = math.sqrt(np.mean(downside ** 2)) * math.sqrt(252)
        return (returns.mean() * 252 - risk_free) / downside_dev

    @staticmethod
    def max_drawdown(equity_curve: np.ndarray) -> float:
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / np.where(peak == 0, 1, peak)
        return float(drawdown.min())

    @staticmethod
    def calmar_ratio(annualized_return: float, max_dd: float) -> float:
        if max_dd == 0:
            return 0.0
        return annualized_return / abs(max_dd)

    @staticmethod
    def information_ratio(portfolio_returns: np.ndarray,
                          benchmark_returns: np.ndarray) -> float:
        active = portfolio_returns - benchmark_returns
        if active.std() == 0:
            return 0.0
        return (active.mean() * 252) / (active.std() * math.sqrt(252))

    @staticmethod
    def kelly_fraction(win_rate: float, avg_win: float, avg_loss: float,
                       fraction: float = 0.5) -> float:
        """Full Kelly times `fraction` (default half-Kelly for safety)."""
        if avg_loss == 0:
            return 0.0
        b = avg_win / avg_loss
        if b == 0:
            return 0.0
        kelly = (b * win_rate - (1 - win_rate)) / b
        return max(0.0, kelly * fraction)

    @staticmethod
    def portfolio_variance(weights: np.ndarray, cov: np.ndarray) -> float:
        return float(weights @ cov @ weights)

    @staticmethod
    def diversification_ratio(weights: np.ndarray, vols: np.ndarray,
                               cov: np.ndarray) -> float:
        weighted_avg_vol = float(weights @ vols)
        port_vol = math.sqrt(FinancialMath.portfolio_variance(weights, cov))
        return weighted_avg_vol / port_vol if port_vol > 0 else 1.0


# ── Portfolio Optimizers ──────────────────────────────────────────────────────

class AIPortfolioOptimizer:
    """
    AI-driven portfolio optimizer supporting multiple optimisation methods.

    All methods operate on annualised inputs and return normalised weights.
    Optimisation is done analytically or via projected-gradient descent so
    no external solver is required.
    """

    def __init__(self, risk_free_rate: float = 0.04):
        self.risk_free_rate = risk_free_rate
        self._math = FinancialMath()

    # ── Public API ──────────────────────────────────────────────────────────

    async def optimize(
        self,
        symbols: List[str],
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        method: PortfolioOptimizationMethod = PortfolioOptimizationMethod.MAXIMUM_SHARPE,
        constraints: Optional[OptimizationConstraints] = None,
        views: Optional[Dict[str, float]] = None,        # Black-Litterman
        view_confidences: Optional[np.ndarray] = None,
    ) -> OptimizationResult:
        start = time.perf_counter()
        constraints = constraints or OptimizationConstraints()
        n = len(symbols)

        if method == PortfolioOptimizationMethod.MEAN_VARIANCE:
            weights, iters = self._mean_variance(expected_returns, covariance_matrix, constraints)
        elif method == PortfolioOptimizationMethod.BLACK_LITTERMAN:
            bl_returns = self._black_litterman(
                symbols, expected_returns, covariance_matrix,
                views or {}, view_confidences
            )
            weights, iters = self._mean_variance(bl_returns, covariance_matrix, constraints)
        elif method == PortfolioOptimizationMethod.RISK_PARITY:
            weights, iters = self._risk_parity(covariance_matrix, constraints)
        elif method == PortfolioOptimizationMethod.KELLY_CRITERION:
            weights, iters = self._kelly_portfolio(expected_returns, covariance_matrix, constraints)
        elif method == PortfolioOptimizationMethod.MINIMUM_VARIANCE:
            weights, iters = self._minimum_variance(covariance_matrix, constraints)
        else:  # MAXIMUM_SHARPE (default)
            weights, iters = self._maximum_sharpe(expected_returns, covariance_matrix, constraints)

        port_return = float(weights @ expected_returns)
        port_variance = self._math.portfolio_variance(weights, covariance_matrix)
        port_vol = math.sqrt(max(port_variance, 0.0))
        sharpe = (port_return - self.risk_free_rate) / port_vol if port_vol > 0 else 0.0

        # Approximate sortino using vol * 0.7 as downside vol heuristic
        downside_vol = port_vol * 0.70
        sortino = (port_return - self.risk_free_rate) / downside_vol if downside_vol > 0 else 0.0

        vols = np.sqrt(np.diag(covariance_matrix))
        div_ratio = self._math.diversification_ratio(weights, vols, covariance_matrix)

        elapsed_ms = (time.perf_counter() - start) * 1000

        return OptimizationResult(
            method=method,
            weights={sym: float(w) for sym, w in zip(symbols, weights)},
            expected_return=port_return,
            expected_volatility=port_vol,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown_estimate=-port_vol * 2.5,  # rough rule-of-thumb
            diversification_ratio=div_ratio,
            convergence_iterations=iters,
            optimization_time_ms=elapsed_ms,
        )

    # ── Optimisation Methods ────────────────────────────────────────────────

    def _maximum_sharpe(
        self, mu: np.ndarray, cov: np.ndarray, c: OptimizationConstraints
    ) -> Tuple[np.ndarray, int]:
        """Tangency portfolio via projected-gradient ascent on Sharpe."""
        n = len(mu)
        w = np.ones(n) / n
        lr, iters, tol = 1e-3, 500, 1e-8

        for i in range(iters):
            port_vol = math.sqrt(max(float(w @ cov @ w), 1e-12))
            excess = float(w @ mu) - self.risk_free_rate
            grad_ret = mu
            grad_vol = (cov @ w) / port_vol
            grad = (grad_ret * port_vol - excess * grad_vol) / (port_vol ** 2)

            w_new = w + lr * grad
            w_new = self._project_constraints(w_new, c)

            if np.linalg.norm(w_new - w) < tol:
                return w_new, i + 1
            w = w_new

        return w, iters

    def _mean_variance(
        self, mu: np.ndarray, cov: np.ndarray, c: OptimizationConstraints
    ) -> Tuple[np.ndarray, int]:
        """Mean-variance: maximise μᵀw − λ·wᵀΣw, λ chosen from target vol."""
        n = len(mu)
        w = np.ones(n) / n
        # risk-aversion parameter from target vol (default ~15% annual)
        target_vol = c.target_volatility or 0.15
        lam = 1.0 / (2 * target_vol ** 2)
        lr, iters, tol = 5e-4, 1000, 1e-9

        for i in range(iters):
            grad = mu - 2 * lam * (cov @ w)
            w_new = w + lr * grad
            w_new = self._project_constraints(w_new, c)

            if np.linalg.norm(w_new - w) < tol:
                return w_new, i + 1
            w = w_new

        return w, iters

    def _risk_parity(
        self, cov: np.ndarray, c: OptimizationConstraints
    ) -> Tuple[np.ndarray, int]:
        """Equal Risk Contribution via gradient descent on concentration penalty."""
        n = cov.shape[0]
        w = np.ones(n) / n
        lr, iters, tol = 1e-3, 2000, 1e-10

        for i in range(iters):
            port_var = float(w @ cov @ w)
            mrc = (cov @ w) / math.sqrt(max(port_var, 1e-12))  # marginal risk contribution
            rc = w * mrc                                         # risk contribution
            target_rc = np.full(n, port_var / n / math.sqrt(max(port_var, 1e-12)))
            grad = 2 * (rc - target_rc) * mrc

            w_new = w - lr * grad
            w_new = self._project_constraints(w_new, c)

            if np.linalg.norm(w_new - w) < tol:
                return w_new, i + 1
            w = w_new

        return w, iters

    def _minimum_variance(
        self, cov: np.ndarray, c: OptimizationConstraints
    ) -> Tuple[np.ndarray, int]:
        """Minimise portfolio variance via gradient descent."""
        n = cov.shape[0]
        w = np.ones(n) / n
        lr, iters, tol = 5e-4, 1000, 1e-10

        for i in range(iters):
            grad = 2 * (cov @ w)
            w_new = w - lr * grad
            w_new = self._project_constraints(w_new, c)

            if np.linalg.norm(w_new - w) < tol:
                return w_new, i + 1
            w = w_new

        return w, iters

    def _kelly_portfolio(
        self, mu: np.ndarray, cov: np.ndarray, c: OptimizationConstraints
    ) -> Tuple[np.ndarray, int]:
        """Full Kelly portfolio: w* = Σ⁻¹(μ − rf·1), then rescale."""
        try:
            cov_inv = np.linalg.inv(cov + np.eye(len(mu)) * 1e-8)
            excess = mu - self.risk_free_rate
            w = cov_inv @ excess
            w = np.maximum(w, 0.0) if c.long_only else w
            total = w.sum()
            if total <= 0:
                w = np.ones(len(mu)) / len(mu)
            else:
                # Apply fractional Kelly (50%) for safety
                w = w / total * 0.5
                remainder = 1.0 - w.sum()
                # Allocate remainder as cash proxy (spread equally)
                w += remainder / len(mu)
            w = self._project_constraints(w, c)
            return w, 1
        except np.linalg.LinAlgError:
            return np.ones(len(mu)) / len(mu), 0

    def _black_litterman(
        self,
        symbols: List[str],
        mu_prior: np.ndarray,
        cov: np.ndarray,
        views: Dict[str, float],
        view_confidences: Optional[np.ndarray],
    ) -> np.ndarray:
        """
        Black-Litterman model: blend prior equilibrium returns with investor views.

        views: {symbol: expected_return} — absolute views.
        """
        n = len(symbols)
        tau = 0.05  # scaling factor

        # Build pick matrix P and view vector Q
        sym_idx = {s: i for i, s in enumerate(symbols)}
        view_syms = [s for s in views if s in sym_idx]
        if not view_syms:
            return mu_prior

        k = len(view_syms)
        P = np.zeros((k, n))
        Q = np.zeros(k)
        for j, sym in enumerate(view_syms):
            P[j, sym_idx[sym]] = 1.0
            Q[j] = views[sym]

        # Uncertainty in views
        if view_confidences is not None and len(view_confidences) == k:
            omega = np.diag(view_confidences ** 2)
        else:
            omega = np.diag(np.diag(tau * P @ cov @ P.T))

        # BL posterior mean
        tau_cov = tau * cov
        M1 = np.linalg.inv(tau_cov)
        M2 = P.T @ np.linalg.inv(omega) @ P
        posterior_cov_inv = M1 + M2
        posterior_mu = np.linalg.solve(
            posterior_cov_inv,
            M1 @ mu_prior + P.T @ np.linalg.inv(omega) @ Q,
        )
        return posterior_mu

    def _project_constraints(
        self, w: np.ndarray, c: OptimizationConstraints
    ) -> np.ndarray:
        """Project weights onto the feasible set (box + sum-to-one)."""
        # Clip to per-asset bounds
        w = np.clip(w, c.min_weight if c.long_only else -c.leverage_limit, c.max_weight)
        w = np.minimum(w, c.max_concentration)

        # Re-normalise to sum to 1 (simplex projection for long-only)
        total = w.sum()
        if total <= 0:
            w = np.ones(len(w)) / len(w)
        else:
            w = w / total

        return w


# ── Strategy Signal Generator ─────────────────────────────────────────────────

class StrategySignalGenerator:
    """Generates AI-driven trading signals for each investment strategy."""

    def __init__(self):
        self._signal_cache: Dict[str, StrategySignal] = {}

    async def generate_signals(
        self,
        symbols: List[str],
        price_history: Dict[str, np.ndarray],     # {symbol: daily_closes}
        volume_history: Dict[str, np.ndarray],
        strategy: InvestmentStrategy,
    ) -> List[StrategySignal]:
        tasks = [
            self._generate_signal(sym, price_history.get(sym, np.array([])),
                                  volume_history.get(sym, np.array([])), strategy)
            for sym in symbols
        ]
        return await asyncio.gather(*tasks)

    async def _generate_signal(
        self,
        symbol: str,
        prices: np.ndarray,
        volumes: np.ndarray,
        strategy: InvestmentStrategy,
    ) -> StrategySignal:
        if len(prices) < 2:
            return self._neutral_signal(symbol, strategy)

        if strategy == InvestmentStrategy.MOMENTUM:
            return self._momentum_signal(symbol, prices, strategy)
        elif strategy == InvestmentStrategy.MEAN_REVERSION:
            return self._mean_reversion_signal(symbol, prices, strategy)
        elif strategy == InvestmentStrategy.TREND_FOLLOWING:
            return self._trend_following_signal(symbol, prices, strategy)
        else:
            return self._momentum_signal(symbol, prices, strategy)

    def _momentum_signal(self, symbol: str, prices: np.ndarray,
                         strategy: InvestmentStrategy) -> StrategySignal:
        lookback = min(21, len(prices) - 1)
        momentum = (prices[-1] / prices[-lookback] - 1.0) if prices[-lookback] != 0 else 0.0
        vol = prices[-lookback:].std() / prices[-lookback:].mean() if prices[-lookback:].mean() != 0 else 0.01
        confidence = min(abs(momentum) / (vol + 1e-8) / 3.0, 1.0)
        direction = "long" if momentum > 0 else "short"
        price = float(prices[-1])
        return StrategySignal(
            symbol=symbol, strategy=strategy, direction=direction,
            confidence=confidence, expected_return=momentum,
            time_horizon_days=21, entry_price=price,
            stop_loss=price * (1 - 2 * vol), take_profit=price * (1 + 3 * vol),
        )

    def _mean_reversion_signal(self, symbol: str, prices: np.ndarray,
                                strategy: InvestmentStrategy) -> StrategySignal:
        lookback = min(20, len(prices))
        mean_price = prices[-lookback:].mean()
        std_price = prices[-lookback:].std() + 1e-8
        z_score = (prices[-1] - mean_price) / std_price
        confidence = min(abs(z_score) / 3.0, 1.0)
        direction = "short" if z_score > 1.0 else ("long" if z_score < -1.0 else "neutral")
        expected_return = -z_score * 0.05
        price = float(prices[-1])
        return StrategySignal(
            symbol=symbol, strategy=strategy, direction=direction,
            confidence=confidence, expected_return=expected_return,
            time_horizon_days=10, entry_price=price,
            stop_loss=price * (1.0 + np.sign(z_score) * 0.03),
            take_profit=float(mean_price),
        )

    def _trend_following_signal(self, symbol: str, prices: np.ndarray,
                                 strategy: InvestmentStrategy) -> StrategySignal:
        fast_ma = prices[-min(10, len(prices)):].mean()
        slow_ma = prices[-min(30, len(prices)):].mean()
        trend_strength = (fast_ma / slow_ma - 1.0) if slow_ma != 0 else 0.0
        vol = prices[-min(30, len(prices)):].std() / (prices[-1] + 1e-8)
        confidence = min(abs(trend_strength) / (vol + 1e-8) / 2.0, 1.0)
        direction = "long" if trend_strength > 0 else "short"
        price = float(prices[-1])
        return StrategySignal(
            symbol=symbol, strategy=strategy, direction=direction,
            confidence=confidence, expected_return=trend_strength * 12,
            time_horizon_days=30, entry_price=price,
            stop_loss=price * (1.0 - 3 * vol), take_profit=price * (1.0 + 5 * vol),
        )

    def _neutral_signal(self, symbol: str, strategy: InvestmentStrategy) -> StrategySignal:
        return StrategySignal(
            symbol=symbol, strategy=strategy, direction="neutral",
            confidence=0.0, expected_return=0.0, time_horizon_days=0,
            entry_price=0.0, stop_loss=0.0, take_profit=0.0,
        )


# ── Execution Engine ──────────────────────────────────────────────────────────

class StrategyExecutor:
    """
    Generates execution plans for portfolio trades.

    Supports TWAP, VWAP, Implementation-Shortfall and Adaptive slicing.
    """

    def __init__(self, max_participation_rate: float = 0.20):
        self.max_participation_rate = max_participation_rate

    async def create_execution_plan(
        self,
        symbol: str,
        target_quantity: float,
        current_price: float,
        algorithm: ExecutionAlgorithm,
        avg_daily_volume: float,
        execution_window_minutes: int = 120,
        risk_limits: Optional[Dict[str, float]] = None,
    ) -> ExecutionPlan:
        risk_limits = risk_limits or {"max_slippage_bps": 20.0, "max_market_impact_bps": 15.0}

        if algorithm == ExecutionAlgorithm.TWAP:
            slices = self._twap_slices(target_quantity, current_price, execution_window_minutes)
        elif algorithm == ExecutionAlgorithm.VWAP:
            slices = self._vwap_slices(target_quantity, current_price, avg_daily_volume,
                                       execution_window_minutes)
        elif algorithm == ExecutionAlgorithm.IS:
            slices = self._is_slices(target_quantity, current_price, avg_daily_volume,
                                     execution_window_minutes)
        elif algorithm == ExecutionAlgorithm.ADAPTIVE:
            slices = self._adaptive_slices(target_quantity, current_price, avg_daily_volume,
                                           execution_window_minutes)
        else:
            slices = [{"quantity": target_quantity, "price": current_price,
                       "offset_minutes": 0, "order_type": algorithm.value}]

        impact_bps = self._estimate_market_impact(target_quantity, avg_daily_volume, current_price)
        completion_time = datetime.now() + timedelta(minutes=execution_window_minutes)

        return ExecutionPlan(
            id=f"exec_{symbol}_{int(time.time() * 1000)}",
            symbol=symbol,
            target_quantity=target_quantity,
            algorithm=algorithm,
            slices=slices,
            estimated_market_impact_bps=impact_bps,
            estimated_completion_time=completion_time,
            risk_limits=risk_limits,
        )

    def _twap_slices(self, qty: float, price: float, window_min: int,
                     n_slices: int = 12) -> List[Dict[str, Any]]:
        slice_qty = qty / n_slices
        interval = window_min / n_slices
        return [
            {"quantity": slice_qty, "price": price, "offset_minutes": i * interval,
             "order_type": "limit", "slice_index": i}
            for i in range(n_slices)
        ]

    def _vwap_slices(self, qty: float, price: float, adv: float,
                     window_min: int) -> List[Dict[str, Any]]:
        """Distribute slices proportional to intraday volume profile (U-shaped)."""
        n = 12
        # Approximate U-shaped intraday volume curve
        profile = np.array([3, 2, 1.5, 1, 1, 1, 1, 1, 1, 1.5, 2, 3], dtype=float)
        profile /= profile.sum()
        interval = window_min / n
        return [
            {"quantity": float(qty * profile[i]), "price": price,
             "offset_minutes": i * interval, "order_type": "limit",
             "volume_weight": float(profile[i]), "slice_index": i}
            for i in range(n)
        ]

    def _is_slices(self, qty: float, price: float, adv: float,
                   window_min: int) -> List[Dict[str, Any]]:
        """
        Implementation-Shortfall: front-load when urgency is high to reduce
        timing risk, with decreasing slice sizes over time.
        """
        n = 10
        weights = np.array([n - i for i in range(n)], dtype=float)
        weights /= weights.sum()
        interval = window_min / n
        return [
            {"quantity": float(qty * weights[i]), "price": price,
             "offset_minutes": i * interval, "order_type": "limit",
             "urgency_weight": float(weights[i]), "slice_index": i}
            for i in range(n)
        ]

    def _adaptive_slices(self, qty: float, price: float, adv: float,
                         window_min: int) -> List[Dict[str, Any]]:
        """Adaptive: balance between TWAP and IS based on participation rate."""
        participation = min(qty / (adv + 1e-8), self.max_participation_rate)
        n = max(4, int(window_min / 10))
        base_qty = qty / n
        interval = window_min / n
        return [
            {"quantity": base_qty, "price": price,
             "offset_minutes": i * interval, "order_type": "limit",
             "participation_rate": participation, "slice_index": i,
             "algorithm": "adaptive"}
            for i in range(n)
        ]

    @staticmethod
    def _estimate_market_impact(qty: float, adv: float, price: float,
                                 impact_coeff: float = 0.1) -> float:
        """Square-root market impact model (bps)."""
        if adv <= 0 or price <= 0:
            return 0.0
        participation = qty / adv
        return impact_coeff * math.sqrt(participation) * 10_000  # in bps


# ── Rebalancing Engine ────────────────────────────────────────────────────────

class PortfolioRebalancer:
    """Computes rebalancing orders given current and target allocations."""

    def __init__(self, drift_threshold: float = 0.05):
        self.drift_threshold = drift_threshold

    def compute_rebalance_orders(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        portfolio_value: float,
        prices: Dict[str, float],
        trigger: RebalanceTrigger = RebalanceTrigger.THRESHOLD,
    ) -> List[PortfolioRebalanceOrder]:
        orders: List[PortfolioRebalanceOrder] = []
        all_symbols = set(current_weights) | set(target_weights)

        for sym in all_symbols:
            cur_w = current_weights.get(sym, 0.0)
            tgt_w = target_weights.get(sym, 0.0)
            drift = tgt_w - cur_w

            if trigger == RebalanceTrigger.THRESHOLD and abs(drift) < self.drift_threshold:
                continue

            price = prices.get(sym, 1.0)
            delta_value = drift * portfolio_value
            estimated_qty = delta_value / price if price > 0 else 0.0

            action = "buy" if drift > 0 else ("sell" if drift < 0 else "hold")
            algo = (ExecutionAlgorithm.TWAP if abs(drift) < 0.15
                    else ExecutionAlgorithm.IS)
            priority = 1 if abs(drift) > 0.20 else (2 if abs(drift) > 0.10 else 3)

            orders.append(PortfolioRebalanceOrder(
                symbol=sym, action=action,
                current_weight=cur_w, target_weight=tgt_w,
                drift=drift, estimated_value=abs(delta_value),
                execution_algorithm=algo, priority=priority,
            ))

        orders.sort(key=lambda o: o.priority)
        return orders


# ── Backtesting Engine ────────────────────────────────────────────────────────

class StrategyBacktester:
    """
    Vectorised backtester for investment strategies.

    Operates on daily returns and produces a comprehensive `BacktestResult`.
    """

    def __init__(self, transaction_cost_bps: float = 5.0, slippage_bps: float = 2.0):
        self.transaction_cost = transaction_cost_bps / 10_000
        self.slippage = slippage_bps / 10_000

    def run(
        self,
        strategy: InvestmentStrategy,
        price_history: Dict[str, np.ndarray],
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 1_000_000.0,
        rebalance_frequency_days: int = 21,
    ) -> BacktestResult:
        # Align all series to the shortest history
        min_len = min(len(v) for v in price_history.values()) if price_history else 0
        if min_len < 2:
            return self._empty_result(strategy, start_date, end_date)

        symbols = list(price_history.keys())
        prices = np.array([price_history[s][-min_len:] for s in symbols]).T  # T × N
        returns = prices[1:] / prices[:-1] - 1.0

        n_days = len(returns)
        equal_weight = np.ones(len(symbols)) / len(symbols)
        portfolio_returns = np.zeros(n_days)

        for t in range(n_days):
            daily_r = returns[t]
            # Apply costs on rebalance days
            cost = self.transaction_cost + self.slippage if t % rebalance_frequency_days == 0 else 0.0
            portfolio_returns[t] = float(equal_weight @ daily_r) - cost

        # Build equity curve
        equity = np.cumprod(1 + portfolio_returns) * initial_capital
        ann_return = float((equity[-1] / initial_capital) ** (252 / n_days) - 1)
        ann_vol = float(portfolio_returns.std() * math.sqrt(252))
        sharpe = FinancialMath.sharpe_ratio(portfolio_returns)
        sortino = FinancialMath.sortino_ratio(portfolio_returns)
        mdd = FinancialMath.max_drawdown(equity)
        calmar = FinancialMath.calmar_ratio(ann_return, mdd)

        positive_r = portfolio_returns[portfolio_returns > 0]
        negative_r = portfolio_returns[portfolio_returns < 0]
        win_rate = len(positive_r) / n_days if n_days > 0 else 0.0
        avg_win = float(positive_r.mean()) if len(positive_r) > 0 else 0.0
        avg_loss = float(abs(negative_r.mean())) if len(negative_r) > 0 else 0.0
        profit_factor = (avg_win * len(positive_r)) / (avg_loss * len(negative_r) + 1e-8)

        # Drawdown series
        peak = np.maximum.accumulate(equity)
        drawdown_series = ((equity - peak) / np.where(peak == 0, 1, peak)).tolist()

        return BacktestResult(
            strategy=strategy,
            start_date=start_date, end_date=end_date,
            total_return=float(equity[-1] / initial_capital - 1),
            annualized_return=ann_return,
            annualized_volatility=ann_vol,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            max_drawdown=mdd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=n_days // rebalance_frequency_days,
            avg_trade_return=float(portfolio_returns.mean()),
            equity_curve=equity.tolist(),
            drawdown_series=drawdown_series,
        )

    def _empty_result(self, strategy: InvestmentStrategy,
                      start_date: datetime, end_date: datetime) -> BacktestResult:
        return BacktestResult(
            strategy=strategy, start_date=start_date, end_date=end_date,
            total_return=0.0, annualized_return=0.0, annualized_volatility=0.0,
            sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
            max_drawdown=0.0, win_rate=0.0, profit_factor=0.0,
            total_trades=0, avg_trade_return=0.0, equity_curve=[], drawdown_series=[],
        )


# ── Top-Level Agent ───────────────────────────────────────────────────────────

class InvestmentStrategyAgent:
    """
    High-level agent that orchestrates the full investment lifecycle:
      1. Generate signals
      2. Optimise portfolio weights
      3. Compute rebalance orders
      4. Build execution plans
      5. Run backtests on request

    Designed to integrate with the broader ACTORS distributed agent network.
    """

    def __init__(
        self,
        risk_free_rate: float = 0.04,
        drift_threshold: float = 0.05,
        transaction_cost_bps: float = 5.0,
    ):
        self.optimizer = AIPortfolioOptimizer(risk_free_rate)
        self.signal_generator = StrategySignalGenerator()
        self.executor = StrategyExecutor()
        self.rebalancer = PortfolioRebalancer(drift_threshold)
        self.backtester = StrategyBacktester(transaction_cost_bps)
        self._optimization_history: List[OptimizationResult] = []

    async def run_full_cycle(
        self,
        symbols: List[str],
        price_history: Dict[str, np.ndarray],
        volume_history: Dict[str, np.ndarray],
        current_weights: Dict[str, float],
        portfolio_value: float,
        prices: Dict[str, float],
        strategy: InvestmentStrategy = InvestmentStrategy.MOMENTUM,
        optimization_method: PortfolioOptimizationMethod = PortfolioOptimizationMethod.MAXIMUM_SHARPE,
        constraints: Optional[OptimizationConstraints] = None,
        views: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Full investment strategy cycle returning signals, optimal weights,
        rebalance orders and execution plans.
        """
        # Step 1: Generate signals
        signals = await self.signal_generator.generate_signals(
            symbols, price_history, volume_history, strategy
        )

        # Step 2: Derive expected returns and covariance from history
        mu, cov = self._estimate_parameters(symbols, price_history)

        # Step 3: Overlay signal-based return views
        signal_views: Dict[str, float] = {
            s.symbol: s.expected_return
            for s in signals if s.confidence > 0.4 and s.direction != "neutral"
        }
        if views:
            signal_views.update(views)

        # Step 4: Optimise
        opt_result = await self.optimizer.optimize(
            symbols=symbols,
            expected_returns=mu,
            covariance_matrix=cov,
            method=optimization_method,
            constraints=constraints,
            views=signal_views if signal_views else None,
        )
        self._optimization_history.append(opt_result)

        # Step 5: Compute rebalance orders
        rebalance_orders = self.rebalancer.compute_rebalance_orders(
            current_weights, opt_result.weights, portfolio_value, prices
        )

        # Step 6: Build execution plans for non-trivial orders
        execution_plans = []
        for order in rebalance_orders:
            if order.estimated_value > 0:
                adv = float(volume_history.get(order.symbol, np.array([1e6])).mean()) * prices.get(order.symbol, 1.0)
                plan = await self.executor.create_execution_plan(
                    symbol=order.symbol,
                    target_quantity=order.estimated_value / prices.get(order.symbol, 1.0),
                    current_price=prices.get(order.symbol, 1.0),
                    algorithm=order.execution_algorithm,
                    avg_daily_volume=adv,
                )
                execution_plans.append(asdict(plan))

        return {
            "signals": [asdict(s) for s in signals],
            "optimization": asdict(opt_result),
            "rebalance_orders": [asdict(o) for o in rebalance_orders],
            "execution_plans": execution_plans,
            "cycle_timestamp": datetime.now().isoformat(),
        }

    async def backtest_strategy(
        self,
        strategy: InvestmentStrategy,
        price_history: Dict[str, np.ndarray],
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 1_000_000.0,
    ) -> BacktestResult:
        return self.backtester.run(
            strategy, price_history, start_date, end_date, initial_capital
        )

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        return [asdict(r) for r in self._optimization_history]

    # ── Internal Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _estimate_parameters(
        symbols: List[str],
        price_history: Dict[str, np.ndarray],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Estimate annualised expected returns and covariance from price history."""
        n = len(symbols)
        min_len = min(len(price_history.get(s, np.array([1.0]))) for s in symbols)
        if min_len < 2:
            return np.zeros(n), np.eye(n) * 0.04

        returns_matrix = []
        for sym in symbols:
            p = price_history.get(sym, np.ones(min_len))[-min_len:]
            r = np.diff(p) / p[:-1]
            returns_matrix.append(r)

        R = np.array(returns_matrix)  # N × T
        mu = R.mean(axis=1) * 252
        cov = np.cov(R) * 252 if n > 1 else np.array([[R[0].var() * 252]])

        # Regularise covariance (Ledoit-Wolf shrinkage approximation)
        cov = cov + np.eye(n) * 1e-6

        return mu, cov


# ── Demo / Smoke Test ─────────────────────────────────────────────────────────

async def _demo():
    """Quick smoke-test demonstrating the full investment cycle."""
    np.random.seed(42)
    symbols = ["AAPL", "GOOGL", "MSFT", "BTC", "ETH"]
    n_days = 252

    # Simulate price history
    price_history: Dict[str, np.ndarray] = {}
    volume_history: Dict[str, np.ndarray] = {}
    prices: Dict[str, float] = {}
    for i, sym in enumerate(symbols):
        daily_returns = np.random.normal(0.0008, 0.02, n_days)
        price_series = 100.0 * np.cumprod(1 + daily_returns)
        price_history[sym] = price_series
        volume_history[sym] = np.random.lognormal(14, 0.5, n_days)
        prices[sym] = float(price_series[-1])

    current_weights = {sym: 1.0 / len(symbols) for sym in symbols}
    portfolio_value = 1_000_000.0

    agent = InvestmentStrategyAgent()

    print("🤖 AI Investment Strategy Agent — Full Cycle Demo")
    print("=" * 60)

    result = await agent.run_full_cycle(
        symbols=symbols,
        price_history=price_history,
        volume_history=volume_history,
        current_weights=current_weights,
        portfolio_value=portfolio_value,
        prices=prices,
        strategy=InvestmentStrategy.MOMENTUM,
        optimization_method=PortfolioOptimizationMethod.MAXIMUM_SHARPE,
    )

    opt = result["optimization"]
    print(f"\n📊 Optimised Portfolio (Max Sharpe):")
    for sym, w in opt["weights"].items():
        print(f"  {sym:6s}: {w * 100:6.2f}%")
    print(f"  Expected Return   : {opt['expected_return'] * 100:.2f}%")
    print(f"  Expected Volatility: {opt['expected_volatility'] * 100:.2f}%")
    print(f"  Sharpe Ratio      : {opt['sharpe_ratio']:.3f}")
    print(f"  Sortino Ratio     : {opt['sortino_ratio']:.3f}")
    print(f"  Diversification   : {opt['diversification_ratio']:.3f}")

    print(f"\n📋 Rebalance Orders: {len(result['rebalance_orders'])}")
    for order in result["rebalance_orders"]:
        print(f"  {order['action'].upper():4s} {order['symbol']:6s}  "
              f"drift={order['drift'] * 100:+.1f}%  "
              f"algo={order['execution_algorithm']}")

    # Backtest
    bt = await agent.backtest_strategy(
        strategy=InvestmentStrategy.MOMENTUM,
        price_history=price_history,
        start_date=datetime.now() - timedelta(days=n_days),
        end_date=datetime.now(),
    )
    print(f"\n📈 Backtest Results (Momentum):")
    print(f"  Total Return      : {bt.total_return * 100:.2f}%")
    print(f"  Ann. Return       : {bt.annualized_return * 100:.2f}%")
    print(f"  Ann. Volatility   : {bt.annualized_volatility * 100:.2f}%")
    print(f"  Sharpe Ratio      : {bt.sharpe_ratio:.3f}")
    print(f"  Sortino Ratio     : {bt.sortino_ratio:.3f}")
    print(f"  Calmar Ratio      : {bt.calmar_ratio:.3f}")
    print(f"  Max Drawdown      : {bt.max_drawdown * 100:.2f}%")
    print(f"  Win Rate          : {bt.win_rate * 100:.1f}%")
    print(f"  Profit Factor     : {bt.profit_factor:.2f}")
    print(f"  Total Trades      : {bt.total_trades}")


if __name__ == "__main__":
    asyncio.run(_demo())
