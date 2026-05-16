#!/usr/bin/env python3
"""
Parallel causality processing demo for ACTORS using Python-native concurrency.

This avoids external C++ dependencies (JUCE/TBB) while showing:
- Parallel region-level workload processing via ProcessPoolExecutor
- Aggregated causality metrics for visualization
- Optional matplotlib rendering for quick graph insight
"""

from __future__ import annotations

import argparse
import math
import random
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class RegionTelemetry:
    """Synthetic telemetry for a region in the causality graph."""

    region: str
    signal_strength: float
    witness_load: int
    jitter_ms: float


def generate_telemetry(seed: int, n_regions: int) -> List[RegionTelemetry]:
    """Create deterministic synthetic telemetry data."""
    random.seed(seed)
    regions = []
    for i in range(n_regions):
        regions.append(
            RegionTelemetry(
                region=f"region-{i + 1:02d}",
                signal_strength=random.uniform(0.1, 1.0),
                witness_load=random.randint(3_000, 30_000),
                jitter_ms=random.uniform(0.4, 9.0),
            )
        )
    return regions


def compute_region_metric(region: RegionTelemetry) -> Tuple[str, float]:
    """CPU-heavy simulation for causality/witness verification scoring."""
    loops = max(1_000, region.witness_load // 2)
    accumulator = 0.0

    for i in range(1, loops + 1):
        harmonic = math.sin(i * 0.0007) + math.cos(i * 0.0011)
        load_factor = math.sqrt(region.witness_load / (i + 1))
        accumulator += abs(harmonic) * load_factor

    score = (
        region.signal_strength * 0.58
        + (1.0 / (1.0 + region.jitter_ms)) * 0.22
        + (accumulator / loops) * 0.20
    )
    return region.region, score


def parallel_causality_scores(
    telemetry: List[RegionTelemetry], workers: int
) -> Dict[str, float]:
    """Compute regional scores in parallel."""
    with ProcessPoolExecutor(max_workers=workers) as executor:
        pairs = list(executor.map(compute_region_metric, telemetry))
    return dict(pairs)


def summarize(scores: Dict[str, float]) -> str:
    """Format summary for CLI output."""
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    values = list(scores.values())
    lines = [
        f"Processed regions: {len(scores)}",
        f"Mean causality score: {mean(values):.4f}",
        "Top regions:",
    ]
    lines.extend([f"  - {name}: {score:.4f}" for name, score in top])
    return "\n".join(lines)


def plot_scores(scores: Dict[str, float]) -> None:
    """Optional matplotlib bar chart rendering."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; skipping plot.")
        return

    items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    labels = [name for name, _ in items]
    values = [value for _, value in items]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values, color="#60a5fa")
    plt.title("ACTORS Parallel Causality Scores (Python native concurrency)")
    plt.xlabel("Region")
    plt.ylabel("Score")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--regions",
        type=int,
        default=18,
        help="Number of synthetic telemetry regions to simulate.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of process workers for parallel scoring.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used for deterministic telemetry generation.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Render a matplotlib bar chart of region scores.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    telemetry = generate_telemetry(seed=args.seed, n_regions=args.regions)

    started = time.perf_counter()
    scores = parallel_causality_scores(telemetry, workers=args.workers)
    duration = time.perf_counter() - started

    print(summarize(scores))
    print(f"Elapsed (parallel): {duration:.3f}s with {args.workers} workers")

    if args.plot:
        plot_scores(scores)


if __name__ == "__main__":
    main()
