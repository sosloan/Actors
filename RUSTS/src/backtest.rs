//! Backtest Engine for ACTORS Financial Intelligence Platform
//!
//! Provides a complete event-driven backtesting framework:
//! - [`HistoricalBar`]    – OHLCV price bar
//! - [`BacktestConfig`]   – simulation parameters
//! - [`Signal`]           – buy / sell / hold action from a strategy
//! - [`Trade`]            – completed round-trip trade record
//! - [`BacktestResult`]   – performance metrics after a simulation run
//! - [`BacktestPortfolio`]– internal portfolio state during simulation
//! - [`BacktestEngine`]   – main simulation driver
//! - [`Strategy`]         – pluggable strategy trait
//! - Example strategies: [`MovingAverageCrossover`], [`MomentumStrategy`]

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

// ── Data structures ────────────────────────────────────────────────────────────

/// A single OHLCV price bar.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HistoricalBar {
    pub timestamp: DateTime<Utc>,
    pub symbol: String,
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
    pub volume: f64,
}

/// Configuration for a backtest run.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BacktestConfig {
    /// Starting cash balance.
    pub initial_capital: f64,
    /// Fractional commission per trade (e.g. `0.001` = 0.1 %).
    pub commission_rate: f64,
    /// Fractional slippage per fill (e.g. `0.0005` = 0.05 %).
    pub slippage_rate: f64,
    /// Maximum fraction of capital risked per trade (e.g. `0.02` = 2 %).
    pub max_position_size: f64,
}

impl Default for BacktestConfig {
    fn default() -> Self {
        Self {
            initial_capital: 100_000.0,
            commission_rate: 0.001,
            slippage_rate: 0.0005,
            max_position_size: 0.10,
        }
    }
}

/// Action produced by a strategy for a given bar.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Signal {
    Buy,
    Sell,
    Hold,
}

/// A completed round-trip trade (entry → exit).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Trade {
    pub symbol: String,
    pub entry_time: DateTime<Utc>,
    pub exit_time: DateTime<Utc>,
    pub entry_price: f64,
    pub exit_price: f64,
    pub quantity: f64,
    pub pnl: f64,
    pub return_pct: f64,
}

/// Performance metrics produced after a full simulation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BacktestResult {
    pub total_return: f64,
    pub annualized_return: f64,
    pub sharpe_ratio: f64,
    pub max_drawdown: f64,
    pub win_rate: f64,
    pub total_trades: usize,
    pub winning_trades: usize,
    pub losing_trades: usize,
    pub profit_factor: f64,
    pub final_equity: f64,
    pub equity_curve: Vec<(DateTime<Utc>, f64)>,
    pub trades: Vec<Trade>,
}

// ── Portfolio state ────────────────────────────────────────────────────────────

/// Tracks cash, open position, and equity during a simulation.
pub struct BacktestPortfolio {
    pub cash: f64,
    pub position_quantity: f64,
    pub position_entry_price: f64,
    pub position_entry_time: Option<DateTime<Utc>>,
    pub symbol: String,
}

impl BacktestPortfolio {
    /// Create a new portfolio with the given starting cash for `symbol`.
    pub fn new(initial_capital: f64, symbol: String) -> Self {
        Self {
            cash: initial_capital,
            position_quantity: 0.0,
            position_entry_price: 0.0,
            position_entry_time: None,
            symbol,
        }
    }

    /// Current market value of the open position.
    pub fn position_value(&self, current_price: f64) -> f64 {
        self.position_quantity * current_price
    }

    /// Total portfolio equity (cash + open position value).
    pub fn equity(&self, current_price: f64) -> f64 {
        self.cash + self.position_value(current_price)
    }

    /// Return `true` when the portfolio holds a long position.
    pub fn is_long(&self) -> bool {
        self.position_quantity > 0.0
    }
}

// ── Strategy trait ─────────────────────────────────────────────────────────────

/// A trading strategy that produces a [`Signal`] for each incoming bar.
///
/// Implement this trait to plug custom strategies into [`BacktestEngine`].
pub trait Strategy {
    /// Called once for every bar in chronological order.
    /// Returns the desired action (buy / sell / hold).
    fn on_bar(&mut self, bar: &HistoricalBar, portfolio: &BacktestPortfolio) -> Signal;

    /// Human-readable name of the strategy (used in reports).
    fn name(&self) -> &str;
}

// ── Backtest engine ────────────────────────────────────────────────────────────

/// Event-driven backtesting engine.
pub struct BacktestEngine {
    config: BacktestConfig,
}

impl BacktestEngine {
    /// Create a new engine with the supplied configuration.
    pub fn new(config: BacktestConfig) -> Self {
        Self { config }
    }

    /// Run a simulation over `bars` using the supplied `strategy`.
    ///
    /// Bars must be sorted in ascending chronological order.
    /// Returns a [`BacktestResult`] with full performance metrics.
    pub fn run(&self, bars: &[HistoricalBar], strategy: &mut dyn Strategy) -> BacktestResult {
        if bars.is_empty() {
            return self.empty_result();
        }

        let symbol = bars[0].symbol.clone();
        let mut portfolio = BacktestPortfolio::new(self.config.initial_capital, symbol);
        let mut equity_curve: Vec<(DateTime<Utc>, f64)> = Vec::with_capacity(bars.len());
        let mut completed_trades: Vec<Trade> = Vec::new();

        for bar in bars {
            let signal = strategy.on_bar(bar, &portfolio);

            match signal {
                Signal::Buy if !portfolio.is_long() => {
                    self.execute_buy(bar, &mut portfolio);
                }
                Signal::Sell if portfolio.is_long() => {
                    if let Some(trade) = self.execute_sell(bar, &mut portfolio) {
                        completed_trades.push(trade);
                    }
                }
                _ => {}
            }

            equity_curve.push((bar.timestamp, portfolio.equity(bar.close)));
        }

        // Close any remaining open position at the last bar's close.
        if portfolio.is_long() {
            let last_bar = bars.last().unwrap();
            if let Some(trade) = self.execute_sell(last_bar, &mut portfolio) {
                completed_trades.push(trade);
            }
        }

        self.calculate_results(
            portfolio.equity(bars.last().unwrap().close),
            &equity_curve,
            &completed_trades,
            bars,
        )
    }

    // ── private helpers ──────────────────────────────────────────────────────

    fn execute_buy(&self, bar: &HistoricalBar, portfolio: &mut BacktestPortfolio) {
        let fill_price = bar.close * (1.0 + self.config.slippage_rate);
        let capital_at_risk = portfolio.cash * self.config.max_position_size;
        let quantity = (capital_at_risk / fill_price).floor();
        if quantity <= 0.0 {
            return;
        }
        let cost = quantity * fill_price * (1.0 + self.config.commission_rate);
        if cost > portfolio.cash {
            return;
        }
        portfolio.cash -= cost;
        portfolio.position_quantity = quantity;
        portfolio.position_entry_price = fill_price;
        portfolio.position_entry_time = Some(bar.timestamp);
    }

    fn execute_sell(&self, bar: &HistoricalBar, portfolio: &mut BacktestPortfolio) -> Option<Trade> {
        if portfolio.position_quantity <= 0.0 {
            return None;
        }
        let fill_price = bar.close * (1.0 - self.config.slippage_rate);
        let proceeds = portfolio.position_quantity * fill_price * (1.0 - self.config.commission_rate);
        let cost_basis = portfolio.position_quantity * portfolio.position_entry_price;
        let pnl = proceeds - cost_basis;
        let return_pct = if cost_basis > 0.0 { pnl / cost_basis } else { 0.0 };

        let trade = Trade {
            symbol: portfolio.symbol.clone(),
            entry_time: portfolio.position_entry_time.unwrap_or(bar.timestamp),
            exit_time: bar.timestamp,
            entry_price: portfolio.position_entry_price,
            exit_price: fill_price,
            quantity: portfolio.position_quantity,
            pnl,
            return_pct,
        };

        portfolio.cash += proceeds;
        portfolio.position_quantity = 0.0;
        portfolio.position_entry_price = 0.0;
        portfolio.position_entry_time = None;

        Some(trade)
    }

    fn calculate_results(
        &self,
        final_equity: f64,
        equity_curve: &[(DateTime<Utc>, f64)],
        trades: &[Trade],
        bars: &[HistoricalBar],
    ) -> BacktestResult {
        let total_return = (final_equity - self.config.initial_capital) / self.config.initial_capital;

        // Annualised return: use trading days as a proxy (≈252 days/year).
        let trading_days = bars.len() as f64;
        let years = trading_days / 252.0;
        let annualized_return = if years > 0.0 {
            (1.0 + total_return).powf(1.0 / years) - 1.0
        } else {
            0.0
        };

        // Daily returns for Sharpe calculation.
        let daily_returns: Vec<f64> = equity_curve
            .windows(2)
            .map(|w| (w[1].1 - w[0].1) / w[0].1)
            .collect();

        let sharpe_ratio = self.calculate_sharpe(&daily_returns);
        let max_drawdown = self.calculate_max_drawdown(equity_curve);

        let winning_trades = trades.iter().filter(|t| t.pnl > 0.0).count();
        let losing_trades = trades.iter().filter(|t| t.pnl <= 0.0).count();
        let win_rate = if !trades.is_empty() {
            winning_trades as f64 / trades.len() as f64
        } else {
            0.0
        };

        let gross_profit: f64 = trades.iter().filter(|t| t.pnl > 0.0).map(|t| t.pnl).sum();
        let gross_loss: f64 = trades.iter().filter(|t| t.pnl < 0.0).map(|t| t.pnl.abs()).sum();
        let profit_factor = if gross_loss > 0.0 { gross_profit / gross_loss } else { f64::INFINITY };

        BacktestResult {
            total_return,
            annualized_return,
            sharpe_ratio,
            max_drawdown,
            win_rate,
            total_trades: trades.len(),
            winning_trades,
            losing_trades,
            profit_factor,
            final_equity,
            equity_curve: equity_curve.to_vec(),
            trades: trades.to_vec(),
        }
    }

    fn calculate_sharpe(&self, daily_returns: &[f64]) -> f64 {
        if daily_returns.len() < 2 {
            return 0.0;
        }
        let mean = daily_returns.iter().sum::<f64>() / daily_returns.len() as f64;
        let variance = daily_returns
            .iter()
            .map(|r| (r - mean).powi(2))
            .sum::<f64>()
            / (daily_returns.len() - 1) as f64;
        let std_dev = variance.sqrt();
        if std_dev == 0.0 {
            return 0.0;
        }
        // Risk-free rate ≈ 0 for daily returns; annualise by √252.
        (mean / std_dev) * 252_f64.sqrt()
    }

    fn calculate_max_drawdown(&self, equity_curve: &[(DateTime<Utc>, f64)]) -> f64 {
        if equity_curve.is_empty() {
            return 0.0;
        }
        let mut peak = equity_curve[0].1;
        let mut max_dd = 0.0_f64;
        for (_, equity) in equity_curve {
            if *equity > peak {
                peak = *equity;
            }
            let dd = (peak - equity) / peak;
            if dd > max_dd {
                max_dd = dd;
            }
        }
        max_dd
    }

    fn empty_result(&self) -> BacktestResult {
        BacktestResult {
            total_return: 0.0,
            annualized_return: 0.0,
            sharpe_ratio: 0.0,
            max_drawdown: 0.0,
            win_rate: 0.0,
            total_trades: 0,
            winning_trades: 0,
            losing_trades: 0,
            profit_factor: 0.0,
            final_equity: self.config.initial_capital,
            equity_curve: Vec::new(),
            trades: Vec::new(),
        }
    }
}

// ── Bundled strategies ─────────────────────────────────────────────────────────

/// Dual simple-moving-average crossover strategy.
///
/// Generates a [`Signal::Buy`] when the fast SMA crosses above the slow SMA and
/// a [`Signal::Sell`] when it crosses below.
pub struct MovingAverageCrossover {
    fast_period: usize,
    slow_period: usize,
    fast_prices: VecDeque<f64>,
    slow_prices: VecDeque<f64>,
    prev_fast_sma: Option<f64>,
    prev_slow_sma: Option<f64>,
}

impl MovingAverageCrossover {
    /// Create a new MA crossover strategy.
    ///
    /// # Panics
    /// Panics if `fast_period >= slow_period` or if either period is zero.
    pub fn new(fast_period: usize, slow_period: usize) -> Self {
        assert!(fast_period > 0, "fast_period must be > 0");
        assert!(slow_period > fast_period, "slow_period must be > fast_period");
        Self {
            fast_period,
            slow_period,
            fast_prices: VecDeque::with_capacity(slow_period),
            slow_prices: VecDeque::with_capacity(slow_period),
            prev_fast_sma: None,
            prev_slow_sma: None,
        }
    }

    fn sma(prices: &VecDeque<f64>, period: usize) -> Option<f64> {
        if prices.len() < period {
            return None;
        }
        let sum: f64 = prices.iter().rev().take(period).sum();
        Some(sum / period as f64)
    }
}

impl Strategy for MovingAverageCrossover {
    fn name(&self) -> &str {
        "MovingAverageCrossover"
    }

    fn on_bar(&mut self, bar: &HistoricalBar, _portfolio: &BacktestPortfolio) -> Signal {
        self.fast_prices.push_back(bar.close);
        self.slow_prices.push_back(bar.close);
        if self.fast_prices.len() > self.slow_period {
            self.fast_prices.pop_front();
        }
        if self.slow_prices.len() > self.slow_period {
            self.slow_prices.pop_front();
        }

        let fast_sma = Self::sma(&self.fast_prices, self.fast_period);
        let slow_sma = Self::sma(&self.slow_prices, self.slow_period);

        let signal = match (fast_sma, slow_sma, self.prev_fast_sma, self.prev_slow_sma) {
            (Some(f), Some(s), Some(pf), Some(ps)) => {
                if pf <= ps && f > s {
                    Signal::Buy
                } else if pf >= ps && f < s {
                    Signal::Sell
                } else {
                    Signal::Hold
                }
            }
            _ => Signal::Hold,
        };

        self.prev_fast_sma = fast_sma;
        self.prev_slow_sma = slow_sma;
        signal
    }
}

/// Rate-of-change momentum strategy.
///
/// Buys when the `lookback`-bar return exceeds `threshold` and sells when it
/// falls below `-threshold`.
pub struct MomentumStrategy {
    lookback: usize,
    threshold: f64,
    price_history: VecDeque<f64>,
}

impl MomentumStrategy {
    /// Create a new momentum strategy.
    pub fn new(lookback: usize, threshold: f64) -> Self {
        assert!(lookback > 0, "lookback must be > 0");
        Self {
            lookback,
            threshold,
            price_history: VecDeque::with_capacity(lookback + 1),
        }
    }
}

impl Strategy for MomentumStrategy {
    fn name(&self) -> &str {
        "MomentumStrategy"
    }

    fn on_bar(&mut self, bar: &HistoricalBar, _portfolio: &BacktestPortfolio) -> Signal {
        self.price_history.push_back(bar.close);
        if self.price_history.len() > self.lookback + 1 {
            self.price_history.pop_front();
        }

        if self.price_history.len() <= self.lookback {
            return Signal::Hold;
        }

        let oldest = self.price_history.front().copied().unwrap_or(0.0);
        if oldest == 0.0 {
            return Signal::Hold;
        }
        let momentum = (bar.close - oldest) / oldest;

        if momentum > self.threshold {
            Signal::Buy
        } else if momentum < -self.threshold {
            Signal::Sell
        } else {
            Signal::Hold
        }
    }
}

// ── Tests ──────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;

    fn make_bars(prices: &[f64]) -> Vec<HistoricalBar> {
        prices
            .iter()
            .enumerate()
            .map(|(i, &p)| HistoricalBar {
                timestamp: Utc.timestamp_opt(1_700_000_000 + i as i64 * 86_400, 0).unwrap(),
                symbol: "TEST".to_string(),
                open: p,
                high: p * 1.01,
                low: p * 0.99,
                close: p,
                volume: 1_000_000.0,
            })
            .collect()
    }

    // ── BacktestEngine basics ─────────────────────────────────────────────────

    #[test]
    fn test_empty_bars_returns_default_result() {
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MovingAverageCrossover::new(5, 20);
        let result = engine.run(&[], &mut strategy);
        assert_eq!(result.total_return, 0.0);
        assert_eq!(result.total_trades, 0);
        assert_eq!(result.final_equity, BacktestConfig::default().initial_capital);
    }

    #[test]
    fn test_equity_curve_length_matches_bars() {
        let prices: Vec<f64> = (1..=50).map(|i| 100.0 + i as f64).collect();
        let bars = make_bars(&prices);
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MovingAverageCrossover::new(5, 20);
        let result = engine.run(&bars, &mut strategy);
        assert_eq!(result.equity_curve.len(), bars.len());
    }

    #[test]
    fn test_final_equity_is_non_negative() {
        let prices: Vec<f64> = (1..=100).map(|i| 100.0 + (i as f64).sin() * 10.0).collect();
        let bars = make_bars(&prices);
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MomentumStrategy::new(10, 0.02);
        let result = engine.run(&bars, &mut strategy);
        assert!(result.final_equity >= 0.0);
    }

    #[test]
    fn test_win_rate_in_valid_range() {
        let prices: Vec<f64> = (1..=100).map(|i| 100.0 + i as f64 * 0.5).collect();
        let bars = make_bars(&prices);
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MovingAverageCrossover::new(5, 20);
        let result = engine.run(&bars, &mut strategy);
        assert!(result.win_rate >= 0.0 && result.win_rate <= 1.0);
    }

    #[test]
    fn test_trade_counts_are_consistent() {
        let prices: Vec<f64> = (1..=120).map(|i| {
            100.0 + (i as f64 * 0.1).sin() * 15.0
        }).collect();
        let bars = make_bars(&prices);
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MovingAverageCrossover::new(5, 20);
        let result = engine.run(&bars, &mut strategy);
        assert_eq!(result.winning_trades + result.losing_trades, result.total_trades);
        assert_eq!(result.trades.len(), result.total_trades);
    }

    #[test]
    fn test_max_drawdown_non_negative() {
        let prices: Vec<f64> = vec![
            100.0, 110.0, 105.0, 95.0, 98.0, 92.0, 100.0, 108.0, 102.0, 115.0,
        ];
        let bars = make_bars(&prices);
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MomentumStrategy::new(3, 0.01);
        let result = engine.run(&bars, &mut strategy);
        assert!(result.max_drawdown >= 0.0 && result.max_drawdown <= 1.0);
    }

    #[test]
    fn test_profit_factor_positive_on_winning_strategy() {
        // Steadily rising prices → all trades should be winners.
        let prices: Vec<f64> = (1..=200).map(|i| 50.0 + i as f64).collect();
        let bars = make_bars(&prices);
        let engine = BacktestEngine::new(BacktestConfig::default());
        let mut strategy = MovingAverageCrossover::new(5, 20);
        let result = engine.run(&bars, &mut strategy);
        if result.total_trades > 0 && result.losing_trades == 0 {
            assert!(result.profit_factor.is_infinite() || result.profit_factor > 1.0);
        }
    }

    // ── MovingAverageCrossover ────────────────────────────────────────────────

    #[test]
    fn test_ma_crossover_hold_before_warmup() {
        let mut strategy = MovingAverageCrossover::new(3, 5);
        let portfolio = BacktestPortfolio::new(100_000.0, "TEST".to_string());
        let bar = HistoricalBar {
            timestamp: Utc::now(),
            symbol: "TEST".to_string(),
            open: 100.0,
            high: 101.0,
            low: 99.0,
            close: 100.0,
            volume: 1_000.0,
        };
        // Before enough bars arrive the strategy must emit Hold.
        let signal = strategy.on_bar(&bar, &portfolio);
        assert_eq!(signal, Signal::Hold);
    }

    #[test]
    fn test_ma_crossover_name() {
        let strategy = MovingAverageCrossover::new(5, 20);
        assert_eq!(strategy.name(), "MovingAverageCrossover");
    }

    // ── MomentumStrategy ─────────────────────────────────────────────────────

    #[test]
    fn test_momentum_hold_during_warmup() {
        let mut strategy = MomentumStrategy::new(5, 0.02);
        let portfolio = BacktestPortfolio::new(100_000.0, "TEST".to_string());
        for price in &[100.0, 101.0, 102.0, 103.0] {
            let bar = HistoricalBar {
                timestamp: Utc::now(),
                symbol: "TEST".to_string(),
                open: *price,
                high: price * 1.01,
                low: price * 0.99,
                close: *price,
                volume: 1_000.0,
            };
            assert_eq!(strategy.on_bar(&bar, &portfolio), Signal::Hold);
        }
    }

    #[test]
    fn test_momentum_buy_on_strong_rise() {
        let mut strategy = MomentumStrategy::new(2, 0.05);
        let portfolio = BacktestPortfolio::new(100_000.0, "TEST".to_string());
        let make_bar = |price: f64| HistoricalBar {
            timestamp: Utc::now(),
            symbol: "TEST".to_string(),
            open: price,
            high: price * 1.01,
            low: price * 0.99,
            close: price,
            volume: 1_000.0,
        };
        // Seed two warmup bars.
        strategy.on_bar(&make_bar(100.0), &portfolio);
        strategy.on_bar(&make_bar(101.0), &portfolio);
        // Third bar is +20 % above the oldest → should produce Buy.
        let signal = strategy.on_bar(&make_bar(120.0), &portfolio);
        assert_eq!(signal, Signal::Buy);
    }

    #[test]
    fn test_momentum_sell_on_strong_drop() {
        let mut strategy = MomentumStrategy::new(2, 0.05);
        let portfolio = BacktestPortfolio::new(100_000.0, "TEST".to_string());
        let make_bar = |price: f64| HistoricalBar {
            timestamp: Utc::now(),
            symbol: "TEST".to_string(),
            open: price,
            high: price * 1.01,
            low: price * 0.99,
            close: price,
            volume: 1_000.0,
        };
        strategy.on_bar(&make_bar(120.0), &portfolio);
        strategy.on_bar(&make_bar(119.0), &portfolio);
        // −20 % move → should produce Sell.
        let signal = strategy.on_bar(&make_bar(96.0), &portfolio);
        assert_eq!(signal, Signal::Sell);
    }

    #[test]
    fn test_momentum_name() {
        let strategy = MomentumStrategy::new(10, 0.02);
        assert_eq!(strategy.name(), "MomentumStrategy");
    }

    // ── BacktestPortfolio ────────────────────────────────────────────────────

    #[test]
    fn test_portfolio_equity_with_no_position() {
        let p = BacktestPortfolio::new(50_000.0, "AAPL".to_string());
        assert_eq!(p.equity(200.0), 50_000.0);
        assert!(!p.is_long());
    }

    #[test]
    fn test_portfolio_equity_with_open_position() {
        let mut p = BacktestPortfolio::new(90_000.0, "AAPL".to_string());
        p.position_quantity = 100.0;
        p.cash = 80_000.0;
        assert_eq!(p.equity(100.0), 90_000.0);
        assert!(p.is_long());
    }
}
