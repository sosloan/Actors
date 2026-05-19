package main

import (
	"testing"
	"time"
)

func TestNewMetricsCollector(t *testing.T) {
	mc := NewMetricsCollector()
	if mc == nil {
		t.Fatal("Expected non-nil MetricsCollector")
	}
	snapshot := mc.GetMetrics()
	if snapshot.OrderExecution.Total != 0 {
		t.Errorf("Expected 0 total order executions, got %d", snapshot.OrderExecution.Total)
	}
}

func TestRecordOrderExecution(t *testing.T) {
	mc := NewMetricsCollector()
	mc.RecordOrderExecution(true, 10*time.Millisecond)
	mc.RecordOrderExecution(true, 20*time.Millisecond)
	mc.RecordOrderExecution(false, 5*time.Millisecond)

	snap := mc.GetMetrics()
	if snap.OrderExecution.Total != 3 {
		t.Errorf("Expected 3 total, got %d", snap.OrderExecution.Total)
	}
	if snap.OrderExecution.Success != 2 {
		t.Errorf("Expected 2 successes, got %d", snap.OrderExecution.Success)
	}
	if snap.OrderExecution.Failed != 1 {
		t.Errorf("Expected 1 failure, got %d", snap.OrderExecution.Failed)
	}
}

func TestRecordPortfolioOptimization(t *testing.T) {
	mc := NewMetricsCollector()
	mc.RecordPortfolioOptimization(true, 50*time.Millisecond)
	mc.RecordPortfolioOptimization(false, 30*time.Millisecond)

	snap := mc.GetMetrics()
	if snap.PortfolioOptimization.Total != 2 {
		t.Errorf("Expected 2 total, got %d", snap.PortfolioOptimization.Total)
	}
	if snap.PortfolioOptimization.Success != 1 {
		t.Errorf("Expected 1 success, got %d", snap.PortfolioOptimization.Success)
	}
	if snap.PortfolioOptimization.Failed != 1 {
		t.Errorf("Expected 1 failure, got %d", snap.PortfolioOptimization.Failed)
	}
}

func TestRecordRiskCalculation(t *testing.T) {
	mc := NewMetricsCollector()
	mc.RecordRiskCalculation(true, 15*time.Millisecond)
	mc.RecordRiskCalculation(true, 25*time.Millisecond)

	snap := mc.GetMetrics()
	if snap.RiskCalculation.Total != 2 {
		t.Errorf("Expected 2 total, got %d", snap.RiskCalculation.Total)
	}
	if snap.RiskCalculation.Success != 2 {
		t.Errorf("Expected 2 successes, got %d", snap.RiskCalculation.Success)
	}
	if snap.RiskCalculation.Failed != 0 {
		t.Errorf("Expected 0 failures, got %d", snap.RiskCalculation.Failed)
	}
}

func TestRecordSpreadAnalysis(t *testing.T) {
	mc := NewMetricsCollector()
	mc.RecordSpreadAnalysis(false, 8*time.Millisecond)

	snap := mc.GetMetrics()
	if snap.SpreadAnalysis.Total != 1 {
		t.Errorf("Expected 1 total, got %d", snap.SpreadAnalysis.Total)
	}
	if snap.SpreadAnalysis.Failed != 1 {
		t.Errorf("Expected 1 failure, got %d", snap.SpreadAnalysis.Failed)
	}
}

func TestRecordCircuitBreakerEvent(t *testing.T) {
	mc := NewMetricsCollector()
	mc.RecordCircuitBreakerEvent("open")
	mc.RecordCircuitBreakerEvent("open")
	mc.RecordCircuitBreakerEvent("close")
	mc.RecordCircuitBreakerEvent("failure")
	mc.RecordCircuitBreakerEvent("unknown") // should be ignored gracefully

	snap := mc.GetMetrics()
	if snap.CircuitBreaker.Opens != 2 {
		t.Errorf("Expected 2 opens, got %d", snap.CircuitBreaker.Opens)
	}
	if snap.CircuitBreaker.Closes != 1 {
		t.Errorf("Expected 1 close, got %d", snap.CircuitBreaker.Closes)
	}
	if snap.CircuitBreaker.Failures != 1 {
		t.Errorf("Expected 1 failure, got %d", snap.CircuitBreaker.Failures)
	}
}

func TestUpdateSystemHealth(t *testing.T) {
	mc := NewMetricsCollector()
	mc.UpdateSystemHealth(42, 1024*1024, 0.35)

	snap := mc.GetMetrics()
	if snap.SystemHealth.ActiveConnections != 42 {
		t.Errorf("Expected 42 active connections, got %d", snap.SystemHealth.ActiveConnections)
	}
	if snap.SystemHealth.MemoryUsage != 1024*1024 {
		t.Errorf("Expected 1MiB memory usage, got %d", snap.SystemHealth.MemoryUsage)
	}
	if snap.SystemHealth.CPUUsage != 0.35 {
		t.Errorf("Expected CPU usage 0.35, got %f", snap.SystemHealth.CPUUsage)
	}
	if snap.SystemHealth.LastHealthCheck.IsZero() {
		t.Error("Expected LastHealthCheck to be set")
	}
}

func TestMetricsAverageLatency(t *testing.T) {
	mc := NewMetricsCollector()
	mc.RecordOrderExecution(true, 10*time.Millisecond)
	mc.RecordOrderExecution(true, 20*time.Millisecond)
	mc.RecordOrderExecution(true, 30*time.Millisecond)

	snap := mc.GetMetrics()
	expected := 20 * time.Millisecond
	if snap.OrderExecution.Latency != expected {
		t.Errorf("Expected average latency %v, got %v", expected, snap.OrderExecution.Latency)
	}
}

func TestMetricsLatencyWindowCap(t *testing.T) {
	mc := NewMetricsCollector()
	// Record more than 1000 entries to trigger the sliding window cap
	for i := 0; i < 1050; i++ {
		mc.RecordOrderExecution(true, time.Duration(i)*time.Microsecond)
	}
	// Should not panic and total should reflect all 1050 recordings
	snap := mc.GetMetrics()
	if snap.OrderExecution.Total != 1050 {
		t.Errorf("Expected 1050 total executions, got %d", snap.OrderExecution.Total)
	}
}
