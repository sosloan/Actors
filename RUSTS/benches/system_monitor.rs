//! Criterion benchmarks for [`SystemMonitor`].

use actors_rust_components::{PerformanceMetrics, SystemMonitor};
use chrono::Utc;
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};

// ── helper ────────────────────────────────────────────────────────────────────

fn make_metrics(processing_time_ms: u64) -> PerformanceMetrics {
    PerformanceMetrics {
        processing_time_ms,
        memory_usage_mb: 64.0,
        cpu_usage_percent: 30.0,
        throughput_ops_per_sec: 1_000.0,
        error_rate: 0.01,
        timestamp: Utc::now(),
    }
}

fn filled_monitor(cap: usize) -> SystemMonitor {
    let mut m = SystemMonitor::new(cap);
    for i in 0..cap as u64 {
        m.record_metrics(make_metrics(i + 1));
    }
    m
}

// ── record_metrics (including eviction when full) ─────────────────────────────

fn bench_record_metrics(c: &mut Criterion) {
    let mut group = c.benchmark_group("record_metrics");

    // Benchmark insertion into a monitor whose history is already at capacity,
    // which exercises both the push and the remove(0) eviction path.
    for &cap in &[10_usize, 100, 1_000] {
        group.bench_with_input(BenchmarkId::from_parameter(cap), &cap, |b, &size| {
            // pre-fill to capacity so every iteration triggers eviction
            let mut monitor = filled_monitor(size);
            b.iter(|| {
                monitor.record_metrics(make_metrics(999));
            });
        });
    }
    group.finish();
}

// ── get_average_metrics ───────────────────────────────────────────────────────

fn bench_get_average_metrics(c: &mut Criterion) {
    let mut group = c.benchmark_group("get_average_metrics");

    for &n in &[10_usize, 100, 1_000] {
        let monitor = filled_monitor(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &monitor, |b, m| {
            b.iter(|| m.get_average_metrics());
        });
    }
    group.finish();
}

// ── get_latest_metrics (constant-time) ───────────────────────────────────────

fn bench_get_latest_metrics(c: &mut Criterion) {
    let mut group = c.benchmark_group("get_latest_metrics");

    // Verify O(1) access regardless of history size
    for &n in &[10_usize, 100, 1_000] {
        let monitor = filled_monitor(n);
        group.bench_with_input(BenchmarkId::from_parameter(n), &monitor, |b, m| {
            b.iter(|| m.get_latest_metrics());
        });
    }
    group.finish();
}

// ── criterion entry point ─────────────────────────────────────────────────────

criterion_group!(
    benches,
    bench_record_metrics,
    bench_get_average_metrics,
    bench_get_latest_metrics,
);
criterion_main!(benches);
