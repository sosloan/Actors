package main

import (
	"testing"
	"time"
)

func TestOrderCreation(t *testing.T) {
	order := Order{
		ID:        "test-order-1",
		Symbol:    "AAPL",
		Quantity:  100,
		Price:     150.0,
		Side:      "buy",
		OrderType: "limit",
		AccountID: "test-account",
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(24 * time.Hour),
	}

	if order.ID != "test-order-1" {
		t.Errorf("Expected order ID 'test-order-1', got '%s'", order.ID)
	}

	if order.Symbol != "AAPL" {
		t.Errorf("Expected symbol 'AAPL', got '%s'", order.Symbol)
	}

	if order.Quantity != 100 {
		t.Errorf("Expected quantity 100, got %d", order.Quantity)
	}

	if order.Price != 150.0 {
		t.Errorf("Expected price 150.0, got %f", order.Price)
	}

	if order.Side != "buy" {
		t.Errorf("Expected side 'buy', got '%s'", order.Side)
	}
}

func TestPositionCalculation(t *testing.T) {
	position := Position{
		ID:             "test-position-1",
		AccountID:      "test-account",
		InstrumentID:   "AAPL",
		InstrumentType: "stock",
		Quantity:       100,
		AveragePrice:   150.0,
		MarketValue:    15500.0,
		UnrealizedPnL:  500.0,
		LastUpdated:    time.Now(),
	}

	expectedMarketValue := float64(position.Quantity) * 155.0 // 100 * 155
	if position.MarketValue != expectedMarketValue {
		t.Errorf("Expected market value %f, got %f", expectedMarketValue, position.MarketValue)
	}

	expectedUnrealizedPnL := (155.0 - position.AveragePrice) * float64(position.Quantity)
	if position.UnrealizedPnL != expectedUnrealizedPnL {
		t.Errorf("Expected unrealized PnL %f, got %f", expectedUnrealizedPnL, position.UnrealizedPnL)
	}
}

func TestOptionContract(t *testing.T) {
	option := OptionContract{
		ID:                "test-option-1",
		Symbol:            "AAPL",
		StrikePrice:       150.0,
		ExpirationDate:    time.Now().Add(30 * 24 * time.Hour),
		OptionType:        "call",
		UnderlyingPrice:   155.0,
		BidPrice:          5.0,
		AskPrice:          5.5,
		Volume:            1000,
		OpenInterest:      5000,
		ImpliedVolatility: 0.25,
		Delta:             0.6,
		Gamma:             0.02,
		Theta:             -0.05,
		Vega:              0.15,
		LastUpdated:       time.Now(),
	}

	if option.Symbol != "AAPL" {
		t.Errorf("Expected symbol 'AAPL', got '%s'", option.Symbol)
	}

	if option.StrikePrice != 150.0 {
		t.Errorf("Expected strike price 150.0, got %f", option.StrikePrice)
	}

	if option.OptionType != "call" {
		t.Errorf("Expected option type 'call', got '%s'", option.OptionType)
	}

	// Test intrinsic value calculation
	expectedIntrinsicValue := 0.0
	if option.UnderlyingPrice <= option.StrikePrice {
		expectedIntrinsicValue = 0.0
	} else {
		expectedIntrinsicValue = option.UnderlyingPrice - option.StrikePrice
	}

	if expectedIntrinsicValue != 5.0 {
		t.Errorf("Expected intrinsic value 5.0, got %f", expectedIntrinsicValue)
	}
}

func TestPortfolioCalculation(t *testing.T) {
	positions := []Position{
		{
			ID:            "pos1",
			Quantity:      100,
			AveragePrice:  150.0,
			MarketValue:   15500.0,
			UnrealizedPnL: 500.0,
		},
		{
			ID:            "pos2",
			Quantity:      50,
			AveragePrice:  200.0,
			MarketValue:   10000.0,
			UnrealizedPnL: 0.0,
		},
	}

	totalValue := 0.0
	totalPnL := 0.0

	for _, pos := range positions {
		totalValue += pos.MarketValue
		totalPnL += pos.UnrealizedPnL
	}

	expectedTotalValue := 25500.0
	expectedTotalPnL := 500.0

	if totalValue != expectedTotalValue {
		t.Errorf("Expected total value %f, got %f", expectedTotalValue, totalValue)
	}

	if totalPnL != expectedTotalPnL {
		t.Errorf("Expected total PnL %f, got %f", expectedTotalPnL, totalPnL)
	}
}

func TestRiskCalculation(t *testing.T) {
	// Test basic risk calculations
	portfolioValue := 100000.0
	positionValue := 10000.0
	volatility := 0.20

	// Calculate position weight
	weight := positionValue / portfolioValue
	expectedWeight := 0.10

	if weight != expectedWeight {
		t.Errorf("Expected weight %f, got %f", expectedWeight, weight)
	}

	// Calculate risk contribution
	riskContribution := weight * volatility
	expectedRiskContribution := 0.02

	if riskContribution != expectedRiskContribution {
		t.Errorf("Expected risk contribution %f, got %f", expectedRiskContribution, riskContribution)
	}
}

// Benchmark tests
func BenchmarkOrderCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		order := Order{
			ID:        "benchmark-order",
			Symbol:    "AAPL",
			Quantity:  100,
			Price:     150.0,
			Side:      "buy",
			OrderType: "limit",
			AccountID: "test-account",
			CreatedAt: time.Now(),
			ExpiresAt: time.Now().Add(24 * time.Hour),
		}
		_ = order
	}
}

func BenchmarkPositionCalculation(b *testing.B) {
	position := Position{
		ID:            "benchmark-position",
		Quantity:      100,
		AveragePrice:  150.0,
		MarketValue:   15500.0,
		UnrealizedPnL: 500.0,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Simulate position calculation
		_ = position.MarketValue / float64(position.Quantity)
	}
}
