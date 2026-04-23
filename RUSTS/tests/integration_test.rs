//! Integration tests for ACTORS Rust performance components.
//!
//! These tests exercise realistic end-to-end scenarios that cross the
//! boundaries of individual structs.

use actors_rust_components::{
    FinancialEngine, InstrumentType, MLPipeline, PerformanceMetrics, Position, SystemMonitor,
};
use chrono::Utc;
use std::collections::HashMap;
use uuid::Uuid;

// ── helpers ────────────────────────────────────────────────────────────────────

fn make_position(symbol: &str, market_value: f64, pnl: f64) -> Position {
    Position {
        id: Uuid::new_v4(),
        account_id: "integration-test".to_string(),
        symbol: symbol.to_string(),
        instrument_type: InstrumentType::Stock,
        quantity: market_value / 100.0,
        average_price: (market_value - pnl) / (market_value / 100.0),
        current_price: 100.0,
        market_value,
        unrealized_pnl: pnl,
        last_updated: Utc::now(),
    }
}

fn make_metrics(processing_time_ms: u64) -> PerformanceMetrics {
    PerformanceMetrics {
        processing_time_ms,
        memory_usage_mb: 64.0,
        cpu_usage_percent: 30.0,
        throughput_ops_per_sec: 500.0,
        error_rate: 0.005,
        timestamp: Utc::now(),
    }
}

// ── Scenario 1: 5-position portfolio ──────────────────────────────────────────

#[test]
fn test_five_position_portfolio() {
    let engine = FinancialEngine::new(0.03);

    let symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"];
    let values = [15_000.0_f64, 10_000.0, 8_000.0, 12_000.0, 5_000.0];
    let pnls = [500.0_f64, -200.0, 300.0, 100.0, -100.0];

    let positions: Vec<Position> = symbols
        .iter()
        .zip(values.iter())
        .zip(pnls.iter())
        .map(|((sym, &mv), &pnl)| make_position(sym, mv, pnl))
        .collect();

    let expected_total_value: f64 = values.iter().sum();
    let expected_total_pnl: f64 = pnls.iter().sum();

    let total_value = engine.calculate_portfolio_value(&positions);
    let total_pnl = engine.calculate_portfolio_pnl(&positions);

    assert!(
        (total_value - expected_total_value).abs() < 1e-6,
        "portfolio value mismatch: got {total_value}, expected {expected_total_value}",
    );
    assert!(
        (total_pnl - expected_total_pnl).abs() < 1e-6,
        "portfolio PnL mismatch: got {total_pnl}, expected {expected_total_pnl}",
    );

    // Weights must sum to 1.0
    let weight_sum: f64 = positions
        .iter()
        .map(|p| engine.calculate_position_weight(p, total_value))
        .sum();
    assert!(
        (weight_sum - 1.0).abs() < 1e-9,
        "weights do not sum to 1: got {weight_sum}",
    );
}

// ── Scenario 2: ML pipeline with 100 training records ─────────────────────────

#[test]
fn test_ml_pipeline_100_records() {
    let feature_names = vec![
        "price".to_string(),
        "volume".to_string(),
        "volatility".to_string(),
        "rsi".to_string(),
        "macd".to_string(),
    ];
    let pipeline = MLPipeline::new("v2.0".to_string(), feature_names.clone());

    let records: Vec<HashMap<String, f64>> = (0..100)
        .map(|i| {
            let mut r = HashMap::new();
            r.insert("price".to_string(), 100.0 + i as f64);
            r.insert("volume".to_string(), 1_000.0 + i as f64 * 10.0);
            r.insert("volatility".to_string(), 0.1 + i as f64 * 0.001);
            r.insert("rsi".to_string(), 50.0 + (i % 50) as f64);
            r.insert("macd".to_string(), (i as f64 - 50.0) * 0.01);
            r
        })
        .collect();

    let processed = pipeline.process_training_data(&records).expect("processing failed");
    assert_eq!(processed.len(), 100, "all 100 records must be processed");
    assert_eq!(
        processed[0].len(),
        feature_names.len(),
        "each record must have {} features",
        feature_names.len(),
    );

    // Every prediction must succeed and be finite
    for (i, row) in processed.iter().enumerate() {
        let pred = pipeline.predict(row).unwrap_or_else(|e| panic!("predict failed on row {i}: {e}"));
        assert!(pred.is_finite(), "prediction for row {i} must be finite, got {pred}");
    }
}

// ── Scenario 3: SystemMonitor history cap ──────────────────────────────────────

#[test]
fn test_system_monitor_50_metrics_capped() {
    let cap = 20_usize;
    let mut monitor = SystemMonitor::new(cap);

    // Insert 50 entries; only the last `cap` should survive
    for i in 1..=50_u64 {
        monitor.record_metrics(make_metrics(i));
    }

    // Latest must be the last inserted
    let latest = monitor.get_latest_metrics().expect("should have latest");
    assert_eq!(latest.processing_time_ms, 50);

    // Average over entries 31..=50 (the cap=20 retained entries)
    let avg = monitor.get_average_metrics().expect("should have average");
    let expected_avg = (31_u64..=50).sum::<u64>() / 20;
    assert_eq!(
        avg.processing_time_ms, expected_avg,
        "average processing time should be {expected_avg}, got {}",
        avg.processing_time_ms,
    );

    // All other averaged fields must be in a reasonable range
    assert!(avg.memory_usage_mb > 0.0);
    assert!(avg.cpu_usage_percent > 0.0);
    assert!(avg.throughput_ops_per_sec > 0.0);
}

// ── Scenario 4: VaR monotonicity ──────────────────────────────────────────────

#[test]
fn test_var_monotonicity() {
    let engine = FinancialEngine::new(0.02);

    // 500-sample return series with realistic daily returns
    let returns: Vec<f64> = (0..500)
        .map(|i| {
            let x = i as f64;
            // mix of small gains and periodic large losses
            if i % 20 == 0 {
                -0.05 - (x * 0.0001)
            } else {
                0.001 + (x * 0.00001)
            }
        })
        .collect();

    let var_90 = engine.calculate_var(&returns, 0.90);
    let var_95 = engine.calculate_var(&returns, 0.95);
    let var_99 = engine.calculate_var(&returns, 0.99);

    assert!(
        var_90 <= var_95,
        "VaR(90%) must be <= VaR(95%): {var_90} vs {var_95}",
    );
    assert!(
        var_95 <= var_99,
        "VaR(95%) must be <= VaR(99%): {var_95} vs {var_99}",
    );
}

// ── Scenario 5: Volatility vs VaR consistency ─────────────────────────────────

#[test]
fn test_higher_volatility_implies_higher_var() {
    let engine = FinancialEngine::new(0.02);

    let low_vol_returns: Vec<f64> = (0..252).map(|_| 0.001).collect();
    let high_vol_returns: Vec<f64> = (0..252)
        .map(|i| if i % 5 == 0 { -0.05 } else { 0.01 })
        .collect();

    let low_vol = engine.calculate_volatility(&low_vol_returns);
    let high_vol = engine.calculate_volatility(&high_vol_returns);
    assert!(high_vol > low_vol, "high-vol series must have greater volatility");

    let low_var = engine.calculate_var(&low_vol_returns, 0.95);
    let high_var = engine.calculate_var(&high_vol_returns, 0.95);
    assert!(high_var > low_var, "high-vol series must have greater VaR");
}
