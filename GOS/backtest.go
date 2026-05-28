package main

import (
	"fmt"
	"math"
	"time"
)

// ── Data structures ────────────────────────────────────────────────────────────

// Bar represents a single OHLCV price bar.
type Bar struct {
	Timestamp time.Time
	Symbol    string
	Open      float64
	High      float64
	Low       float64
	Close     float64
	Volume    float64
}

// BacktestConfig holds simulation parameters.
type BacktestConfig struct {
	// Starting cash balance.
	InitialCapital float64
	// Fractional commission per trade (e.g. 0.001 = 0.1%).
	CommissionRate float64
	// Fractional slippage per fill (e.g. 0.0005 = 0.05%).
	SlippageRate float64
	// Maximum fraction of capital risked per trade (e.g. 0.10 = 10%).
	MaxPositionSize float64
}

// DefaultBacktestConfig returns sensible defaults.
func DefaultBacktestConfig() BacktestConfig {
	return BacktestConfig{
		InitialCapital:  100_000.0,
		CommissionRate:  0.001,
		SlippageRate:    0.0005,
		MaxPositionSize: 0.10,
	}
}

// BacktestSignal is the action a strategy returns for each bar.
type BacktestSignal int

const (
	SignalHold BacktestSignal = iota
	SignalBuy
	SignalSell
)

// BacktestTrade records a completed round-trip trade.
type BacktestTrade struct {
	Symbol     string
	EntryTime  time.Time
	ExitTime   time.Time
	EntryPrice float64
	ExitPrice  float64
	Quantity   float64
	PnL        float64
	ReturnPct  float64
}

// EquityPoint pairs a timestamp with a portfolio equity value.
type EquityPoint struct {
	Timestamp time.Time
	Equity    float64
}

// BacktestResult holds performance metrics after a simulation.
type BacktestResult struct {
	TotalReturn      float64
	AnnualizedReturn float64
	SharpeRatio      float64
	MaxDrawdown      float64
	WinRate          float64
	TotalTrades      int
	WinningTrades    int
	LosingTrades     int
	ProfitFactor     float64
	FinalEquity      float64
	EquityCurve      []EquityPoint
	Trades           []BacktestTrade
}

// String returns a human-readable summary of a BacktestResult.
func (r BacktestResult) String() string {
	return fmt.Sprintf(
		"BacktestResult{TotalReturn=%.2f%% AnnReturn=%.2f%% Sharpe=%.2f MaxDD=%.2f%% WinRate=%.1f%% Trades=%d FinalEquity=%.2f}",
		r.TotalReturn*100, r.AnnualizedReturn*100, r.SharpeRatio,
		r.MaxDrawdown*100, r.WinRate*100, r.TotalTrades, r.FinalEquity,
	)
}

// ── Portfolio state ────────────────────────────────────────────────────────────

// backtestPortfolio tracks the live state of the simulated portfolio.
type backtestPortfolio struct {
	cash               float64
	positionQuantity   float64
	positionEntryPrice float64
	positionEntryTime  time.Time
	hasPosition        bool
	symbol             string
}

func newBacktestPortfolio(initialCapital float64, symbol string) *backtestPortfolio {
	return &backtestPortfolio{
		cash:   initialCapital,
		symbol: symbol,
	}
}

func (p *backtestPortfolio) positionValue(currentPrice float64) float64 {
	return p.positionQuantity * currentPrice
}

func (p *backtestPortfolio) equity(currentPrice float64) float64 {
	return p.cash + p.positionValue(currentPrice)
}

// ── Strategy interface ─────────────────────────────────────────────────────────

// Strategy is the interface that all backtest strategies must implement.
type BacktestStrategy interface {
	// OnBar is called for every bar in chronological order.
	OnBar(bar Bar, portfolio *backtestPortfolio) BacktestSignal
	// Name returns the strategy identifier used in reports.
	Name() string
}

// ── Backtest engine ────────────────────────────────────────────────────────────

// BacktestEngine drives an event-driven simulation over historical bars.
type BacktestEngine struct {
	config BacktestConfig
}

// NewBacktestEngine creates a new engine with the given config.
func NewBacktestEngine(config BacktestConfig) *BacktestEngine {
	return &BacktestEngine{config: config}
}

// Run executes the simulation over bars using strategy.
// Bars must be sorted in ascending chronological order.
func (e *BacktestEngine) Run(bars []Bar, strategy BacktestStrategy) BacktestResult {
	if len(bars) == 0 {
		return e.emptyResult()
	}

	symbol := bars[0].Symbol
	portfolio := newBacktestPortfolio(e.config.InitialCapital, symbol)
	equityCurve := make([]EquityPoint, 0, len(bars))
	var completedTrades []BacktestTrade

	for _, bar := range bars {
		signal := strategy.OnBar(bar, portfolio)

		switch {
		case signal == SignalBuy && !portfolio.hasPosition:
			e.executeBuy(bar, portfolio)
		case signal == SignalSell && portfolio.hasPosition:
			if trade, ok := e.executeSell(bar, portfolio); ok {
				completedTrades = append(completedTrades, trade)
			}
		}

		equityCurve = append(equityCurve, EquityPoint{
			Timestamp: bar.Timestamp,
			Equity:    portfolio.equity(bar.Close),
		})
	}

	// Close any remaining open position at the last bar's close.
	if portfolio.hasPosition {
		lastBar := bars[len(bars)-1]
		if trade, ok := e.executeSell(lastBar, portfolio); ok {
			completedTrades = append(completedTrades, trade)
		}
	}

	finalEquity := portfolio.equity(bars[len(bars)-1].Close)
	return e.calculateResults(finalEquity, equityCurve, completedTrades, len(bars))
}

func (e *BacktestEngine) executeBuy(bar Bar, p *backtestPortfolio) {
	fillPrice := bar.Close * (1.0 + e.config.SlippageRate)
	capitalAtRisk := p.cash * e.config.MaxPositionSize
	quantity := math.Floor(capitalAtRisk / fillPrice)
	if quantity <= 0 {
		return
	}
	cost := quantity * fillPrice * (1.0 + e.config.CommissionRate)
	if cost > p.cash {
		return
	}
	p.cash -= cost
	p.positionQuantity = quantity
	p.positionEntryPrice = fillPrice
	p.positionEntryTime = bar.Timestamp
	p.hasPosition = true
}

func (e *BacktestEngine) executeSell(bar Bar, p *backtestPortfolio) (BacktestTrade, bool) {
	if !p.hasPosition || p.positionQuantity <= 0 {
		return BacktestTrade{}, false
	}
	fillPrice := bar.Close * (1.0 - e.config.SlippageRate)
	proceeds := p.positionQuantity * fillPrice * (1.0 - e.config.CommissionRate)
	costBasis := p.positionQuantity * p.positionEntryPrice
	pnl := proceeds - costBasis
	returnPct := 0.0
	if costBasis > 0 {
		returnPct = pnl / costBasis
	}

	trade := BacktestTrade{
		Symbol:     p.symbol,
		EntryTime:  p.positionEntryTime,
		ExitTime:   bar.Timestamp,
		EntryPrice: p.positionEntryPrice,
		ExitPrice:  fillPrice,
		Quantity:   p.positionQuantity,
		PnL:        pnl,
		ReturnPct:  returnPct,
	}

	p.cash += proceeds
	p.positionQuantity = 0
	p.positionEntryPrice = 0
	p.positionEntryTime = time.Time{}
	p.hasPosition = false

	return trade, true
}

func (e *BacktestEngine) calculateResults(
	finalEquity float64,
	equityCurve []EquityPoint,
	trades []BacktestTrade,
	numBars int,
) BacktestResult {
	totalReturn := (finalEquity - e.config.InitialCapital) / e.config.InitialCapital

	years := float64(numBars) / 252.0
	annualizedReturn := 0.0
	if years > 0 {
		annualizedReturn = math.Pow(1.0+totalReturn, 1.0/years) - 1.0
	}

	sharpeRatio := e.calculateSharpe(equityCurve)
	maxDrawdown := e.calculateMaxDrawdown(equityCurve)

	winningTrades := 0
	losingTrades := 0
	grossProfit := 0.0
	grossLoss := 0.0
	for _, t := range trades {
		if t.PnL > 0 {
			winningTrades++
			grossProfit += t.PnL
		} else {
			losingTrades++
			grossLoss += math.Abs(t.PnL)
		}
	}

	winRate := 0.0
	if len(trades) > 0 {
		winRate = float64(winningTrades) / float64(len(trades))
	}

	profitFactor := math.Inf(1)
	if grossLoss > 0 {
		profitFactor = grossProfit / grossLoss
	}

	return BacktestResult{
		TotalReturn:      totalReturn,
		AnnualizedReturn: annualizedReturn,
		SharpeRatio:      sharpeRatio,
		MaxDrawdown:      maxDrawdown,
		WinRate:          winRate,
		TotalTrades:      len(trades),
		WinningTrades:    winningTrades,
		LosingTrades:     losingTrades,
		ProfitFactor:     profitFactor,
		FinalEquity:      finalEquity,
		EquityCurve:      equityCurve,
		Trades:           trades,
	}
}

func (e *BacktestEngine) calculateSharpe(curve []EquityPoint) float64 {
	if len(curve) < 2 {
		return 0.0
	}
	returns := make([]float64, len(curve)-1)
	for i := 1; i < len(curve); i++ {
		if curve[i-1].Equity == 0 {
			continue
		}
		returns[i-1] = (curve[i].Equity - curve[i-1].Equity) / curve[i-1].Equity
	}
	mean := 0.0
	for _, r := range returns {
		mean += r
	}
	mean /= float64(len(returns))

	variance := 0.0
	for _, r := range returns {
		d := r - mean
		variance += d * d
	}
	variance /= float64(len(returns) - 1)
	stdDev := math.Sqrt(variance)
	if stdDev == 0 {
		return 0.0
	}
	return (mean / stdDev) * math.Sqrt(252)
}

func (e *BacktestEngine) calculateMaxDrawdown(curve []EquityPoint) float64 {
	if len(curve) == 0 {
		return 0.0
	}
	peak := curve[0].Equity
	maxDD := 0.0
	for _, pt := range curve {
		if pt.Equity > peak {
			peak = pt.Equity
		}
		dd := (peak - pt.Equity) / peak
		if dd > maxDD {
			maxDD = dd
		}
	}
	return maxDD
}

func (e *BacktestEngine) emptyResult() BacktestResult {
	return BacktestResult{
		FinalEquity: e.config.InitialCapital,
	}
}

// ── Bundled strategies ─────────────────────────────────────────────────────────

// SMAStrategy is a dual simple-moving-average crossover strategy.
// It generates SignalBuy when the fast SMA crosses above the slow SMA and
// SignalSell when it crosses below.
type SMAStrategy struct {
	fastPeriod  int
	slowPeriod  int
	prices      []float64
	prevFastSMA float64
	prevSlowSMA float64
	warmedUp    bool
}

// NewSMAStrategy creates a new SMA crossover strategy.
func NewSMAStrategy(fastPeriod, slowPeriod int) *SMAStrategy {
	return &SMAStrategy{
		fastPeriod: fastPeriod,
		slowPeriod: slowPeriod,
		prices:     make([]float64, 0, slowPeriod+1),
	}
}

func (s *SMAStrategy) Name() string { return "SMAStrategy" }

func (s *SMAStrategy) OnBar(bar Bar, _ *backtestPortfolio) BacktestSignal {
	s.prices = append(s.prices, bar.Close)
	if len(s.prices) > s.slowPeriod+1 {
		s.prices = s.prices[1:]
	}
	if len(s.prices) < s.slowPeriod {
		return SignalHold
	}

	fastSMA := average(s.prices[len(s.prices)-s.fastPeriod:])
	slowSMA := average(s.prices[len(s.prices)-s.slowPeriod:])

	signal := SignalHold
	if s.warmedUp {
		if s.prevFastSMA <= s.prevSlowSMA && fastSMA > slowSMA {
			signal = SignalBuy
		} else if s.prevFastSMA >= s.prevSlowSMA && fastSMA < slowSMA {
			signal = SignalSell
		}
	}

	s.prevFastSMA = fastSMA
	s.prevSlowSMA = slowSMA
	s.warmedUp = true
	return signal
}

// RoCStrategy is a rate-of-change momentum strategy.
// Generates SignalBuy when the lookback-bar return exceeds threshold and
// SignalSell when it falls below -threshold.
type RoCStrategy struct {
	lookback  int
	threshold float64
	prices    []float64
}

// NewRoCStrategy creates a new rate-of-change momentum strategy.
func NewRoCStrategy(lookback int, threshold float64) *RoCStrategy {
	return &RoCStrategy{
		lookback:  lookback,
		threshold: threshold,
		prices:    make([]float64, 0, lookback+1),
	}
}

func (r *RoCStrategy) Name() string { return "RoCStrategy" }

func (r *RoCStrategy) OnBar(bar Bar, _ *backtestPortfolio) BacktestSignal {
	r.prices = append(r.prices, bar.Close)
	if len(r.prices) > r.lookback+1 {
		r.prices = r.prices[1:]
	}
	if len(r.prices) <= r.lookback {
		return SignalHold
	}
	oldest := r.prices[0]
	if oldest == 0 {
		return SignalHold
	}
	momentum := (bar.Close - oldest) / oldest
	if momentum > r.threshold {
		return SignalBuy
	}
	if momentum < -r.threshold {
		return SignalSell
	}
	return SignalHold
}

// ── Helpers ────────────────────────────────────────────────────────────────────

func average(prices []float64) float64 {
	if len(prices) == 0 {
		return 0
	}
	sum := 0.0
	for _, p := range prices {
		sum += p
	}
	return sum / float64(len(prices))
}
