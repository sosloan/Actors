package main

import (
	"context"
	"fmt"
	"log"
	"time"
)

// EnhancedDerivativesGateway extends the base gateway with circuit breakers and retry logic
type EnhancedDerivativesGateway struct {
	*DerivativesGateway
	circuitBreakerManager *CircuitBreakerManager
	retryConfig           *RetryConfig
}

// NewEnhancedDerivativesGateway creates a new enhanced derivatives gateway
func NewEnhancedDerivativesGateway(config *GatewayConfig) *EnhancedDerivativesGateway {
	baseGateway := NewDerivativesGateway(config)

	return &EnhancedDerivativesGateway{
		DerivativesGateway:    baseGateway,
		circuitBreakerManager: NewCircuitBreakerManager(),
		retryConfig:           DefaultRetryConfig(),
	}
}

// EnhancedExchangeConnector wraps an exchange connector with circuit breaker and retry logic
type EnhancedExchangeConnector struct {
	connector   ExchangeConnector
	breaker     *CircuitBreaker
	retryConfig *RetryConfig
}

// NewEnhancedExchangeConnector creates a new enhanced exchange connector
func NewEnhancedExchangeConnector(connector ExchangeConnector, name string) *EnhancedExchangeConnector {
	breakerConfig := &CircuitBreakerConfig{
		FailureThreshold: 3,                // Fail after 3 consecutive failures
		SuccessThreshold: 2,                // Need 2 successes to close from half-open
		Timeout:          10 * time.Second, // Wait 10s before trying half-open
		MaxRequests:      2,                // Allow 2 requests in half-open state
	}

	breaker := NewCircuitBreaker(breakerConfig)

	return &EnhancedExchangeConnector{
		connector:   connector,
		breaker:     breaker,
		retryConfig: DefaultRetryConfig(),
	}
}

// ExecuteOrder executes an order with circuit breaker and retry logic
func (eec *EnhancedExchangeConnector) ExecuteOrder(ctx context.Context, order *ExchangeOrder) (*ExecutionResult, error) {
	var result *ExecutionResult

	err := eec.breaker.Execute(ctx, func() error {
		return RetryWithBackoff(ctx, eec.retryConfig, func() error {
			var err error
			result, err = eec.connector.ExecuteOrder(ctx, order)
			return err
		})
	})

	if err != nil {
		log.Printf("Enhanced exchange connector failed after retries: %v", err)
		return nil, fmt.Errorf("enhanced exchange execution failed: %w", err)
	}

	return result, nil
}

// GetMarketData gets market data with circuit breaker and retry logic
func (eec *EnhancedExchangeConnector) GetMarketData(ctx context.Context, symbol string) (*MarketData, error) {
	var result *MarketData

	err := eec.breaker.Execute(ctx, func() error {
		return RetryWithBackoff(ctx, eec.retryConfig, func() error {
			var err error
			result, err = eec.connector.GetMarketData(ctx, symbol)
			return err
		})
	})

	if err != nil {
		log.Printf("Enhanced market data retrieval failed after retries: %v", err)
		return nil, fmt.Errorf("enhanced market data retrieval failed: %w", err)
	}

	return result, nil
}

// GetAccountInfo gets account info with circuit breaker and retry logic
func (eec *EnhancedExchangeConnector) GetAccountInfo(ctx context.Context, accountID string) (*AccountInfo, error) {
	var result *AccountInfo

	err := eec.breaker.Execute(ctx, func() error {
		return RetryWithBackoff(ctx, eec.retryConfig, func() error {
			var err error
			result, err = eec.connector.GetAccountInfo(ctx, accountID)
			return err
		})
	})

	if err != nil {
		log.Printf("Enhanced account info retrieval failed after retries: %v", err)
		return nil, fmt.Errorf("enhanced account info retrieval failed: %w", err)
	}

	return result, nil
}

// GetCircuitBreakerState returns the current state of the circuit breaker
func (eec *EnhancedExchangeConnector) GetCircuitBreakerState() CircuitState {
	return eec.breaker.GetState()
}

// GetCircuitBreakerMetrics returns the metrics for the circuit breaker
func (eec *EnhancedExchangeConnector) GetCircuitBreakerMetrics() CircuitBreakerMetrics {
	return eec.breaker.GetMetrics()
}

// EnhancedExecutionRepository wraps an execution repository with circuit breaker and retry logic
type EnhancedExecutionRepository struct {
	repository  ExecutionRepository
	breaker     *CircuitBreaker
	retryConfig *RetryConfig
}

// NewEnhancedExecutionRepository creates a new enhanced execution repository
func NewEnhancedExecutionRepository(repository ExecutionRepository) *EnhancedExecutionRepository {
	breakerConfig := &CircuitBreakerConfig{
		FailureThreshold: 5,                // Fail after 5 consecutive failures
		SuccessThreshold: 3,                // Need 3 successes to close from half-open
		Timeout:          15 * time.Second, // Wait 15s before trying half-open
		MaxRequests:      3,                // Allow 3 requests in half-open state
	}

	breaker := NewCircuitBreaker(breakerConfig)

	return &EnhancedExecutionRepository{
		repository:  repository,
		breaker:     breaker,
		retryConfig: DefaultRetryConfig(),
	}
}

// SaveExecution saves an execution with circuit breaker and retry logic
func (eer *EnhancedExecutionRepository) SaveExecution(ctx context.Context, execution *Execution) error {
	return eer.breaker.Execute(ctx, func() error {
		return RetryWithBackoff(ctx, eer.retryConfig, func() error {
			return eer.repository.SaveExecution(ctx, execution)
		})
	})
}

// GetExecutionsByOrderID gets executions by order ID with circuit breaker and retry logic
func (eer *EnhancedExecutionRepository) GetExecutionsByOrderID(ctx context.Context, orderID string) ([]*Execution, error) {
	var result []*Execution

	err := eer.breaker.Execute(ctx, func() error {
		return RetryWithBackoff(ctx, eer.retryConfig, func() error {
			var err error
			result, err = eer.repository.GetExecutionsByOrderID(ctx, orderID)
			return err
		})
	})

	if err != nil {
		return nil, fmt.Errorf("enhanced execution retrieval failed: %w", err)
	}

	return result, nil
}

// EnhancedRiskManager wraps a risk manager with circuit breaker and retry logic
type EnhancedRiskManager struct {
	riskManager RiskManager
	breaker     *CircuitBreaker
	retryConfig *RetryConfig
}

// NewEnhancedRiskManager creates a new enhanced risk manager
func NewEnhancedRiskManager(riskManager RiskManager) *EnhancedRiskManager {
	breakerConfig := &CircuitBreakerConfig{
		FailureThreshold: 2,               // Fail after 2 consecutive failures (critical for risk)
		SuccessThreshold: 1,               // Need 1 success to close from half-open
		Timeout:          5 * time.Second, // Wait 5s before trying half-open
		MaxRequests:      1,               // Allow 1 request in half-open state
	}

	breaker := NewCircuitBreaker(breakerConfig)

	return &EnhancedRiskManager{
		riskManager: riskManager,
		breaker:     breaker,
		retryConfig: &RetryConfig{
			MaxRetries:    1, // Only 1 retry for risk calculations (critical path)
			InitialDelay:  50 * time.Millisecond,
			MaxDelay:      100 * time.Millisecond,
			BackoffFactor: 2.0,
			Jitter:        false, // No jitter for risk calculations
		},
	}
}

// ValidateOrder validates an order with circuit breaker and retry logic
func (erm *EnhancedRiskManager) ValidateOrder(order *Order) error {
	return erm.breaker.Execute(context.Background(), func() error {
		return RetryWithBackoff(context.Background(), erm.retryConfig, func() error {
			return erm.riskManager.ValidateOrder(order)
		})
	})
}

// CalculateRiskMetrics calculates risk metrics with circuit breaker and retry logic
func (erm *EnhancedRiskManager) CalculateRiskMetrics(slices []ExecutionSlice) RiskMetrics {
	var result RiskMetrics

	err := erm.breaker.Execute(context.Background(), func() error {
		return RetryWithBackoff(context.Background(), erm.retryConfig, func() error {
			result = erm.riskManager.CalculateRiskMetrics(slices)
			return nil
		})
	})

	if err != nil {
		log.Printf("Risk calculation failed, returning zero metrics: %v", err)
		// Return zero metrics as fallback for risk calculations
		return RiskMetrics{}
	}

	return result
}

// EnhancedSmartOrderRouter extends the smart order router with enhanced error handling
type EnhancedSmartOrderRouter struct {
	*SmartOrderRouter
	enhancedExchangeConnectors map[string]*EnhancedExchangeConnector
	enhancedExecutionRepo      *EnhancedExecutionRepository
	enhancedRiskManager        *EnhancedRiskManager
}

// NewEnhancedSmartOrderRouter creates a new enhanced smart order router
func NewEnhancedSmartOrderRouter(
	executionRepo ExecutionRepository,
	exchangeConnectors map[string]ExchangeConnector,
	routingEngine RoutingEngine,
	riskManager RiskManager,
) *EnhancedSmartOrderRouter {

	// Create enhanced components
	enhancedExecutionRepo := NewEnhancedExecutionRepository(executionRepo)
	enhancedRiskManager := NewEnhancedRiskManager(riskManager)

	// Create enhanced exchange connectors
	enhancedExchangeConnectors := make(map[string]*EnhancedExchangeConnector)
	for name, connector := range exchangeConnectors {
		enhancedExchangeConnectors[name] = NewEnhancedExchangeConnector(connector, name)
	}

	// Create base smart order router
	baseRouter := &SmartOrderRouter{
		executionRepo:      enhancedExecutionRepo,
		exchangeConnectors: exchangeConnectors, // Keep original for interface compatibility
		routingEngine:      routingEngine,
		riskManager:        enhancedRiskManager,
	}

	return &EnhancedSmartOrderRouter{
		SmartOrderRouter:           baseRouter,
		enhancedExchangeConnectors: enhancedExchangeConnectors,
		enhancedExecutionRepo:      enhancedExecutionRepo,
		enhancedRiskManager:        enhancedRiskManager,
	}
}

// ExecutePlan executes a plan with enhanced error handling
func (esor *EnhancedSmartOrderRouter) ExecutePlan(ctx context.Context, plan *ExecutionPlan) (*ExecutionResult, error) {
	totalExecuted := int64(0)
	totalCost := 0.0
	failedSlices := []string{}

	log.Printf("Starting enhanced execution of plan %s with %d slices", plan.ID, len(plan.Slices))

	for i, slice := range plan.Slices {
		enhancedConnector, exists := esor.enhancedExchangeConnectors[slice.ExchangeID]
		if !exists {
			log.Printf("No enhanced connector found for exchange %s, skipping slice %s", slice.ExchangeID, slice.ID)
			failedSlices = append(failedSlices, slice.ID)
			continue
		}

		// Check circuit breaker state before attempting execution
		breakerState := enhancedConnector.GetCircuitBreakerState()
		if breakerState == CircuitOpen {
			log.Printf("Circuit breaker is OPEN for exchange %s, skipping slice %s", slice.ExchangeID, slice.ID)
			failedSlices = append(failedSlices, slice.ID)
			continue
		}

		exchangeOrder := &ExchangeOrder{
			Symbol:    slice.Symbol,
			Quantity:  slice.Quantity,
			Price:     slice.Price,
			Side:      slice.Side,
			OrderType: slice.OrderType,
		}

		result, err := enhancedConnector.ExecuteOrder(ctx, exchangeOrder)
		if err != nil {
			log.Printf("Enhanced execution failed for slice %s on exchange %s: %v", slice.ID, slice.ExchangeID, err)
			failedSlices = append(failedSlices, slice.ID)
			continue
		}

		// Update slice with execution results
		slice.Status = "executed"
		slice.ExecutionID = result.ExecutionID
		slice.ExecutedQuantity = result.ExecutedQuantity
		slice.ExecutedPrice = result.ExecutedPrice
		slice.ExecutionTime = result.ExecutionTime

		totalExecuted += result.ExecutedQuantity
		totalCost += float64(result.ExecutedQuantity) * result.ExecutedPrice

		log.Printf("Successfully executed slice %d/%d: %d shares at $%.2f",
			i+1, len(plan.Slices), result.ExecutedQuantity, result.ExecutedPrice)
	}

	// Log execution summary
	log.Printf("Enhanced execution completed: %d/%d slices executed, %d failed",
		len(plan.Slices)-len(failedSlices), len(plan.Slices), len(failedSlices))

	if len(failedSlices) > 0 {
		log.Printf("Failed slices: %v", failedSlices)
	}

	// Calculate average price
	var averagePrice float64
	if totalExecuted > 0 {
		averagePrice = totalCost / float64(totalExecuted)
	}

	return &ExecutionResult{
		ExecutionID:      plan.ID,
		ExecutedQuantity: totalExecuted,
		ExecutedPrice:    averagePrice,
		ExecutionTime:    time.Now(),
		Status:           "completed",
	}, nil
}

// GetCircuitBreakerStatus returns the status of all circuit breakers
func (esor *EnhancedSmartOrderRouter) GetCircuitBreakerStatus() map[string]CircuitBreakerMetrics {
	status := make(map[string]CircuitBreakerMetrics)

	for exchangeID, connector := range esor.enhancedExchangeConnectors {
		status[exchangeID] = connector.GetCircuitBreakerMetrics()
	}

	status["execution_repo"] = esor.enhancedExecutionRepo.breaker.GetMetrics()
	status["risk_manager"] = esor.enhancedRiskManager.breaker.GetMetrics()

	return status
}

// ResetAllCircuitBreakers resets all circuit breakers
func (esor *EnhancedSmartOrderRouter) ResetAllCircuitBreakers() {
	for _, connector := range esor.enhancedExchangeConnectors {
		connector.breaker.Reset()
	}
	esor.enhancedExecutionRepo.breaker.Reset()
	esor.enhancedRiskManager.breaker.Reset()

	log.Println("All circuit breakers have been reset")
}
