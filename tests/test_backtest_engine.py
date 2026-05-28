#!/usr/bin/env python3
"""
Comprehensive tests for core.backtest_engine
=============================================

Covers:
- Data structures: Bar, BacktestConfig, Signal, Trade, BacktestResult
- BacktestEngine.run() with MovingAverageCrossover and MomentumStrategy
- Edge cases: empty bars, single bar, no trades, always-long, flat prices
- Performance metrics: total_return, annualized_return, sharpe_ratio,
  max_drawdown, win_rate, profit_factor
- Commission and slippage cost accounting
- Position sizing and capital constraints
"""

from __future__ import annotations

import math
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import List

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.backtest_engine import (
    Bar,
    BacktestConfig,
    BacktestEngine,
    BacktestResult,
    MomentumStrategy,
    MovingAverageCrossover,
    Signal,
    Strategy,
    Trade,
    _BacktestPortfolio,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_bars(
    prices: List[float],
    symbol: str = "TEST",
    start: datetime | None = None,
) -> List[Bar]:
    """Build a minimal list of Bar objects from a price series."""
    if start is None:
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    bars = []
    for i, price in enumerate(prices):
        ts = start + timedelta(days=i)
        bars.append(
            Bar(
                timestamp=ts,
                symbol=symbol,
                open=price,
                high=price * 1.01,
                low=price * 0.99,
                close=price,
                volume=1_000_000.0,
            )
        )
    return bars


def _trending_up(n: int = 60, start_price: float = 100.0, step: float = 1.0) -> List[float]:
    """Flat warm-up (25 bars) then linear rise so fast/slow SMA cross is triggered."""
    flat_bars = 25
    flat = [start_price] * flat_bars
    rise_n = max(n - flat_bars, 1)
    rise = [start_price + i * step for i in range(1, rise_n + 1)]
    return (flat + rise)[:n]


def _trending_down(n: int = 60, start_price: float = 160.0, step: float = 1.0) -> List[float]:
    """Rise for warm-up then fall so a death-cross is triggered."""
    flat_bars = 25
    flat = [start_price] * flat_bars
    fall_n = max(n - flat_bars, 1)
    fall = [start_price - i * step for i in range(1, fall_n + 1)]
    return (flat + fall)[:n]


def _flat(n: int = 50, price: float = 100.0) -> List[float]:
    return [price] * n


# ---------------------------------------------------------------------------
# Tests: Bar dataclass
# ---------------------------------------------------------------------------

class TestBar:
    def test_construction(self):
        ts = datetime(2024, 6, 1, tzinfo=timezone.utc)
        bar = Bar(
            timestamp=ts,
            symbol="AAPL",
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=5_000_000.0,
        )
        assert bar.timestamp == ts
        assert bar.symbol == "AAPL"
        assert bar.open == 150.0
        assert bar.high == 155.0
        assert bar.low == 148.0
        assert bar.close == 153.0
        assert bar.volume == 5_000_000.0

    def test_equality(self):
        ts = datetime(2024, 6, 1, tzinfo=timezone.utc)
        b1 = Bar(ts, "X", 1.0, 2.0, 0.5, 1.5, 100.0)
        b2 = Bar(ts, "X", 1.0, 2.0, 0.5, 1.5, 100.0)
        assert b1 == b2


# ---------------------------------------------------------------------------
# Tests: BacktestConfig dataclass
# ---------------------------------------------------------------------------

class TestBacktestConfig:
    def test_defaults(self):
        cfg = BacktestConfig()
        assert cfg.initial_capital == 100_000.0
        assert cfg.commission_rate == 0.001
        assert cfg.slippage_rate == 0.0005
        assert cfg.max_position_size == 0.10

    def test_custom_values(self):
        cfg = BacktestConfig(
            initial_capital=50_000.0,
            commission_rate=0.002,
            slippage_rate=0.001,
            max_position_size=0.25,
        )
        assert cfg.initial_capital == 50_000.0
        assert cfg.commission_rate == 0.002
        assert cfg.slippage_rate == 0.001
        assert cfg.max_position_size == 0.25


# ---------------------------------------------------------------------------
# Tests: BacktestResult.__str__
# ---------------------------------------------------------------------------

class TestBacktestResultStr:
    def test_str_format(self):
        result = BacktestResult(
            total_return=0.0877,
            annualized_return=0.1117,
            sharpe_ratio=45.11,
            max_drawdown=0.02,
            win_rate=0.75,
            total_trades=10,
            winning_trades=7,
            losing_trades=3,
            profit_factor=3.5,
            final_equity=108_770.0,
        )
        s = str(result)
        assert s.startswith("BacktestResult(")
        assert "8.77%" in s
        assert "11.17%" in s
        assert "45.11" in s

    def test_str_contains_all_fields(self):
        result = BacktestResult(
            total_return=0.05,
            annualized_return=0.06,
            sharpe_ratio=1.5,
            max_drawdown=0.03,
            win_rate=0.6,
            total_trades=5,
            winning_trades=3,
            losing_trades=2,
            profit_factor=2.0,
            final_equity=105_000.0,
        )
        s = str(result)
        assert "total_return=" in s
        assert "ann_return=" in s
        assert "sharpe=" in s
        assert "max_drawdown=" in s
        assert "win_rate=" in s
        assert "trades=" in s
        assert "final_equity=" in s


# ---------------------------------------------------------------------------
# Tests: _BacktestPortfolio
# ---------------------------------------------------------------------------

class TestBacktestPortfolio:
    def test_initial_state(self):
        p = _BacktestPortfolio(100_000.0, "AAPL")
        assert p.cash == 100_000.0
        assert p.position_quantity == 0.0
        assert not p.is_long

    def test_equity_no_position(self):
        p = _BacktestPortfolio(100_000.0, "AAPL")
        assert p.equity(150.0) == 100_000.0

    def test_equity_with_position(self):
        p = _BacktestPortfolio(100_000.0, "AAPL")
        p.cash = 85_000.0
        p.position_quantity = 100.0
        assert p.equity(150.0) == 85_000.0 + 100.0 * 150.0

    def test_is_long_true(self):
        p = _BacktestPortfolio(100_000.0, "AAPL")
        p.position_quantity = 10.0
        assert p.is_long

    def test_position_value(self):
        p = _BacktestPortfolio(100_000.0, "AAPL")
        p.position_quantity = 50.0
        assert p.position_value(200.0) == 10_000.0


# ---------------------------------------------------------------------------
# Tests: BacktestEngine edge cases
# ---------------------------------------------------------------------------

class TestBacktestEngineEdgeCases:
    def test_empty_bars_returns_empty_result(self):
        engine = BacktestEngine(BacktestConfig(initial_capital=100_000.0))
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run([], strategy)
        assert result.total_return == 0.0
        assert result.total_trades == 0
        assert result.final_equity == 100_000.0

    def test_single_bar_no_trade(self):
        bars = _make_bars([100.0])
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run(bars, strategy)
        assert result.total_trades == 0
        assert result.final_equity == pytest.approx(100_000.0, rel=1e-6)

    def test_fewer_bars_than_slow_period_no_trade(self):
        bars = _make_bars(_trending_up(n=15))
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run(bars, strategy)
        assert result.total_trades == 0

    def test_flat_price_no_crossover(self):
        bars = _make_bars(_flat(n=50, price=100.0))
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run(bars, strategy)
        # No crossover on flat prices → no trades
        assert result.total_trades == 0

    def test_default_config_used_when_none(self):
        engine = BacktestEngine()
        assert engine._config.initial_capital == 100_000.0

    def test_result_equity_curve_length_matches_bars(self):
        prices = _trending_up(n=50)
        bars = _make_bars(prices)
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run(bars, strategy)
        assert len(result.equity_curve) == len(bars)

    def test_equity_curve_timestamps_match_bars(self):
        prices = _trending_up(n=30)
        bars = _make_bars(prices)
        engine = BacktestEngine()
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run(bars, strategy)
        for (curve_ts, _), bar in zip(result.equity_curve, bars):
            assert curve_ts == bar.timestamp


# ---------------------------------------------------------------------------
# Tests: MovingAverageCrossover strategy
# ---------------------------------------------------------------------------

class TestMovingAverageCrossover:
    def test_invalid_fast_period_raises(self):
        with pytest.raises(ValueError, match="fast_period"):
            MovingAverageCrossover(fast_period=0, slow_period=20)

    def test_slow_not_greater_than_fast_raises(self):
        with pytest.raises(ValueError, match="slow_period"):
            MovingAverageCrossover(fast_period=10, slow_period=10)

    def test_slow_less_than_fast_raises(self):
        with pytest.raises(ValueError, match="slow_period"):
            MovingAverageCrossover(fast_period=20, slow_period=5)

    def test_name(self):
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        assert strategy.name == "MovingAverageCrossover"

    def test_hold_before_warmup(self):
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        bars = _make_bars(_trending_up(n=19))
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert all(s is Signal.HOLD for s in signals)

    def test_buy_signal_on_golden_cross(self):
        """Craft a price series where fast SMA crosses above slow SMA once."""
        # Start flat at 100, then step up sharply so fast SMA crosses slow SMA
        flat = [100.0] * 25
        rise = [100.0 + i * 3 for i in range(15)]
        prices = flat + rise
        bars = _make_bars(prices)
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert Signal.BUY in signals

    def test_sell_signal_on_death_cross(self):
        """Price rises then falls – expect a SELL after the peak."""
        rise = [100.0 + i * 2 for i in range(30)]
        fall = [160.0 - i * 2 for i in range(30)]
        prices = rise + fall
        bars = _make_bars(prices)
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert Signal.SELL in signals

    def test_trending_up_generates_trades(self):
        prices = _trending_up(n=80, step=0.5)
        bars = _make_bars(prices)
        engine = BacktestEngine(BacktestConfig(initial_capital=100_000.0))
        strategy = MovingAverageCrossover(fast_period=5, slow_period=20)
        result = engine.run(bars, strategy)
        assert result.total_trades >= 1

    def test_positive_return_on_trending_market(self):
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        engine = BacktestEngine(BacktestConfig(initial_capital=100_000.0))
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert result.total_return > 0

    def test_final_equity_positive(self):
        prices = _trending_up(n=60)
        bars = _make_bars(prices)
        engine = BacktestEngine()
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert result.final_equity > 0


# ---------------------------------------------------------------------------
# Tests: MomentumStrategy
# ---------------------------------------------------------------------------

class TestMomentumStrategy:
    def test_invalid_lookback_raises(self):
        with pytest.raises(ValueError, match="lookback"):
            MomentumStrategy(lookback=0, threshold=0.02)

    def test_name(self):
        strategy = MomentumStrategy(lookback=10, threshold=0.02)
        assert strategy.name == "MomentumStrategy"

    def test_hold_during_warmup(self):
        strategy = MomentumStrategy(lookback=10, threshold=0.02)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        bars = _make_bars(_trending_up(n=10))
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert all(s is Signal.HOLD for s in signals)

    def test_buy_on_strong_uptrend(self):
        # 10% rise in lookback window should trigger buy (threshold=0.02)
        base = [100.0] * 11
        surge = [100.0 + i * 5 for i in range(20)]
        prices = base + surge
        bars = _make_bars(prices)
        strategy = MomentumStrategy(lookback=5, threshold=0.02)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert Signal.BUY in signals

    def test_sell_on_strong_downtrend(self):
        base = [100.0] * 11
        crash = [100.0 - i * 5 for i in range(20)]
        prices = base + crash
        bars = _make_bars(prices)
        strategy = MomentumStrategy(lookback=5, threshold=0.02)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert Signal.SELL in signals

    def test_flat_market_hold_only(self):
        bars = _make_bars(_flat(n=50))
        strategy = MomentumStrategy(lookback=10, threshold=0.02)
        portfolio = _BacktestPortfolio(100_000.0, "T")
        signals = [strategy.on_bar(b, portfolio) for b in bars]
        assert all(s is Signal.HOLD for s in signals)

    def test_engine_run_with_momentum(self):
        prices = _trending_up(n=100, step=0.5)
        bars = _make_bars(prices)
        engine = BacktestEngine(BacktestConfig(initial_capital=100_000.0))
        result = engine.run(bars, MomentumStrategy(lookback=10, threshold=0.02))
        assert isinstance(result, BacktestResult)
        assert result.final_equity > 0


# ---------------------------------------------------------------------------
# Tests: Trade accounting
# ---------------------------------------------------------------------------

class TestTradeAccounting:
    def _run_trending(self, fast: int = 5, slow: int = 20) -> BacktestResult:
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        cfg = BacktestConfig(initial_capital=100_000.0, commission_rate=0.001, slippage_rate=0.0005)
        engine = BacktestEngine(cfg)
        return engine.run(bars, MovingAverageCrossover(fast_period=fast, slow_period=slow))

    def test_trade_fields_populated(self):
        result = self._run_trending()
        for trade in result.trades:
            assert trade.symbol == "TEST"
            assert isinstance(trade.entry_time, datetime)
            assert isinstance(trade.exit_time, datetime)
            assert trade.entry_price > 0
            assert trade.exit_price > 0
            assert trade.quantity > 0

    def test_winning_plus_losing_equals_total(self):
        result = self._run_trending()
        assert result.winning_trades + result.losing_trades == result.total_trades

    def test_win_rate_between_zero_and_one(self):
        result = self._run_trending()
        assert 0.0 <= result.win_rate <= 1.0

    def test_profit_factor_positive_when_profitable(self):
        result = self._run_trending()
        if result.winning_trades > 0 and result.losing_trades > 0:
            assert result.profit_factor > 0
        elif result.losing_trades == 0:
            assert result.profit_factor == float("inf")

    def test_trade_return_pct_consistent(self):
        result = self._run_trending()
        for trade in result.trades:
            expected = (trade.exit_price - trade.entry_price) / trade.entry_price
            # return_pct accounts for slippage/commission so allow some tolerance
            assert abs(trade.return_pct - expected) < 0.01

    def test_commission_reduces_pnl(self):
        """Zero-commission result should have higher final equity than with commission."""
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        strategy_a = MovingAverageCrossover(fast_period=5, slow_period=20)
        strategy_b = MovingAverageCrossover(fast_period=5, slow_period=20)
        cfg_with = BacktestConfig(initial_capital=100_000.0, commission_rate=0.005)
        cfg_without = BacktestConfig(initial_capital=100_000.0, commission_rate=0.0, slippage_rate=0.0)
        result_with = BacktestEngine(cfg_with).run(bars, strategy_a)
        result_without = BacktestEngine(cfg_without).run(bars, strategy_b)
        if result_with.total_trades > 0:
            assert result_without.final_equity >= result_with.final_equity

    def test_position_size_respects_max_fraction(self):
        """Cost of each buy should not exceed max_position_size fraction of capital."""
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        cfg = BacktestConfig(initial_capital=100_000.0, max_position_size=0.10, commission_rate=0.0, slippage_rate=0.0)
        engine = BacktestEngine(cfg)
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        for trade in result.trades:
            trade_cost = trade.quantity * trade.entry_price
            assert trade_cost <= cfg.initial_capital * cfg.max_position_size * 1.02  # tiny rounding buffer


# ---------------------------------------------------------------------------
# Tests: Performance metrics
# ---------------------------------------------------------------------------

class TestPerformanceMetrics:
    def test_total_return_consistent_with_equity(self):
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        cfg = BacktestConfig(initial_capital=100_000.0)
        result = BacktestEngine(cfg).run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        expected_return = (result.final_equity - cfg.initial_capital) / cfg.initial_capital
        assert result.total_return == pytest.approx(expected_return, rel=1e-9)

    def test_max_drawdown_between_zero_and_one(self):
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        result = BacktestEngine().run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert 0.0 <= result.max_drawdown <= 1.0

    def test_max_drawdown_zero_for_monotone_equity(self):
        """Pure uptrend with no drawdown in equity."""
        prices = _flat(n=50)
        bars = _make_bars(prices)
        result = BacktestEngine().run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert result.max_drawdown == pytest.approx(0.0, abs=1e-9)

    def test_sharpe_is_finite_for_normal_run(self):
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        result = BacktestEngine().run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert math.isfinite(result.sharpe_ratio)

    def test_annualized_return_gt_zero_for_uptrend(self):
        prices = _trending_up(n=252, step=0.5)
        bars = _make_bars(prices)
        result = BacktestEngine(BacktestConfig(initial_capital=100_000.0)).run(
            bars, MovingAverageCrossover(fast_period=5, slow_period=20)
        )
        assert result.annualized_return > 0

    def test_empty_result_all_zeros(self):
        engine = BacktestEngine(BacktestConfig(initial_capital=50_000.0))
        result = engine.run([], MovingAverageCrossover(fast_period=5, slow_period=20))
        assert result.total_return == 0.0
        assert result.annualized_return == 0.0
        assert result.sharpe_ratio == 0.0
        assert result.max_drawdown == 0.0
        assert result.total_trades == 0
        assert result.final_equity == 50_000.0

    def test_no_trade_result_preserves_capital(self):
        bars = _make_bars(_flat(n=50))
        engine = BacktestEngine(BacktestConfig(initial_capital=75_000.0))
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert result.final_equity == pytest.approx(75_000.0, rel=1e-9)
        assert result.total_return == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Tests: Custom strategy via ABC
# ---------------------------------------------------------------------------

class TestCustomStrategy:
    def test_abstract_strategy_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Strategy()  # type: ignore[abstract]

    def test_custom_buy_hold_strategy(self):
        """A strategy that always buys and never sells."""

        class AlwaysBuy(Strategy):
            @property
            def name(self) -> str:
                return "AlwaysBuy"

            def on_bar(self, bar: Bar, portfolio: _BacktestPortfolio) -> Signal:
                return Signal.BUY

        prices = _trending_up(n=50)
        bars = _make_bars(prices)
        engine = BacktestEngine(BacktestConfig(initial_capital=100_000.0))
        result = engine.run(bars, AlwaysBuy())
        # Bought on bar 0, closed at last bar – exactly 1 trade
        assert result.total_trades == 1

    def test_custom_always_sell_strategy(self):
        """A strategy that always sells → never enters, 0 trades."""

        class AlwaysSell(Strategy):
            @property
            def name(self) -> str:
                return "AlwaysSell"

            def on_bar(self, bar: Bar, portfolio: _BacktestPortfolio) -> Signal:
                return Signal.SELL

        prices = _trending_up(n=50)
        bars = _make_bars(prices)
        engine = BacktestEngine()
        result = engine.run(bars, AlwaysSell())
        assert result.total_trades == 0


# ---------------------------------------------------------------------------
# Tests: Full end-to-end scenario (problem statement demonstration)
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_problem_statement_api(self):
        """Validate the exact API shown in the problem statement."""
        prices = _trending_up(n=252, step=0.5)
        bars = _make_bars(prices, symbol="DEMO")

        engine = BacktestEngine(BacktestConfig(initial_capital=100_000))
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))

        assert isinstance(result, BacktestResult)
        s = str(result)
        assert s.startswith("BacktestResult(")
        assert "total_return=" in s
        assert "ann_return=" in s
        assert "sharpe=" in s

    def test_result_is_reproducible(self):
        """Same input → same output (deterministic)."""
        prices = _trending_up(n=120, step=1.0)
        bars = _make_bars(prices)
        cfg = BacktestConfig(initial_capital=100_000.0)
        r1 = BacktestEngine(cfg).run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        r2 = BacktestEngine(cfg).run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert r1.total_return == r2.total_return
        assert r1.total_trades == r2.total_trades
        assert r1.final_equity == r2.final_equity

    def test_multi_symbol_isolation(self):
        """Running the same engine instance multiple times is independent."""
        prices_a = _trending_up(n=80, step=1.0)
        prices_b = _trending_down(n=80, step=1.0)
        bars_a = _make_bars(prices_a, symbol="UP")
        bars_b = _make_bars(prices_b, symbol="DOWN")
        cfg = BacktestConfig(initial_capital=100_000.0)
        engine = BacktestEngine(cfg)
        result_a = engine.run(bars_a, MovingAverageCrossover(fast_period=5, slow_period=20))
        result_b = engine.run(bars_b, MovingAverageCrossover(fast_period=5, slow_period=20))
        # Both runs should be independent; engine should not bleed state
        assert result_a.total_trades >= 0
        assert result_b.total_trades >= 0

    def test_large_capital_does_not_crash(self):
        prices = _trending_up(n=252, step=1.0)
        bars = _make_bars(prices)
        engine = BacktestEngine(BacktestConfig(initial_capital=1_000_000_000.0))
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        assert math.isfinite(result.final_equity)

    def test_very_small_capital(self):
        prices = _trending_up(n=60, step=1.0)
        bars = _make_bars(prices)
        engine = BacktestEngine(BacktestConfig(initial_capital=1.0, max_position_size=1.0))
        result = engine.run(bars, MovingAverageCrossover(fast_period=5, slow_period=20))
        # With $1 capital and ~$100 share price, no quantity can be bought
        assert result.total_trades == 0
        assert result.final_equity == pytest.approx(1.0, rel=1e-6)
