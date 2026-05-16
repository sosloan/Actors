# Native Audio and Parallelism Strategy (No JUCE/TBB)

This repository should prioritize native capabilities in the existing stack instead of introducing C++ framework dependencies.

## Audio Visualization

- Use browser-native **Web Audio API** and Canvas in the frontend layer.
- See: `/home/runner/work/Actors/Actors/examples/audio_causality_visualizer.html`

## Python Parallelism

- Use `concurrent.futures`, `multiprocessing`, or Ray (if distributed scale is needed).
- See: `/home/runner/work/Actors/Actors/examples/parallel_causality_visualizer.py`

## Go Parallelism

- Continue using goroutines + channels for agent message processing.
- Existing patterns: `/home/runner/work/Actors/Actors/GOS/time/`

## Rust Parallelism

- Prefer Tokio async for concurrent pipeline tasks and introduce Rayon only when benchmarks justify data-parallel execution.
- Existing async coordination example: `/home/runner/work/Actors/Actors/RUSTS/ml_pipeline.rs`

## C++/FFI Escalation Rule

Only consider Rust/C++ FFI (for TBB or DSP libraries) when:

1. A specific hotspot is identified through profiling.
2. Native Python/Go/Rust approaches fail to meet latency/throughput targets.
3. The benchmark gain outweighs maintenance and deployment complexity.
