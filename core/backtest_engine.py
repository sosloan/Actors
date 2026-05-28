"""
Backtest Engine for the ACTORS Financial Intelligence Platform
==============================================================

A lightweight, event-driven backtesting framework that integrates with the
existing ACTORS ecosystem.

Key components
--------------
- :class:`Bar`             – OHLCV price bar
- :class:`BacktestConfig`  – simulation parameters
- :class:`Signal`          – buy / sell / hold action
- :class:`Trade`           – completed round-trip trade record
- :class:`BacktestResult`  – performance metrics after a run
- :class:`BacktestEngine`  – main simulation driver
- :class:`Strategy`        – abstract base for pluggable strategies
- Bundled strategies: :class:`MovingAverageCrossover`, :class:`MomentumStrategy`
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import List, Optional, Tuple


# ── Data structures ─────────────────────────────────────────────────────────────

@dataclass
class Bar:
    """A single OHLCV price bar."""

    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class BacktestConfig:
    """Configuration for a backtest simulation."""

    #: Starting cash balance.
    initial_capital: float = 100_000.0
    #: Fractional commission per trade (e.g. ``0.001`` = 0.1 %).
    commission_rate: float = 0.001
    #: Fractional slippage per fill (e.g. ``0.0005`` = 0.05 %).
    slippage_rate: float = 0.0005
    #: Maximum fraction of capital risked per single trade (e.g. ``0.10`` = 10 %).
    max_position_size: float = 0.10


class Signal(Enum):
    """Action returned by a strategy for a given bar."""

    BUY = auto()
    SELL = auto()
    HOLD = auto()


@dataclass
class Trade:
    """Records a completed round-trip trade (entry → exit)."""

    symbol: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    return_pct: float


@dataclass
class BacktestResult:
    """Performance metrics produced after a full simulation."""

    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    profit_factor: float
    final_equity: float
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"BacktestResult("
            f"total_return={self.total_return:.2%}, "
            f"ann_return={self.annualized_return:.2%}, "
            f"sharpe={self.sharpe_ratio:.2f}, "
            f"max_drawdown={self.max_drawdown:.2%}, "
            f"win_rate={self.win_rate:.1%}, "
            f"trades={self.total_trades}, "
            f"final_equity={self.final_equity:.2f}"
            f")"
        )


# ── Portfolio state ──────────────────────────────────────────────────────────────

class _BacktestPortfolio:
    """Internal portfolio state during a simulation."""

    def __init__(self, initial_capital: float, symbol: str) -> None:
        self.cash: float = initial_capital
        self.position_quantity: float = 0.0
        self.position_entry_price: float = 0.0
        self.position_entry_time: Optional[datetime] = None
        self.symbol: str = symbol

    @property
    def is_long(self) -> bool:
        return self.position_quantity > 0.0

    def position_value(self, current_price: float) -> float:
        return self.position_quantity * current_price

    def equity(self, current_price: float) -> float:
        return self.cash + self.position_value(current_price)


# ── Strategy base class ──────────────────────────────────────────────────────────

class Strategy(ABC):
    """Abstract base class for all backtest strategies.

    Subclass this and implement :meth:`on_bar` to create a custom strategy.
    """

    @abstractmethod
    def on_bar(self, bar: Bar, portfolio: _BacktestPortfolio) -> Signal:
        """Called once per bar in ascending chronological order.

        Parameters
        ----------
        bar:
            The current OHLCV bar.
        portfolio:
            Read-only view of the current portfolio state.

        Returns
        -------
        Signal
            The desired action for this bar.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy identifier."""


# ── Backtest engine ──────────────────────────────────────────────────────────────

class BacktestEngine:
    """Event-driven backtesting engine.

    Parameters
    ----------
    config:
        Simulation parameters.  Defaults to :class:`BacktestConfig` defaults
        when not provided.
    """

    def __init__(self, config: Optional[BacktestConfig] = None) -> None:
        self._config: BacktestConfig = config or BacktestConfig()

    def run(self, bars: List[Bar], strategy: Strategy) -> BacktestResult:
        """Simulate *strategy* over *bars* and return performance metrics.

        Parameters
        ----------
        bars:
            OHLCV bars sorted in ascending chronological order.
        strategy:
            A :class:`Strategy` instance.  ``on_bar`` is called once per bar.

        Returns
        -------
        BacktestResult
            Full performance metrics including the equity curve and trade log.
        """
        if not bars:
            return self._empty_result()

        symbol = bars[0].symbol
        portfolio = _BacktestPortfolio(self._config.initial_capital, symbol)
        equity_curve: List[Tuple[datetime, float]] = []
        completed_trades: List[Trade] = []

        for bar in bars:
            signal = strategy.on_bar(bar, portfolio)

            if signal is Signal.BUY and not portfolio.is_long:
                self._execute_buy(bar, portfolio)
            elif signal is Signal.SELL and portfolio.is_long:
                trade = self._execute_sell(bar, portfolio)
                if trade is not None:
                    completed_trades.append(trade)

            equity_curve.append((bar.timestamp, portfolio.equity(bar.close)))

        # Close any open position at the last bar's close.
        if portfolio.is_long:
            trade = self._execute_sell(bars[-1], portfolio)
            if trade is not None:
                completed_trades.append(trade)

        final_equity = portfolio.equity(bars[-1].close)
        return self._calculate_results(final_equity, equity_curve, completed_trades, len(bars))

    # ── private helpers ────────────────────────────────────────────────────────

    def _execute_buy(self, bar: Bar, portfolio: _BacktestPortfolio) -> None:
        fill_price = bar.close * (1.0 + self._config.slippage_rate)
        capital_at_risk = portfolio.cash * self._config.max_position_size
        quantity = math.floor(capital_at_risk / fill_price)
        if quantity <= 0:
            return
        cost = quantity * fill_price * (1.0 + self._config.commission_rate)
        if cost > portfolio.cash:
            return
        portfolio.cash -= cost
        portfolio.position_quantity = quantity
        portfolio.position_entry_price = fill_price
        portfolio.position_entry_time = bar.timestamp

    def _execute_sell(self, bar: Bar, portfolio: _BacktestPortfolio) -> Optional[Trade]:
        if portfolio.position_quantity <= 0:
            return None
        fill_price = bar.close * (1.0 - self._config.slippage_rate)
        proceeds = portfolio.position_quantity * fill_price * (1.0 - self._config.commission_rate)
        cost_basis = portfolio.position_quantity * portfolio.position_entry_price
        pnl = proceeds - cost_basis
        return_pct = pnl / cost_basis if cost_basis > 0 else 0.0

        trade = Trade(
            symbol=portfolio.symbol,
            entry_time=portfolio.position_entry_time or bar.timestamp,
            exit_time=bar.timestamp,
            entry_price=portfolio.position_entry_price,
            exit_price=fill_price,
            quantity=portfolio.position_quantity,
            pnl=pnl,
            return_pct=return_pct,
        )
        portfolio.cash += proceeds
        portfolio.position_quantity = 0.0
        portfolio.position_entry_price = 0.0
        portfolio.position_entry_time = None
        return trade

    def _calculate_results(
        self,
        final_equity: float,
        equity_curve: List[Tuple[datetime, float]],
        trades: List[Trade],
        num_bars: int,
    ) -> BacktestResult:
        total_return = (final_equity - self._config.initial_capital) / self._config.initial_capital

        years = num_bars / 252.0
        annualized_return = (
            (1.0 + total_return) ** (1.0 / years) - 1.0 if years > 0 else 0.0
        )

        sharpe = self._sharpe(equity_curve)
        max_dd = self._max_drawdown(equity_curve)

        winning = [t for t in trades if t.pnl > 0]
        losing = [t for t in trades if t.pnl <= 0]
        win_rate = len(winning) / len(trades) if trades else 0.0
        gross_profit = sum(t.pnl for t in winning)
        gross_loss = sum(abs(t.pnl) for t in losing)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        return BacktestResult(
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            win_rate=win_rate,
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            profit_factor=profit_factor,
            final_equity=final_equity,
            equity_curve=equity_curve,
            trades=trades,
        )

    def _sharpe(self, curve: List[Tuple[datetime, float]]) -> float:
        if len(curve) < 2:
            return 0.0
        returns = [
            (curve[i][1] - curve[i - 1][1]) / curve[i - 1][1]
            for i in range(1, len(curve))
            if curve[i - 1][1] != 0.0
        ]
        if len(returns) < 2:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        if std_dev == 0.0:
            return 0.0
        return (mean / std_dev) * math.sqrt(252)

    def _max_drawdown(self, curve: List[Tuple[datetime, float]]) -> float:
        if not curve:
            return 0.0
        peak = curve[0][1]
        max_dd = 0.0
        for _, equity in curve:
            if equity > peak:
                peak = equity
            if peak > 0:
                dd = (peak - equity) / peak
                if dd > max_dd:
                    max_dd = dd
        return max_dd

    def _empty_result(self) -> BacktestResult:
        return BacktestResult(
            total_return=0.0,
            annualized_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            profit_factor=0.0,
            final_equity=self._config.initial_capital,
        )


# ── Bundled strategies ───────────────────────────────────────────────────────────

class MovingAverageCrossover(Strategy):
    """Dual simple-moving-average crossover strategy.

    Generates :attr:`Signal.BUY` when the fast SMA crosses above the slow SMA
    and :attr:`Signal.SELL` when it crosses below.

    Parameters
    ----------
    fast_period:
        Window length for the fast moving average.
    slow_period:
        Window length for the slow moving average.  Must be > ``fast_period``.
    """

    def __init__(self, fast_period: int, slow_period: int) -> None:
        if fast_period <= 0:
            raise ValueError("fast_period must be > 0")
        if slow_period <= fast_period:
            raise ValueError("slow_period must be > fast_period")
        self._fast_period = fast_period
        self._slow_period = slow_period
        self._prices: deque[float] = deque(maxlen=slow_period)
        self._prev_fast_sma: Optional[float] = None
        self._prev_slow_sma: Optional[float] = None

    @property
    def name(self) -> str:
        return "MovingAverageCrossover"

    def on_bar(self, bar: Bar, portfolio: _BacktestPortfolio) -> Signal:  # noqa: ARG002
        self._prices.append(bar.close)

        if len(self._prices) < self._slow_period:
            return Signal.HOLD

        prices_list = list(self._prices)
        fast_sma = sum(prices_list[-self._fast_period :]) / self._fast_period
        slow_sma = sum(prices_list[-self._slow_period :]) / self._slow_period

        signal = Signal.HOLD
        if self._prev_fast_sma is not None and self._prev_slow_sma is not None:
            if self._prev_fast_sma <= self._prev_slow_sma and fast_sma > slow_sma:
                signal = Signal.BUY
            elif self._prev_fast_sma >= self._prev_slow_sma and fast_sma < slow_sma:
                signal = Signal.SELL

        self._prev_fast_sma = fast_sma
        self._prev_slow_sma = slow_sma
        return signal


class MomentumStrategy(Strategy):
    """Rate-of-change momentum strategy.

    Generates :attr:`Signal.BUY` when the ``lookback``-bar return exceeds
    ``threshold`` and :attr:`Signal.SELL` when it falls below ``-threshold``.

    Parameters
    ----------
    lookback:
        Number of bars used to compute the rate of change.
    threshold:
        Minimum absolute return required to trigger a signal (e.g. ``0.02``
        for 2 %).
    """

    def __init__(self, lookback: int, threshold: float) -> None:
        if lookback <= 0:
            raise ValueError("lookback must be > 0")
        self._lookback = lookback
        self._threshold = threshold
        self._prices: deque[float] = deque(maxlen=lookback + 1)

    @property
    def name(self) -> str:
        return "MomentumStrategy"

    def on_bar(self, bar: Bar, portfolio: _BacktestPortfolio) -> Signal:  # noqa: ARG002
        self._prices.append(bar.close)
        if len(self._prices) <= self._lookback:
            return Signal.HOLD

        oldest = self._prices[0]
        if oldest == 0.0:
            return Signal.HOLD

        momentum = (bar.close - oldest) / oldest
        if momentum > self._threshold:
            return Signal.BUY
        if momentum < -self._threshold:
            return Signal.SELL
        return Signal.HOLD
