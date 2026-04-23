//! Criterion benchmarks for [`FinancialEngine`].

use actors_rust_components::{FinancialEngine, InstrumentType, Position};
use chrono::Utc;
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use uuid::Uuid;

// ── helpers ───────────────────────────────────────────────────────────────────

fn make_positions(n: usize) -> Vec<Position> {
    (0..n)
        .map(|i| Position {
            id: Uuid::new_v4(),
            account_id: "bench".to_string(),
            symbol: format!("SYM{i}"),
            instrument_type: InstrumentType::Stock,
            quantity: 100.0,
            average_price: 100.0,
            current_price: 105.0,
            market_value: 10_500.0,
            unrealized_pnl: 500.0,
            last_updated: Utc::now(),
        })
        .collect()
}

fn make_returns(n: usize) -> Vec<f64> {
    (0..n)
        .map(|i| if i % 10 == 0 { -0.03 } else { 0.01 })
        .collect()
}

// ── portfolio value ────────────────────────────────────────────────────────────

fn bench_portfolio_value(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let mut group = c.benchmark_group("portfolio_value");

    for n in [10, 100, 1_000] {
        let positions = make_positions(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &positions, |b, pos| {
            b.iter(|| engine.calculate_portfolio_value(pos));
        });
    }
    group.finish();
}

// ── portfolio PnL ─────────────────────────────────────────────────────────────

fn bench_portfolio_pnl(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let mut group = c.benchmark_group("portfolio_pnl");

    for n in [10, 100, 1_000] {
        let positions = make_positions(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &positions, |b, pos| {
            b.iter(|| engine.calculate_portfolio_pnl(pos));
        });
    }
    group.finish();
}

// ── position weight ───────────────────────────────────────────────────────────

fn bench_position_weight(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let positions = make_positions(1);
    let pos = &positions[0];
    let total = engine.calculate_portfolio_value(&positions);

    c.bench_function("position_weight", |b| {
        b.iter(|| engine.calculate_position_weight(pos, total));
    });
}

// ── Sharpe ratio ──────────────────────────────────────────────────────────────

fn bench_sharpe_ratio(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let mut group = c.benchmark_group("sharpe_ratio");

    for n in [30, 252, 1_000] {
        let returns = make_returns(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &returns, |b, ret| {
            b.iter(|| engine.calculate_sharpe_ratio(ret, 0.15));
        });
    }
    group.finish();
}

// ── VaR 95% ───────────────────────────────────────────────────────────────────

fn bench_var_95(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let mut group = c.benchmark_group("var_95");

    for n in [252, 1_000, 10_000] {
        let returns = make_returns(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &returns, |b, ret| {
            b.iter(|| engine.calculate_var(ret, 0.95));
        });
    }
    group.finish();
}

// ── VaR 99% ───────────────────────────────────────────────────────────────────

fn bench_var_99(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let mut group = c.benchmark_group("var_99");

    for n in [252, 1_000, 10_000] {
        let returns = make_returns(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &returns, |b, ret| {
            b.iter(|| engine.calculate_var(ret, 0.99));
        });
    }
    group.finish();
}

// ── volatility ────────────────────────────────────────────────────────────────

fn bench_volatility(c: &mut Criterion) {
    let engine = FinancialEngine::new(0.02);
    let mut group = c.benchmark_group("volatility");

    for n in [30, 252, 1_000] {
        let returns = make_returns(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &returns, |b, ret| {
            b.iter(|| engine.calculate_volatility(ret));
        });
    }
    group.finish();
}

// ── criterion entry point ─────────────────────────────────────────────────────

criterion_group!(
    benches,
    bench_portfolio_value,
    bench_portfolio_pnl,
    bench_position_weight,
    bench_sharpe_ratio,
    bench_var_95,
    bench_var_99,
    bench_volatility,
);
criterion_main!(benches);
