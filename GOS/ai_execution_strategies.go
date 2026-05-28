package main

import (
	"context"
	"fmt"
	"math"
	"sort"
	"time"
)

// ── Execution Algorithm Types ─────────────────────────────────────────────────

// ExecutionAlgorithmType defines the strategy used to fill an order.
type ExecutionAlgorithmType string

const (
	AlgoTWAP             ExecutionAlgorithmType = "twap"              // Time-Weighted Average Price
	AlgoVWAP             ExecutionAlgorithmType = "vwap"              // Volume-Weighted Average Price
	AlgoIS               ExecutionAlgorithmType = "implementation_shortfall"
	AlgoAdaptive         ExecutionAlgorithmType = "adaptive"
	AlgoParticipation    ExecutionAlgorithmType = "participation_rate"
)

// AIExecutionSlice is a single child order produced by an execution algorithm.
type AIExecutionSlice struct {
	Index            int
	Symbol           string
	Quantity         float64
	LimitPrice       float64
	ScheduledAt      time.Time // when to submit this slice
	VolumeWeight     float64   // VWAP profile weight (0–1)
	UrgencyWeight    float64   // IS urgency weight (0–1)
	ParticipationRate float64  // fraction of expected market volume
}

// AIExecutionPlan is the full execution schedule for a parent order.
type AIExecutionPlan struct {
	ID                      string
	Symbol                  string
	TotalQuantity           float64
	Algorithm               ExecutionAlgorithmType
	Slices                  []AIExecutionSlice
	EstimatedMarketImpactBPS float64
	ExpectedCompletionTime  time.Time
	CreatedAt               time.Time
}

// AIOrderRequest is the input to the AI execution engine.
type AIOrderRequest struct {
	Symbol              string
	TotalQuantity       float64   // shares / contracts
	Side                string    // "buy" | "sell"
	RefPrice            float64   // current mid-price
	AvgDailyVolume      float64   // shares per day
	WindowMinutes       int       // total execution window
	Algorithm           ExecutionAlgorithmType
	MaxParticipationRate float64  // 0–1, default 0.20
}

// ── AI Execution Engine ───────────────────────────────────────────────────────

// AIExecutionEngine generates optimal execution plans for large orders,
// minimising market impact via TWAP, VWAP, IS and Adaptive strategies.
type AIExecutionEngine struct {
	maxParticipationRate float64
	impactCoefficient    float64 // square-root model coefficient
}

// NewAIExecutionEngine creates an engine with sensible defaults.
func NewAIExecutionEngine() *AIExecutionEngine {
	return &AIExecutionEngine{
		maxParticipationRate: 0.20,
		impactCoefficient:    0.10,
	}
}

// BuildPlan creates an AIExecutionPlan for the given request.
func (e *AIExecutionEngine) BuildPlan(ctx context.Context, req AIOrderRequest) (*AIExecutionPlan, error) {
	if req.TotalQuantity <= 0 {
		return nil, fmt.Errorf("total quantity must be positive")
	}
	if req.WindowMinutes <= 0 {
		req.WindowMinutes = 120
	}
	if req.MaxParticipationRate <= 0 {
		req.MaxParticipationRate = e.maxParticipationRate
	}

	var slices []AIExecutionSlice
	switch req.Algorithm {
	case AlgoTWAP:
		slices = e.twapSlices(req)
	case AlgoVWAP:
		slices = e.vwapSlices(req)
	case AlgoIS:
		slices = e.isSlices(req)
	case AlgoAdaptive:
		slices = e.adaptiveSlices(req)
	case AlgoParticipation:
		slices = e.participationSlices(req)
	default:
		slices = e.twapSlices(req)
	}

	impact := e.estimateMarketImpactBPS(req.TotalQuantity, req.AvgDailyVolume, req.RefPrice)
	completionTime := time.Now().Add(time.Duration(req.WindowMinutes) * time.Minute)

	return &AIExecutionPlan{
		ID:                      fmt.Sprintf("aip_%s_%d", req.Symbol, time.Now().UnixMilli()),
		Symbol:                  req.Symbol,
		TotalQuantity:           req.TotalQuantity,
		Algorithm:               req.Algorithm,
		Slices:                  slices,
		EstimatedMarketImpactBPS: impact,
		ExpectedCompletionTime:  completionTime,
		CreatedAt:               time.Now(),
	}, nil
}

// twapSlices distributes quantity uniformly over time intervals.
func (e *AIExecutionEngine) twapSlices(req AIOrderRequest) []AIExecutionSlice {
	n := 12
	sliceQty := req.TotalQuantity / float64(n)
	interval := float64(req.WindowMinutes) / float64(n)
	now := time.Now()

	slices := make([]AIExecutionSlice, n)
	for i := 0; i < n; i++ {
		slices[i] = AIExecutionSlice{
			Index:       i,
			Symbol:      req.Symbol,
			Quantity:    sliceQty,
			LimitPrice:  req.RefPrice,
			ScheduledAt: now.Add(time.Duration(float64(i)*interval*float64(time.Minute))),
		}
	}
	return slices
}

// vwapSlices distributes quantity proportionally to an intraday volume profile.
// The profile approximates the well-known U-shaped intraday volume curve.
func (e *AIExecutionEngine) vwapSlices(req AIOrderRequest) []AIExecutionSlice {
	profile := intradayVolumeProfile(12)
	now := time.Now()
	interval := float64(req.WindowMinutes) / float64(len(profile))

	slices := make([]AIExecutionSlice, len(profile))
	for i, w := range profile {
		slices[i] = AIExecutionSlice{
			Index:        i,
			Symbol:       req.Symbol,
			Quantity:     req.TotalQuantity * w,
			LimitPrice:   req.RefPrice,
			ScheduledAt:  now.Add(time.Duration(float64(i)*interval*float64(time.Minute))),
			VolumeWeight: w,
		}
	}
	return slices
}

// isSlices front-loads execution to minimise timing risk (Implementation Shortfall).
// Slice sizes decrease linearly so early slices are largest.
func (e *AIExecutionEngine) isSlices(req AIOrderRequest) []AIExecutionSlice {
	n := 10
	// Weights: n, n-1, ..., 1 (normalised)
	total := float64(n*(n+1)) / 2.0
	now := time.Now()
	interval := float64(req.WindowMinutes) / float64(n)

	slices := make([]AIExecutionSlice, n)
	for i := 0; i < n; i++ {
		w := float64(n-i) / total
		slices[i] = AIExecutionSlice{
			Index:         i,
			Symbol:        req.Symbol,
			Quantity:      req.TotalQuantity * w,
			LimitPrice:    req.RefPrice,
			ScheduledAt:   now.Add(time.Duration(float64(i)*interval*float64(time.Minute))),
			UrgencyWeight: w,
		}
	}
	return slices
}

// adaptiveSlices blends TWAP and IS based on the participation rate.
// High participation → IS-weighted; low participation → uniform TWAP.
func (e *AIExecutionEngine) adaptiveSlices(req AIOrderRequest) []AIExecutionSlice {
	participation := req.TotalQuantity / (req.AvgDailyVolume + 1e-8)
	participation = math.Min(participation, req.MaxParticipationRate)

	// Blend factor: 0 = pure TWAP, 1 = pure IS
	blend := math.Min(participation/req.MaxParticipationRate, 1.0)

	n := 12
	twapW := 1.0 / float64(n)
	now := time.Now()
	interval := float64(req.WindowMinutes) / float64(n)

	// IS weights
	isTotal := float64(n*(n+1)) / 2.0
	slices := make([]AIExecutionSlice, n)

	for i := 0; i < n; i++ {
		isW := float64(n-i) / isTotal
		w := blend*isW + (1.0-blend)*twapW

		slices[i] = AIExecutionSlice{
			Index:             i,
			Symbol:            req.Symbol,
			Quantity:          req.TotalQuantity * w,
			LimitPrice:        req.RefPrice,
			ScheduledAt:       now.Add(time.Duration(float64(i)*interval*float64(time.Minute))),
			ParticipationRate: participation,
		}
	}
	return slices
}

// participationSlices creates slices sized to match a constant participation rate
// of total expected market volume.
//
// tradingHoursPerDay is the exchange session length; pass 0 to use the default
// NYSE/NASDAQ value of 6.5 hours.  For CME futures (23h), pass 23; for crypto
// 24×7, pass 24.
func (e *AIExecutionEngine) participationSlices(req AIOrderRequest) []AIExecutionSlice {
	return e.participationSlicesWithHours(req, 0)
}

func (e *AIExecutionEngine) participationSlicesWithHours(req AIOrderRequest, tradingHoursPerDay float64) []AIExecutionSlice {
	if tradingHoursPerDay <= 0 {
		tradingHoursPerDay = 6.5 // NYSE / NASDAQ regular session
	}
	participation := math.Min(req.MaxParticipationRate, 0.25)
	intervalMinutes := 10.0
	n := int(math.Ceil(float64(req.WindowMinutes) / intervalMinutes))
	if n < 1 {
		n = 1
	}

	minutesPerDay := tradingHoursPerDay * 60.0
	bucketsPerDay := minutesPerDay / intervalMinutes
	volumePerInterval := req.AvgDailyVolume / bucketsPerDay
	sliceQty := volumePerInterval * participation
	now := time.Now()

	remaining := req.TotalQuantity
	slices := make([]AIExecutionSlice, 0, n)
	for i := 0; i < n && remaining > 0; i++ {
		qty := math.Min(sliceQty, remaining)
		slices = append(slices, AIExecutionSlice{
			Index:             i,
			Symbol:            req.Symbol,
			Quantity:          qty,
			LimitPrice:        req.RefPrice,
			ScheduledAt:       now.Add(time.Duration(float64(i)*intervalMinutes*float64(time.Minute))),
			ParticipationRate: participation,
		})
		remaining -= qty
	}
	return slices
}

// estimateMarketImpactBPS uses the square-root market impact model.
func (e *AIExecutionEngine) estimateMarketImpactBPS(qty, adv, price float64) float64 {
	if adv <= 0 || price <= 0 {
		return 0.0
	}
	participation := qty / adv
	return e.impactCoefficient * math.Sqrt(participation) * 10_000
}

// ── Portfolio Optimizer (Go) ──────────────────────────────────────────────────

// PortfolioSignal is a directional signal for a single asset.
type PortfolioSignal struct {
	Symbol         string
	Direction      string  // "long", "short", "neutral"
	Confidence     float64 // 0–1
	ExpectedReturn float64 // annualised
	TimeHorizonDays int
}

// WeightedPortfolio maps symbols to target allocations.
type WeightedPortfolio struct {
	Weights         map[string]float64
	ExpectedReturn  float64
	ExpectedVolatility float64
	SharpeRatio     float64
	Method          string
}

// AIPortfolioOptimizer generates optimal portfolio weights from signals
// and a simple covariance-proxy model.
type AIPortfolioOptimizer struct {
	RiskFreeRate float64
}

// NewAIPortfolioOptimizer creates an optimizer with the given risk-free rate.
func NewAIPortfolioOptimizer(riskFreeRate float64) *AIPortfolioOptimizer {
	return &AIPortfolioOptimizer{RiskFreeRate: riskFreeRate}
}

// OptimiseFromSignals produces a portfolio allocation driven by the
// supplied strategy signals.  A simple signal-strength weighting is used
// (no covariance matrix required), making this suitable for real-time use.
func (o *AIPortfolioOptimizer) OptimiseFromSignals(
	signals []PortfolioSignal,
	maxWeight float64,
) WeightedPortfolio {
	if len(signals) == 0 {
		return WeightedPortfolio{Weights: map[string]float64{}, Method: "empty"}
	}
	if maxWeight <= 0 || maxWeight > 1 {
		maxWeight = 0.40
	}

	// Score each signal: long signals get positive weight, short negative
	type scored struct {
		symbol string
		score  float64
	}
	items := make([]scored, 0, len(signals))
	for _, s := range signals {
		score := s.ExpectedReturn * s.Confidence
		if s.Direction == "short" {
			score = -score
		} else if s.Direction == "neutral" {
			score = 0
		}
		items = append(items, scored{s.Symbol, score})
	}

	// Keep only positive scores (long-only portfolio)
	positive := make([]scored, 0)
	for _, it := range items {
		if it.score > 0 {
			positive = append(positive, it)
		}
	}
	if len(positive) == 0 {
		// Fall back to equal-weight across all assets
		w := 1.0 / float64(len(signals))
		weights := make(map[string]float64, len(signals))
		for _, s := range signals {
			weights[s.Symbol] = w
		}
		return WeightedPortfolio{Weights: weights, Method: "equal_weight_fallback"}
	}

	// Sort by score descending
	sort.Slice(positive, func(i, j int) bool {
		return positive[i].score > positive[j].score
	})

	// Normalise to sum = 1 subject to max-weight cap
	total := 0.0
	for _, it := range positive {
		total += it.score
	}

	weights := make(map[string]float64, len(positive))
	for _, it := range positive {
		w := it.score / total
		if w > maxWeight {
			w = maxWeight
		}
		weights[it.symbol] = w
	}

	// Re-normalise after capping
	sum := 0.0
	for _, w := range weights {
		sum += w
	}
	if sum > 0 {
		for k := range weights {
			weights[k] /= sum
		}
	}

	// Estimate portfolio metrics (simplified)
	expectedReturn := 0.0
	for _, s := range signals {
		if w, ok := weights[s.Symbol]; ok {
			expectedReturn += w * s.ExpectedReturn
		}
	}

	// Approximate annualised volatility: start from a 20% equity-market base
	// (roughly the long-run realised vol of a diversified equity index) and
	// reduce it linearly by up to 30% as average signal confidence rises toward 1.
	// This is a rough proxy intended for sizing/display; replace with realised vol
	// when historical data is available.
	const baseVol = 0.20        // 20% — long-run equity index vol heuristic
	const confVolReduction = 0.30 // max vol reduction at full confidence
	avgConfidence := 0.0
	for _, s := range signals {
		if w, ok := weights[s.Symbol]; ok {
			avgConfidence += w * s.Confidence
		}
	}
	approxVol := baseVol * (1.0 - avgConfidence*confVolReduction)
	sharpe := 0.0
	if approxVol > 0 {
		sharpe = (expectedReturn - o.RiskFreeRate) / approxVol
	}

	return WeightedPortfolio{
		Weights:             weights,
		ExpectedReturn:      expectedReturn,
		ExpectedVolatility:  approxVol,
		SharpeRatio:         sharpe,
		Method:              "signal_strength_weighted",
	}
}

// ── Rebalancing Scheduler ─────────────────────────────────────────────────────

// DriftAlert is produced when a position's weight deviates beyond the threshold.
type DriftAlert struct {
	Symbol        string
	CurrentWeight float64
	TargetWeight  float64
	Drift         float64   // signed
	AbsDrift      float64
	Severity      string    // "low", "medium", "high"
}

// RebalancingScheduler monitors a portfolio and triggers rebalance alerts.
type RebalancingScheduler struct {
	DriftThreshold float64  // e.g. 0.05 (5%)
	HighThreshold  float64  // e.g. 0.15 — "high" severity
}

// NewRebalancingScheduler creates a scheduler with sensible defaults.
func NewRebalancingScheduler() *RebalancingScheduler {
	return &RebalancingScheduler{
		DriftThreshold: 0.05,
		HighThreshold:  0.15,
	}
}

// CheckDrift returns alerts for all symbols whose weight has drifted beyond
// the threshold.
func (rs *RebalancingScheduler) CheckDrift(
	currentWeights map[string]float64,
	targetWeights map[string]float64,
) []DriftAlert {
	alerts := make([]DriftAlert, 0)
	visited := make(map[string]bool)

	for sym, tgt := range targetWeights {
		cur := currentWeights[sym]
		drift := cur - tgt
		abs := math.Abs(drift)
		if abs >= rs.DriftThreshold {
			severity := "low"
			if abs >= rs.HighThreshold {
				severity = "high"
			} else if abs >= rs.DriftThreshold*2 {
				severity = "medium"
			}
			alerts = append(alerts, DriftAlert{
				Symbol: sym, CurrentWeight: cur, TargetWeight: tgt,
				Drift: drift, AbsDrift: abs, Severity: severity,
			})
		}
		visited[sym] = true
	}

	// Also check symbols in current but not in target (unexpected positions)
	for sym, cur := range currentWeights {
		if visited[sym] {
			continue
		}
		if cur >= rs.DriftThreshold {
			alerts = append(alerts, DriftAlert{
				Symbol: sym, CurrentWeight: cur, TargetWeight: 0,
				Drift: cur, AbsDrift: cur, Severity: "high",
			})
		}
	}

	// Sort by absolute drift descending
	sort.Slice(alerts, func(i, j int) bool {
		return alerts[i].AbsDrift > alerts[j].AbsDrift
	})
	return alerts
}

// ── Intraday Volume Profile ───────────────────────────────────────────────────

// intradayVolumeProfile returns a normalised U-shaped intraday volume curve
// for `n` buckets covering a regular trading session.
//
// The curve is modelled as 1 + A·exp(−k·(t−0.5)²) where:
//   - t ∈ [0,1] is the normalised time within the session
//   - A = 2.0 amplifies the open/close spikes relative to the mid-day trough
//   - k = 8.0 controls how sharply activity peaks at open and close
//
// This produces the well-documented U-shape (high activity at open & close,
// low at mid-day) observed across major equity exchanges.
func intradayVolumeProfile(n int) []float64 {
	if n <= 0 {
		return nil
	}
	const amplitude = 2.0 // height of open/close peaks above the mid-day base
	const sharpness = 8.0 // controls width of the mid-day trough

	profile := make([]float64, n)
	for i := 0; i < n; i++ {
		t := float64(i) / float64(n-1) // 0 → 1
		deviation := t - 0.5
		profile[i] = 1.0 + amplitude*math.Exp(-sharpness*deviation*deviation)
	}
	// Normalise so weights sum to 1
	total := 0.0
	for _, v := range profile {
		total += v
	}
	for i := range profile {
		profile[i] /= total
	}
	return profile
}
