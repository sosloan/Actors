#!/usr/bin/env python3
"""Tests for examples.parallel_causality_visualizer."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.parallel_causality_visualizer import (
    RegionTelemetry,
    compute_region_metric,
    generate_telemetry,
    parallel_causality_scores,
    summarize,
)


def test_generate_telemetry_deterministic():
    first = generate_telemetry(seed=123, n_regions=3)
    second = generate_telemetry(seed=123, n_regions=3)
    assert first == second


def test_generate_telemetry_bounds_and_sizes():
    assert generate_telemetry(seed=1, n_regions=0) == []

    telemetry = generate_telemetry(seed=7, n_regions=1)
    assert len(telemetry) == 1
    item = telemetry[0]
    assert 0.1 <= item.signal_strength <= 1.0
    assert 3_000 <= item.witness_load <= 30_000
    assert 0.4 <= item.jitter_ms <= 9.0


def test_compute_region_metric_shape_and_positive_score():
    region = RegionTelemetry(
        region="region-01",
        signal_strength=0.75,
        witness_load=3_000,
        jitter_ms=1.2,
    )
    name, score = compute_region_metric(region)
    assert name == "region-01"
    assert score > 0


def test_parallel_matches_sequential_for_same_inputs():
    telemetry = generate_telemetry(seed=99, n_regions=6)
    parallel = parallel_causality_scores(telemetry, workers=2)
    sequential = dict(compute_region_metric(t) for t in telemetry)
    assert parallel == sequential


def test_parallel_empty_input():
    assert parallel_causality_scores([], workers=2) == {}


def test_summarize_formats_top_regions():
    scores = {
        "region-a": 0.2,
        "region-b": 0.7,
        "region-c": 0.4,
        "region-d": 0.9,
        "region-e": 0.6,
        "region-f": 0.1,
    }
    output = summarize(scores)
    assert "Processed regions: 6" in output
    assert "Mean causality score:" in output
    assert "Top regions:" in output
    assert "region-d" in output


def test_summarize_empty_scores():
    output = summarize({})
    assert "Processed regions: 0" in output
    assert "Mean causality score: 0.0000" in output
