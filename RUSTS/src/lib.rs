//! ACTORS Rust Performance Components
//! 
//! High-performance Rust components for the ACTORS financial intelligence platform.
//! This module provides optimized implementations for financial calculations,
//! data processing, and ML pipeline components.

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
}
