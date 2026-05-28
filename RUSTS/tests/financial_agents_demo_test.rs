//! Tests for the scenarios presented in `financial_agents_demo.rs`.
//!
//! The demo file references a `lobster` crate that is not part of this
//! repository.  These tests exercise the same financial concepts—market-data
//! tracking, FIRE-plan math, order construction, risk management, and
//! performance monitoring—using the `actors_rust_components` API that is
//! actually available.

use actors_rust_components::{
    FinancialEngine, InstrumentType, MLPipeline, Order, OrderSide, OrderType, PerformanceMetrics,
    Position, SystemMonitor,
};
use chrono::Utc;
use std::collections::HashMap;
use uuid::Uuid;

// ── helpers ────────────────────────────────────────────────────────────────────

fn make_position(
    symbol: &str,
    quantity: f64,
    average_price: f64,
    current_price: f64,
) -> Position {
    let market_value = quantity * current_price;
    let unrealized_pnl = quantity * (current_price - average_price);
    Position {
        id: Uuid::new_v4(),
        account_id: "demo-account".to_string(),
        symbol: symbol.to_string(),
        instrument_type: InstrumentType::Stock,
        quantity,
        average_price,
        current_price,
        market_value,
        unrealized_pnl,
        last_updated: Utc::now(),
    }
}

fn make_metrics(processing_time_ms: u64, memory_mb: f64, cpu: f64) -> PerformanceMetrics {
    PerformanceMetrics {
        processing_time_ms,
        memory_usage_mb: memory_mb,
        cpu_usage_percent: cpu,
        throughput_ops_per_sec: 500.0,
        error_rate: 0.005,
        timestamp: Utc::now(),
    }
}

// ── Demo 1 & 2 — Market data / instrument tracking ────────────────────────────

/// The demo adds AAPL (equity) and BTC (crypto) instruments and processes
/// tick data.  Here we verify that a two-asset portfolio with those symbols
/// reports correct aggregate value and PnL.
#[test]
fn test_market_data_two_instrument_portfolio() {
    let engine = FinancialEngine::new(0.03); // demo uses equity + crypto

    // AAPL tick: price 150, quantity 10
    let aapl = make_position("AAPL", 10.0, 148.0, 150.0);
    // BTC tick: price 30_000, quantity 0.5
    let btc = Position {
        id: Uuid::new_v4(),
        account_id: "demo-account".to_string(),
        symbol: "BTC".to_string(),
        instrument_type: InstrumentType::Crypto,
        quantity: 0.5,
        average_price: 28_000.0,
        current_price: 30_000.0,
        market_value: 15_000.0,
        unrealized_pnl: 1_000.0,
        last_updated: Utc::now(),
    };

    let positions = vec![aapl, btc];
    let total_value = engine.calculate_portfolio_value(&positions);
    let total_pnl = engine.calculate_portfolio_pnl(&positions);

    // AAPL: 10 * 150 = 1500; BTC: 0.5 * 30_000 = 15_000; sum = 16_500
    assert!((total_value - 16_500.0).abs() < 1e-6, "total value: {total_value}");
    // AAPL pnl: 10 * (150 - 148) = 20; BTC pnl: 1000; sum = 1020
    assert!((total_pnl - 1_020.0).abs() < 1e-6, "total pnl: {total_pnl}");
}

/// Movement threshold simulation: a 2% threshold for AAPL means a 2% gain
/// increases weight noticeably relative to a flat position.
#[test]
fn test_movement_threshold_weight_shift() {
    let engine = FinancialEngine::new(0.03);

    let baseline = make_position("AAPL", 100.0, 150.0, 150.0); // flat
    let after_move = make_position("AAPL", 100.0, 150.0, 153.0); // +2%

    let portfolio_baseline = vec![baseline.clone()];
    let portfolio_moved = vec![after_move.clone()];

    let val_before = engine.calculate_portfolio_value(&portfolio_baseline);
    let val_after = engine.calculate_portfolio_value(&portfolio_moved);

    // After a 2% move the portfolio is worth more
    assert!(
        val_after > val_before,
        "portfolio value must increase after a positive price move"
    );
    // PnL must be positive
    assert!(
        engine.calculate_portfolio_pnl(&portfolio_moved) > 0.0,
        "unrealized PnL must be positive after the move"
    );
}

// ── Demo 3 — Personal Finance / FIRE planning ─────────────────────────────────

/// Mirror the demo's VTI position:
///   100 shares, avg $200, current $220, market_value $22_000, pnl $2_000.
/// Cash of $10_000 is added directly.  Total = $32_000.
#[test]
fn test_fire_portfolio_value_and_pnl() {
    let engine = FinancialEngine::new(0.02);

    let vti = Position {
        id: Uuid::new_v4(),
        account_id: "user123".to_string(),
        symbol: "VTI".to_string(),
        instrument_type: InstrumentType::Stock,
        quantity: 100.0,
        average_price: 200.0,
        current_price: 220.0,
        market_value: 22_000.0,
        unrealized_pnl: 2_000.0,
        last_updated: Utc::now(),
    };

    let invested_value = engine.calculate_portfolio_value(&[vti.clone()]);
    let cash_balance = 10_000.0_f64;
    let total = invested_value + cash_balance;

    assert!((invested_value - 22_000.0).abs() < 1e-6);
    assert!((total - 32_000.0).abs() < 1e-6);
    assert!((engine.calculate_portfolio_pnl(&[vti]) - 2_000.0).abs() < 1e-6);
}

/// FIRE number based on 4% safe withdrawal rate:
///   monthly_expenses = $4_000 → annual = $48_000 → FI target = $1_200_000.
/// Verify the math and that the demo's $1M target is below the 4%-rule figure.
#[test]
fn test_fire_number_4pct_rule() {
    let monthly_expenses = 4_000.0_f64;
    let annual_expenses = monthly_expenses * 12.0;
    let withdrawal_rate = 0.04_f64;
    let fi_number = annual_expenses / withdrawal_rate;

    assert!(
        (fi_number - 1_200_000.0).abs() < 1e-6,
        "FI number should be $1.2M with 4% SWR: {fi_number}"
    );
    // The demo uses a round $1M target which is slightly below the strict 4%-rule
    assert!(1_000_000.0 < fi_number);
}

/// Monthly savings rate: income $8k, expenses $4k → $4k surplus.
/// Discretionary for investing is $2k (50% of surplus).
/// Verify the savings-rate arithmetic.
#[test]
fn test_fire_monthly_savings_arithmetic() {
    let monthly_income = 8_000.0_f64;
    let monthly_expenses = 4_000.0_f64;
    let surplus = monthly_income - monthly_expenses;
    let discretionary = 2_000.0_f64;

    assert!((surplus - 4_000.0).abs() < 1e-6);
    assert!(discretionary <= surplus, "discretionary must not exceed surplus");
}

// ── Demo 5 — Execution agent / order construction ─────────────────────────────

/// The demo creates a Limit Buy for 100 AAPL at $149.50 (GTC).
/// Verify that the Order struct can be constructed with these exact fields.
#[test]
fn test_execution_agent_order_construction() {
    let order = Order {
        id: Uuid::new_v4(),
        symbol: "AAPL".to_string(),
        instrument_type: InstrumentType::Stock,
        side: OrderSide::Buy,
        order_type: OrderType::Limit,
        quantity: 100.0,
        price: Some(149.50),
        stop_price: None,
        account_id: "demo-account".to_string(),
        created_at: Utc::now(),
        expires_at: None,
    };

    assert_eq!(order.symbol, "AAPL");
    assert_eq!(order.side, OrderSide::Buy);
    assert_eq!(order.order_type, OrderType::Limit);
    assert!((order.quantity - 100.0).abs() < 1e-9);
    assert_eq!(order.price, Some(149.50));
    assert!(order.stop_price.is_none());
}

/// A Market order must not require a price field.
#[test]
fn test_market_order_has_no_price() {
    let order = Order {
        id: Uuid::new_v4(),
        symbol: "MSFT".to_string(),
        instrument_type: InstrumentType::Stock,
        side: OrderSide::Sell,
        order_type: OrderType::Market,
        quantity: 50.0,
        price: None,
        stop_price: None,
        account_id: "demo-account".to_string(),
        created_at: Utc::now(),
        expires_at: None,
    };

    assert_eq!(order.order_type, OrderType::Market);
    assert!(order.price.is_none());
}

/// A StopLimit order requires both a price and a stop_price.
#[test]
fn test_stop_limit_order_fields() {
    let order = Order {
        id: Uuid::new_v4(),
        symbol: "TSLA".to_string(),
        instrument_type: InstrumentType::Stock,
        side: OrderSide::Sell,
        order_type: OrderType::StopLimit,
        quantity: 10.0,
        price: Some(200.0),
        stop_price: Some(205.0),
        account_id: "demo-account".to_string(),
        created_at: Utc::now(),
        expires_at: None,
    };

    assert!(order.price.is_some());
    assert!(order.stop_price.is_some());
    assert!(order.stop_price.unwrap() > order.price.unwrap());
}

// ── Demo 6 — Risk management ──────────────────────────────────────────────────

/// The demo's risk portfolio: AAPL 200 shares, avg $150, current $155,
/// market_value $31_000, pnl $1_000; cash $19_000; total $50_000.
/// The position is $31k out of $50k = 62%, which breaches the 25%
/// concentration cap — the risk monitor would flag this as a limit breach.
#[test]
fn test_risk_portfolio_concentration_breach_detected() {
    let engine = FinancialEngine::new(0.02);

    let aapl = Position {
        id: Uuid::new_v4(),
        account_id: "user123".to_string(),
        symbol: "AAPL".to_string(),
        instrument_type: InstrumentType::Stock,
        quantity: 200.0,
        average_price: 150.0,
        current_price: 155.0,
        market_value: 31_000.0,
        unrealized_pnl: 1_000.0,
        last_updated: Utc::now(),
    };

    let max_position_size = 50_000.0_f64;
    let portfolio_total = 50_000.0_f64;
    let max_concentration = 0.25_f64; // 25% cap per asset

    let invested_value = engine.calculate_portfolio_value(&[aapl.clone()]);
    let weight = engine.calculate_position_weight(&aapl, portfolio_total);

    // Position dollar value is within the absolute size limit
    assert!(
        invested_value <= max_position_size,
        "position size {invested_value} exceeds limit {max_position_size}"
    );
    // But concentration (62%) exceeds the 25% cap → the risk monitor flags it
    assert!(
        weight > max_concentration,
        "expected a concentration breach: weight {weight:.2} should exceed {max_concentration}"
    );
}

/// A four-asset equally weighted portfolio ($12_500 each, total $50_000)
/// satisfies the 25% concentration cap on every individual position.
#[test]
fn test_risk_portfolio_within_concentration_limit() {
    let engine = FinancialEngine::new(0.02);

    let symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"];
    let positions: Vec<Position> = symbols
        .iter()
        .map(|&sym| Position {
            id: Uuid::new_v4(),
            account_id: "user123".to_string(),
            symbol: sym.to_string(),
            instrument_type: InstrumentType::Stock,
            quantity: 100.0,
            average_price: 120.0,
            current_price: 125.0,
            market_value: 12_500.0,
            unrealized_pnl: 500.0,
            last_updated: Utc::now(),
        })
        .collect();

    let portfolio_total = engine.calculate_portfolio_value(&positions);
    let max_concentration = 0.25_f64;

    for pos in &positions {
        let weight = engine.calculate_position_weight(pos, portfolio_total);
        assert!(
            weight <= max_concentration,
            "{} weight {weight:.4} exceeds max {max_concentration}",
            pos.symbol
        );
    }
}

/// VaR monotonicity: VaR(90%) ≤ VaR(95%) ≤ VaR(99%) — mirrors the demo's
/// risk monitor stress-test checks.
#[test]
fn test_risk_var_monotonicity_stress() {
    let engine = FinancialEngine::new(0.02);
    // 300 daily returns with periodic drawdowns (simulating stress scenarios)
    let returns: Vec<f64> = (0..300)
        .map(|i| if i % 15 == 0 { -0.08 } else { 0.002 })
        .collect();

    let var_90 = engine.calculate_var(&returns, 0.90);
    let var_95 = engine.calculate_var(&returns, 0.95);
    let var_99 = engine.calculate_var(&returns, 0.99);

    assert!(
        var_90 <= var_95,
        "VaR(90%) must be <= VaR(95%): {var_90} vs {var_95}"
    );
    assert!(
        var_95 <= var_99,
        "VaR(95%) must be <= VaR(99%): {var_95} vs {var_99}"
    );
}

/// Max drawdown scenario: high-volatility returns must produce greater VaR
/// than low-volatility returns (15% max drawdown guard from the demo).
#[test]
fn test_risk_high_vol_exceeds_low_vol_var() {
    let engine = FinancialEngine::new(0.02);

    let low_vol: Vec<f64> = vec![0.001; 252];
    let high_vol: Vec<f64> = (0..252)
        .map(|i| if i % 6 == 0 { -0.07 } else { 0.01 })
        .collect();

    let low_var = engine.calculate_var(&low_vol, 0.95);
    let high_var = engine.calculate_var(&high_vol, 0.95);

    assert!(
        high_var > low_var,
        "high-vol VaR {high_var} must exceed low-vol VaR {low_var}"
    );
}

/// Sharpe ratio with the demo's risk-free rate (2% annual): use a daily
/// risk-free rate so the scale matches the daily return series.
#[test]
fn test_risk_sharpe_ratio_positive() {
    // Daily risk-free rate: 2% / 252 trading days
    let daily_rf = 0.02_f64 / 252.0;
    let engine = FinancialEngine::new(daily_rf);
    // Daily returns targeting ~10% p.a. (well above the 2% risk-free rate)
    let returns: Vec<f64> = vec![0.10 / 252.0; 252];
    let volatility = engine.calculate_volatility(&returns);
    let sharpe = engine.calculate_sharpe_ratio(&returns, volatility.max(1e-9));
    // Avg daily return (≈ 0.000397) > daily_rf (≈ 0.0000794) → Sharpe > 0
    assert!(sharpe > 0.0, "Sharpe ratio must be positive: {sharpe}");
}

// ── Demo 7 — DeFi yield optimisation ─────────────────────────────────────────

/// The demo deposits $10_000 USDC with a 3% minimum yield target.
/// Verify the arithmetic: 3% of $10_000 = $300 annual return.
#[test]
fn test_defi_minimum_yield_math() {
    let principal = 10_000.0_f64;
    let min_yield = 0.03_f64;
    let expected_annual = principal * min_yield;

    assert!((expected_annual - 300.0).abs() < 1e-6);
}

/// Allocation percentage must sum to 100% in a two-protocol split.
#[test]
fn test_defi_allocation_splits_sum_to_one() {
    let aave_weight = 0.6_f64;
    let compound_weight = 0.4_f64;
    assert!((aave_weight + compound_weight - 1.0).abs() < 1e-9);
}

// ── Demo 8 — Performance evaluation ──────────────────────────────────────────

/// Verify that `SystemMonitor` records and averages metrics correctly—
/// the same role as the demo's PerformanceEvaluationAgent.
#[test]
fn test_performance_evaluation_monitor_average() {
    let mut monitor = SystemMonitor::new(10);

    // Simulate three performance snapshots
    monitor.record_metrics(make_metrics(80, 60.0, 20.0));
    monitor.record_metrics(make_metrics(100, 70.0, 30.0));
    monitor.record_metrics(make_metrics(120, 80.0, 40.0));

    let avg = monitor.get_average_metrics().expect("average must exist");
    // (80 + 100 + 120) / 3 = 100
    assert_eq!(avg.processing_time_ms, 100);
    // (60 + 70 + 80) / 3 = 70
    assert!((avg.memory_usage_mb - 70.0).abs() < 1e-6);
    // (20 + 30 + 40) / 3 = 30
    assert!((avg.cpu_usage_percent - 30.0).abs() < 1e-6);
}

/// The latest snapshot must always be the most recently recorded entry.
#[test]
fn test_performance_evaluation_latest_metrics() {
    let mut monitor = SystemMonitor::new(10);
    monitor.record_metrics(make_metrics(50, 40.0, 10.0));
    monitor.record_metrics(make_metrics(200, 90.0, 75.0));

    let latest = monitor.get_latest_metrics().expect("latest must exist");
    assert_eq!(latest.processing_time_ms, 200);
}

/// When history exceeds the cap, old entries are evicted and the average
/// reflects only the retained window.
#[test]
fn test_performance_evaluation_history_cap_eviction() {
    let cap = 3_usize;
    let mut monitor = SystemMonitor::new(cap);

    for t in 1_u64..=5 {
        monitor.record_metrics(make_metrics(t * 10, 50.0, 25.0));
    }

    // Retained entries: 30, 40, 50 → average = 40
    let avg = monitor.get_average_metrics().unwrap();
    assert_eq!(avg.processing_time_ms, 40);
}

// ── ML pipeline used in Demo 8 ────────────────────────────────────────────────

/// The demo creates a PerformanceEvaluationAgent with multiple feature
/// streams.  Here we confirm the ML pipeline processes a representative
/// set of financial features correctly.
#[test]
fn test_performance_ml_pipeline_financial_features() {
    let features = vec![
        "price".to_string(),
        "volume".to_string(),
        "volatility".to_string(),
        "rsi".to_string(),
        "macd".to_string(),
    ];
    let pipeline = MLPipeline::new("demo-v1".to_string(), features.clone());

    let records: Vec<HashMap<String, f64>> = (0..10)
        .map(|i| {
            let mut r = HashMap::new();
            r.insert("price".to_string(), 150.0 + i as f64);
            r.insert("volume".to_string(), 1_000.0 + i as f64 * 10.0);
            r.insert("volatility".to_string(), 0.02 + i as f64 * 0.001);
            r.insert("rsi".to_string(), 50.0 + i as f64);
            r.insert("macd".to_string(), (i as f64 - 5.0) * 0.01);
            r
        })
        .collect();

    let processed = pipeline.process_training_data(&records).expect("processing must succeed");
    assert_eq!(processed.len(), 10);
    assert_eq!(processed[0].len(), features.len());

    for (i, row) in processed.iter().enumerate() {
        let pred = pipeline
            .predict(row)
            .unwrap_or_else(|e| panic!("predict failed on row {i}: {e}"));
        assert!(pred.is_finite(), "prediction for row {i} must be finite: {pred}");
    }
}
