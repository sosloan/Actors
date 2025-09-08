package main

import (
	"context"
	"fmt"
	"net/http"
	"sync"
	"time"
)

// MetricsCollector collects and exposes metrics for the derivatives gateway
type MetricsCollector struct {
	// Order execution metrics
	orderExecutionsTotal   int64
	orderExecutionsSuccess int64
	orderExecutionsFailed  int64
	orderExecutionDuration time.Duration
	orderExecutionLatency  []time.Duration

	// Portfolio optimization metrics
	optimizationsTotal   int64
	optimizationsSuccess int64
	optimizationsFailed  int64
	optimizationDuration time.Duration
	optimizationLatency  []time.Duration

	// Risk calculation metrics
	riskCalculationsTotal   int64
	riskCalculationsSuccess int64
	riskCalculationsFailed  int64
	riskCalculationDuration time.Duration
	riskCalculationLatency  []time.Duration

	// Spread analysis metrics
	spreadAnalysesTotal    int64
	spreadAnalysesSuccess  int64
	spreadAnalysesFailed   int64
	spreadAnalysisDuration time.Duration
	spreadAnalysisLatency  []time.Duration

	// Circuit breaker metrics
	circuitBreakerOpens    int64
	circuitBreakerCloses   int64
	circuitBreakerFailures int64

	// System health metrics
	systemUptime      time.Duration
	lastHealthCheck   time.Time
	activeConnections int64
	memoryUsage       int64
	cpuUsage          float64

	// Mutex for thread safety
	mutex     sync.RWMutex
	startTime time.Time
}

// NewMetricsCollector creates a new metrics collector
func NewMetricsCollector() *MetricsCollector {
	return &MetricsCollector{
		startTime: time.Now(),
	}
}

// RecordOrderExecution records order execution metrics
func (mc *MetricsCollector) RecordOrderExecution(success bool, duration time.Duration) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	mc.orderExecutionsTotal++
	if success {
		mc.orderExecutionsSuccess++
	} else {
		mc.orderExecutionsFailed++
	}

	mc.orderExecutionDuration += duration
	mc.orderExecutionLatency = append(mc.orderExecutionLatency, duration)

	// Keep only last 1000 latency measurements
	if len(mc.orderExecutionLatency) > 1000 {
		mc.orderExecutionLatency = mc.orderExecutionLatency[1:]
	}
}

// RecordPortfolioOptimization records portfolio optimization metrics
func (mc *MetricsCollector) RecordPortfolioOptimization(success bool, duration time.Duration) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	mc.optimizationsTotal++
	if success {
		mc.optimizationsSuccess++
	} else {
		mc.optimizationsFailed++
	}

	mc.optimizationDuration += duration
	mc.optimizationLatency = append(mc.optimizationLatency, duration)

	// Keep only last 1000 latency measurements
	if len(mc.optimizationLatency) > 1000 {
		mc.optimizationLatency = mc.optimizationLatency[1:]
	}
}

// RecordRiskCalculation records risk calculation metrics
func (mc *MetricsCollector) RecordRiskCalculation(success bool, duration time.Duration) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	mc.riskCalculationsTotal++
	if success {
		mc.riskCalculationsSuccess++
	} else {
		mc.riskCalculationsFailed++
	}

	mc.riskCalculationDuration += duration
	mc.riskCalculationLatency = append(mc.riskCalculationLatency, duration)

	// Keep only last 1000 latency measurements
	if len(mc.riskCalculationLatency) > 1000 {
		mc.riskCalculationLatency = mc.riskCalculationLatency[1:]
	}
}

// RecordSpreadAnalysis records spread analysis metrics
func (mc *MetricsCollector) RecordSpreadAnalysis(success bool, duration time.Duration) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	mc.spreadAnalysesTotal++
	if success {
		mc.spreadAnalysesSuccess++
	} else {
		mc.spreadAnalysesFailed++
	}

	mc.spreadAnalysisDuration += duration
	mc.spreadAnalysisLatency = append(mc.spreadAnalysisLatency, duration)

	// Keep only last 1000 latency measurements
	if len(mc.spreadAnalysisLatency) > 1000 {
		mc.spreadAnalysisLatency = mc.spreadAnalysisLatency[1:]
	}
}

// RecordCircuitBreakerEvent records circuit breaker events
func (mc *MetricsCollector) RecordCircuitBreakerEvent(eventType string) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	switch eventType {
	case "open":
		mc.circuitBreakerOpens++
	case "close":
		mc.circuitBreakerCloses++
	case "failure":
		mc.circuitBreakerFailures++
	}
}

// UpdateSystemHealth updates system health metrics
func (mc *MetricsCollector) UpdateSystemHealth(activeConnections int64, memoryUsage int64, cpuUsage float64) {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()

	mc.activeConnections = activeConnections
	mc.memoryUsage = memoryUsage
	mc.cpuUsage = cpuUsage
	mc.lastHealthCheck = time.Now()
	mc.systemUptime = time.Since(mc.startTime)
}

// GetMetrics returns a snapshot of all metrics
func (mc *MetricsCollector) GetMetrics() MetricsSnapshot {
	mc.mutex.RLock()
	defer mc.mutex.RUnlock()

	return MetricsSnapshot{
		OrderExecution: OrderExecutionMetrics{
			Total:    mc.orderExecutionsTotal,
			Success:  mc.orderExecutionsSuccess,
			Failed:   mc.orderExecutionsFailed,
			Duration: mc.orderExecutionDuration,
			Latency:  mc.calculateAverageLatency(mc.orderExecutionLatency),
		},
		PortfolioOptimization: PortfolioOptimizationMetrics{
			Total:    mc.optimizationsTotal,
			Success:  mc.optimizationsSuccess,
			Failed:   mc.optimizationsFailed,
			Duration: mc.optimizationDuration,
			Latency:  mc.calculateAverageLatency(mc.optimizationLatency),
		},
		RiskCalculation: RiskCalculationMetrics{
			Total:    mc.riskCalculationsTotal,
			Success:  mc.riskCalculationsSuccess,
			Failed:   mc.riskCalculationsFailed,
			Duration: mc.riskCalculationDuration,
			Latency:  mc.calculateAverageLatency(mc.riskCalculationLatency),
		},
		SpreadAnalysis: SpreadAnalysisMetrics{
			Total:    mc.spreadAnalysesTotal,
			Success:  mc.spreadAnalysesSuccess,
			Failed:   mc.spreadAnalysesFailed,
			Duration: mc.spreadAnalysisDuration,
			Latency:  mc.calculateAverageLatency(mc.spreadAnalysisLatency),
		},
		CircuitBreaker: CircuitBreakerSystemMetrics{
			Opens:    mc.circuitBreakerOpens,
			Closes:   mc.circuitBreakerCloses,
			Failures: mc.circuitBreakerFailures,
		},
		SystemHealth: SystemHealthMetrics{
			Uptime:            mc.systemUptime,
			LastHealthCheck:   mc.lastHealthCheck,
			ActiveConnections: mc.activeConnections,
			MemoryUsage:       mc.memoryUsage,
			CPUUsage:          mc.cpuUsage,
		},
	}
}

// calculateAverageLatency calculates the average latency from a slice of durations
func (mc *MetricsCollector) calculateAverageLatency(latencies []time.Duration) time.Duration {
	if len(latencies) == 0 {
		return 0
	}

	total := time.Duration(0)
	for _, latency := range latencies {
		total += latency
	}

	return total / time.Duration(len(latencies))
}

// MetricsSnapshot represents a snapshot of all metrics
type MetricsSnapshot struct {
	OrderExecution        OrderExecutionMetrics        `json:"order_execution"`
	PortfolioOptimization PortfolioOptimizationMetrics `json:"portfolio_optimization"`
	RiskCalculation       RiskCalculationMetrics       `json:"risk_calculation"`
	SpreadAnalysis        SpreadAnalysisMetrics        `json:"spread_analysis"`
	CircuitBreaker        CircuitBreakerSystemMetrics  `json:"circuit_breaker"`
	SystemHealth          SystemHealthMetrics          `json:"system_health"`
}

// OrderExecutionMetrics contains order execution metrics
type OrderExecutionMetrics struct {
	Total    int64         `json:"total"`
	Success  int64         `json:"success"`
	Failed   int64         `json:"failed"`
	Duration time.Duration `json:"duration"`
	Latency  time.Duration `json:"average_latency"`
}

// PortfolioOptimizationMetrics contains portfolio optimization metrics
type PortfolioOptimizationMetrics struct {
	Total    int64         `json:"total"`
	Success  int64         `json:"success"`
	Failed   int64         `json:"failed"`
	Duration time.Duration `json:"duration"`
	Latency  time.Duration `json:"average_latency"`
}

// RiskCalculationMetrics contains risk calculation metrics
type RiskCalculationMetrics struct {
	Total    int64         `json:"total"`
	Success  int64         `json:"success"`
	Failed   int64         `json:"failed"`
	Duration time.Duration `json:"duration"`
	Latency  time.Duration `json:"average_latency"`
}

// SpreadAnalysisMetrics contains spread analysis metrics
type SpreadAnalysisMetrics struct {
	Total    int64         `json:"total"`
	Success  int64         `json:"success"`
	Failed   int64         `json:"failed"`
	Duration time.Duration `json:"duration"`
	Latency  time.Duration `json:"average_latency"`
}

// CircuitBreakerSystemMetrics contains circuit breaker system metrics
type CircuitBreakerSystemMetrics struct {
	Opens    int64 `json:"opens"`
	Closes   int64 `json:"closes"`
	Failures int64 `json:"failures"`
}

// SystemHealthMetrics contains system health metrics
type SystemHealthMetrics struct {
	Uptime            time.Duration `json:"uptime"`
	LastHealthCheck   time.Time     `json:"last_health_check"`
	ActiveConnections int64         `json:"active_connections"`
	MemoryUsage       int64         `json:"memory_usage_bytes"`
	CPUUsage          float64       `json:"cpu_usage_percent"`
}

// HealthChecker performs health checks on system components
type HealthChecker struct {
	gateway *DerivativesGateway
	metrics *MetricsCollector
}

// NewHealthChecker creates a new health checker
func NewHealthChecker(gateway *DerivativesGateway, metrics *MetricsCollector) *HealthChecker {
	return &HealthChecker{
		gateway: gateway,
		metrics: metrics,
	}
}

// HealthStatus represents the health status of a component
type HealthStatus struct {
	Component string        `json:"component"`
	Status    string        `json:"status"` // "healthy", "degraded", "unhealthy"
	Message   string        `json:"message"`
	Timestamp time.Time     `json:"timestamp"`
	Latency   time.Duration `json:"latency"`
}

// OverallHealthStatus represents the overall system health
type OverallHealthStatus struct {
	Status     string         `json:"status"` // "healthy", "degraded", "unhealthy"
	Message    string         `json:"message"`
	Timestamp  time.Time      `json:"timestamp"`
	Components []HealthStatus `json:"components"`
}

// CheckHealth performs comprehensive health checks
func (hc *HealthChecker) CheckHealth(ctx context.Context) *OverallHealthStatus {
	components := []HealthStatus{}

	// Check order router health
	orderRouterHealth := hc.checkOrderRouterHealth(ctx)
	components = append(components, orderRouterHealth)

	// Check portfolio optimizer health
	optimizerHealth := hc.checkPortfolioOptimizerHealth(ctx)
	components = append(components, optimizerHealth)

	// Check spread analyzer health
	analyzerHealth := hc.checkSpreadAnalyzerHealth(ctx)
	components = append(components, analyzerHealth)

	// Check expiration manager health
	managerHealth := hc.checkExpirationManagerHealth(ctx)
	components = append(components, managerHealth)

	// Check risk manager health
	riskManagerHealth := hc.checkRiskManagerHealth(ctx)
	components = append(components, riskManagerHealth)

	// Determine overall health status
	overallStatus := hc.determineOverallHealth(components)

	return &OverallHealthStatus{
		Status:     overallStatus,
		Message:    hc.getHealthMessage(overallStatus),
		Timestamp:  time.Now(),
		Components: components,
	}
}

// checkOrderRouterHealth checks the health of the order router
func (hc *HealthChecker) checkOrderRouterHealth(ctx context.Context) HealthStatus {
	startTime := time.Now()

	// Simulate a simple health check
	time.Sleep(1 * time.Millisecond)

	latency := time.Since(startTime)

	return HealthStatus{
		Component: "order_router",
		Status:    "healthy",
		Message:   "Order router is functioning normally",
		Timestamp: time.Now(),
		Latency:   latency,
	}
}

// checkPortfolioOptimizerHealth checks the health of the portfolio optimizer
func (hc *HealthChecker) checkPortfolioOptimizerHealth(ctx context.Context) HealthStatus {
	startTime := time.Now()

	// Simulate a simple health check
	time.Sleep(2 * time.Millisecond)

	latency := time.Since(startTime)

	return HealthStatus{
		Component: "portfolio_optimizer",
		Status:    "healthy",
		Message:   "Portfolio optimizer is functioning normally",
		Timestamp: time.Now(),
		Latency:   latency,
	}
}

// checkSpreadAnalyzerHealth checks the health of the spread analyzer
func (hc *HealthChecker) checkSpreadAnalyzerHealth(ctx context.Context) HealthStatus {
	startTime := time.Now()

	// Simulate a simple health check
	time.Sleep(1 * time.Millisecond)

	latency := time.Since(startTime)

	return HealthStatus{
		Component: "spread_analyzer",
		Status:    "healthy",
		Message:   "Spread analyzer is functioning normally",
		Timestamp: time.Now(),
		Latency:   latency,
	}
}

// checkExpirationManagerHealth checks the health of the expiration manager
func (hc *HealthChecker) checkExpirationManagerHealth(ctx context.Context) HealthStatus {
	startTime := time.Now()

	// Simulate a simple health check
	time.Sleep(1 * time.Millisecond)

	latency := time.Since(startTime)

	return HealthStatus{
		Component: "expiration_manager",
		Status:    "healthy",
		Message:   "Expiration manager is functioning normally",
		Timestamp: time.Now(),
		Latency:   latency,
	}
}

// checkRiskManagerHealth checks the health of the risk manager
func (hc *HealthChecker) checkRiskManagerHealth(ctx context.Context) HealthStatus {
	startTime := time.Now()

	// Simulate a simple health check
	time.Sleep(1 * time.Millisecond)

	latency := time.Since(startTime)

	return HealthStatus{
		Component: "risk_manager",
		Status:    "healthy",
		Message:   "Risk manager is functioning normally",
		Timestamp: time.Now(),
		Latency:   latency,
	}
}

// determineOverallHealth determines the overall health status based on component health
func (hc *HealthChecker) determineOverallHealth(components []HealthStatus) string {
	unhealthyCount := 0
	degradedCount := 0

	for _, component := range components {
		switch component.Status {
		case "unhealthy":
			unhealthyCount++
		case "degraded":
			degradedCount++
		}
	}

	if unhealthyCount > 0 {
		return "unhealthy"
	} else if degradedCount > 0 {
		return "degraded"
	}

	return "healthy"
}

// getHealthMessage returns a human-readable health message
func (hc *HealthChecker) getHealthMessage(status string) string {
	switch status {
	case "healthy":
		return "All systems are operating normally"
	case "degraded":
		return "Some systems are experiencing issues but core functionality is available"
	case "unhealthy":
		return "Critical systems are experiencing issues"
	default:
		return "Health status unknown"
	}
}

// MetricsServer serves metrics and health check endpoints
type MetricsServer struct {
	metrics       *MetricsCollector
	healthChecker *HealthChecker
	server        *http.Server
}

// NewMetricsServer creates a new metrics server
func NewMetricsServer(metrics *MetricsCollector, healthChecker *HealthChecker, port int) *MetricsServer {
	mux := http.NewServeMux()

	server := &MetricsServer{
		metrics:       metrics,
		healthChecker: healthChecker,
		server: &http.Server{
			Addr:    fmt.Sprintf(":%d", port),
			Handler: mux,
		},
	}

	// Register endpoints
	mux.HandleFunc("/metrics", server.handleMetrics)
	mux.HandleFunc("/health", server.handleHealth)
	mux.HandleFunc("/health/ready", server.handleReadiness)
	mux.HandleFunc("/health/live", server.handleLiveness)

	return server
}

// Start starts the metrics server
func (ms *MetricsServer) Start() error {
	return ms.server.ListenAndServe()
}

// Stop stops the metrics server
func (ms *MetricsServer) Stop(ctx context.Context) error {
	return ms.server.Shutdown(ctx)
}

// handleMetrics handles the /metrics endpoint
func (ms *MetricsServer) handleMetrics(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	metrics := ms.metrics.GetMetrics()

	// Convert to Prometheus format (simplified)
	prometheusMetrics := ms.convertToPrometheusFormat(metrics)

	w.WriteHeader(http.StatusOK)
	w.Write([]byte(prometheusMetrics))
}

// handleHealth handles the /health endpoint
func (ms *MetricsServer) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	healthStatus := ms.healthChecker.CheckHealth(r.Context())

	statusCode := http.StatusOK
	if healthStatus.Status == "unhealthy" {
		statusCode = http.StatusServiceUnavailable
	} else if healthStatus.Status == "degraded" {
		statusCode = http.StatusOK // Still OK but with warnings
	}

	w.WriteHeader(statusCode)

	// Convert to JSON (simplified)
	jsonResponse := fmt.Sprintf(`{
		"status": "%s",
		"message": "%s",
		"timestamp": "%s",
		"components": %d
	}`, healthStatus.Status, healthStatus.Message,
		healthStatus.Timestamp.Format(time.RFC3339), len(healthStatus.Components))

	w.Write([]byte(jsonResponse))
}

// handleReadiness handles the /health/ready endpoint
func (ms *MetricsServer) handleReadiness(w http.ResponseWriter, r *http.Request) {
	healthStatus := ms.healthChecker.CheckHealth(r.Context())

	if healthStatus.Status == "healthy" || healthStatus.Status == "degraded" {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("ready"))
	} else {
		w.WriteHeader(http.StatusServiceUnavailable)
		w.Write([]byte("not ready"))
	}
}

// handleLiveness handles the /health/live endpoint
func (ms *MetricsServer) handleLiveness(w http.ResponseWriter, r *http.Request) {
	// Simple liveness check - if we can respond, we're alive
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("alive"))
}

// convertToPrometheusFormat converts metrics to Prometheus format
func (ms *MetricsServer) convertToPrometheusFormat(metrics MetricsSnapshot) string {
	// Simplified Prometheus format
	return fmt.Sprintf(`# HELP derivatives_gateway_order_executions_total Total number of order executions
# TYPE derivatives_gateway_order_executions_total counter
derivatives_gateway_order_executions_total %d

# HELP derivatives_gateway_order_executions_success_total Total number of successful order executions
# TYPE derivatives_gateway_order_executions_success_total counter
derivatives_gateway_order_executions_success_total %d

# HELP derivatives_gateway_order_executions_failed_total Total number of failed order executions
# TYPE derivatives_gateway_order_executions_failed_total counter
derivatives_gateway_order_executions_failed_total %d

# HELP derivatives_gateway_order_execution_duration_seconds Total duration of order executions
# TYPE derivatives_gateway_order_execution_duration_seconds counter
derivatives_gateway_order_execution_duration_seconds %f

# HELP derivatives_gateway_order_execution_latency_seconds Average latency of order executions
# TYPE derivatives_gateway_order_execution_latency_seconds gauge
derivatives_gateway_order_execution_latency_seconds %f

# HELP derivatives_gateway_portfolio_optimizations_total Total number of portfolio optimizations
# TYPE derivatives_gateway_portfolio_optimizations_total counter
derivatives_gateway_portfolio_optimizations_total %d

# HELP derivatives_gateway_portfolio_optimizations_success_total Total number of successful portfolio optimizations
# TYPE derivatives_gateway_portfolio_optimizations_success_total counter
derivatives_gateway_portfolio_optimizations_success_total %d

# HELP derivatives_gateway_portfolio_optimizations_failed_total Total number of failed portfolio optimizations
# TYPE derivatives_gateway_portfolio_optimizations_failed_total counter
derivatives_gateway_portfolio_optimizations_failed_total %d

# HELP derivatives_gateway_portfolio_optimization_duration_seconds Total duration of portfolio optimizations
# TYPE derivatives_gateway_portfolio_optimization_duration_seconds counter
derivatives_gateway_portfolio_optimization_duration_seconds %f

# HELP derivatives_gateway_portfolio_optimization_latency_seconds Average latency of portfolio optimizations
# TYPE derivatives_gateway_portfolio_optimization_latency_seconds gauge
derivatives_gateway_portfolio_optimization_latency_seconds %f

# HELP derivatives_gateway_risk_calculations_total Total number of risk calculations
# TYPE derivatives_gateway_risk_calculations_total counter
derivatives_gateway_risk_calculations_total %d

# HELP derivatives_gateway_risk_calculations_success_total Total number of successful risk calculations
# TYPE derivatives_gateway_risk_calculations_success_total counter
derivatives_gateway_risk_calculations_success_total %d

# HELP derivatives_gateway_risk_calculations_failed_total Total number of failed risk calculations
# TYPE derivatives_gateway_risk_calculations_failed_total counter
derivatives_gateway_risk_calculations_failed_total %d

# HELP derivatives_gateway_risk_calculation_duration_seconds Total duration of risk calculations
# TYPE derivatives_gateway_risk_calculation_duration_seconds counter
derivatives_gateway_risk_calculation_duration_seconds %f

# HELP derivatives_gateway_risk_calculation_latency_seconds Average latency of risk calculations
# TYPE derivatives_gateway_risk_calculation_latency_seconds gauge
derivatives_gateway_risk_calculation_latency_seconds %f

# HELP derivatives_gateway_spread_analyses_total Total number of spread analyses
# TYPE derivatives_gateway_spread_analyses_total counter
derivatives_gateway_spread_analyses_total %d

# HELP derivatives_gateway_spread_analyses_success_total Total number of successful spread analyses
# TYPE derivatives_gateway_spread_analyses_success_total counter
derivatives_gateway_spread_analyses_success_total %d

# HELP derivatives_gateway_spread_analyses_failed_total Total number of failed spread analyses
# TYPE derivatives_gateway_spread_analyses_failed_total counter
derivatives_gateway_spread_analyses_failed_total %d

# HELP derivatives_gateway_spread_analysis_duration_seconds Total duration of spread analyses
# TYPE derivatives_gateway_spread_analysis_duration_seconds counter
derivatives_gateway_spread_analysis_duration_seconds %f

# HELP derivatives_gateway_spread_analysis_latency_seconds Average latency of spread analyses
# TYPE derivatives_gateway_spread_analysis_latency_seconds gauge
derivatives_gateway_spread_analysis_latency_seconds %f

# HELP derivatives_gateway_circuit_breaker_opens_total Total number of circuit breaker opens
# TYPE derivatives_gateway_circuit_breaker_opens_total counter
derivatives_gateway_circuit_breaker_opens_total %d

# HELP derivatives_gateway_circuit_breaker_closes_total Total number of circuit breaker closes
# TYPE derivatives_gateway_circuit_breaker_closes_total counter
derivatives_gateway_circuit_breaker_closes_total %d

# HELP derivatives_gateway_circuit_breaker_failures_total Total number of circuit breaker failures
# TYPE derivatives_gateway_circuit_breaker_failures_total counter
derivatives_gateway_circuit_breaker_failures_total %d

# HELP derivatives_gateway_system_uptime_seconds System uptime in seconds
# TYPE derivatives_gateway_system_uptime_seconds gauge
derivatives_gateway_system_uptime_seconds %f

# HELP derivatives_gateway_active_connections System active connections
# TYPE derivatives_gateway_active_connections gauge
derivatives_gateway_active_connections %d

# HELP derivatives_gateway_memory_usage_bytes System memory usage in bytes
# TYPE derivatives_gateway_memory_usage_bytes gauge
derivatives_gateway_memory_usage_bytes %d

# HELP derivatives_gateway_cpu_usage_percent System CPU usage percentage
# TYPE derivatives_gateway_cpu_usage_percent gauge
derivatives_gateway_cpu_usage_percent %f
`,
		metrics.OrderExecution.Total,
		metrics.OrderExecution.Success,
		metrics.OrderExecution.Failed,
		metrics.OrderExecution.Duration.Seconds(),
		metrics.OrderExecution.Latency.Seconds(),
		metrics.PortfolioOptimization.Total,
		metrics.PortfolioOptimization.Success,
		metrics.PortfolioOptimization.Failed,
		metrics.PortfolioOptimization.Duration.Seconds(),
		metrics.PortfolioOptimization.Latency.Seconds(),
		metrics.RiskCalculation.Total,
		metrics.RiskCalculation.Success,
		metrics.RiskCalculation.Failed,
		metrics.RiskCalculation.Duration.Seconds(),
		metrics.RiskCalculation.Latency.Seconds(),
		metrics.SpreadAnalysis.Total,
		metrics.SpreadAnalysis.Success,
		metrics.SpreadAnalysis.Failed,
		metrics.SpreadAnalysis.Duration.Seconds(),
		metrics.SpreadAnalysis.Latency.Seconds(),
		metrics.CircuitBreaker.Opens,
		metrics.CircuitBreaker.Closes,
		metrics.CircuitBreaker.Failures,
		metrics.SystemHealth.Uptime.Seconds(),
		metrics.SystemHealth.ActiveConnections,
		metrics.SystemHealth.MemoryUsage,
		metrics.SystemHealth.CPUUsage,
	)
}
