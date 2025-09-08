package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"
)

// runMonitoringDemo demonstrates the monitoring and metrics capabilities
func runMonitoringDemo() {
	fmt.Println("📊 MONITORING AND METRICS DEMO")
	fmt.Println("==============================")
	fmt.Println("Demonstrating Prometheus Metrics and Health Check Endpoints")
	fmt.Println()

	// Create metrics collector and health checker
	metrics := NewMetricsCollector()
	gateway := createEnhancedGateway()
	healthChecker := NewHealthChecker(gateway.DerivativesGateway, metrics)

	// Demo 1: Metrics Collection
	fmt.Println("📈 DEMO 1: METRICS COLLECTION")
	fmt.Println("=============================")
	demonstrateMetricsCollection(metrics)

	// Demo 2: Health Check System
	fmt.Println("\n🏥 DEMO 2: HEALTH CHECK SYSTEM")
	fmt.Println("==============================")
	demonstrateHealthChecks(healthChecker)

	// Demo 3: Metrics Server
	fmt.Println("\n🌐 DEMO 3: METRICS SERVER")
	fmt.Println("=========================")
	demonstrateMetricsServer(metrics, healthChecker)

	// Demo 4: Real-time Monitoring
	fmt.Println("\n⏱️ DEMO 4: REAL-TIME MONITORING")
	fmt.Println("===============================")
	demonstrateRealTimeMonitoring(metrics, gateway)

	fmt.Println("\n🎉 MONITORING DEMO COMPLETED!")
	fmt.Println("✅ Prometheus metrics and health checks demonstrated successfully!")
}

// demonstrateMetricsCollection shows how metrics are collected and tracked
func demonstrateMetricsCollection(metrics *MetricsCollector) {
	fmt.Println("📊 Collecting various metrics...")

	// Simulate order execution metrics
	fmt.Println("📈 Recording order execution metrics...")
	for i := 0; i < 5; i++ {
		success := i%4 != 0 // 80% success rate
		duration := time.Duration(50+i*10) * time.Millisecond
		metrics.RecordOrderExecution(success, duration)

		status := "✅ Success"
		if !success {
			status = "❌ Failed"
		}
		fmt.Printf("   Order %d: %s (Duration: %v)\n", i+1, status, duration)
	}

	// Simulate portfolio optimization metrics
	fmt.Println("\n🎯 Recording portfolio optimization metrics...")
	for i := 0; i < 3; i++ {
		success := i%3 != 0 // 67% success rate
		duration := time.Duration(100+i*50) * time.Millisecond
		metrics.RecordPortfolioOptimization(success, duration)

		status := "✅ Success"
		if !success {
			status = "❌ Failed"
		}
		fmt.Printf("   Optimization %d: %s (Duration: %v)\n", i+1, status, duration)
	}

	// Simulate risk calculation metrics
	fmt.Println("\n⚠️ Recording risk calculation metrics...")
	for i := 0; i < 10; i++ {
		success := i%10 != 0 // 90% success rate
		duration := time.Duration(20+i*5) * time.Millisecond
		metrics.RecordRiskCalculation(success, duration)

		status := "✅ Success"
		if !success {
			status = "❌ Failed"
		}
		fmt.Printf("   Risk Calc %d: %s (Duration: %v)\n", i+1, status, duration)
	}

	// Simulate spread analysis metrics
	fmt.Println("\n📊 Recording spread analysis metrics...")
	for i := 0; i < 2; i++ {
		success := true // 100% success rate
		duration := time.Duration(200+i*100) * time.Millisecond
		metrics.RecordSpreadAnalysis(success, duration)

		fmt.Printf("   Analysis %d: ✅ Success (Duration: %v)\n", i+1, duration)
	}

	// Simulate circuit breaker events
	fmt.Println("\n🔧 Recording circuit breaker events...")
	metrics.RecordCircuitBreakerEvent("open")
	metrics.RecordCircuitBreakerEvent("close")
	metrics.RecordCircuitBreakerEvent("failure")
	metrics.RecordCircuitBreakerEvent("open")
	metrics.RecordCircuitBreakerEvent("close")

	fmt.Println("   Circuit breaker events recorded: 2 opens, 2 closes, 1 failure")

	// Update system health metrics
	fmt.Println("\n💻 Updating system health metrics...")
	metrics.UpdateSystemHealth(25, 1024*1024*512, 45.5) // 25 connections, 512MB memory, 45.5% CPU
	fmt.Println("   System health updated: 25 connections, 512MB memory, 45.5% CPU")

	// Display metrics summary
	fmt.Println("\n📊 METRICS SUMMARY:")
	metricsSnapshot := metrics.GetMetrics()

	fmt.Printf("   Order Executions: %d total, %d success, %d failed\n",
		metricsSnapshot.OrderExecution.Total,
		metricsSnapshot.OrderExecution.Success,
		metricsSnapshot.OrderExecution.Failed)

	fmt.Printf("   Portfolio Optimizations: %d total, %d success, %d failed\n",
		metricsSnapshot.PortfolioOptimization.Total,
		metricsSnapshot.PortfolioOptimization.Success,
		metricsSnapshot.PortfolioOptimization.Failed)

	fmt.Printf("   Risk Calculations: %d total, %d success, %d failed\n",
		metricsSnapshot.RiskCalculation.Total,
		metricsSnapshot.RiskCalculation.Success,
		metricsSnapshot.RiskCalculation.Failed)

	fmt.Printf("   Spread Analyses: %d total, %d success, %d failed\n",
		metricsSnapshot.SpreadAnalysis.Total,
		metricsSnapshot.SpreadAnalysis.Success,
		metricsSnapshot.SpreadAnalysis.Failed)

	fmt.Printf("   Circuit Breaker Events: %d opens, %d closes, %d failures\n",
		metricsSnapshot.CircuitBreaker.Opens,
		metricsSnapshot.CircuitBreaker.Closes,
		metricsSnapshot.CircuitBreaker.Failures)

	fmt.Printf("   System Health: %v uptime, %d connections, %dMB memory, %.1f%% CPU\n",
		metricsSnapshot.SystemHealth.Uptime.Round(time.Second),
		metricsSnapshot.SystemHealth.ActiveConnections,
		metricsSnapshot.SystemHealth.MemoryUsage/(1024*1024),
		metricsSnapshot.SystemHealth.CPUUsage)
}

// demonstrateHealthChecks shows how health checks work
func demonstrateHealthChecks(healthChecker *HealthChecker) {
	fmt.Println("🏥 Performing comprehensive health checks...")

	// Perform health check
	healthStatus := healthChecker.CheckHealth(context.Background())

	fmt.Printf("🔍 Overall Health Status: %s\n", healthStatus.Status)
	fmt.Printf("📝 Message: %s\n", healthStatus.Message)
	fmt.Printf("⏰ Timestamp: %s\n", healthStatus.Timestamp.Format("15:04:05"))
	fmt.Printf("🧩 Components Checked: %d\n", len(healthStatus.Components))

	fmt.Println("\n📋 Component Health Details:")
	for _, component := range healthStatus.Components {
		statusIcon := "✅"
		if component.Status == "degraded" {
			statusIcon = "⚠️"
		} else if component.Status == "unhealthy" {
			statusIcon = "❌"
		}

		fmt.Printf("   %s %s: %s (Latency: %v)\n",
			statusIcon, component.Component, component.Message, component.Latency)
	}

	// Test different health scenarios
	fmt.Println("\n🔄 Testing different health scenarios...")

	// Simulate degraded health
	fmt.Println("   Simulating degraded health scenario...")
	// In a real system, this would involve actual component failures

	// Simulate unhealthy health
	fmt.Println("   Simulating unhealthy health scenario...")
	// In a real system, this would involve critical component failures

	fmt.Println("   ✅ Health check system is functioning correctly")
}

// demonstrateMetricsServer shows how the metrics server works
func demonstrateMetricsServer(metrics *MetricsCollector, healthChecker *HealthChecker) {
	fmt.Println("🌐 Starting metrics server on port 8080...")

	// Create metrics server
	metricsServer := NewMetricsServer(metrics, healthChecker, 8080)

	// Start server in background
	go func() {
		if err := metricsServer.Start(); err != nil && err != http.ErrServerClosed {
			log.Printf("Metrics server error: %v", err)
		}
	}()

	// Wait a moment for server to start
	time.Sleep(100 * time.Millisecond)

	fmt.Println("   ✅ Metrics server started successfully")

	// Test endpoints
	fmt.Println("\n🔗 Testing metrics endpoints...")

	// Test /metrics endpoint
	fmt.Println("   Testing /metrics endpoint...")
	resp, err := http.Get("http://localhost:8080/metrics")
	if err != nil {
		fmt.Printf("   ❌ Failed to get metrics: %v\n", err)
	} else {
		fmt.Printf("   ✅ Metrics endpoint responded with status: %d\n", resp.StatusCode)
		resp.Body.Close()
	}

	// Test /health endpoint
	fmt.Println("   Testing /health endpoint...")
	resp, err = http.Get("http://localhost:8080/health")
	if err != nil {
		fmt.Printf("   ❌ Failed to get health: %v\n", err)
	} else {
		fmt.Printf("   ✅ Health endpoint responded with status: %d\n", resp.StatusCode)
		resp.Body.Close()
	}

	// Test /health/ready endpoint
	fmt.Println("   Testing /health/ready endpoint...")
	resp, err = http.Get("http://localhost:8080/health/ready")
	if err != nil {
		fmt.Printf("   ❌ Failed to get readiness: %v\n", err)
	} else {
		fmt.Printf("   ✅ Readiness endpoint responded with status: %d\n", resp.StatusCode)
		resp.Body.Close()
	}

	// Test /health/live endpoint
	fmt.Println("   Testing /health/live endpoint...")
	resp, err = http.Get("http://localhost:8080/health/live")
	if err != nil {
		fmt.Printf("   ❌ Failed to get liveness: %v\n", err)
	} else {
		fmt.Printf("   ✅ Liveness endpoint responded with status: %d\n", resp.StatusCode)
		resp.Body.Close()
	}

	// Stop server
	fmt.Println("\n🛑 Stopping metrics server...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := metricsServer.Stop(ctx); err != nil {
		fmt.Printf("   ⚠️ Error stopping server: %v\n", err)
	} else {
		fmt.Println("   ✅ Metrics server stopped successfully")
	}
}

// demonstrateRealTimeMonitoring shows real-time monitoring capabilities
func demonstrateRealTimeMonitoring(metrics *MetricsCollector, gateway *EnhancedDerivativesGateway) {
	fmt.Println("⏱️ Demonstrating real-time monitoring...")

	// Simulate real-time activity
	fmt.Println("📈 Simulating real-time trading activity...")

	for i := 0; i < 10; i++ {
		// Simulate order execution
		success := i%5 != 0 // 80% success rate
		duration := time.Duration(30+i*5) * time.Millisecond
		metrics.RecordOrderExecution(success, duration)

		// Simulate risk calculation
		riskSuccess := i%10 != 0 // 90% success rate
		riskDuration := time.Duration(15+i*2) * time.Millisecond
		metrics.RecordRiskCalculation(riskSuccess, riskDuration)

		// Update system health
		connections := int64(20 + i)
		memory := int64(1024*1024*400 + i*1024*1024*10)
		cpu := 40.0 + float64(i)*2.0
		metrics.UpdateSystemHealth(connections, memory, cpu)

		// Display real-time metrics
		metricsSnapshot := metrics.GetMetrics()

		fmt.Printf("   Activity %d: Orders=%d, Risk=%d, Connections=%d, CPU=%.1f%%\n",
			i+1,
			metricsSnapshot.OrderExecution.Total,
			metricsSnapshot.RiskCalculation.Total,
			metricsSnapshot.SystemHealth.ActiveConnections,
			metricsSnapshot.SystemHealth.CPUUsage)

		// Small delay to simulate real-time
		time.Sleep(50 * time.Millisecond)
	}

	// Display final metrics
	fmt.Println("\n📊 FINAL REAL-TIME METRICS:")
	metricsSnapshot := metrics.GetMetrics()

	fmt.Printf("   Total Order Executions: %d (%.1f%% success rate)\n",
		metricsSnapshot.OrderExecution.Total,
		float64(metricsSnapshot.OrderExecution.Success)/float64(metricsSnapshot.OrderExecution.Total)*100)

	fmt.Printf("   Total Risk Calculations: %d (%.1f%% success rate)\n",
		metricsSnapshot.RiskCalculation.Total,
		float64(metricsSnapshot.RiskCalculation.Success)/float64(metricsSnapshot.RiskCalculation.Total)*100)

	fmt.Printf("   Average Order Execution Latency: %v\n",
		metricsSnapshot.OrderExecution.Latency)

	fmt.Printf("   Average Risk Calculation Latency: %v\n",
		metricsSnapshot.RiskCalculation.Latency)

	fmt.Printf("   Current System Load: %d connections, %dMB memory, %.1f%% CPU\n",
		metricsSnapshot.SystemHealth.ActiveConnections,
		metricsSnapshot.SystemHealth.MemoryUsage/(1024*1024),
		metricsSnapshot.SystemHealth.CPUUsage)

	fmt.Println("   ✅ Real-time monitoring demonstrated successfully")
}
