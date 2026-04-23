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
