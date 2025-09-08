package main

import (
	"context"
	"fmt"
	"log"
	"time"
)

// runDataValidationDemo demonstrates the data validation capabilities
func runDataValidationDemo() {
	fmt.Println("🔍 DATA VALIDATION DEMO")
	fmt.Println("=======================")
	fmt.Println("Demonstrating Cross-Service Data Consistency Validation")
	fmt.Println()

	// Create data validator and register validators
	validator := NewDataValidator()

	// Create mock repositories for validators
	executionRepo := &MockExecutionRepository{}
	positionRepo := &MockPositionRepository{}
	optionRepo := &MockOptionRepository{}
	riskManager := &MockRiskManager{}

	// Register validators
	validator.RegisterValidator(NewOrderValidator(positionRepo, riskManager))
	validator.RegisterValidator(NewPositionValidator(optionRepo))
	validator.RegisterValidator(NewExecutionValidator(executionRepo))
	validator.RegisterValidator(NewCrossServiceValidator(positionRepo, optionRepo))

	// Demo 1: Order Validation
	fmt.Println("📋 DEMO 1: ORDER VALIDATION")
	fmt.Println("===========================")
	demonstrateOrderValidation(validator)

	// Demo 2: Position Validation
	fmt.Println("\n📊 DEMO 2: POSITION VALIDATION")
	fmt.Println("==============================")
	demonstratePositionValidation(validator)

	// Demo 3: Execution Validation
	fmt.Println("\n⚡ DEMO 3: EXECUTION VALIDATION")
	fmt.Println("===============================")
	demonstrateExecutionValidation(validator)

	// Demo 4: Cross-Service Validation
	fmt.Println("\n🔗 DEMO 4: CROSS-SERVICE VALIDATION")
	fmt.Println("===================================")
	demonstrateCrossServiceValidation(validator)

	// Demo 5: Validation Metrics
	fmt.Println("\n📈 DEMO 5: VALIDATION METRICS")
	fmt.Println("=============================")
	demonstrateValidationMetrics(validator)

	fmt.Println("\n🎉 DATA VALIDATION DEMO COMPLETED!")
	fmt.Println("✅ Cross-service data consistency validation demonstrated successfully!")
}

// demonstrateOrderValidation shows order validation in action
func demonstrateOrderValidation(validator *DataValidator) {
	fmt.Println("🔍 Testing order validation...")

	// Test 1: Valid order
	fmt.Println("\n✅ Test 1: Valid Order")
	validOrder := &Order{
		ID:        "order_123",
		Symbol:    "AAPL",
		Quantity:  100,
		Price:     150.0,
		Side:      "buy",
		OrderType: "limit",
		AccountID: "account_456",
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(24 * time.Hour),
	}

	result, err := validator.Validate(context.Background(), validOrder)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))
	fmt.Printf("   Duration: %v\n", result.TotalDuration)
	fmt.Printf("   Validators Run: %d\n", len(result.Results))

	for _, res := range result.Results {
		fmt.Printf("   - %s: %s (%v)\n", res.ValidatorName, getValidationStatus(res.IsValid), res.Duration)
		if len(res.Errors) > 0 {
			for _, err := range res.Errors {
				fmt.Printf("     ❌ Error: %s (%s)\n", err.Message, err.Severity)
			}
		}
		if len(res.Warnings) > 0 {
			for _, warning := range res.Warnings {
				fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
			}
		}
	}

	// Test 2: Invalid order (missing fields)
	fmt.Println("\n❌ Test 2: Invalid Order (Missing Fields)")
	invalidOrder := &Order{
		ID:        "",        // Missing ID
		Symbol:    "",        // Missing symbol
		Quantity:  -100,      // Invalid quantity
		Price:     0,         // Invalid price
		Side:      "invalid", // Invalid side
		OrderType: "limit",
		AccountID: "account_456",
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(-1 * time.Hour), // Expired
	}

	result, err = validator.Validate(context.Background(), invalidOrder)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))
	fmt.Printf("   Duration: %v\n", result.TotalDuration)

	for _, res := range result.Results {
		fmt.Printf("   - %s: %s (%v)\n", res.ValidatorName, getValidationStatus(res.IsValid), res.Duration)
		if len(res.Errors) > 0 {
			for _, err := range res.Errors {
				fmt.Printf("     ❌ Error: %s (%s) - %s\n", err.Message, err.Severity, err.SuggestedFix)
			}
		}
		if len(res.Warnings) > 0 {
			for _, warning := range res.Warnings {
				fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
			}
		}
	}

	// Test 3: Large order (with warnings)
	fmt.Println("\n⚠️ Test 3: Large Order (With Warnings)")
	largeOrder := &Order{
		ID:        "order_large",
		Symbol:    "AAPL",
		Quantity:  15000,  // Large quantity
		Price:     1500.0, // High price
		Side:      "buy",
		OrderType: "limit",
		AccountID: "account_456",
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(24 * time.Hour),
	}

	result, err = validator.Validate(context.Background(), largeOrder)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))

	for _, res := range result.Results {
		if len(res.Warnings) > 0 {
			for _, warning := range res.Warnings {
				fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
			}
		}
	}
}

// demonstratePositionValidation shows position validation in action
func demonstratePositionValidation(validator *DataValidator) {
	fmt.Println("🔍 Testing position validation...")

	// Test 1: Valid position
	fmt.Println("\n✅ Test 1: Valid Position")
	validPosition := &Position{
		ID:             "pos_123",
		AccountID:      "account_456",
		InstrumentID:   "AAPL",
		InstrumentType: "stock",
		Quantity:       100,
		AveragePrice:   150.0,
		MarketValue:    15500.0,
		UnrealizedPnL:  500.0,
		LastUpdated:    time.Now(),
	}

	result, err := validator.Validate(context.Background(), validPosition)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))
	fmt.Printf("   Duration: %v\n", result.TotalDuration)

	for _, res := range result.Results {
		if res.ValidatorName == "position_validator" {
			fmt.Printf("   - %s: %s (%v)\n", res.ValidatorName, getValidationStatus(res.IsValid), res.Duration)
			if len(res.Errors) > 0 {
				for _, err := range res.Errors {
					fmt.Printf("     ❌ Error: %s (%s)\n", err.Message, err.Severity)
				}
			}
			if len(res.Warnings) > 0 {
				for _, warning := range res.Warnings {
					fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
				}
			}
		}
	}

	// Test 2: Invalid position
	fmt.Println("\n❌ Test 2: Invalid Position")
	invalidPosition := &Position{
		ID:             "",        // Missing ID
		AccountID:      "",        // Missing account ID
		InstrumentID:   "",        // Missing instrument ID
		InstrumentType: "invalid", // Invalid type
		Quantity:       0,         // Zero quantity
		AveragePrice:   150.0,
		MarketValue:    -1000.0, // Negative market value
		UnrealizedPnL:  500.0,
		LastUpdated:    time.Now(),
	}

	result, err = validator.Validate(context.Background(), invalidPosition)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))

	for _, res := range result.Results {
		if res.ValidatorName == "position_validator" {
			if len(res.Errors) > 0 {
				for _, err := range res.Errors {
					fmt.Printf("     ❌ Error: %s (%s) - %s\n", err.Message, err.Severity, err.SuggestedFix)
				}
			}
			if len(res.Warnings) > 0 {
				for _, warning := range res.Warnings {
					fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
				}
			}
		}
	}
}

// demonstrateExecutionValidation shows execution validation in action
func demonstrateExecutionValidation(validator *DataValidator) {
	fmt.Println("🔍 Testing execution validation...")

	// Test 1: Valid execution
	fmt.Println("\n✅ Test 1: Valid Execution")
	validExecution := &Execution{
		ID:               "exec_123",
		OrderID:          "order_123",
		ExchangeID:       "NYSE",
		ExecutedQuantity: 100,
		ExecutedPrice:    150.0,
		ExecutionTime:    time.Now(),
		Status:           "executed",
	}

	result, err := validator.Validate(context.Background(), validExecution)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))

	for _, res := range result.Results {
		if res.ValidatorName == "execution_validator" {
			fmt.Printf("   - %s: %s (%v)\n", res.ValidatorName, getValidationStatus(res.IsValid), res.Duration)
			if len(res.Errors) > 0 {
				for _, err := range res.Errors {
					fmt.Printf("     ❌ Error: %s (%s)\n", err.Message, err.Severity)
				}
			}
			if len(res.Warnings) > 0 {
				for _, warning := range res.Warnings {
					fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
				}
			}
		}
	}

	// Test 2: Invalid execution
	fmt.Println("\n❌ Test 2: Invalid Execution")
	invalidExecution := &Execution{
		ID:               "",                            // Missing ID
		OrderID:          "",                            // Missing order ID
		ExchangeID:       "",                            // Missing exchange ID
		ExecutedQuantity: -100,                          // Invalid quantity
		ExecutedPrice:    0,                             // Invalid price
		ExecutionTime:    time.Now().Add(1 * time.Hour), // Future time
		Status:           "invalid",                     // Invalid status
	}

	result, err = validator.Validate(context.Background(), invalidExecution)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))

	for _, res := range result.Results {
		if res.ValidatorName == "execution_validator" {
			if len(res.Errors) > 0 {
				for _, err := range res.Errors {
					fmt.Printf("     ❌ Error: %s (%s) - %s\n", err.Message, err.Severity, err.SuggestedFix)
				}
			}
		}
	}
}

// demonstrateCrossServiceValidation shows cross-service validation
func demonstrateCrossServiceValidation(validator *DataValidator) {
	fmt.Println("🔍 Testing cross-service validation...")

	// Test with any data type to trigger cross-service validation
	testData := map[string]interface{}{
		"service": "cross_service_test",
		"data":    "test_data",
	}

	result, err := validator.Validate(context.Background(), testData)
	if err != nil {
		log.Printf("Validation error: %v", err)
		return
	}

	fmt.Printf("   Validation Result: %s\n", getValidationStatus(result.IsValid))
	fmt.Printf("   Duration: %v\n", result.TotalDuration)

	for _, res := range result.Results {
		if res.ValidatorName == "cross_service_validator" {
			fmt.Printf("   - %s: %s (%v)\n", res.ValidatorName, getValidationStatus(res.IsValid), res.Duration)
			if len(res.Warnings) > 0 {
				for _, warning := range res.Warnings {
					fmt.Printf("     ⚠️ Warning: %s (%s)\n", warning.Message, warning.Impact)
				}
			}
		}
	}
}

// demonstrateValidationMetrics shows validation metrics
func demonstrateValidationMetrics(validator *DataValidator) {
	fmt.Println("📊 Validation Metrics Summary:")

	metrics := validator.GetMetrics()

	fmt.Printf("   Total Validations: %d\n", metrics.TotalValidations)
	fmt.Printf("   Successful Validations: %d\n", metrics.SuccessfulValidations)
	fmt.Printf("   Failed Validations: %d\n", metrics.FailedValidations)
	fmt.Printf("   Total Validation Duration: %v\n", metrics.ValidationDuration)

	if metrics.TotalValidations > 0 {
		successRate := float64(metrics.SuccessfulValidations) / float64(metrics.TotalValidations) * 100
		avgDuration := metrics.ValidationDuration / time.Duration(metrics.TotalValidations)
		fmt.Printf("   Success Rate: %.1f%%\n", successRate)
		fmt.Printf("   Average Duration: %v\n", avgDuration)
	}

	fmt.Println("\n   Error Counts by Type:")
	for errorCode, count := range metrics.ErrorCounts {
		fmt.Printf("     %s: %d\n", errorCode, count)
	}

	fmt.Println("\n   Warning Counts by Type:")
	for warningCode, count := range metrics.WarningCounts {
		fmt.Printf("     %s: %d\n", warningCode, count)
	}
}

// getValidationStatus returns a human-readable validation status
func getValidationStatus(isValid bool) string {
	if isValid {
		return "✅ VALID"
	}
	return "❌ INVALID"
}

// ValidationDemoData contains sample data for validation demos
type ValidationDemoData struct {
	Orders     []*Order
	Positions  []*Position
	Executions []*Execution
}

// createValidationDemoData creates sample data for validation demos
func createValidationDemoData() *ValidationDemoData {
	return &ValidationDemoData{
		Orders: []*Order{
			{
				ID:        "order_valid",
				Symbol:    "AAPL",
				Quantity:  100,
				Price:     150.0,
				Side:      "buy",
				OrderType: "limit",
				AccountID: "account_123",
				CreatedAt: time.Now(),
				ExpiresAt: time.Now().Add(24 * time.Hour),
			},
			{
				ID:        "order_invalid",
				Symbol:    "",
				Quantity:  -50,
				Price:     0,
				Side:      "invalid",
				OrderType: "limit",
				AccountID: "account_123",
				CreatedAt: time.Now(),
				ExpiresAt: time.Now().Add(-1 * time.Hour),
			},
		},
		Positions: []*Position{
			{
				ID:             "pos_valid",
				AccountID:      "account_123",
				InstrumentID:   "AAPL",
				InstrumentType: "stock",
				Quantity:       100,
				AveragePrice:   150.0,
				MarketValue:    15500.0,
				UnrealizedPnL:  500.0,
				LastUpdated:    time.Now(),
			},
			{
				ID:             "pos_invalid",
				AccountID:      "",
				InstrumentID:   "",
				InstrumentType: "invalid",
				Quantity:       0,
				AveragePrice:   150.0,
				MarketValue:    -1000.0,
				UnrealizedPnL:  500.0,
				LastUpdated:    time.Now(),
			},
		},
		Executions: []*Execution{
			{
				ID:               "exec_valid",
				OrderID:          "order_valid",
				ExchangeID:       "NYSE",
				ExecutedQuantity: 100,
				ExecutedPrice:    150.0,
				ExecutionTime:    time.Now(),
				Status:           "executed",
			},
			{
				ID:               "exec_invalid",
				OrderID:          "",
				ExchangeID:       "",
				ExecutedQuantity: -100,
				ExecutedPrice:    0,
				ExecutionTime:    time.Now().Add(1 * time.Hour),
				Status:           "invalid",
			},
		},
	}
}
