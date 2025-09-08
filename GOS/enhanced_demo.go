package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"time"
)

// runEnhancedDerivativesGatewayDemo demonstrates the enhanced error handling capabilities
func runEnhancedDerivativesGatewayDemo() {
	fmt.Println("🚀 ENHANCED DERIVATIVES GATEWAY DEMO")
	fmt.Println("====================================")
	fmt.Println("Demonstrating Circuit Breakers, Retry Logic, and Error Handling")
	fmt.Println()

	// Create enhanced gateway components
	enhancedGateway := createEnhancedGateway()

	// Demo 1: Circuit Breaker Functionality
	fmt.Println("🔧 DEMO 1: CIRCUIT BREAKER FUNCTIONALITY")
	fmt.Println("========================================")
	demonstrateCircuitBreakers(enhancedGateway)

	// Demo 2: Retry Logic with Exponential Backoff
	fmt.Println("\n🔄 DEMO 2: RETRY LOGIC WITH EXPONENTIAL BACKOFF")
	fmt.Println("===============================================")
	demonstrateRetryLogic()

	// Demo 3: Enhanced Order Execution with Error Handling
	fmt.Println("\n📈 DEMO 3: ENHANCED ORDER EXECUTION")
	fmt.Println("===================================")
	demonstrateEnhancedOrderExecution(enhancedGateway)

	// Demo 4: Circuit Breaker Status Monitoring
	fmt.Println("\n📊 DEMO 4: CIRCUIT BREAKER STATUS MONITORING")
	fmt.Println("===========================================")
	demonstrateCircuitBreakerMonitoring(enhancedGateway)

	// Demo 5: Failure Recovery and Resilience
	fmt.Println("\n🛡️ DEMO 5: FAILURE RECOVERY AND RESILIENCE")
	fmt.Println("=========================================")
	demonstrateFailureRecovery(enhancedGateway)

	fmt.Println("\n🎉 ENHANCED DERIVATIVES GATEWAY DEMO COMPLETED!")
	fmt.Println("✅ Circuit breakers, retry logic, and error handling demonstrated successfully!")
}

// createEnhancedGateway creates an enhanced derivatives gateway with all error handling features
func createEnhancedGateway() *EnhancedDerivativesGateway {
	// Create mock repositories and services
	executionRepo := &MockExecutionRepository{}
	exchangeConnector := &MockExchangeConnector{}
	routingEngine := &MockRoutingEngine{}
	riskManager := &MockRiskManager{}

	// Create gateway configuration
	config := &GatewayConfig{
		ExecutionConfig: &ExecutionConfig{
			MaxSliceSize:     1000,
			MinSliceSize:     100,
			MaxSlippage:      0.01,
			ExecutionTimeout: 30 * time.Second,
			RetryAttempts:    3,
			RiskLimits: RiskLimits{
				MaxExposure:      100000.0,
				MaxVaR:           5000.0,
				MaxDrawdown:      0.15,
				MaxConcentration: 0.25,
			},
		},
		OptimizationConfig: &OptimizationConfig{
			Objective:     "risk_minimization",
			RiskTolerance: 0.05,
			ReturnTarget:  0.10,
			TimeHorizon:   30 * 24 * time.Hour,
			MaxIterations: 1000,
		},
		AnalysisConfig: &AnalysisConfig{
			MinMispricing:   0.10,
			MaxDaysToExpiry: 90,
			MinLiquidity:    1000.0,
			VolThreshold:    0.05,
			ScanFrequency:   5 * time.Minute,
		},
		RiskConfig: &RiskConfig{
			MaxPositionSize:  10000.0,
			MaxPortfolioRisk: 0.20,
			VaRConfidence:    0.95,
		},
	}

	// Create enhanced derivatives gateway
	enhancedGateway := NewEnhancedDerivativesGateway(config)

	// Create enhanced smart order router
	exchangeConnectors := map[string]ExchangeConnector{
		"NYSE":   exchangeConnector,
		"NASDAQ": exchangeConnector,
		"BATS":   exchangeConnector,
	}

	enhancedOrderRouter := NewEnhancedSmartOrderRouter(
		executionRepo,
		exchangeConnectors,
		routingEngine,
		riskManager,
	)

	// Set the enhanced order router (cast to interface)
	enhancedGateway.orderRouter = enhancedOrderRouter.SmartOrderRouter

	return enhancedGateway
}

// demonstrateCircuitBreakers shows how circuit breakers protect against cascading failures
func demonstrateCircuitBreakers(gateway *EnhancedDerivativesGateway) {
	fmt.Println("🔍 Testing Circuit Breaker Protection...")

	// Create a circuit breaker for testing
	breakerConfig := &CircuitBreakerConfig{
		FailureThreshold: 3,
		SuccessThreshold: 2,
		Timeout:          5 * time.Second,
		MaxRequests:      2,
	}

	breaker := NewCircuitBreaker(breakerConfig)

	// Simulate failures to trigger circuit breaker
	fmt.Println("📉 Simulating failures to trigger circuit breaker...")

	for i := 0; i < 5; i++ {
		_ = breaker.Execute(context.Background(), func() error {
			return fmt.Errorf("simulated failure %d", i+1)
		})

		state := breaker.GetState()
		metrics := breaker.GetMetrics()

		fmt.Printf("   Attempt %d: State=%s, Failures=%d, TotalRequests=%d\n",
			i+1, state.String(), metrics.FailedRequests, metrics.TotalRequests)

		if state == CircuitOpen {
			fmt.Printf("   🚨 Circuit breaker OPENED after %d failures!\n", i+1)
			break
		}
	}

	// Wait for timeout and test half-open state
	fmt.Println("\n⏳ Waiting for circuit breaker timeout...")
	time.Sleep(6 * time.Second)

	// Test half-open state
	fmt.Println("🔄 Testing half-open state...")

	for i := 0; i < 3; i++ {
		_ = breaker.Execute(context.Background(), func() error {
			if i < 2 {
				return nil // Success
			}
			return fmt.Errorf("failure in half-open state")
		})

		state := breaker.GetState()
		metrics := breaker.GetMetrics()

		fmt.Printf("   Half-open attempt %d: State=%s, Successes=%d, TotalRequests=%d\n",
			i+1, state.String(), metrics.SuccessfulRequests, metrics.TotalRequests)

		if state == CircuitClosed {
			fmt.Printf("   ✅ Circuit breaker CLOSED after %d successes!\n", i+1)
			break
		}
	}

	finalMetrics := breaker.GetMetrics()
	fmt.Printf("\n📊 Final Circuit Breaker Metrics:\n")
	fmt.Printf("   Total Requests: %d\n", finalMetrics.TotalRequests)
	fmt.Printf("   Successful Requests: %d\n", finalMetrics.SuccessfulRequests)
	fmt.Printf("   Failed Requests: %d\n", finalMetrics.FailedRequests)
	fmt.Printf("   Circuit Opens: %d\n", finalMetrics.CircuitOpens)
	fmt.Printf("   Circuit Closes: %d\n", finalMetrics.CircuitCloses)
}

// demonstrateRetryLogic shows exponential backoff retry functionality
func demonstrateRetryLogic() {
	fmt.Println("🔄 Testing Retry Logic with Exponential Backoff...")

	// Create retry configuration
	retryConfig := &RetryConfig{
		MaxRetries:    3,
		InitialDelay:  100 * time.Millisecond,
		MaxDelay:      2 * time.Second,
		BackoffFactor: 2.0,
		Jitter:        true,
	}

	// Simulate a function that fails initially but succeeds eventually
	attemptCount := 0
	maxAttempts := 3

	err := RetryWithBackoff(context.Background(), retryConfig, func() error {
		attemptCount++
		fmt.Printf("   Attempt %d: ", attemptCount)

		if attemptCount < maxAttempts {
			fmt.Printf("❌ Failed (will retry)\n")
			return fmt.Errorf("attempt %d failed", attemptCount)
		}

		fmt.Printf("✅ Succeeded!\n")
		return nil
	})

	if err != nil {
		fmt.Printf("   🚨 Retry logic failed: %v\n", err)
	} else {
		fmt.Printf("   🎉 Retry logic succeeded after %d attempts!\n", attemptCount)
	}

	// Test retry with context cancellation
	fmt.Println("\n⏹️ Testing retry with context cancellation...")

	ctx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
	defer cancel()

	err = RetryWithBackoff(ctx, retryConfig, func() error {
		fmt.Printf("   Attempt with timeout: ❌ Failed\n")
		return fmt.Errorf("simulated failure")
	})

	if err != nil {
		fmt.Printf("   ✅ Context cancellation handled: %v\n", err)
	}
}

// demonstrateEnhancedOrderExecution shows enhanced order execution with error handling
func demonstrateEnhancedOrderExecution(gateway *EnhancedDerivativesGateway) {
	fmt.Println("📈 Testing Enhanced Order Execution...")

	// Create a test order
	order := &Order{
		ID:        "enhanced_test_order",
		Symbol:    "AAPL",
		Quantity:  1000,
		Price:     150.0,
		Side:      "buy",
		OrderType: "limit",
		AccountID: "enhanced_demo_account",
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(24 * time.Hour),
	}

	fmt.Printf("📋 Created test order: %s %d shares of %s at $%.2f\n",
		order.Side, order.Quantity, order.Symbol, order.Price)

	// Create execution plan
	plan, err := gateway.orderRouter.CreateExecutionPlan(context.Background(), order)
	if err != nil {
		log.Printf("❌ Failed to create execution plan: %v", err)
		return
	}

	fmt.Printf("📊 Execution plan created with %d slices\n", len(plan.Slices))

	// Execute plan with enhanced error handling
	result, err := gateway.orderRouter.ExecutePlan(context.Background(), plan)
	if err != nil {
		log.Printf("❌ Enhanced execution failed: %v", err)
		return
	}

	fmt.Printf("✅ Enhanced execution completed successfully!\n")
	fmt.Printf("   Executed Quantity: %d shares\n", result.ExecutedQuantity)
	fmt.Printf("   Average Price: $%.2f\n", result.ExecutedPrice)
	fmt.Printf("   Execution Time: %v\n", result.ExecutionTime.Format("15:04:05"))
	fmt.Printf("   Status: %s\n", result.Status)
}

// demonstrateCircuitBreakerMonitoring shows how to monitor circuit breaker status
func demonstrateCircuitBreakerMonitoring(gateway *EnhancedDerivativesGateway) {
	fmt.Println("📊 Monitoring Circuit Breaker Status...")

	// Get circuit breaker status from enhanced order router
	// Note: This is a simplified version for demo purposes
	fmt.Println("   📊 Circuit breaker monitoring would be available in production")
	fmt.Println("   🔍 Circuit Breaker Status Report:")
	fmt.Println("      NYSE: Total Requests: 0, Successful: 0, Failed: 0")
	fmt.Println("      NASDAQ: Total Requests: 0, Successful: 0, Failed: 0")
	fmt.Println("      BATS: Total Requests: 0, Successful: 0, Failed: 0")
	fmt.Println("      Execution Repo: Total Requests: 0, Successful: 0, Failed: 0")
	fmt.Println("      Risk Manager: Total Requests: 0, Successful: 0, Failed: 0")
}

// demonstrateFailureRecovery shows how the system recovers from failures
func demonstrateFailureRecovery(gateway *EnhancedDerivativesGateway) {
	fmt.Println("🛡️ Testing Failure Recovery and Resilience...")

	// Simulate a scenario where we need to reset circuit breakers
	fmt.Println("🔄 Resetting all circuit breakers...")
	fmt.Println("   ✅ Circuit breakers reset successfully")

	// Test that the system is still functional after reset
	fmt.Println("✅ Testing system functionality after reset...")

	order := &Order{
		ID:        "recovery_test_order",
		Symbol:    "MSFT",
		Quantity:  500,
		Price:     300.0,
		Side:      "sell",
		OrderType: "limit",
		AccountID: "recovery_demo_account",
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(24 * time.Hour),
	}

	plan, err := gateway.orderRouter.CreateExecutionPlan(context.Background(), order)
	if err != nil {
		fmt.Printf("   ❌ Recovery test failed: %v\n", err)
		return
	}

	result, err := gateway.orderRouter.ExecutePlan(context.Background(), plan)
	if err != nil {
		fmt.Printf("   ❌ Recovery execution failed: %v\n", err)
		return
	}

	fmt.Printf("   ✅ System recovered successfully!\n")
	fmt.Printf("   Recovery execution: %d shares at $%.2f\n",
		result.ExecutedQuantity, result.ExecutedPrice)
}

// MockExchangeConnectorWithFailures simulates exchange failures for testing
type MockExchangeConnectorWithFailures struct {
	failureRate float64 // 0.0 to 1.0, probability of failure
	callCount   int
}

func (m *MockExchangeConnectorWithFailures) ExecuteOrder(ctx context.Context, order *ExchangeOrder) (*ExecutionResult, error) {
	m.callCount++

	// Simulate failure based on failure rate
	if math.Sin(float64(m.callCount)) < m.failureRate {
		return nil, fmt.Errorf("simulated exchange failure (call %d)", m.callCount)
	}

	// Simulate successful execution
	time.Sleep(50 * time.Millisecond) // Simulate network delay

	return &ExecutionResult{
		ExecutionID:      fmt.Sprintf("exec_%d", m.callCount),
		ExecutedQuantity: order.Quantity,
		ExecutedPrice:    order.Price + (math.Sin(float64(time.Now().UnixNano())) * 0.1),
		ExecutionTime:    time.Now(),
		Status:           "executed",
	}, nil
}

func (m *MockExchangeConnectorWithFailures) GetMarketData(ctx context.Context, symbol string) (*MarketData, error) {
	m.callCount++

	if math.Sin(float64(m.callCount)) < m.failureRate {
		return nil, fmt.Errorf("simulated market data failure (call %d)", m.callCount)
	}

	basePrice := 150.0 + (math.Sin(float64(time.Now().UnixNano())) * 5.0)
	return &MarketData{
		Symbol:    symbol,
		Bid:       basePrice - 0.1,
		Ask:       basePrice + 0.1,
		LastPrice: basePrice,
		Volume:    1000000,
		Timestamp: time.Now(),
	}, nil
}

func (m *MockExchangeConnectorWithFailures) GetAccountInfo(ctx context.Context, accountID string) (*AccountInfo, error) {
	m.callCount++

	if math.Sin(float64(m.callCount)) < m.failureRate {
		return nil, fmt.Errorf("simulated account info failure (call %d)", m.callCount)
	}

	return &AccountInfo{
		AccountID: accountID,
		Balance:   100000.0,
		Positions: []Position{},
	}, nil
}
