//! Criterion benchmarks for [`MLPipeline`].

use actors_rust_components::MLPipeline;
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use std::collections::HashMap;

// ── helpers ───────────────────────────────────────────────────────────────────

fn feature_names(n: usize) -> Vec<String> {
    (0..n).map(|i| format!("feature_{i}")).collect()
}

fn make_records(num_records: usize, num_features: usize) -> Vec<HashMap<String, f64>> {
    let names = feature_names(num_features);
    (0..num_records)
        .map(|i| {
            names
                .iter()
                .enumerate()
                .map(|(j, name)| (name.clone(), (i * num_features + j) as f64))
                .collect()
        })
        .collect()
}

fn make_feature_vec(n: usize) -> Vec<f64> {
    (0..n).map(|i| i as f64 + 1.0).collect()
}

// ── process_training_data ─────────────────────────────────────────────────────

fn bench_process_training_data(c: &mut Criterion) {
    let mut group = c.benchmark_group("process_training_data");

    for &num_records in &[1_usize, 10, 100, 1_000] {
        for &num_features in &[3_usize, 10, 50] {
            let pipeline =
                MLPipeline::new("bench".to_string(), feature_names(num_features));
            let records = make_records(num_records, num_features);

            group.bench_with_input(
                BenchmarkId::new(format!("records={num_records}"), format!("features={num_features}")),
                &records,
                |b, data| {
                    b.iter(|| pipeline.process_training_data(data).unwrap());
                },
            );
        }
    }
    group.finish();
}

// ── predict ───────────────────────────────────────────────────────────────────

fn bench_predict(c: &mut Criterion) {
    let mut group = c.benchmark_group("predict");

    for &n in &[3_usize, 10, 50] {
        let pipeline = MLPipeline::new("bench".to_string(), feature_names(n));
        let features = make_feature_vec(n);

        group.bench_with_input(BenchmarkId::from_parameter(n), &features, |b, feat| {
            b.iter(|| pipeline.predict(feat).unwrap());
        });
    }
    group.finish();
}

// ── get_feature_importance ────────────────────────────────────────────────────

fn bench_get_feature_importance(c: &mut Criterion) {
    let mut group = c.benchmark_group("get_feature_importance");

    for &n in &[5_usize, 20, 100] {
        let pipeline = MLPipeline::new("bench".to_string(), feature_names(n));
        group.bench_with_input(BenchmarkId::from_parameter(n), &n, |b, _| {
            b.iter(|| pipeline.get_feature_importance());
        });
    }
    group.finish();
}

// ── criterion entry point ─────────────────────────────────────────────────────

criterion_group!(
    benches,
    bench_process_training_data,
    bench_predict,
    bench_get_feature_importance,
);
criterion_main!(benches);
