//! ACTORS Rust Performance Components
//! 
//! High-performance Rust components for the ACTORS financial intelligence platform.
//! This module provides optimized implementations for financial calculations,
//! data processing, and ML pipeline components.

pub mod backtest;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use uuid::Uuid;

/// Financial instrument types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum InstrumentType {
    Stock,
    Option,
    Future,
    Bond,
    Crypto,
    Forex,
}

/// Order side
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OrderSide {
    Buy,
    Sell,
}

/// Order type
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum OrderType {
    Market,
    Limit,
    Stop,
    StopLimit,
}

/// Financial order representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Order {
    pub id: Uuid,
    pub symbol: String,
    pub instrument_type: InstrumentType,
    pub side: OrderSide,
    pub order_type: OrderType,
    pub quantity: f64,
    pub price: Option<f64>,
    pub stop_price: Option<f64>,
    pub account_id: String,
    pub created_at: DateTime<Utc>,
    pub expires_at: Option<DateTime<Utc>>,
}

/// Position in a financial instrument
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Position {
    pub id: Uuid,
    pub account_id: String,
    pub symbol: String,
    pub instrument_type: InstrumentType,
    pub quantity: f64,
    pub average_price: f64,
    pub current_price: f64,
    pub market_value: f64,
    pub unrealized_pnl: f64,
    pub last_updated: DateTime<Utc>,
}

/// Portfolio representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Portfolio {
    pub id: Uuid,
    pub account_id: String,
    pub positions: HashMap<String, Position>,
    pub total_value: f64,
    pub total_pnl: f64,
    pub last_updated: DateTime<Utc>,
}

/// Risk metrics for a position or portfolio
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RiskMetrics {
    pub var_95: f64,        // Value at Risk (95% confidence)
    pub var_99: f64,        // Value at Risk (99% confidence)
    pub expected_shortfall: f64,
    pub volatility: f64,
    pub beta: f64,
    pub sharpe_ratio: f64,
    pub max_drawdown: f64,
}

/// Financial calculation engine
pub struct FinancialEngine {
    risk_free_rate: f64,
}

impl FinancialEngine {
    /// Create a new financial engine
    pub fn new(risk_free_rate: f64) -> Self {
        Self { risk_free_rate }
    }
    
    /// Calculate portfolio value
    pub fn calculate_portfolio_value(&self, positions: &[Position]) -> f64 {
        positions.iter().map(|pos| pos.market_value).sum()
    }
    
    /// Calculate portfolio PnL
    pub fn calculate_portfolio_pnl(&self, positions: &[Position]) -> f64 {
        positions.iter().map(|pos| pos.unrealized_pnl).sum()
    }
    
    /// Calculate position weight in portfolio
    pub fn calculate_position_weight(&self, position: &Position, total_value: f64) -> f64 {
        if total_value == 0.0 {
            0.0
        } else {
            position.market_value / total_value
        }
    }
    
    /// Calculate Sharpe ratio
    pub fn calculate_sharpe_ratio(&self, returns: &[f64], volatility: f64) -> f64 {
        if volatility == 0.0 {
            0.0
        } else {
            let avg_return = returns.iter().sum::<f64>() / returns.len() as f64;
            (avg_return - self.risk_free_rate) / volatility
        }
    }
    
    /// Calculate Value at Risk (VaR)
    pub fn calculate_var(&self, returns: &[f64], confidence_level: f64) -> f64 {
        if returns.is_empty() {
            return 0.0;
        }
        
        let mut sorted_returns = returns.to_vec();
        sorted_returns.sort_by(|a, b| a.partial_cmp(b).unwrap());
        
        let index = ((1.0 - confidence_level) * returns.len() as f64) as usize;
        let clamped_index = index.min(returns.len() - 1);
        
        -sorted_returns[clamped_index]
    }
    
    /// Calculate volatility (standard deviation of returns)
    pub fn calculate_volatility(&self, returns: &[f64]) -> f64 {
        if returns.len() < 2 {
            return 0.0;
        }
        
        let mean = returns.iter().sum::<f64>() / returns.len() as f64;
        let variance = returns.iter()
            .map(|r| (r - mean).powi(2))
            .sum::<f64>() / (returns.len() - 1) as f64;
        
        variance.sqrt()
    }
}

/// ML Pipeline component for financial data processing
pub struct MLPipeline {
    model_version: String,
    features: Vec<String>,
}

impl MLPipeline {
    /// Create a new ML pipeline
    pub fn new(model_version: String, features: Vec<String>) -> Self {
        Self {
            model_version,
            features,
        }
    }
    
    /// Process financial data for ML training
    pub fn process_training_data(&self, data: &[HashMap<String, f64>]) -> Result<Vec<Vec<f64>>, String> {
        if data.is_empty() {
            return Err("No data provided".to_string());
        }
        
        let mut processed_data = Vec::new();
        
        for record in data {
            let mut features = Vec::new();
            
            for feature in &self.features {
                match record.get(feature) {
                    Some(value) => features.push(*value),
                    None => return Err(format!("Missing feature: {}", feature)),
                }
            }
            
            processed_data.push(features);
        }
        
        Ok(processed_data)
    }
    
    /// Generate predictions (mock implementation)
    pub fn predict(&self, features: &[f64]) -> Result<f64, String> {
        if features.len() != self.features.len() {
            return Err("Feature count mismatch".to_string());
        }
        
        // Mock prediction - in real implementation, this would use a trained model
        let prediction = features.iter().sum::<f64>() / features.len() as f64;
        Ok(prediction)
    }
    
    /// Calculate feature importance (mock implementation)
    pub fn get_feature_importance(&self) -> HashMap<String, f64> {
        let mut importance = HashMap::new();
        
        for (i, feature) in self.features.iter().enumerate() {
            // Mock importance - in real implementation, this would come from the model
            importance.insert(feature.clone(), 1.0 / (i + 1) as f64);
        }
        
        importance
    }
}

/// Performance metrics for the system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub processing_time_ms: u64,
    pub memory_usage_mb: f64,
    pub cpu_usage_percent: f64,
    pub throughput_ops_per_sec: f64,
    pub error_rate: f64,
    pub timestamp: DateTime<Utc>,
}

/// System monitor for performance tracking
pub struct SystemMonitor {
    metrics_history: Vec<PerformanceMetrics>,
    max_history_size: usize,
}

impl SystemMonitor {
    /// Create a new system monitor
    pub fn new(max_history_size: usize) -> Self {
        Self {
            metrics_history: Vec::new(),
            max_history_size,
        }
    }
    
    /// Record performance metrics
    pub fn record_metrics(&mut self, metrics: PerformanceMetrics) {
        self.metrics_history.push(metrics);
        
        if self.metrics_history.len() > self.max_history_size {
            self.metrics_history.remove(0);
        }
    }
    
    /// Get average performance metrics
    pub fn get_average_metrics(&self) -> Option<PerformanceMetrics> {
        if self.metrics_history.is_empty() {
            return None;
        }
        
        let count = self.metrics_history.len() as f64;
        
        let avg_processing_time = self.metrics_history.iter()
            .map(|m| m.processing_time_ms as f64)
            .sum::<f64>() / count;
        
        let avg_memory = self.metrics_history.iter()
            .map(|m| m.memory_usage_mb)
            .sum::<f64>() / count;
        
        let avg_cpu = self.metrics_history.iter()
            .map(|m| m.cpu_usage_percent)
            .sum::<f64>() / count;
        
        let avg_throughput = self.metrics_history.iter()
            .map(|m| m.throughput_ops_per_sec)
            .sum::<f64>() / count;
        
        let avg_error_rate = self.metrics_history.iter()
            .map(|m| m.error_rate)
            .sum::<f64>() / count;
        
        Some(PerformanceMetrics {
            processing_time_ms: avg_processing_time as u64,
            memory_usage_mb: avg_memory,
            cpu_usage_percent: avg_cpu,
            throughput_ops_per_sec: avg_throughput,
            error_rate: avg_error_rate,
            timestamp: Utc::now(),
        })
    }
    
    /// Get latest metrics
    pub fn get_latest_metrics(&self) -> Option<&PerformanceMetrics> {
        self.metrics_history.last()
    }
}

// ── AI-Driven Investment Strategy Module ──────────────────────────────────────
//
// Extends the FinancialEngine with Modern Portfolio Theory, Kelly Criterion
// position sizing, advanced risk metrics, and a portfolio rebalancing engine.

/// Portfolio optimisation objective
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum OptimisationObjective {
    MaximiseSharpe,
    MinimiseVariance,
    MaximiseReturn,
    RiskParity,
    KellyCriterion,
}

/// Target allocation for a single asset produced by the optimiser
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssetAllocation {
    pub symbol: String,
    pub target_weight: f64,
    pub expected_return: f64,
    pub volatility: f64,
    pub risk_contribution: f64,
}

/// Full result from a portfolio optimisation run
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioOptimisationResult {
    pub objective: OptimisationObjective,
    pub allocations: Vec<AssetAllocation>,
    pub expected_portfolio_return: f64,
    pub expected_portfolio_volatility: f64,
    pub sharpe_ratio: f64,
    pub sortino_ratio: f64,
    pub diversification_ratio: f64,
    pub iterations: usize,
}

/// Rebalancing order computed from current vs. target weights
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RebalanceOrder {
    pub symbol: String,
    pub action: String,          // "buy", "sell", "hold"
    pub current_weight: f64,
    pub target_weight: f64,
    pub drift: f64,
    pub estimated_trade_value: f64,
}

/// AI-driven portfolio optimiser using gradient-based methods.
///
/// All inputs are annualised.  The optimiser does not require an external
/// solver; it uses projected-gradient ascent / descent on a simplex.
pub struct PortfolioOptimiser {
    pub risk_free_rate: f64,
}

impl PortfolioOptimiser {
    /// Create a new optimiser with the given annualised risk-free rate.
    pub fn new(risk_free_rate: f64) -> Self {
        Self { risk_free_rate }
    }

    /// Optimise portfolio weights for `symbols` given annualised expected
    /// returns `mu` (length N) and covariance matrix `cov` (N×N, row-major).
    ///
    /// Returns `None` if inputs are inconsistent.
    pub fn optimise(
        &self,
        symbols: &[String],
        mu: &[f64],
        cov: &[Vec<f64>],
        objective: OptimisationObjective,
        min_weight: f64,
        max_weight: f64,
    ) -> Option<PortfolioOptimisationResult> {
        let n = symbols.len();
        if n == 0 || mu.len() != n || cov.len() != n {
            return None;
        }

        let (weights, iters) = match objective {
            OptimisationObjective::MaximiseSharpe => {
                self.maximise_sharpe(mu, cov, min_weight, max_weight, n)
            }
            OptimisationObjective::MinimiseVariance => {
                self.minimise_variance(cov, min_weight, max_weight, n)
            }
            OptimisationObjective::RiskParity => {
                self.risk_parity(cov, min_weight, max_weight, n)
            }
            OptimisationObjective::KellyCriterion => {
                self.kelly_portfolio(mu, cov, min_weight, max_weight, n)
            }
            OptimisationObjective::MaximiseReturn => {
                self.maximise_return(mu, min_weight, max_weight, n)
            }
        };

        let port_return = dot(&weights, mu);
        let port_var = portfolio_variance(&weights, cov);
        let port_vol = port_var.sqrt().max(1e-12);
        let sharpe = (port_return - self.risk_free_rate) / port_vol;
        let sortino = self.sortino_from_vol(port_return, port_vol);
        let div_ratio = self.diversification_ratio(&weights, cov);

        let vols: Vec<f64> = (0..n).map(|i| cov[i][i].sqrt()).collect();
        let risk_contributions: Vec<f64> = (0..n)
            .map(|i| {
                let mrc = marginal_risk_contribution(&weights, cov, i);
                weights[i] * mrc / port_vol
            })
            .collect();

        let allocations = symbols
            .iter()
            .enumerate()
            .map(|(i, sym)| AssetAllocation {
                symbol: sym.clone(),
                target_weight: weights[i],
                expected_return: mu[i],
                volatility: vols[i],
                risk_contribution: risk_contributions[i],
            })
            .collect();

        Some(PortfolioOptimisationResult {
            objective,
            allocations,
            expected_portfolio_return: port_return,
            expected_portfolio_volatility: port_vol,
            sharpe_ratio: sharpe,
            sortino_ratio: sortino,
            diversification_ratio: div_ratio,
            iterations: iters,
        })
    }

    // ── Optimisation algorithms ──────────────────────────────────────────────

    fn maximise_sharpe(
        &self, mu: &[f64], cov: &[Vec<f64>],
        lo: f64, hi: f64, n: usize,
    ) -> (Vec<f64>, usize) {
        let mut w = uniform_weights(n);
        let lr = 1e-3_f64;
        let tol = 1e-9_f64;

        for iter in 0..1000 {
            let port_vol = portfolio_variance(&w, cov).sqrt().max(1e-12);
            let excess = dot(&w, mu) - self.risk_free_rate;
            let grad: Vec<f64> = (0..n)
                .map(|i| {
                    let mrc = marginal_risk_contribution(&w, cov, i);
                    (mu[i] * port_vol - excess * mrc) / (port_vol * port_vol)
                })
                .collect();

            let w_new: Vec<f64> = w.iter().zip(&grad).map(|(wi, gi)| wi + lr * gi).collect();
            let w_new = project_simplex(w_new, lo, hi);

            let delta: f64 = w_new.iter().zip(&w).map(|(a, b)| (a - b).powi(2)).sum::<f64>().sqrt();
            w = w_new;
            if delta < tol {
                return (w, iter + 1);
            }
        }
        (w, 1000)
    }

    fn minimise_variance(
        &self, cov: &[Vec<f64>], lo: f64, hi: f64, n: usize,
    ) -> (Vec<f64>, usize) {
        let mut w = uniform_weights(n);
        let lr = 5e-4_f64;
        let tol = 1e-10_f64;

        for iter in 0..1000 {
            let grad: Vec<f64> = (0..n)
                .map(|i| 2.0 * marginal_risk_contribution(&w, cov, i))
                .collect();
            let w_new = project_simplex(
                w.iter().zip(&grad).map(|(wi, gi)| wi - lr * gi).collect(),
                lo, hi,
            );
            let delta: f64 = w_new.iter().zip(&w).map(|(a, b)| (a - b).powi(2)).sum::<f64>().sqrt();
            w = w_new;
            if delta < tol {
                return (w, iter + 1);
            }
        }
        (w, 1000)
    }

    fn risk_parity(
        &self, cov: &[Vec<f64>], lo: f64, hi: f64, n: usize,
    ) -> (Vec<f64>, usize) {
        let mut w = uniform_weights(n);
        let lr = 1e-3_f64;
        let tol = 1e-10_f64;

        for iter in 0..2000 {
            let port_var = portfolio_variance(&w, cov);
            let port_vol = port_var.sqrt().max(1e-12);
            let target_rc = port_vol / n as f64;

            let grad: Vec<f64> = (0..n)
                .map(|i| {
                    let mrc = marginal_risk_contribution(&w, cov, i);
                    let rc = w[i] * mrc / port_vol;
                    2.0 * (rc - target_rc) * mrc
                })
                .collect();

            let w_new = project_simplex(
                w.iter().zip(&grad).map(|(wi, gi)| wi - lr * gi).collect(),
                lo, hi,
            );
            let delta: f64 = w_new.iter().zip(&w).map(|(a, b)| (a - b).powi(2)).sum::<f64>().sqrt();
            w = w_new;
            if delta < tol {
                return (w, iter + 1);
            }
        }
        (w, 2000)
    }

    fn kelly_portfolio(
        &self, mu: &[f64], cov: &[Vec<f64>], lo: f64, hi: f64, n: usize,
    ) -> (Vec<f64>, usize) {
        // Approximate Kelly: w ∝ max(Σ⁻¹(μ − rf), 0), then scale by KELLY_FRACTION.
        // Half-Kelly (0.5) is the recommended default: it roughly halves drawdowns
        // while retaining ~75% of full-Kelly long-run growth (Thorp 2006).
        const KELLY_FRACTION: f64 = 0.5;
        let excess: Vec<f64> = mu.iter().map(|m| m - self.risk_free_rate).collect();
        // Simple diagonal-only approximation of Σ⁻¹ for robustness
        let w_raw: Vec<f64> = (0..n)
            .map(|i| {
                let var_i = cov[i][i].max(1e-8);
                (excess[i] / var_i).max(0.0)
            })
            .collect();
        let total: f64 = w_raw.iter().sum();
        let w = if total > 0.0 {
            project_simplex(w_raw.iter().map(|x| x / total * KELLY_FRACTION).collect(), lo, hi)
        } else {
            uniform_weights(n)
        };
        (w, 1)
    }

    fn maximise_return(
        &self, mu: &[f64], lo: f64, hi: f64, n: usize,
    ) -> (Vec<f64>, usize) {
        // Greedy: allocate max weight to highest-return assets
        let mut indexed: Vec<(usize, f64)> = mu.iter().cloned().enumerate().collect();
        indexed.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        let mut w = vec![lo; n];
        let mut remaining = 1.0 - lo * n as f64;
        for (idx, _) in &indexed {
            let alloc = remaining.min(hi - lo);
            w[*idx] += alloc;
            remaining -= alloc;
            if remaining <= 0.0 {
                break;
            }
        }
        (w, 1)
    }

    fn sortino_from_vol(&self, port_return: f64, port_vol: f64) -> f64 {
        // Downside deviation is approximated as DOWNSIDE_VOL_RATIO × total vol.
        // Empirical studies (Sortino & Satchell 2001) show this ratio is typically
        // 0.65–0.75 for diversified equity portfolios; 0.70 is the midpoint default.
        const DOWNSIDE_VOL_RATIO: f64 = 0.70;
        let downside_vol = port_vol * DOWNSIDE_VOL_RATIO;
        if downside_vol == 0.0 {
            return 0.0;
        }
        (port_return - self.risk_free_rate) / downside_vol
    }

    fn diversification_ratio(&self, weights: &[f64], cov: &[Vec<f64>]) -> f64 {
        let n = weights.len();
        let vols: Vec<f64> = (0..n).map(|i| cov[i][i].sqrt()).collect();
        let weighted_vol: f64 = weights.iter().zip(&vols).map(|(w, v)| w * v).sum();
        let port_vol = portfolio_variance(weights, cov).sqrt().max(1e-12);
        weighted_vol / port_vol
    }
}

/// Portfolio rebalancing engine — produces rebalance orders when drift exceeds threshold.
pub struct PortfolioRebalancingEngine {
    pub drift_threshold: f64,
}

impl PortfolioRebalancingEngine {
    pub fn new(drift_threshold: f64) -> Self {
        Self { drift_threshold }
    }

    /// Compute rebalancing orders given current weights, target weights and
    /// total portfolio value.
    pub fn compute_orders(
        &self,
        current_weights: &HashMap<String, f64>,
        target_weights: &HashMap<String, f64>,
        portfolio_value: f64,
    ) -> Vec<RebalanceOrder> {
        let all_symbols: std::collections::HashSet<&String> =
            current_weights.keys().chain(target_weights.keys()).collect();

        let mut orders: Vec<RebalanceOrder> = all_symbols
            .iter()
            .filter_map(|sym| {
                let cur = *current_weights.get(*sym).unwrap_or(&0.0);
                let tgt = *target_weights.get(*sym).unwrap_or(&0.0);
                let drift = tgt - cur;
                if drift.abs() < self.drift_threshold {
                    return None;
                }
                let action = if drift > 0.0 { "buy" } else { "sell" }.to_string();
                Some(RebalanceOrder {
                    symbol: (*sym).clone(),
                    action,
                    current_weight: cur,
                    target_weight: tgt,
                    drift,
                    estimated_trade_value: drift.abs() * portfolio_value,
                })
            })
            .collect();

        // Sort by absolute drift descending (most urgent first)
        orders.sort_by(|a, b| b.drift.abs().partial_cmp(&a.drift.abs()).unwrap_or(std::cmp::Ordering::Equal));
        orders
    }
}

// ── Extended FinancialEngine metrics ────────────────────────────────────────

impl FinancialEngine {
    /// Sortino ratio using downside deviation (returns below `mar`).
    pub fn calculate_sortino_ratio(&self, returns: &[f64], mar: f64) -> f64 {
        if returns.is_empty() {
            return 0.0;
        }
        let downside: Vec<f64> = returns.iter().filter(|&&r| r < mar).map(|&r| r).collect();
        if downside.is_empty() {
            return f64::INFINITY;
        }
        let downside_dev = (downside.iter().map(|r| r.powi(2)).sum::<f64>() / downside.len() as f64)
            .sqrt()
            * (252_f64).sqrt();
        let avg_return = returns.iter().sum::<f64>() / returns.len() as f64 * 252.0;
        (avg_return - self.risk_free_rate) / downside_dev
    }

    /// Calmar ratio: annualised return / absolute max drawdown.
    pub fn calculate_calmar_ratio(&self, annualised_return: f64, max_drawdown: f64) -> f64 {
        if max_drawdown == 0.0 {
            return 0.0;
        }
        annualised_return / max_drawdown.abs()
    }

    /// Information ratio: active return / tracking error.
    pub fn calculate_information_ratio(
        &self,
        portfolio_returns: &[f64],
        benchmark_returns: &[f64],
    ) -> f64 {
        if portfolio_returns.len() != benchmark_returns.len() || portfolio_returns.is_empty() {
            return 0.0;
        }
        let active: Vec<f64> = portfolio_returns
            .iter()
            .zip(benchmark_returns)
            .map(|(p, b)| p - b)
            .collect();
        let tracking_error = self.calculate_volatility(&active);
        if tracking_error == 0.0 {
            return 0.0;
        }
        let avg_active = active.iter().sum::<f64>() / active.len() as f64 * 252.0;
        avg_active / (tracking_error * (252_f64).sqrt())
    }

    /// Kelly Criterion: optimal fraction of capital to risk.
    ///
    /// `fraction` scales the full Kelly (use 0.5 for half-Kelly).
    pub fn kelly_position_size(
        &self,
        win_rate: f64,
        avg_win: f64,
        avg_loss: f64,
        fraction: f64,
    ) -> f64 {
        if avg_loss == 0.0 {
            return 0.0;
        }
        let b = avg_win / avg_loss;
        let kelly = (b * win_rate - (1.0 - win_rate)) / b;
        (kelly * fraction).max(0.0)
    }

    /// Max drawdown of an equity curve.
    pub fn calculate_max_drawdown(&self, equity_curve: &[f64]) -> f64 {
        if equity_curve.is_empty() {
            return 0.0;
        }
        let mut peak = equity_curve[0];
        let mut max_dd = 0.0_f64;
        for &v in equity_curve {
            if v > peak {
                peak = v;
            }
            let dd = (v - peak) / peak;
            if dd < max_dd {
                max_dd = dd;
            }
        }
        max_dd
    }

    /// Omega ratio: probability-weighted gains / losses above threshold `tau`.
    pub fn calculate_omega_ratio(&self, returns: &[f64], tau: f64) -> f64 {
        if returns.is_empty() {
            return 1.0;
        }
        let gains: f64 = returns.iter().filter(|&&r| r > tau).map(|&r| r - tau).sum();
        let losses: f64 = returns.iter().filter(|&&r| r <= tau).map(|&r| tau - r).sum();
        if losses == 0.0 {
            return f64::INFINITY;
        }
        gains / losses
    }
}

// ── Linear-algebra helpers (no external crate) ──────────────────────────────

fn dot(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

fn portfolio_variance(weights: &[f64], cov: &[Vec<f64>]) -> f64 {
    let n = weights.len();
    let mut var = 0.0_f64;
    for i in 0..n {
        for j in 0..n {
            var += weights[i] * weights[j] * cov[i][j];
        }
    }
    var.max(0.0)
}

fn marginal_risk_contribution(weights: &[f64], cov: &[Vec<f64>], k: usize) -> f64 {
    // (Σw)[k]
    cov[k].iter().zip(weights).map(|(c, w)| c * w).sum()
}

fn uniform_weights(n: usize) -> Vec<f64> {
    vec![1.0 / n as f64; n]
}

/// Project a weight vector onto the probability simplex with per-asset bounds
/// [lo, hi] using iterative clipping + renormalisation (≈ Dykstra's algorithm).
fn project_simplex(mut w: Vec<f64>, lo: f64, hi: f64) -> Vec<f64> {
    let n = w.len();
    for _ in 0..50 {
        for wi in w.iter_mut() {
            *wi = wi.clamp(lo, hi);
        }
        let s: f64 = w.iter().sum();
        if s <= 0.0 {
            return vec![1.0 / n as f64; n];
        }
        let scale = 1.0 / s;
        for wi in w.iter_mut() {
            *wi *= scale;
        }
        // Re-clip after normalisation
        for wi in w.iter_mut() {
            *wi = wi.clamp(lo, hi);
        }
        let s2: f64 = w.iter().sum();
        if (s2 - 1.0).abs() < 1e-9 {
            break;
        }
    }
    w
}

// ── StudyHall Economy Module ───────────────────────────────────────────────────
//
// Author: Steve Sloan (Prince Sloan)
// Purpose: Rust translation of the Lean 4 StudyHall economy specification.
//          Defines types and predicates for a sustainable "Learn-to-Earn" and
//          "Play-to-Earn" educational economy.

/// Funding origins that bring real value into the StudyHall system.
///
/// Mirrors: `inductive Source` in the Lean 4 specification.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum StudyHallSource {
    /// Schools, universities, districts
    Institution,
    /// Corporations, NIL brands, partners
    Sponsor,
    /// Nonprofit or donor foundations
    Philanthropy,
    /// Subscriptions, tutoring, or app fees
    UserRevenue,
    /// Initial capital reserve (seed, DAO, investors)
    TreasurySeed,
}

impl StudyHallSource {
    /// All canonical source variants.
    pub const ALL: [StudyHallSource; 5] = [
        StudyHallSource::Institution,
        StudyHallSource::Sponsor,
        StudyHallSource::Philanthropy,
        StudyHallSource::UserRevenue,
        StudyHallSource::TreasurySeed,
    ];
}

/// Reward distribution channels within the StudyHall economy.
///
/// Mirrors: `inductive Flow` in the Lean 4 specification.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum StudyHallFlow {
    LearnToEarn,
    PlayToEarn,
    MentorReward,
    Reserve,
}

impl StudyHallFlow {
    /// All canonical flow variants.
    pub const ALL: [StudyHallFlow; 4] = [
        StudyHallFlow::LearnToEarn,
        StudyHallFlow::PlayToEarn,
        StudyHallFlow::MentorReward,
        StudyHallFlow::Reserve,
    ];
}

/// Returns `true` iff the given source represents real, fiat-backed value.
///
/// Mirrors: `def isRealValue (s : Source) : Prop` — every known variant is real.
pub fn studyhall_is_real_value(source: StudyHallSource) -> bool {
    matches!(
        source,
        StudyHallSource::Institution
            | StudyHallSource::Sponsor
            | StudyHallSource::Philanthropy
            | StudyHallSource::UserRevenue
            | StudyHallSource::TreasurySeed
    )
}

/// Returns `true` iff `source` is a valid funding origin for `flow`.
///
/// Mirrors: `def funded (f : Flow) (s : Source) : Prop`.
pub fn studyhall_funded(flow: StudyHallFlow, source: StudyHallSource) -> bool {
    use StudyHallFlow::*;
    use StudyHallSource::*;
    match flow {
        LearnToEarn => matches!(
            source,
            Institution | Sponsor | Philanthropy | UserRevenue | TreasurySeed
        ),
        PlayToEarn => matches!(source, Sponsor | UserRevenue | TreasurySeed),
        MentorReward => matches!(source, Institution | UserRevenue),
        Reserve => true, // Any source funds the reserve
    }
}

/// Returns the first valid funding source for `flow`, or `None` if none exists.
///
/// Mirrors: the existential `∀ f, ∃ s, funded f s`.
pub fn studyhall_find_funding_source(flow: StudyHallFlow) -> Option<StudyHallSource> {
    StudyHallSource::ALL
        .iter()
        .copied()
        .find(|&s| studyhall_funded(flow, s))
}

/// Returns `true` when the payout does **not** violate the no-self-minting axiom.
///
/// A violation occurs when `amount > 0` but `source` is `None` (self-generated).
///
/// Mirrors: `axiom no_self_minting : ∀ (t : Flow), ¬ (∃ v : Nat, v > 0 ∧ v originates_from t)`.
pub fn studyhall_no_self_minting(
    _flow: StudyHallFlow,
    amount: u64,
    source: Option<StudyHallSource>,
) -> bool {
    !(amount > 0 && source.is_none())
}

/// Returns `true` iff the StudyHall economy satisfies all three sustainability conditions:
///
/// 1. Every flow has at least one valid real funding source.
/// 2. Every source is real-valued (fiat or tangible goods).
/// 3. No flow can produce a positive payout without an external source.
///
/// Mirrors: `def SustainableSystem : Prop` and `theorem sustainability_truth`.
pub fn studyhall_is_sustainable_system() -> bool {
    let all_flows_funded = StudyHallFlow::ALL
        .iter()
        .all(|&f| studyhall_find_funding_source(f).is_some());

    let all_sources_real = StudyHallSource::ALL
        .iter()
        .all(|&s| studyhall_is_real_value(s));

    // No flow may self-mint: a positive amount without a source must be blocked.
    let no_self_mint = StudyHallFlow::ALL
        .iter()
        .all(|&f| !studyhall_no_self_minting(f, 1, None));

    all_flows_funded && all_sources_real && no_self_mint
}

// ── FIRE Optimization Module ───────────────────────────────────────────────────
//
// Personal Financial Freedom Planning: Financial Independence, Retire Early (FIRE)
// Provides core calculations for FI number, CoastFIRE, time-to-FIRE,
// safe-withdrawal-rate scenario analysis, and Monte Carlo success probability.

/// FIRE variants representing different lifestyle and savings targets.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum FIREVariant {
    /// Lean FIRE – minimal expenses, typically < $40k/year in the US.
    Lean,
    /// Regular FIRE – covers comfortable living expenses.
    Regular,
    /// Fat FIRE – covers affluent lifestyle with significant discretionary spending.
    Fat,
    /// Coast FIRE – has enough saved to coast to full FI without new contributions.
    Coast,
    /// Barista FIRE – partially retired; part-time income covers basic expenses.
    Barista,
}

/// A single safe-withdrawal-rate scenario.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SWRScenario {
    /// Annual withdrawal rate (e.g. 0.04 for 4 %).
    pub withdrawal_rate: f64,
    /// Required portfolio size at this withdrawal rate.
    pub required_portfolio: f64,
    /// Annual withdrawal amount.
    pub annual_withdrawal: f64,
    /// Monthly withdrawal amount.
    pub monthly_withdrawal: f64,
}

/// A milestone on the path to financial independence.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FIREMilestone {
    /// Descriptive label (e.g. "25% FI", "CoastFIRE").
    pub label: String,
    /// Portfolio value at this milestone.
    pub portfolio_value: f64,
    /// Percentage of FI number achieved.
    pub percent_complete: f64,
}

/// The result of a complete FIRE optimisation run.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FIREPlan {
    /// Detected / requested FIRE variant.
    pub variant: FIREVariant,
    /// Full financial-independence portfolio target.
    pub fi_number: f64,
    /// CoastFIRE portfolio target (amount needed now to coast without new contributions).
    pub coast_fi_number: f64,
    /// Months until FI assuming constant monthly savings and expected return.
    pub months_to_fi: u32,
    /// Safe-withdrawal-rate scenarios (3 %, 3.5 %, 4 %, 4.5 %, 5 %).
    pub swr_scenarios: Vec<SWRScenario>,
    /// Monte Carlo success probability (0–1).
    pub monte_carlo_success_rate: f64,
    /// Recommended monthly savings to hit the target in `months_to_fi` months.
    pub recommended_monthly_savings: f64,
    /// Key milestones on the path to FI.
    pub milestones: Vec<FIREMilestone>,
}

/// Engine for FIRE (Financial Independence, Retire Early) planning and optimisation.
pub struct FIREOptimizer {
    /// Deterministic seed used for reproducible Monte Carlo results.
    rng_seed: u64,
}

impl FIREOptimizer {
    /// Create a new `FIREOptimizer`.
    ///
    /// `rng_seed` is used to initialise the internal pseudo-random number
    /// generator for Monte Carlo simulations so that results are reproducible.
    pub fn new(rng_seed: u64) -> Self {
        Self { rng_seed }
    }

    /// Calculate the FI number (required portfolio) for a given annual expense
    /// level and safe-withdrawal rate.
    ///
    /// Uses the standard formula: `fi_number = annual_expenses / withdrawal_rate`.
    ///
    /// Returns an error when `withdrawal_rate` is not in (0, 1].
    pub fn calculate_fi_number(
        &self,
        annual_expenses: f64,
        withdrawal_rate: f64,
    ) -> Result<f64, String> {
        if withdrawal_rate <= 0.0 || withdrawal_rate > 1.0 {
            return Err(format!(
                "withdrawal_rate must be in (0, 1]; got {withdrawal_rate}"
            ));
        }
        Ok(annual_expenses / withdrawal_rate)
    }

    /// Calculate the CoastFIRE number: the lump-sum needed *today* so that,
    /// with no further contributions, it compounds to `fi_number` in
    /// `years_to_retirement` years at `annual_return`.
    ///
    /// Formula: `coast_fi = fi_number / (1 + annual_return)^years`.
    pub fn calculate_coast_fi_number(
        &self,
        fi_number: f64,
        years_to_retirement: f64,
        annual_return: f64,
    ) -> Result<f64, String> {
        if years_to_retirement < 0.0 {
            return Err("years_to_retirement must be non-negative".to_string());
        }
        if annual_return <= -1.0 {
            return Err("annual_return must be > -1".to_string());
        }
        Ok(fi_number / (1.0 + annual_return).powf(years_to_retirement))
    }

    /// Calculate months to reach `fi_number` starting from `current_savings`,
    /// adding `monthly_savings` each month, compounding at `annual_return`.
    ///
    /// Uses the standard future-value-of-annuity formula solved for *n*:
    /// ```text
    /// FV = PV * (1+r)^n  +  PMT * ((1+r)^n - 1) / r
    /// ```
    /// where `r` is the monthly return.  Returns `None` when the target is
    /// unreachable (e.g. zero savings rate and current savings below target).
    pub fn calculate_months_to_fi(
        &self,
        current_savings: f64,
        monthly_savings: f64,
        fi_number: f64,
        annual_return: f64,
    ) -> Option<u32> {
        if current_savings >= fi_number {
            return Some(0);
        }
        let monthly_return = annual_return / 12.0;

        // No investment growth – purely linear accumulation.
        if monthly_return.abs() < 1e-10 {
            if monthly_savings <= 0.0 {
                return None;
            }
            let months = (fi_number - current_savings) / monthly_savings;
            return Some(months.ceil() as u32);
        }

        // Binary-search for *n* because the closed-form log solution can be
        // numerically unstable when `current_savings` is large relative to PMT.
        let mut lo: u32 = 0;
        let mut hi: u32 = 1_200; // 100 years cap
        let fv = |n: u32| -> f64 {
            let factor = (1.0 + monthly_return).powi(n as i32);
            current_savings * factor + monthly_savings * (factor - 1.0) / monthly_return
        };

        if fv(hi) < fi_number {
            return None; // Cannot reach target within 100 years
        }

        while lo < hi {
            let mid = lo + (hi - lo) / 2;
            if fv(mid) >= fi_number {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        Some(lo)
    }

    /// Generate SWR scenarios for `annual_expenses` at standard withdrawal rates
    /// (3 %, 3.5 %, 4 %, 4.5 %, 5 %).
    pub fn calculate_swr_scenarios(&self, annual_expenses: f64) -> Vec<SWRScenario> {
        [0.03, 0.035, 0.04, 0.045, 0.05]
            .iter()
            .map(|&rate| SWRScenario {
                withdrawal_rate: rate,
                required_portfolio: annual_expenses / rate,
                annual_withdrawal: annual_expenses,
                monthly_withdrawal: annual_expenses / 12.0,
            })
            .collect()
    }

    /// Estimate the probability of a portfolio sustaining `annual_withdrawal`
    /// for `years` years via a simplified Monte Carlo simulation.
    ///
    /// Uses a seeded linear-congruential generator for reproducibility without
    /// external dependencies.  Each simulation draws annual returns from a
    /// normal distribution approximated by the Box–Muller transform.
    ///
    /// * `portfolio_value` – starting portfolio balance.
    /// * `annual_withdrawal` – amount withdrawn at the start of each year.
    /// * `years` – number of years the portfolio must last.
    /// * `mean_annual_return` – expected annual return (e.g. 0.07 for 7 %).
    /// * `annual_volatility` – annual standard deviation (e.g. 0.15 for 15 %).
    /// * `simulations` – number of Monte Carlo paths (≥ 1, capped at 100 000).
    pub fn monte_carlo_success_rate(
        &self,
        portfolio_value: f64,
        annual_withdrawal: f64,
        years: u32,
        mean_annual_return: f64,
        annual_volatility: f64,
        simulations: u32,
    ) -> f64 {
        let simulations = simulations.clamp(1, 100_000);
        let mut successes = 0u32;

        // Seeded LCG for reproducible pseudo-random numbers.
        let mut state = self.rng_seed.wrapping_add(1);
        // 2^32: upper 32 bits of the 64-bit LCG state are mapped to (0, 1).
        const U32_RANGE: f64 = 4_294_967_296.0;
        let lcg_next = |s: &mut u64| -> f64 {
            *s = s.wrapping_mul(6_364_136_223_846_793_005)
                .wrapping_add(1_442_695_040_888_963_407);
            // Map to (0, 1) by taking the upper 32 bits.
            ((*s >> 32) as f64 + 0.5) / U32_RANGE
        };

        for _ in 0..simulations {
            let mut balance = portfolio_value;
            let mut survived = true;

            for _ in 0..years {
                // Box–Muller transform: two uniform samples → one normal sample.
                let u1 = lcg_next(&mut state);
                let u2 = lcg_next(&mut state);
                let z = (-2.0 * u1.ln()).sqrt() * (2.0 * std::f64::consts::PI * u2).cos();
                let annual_return = mean_annual_return + annual_volatility * z;

                balance = balance * (1.0 + annual_return) - annual_withdrawal;
                if balance <= 0.0 {
                    survived = false;
                    break;
                }
            }

            if survived {
                successes += 1;
            }
        }

        successes as f64 / simulations as f64
    }

    /// Calculate the savings rate required to reach `fi_number` in exactly
    /// `target_years` years, given `monthly_income` and `current_savings`.
    ///
    /// Returns the required monthly savings amount, or `None` if the target is
    /// already met or the required savings exceeds monthly income.
    pub fn required_monthly_savings(
        &self,
        monthly_income: f64,
        current_savings: f64,
        fi_number: f64,
        target_years: f64,
        annual_return: f64,
    ) -> Option<f64> {
        if current_savings >= fi_number {
            return None; // Already FI
        }
        let n = (target_years * 12.0) as u32;
        let monthly_return = annual_return / 12.0;

        // FV of current savings after n months.
        let fv_current = if monthly_return.abs() < 1e-10 {
            current_savings
        } else {
            current_savings * (1.0 + monthly_return).powi(n as i32)
        };

        let remaining = fi_number - fv_current;
        if remaining <= 0.0 {
            return Some(0.0); // Existing savings suffice
        }

        // PMT needed: remaining = PMT * ((1+r)^n - 1) / r
        let pmt = if monthly_return.abs() < 1e-10 {
            remaining / n as f64
        } else {
            let factor = (1.0 + monthly_return).powi(n as i32);
            remaining * monthly_return / (factor - 1.0)
        };

        if pmt > monthly_income {
            None // Cannot save enough even on full income
        } else {
            Some(pmt)
        }
    }

    /// Build a complete FIRE plan for a user.
    ///
    /// * `variant` – desired FIRE variant.
    /// * `annual_expenses` – current annual spending.
    /// * `current_savings` – existing investment portfolio.
    /// * `monthly_savings` – planned monthly contribution.
    /// * `monthly_income` – gross monthly income (used for savings rate advice).
    /// * `years_to_retirement` – years until the user wants to stop working
    ///   (used for CoastFIRE and Monte Carlo).
    /// * `mean_annual_return` – expected portfolio annual return.
    /// * `annual_volatility` – portfolio annual return standard deviation.
    pub fn build_fire_plan(
        &self,
        variant: FIREVariant,
        annual_expenses: f64,
        current_savings: f64,
        monthly_savings: f64,
        monthly_income: f64,
        years_to_retirement: f64,
        mean_annual_return: f64,
        annual_volatility: f64,
    ) -> Result<FIREPlan, String> {
        // Choose withdrawal rate by variant.
        let withdrawal_rate = match variant {
            FIREVariant::Lean => 0.035,   // More conservative for lean budgets
            FIREVariant::Regular => 0.04,
            FIREVariant::Fat => 0.03,     // Lower rate for fat FIRE (longer horizon)
            FIREVariant::Coast => 0.04,
            FIREVariant::Barista => 0.04,
        };

        let fi_number = self.calculate_fi_number(annual_expenses, withdrawal_rate)?;
        let coast_fi_number = self.calculate_coast_fi_number(
            fi_number,
            years_to_retirement,
            mean_annual_return,
        )?;

        let months_to_fi = self
            .calculate_months_to_fi(current_savings, monthly_savings, fi_number, mean_annual_return)
            .unwrap_or(u32::MAX);

        let swr_scenarios = self.calculate_swr_scenarios(annual_expenses);

        let monte_carlo_success_rate = self.monte_carlo_success_rate(
            fi_number,
            annual_expenses,
            (years_to_retirement * 1.5) as u32 + 30, // Stress-test beyond planned horizon
            mean_annual_return,
            annual_volatility,
            10_000,
        );

        let recommended_monthly_savings = self
            .required_monthly_savings(
                monthly_income,
                current_savings,
                fi_number,
                years_to_retirement,
                mean_annual_return,
            )
            .unwrap_or(monthly_savings);

        let milestones = vec![
            FIREMilestone {
                label: "25% FI".to_string(),
                portfolio_value: fi_number * 0.25,
                percent_complete: 25.0,
            },
            FIREMilestone {
                label: "CoastFIRE".to_string(),
                portfolio_value: coast_fi_number,
                percent_complete: (coast_fi_number / fi_number * 100.0).min(100.0),
            },
            FIREMilestone {
                label: "50% FI".to_string(),
                portfolio_value: fi_number * 0.50,
                percent_complete: 50.0,
            },
            FIREMilestone {
                label: "BaristaFIRE".to_string(),
                portfolio_value: fi_number * 0.70,
                percent_complete: 70.0,
            },
            FIREMilestone {
                label: "Full FI".to_string(),
                portfolio_value: fi_number,
                percent_complete: 100.0,
            },
        ];

        Ok(FIREPlan {
            variant,
            fi_number,
            coast_fi_number,
            months_to_fi,
            swr_scenarios,
            monte_carlo_success_rate,
            recommended_monthly_savings,
            milestones,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    // ── helpers ────────────────────────────────────────────────────────────────

    fn make_position(symbol: &str, market_value: f64, unrealized_pnl: f64) -> Position {
        Position {
            id: Uuid::new_v4(),
            account_id: "test".to_string(),
            symbol: symbol.to_string(),
            instrument_type: InstrumentType::Stock,
            quantity: 1.0,
            average_price: market_value - unrealized_pnl,
            current_price: market_value,
            market_value,
            unrealized_pnl,
            last_updated: Utc::now(),
        }
    }

    fn make_metrics(processing_time_ms: u64) -> PerformanceMetrics {
        PerformanceMetrics {
            processing_time_ms,
            memory_usage_mb: 50.0,
            cpu_usage_percent: 25.0,
            throughput_ops_per_sec: 1000.0,
            error_rate: 0.01,
            timestamp: Utc::now(),
        }
    }

    // ── FinancialEngine: original tests ────────────────────────────────────────

    #[test]
    fn test_financial_engine_calculations() {
        let engine = FinancialEngine::new(0.02);

        let positions = vec![
            Position {
                id: Uuid::new_v4(),
                account_id: "test".to_string(),
                symbol: "AAPL".to_string(),
                instrument_type: InstrumentType::Stock,
                quantity: 100.0,
                average_price: 150.0,
                current_price: 155.0,
                market_value: 15500.0,
                unrealized_pnl: 500.0,
                last_updated: Utc::now(),
            },
            Position {
                id: Uuid::new_v4(),
                account_id: "test".to_string(),
                symbol: "GOOGL".to_string(),
                instrument_type: InstrumentType::Stock,
                quantity: 50.0,
                average_price: 200.0,
                current_price: 200.0,
                market_value: 10000.0,
                unrealized_pnl: 0.0,
                last_updated: Utc::now(),
            },
        ];

        let total_value = engine.calculate_portfolio_value(&positions);
        assert_eq!(total_value, 25500.0);

        let total_pnl = engine.calculate_portfolio_pnl(&positions);
        assert_eq!(total_pnl, 500.0);

        let weight = engine.calculate_position_weight(&positions[0], total_value);
        assert!((weight - 0.6078).abs() < 0.001);
    }

    #[test]
    fn test_volatility_calculation() {
        let engine = FinancialEngine::new(0.02);
        let returns = vec![0.01, -0.02, 0.03, -0.01, 0.02];

        let volatility = engine.calculate_volatility(&returns);
        assert!(volatility > 0.0);
    }

    #[test]
    fn test_var_calculation() {
        let engine = FinancialEngine::new(0.02);
        let returns = vec![0.01, -0.02, 0.03, -0.01, 0.02, -0.05, 0.01];

        let var_95 = engine.calculate_var(&returns, 0.95);
        assert!(var_95 > 0.0);

        let var_99 = engine.calculate_var(&returns, 0.99);
        assert!(var_99 >= var_95);
    }

    // ── FinancialEngine: expanded tests ────────────────────────────────────────

    #[test]
    fn test_zero_portfolio_value() {
        let engine = FinancialEngine::new(0.02);
        assert_eq!(engine.calculate_portfolio_value(&[]), 0.0);
        assert_eq!(engine.calculate_portfolio_pnl(&[]), 0.0);
    }

    #[test]
    fn test_single_position_weight() {
        let engine = FinancialEngine::new(0.02);
        let pos = make_position("SPY", 10000.0, 0.0);
        let total = engine.calculate_portfolio_value(&[pos.clone()]);
        let weight = engine.calculate_position_weight(&pos, total);
        assert!((weight - 1.0).abs() < 1e-10);
    }

    #[test]
    fn test_zero_total_value_weight() {
        let engine = FinancialEngine::new(0.02);
        let pos = make_position("SPY", 0.0, 0.0);
        // total_value == 0.0 must return 0.0 without panicking
        assert_eq!(engine.calculate_position_weight(&pos, 0.0), 0.0);
    }

    #[test]
    fn test_sharpe_ratio_zero_volatility() {
        let engine = FinancialEngine::new(0.02);
        // volatility == 0.0 must return 0.0 without panicking
        assert_eq!(engine.calculate_sharpe_ratio(&[0.05, 0.05], 0.0), 0.0);
    }

    #[test]
    fn test_sharpe_ratio_positive() {
        let engine = FinancialEngine::new(0.02); // risk-free 2%
        // avg return of 10% >> risk-free rate → positive Sharpe
        let returns = vec![0.10; 252];
        let sharpe = engine.calculate_sharpe_ratio(&returns, 0.05);
        assert!(sharpe > 0.0);
    }

    #[test]
    fn test_var_empty_returns() {
        let engine = FinancialEngine::new(0.02);
        assert_eq!(engine.calculate_var(&[], 0.95), 0.0);
        assert_eq!(engine.calculate_var(&[], 0.99), 0.0);
    }

    #[test]
    fn test_var_95_vs_99_ordering() {
        let engine = FinancialEngine::new(0.02);
        // Large sample with variety of losses
        let returns: Vec<f64> = (0..1000)
            .map(|i| if i % 10 == 0 { -0.1 } else { 0.01 })
            .collect();
        let var_95 = engine.calculate_var(&returns, 0.95);
        let var_99 = engine.calculate_var(&returns, 0.99);
        assert!(var_99 >= var_95, "VaR(99%) must be >= VaR(95%)");
    }

    #[test]
    fn test_volatility_single_element() {
        let engine = FinancialEngine::new(0.02);
        // Less than 2 elements → not enough data, returns 0.0
        assert_eq!(engine.calculate_volatility(&[0.05]), 0.0);
        assert_eq!(engine.calculate_volatility(&[]), 0.0);
    }

    #[test]
    fn test_volatility_identical_returns() {
        let engine = FinancialEngine::new(0.02);
        // All returns equal → variance is effectively zero (within floating-point precision)
        let returns = vec![0.05; 100];
        assert!(
            engine.calculate_volatility(&returns) < 1e-12,
            "volatility of identical returns must be effectively zero",
        );
    }

    // ── MLPipeline: original test ──────────────────────────────────────────────

    #[test]
    fn test_ml_pipeline_processing() {
        let features = vec!["price".to_string(), "volume".to_string(), "volatility".to_string()];
        let pipeline = MLPipeline::new("v1.0".to_string(), features);

        let mut data = Vec::new();
        let mut record = HashMap::new();
        record.insert("price".to_string(), 100.0);
        record.insert("volume".to_string(), 1000.0);
        record.insert("volatility".to_string(), 0.2);
        data.push(record);

        let processed = pipeline.process_training_data(&data).unwrap();
        assert_eq!(processed.len(), 1);
        assert_eq!(processed[0].len(), 3);

        let prediction = pipeline.predict(&processed[0]).unwrap();
        assert!(prediction > 0.0);
    }

    // ── MLPipeline: expanded tests ─────────────────────────────────────────────

    #[test]
    fn test_process_empty_data() {
        let pipeline = MLPipeline::new("v1.0".to_string(), vec!["price".to_string()]);
        assert!(pipeline.process_training_data(&[]).is_err());
    }

    #[test]
    fn test_process_missing_feature() {
        let pipeline = MLPipeline::new(
            "v1.0".to_string(),
            vec!["price".to_string(), "missing_feature".to_string()],
        );
        let mut record = HashMap::new();
        record.insert("price".to_string(), 100.0);
        // "missing_feature" is absent → must return Err
        let result = pipeline.process_training_data(&[record]);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Missing feature"));
    }

    #[test]
    fn test_predict_feature_count_mismatch() {
        let pipeline = MLPipeline::new(
            "v1.0".to_string(),
            vec!["price".to_string(), "volume".to_string()],
        );
        // Pipeline expects 2 features but we supply 3
        let result = pipeline.predict(&[1.0, 2.0, 3.0]);
        assert!(result.is_err());
    }

    #[test]
    fn test_feature_importance_ordering() {
        let features = vec!["a".to_string(), "b".to_string(), "c".to_string()];
        let pipeline = MLPipeline::new("v1.0".to_string(), features);
        let importance = pipeline.get_feature_importance();
        // Importance for index 0 ("a") is 1/1 = 1.0, for "b" 1/2 = 0.5, "c" 1/3
        assert!(importance["a"] > importance["b"]);
        assert!(importance["b"] > importance["c"]);
    }

    #[test]
    fn test_predict_returns_mean() {
        // Pipeline prediction is the arithmetic mean of input features
        let pipeline = MLPipeline::new(
            "v1.0".to_string(),
            vec!["x".to_string(), "y".to_string(), "z".to_string()],
        );
        // mean of [3.0, 6.0, 9.0] = 6.0
        let result = pipeline.predict(&[3.0, 6.0, 9.0]).unwrap();
        assert!((result - 6.0).abs() < 1e-10);
    }

    // ── SystemMonitor: original test ───────────────────────────────────────────

    #[test]
    fn test_system_monitor() {
        let mut monitor = SystemMonitor::new(10);

        let metrics = PerformanceMetrics {
            processing_time_ms: 100,
            memory_usage_mb: 50.0,
            cpu_usage_percent: 25.0,
            throughput_ops_per_sec: 1000.0,
            error_rate: 0.01,
            timestamp: Utc::now(),
        };

        monitor.record_metrics(metrics);

        let latest = monitor.get_latest_metrics().unwrap();
        assert_eq!(latest.processing_time_ms, 100);

        let average = monitor.get_average_metrics().unwrap();
        assert_eq!(average.processing_time_ms, 100);
    }

    // ── SystemMonitor: expanded tests ──────────────────────────────────────────

    #[test]
    fn test_empty_monitor() {
        let monitor = SystemMonitor::new(10);
        assert!(monitor.get_average_metrics().is_none());
    }

    #[test]
    fn test_empty_latest_metrics() {
        let monitor = SystemMonitor::new(10);
        assert!(monitor.get_latest_metrics().is_none());
    }

    #[test]
    fn test_max_history_eviction() {
        let cap = 5_usize;
        let mut monitor = SystemMonitor::new(cap);

        // Insert cap+1 entries; the oldest (processing_time_ms = 1) should be evicted
        for i in 1..=(cap + 1) as u64 {
            monitor.record_metrics(make_metrics(i));
        }

        // History must not exceed the cap
        let avg = monitor.get_average_metrics().unwrap();
        // Entries in history: 2, 3, 4, 5, 6  → avg = (2+3+4+5+6)/5 = 4
        assert_eq!(avg.processing_time_ms, 4);

        // The latest entry should be the last one inserted
        let latest = monitor.get_latest_metrics().unwrap();
        assert_eq!(latest.processing_time_ms, (cap + 1) as u64);
    }

    #[test]
    fn test_average_multiple_metrics() {
        let mut monitor = SystemMonitor::new(100);

        // Insert entries with processing_time_ms 10, 20, 30
        for &t in &[10_u64, 20, 30] {
            monitor.record_metrics(make_metrics(t));
        }

        let avg = monitor.get_average_metrics().unwrap();
        // (10 + 20 + 30) / 3 = 20
        assert_eq!(avg.processing_time_ms, 20);
    }

    // ── FIREOptimizer tests ────────────────────────────────────────────────────

    fn fire_optimizer() -> FIREOptimizer {
        FIREOptimizer::new(42)
    }

    #[test]
    fn test_fi_number_standard_4pct() {
        let opt = fire_optimizer();
        // Classic 4% rule: $80k/year → $2M portfolio
        let fi = opt.calculate_fi_number(80_000.0, 0.04).unwrap();
        assert!((fi - 2_000_000.0).abs() < 1.0, "fi = {fi}");
    }

    #[test]
    fn test_fi_number_invalid_rate() {
        let opt = fire_optimizer();
        assert!(opt.calculate_fi_number(80_000.0, 0.0).is_err());
        assert!(opt.calculate_fi_number(80_000.0, -0.01).is_err());
        assert!(opt.calculate_fi_number(80_000.0, 1.1).is_err());
    }

    #[test]
    fn test_coast_fi_number_zero_years() {
        let opt = fire_optimizer();
        // Zero years to retirement → coast FI == FI number
        let coast = opt.calculate_coast_fi_number(1_000_000.0, 0.0, 0.07).unwrap();
        assert!((coast - 1_000_000.0).abs() < 1.0);
    }

    #[test]
    fn test_coast_fi_number_discounts_over_time() {
        let opt = fire_optimizer();
        let fi = 1_000_000.0;
        let coast_10 = opt.calculate_coast_fi_number(fi, 10.0, 0.07).unwrap();
        let coast_20 = opt.calculate_coast_fi_number(fi, 20.0, 0.07).unwrap();
        // Longer horizon → smaller coast number (more time to compound)
        assert!(coast_10 > coast_20, "coast_10={coast_10}, coast_20={coast_20}");
        // Coast number should always be ≤ FI number
        assert!(coast_10 <= fi);
    }

    #[test]
    fn test_coast_fi_invalid_years() {
        let opt = fire_optimizer();
        assert!(opt.calculate_coast_fi_number(1_000_000.0, -1.0, 0.07).is_err());
    }

    #[test]
    fn test_months_to_fi_already_there() {
        let opt = fire_optimizer();
        // Already at FI number → 0 months
        assert_eq!(opt.calculate_months_to_fi(1_000_000.0, 1_000.0, 500_000.0, 0.07), Some(0));
    }

    #[test]
    fn test_months_to_fi_linear_no_return() {
        let opt = fire_optimizer();
        // $0 savings, $1k/month, need $12k → exactly 12 months (no return)
        let months = opt.calculate_months_to_fi(0.0, 1_000.0, 12_000.0, 0.0).unwrap();
        assert_eq!(months, 12);
    }

    #[test]
    fn test_months_to_fi_with_return() {
        let opt = fire_optimizer();
        // With positive return, fewer months than linear estimate
        let linear = opt.calculate_months_to_fi(0.0, 1_000.0, 120_000.0, 0.0).unwrap();
        let with_return = opt.calculate_months_to_fi(0.0, 1_000.0, 120_000.0, 0.07).unwrap();
        assert!(with_return < linear, "with_return={with_return}, linear={linear}");
    }

    #[test]
    fn test_months_to_fi_unreachable() {
        let opt = fire_optimizer();
        // Zero savings, zero monthly savings → unreachable
        assert!(opt.calculate_months_to_fi(0.0, 0.0, 1_000_000.0, 0.07).is_none());
    }

    #[test]
    fn test_swr_scenarios_count_and_order() {
        let opt = fire_optimizer();
        let scenarios = opt.calculate_swr_scenarios(80_000.0);
        assert_eq!(scenarios.len(), 5);
        // Rates should be ascending: 3%, 3.5%, 4%, 4.5%, 5%
        let rates: Vec<f64> = scenarios.iter().map(|s| s.withdrawal_rate).collect();
        for w in rates.windows(2) {
            assert!(w[0] < w[1]);
        }
        // Lower rate → higher required portfolio
        for w in scenarios.windows(2) {
            assert!(w[0].required_portfolio > w[1].required_portfolio);
        }
    }

    #[test]
    fn test_swr_scenario_4pct_math() {
        let opt = fire_optimizer();
        let scenarios = opt.calculate_swr_scenarios(40_000.0);
        let four_pct = scenarios.iter().find(|s| (s.withdrawal_rate - 0.04).abs() < 1e-10).unwrap();
        assert!((four_pct.required_portfolio - 1_000_000.0).abs() < 1.0);
        assert!((four_pct.monthly_withdrawal - 40_000.0 / 12.0).abs() < 0.01);
    }

    #[test]
    fn test_monte_carlo_high_success_rate() {
        let opt = fire_optimizer();
        // Conservative portfolio (4% WR for 30 years) should have a high success rate
        let rate = opt.monte_carlo_success_rate(1_000_000.0, 40_000.0, 30, 0.07, 0.15, 5_000);
        assert!(rate > 0.70, "expected high success rate, got {rate}");
    }

    #[test]
    fn test_monte_carlo_low_success_for_aggressive_withdrawal() {
        let opt = fire_optimizer();
        // 10% withdrawal rate for 40 years should fail most of the time
        let rate = opt.monte_carlo_success_rate(1_000_000.0, 100_000.0, 40, 0.05, 0.20, 5_000);
        assert!(rate < 0.80, "expected lower success rate, got {rate}");
    }

    #[test]
    fn test_monte_carlo_zero_volatility_deterministic() {
        let opt = fire_optimizer();
        // With zero volatility the return is constant; all simulations behave identically.
        let r1 = opt.monte_carlo_success_rate(1_000_000.0, 40_000.0, 30, 0.07, 0.0, 100);
        let r2 = opt.monte_carlo_success_rate(1_000_000.0, 40_000.0, 30, 0.07, 0.0, 100);
        assert!((r1 - r2).abs() < 1e-10);
    }

    #[test]
    fn test_required_monthly_savings_already_fi() {
        let opt = fire_optimizer();
        // Already FI → returns None
        assert!(opt.required_monthly_savings(10_000.0, 2_000_000.0, 1_000_000.0, 20.0, 0.07).is_none());
    }

    #[test]
    fn test_required_monthly_savings_reasonable() {
        let opt = fire_optimizer();
        // Need $1M in 20 years with 7% return from $0
        let pmt = opt.required_monthly_savings(10_000.0, 0.0, 1_000_000.0, 20.0, 0.07).unwrap();
        assert!(pmt > 0.0 && pmt < 10_000.0, "pmt={pmt}");
    }

    #[test]
    fn test_build_fire_plan_regular() {
        let opt = fire_optimizer();
        let plan = opt.build_fire_plan(
            FIREVariant::Regular,
            60_000.0,    // annual expenses
            200_000.0,   // current savings
            3_000.0,     // monthly savings
            8_000.0,     // monthly income
            20.0,        // years to retirement
            0.07,        // mean annual return
            0.15,        // annual volatility
        ).unwrap();

        // FI number at 4% SWR should be $1.5M
        assert!((plan.fi_number - 1_500_000.0).abs() < 1.0);
        // CoastFIRE number must be < FI number
        assert!(plan.coast_fi_number < plan.fi_number);
        // Must have exactly 5 SWR scenarios
        assert_eq!(plan.swr_scenarios.len(), 5);
        // Monte Carlo rate should be a probability
        assert!((0.0..=1.0).contains(&plan.monte_carlo_success_rate));
        // Milestones: 5 entries
        assert_eq!(plan.milestones.len(), 5);
    }

    #[test]
    fn test_build_fire_plan_lean_uses_lower_swr() {
        let opt = fire_optimizer();
        let lean = opt.build_fire_plan(
            FIREVariant::Lean, 40_000.0, 0.0, 2_000.0, 6_000.0, 25.0, 0.07, 0.15,
        ).unwrap();
        let regular = opt.build_fire_plan(
            FIREVariant::Regular, 40_000.0, 0.0, 2_000.0, 6_000.0, 25.0, 0.07, 0.15,
        ).unwrap();
        // Lean FIRE uses 3.5% SWR → larger fi_number than Regular at 4%
        assert!(lean.fi_number > regular.fi_number, "lean={}, regular={}", lean.fi_number, regular.fi_number);
    }

    #[test]
    fn test_build_fire_plan_fat_uses_lowest_swr() {
        let opt = fire_optimizer();
        let fat = opt.build_fire_plan(
            FIREVariant::Fat, 120_000.0, 0.0, 5_000.0, 15_000.0, 20.0, 0.07, 0.15,
        ).unwrap();
        // Fat FIRE uses 3% SWR → fi_number = 120k / 0.03 = $4M
        assert!((fat.fi_number - 4_000_000.0).abs() < 1.0);
    }
}
