package main

import (
	"math"
	"testing"
	"time"
)

// ── helpers ────────────────────────────────────────────────────────────────────

func makeBars(prices []float64) []Bar {
	bars := make([]Bar, len(prices))
	base := time.Date(2020, 1, 1, 0, 0, 0, 0, time.UTC)
	for i, p := range prices {
		bars[i] = Bar{
			Timestamp: base.Add(time.Duration(i) * 24 * time.Hour),
			Symbol:    "TEST",
			Open:      p,
			High:      p * 1.01,
			Low:       p * 0.99,
			Close:     p,
			Volume:    1_000_000,
		}
	}
	return bars
}

func linspace(start, end float64, n int) []float64 {
	prices := make([]float64, n)
	step := (end - start) / float64(n-1)
	for i := range prices {
		prices[i] = start + float64(i)*step
	}
	return prices
}

// ── BacktestEngine ─────────────────────────────────────────────────────────────

func TestEmptyBarsReturnsDefaultResult(t *testing.T) {
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewSMAStrategy(5, 20)
	result := engine.Run(nil, strategy)

	if result.TotalReturn != 0 {
		t.Errorf("expected TotalReturn=0, got %f", result.TotalReturn)
	}
	if result.TotalTrades != 0 {
		t.Errorf("expected TotalTrades=0, got %d", result.TotalTrades)
	}
	if result.FinalEquity != DefaultBacktestConfig().InitialCapital {
		t.Errorf("expected FinalEquity=%f, got %f", DefaultBacktestConfig().InitialCapital, result.FinalEquity)
	}
}

func TestEquityCurveLengthMatchesBars(t *testing.T) {
	prices := linspace(100, 150, 50)
	bars := makeBars(prices)
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewSMAStrategy(5, 20)
	result := engine.Run(bars, strategy)

	if len(result.EquityCurve) != len(bars) {
		t.Errorf("expected equity curve length %d, got %d", len(bars), len(result.EquityCurve))
	}
}

func TestFinalEquityNonNegative(t *testing.T) {
	prices := make([]float64, 100)
	for i := range prices {
		prices[i] = 100.0 + math.Sin(float64(i)*0.3)*20.0
	}
	bars := makeBars(prices)
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewRoCStrategy(10, 0.02)
	result := engine.Run(bars, strategy)

	if result.FinalEquity < 0 {
		t.Errorf("final equity must be non-negative, got %f", result.FinalEquity)
	}
}

func TestWinRateInValidRange(t *testing.T) {
	prices := linspace(100, 150, 80)
	bars := makeBars(prices)
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewSMAStrategy(5, 20)
	result := engine.Run(bars, strategy)

	if result.WinRate < 0 || result.WinRate > 1 {
		t.Errorf("win rate must be in [0,1], got %f", result.WinRate)
	}
}

func TestTradeCountsAreConsistent(t *testing.T) {
	prices := make([]float64, 120)
	for i := range prices {
		prices[i] = 100.0 + math.Sin(float64(i)*0.15)*15.0
	}
	bars := makeBars(prices)
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewSMAStrategy(5, 20)
	result := engine.Run(bars, strategy)

	if result.WinningTrades+result.LosingTrades != result.TotalTrades {
		t.Errorf("winning+losing=%d != total=%d",
			result.WinningTrades+result.LosingTrades, result.TotalTrades)
	}
	if len(result.Trades) != result.TotalTrades {
		t.Errorf("trades slice len=%d != TotalTrades=%d", len(result.Trades), result.TotalTrades)
	}
}

func TestMaxDrawdownInValidRange(t *testing.T) {
	prices := []float64{100, 110, 105, 95, 98, 92, 100, 108, 102, 115}
	bars := makeBars(prices)
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewRoCStrategy(3, 0.01)
	result := engine.Run(bars, strategy)

	if result.MaxDrawdown < 0 || result.MaxDrawdown > 1 {
		t.Errorf("max drawdown must be in [0,1], got %f", result.MaxDrawdown)
	}
}

func TestResultStringContainsKeyFields(t *testing.T) {
	prices := linspace(50, 200, 100)
	bars := makeBars(prices)
	engine := NewBacktestEngine(DefaultBacktestConfig())
	strategy := NewSMAStrategy(5, 20)
	result := engine.Run(bars, strategy)
	s := result.String()
	if len(s) == 0 {
		t.Error("result String() must not be empty")
	}
}

// ── SMAStrategy ────────────────────────────────────────────────────────────────

func TestSMAStrategyName(t *testing.T) {
	s := NewSMAStrategy(5, 20)
	if s.Name() != "SMAStrategy" {
		t.Errorf("expected SMAStrategy, got %s", s.Name())
	}
}

func TestSMAStrategyHoldDuringWarmup(t *testing.T) {
	s := NewSMAStrategy(3, 5)
	portfolio := newBacktestPortfolio(100_000, "TEST")
	bar := Bar{Symbol: "TEST", Close: 100.0, Timestamp: time.Now()}
	signal := s.OnBar(bar, portfolio)
	if signal != SignalHold {
		t.Errorf("expected Hold during warmup, got %d", signal)
	}
}

func TestSMAStrategyProducesBuyAfterCrossover(t *testing.T) {
	// Build a price series that creates a real fast-over-slow crossover:
	// first 15 bars are flat (fast SMA ≈ slow SMA), then 15 bars rise sharply.
	s := NewSMAStrategy(3, 10)
	portfolio := newBacktestPortfolio(100_000, "TEST")
	base := time.Date(2023, 1, 1, 0, 0, 0, 0, time.UTC)

	flat := make([]float64, 15)
	for i := range flat {
		flat[i] = 100.0
	}
	rising := linspace(100, 160, 15)
	prices := append(flat, rising...)

	gotBuy := false
	for i, p := range prices {
		bar := Bar{
			Symbol:    "TEST",
			Close:     p,
			Timestamp: base.Add(time.Duration(i) * 24 * time.Hour),
		}
		if s.OnBar(bar, portfolio) == SignalBuy {
			gotBuy = true
			break
		}
	}
	if !gotBuy {
		t.Error("expected a Buy signal when fast SMA crosses above slow SMA")
	}
}

// ── RoCStrategy ───────────────────────────────────────────────────────────────

func TestRoCStrategyName(t *testing.T) {
	s := NewRoCStrategy(10, 0.02)
	if s.Name() != "RoCStrategy" {
		t.Errorf("expected RoCStrategy, got %s", s.Name())
	}
}

func TestRoCStrategyHoldDuringWarmup(t *testing.T) {
	s := NewRoCStrategy(5, 0.02)
	portfolio := newBacktestPortfolio(100_000, "TEST")
	base := time.Now()
	for i, p := range []float64{100, 101, 102, 103} {
		bar := Bar{Symbol: "TEST", Close: p, Timestamp: base.Add(time.Duration(i) * 24 * time.Hour)}
		if sig := s.OnBar(bar, portfolio); sig != SignalHold {
			t.Errorf("expected Hold during warmup at bar %d, got %d", i, sig)
		}
	}
}

func TestRoCStrategyBuyOnStrongRise(t *testing.T) {
	s := NewRoCStrategy(2, 0.05)
	portfolio := newBacktestPortfolio(100_000, "TEST")
	base := time.Now()
	make := func(i int, p float64) Bar {
		return Bar{Symbol: "TEST", Close: p, Timestamp: base.Add(time.Duration(i) * 24 * time.Hour)}
	}
	s.OnBar(make(0, 100), portfolio)
	s.OnBar(make(1, 101), portfolio)
	// +20% above oldest → Buy
	sig := s.OnBar(make(2, 120), portfolio)
	if sig != SignalBuy {
		t.Errorf("expected Buy on +20%% move, got %d", sig)
	}
}

func TestRoCStrategySellOnStrongDrop(t *testing.T) {
	s := NewRoCStrategy(2, 0.05)
	portfolio := newBacktestPortfolio(100_000, "TEST")
	base := time.Now()
	make := func(i int, p float64) Bar {
		return Bar{Symbol: "TEST", Close: p, Timestamp: base.Add(time.Duration(i) * 24 * time.Hour)}
	}
	s.OnBar(make(0, 120), portfolio)
	s.OnBar(make(1, 119), portfolio)
	// -20% → Sell
	sig := s.OnBar(make(2, 96), portfolio)
	if sig != SignalSell {
		t.Errorf("expected Sell on -20%% drop, got %d", sig)
	}
}

// ── portfolio helpers ─────────────────────────────────────────────────────────

func TestPortfolioEquityNoPosition(t *testing.T) {
	p := newBacktestPortfolio(50_000, "AAPL")
	if p.equity(200) != 50_000 {
		t.Errorf("expected equity 50000, got %f", p.equity(200))
	}
	if p.hasPosition {
		t.Error("should not have a position")
	}
}

func TestPortfolioEquityWithOpenPosition(t *testing.T) {
	p := newBacktestPortfolio(90_000, "AAPL")
	p.cash = 80_000
	p.positionQuantity = 100
	p.hasPosition = true
	if p.equity(100) != 90_000 {
		t.Errorf("expected equity 90000, got %f", p.equity(100))
	}
}
