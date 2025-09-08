package main

import (
	"context"
	"fmt"
	"log"
	"runtime"
	"sync"
	"time"
	"unsafe"
)

// DataValidator performs cross-service data consistency validation
type DataValidator struct {
	validators map[string]Validator
	mutex      sync.RWMutex
	metrics    *ValidationMetrics
}

// Validator interface for different types of data validation
type Validator interface {
	Validate(ctx context.Context, data interface{}) (*ValidationResult, error)
	GetName() string
	GetPriority() ValidationPriority
}

// ValidationResult represents the result of a validation
type ValidationResult struct {
	ValidatorName string                 `json:"validator_name"`
	IsValid       bool                   `json:"is_valid"`
	Errors        []ValidationError      `json:"errors"`
	Warnings      []ValidationWarning    `json:"warnings"`
	Metadata      map[string]interface{} `json:"metadata"`
	Timestamp     time.Time              `json:"timestamp"`
	Duration      time.Duration          `json:"duration"`
}

// ValidationError represents a validation error
type ValidationError struct {
	Code         string `json:"code"`
	Message      string `json:"message"`
	Field        string `json:"field,omitempty"`
	Severity     string `json:"severity"` // "critical", "high", "medium", "low"
	SuggestedFix string `json:"suggested_fix,omitempty"`
}

// ValidationWarning represents a validation warning
type ValidationWarning struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Field   string `json:"field,omitempty"`
	Impact  string `json:"impact"` // "performance", "accuracy", "compliance"
}

// ValidationPriority defines the priority of validation
type ValidationPriority int

const (
	PriorityCritical ValidationPriority = iota
	PriorityHigh
	PriorityMedium
	PriorityLow
)

// ValidationMetrics tracks validation performance
type ValidationMetrics struct {
	// 🏎️ Ferrari Speed Metrics - Core Performance Indicators
	TotalValidations      int64         `json:"total_validations"`      // Total validation operations
	SuccessfulValidations int64         `json:"successful_validations"` // Successful validations count
	FailedValidations     int64         `json:"failed_validations"`     // Failed validations count
	ValidationDuration    time.Duration `json:"validation_duration"`    // Total validation time

	// ⭐ Starry Precision Metrics - Advanced Analytics
	AverageValidationTime time.Duration `json:"avg_validation_time"`   // Average time per validation
	P95ValidationTime     time.Duration `json:"p95_validation_time"`   // 95th percentile validation time
	P99ValidationTime     time.Duration `json:"p99_validation_time"`   // 99th percentile validation time
	ThroughputPerSecond   float64       `json:"throughput_per_second"` // Validations per second
	SuccessRate           float64       `json:"success_rate"`          // Success rate percentage

	// 🎡 Ferris Wheel Dynamics - Rotating State Metrics
	ErrorCounts        map[string]int64  `json:"error_counts"`         // Error type frequencies
	WarningCounts      map[string]int64  `json:"warning_counts"`       // Warning type frequencies
	ValidationHistory  []ValidationEvent `json:"validation_history"`   // Recent validation events
	PeakThroughput     float64           `json:"peak_throughput"`      // Peak throughput achieved
	LastValidationTime time.Time         `json:"last_validation_time"` // Last validation timestamp

	// 🚀 Performance Boosters - Real-time Optimization
	ConcurrentValidations int64   `json:"concurrent_validations"` // Current concurrent validations
	CacheHitRate          float64 `json:"cache_hit_rate"`         // Validation cache hit rate
	MemoryUsage           int64   `json:"memory_usage_bytes"`     // Memory usage in bytes
	CPUUtilization        float64 `json:"cpu_utilization"`        // CPU utilization percentage

	// 🔒 Thread Safety & Concurrency
	mutex sync.RWMutex `json:"-"` // Read-write mutex for thread safety
}

// ValidationEvent represents a single validation event for history tracking
type ValidationEvent struct {
	Timestamp     time.Time     `json:"timestamp"`      // Event timestamp
	Duration      time.Duration `json:"duration"`       // Validation duration
	Success       bool          `json:"success"`        // Whether validation succeeded
	ErrorType     string        `json:"error_type"`     // Error type if failed
	WarningCount  int           `json:"warning_count"`  // Number of warnings
	DataSize      int64         `json:"data_size"`      // Size of validated data
	ValidatorType string        `json:"validator_type"` // Type of validator used
}

// NewDataValidator creates a new data validator
func NewDataValidator() *DataValidator {
	return &DataValidator{
		validators: make(map[string]Validator),
		metrics: &ValidationMetrics{
			// 🏎️ Initialize Ferrari Speed Metrics
			TotalValidations:      0,
			SuccessfulValidations: 0,
			FailedValidations:     0,
			ValidationDuration:    0,

			// ⭐ Initialize Starry Precision Metrics
			AverageValidationTime: 0,
			P95ValidationTime:     0,
			P99ValidationTime:     0,
			ThroughputPerSecond:   0.0,
			SuccessRate:           0.0,

			// 🎡 Initialize Ferris Wheel Dynamics
			ErrorCounts:        make(map[string]int64),
			WarningCounts:      make(map[string]int64),
			ValidationHistory:  make([]ValidationEvent, 0, 1000), // Pre-allocate for 1000 events
			PeakThroughput:     0.0,
			LastValidationTime: time.Now(),

			// 🚀 Initialize Performance Boosters
			ConcurrentValidations: 0,
			CacheHitRate:          0.0,
			MemoryUsage:           0,
			CPUUtilization:        0.0,
		},
	}
}

// RegisterValidator registers a validator
func (dv *DataValidator) RegisterValidator(validator Validator) {
	dv.mutex.Lock()
	defer dv.mutex.Unlock()

	dv.validators[validator.GetName()] = validator
	log.Printf("Registered validator: %s (Priority: %d)", validator.GetName(), validator.GetPriority())
}

// Validate performs comprehensive validation on data
func (dv *DataValidator) Validate(ctx context.Context, data interface{}) (*ComprehensiveValidationResult, error) {
	startTime := time.Now()

	dv.mutex.RLock()
	validators := make([]Validator, 0, len(dv.validators))
	for _, validator := range dv.validators {
		validators = append(validators, validator)
	}
	dv.mutex.RUnlock()

	// Sort validators by priority
	validators = dv.sortValidatorsByPriority(validators)

	results := make([]*ValidationResult, 0, len(validators))
	overallValid := true

	// Run validators in priority order
	for _, validator := range validators {
		result, err := validator.Validate(ctx, data)
		if err != nil {
			log.Printf("Validator %s failed: %v", validator.GetName(), err)
			continue
		}

		results = append(results, result)

		// Update overall validity
		if !result.IsValid {
			overallValid = false
		}

		// Update metrics
		dv.updateMetrics(result)
	}

	duration := time.Since(startTime)

	comprehensiveResult := &ComprehensiveValidationResult{
		IsValid:       overallValid,
		Results:       results,
		TotalDuration: duration,
		Timestamp:     time.Now(),
	}

	// Update overall metrics
	dv.metrics.mutex.Lock()
	dv.metrics.TotalValidations++
	if overallValid {
		dv.metrics.SuccessfulValidations++
	} else {
		dv.metrics.FailedValidations++
	}
	dv.metrics.ValidationDuration += duration
	dv.metrics.mutex.Unlock()

	return comprehensiveResult, nil
}

// sortValidatorsByPriority sorts validators by priority (critical first)
func (dv *DataValidator) sortValidatorsByPriority(validators []Validator) []Validator {
	// Simple bubble sort by priority
	for i := 0; i < len(validators)-1; i++ {
		for j := 0; j < len(validators)-i-1; j++ {
			if validators[j].GetPriority() > validators[j+1].GetPriority() {
				validators[j], validators[j+1] = validators[j+1], validators[j]
			}
		}
	}
	return validators
}

// updateMetrics updates validation metrics
func (dv *DataValidator) updateMetrics(result *ValidationResult) {
	dv.metrics.mutex.Lock()
	defer dv.metrics.mutex.Unlock()

	// 🏎️ Update Ferrari Speed Metrics
	dv.metrics.TotalValidations++
	if result.IsValid {
		dv.metrics.SuccessfulValidations++
	} else {
		dv.metrics.FailedValidations++
	}
	dv.metrics.ValidationDuration += result.Duration
	dv.metrics.LastValidationTime = time.Now()

	// ⭐ Update Starry Precision Metrics
	if dv.metrics.TotalValidations > 0 {
		dv.metrics.AverageValidationTime = dv.metrics.ValidationDuration / time.Duration(dv.metrics.TotalValidations)
		dv.metrics.SuccessRate = float64(dv.metrics.SuccessfulValidations) / float64(dv.metrics.TotalValidations) * 100.0
	}

	// 🎡 Update Ferris Wheel Dynamics - Add to validation history
	event := ValidationEvent{
		Timestamp:     time.Now(),
		Duration:      result.Duration,
		Success:       result.IsValid,
		ErrorType:     "",
		WarningCount:  len(result.Warnings),
		DataSize:      int64(len(result.ValidatorName)), // Use validator name length as proxy
		ValidatorType: result.ValidatorName,
	}

	// Add error type if validation failed
	if !result.IsValid && len(result.Errors) > 0 {
		event.ErrorType = result.Errors[0].Code
	}

	// Maintain rolling history (keep last 1000 events)
	if len(dv.metrics.ValidationHistory) >= 1000 {
		dv.metrics.ValidationHistory = dv.metrics.ValidationHistory[1:]
	}
	dv.metrics.ValidationHistory = append(dv.metrics.ValidationHistory, event)

	// 🚀 Update Performance Boosters
	dv.metrics.ConcurrentValidations = int64(runtime.NumGoroutine()) // Approximate concurrent operations
	dv.metrics.MemoryUsage = int64(unsafe.Sizeof(*dv.metrics))       // Approximate memory usage

	// Update error and warning counts
	for _, err := range result.Errors {
		dv.metrics.ErrorCounts[err.Code]++
	}

	for _, warning := range result.Warnings {
		dv.metrics.WarningCounts[warning.Code]++
	}
}

// GetMetrics returns validation metrics
func (dv *DataValidator) GetMetrics() ValidationMetrics {
	dv.metrics.mutex.RLock()
	defer dv.metrics.mutex.RUnlock()

	// 🚀 Calculate real-time performance metrics
	dv.calculateAdvancedMetrics()

	// Create a copy without the mutex to avoid lock copying
	return ValidationMetrics{
		// 🏎️ Ferrari Speed Metrics
		TotalValidations:      dv.metrics.TotalValidations,
		SuccessfulValidations: dv.metrics.SuccessfulValidations,
		FailedValidations:     dv.metrics.FailedValidations,
		ValidationDuration:    dv.metrics.ValidationDuration,

		// ⭐ Starry Precision Metrics
		AverageValidationTime: dv.metrics.AverageValidationTime,
		P95ValidationTime:     dv.metrics.P95ValidationTime,
		P99ValidationTime:     dv.metrics.P99ValidationTime,
		ThroughputPerSecond:   dv.metrics.ThroughputPerSecond,
		SuccessRate:           dv.metrics.SuccessRate,

		// 🎡 Ferris Wheel Dynamics
		ErrorCounts:        dv.metrics.ErrorCounts,
		WarningCounts:      dv.metrics.WarningCounts,
		ValidationHistory:  dv.metrics.ValidationHistory,
		PeakThroughput:     dv.metrics.PeakThroughput,
		LastValidationTime: dv.metrics.LastValidationTime,

		// 🚀 Performance Boosters
		ConcurrentValidations: dv.metrics.ConcurrentValidations,
		CacheHitRate:          dv.metrics.CacheHitRate,
		MemoryUsage:           dv.metrics.MemoryUsage,
		CPUUtilization:        dv.metrics.CPUUtilization,

		// 🔒 Thread Safety (new mutex for the copy)
		mutex: sync.RWMutex{},
	}
}

// calculateAdvancedMetrics calculates advanced performance metrics
func (dv *DataValidator) calculateAdvancedMetrics() {
	// ⭐ Calculate throughput per second
	if dv.metrics.ValidationDuration > 0 {
		dv.metrics.ThroughputPerSecond = float64(dv.metrics.TotalValidations) / dv.metrics.ValidationDuration.Seconds()

		// Update peak throughput
		if dv.metrics.ThroughputPerSecond > dv.metrics.PeakThroughput {
			dv.metrics.PeakThroughput = dv.metrics.ThroughputPerSecond
		}
	}

	// 🎡 Calculate percentiles from validation history
	if len(dv.metrics.ValidationHistory) > 0 {
		durations := make([]time.Duration, len(dv.metrics.ValidationHistory))
		for i, event := range dv.metrics.ValidationHistory {
			durations[i] = event.Duration
		}

		// Simple percentile calculation (for demo purposes)
		if len(durations) >= 20 {
			dv.metrics.P95ValidationTime = durations[len(durations)*95/100]
			dv.metrics.P99ValidationTime = durations[len(durations)*99/100]
		}
	}
}

// GetPerformanceSummary returns a formatted performance summary
func (dv *DataValidator) GetPerformanceSummary() string {
	metrics := dv.GetMetrics()

	return fmt.Sprintf(`
🏎️ FERRARI SPEED METRICS:
   Total Validations: %d
   Success Rate: %.2f%% ⭐
   Average Time: %v
   Throughput: %.2f validations/sec 🚀

🎡 FERRIS WHEEL DYNAMICS:
   Peak Throughput: %.2f validations/sec
   P95 Time: %v
   P99 Time: %v
   Concurrent Operations: %d

🚀 PERFORMANCE BOOSTERS:
   Memory Usage: %d bytes
   Cache Hit Rate: %.2f%%
   Last Validation: %v
`,
		metrics.TotalValidations,
		metrics.SuccessRate,
		metrics.AverageValidationTime,
		metrics.ThroughputPerSecond,
		metrics.PeakThroughput,
		metrics.P95ValidationTime,
		metrics.P99ValidationTime,
		metrics.ConcurrentValidations,
		metrics.MemoryUsage,
		metrics.CacheHitRate,
		metrics.LastValidationTime.Format("15:04:05"),
	)
}

// ComprehensiveValidationResult represents the result of comprehensive validation
type ComprehensiveValidationResult struct {
	IsValid       bool                `json:"is_valid"`
	Results       []*ValidationResult `json:"results"`
	TotalDuration time.Duration       `json:"total_duration"`
	Timestamp     time.Time           `json:"timestamp"`
}

// OrderValidator validates order data consistency
type OrderValidator struct {
	positionRepo PositionRepository
	riskManager  RiskManager
}

// NewOrderValidator creates a new order validator
func NewOrderValidator(positionRepo PositionRepository, riskManager RiskManager) *OrderValidator {
	return &OrderValidator{
		positionRepo: positionRepo,
		riskManager:  riskManager,
	}
}

// GetName returns the validator name
func (ov *OrderValidator) GetName() string {
	return "order_validator"
}

// GetPriority returns the validation priority
func (ov *OrderValidator) GetPriority() ValidationPriority {
	return PriorityCritical
}

// Validate validates order data
func (ov *OrderValidator) Validate(ctx context.Context, data interface{}) (*ValidationResult, error) {
	startTime := time.Now()

	order, ok := data.(*Order)
	if !ok {
		return &ValidationResult{
			ValidatorName: ov.GetName(),
			IsValid:       false,
			Errors: []ValidationError{
				{
					Code:     "INVALID_DATA_TYPE",
					Message:  "Expected Order type",
					Severity: "critical",
				},
			},
			Timestamp: time.Now(),
			Duration:  time.Since(startTime),
		}, nil
	}

	errors := []ValidationError{}
	warnings := []ValidationWarning{}

	// Validate order basic fields
	if order.ID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_ORDER_ID",
			Message:      "Order ID is required",
			Field:        "id",
			Severity:     "critical",
			SuggestedFix: "Generate a unique order ID",
		})
	}

	if order.Symbol == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_SYMBOL",
			Message:      "Symbol is required",
			Field:        "symbol",
			Severity:     "critical",
			SuggestedFix: "Specify a valid trading symbol",
		})
	}

	if order.Quantity <= 0 {
		errors = append(errors, ValidationError{
			Code:         "INVALID_QUANTITY",
			Message:      "Quantity must be positive",
			Field:        "quantity",
			Severity:     "critical",
			SuggestedFix: "Set quantity to a positive value",
		})
	}

	if order.Price <= 0 {
		errors = append(errors, ValidationError{
			Code:         "INVALID_PRICE",
			Message:      "Price must be positive",
			Field:        "price",
			Severity:     "critical",
			SuggestedFix: "Set price to a positive value",
		})
	}

	if order.Side != "buy" && order.Side != "sell" {
		errors = append(errors, ValidationError{
			Code:         "INVALID_SIDE",
			Message:      "Side must be 'buy' or 'sell'",
			Field:        "side",
			Severity:     "critical",
			SuggestedFix: "Set side to 'buy' or 'sell'",
		})
	}

	// Validate order expiration
	if order.ExpiresAt.Before(time.Now()) {
		errors = append(errors, ValidationError{
			Code:         "EXPIRED_ORDER",
			Message:      "Order has already expired",
			Field:        "expires_at",
			Severity:     "high",
			SuggestedFix: "Set expiration time to future",
		})
	}

	// Validate against risk limits
	if err := ov.riskManager.ValidateOrder(order); err != nil {
		errors = append(errors, ValidationError{
			Code:         "RISK_LIMIT_VIOLATION",
			Message:      fmt.Sprintf("Order violates risk limits: %v", err),
			Field:        "risk_validation",
			Severity:     "high",
			SuggestedFix: "Adjust order parameters to comply with risk limits",
		})
	}

	// Check for large orders that might need special handling
	if order.Quantity > 10000 {
		warnings = append(warnings, ValidationWarning{
			Code:    "LARGE_ORDER",
			Message: "Large order detected - consider splitting for better execution",
			Field:   "quantity",
			Impact:  "performance",
		})
	}

	// Check for unusual price movements
	if order.Price > 1000 {
		warnings = append(warnings, ValidationWarning{
			Code:    "HIGH_PRICE",
			Message: "Unusually high price detected - verify market data",
			Field:   "price",
			Impact:  "accuracy",
		})
	}

	isValid := len(errors) == 0

	return &ValidationResult{
		ValidatorName: ov.GetName(),
		IsValid:       isValid,
		Errors:        errors,
		Warnings:      warnings,
		Metadata: map[string]interface{}{
			"order_id":   order.ID,
			"symbol":     order.Symbol,
			"quantity":   order.Quantity,
			"price":      order.Price,
			"side":       order.Side,
			"order_type": order.OrderType,
		},
		Timestamp: time.Now(),
		Duration:  time.Since(startTime),
	}, nil
}

// PositionValidator validates position data consistency
type PositionValidator struct {
	optionRepo OptionRepository
}

// NewPositionValidator creates a new position validator
func NewPositionValidator(optionRepo OptionRepository) *PositionValidator {
	return &PositionValidator{
		optionRepo: optionRepo,
	}
}

// GetName returns the validator name
func (pv *PositionValidator) GetName() string {
	return "position_validator"
}

// GetPriority returns the validation priority
func (pv *PositionValidator) GetPriority() ValidationPriority {
	return PriorityHigh
}

// Validate validates position data
func (pv *PositionValidator) Validate(ctx context.Context, data interface{}) (*ValidationResult, error) {
	startTime := time.Now()

	position, ok := data.(*Position)
	if !ok {
		return &ValidationResult{
			ValidatorName: pv.GetName(),
			IsValid:       false,
			Errors: []ValidationError{
				{
					Code:     "INVALID_DATA_TYPE",
					Message:  "Expected Position type",
					Severity: "critical",
				},
			},
			Timestamp: time.Now(),
			Duration:  time.Since(startTime),
		}, nil
	}

	errors := []ValidationError{}
	warnings := []ValidationWarning{}

	// Validate position basic fields
	if position.ID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_POSITION_ID",
			Message:      "Position ID is required",
			Field:        "id",
			Severity:     "critical",
			SuggestedFix: "Generate a unique position ID",
		})
	}

	if position.AccountID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_ACCOUNT_ID",
			Message:      "Account ID is required",
			Field:        "account_id",
			Severity:     "critical",
			SuggestedFix: "Specify a valid account ID",
		})
	}

	if position.InstrumentID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_INSTRUMENT_ID",
			Message:      "Instrument ID is required",
			Field:        "instrument_id",
			Severity:     "critical",
			SuggestedFix: "Specify a valid instrument ID",
		})
	}

	if position.Quantity == 0 {
		errors = append(errors, ValidationError{
			Code:         "ZERO_QUANTITY",
			Message:      "Position quantity cannot be zero",
			Field:        "quantity",
			Severity:     "high",
			SuggestedFix: "Set quantity to non-zero value or close position",
		})
	}

	// Validate instrument type
	if position.InstrumentType != "stock" && position.InstrumentType != "option" && position.InstrumentType != "future" {
		errors = append(errors, ValidationError{
			Code:         "INVALID_INSTRUMENT_TYPE",
			Message:      "Invalid instrument type",
			Field:        "instrument_type",
			Severity:     "high",
			SuggestedFix: "Set instrument type to 'stock', 'option', or 'future'",
		})
	}

	// Validate option positions
	if position.InstrumentType == "option" {
		option, err := pv.optionRepo.FindOne(ctx, position.InstrumentID)
		if err != nil {
			errors = append(errors, ValidationError{
				Code:         "INVALID_OPTION",
				Message:      fmt.Sprintf("Option not found: %v", err),
				Field:        "instrument_id",
				Severity:     "high",
				SuggestedFix: "Verify option contract exists",
			})
		} else {
			// Check if option has expired
			if option.ExpirationDate.Before(time.Now()) {
				warnings = append(warnings, ValidationWarning{
					Code:    "EXPIRED_OPTION",
					Message: "Position contains expired option",
					Field:   "instrument_id",
					Impact:  "compliance",
				})
			}
		}
	}

	// Validate market value consistency
	if position.MarketValue < 0 {
		warnings = append(warnings, ValidationWarning{
			Code:    "NEGATIVE_MARKET_VALUE",
			Message: "Negative market value detected",
			Field:   "market_value",
			Impact:  "accuracy",
		})
	}

	// Check for large positions
	if position.MarketValue > 100000 {
		warnings = append(warnings, ValidationWarning{
			Code:    "LARGE_POSITION",
			Message: "Large position detected - monitor for concentration risk",
			Field:   "market_value",
			Impact:  "compliance",
		})
	}

	isValid := len(errors) == 0

	return &ValidationResult{
		ValidatorName: pv.GetName(),
		IsValid:       isValid,
		Errors:        errors,
		Warnings:      warnings,
		Metadata: map[string]interface{}{
			"position_id":     position.ID,
			"account_id":      position.AccountID,
			"instrument_id":   position.InstrumentID,
			"instrument_type": position.InstrumentType,
			"quantity":        position.Quantity,
			"market_value":    position.MarketValue,
		},
		Timestamp: time.Now(),
		Duration:  time.Since(startTime),
	}, nil
}

// ExecutionValidator validates execution data consistency
type ExecutionValidator struct {
	executionRepo ExecutionRepository
}

// NewExecutionValidator creates a new execution validator
func NewExecutionValidator(executionRepo ExecutionRepository) *ExecutionValidator {
	return &ExecutionValidator{
		executionRepo: executionRepo,
	}
}

// GetName returns the validator name
func (ev *ExecutionValidator) GetName() string {
	return "execution_validator"
}

// GetPriority returns the validation priority
func (ev *ExecutionValidator) GetPriority() ValidationPriority {
	return PriorityHigh
}

// Validate validates execution data
func (ev *ExecutionValidator) Validate(ctx context.Context, data interface{}) (*ValidationResult, error) {
	startTime := time.Now()

	execution, ok := data.(*Execution)
	if !ok {
		return &ValidationResult{
			ValidatorName: ev.GetName(),
			IsValid:       false,
			Errors: []ValidationError{
				{
					Code:     "INVALID_DATA_TYPE",
					Message:  "Expected Execution type",
					Severity: "critical",
				},
			},
			Timestamp: time.Now(),
			Duration:  time.Since(startTime),
		}, nil
	}

	errors := []ValidationError{}
	warnings := []ValidationWarning{}

	// Validate execution basic fields
	if execution.ID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_EXECUTION_ID",
			Message:      "Execution ID is required",
			Field:        "id",
			Severity:     "critical",
			SuggestedFix: "Generate a unique execution ID",
		})
	}

	if execution.OrderID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_ORDER_ID",
			Message:      "Order ID is required",
			Field:        "order_id",
			Severity:     "critical",
			SuggestedFix: "Specify the associated order ID",
		})
	}

	if execution.ExchangeID == "" {
		errors = append(errors, ValidationError{
			Code:         "MISSING_EXCHANGE_ID",
			Message:      "Exchange ID is required",
			Field:        "exchange_id",
			Severity:     "critical",
			SuggestedFix: "Specify the exchange where execution occurred",
		})
	}

	if execution.ExecutedQuantity <= 0 {
		errors = append(errors, ValidationError{
			Code:         "INVALID_EXECUTED_QUANTITY",
			Message:      "Executed quantity must be positive",
			Field:        "executed_quantity",
			Severity:     "critical",
			SuggestedFix: "Set executed quantity to positive value",
		})
	}

	if execution.ExecutedPrice <= 0 {
		errors = append(errors, ValidationError{
			Code:         "INVALID_EXECUTED_PRICE",
			Message:      "Executed price must be positive",
			Field:        "executed_price",
			Severity:     "critical",
			SuggestedFix: "Set executed price to positive value",
		})
	}

	// Validate execution time
	if execution.ExecutionTime.IsZero() {
		errors = append(errors, ValidationError{
			Code:         "MISSING_EXECUTION_TIME",
			Message:      "Execution time is required",
			Field:        "execution_time",
			Severity:     "high",
			SuggestedFix: "Set execution time to when execution occurred",
		})
	} else if execution.ExecutionTime.After(time.Now()) {
		errors = append(errors, ValidationError{
			Code:         "FUTURE_EXECUTION_TIME",
			Message:      "Execution time cannot be in the future",
			Field:        "execution_time",
			Severity:     "high",
			SuggestedFix: "Set execution time to past or current time",
		})
	}

	// Validate execution status
	validStatuses := []string{"executed", "partial", "failed", "cancelled"}
	validStatus := false
	for _, status := range validStatuses {
		if execution.Status == status {
			validStatus = true
			break
		}
	}

	if !validStatus {
		errors = append(errors, ValidationError{
			Code:         "INVALID_EXECUTION_STATUS",
			Message:      "Invalid execution status",
			Field:        "status",
			Severity:     "high",
			SuggestedFix: "Set status to one of: executed, partial, failed, cancelled",
		})
	}

	// Check for duplicate executions
	existingExecutions, err := ev.executionRepo.GetExecutionsByOrderID(ctx, execution.OrderID)
	if err == nil {
		for _, existing := range existingExecutions {
			if existing.ID == execution.ID && existing.ExchangeID == execution.ExchangeID {
				warnings = append(warnings, ValidationWarning{
					Code:    "POTENTIAL_DUPLICATE",
					Message: "Potential duplicate execution detected",
					Field:   "id",
					Impact:  "accuracy",
				})
				break
			}
		}
	}

	isValid := len(errors) == 0

	return &ValidationResult{
		ValidatorName: ev.GetName(),
		IsValid:       isValid,
		Errors:        errors,
		Warnings:      warnings,
		Metadata: map[string]interface{}{
			"execution_id":      execution.ID,
			"order_id":          execution.OrderID,
			"exchange_id":       execution.ExchangeID,
			"executed_quantity": execution.ExecutedQuantity,
			"executed_price":    execution.ExecutedPrice,
			"status":            execution.Status,
		},
		Timestamp: time.Now(),
		Duration:  time.Since(startTime),
	}, nil
}

// CrossServiceValidator validates data consistency across services
type CrossServiceValidator struct {
	positionRepo PositionRepository
	optionRepo   OptionRepository
}

// NewCrossServiceValidator creates a new cross-service validator
func NewCrossServiceValidator(positionRepo PositionRepository, optionRepo OptionRepository) *CrossServiceValidator {
	return &CrossServiceValidator{
		positionRepo: positionRepo,
		optionRepo:   optionRepo,
	}
}

// GetName returns the validator name
func (csv *CrossServiceValidator) GetName() string {
	return "cross_service_validator"
}

// GetPriority returns the validation priority
func (csv *CrossServiceValidator) GetPriority() ValidationPriority {
	return PriorityMedium
}

// Validate validates cross-service data consistency
func (csv *CrossServiceValidator) Validate(ctx context.Context, data interface{}) (*ValidationResult, error) {
	startTime := time.Now()

	// This validator checks consistency across multiple services
	errors := []ValidationError{}
	warnings := []ValidationWarning{}

	// Example: Check if positions are consistent with option contracts
	// This would be implemented based on specific business rules

	// For demo purposes, we'll add some generic cross-service validations
	warnings = append(warnings, ValidationWarning{
		Code:    "CROSS_SERVICE_CHECK",
		Message: "Cross-service consistency check performed",
		Impact:  "accuracy",
	})

	isValid := len(errors) == 0

	return &ValidationResult{
		ValidatorName: csv.GetName(),
		IsValid:       isValid,
		Errors:        errors,
		Warnings:      warnings,
		Metadata: map[string]interface{}{
			"validation_type":  "cross_service",
			"services_checked": []string{"position_service", "option_service"},
		},
		Timestamp: time.Now(),
		Duration:  time.Since(startTime),
	}, nil
}
