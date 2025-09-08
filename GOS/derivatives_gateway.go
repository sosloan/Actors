package main

import (
	"context"
	"fmt"
	"log"
	"math"
	"sort"
	"time"

	"github.com/google/uuid"
)

// Core Types
type Order struct {
	ID        string
	Symbol    string
	Quantity  int64
	Price     float64
	Side      string // "buy" or "sell"
	OrderType string // "market", "limit", "stop"
	AccountID string
	CreatedAt time.Time
	ExpiresAt time.Time
}

type Execution struct {
	ID               string
	OrderID          string
	ExchangeID       string
	ExecutedQuantity int64
	ExecutedPrice    float64
	ExecutionTime    time.Time
	Status           string
}

type Position struct {
	ID             string
	AccountID      string
	InstrumentID   string
	InstrumentType string
	Quantity       int64
	AveragePrice   float64
	MarketValue    float64
	UnrealizedPnL  float64
	LastUpdated    time.Time
}

type OptionContract struct {
	ID               string
	UnderlyingSymbol string
	Strike           float64
	ExpirationDate   time.Time
	OptionType       string // "call" or "put"
	Multiplier       int64
	CreatedAt        time.Time
}

type OptionMarketData struct {
	OptionID          string
	Bid               float64
	Ask               float64
	BidSize           int64
	AskSize           int64
	LastPrice         float64
	Volume            int64
	ImpliedVolatility float64
	Delta             float64
	Gamma             float64
	Theta             float64
	Vega              float64
	LastUpdated       time.Time
}

// Smart Order Router
type SmartOrderRouter struct {
	executionRepo      ExecutionRepository
	exchangeConnectors map[string]ExchangeConnector
	routingEngine      RoutingEngine
	riskManager        RiskManager
}

type ExecutionPlan struct {
	ID          string
	OrderID     string
	Slices      []ExecutionSlice
	TotalCost   float64
	RiskMetrics RiskMetrics
	CreatedAt   time.Time
}

type ExecutionSlice struct {
	ID               string
	ExchangeID       string
	Symbol           string
	Quantity         int64
	Price            float64
	Side             string
	OrderType        string
	Status           string
	ExecutionID      string
	ExecutedQuantity int64
	ExecutedPrice    float64
	ExecutionTime    time.Time
}

type ExchangeConnector interface {
	ExecuteOrder(ctx context.Context, order *ExchangeOrder) (*ExecutionResult, error)
	GetMarketData(ctx context.Context, symbol string) (*MarketData, error)
	GetAccountInfo(ctx context.Context, accountID string) (*AccountInfo, error)
}

type ExchangeOrder struct {
	Symbol    string
	Quantity  int64
	Price     float64
	Side      string
	OrderType string
}

type ExecutionResult struct {
	ExecutionID      string
	ExecutedQuantity int64
	ExecutedPrice    float64
	ExecutionTime    time.Time
	Status           string
}

type MarketData struct {
	Symbol    string
	Bid       float64
	Ask       float64
	LastPrice float64
	Volume    int64
	Timestamp time.Time
}

type AccountInfo struct {
	AccountID string
	Balance   float64
	Positions []Position
}

type RoutingEngine interface {
	SelectExchanges(order *Order) []string
	CalculateOptimalSlices(order *Order, exchanges []string) []ExecutionSlice
}

type RiskManager interface {
	ValidateOrder(order *Order) error
	CalculateRiskMetrics(slices []ExecutionSlice) RiskMetrics
}

type RiskMetrics struct {
	MaxExposure       float64
	VaR               float64
	ExpectedShortfall float64
	LiquidityRisk     float64
}

type ExecutionRepository interface {
	SaveExecution(ctx context.Context, execution *Execution) error
	GetExecutionsByOrderID(ctx context.Context, orderID string) ([]*Execution, error)
}

// Portfolio Optimizer
type DerivativesPortfolioOptimizer struct {
	positionRepo       PositionRepository
	optionRepo         OptionRepository
	marketDataRepo     OptionMarketDataRepository
	riskCalculator     PortfolioRiskCalculator
	optimizationEngine OptimizationEngine
}

type OptimizationParams struct {
	AccountID             string
	OptimizationObjective string // "risk_minimization", "return_maximization", "sharpe_optimization"
	RiskTolerance         float64
	ReturnTarget          float64
	TimeHorizon           time.Duration
	Constraints           []Constraint
}

type Constraint struct {
	Type        string
	Instrument  string
	MinWeight   float64
	MaxWeight   float64
	MaxQuantity int64
}

type OptimizedPortfolio struct {
	CurrentPositions   []Position
	CurrentRisk        PortfolioRisk
	ProposedTrades     []ProposedTrade
	OptimizedRisk      PortfolioRisk
	ImprovementMetrics ImprovementMetrics
	OptimizationTime   time.Duration
}

type ProposedTrade struct {
	InstrumentID     string
	Action           string // "buy", "sell", "hold"
	Quantity         int64
	ExpectedPrice    float64
	ExpectedImpact   float64
	RiskContribution float64
}

type PortfolioRisk struct {
	VaR               float64
	ExpectedShortfall float64
	Volatility        float64
	Beta              float64
	SharpeRatio       float64
	MaxDrawdown       float64
	ConcentrationRisk float64
}

type ImprovementMetrics struct {
	RiskReduction       float64
	ReturnImprovement   float64
	SharpeImprovement   float64
	VolatilityReduction float64
	DrawdownReduction   float64
}

type PositionRepository interface {
	GetAccountPositions(ctx context.Context, accountID string) ([]Position, error)
	UpdatePosition(ctx context.Context, position *Position) error
}

type OptionRepository interface {
	FindOne(ctx context.Context, id string) (*OptionContract, error)
	FindByStrikeAndType(ctx context.Context, underlying string, strike float64, optionType string) ([]*OptionContract, error)
	FindByUnderlying(ctx context.Context, underlying string) ([]*OptionContract, error)
}

type OptionMarketDataRepository interface {
	GetMarketData(ctx context.Context, optionID string) (*OptionMarketData, error)
	GetMarketDataByUnderlying(ctx context.Context, underlying string) ([]*OptionMarketData, error)
}

type PortfolioRiskCalculator interface {
	CalculatePortfolioRisk(ctx context.Context, positions []Position) (*PortfolioRisk, error)
	CalculateVaR(positions []Position, confidence float64) float64
	CalculateExpectedShortfall(positions []Position, confidence float64) float64
}

type OptimizationEngine interface {
	Solve(ctx context.Context, problem *OptimizationProblem) (*OptimizationSolution, error)
}

type OptimizationProblem struct {
	Objective          string
	CurrentPositions   []Position
	HedgingInstruments []HedgingInstrument
	Constraints        []Constraint
	RiskTolerance      float64
	ReturnTarget       float64
}

type HedgingInstrument struct {
	InstrumentID   string
	InstrumentType string
	HedgeRatio     float64
	Cost           float64
	Effectiveness  float64
}

type OptimizationSolution struct {
	ProposedTrades     []ProposedTrade
	OptimizedRisk      *PortfolioRisk
	ImprovementMetrics *ImprovementMetrics
	ConvergenceStatus  string
	Iterations         int
}

// Calendar Spread Analyzer
type CalendarSpreadAnalysisService struct {
	optionRepo        OptionRepository
	marketDataRepo    OptionMarketDataRepository
	volSurfaceRepo    VolatilitySurfaceRepository
	termStructureRepo TermStructureRepository
	historicalRepo    HistoricalSpreadRepository
}

type SpreadAnalysisParams struct {
	UnderlyingSymbol string
	MinMispricing    float64
	MaxDaysToExpiry  int
	MinLiquidity     float64
	VolThreshold     float64
	MaxStrikes       int
}

type CalendarSpreadAnalysis struct {
	UnderlyingSymbol   string
	Opportunities      []CalendarSpreadOpportunity
	AnalysisTime       time.Time
	TotalOpportunities int
	BestOpportunity    *CalendarSpreadOpportunity
}

type CalendarSpreadOpportunity struct {
	ID               string
	Strike           float64
	NearExpiry       time.Time
	FarExpiry        time.Time
	OptionType       string
	SpreadPrice      float64
	ImpliedVolDiff   float64
	TheoreticalValue float64
	Mispricing       float64
	LiquidityScore   float64
	RiskMetrics      SpreadRiskMetrics
	Confidence       float64
	CreatedAt        time.Time
}

type SpreadRiskMetrics struct {
	Delta             float64
	Gamma             float64
	Theta             float64
	Vega              float64
	MaxLoss           float64
	BreakevenPoints   []float64
	ProfitProbability float64
}

type VolatilitySurfaceRepository interface {
	GetVolatilitySurface(ctx context.Context, underlying string) (*VolatilitySurface, error)
}

type VolatilitySurface struct {
	UnderlyingSymbol string
	Strikes          []float64
	Expirations      []time.Time
	Volatilities     [][]float64
	LastUpdated      time.Time
}

type TermStructureRepository interface {
	GetTermStructure(ctx context.Context, underlying string) (*VolatilityTermStructure, error)
}

type VolatilityTermStructure struct {
	UnderlyingSymbol string
	Expirations      []time.Time
	Volatilities     []float64
	LastUpdated      time.Time
}

type HistoricalSpreadRepository interface {
	GetHistoricalSpreads(ctx context.Context, params HistoricalSpreadParams) ([]HistoricalSpread, error)
}

type HistoricalSpreadParams struct {
	UnderlyingSymbol string
	Strike           float64
	OptionType       string
	StartDate        time.Time
	EndDate          time.Time
}

type HistoricalSpread struct {
	ID          string
	Strike      float64
	NearExpiry  time.Time
	FarExpiry   time.Time
	OptionType  string
	SpreadPrice float64
	Timestamp   time.Time
}

// Expiration Manager
type ExpirationManagementService struct {
	optionRepo     OptionRepository
	positionRepo   PositionRepository
	strategyRepo   OptionsStrategyRepository
	marketDataRepo OptionMarketDataRepository
	eventRepo      DerivativesEventRepository
}

type ExpirationAnalysis struct {
	AccountID         string
	ExpiringPositions []ExpiringPosition
	AnalysisTime      time.Time
	TotalPositions    int
	HighRiskPositions int
}

type ExpiringPosition struct {
	PositionID        string
	OptionID          string
	DaysToExpiration  int
	InTheMoney        bool
	AssignmentRisk    float64
	RollCandidates    []RollCandidate
	CurrentValue      float64
	MaxLoss           float64
	RecommendedAction string
}

type RollCandidate struct {
	OptionID       string
	ExpirationDate time.Time
	RollCost       float64
	LiquidityScore float64
	RiskReduction  float64
	NetBenefit     float64
}

type OptionsStrategyRepository interface {
	GetStrategiesByAccount(ctx context.Context, accountID string) ([]OptionsStrategy, error)
	GetStrategyPositions(ctx context.Context, strategyID string) ([]Position, error)
}

type OptionsStrategy struct {
	ID           string
	AccountID    string
	StrategyType string
	Positions    []Position
	NetDelta     float64
	NetGamma     float64
	NetTheta     float64
	NetVega      float64
	CreatedAt    time.Time
}

type DerivativesEventRepository interface {
	SaveEvent(ctx context.Context, event *DerivativesEvent) error
	GetEventsByAccount(ctx context.Context, accountID string) ([]*DerivativesEvent, error)
}

type DerivativesEvent struct {
	ID          string
	AccountID   string
	EventType   string
	Description string
	Timestamp   time.Time
	Data        map[string]interface{}
}

// Risk Management
type RiskManagerService struct {
	riskLimits          map[string]float64
	exposureCalculator  *ExposureCalculator
	correlationMatrix   *CorrelationMatrix
	stressTestScenarios []*StressScenario
	volatilityModels    map[string]*VolatilityModel
}

type SystemRiskAssessment struct {
	Timestamp          time.Time
	TotalExposure      float64
	LimitBreaches      []LimitBreach
	StressTestResults  []StressTestResult
	ConcentrationRisks []ConcentrationRisk
	LiquidityRisks     []LiquidityRisk
	OverallRiskLevel   string
	RecommendedActions []string
}

type LimitBreach struct {
	LimitType    string
	CurrentValue float64
	LimitValue   float64
	Severity     string
	Timestamp    time.Time
}

type StressTestResult struct {
	ScenarioName   string
	PortfolioValue float64
	LossAmount     float64
	LossPercentage float64
	RecoveryTime   time.Duration
	Severity       string
}

type ConcentrationRisk struct {
	InstrumentID   string
	Exposure       float64
	Percentage     float64
	RiskLevel      string
	Recommendation string
}

type LiquidityRisk struct {
	InstrumentID   string
	LiquidityScore float64
	RiskLevel      string
	Recommendation string
}

type ExposureCalculator interface {
	CalculateSystemExposure(positions []Position) float64
	CalculateInstrumentExposure(positions []Position, instrumentID string) float64
}

type CorrelationMatrix interface {
	GetCorrelation(instrument1, instrument2 string) float64
	UpdateCorrelations(data map[string][]float64) error
}

type StressScenario struct {
	Name        string
	Description string
	Parameters  map[string]float64
	Severity    string
}

type VolatilityModel interface {
	CalculateVolatility(instrumentID string, timeWindow time.Duration) float64
	PredictVolatility(instrumentID string, horizon time.Duration) float64
}

// Main Derivatives Gateway
type DerivativesGateway struct {
	orderRouter        *SmartOrderRouter
	portfolioOptimizer *DerivativesPortfolioOptimizer
	spreadAnalyzer     *CalendarSpreadAnalysisService
	expirationManager  *ExpirationManagementService
	riskManager        *RiskManagerService
	config             *GatewayConfig
}

type GatewayConfig struct {
	ExecutionConfig    *ExecutionConfig
	OptimizationConfig *OptimizationConfig
	AnalysisConfig     *AnalysisConfig
	RiskConfig         *RiskConfig
}

type ExecutionConfig struct {
	MaxSliceSize     int64
	MinSliceSize     int64
	MaxSlippage      float64
	ExecutionTimeout time.Duration
	RetryAttempts    int
	RiskLimits       RiskLimits
}

type OptimizationConfig struct {
	Objective     string
	RiskTolerance float64
	ReturnTarget  float64
	Constraints   []Constraint
	TimeHorizon   time.Duration
	MaxIterations int
}

type AnalysisConfig struct {
	MinMispricing   float64
	MaxDaysToExpiry int
	MinLiquidity    float64
	VolThreshold    float64
	ScanFrequency   time.Duration
}

type RiskConfig struct {
	MaxPositionSize     float64
	MaxPortfolioRisk    float64
	VaRConfidence       float64
	StressTestScenarios []string
}

type RiskLimits struct {
	MaxExposure      float64
	MaxVaR           float64
	MaxDrawdown      float64
	MaxConcentration float64
}

// Implementation Methods

func NewDerivativesGateway(config *GatewayConfig) *DerivativesGateway {
	return &DerivativesGateway{
		config: config,
	}
}

func (dg *DerivativesGateway) ExecuteOrder(ctx context.Context, order *Order) (*ExecutionResult, error) {
	// Validate order
	if err := dg.riskManager.ValidateOrder(order); err != nil {
		return nil, fmt.Errorf("order validation failed: %w", err)
	}

	// Create execution plan
	plan, err := dg.orderRouter.CreateExecutionPlan(ctx, order)
	if err != nil {
		return nil, fmt.Errorf("failed to create execution plan: %w", err)
	}

	// Execute plan
	result, err := dg.orderRouter.ExecutePlan(ctx, plan)
	if err != nil {
		return nil, fmt.Errorf("execution failed: %w", err)
	}

	return result, nil
}

func (dg *DerivativesGateway) OptimizePortfolio(ctx context.Context, params OptimizationParams) (*OptimizedPortfolio, error) {
	return dg.portfolioOptimizer.OptimizePortfolio(ctx, params)
}

func (dg *DerivativesGateway) AnalyzeCalendarSpreads(ctx context.Context, params SpreadAnalysisParams) (*CalendarSpreadAnalysis, error) {
	return dg.spreadAnalyzer.AnalyzeCalendarSpreads(ctx, params)
}

func (dg *DerivativesGateway) ManageExpirations(ctx context.Context, accountID string, daysThreshold int) (*ExpirationAnalysis, error) {
	return dg.expirationManager.IdentifyExpiringPositions(ctx, accountID, daysThreshold)
}

func (dg *DerivativesGateway) PerformRiskAssessment(ctx context.Context, accountID string) (*SystemRiskAssessment, error) {
	return dg.riskManager.PerformSystemCheck(ctx, accountID)
}

// Smart Order Router Implementation
func (sor *SmartOrderRouter) CreateExecutionPlan(ctx context.Context, order *Order) (*ExecutionPlan, error) {
	// Select exchanges
	exchanges := sor.routingEngine.SelectExchanges(order)

	// Calculate optimal slices
	slices := sor.routingEngine.CalculateOptimalSlices(order, exchanges)

	// Calculate risk metrics
	riskMetrics := sor.riskManager.CalculateRiskMetrics(slices)

	// Calculate total cost
	totalCost := sor.calculateTotalCost(slices)

	plan := &ExecutionPlan{
		ID:          uuid.New().String(),
		OrderID:     order.ID,
		Slices:      slices,
		TotalCost:   totalCost,
		RiskMetrics: riskMetrics,
		CreatedAt:   time.Now(),
	}

	return plan, nil
}

func (sor *SmartOrderRouter) ExecutePlan(ctx context.Context, plan *ExecutionPlan) (*ExecutionResult, error) {
	totalExecuted := int64(0)
	totalCost := 0.0

	for _, slice := range plan.Slices {
		connector := sor.exchangeConnectors[slice.ExchangeID]

		exchangeOrder := &ExchangeOrder{
			Symbol:    slice.Symbol,
			Quantity:  slice.Quantity,
			Price:     slice.Price,
			Side:      slice.Side,
			OrderType: slice.OrderType,
		}

		result, err := connector.ExecuteOrder(ctx, exchangeOrder)
		if err != nil {
			log.Printf("Execution failed for slice %s: %v", slice.ID, err)
			continue
		}

		// Update slice
		slice.Status = "executed"
		slice.ExecutionID = result.ExecutionID
		slice.ExecutedQuantity = result.ExecutedQuantity
		slice.ExecutedPrice = result.ExecutedPrice
		slice.ExecutionTime = result.ExecutionTime

		totalExecuted += result.ExecutedQuantity
		totalCost += float64(result.ExecutedQuantity) * result.ExecutedPrice
	}

	averagePrice := totalCost / float64(totalExecuted)

	return &ExecutionResult{
		ExecutionID:      uuid.New().String(),
		ExecutedQuantity: totalExecuted,
		ExecutedPrice:    averagePrice,
		ExecutionTime:    time.Now(),
		Status:           "completed",
	}, nil
}

func (sor *SmartOrderRouter) calculateTotalCost(slices []ExecutionSlice) float64 {
	total := 0.0
	for _, slice := range slices {
		total += float64(slice.Quantity) * slice.Price
	}
	return total
}

// Portfolio Optimizer Implementation
func (dpo *DerivativesPortfolioOptimizer) OptimizePortfolio(ctx context.Context, params OptimizationParams) (*OptimizedPortfolio, error) {
	startTime := time.Now()

	// Get current positions
	currentPositions, err := dpo.positionRepo.GetAccountPositions(ctx, params.AccountID)
	if err != nil {
		return nil, fmt.Errorf("failed to get positions: %w", err)
	}

	// Calculate current risk
	currentRisk, err := dpo.riskCalculator.CalculatePortfolioRisk(ctx, currentPositions)
	if err != nil {
		return nil, fmt.Errorf("failed to calculate current risk: %w", err)
	}

	// Find hedging instruments
	hedgingInstruments, err := dpo.findHedgingInstruments(ctx, currentPositions, params)
	if err != nil {
		return nil, fmt.Errorf("failed to find hedging instruments: %w", err)
	}

	// Create optimization problem
	problem := dpo.createOptimizationProblem(currentPositions, hedgingInstruments, params)

	// Solve optimization problem
	solution, err := dpo.optimizationEngine.Solve(ctx, problem)
	if err != nil {
		return nil, fmt.Errorf("optimization failed: %w", err)
	}

	optimizationTime := time.Since(startTime)

	return &OptimizedPortfolio{
		CurrentPositions:   currentPositions,
		CurrentRisk:        *currentRisk,
		ProposedTrades:     solution.ProposedTrades,
		OptimizedRisk:      *solution.OptimizedRisk,
		ImprovementMetrics: *solution.ImprovementMetrics,
		OptimizationTime:   optimizationTime,
	}, nil
}

func (dpo *DerivativesPortfolioOptimizer) findHedgingInstruments(ctx context.Context, positions []Position, params OptimizationParams) ([]HedgingInstrument, error) {
	// Implementation would find appropriate hedging instruments
	// based on current positions and optimization objectives
	return []HedgingInstrument{}, nil
}

func (dpo *DerivativesPortfolioOptimizer) createOptimizationProblem(positions []Position, hedgingInstruments []HedgingInstrument, params OptimizationParams) *OptimizationProblem {
	return &OptimizationProblem{
		Objective:          params.OptimizationObjective,
		CurrentPositions:   positions,
		HedgingInstruments: hedgingInstruments,
		Constraints:        params.Constraints,
		RiskTolerance:      params.RiskTolerance,
		ReturnTarget:       params.ReturnTarget,
	}
}

// Calendar Spread Analyzer Implementation
func (csas *CalendarSpreadAnalysisService) AnalyzeCalendarSpreads(ctx context.Context, params SpreadAnalysisParams) (*CalendarSpreadAnalysis, error) {
	// Get options for underlying
	options, err := csas.optionRepo.FindByUnderlying(ctx, params.UnderlyingSymbol)
	if err != nil {
		return nil, fmt.Errorf("failed to get options: %w", err)
	}

	// Group options by strike and type
	spreadMap := csas.groupOptionsByStrikeAndType(options)

	// Find spread opportunities
	opportunities := []CalendarSpreadOpportunity{}

	for strike, optionTypes := range spreadMap {
		for optionType, expirations := range optionTypes {
			spreadOpportunities := csas.findSpreadOpportunities(strike, optionType, expirations, params)
			opportunities = append(opportunities, spreadOpportunities...)
		}
	}

	// Sort by mispricing (descending)
	sort.Slice(opportunities, func(i, j int) bool {
		return opportunities[i].Mispricing > opportunities[j].Mispricing
	})

	var bestOpportunity *CalendarSpreadOpportunity
	if len(opportunities) > 0 {
		bestOpportunity = &opportunities[0]
	}

	return &CalendarSpreadAnalysis{
		UnderlyingSymbol:   params.UnderlyingSymbol,
		Opportunities:      opportunities,
		AnalysisTime:       time.Now(),
		TotalOpportunities: len(opportunities),
		BestOpportunity:    bestOpportunity,
	}, nil
}

func (csas *CalendarSpreadAnalysisService) groupOptionsByStrikeAndType(options []*OptionContract) map[float64]map[string]map[time.Time]*OptionContract {
	spreadMap := make(map[float64]map[string]map[time.Time]*OptionContract)

	for _, option := range options {
		if spreadMap[option.Strike] == nil {
			spreadMap[option.Strike] = make(map[string]map[time.Time]*OptionContract)
		}
		if spreadMap[option.Strike][option.OptionType] == nil {
			spreadMap[option.Strike][option.OptionType] = make(map[time.Time]*OptionContract)
		}
		spreadMap[option.Strike][option.OptionType][option.ExpirationDate] = option
	}

	return spreadMap
}

func (csas *CalendarSpreadAnalysisService) findSpreadOpportunities(strike float64, optionType string, expirations map[time.Time]*OptionContract, params SpreadAnalysisParams) []CalendarSpreadOpportunity {
	opportunities := []CalendarSpreadOpportunity{}

	// Convert map to sorted slice
	expirationTimes := make([]time.Time, 0, len(expirations))
	for expiry := range expirations {
		expirationTimes = append(expirationTimes, expiry)
	}
	sort.Slice(expirationTimes, func(i, j int) bool {
		return expirationTimes[i].Before(expirationTimes[j])
	})

	// Analyze each potential spread pair
	for i := 0; i < len(expirationTimes)-1; i++ {
		for j := i + 1; j < len(expirationTimes); j++ {
			nearExpiry := expirationTimes[i]
			farExpiry := expirationTimes[j]

			nearOption := expirations[nearExpiry]
			farOption := expirations[farExpiry]

			// Check if both options are within max days to expiry
			daysToFarExpiry := int(farExpiry.Sub(time.Now()).Hours() / 24)

			if daysToFarExpiry > params.MaxDaysToExpiry {
				continue
			}

			// Calculate spread metrics
			spreadMetrics := csas.calculateSpreadMetrics(nearOption, farOption, params)

			// Check if opportunity meets criteria
			if csas.isOpportunity(spreadMetrics, params) {
				opportunity := CalendarSpreadOpportunity{
					ID:               uuid.New().String(),
					Strike:           strike,
					NearExpiry:       nearExpiry,
					FarExpiry:        farExpiry,
					OptionType:       optionType,
					SpreadPrice:      spreadMetrics.SpreadPrice,
					ImpliedVolDiff:   spreadMetrics.ImpliedVolDiff,
					TheoreticalValue: spreadMetrics.TheoreticalValue,
					Mispricing:       spreadMetrics.Mispricing,
					LiquidityScore:   spreadMetrics.LiquidityScore,
					RiskMetrics:      spreadMetrics.RiskMetrics,
					Confidence:       spreadMetrics.Confidence,
					CreatedAt:        time.Now(),
				}
				opportunities = append(opportunities, opportunity)
			}
		}
	}

	return opportunities
}

type SpreadMetrics struct {
	SpreadPrice      float64
	ImpliedVolDiff   float64
	TheoreticalValue float64
	Mispricing       float64
	LiquidityScore   float64
	RiskMetrics      SpreadRiskMetrics
	Confidence       float64
}

func (csas *CalendarSpreadAnalysisService) calculateSpreadMetrics(nearOption, farOption *OptionContract, params SpreadAnalysisParams) *SpreadMetrics {
	// This would calculate actual spread metrics using market data
	// For now, return mock data
	return &SpreadMetrics{
		SpreadPrice:      1.50,
		ImpliedVolDiff:   0.05,
		TheoreticalValue: 1.25,
		Mispricing:       0.25,
		LiquidityScore:   0.85,
		RiskMetrics: SpreadRiskMetrics{
			Delta:             0.45,
			Gamma:             0.02,
			Theta:             -0.05,
			Vega:              0.15,
			MaxLoss:           1.50,
			BreakevenPoints:   []float64{100.0, 110.0},
			ProfitProbability: 0.65,
		},
		Confidence: 0.80,
	}
}

func (csas *CalendarSpreadAnalysisService) isOpportunity(metrics *SpreadMetrics, params SpreadAnalysisParams) bool {
	return metrics.Mispricing >= params.MinMispricing &&
		metrics.LiquidityScore >= params.MinLiquidity &&
		math.Abs(metrics.ImpliedVolDiff) >= params.VolThreshold
}

// Expiration Manager Implementation
func (ems *ExpirationManagementService) IdentifyExpiringPositions(ctx context.Context, accountID string, daysThreshold int) (*ExpirationAnalysis, error) {
	// Get current positions
	positions, err := ems.positionRepo.GetAccountPositions(ctx, accountID)
	if err != nil {
		return nil, fmt.Errorf("failed to get positions: %w", err)
	}

	expiringPositions := []ExpiringPosition{}
	highRiskCount := 0
	thresholdDate := time.Now().AddDate(0, 0, daysThreshold)

	for _, position := range positions {
		if position.InstrumentType != "option" {
			continue
		}

		// Get option details
		option, err := ems.optionRepo.FindOne(ctx, position.InstrumentID)
		if err != nil {
			continue
		}

		// Check if expiring soon
		if option.ExpirationDate.After(thresholdDate) {
			continue
		}

		// Calculate days to expiration
		daysToExp := int(option.ExpirationDate.Sub(time.Now()).Hours() / 24)

		// Analyze ITM/OTM status (mock implementation)
		inTheMoney := ems.isInTheMoney(option, 100.0) // Mock underlying price

		// Calculate assignment risk (mock implementation)
		assignmentRisk := ems.calculateAssignmentRisk(option, position)

		// Find roll candidates
		rollCandidates, err := ems.findRollCandidates(ctx, option, position)
		if err != nil {
			log.Printf("Failed to find roll candidates for position %s: %v", position.ID, err)
		}

		// Determine recommended action
		recommendedAction := ems.determineRecommendedAction(option, position, assignmentRisk, rollCandidates)

		expiringPosition := ExpiringPosition{
			PositionID:        position.ID,
			OptionID:          option.ID,
			DaysToExpiration:  daysToExp,
			InTheMoney:        inTheMoney,
			AssignmentRisk:    assignmentRisk,
			RollCandidates:    rollCandidates,
			CurrentValue:      position.MarketValue,
			MaxLoss:           position.MarketValue, // Simplified
			RecommendedAction: recommendedAction,
		}

		expiringPositions = append(expiringPositions, expiringPosition)

		if assignmentRisk > 0.7 || daysToExp < 7 {
			highRiskCount++
		}
	}

	return &ExpirationAnalysis{
		AccountID:         accountID,
		ExpiringPositions: expiringPositions,
		AnalysisTime:      time.Now(),
		TotalPositions:    len(expiringPositions),
		HighRiskPositions: highRiskCount,
	}, nil
}

func (ems *ExpirationManagementService) isInTheMoney(option *OptionContract, underlyingPrice float64) bool {
	if option.OptionType == "call" {
		return underlyingPrice > option.Strike
	} else {
		return underlyingPrice < option.Strike
	}
}

func (ems *ExpirationManagementService) calculateAssignmentRisk(option *OptionContract, position Position) float64 {
	// Mock implementation - would use actual market data and models
	daysToExp := int(option.ExpirationDate.Sub(time.Now()).Hours() / 24)

	// Higher risk for ITM options and shorter time to expiration
	baseRisk := 0.1
	if ems.isInTheMoney(option, 100.0) {
		baseRisk += 0.3
	}
	if daysToExp < 7 {
		baseRisk += 0.4
	} else if daysToExp < 14 {
		baseRisk += 0.2
	}

	return math.Min(baseRisk, 1.0)
}

func (ems *ExpirationManagementService) findRollCandidates(ctx context.Context, option *OptionContract, position Position) ([]RollCandidate, error) {
	// Find options with same strike but later expiration
	candidates, err := ems.optionRepo.FindByStrikeAndType(ctx, option.UnderlyingSymbol, option.Strike, option.OptionType)
	if err != nil {
		return nil, err
	}

	rollCandidates := []RollCandidate{}

	for _, candidate := range candidates {
		// Skip if same or earlier expiration
		if candidate.ExpirationDate.Before(option.ExpirationDate) || candidate.ExpirationDate.Equal(option.ExpirationDate) {
			continue
		}

		// Calculate roll cost (mock implementation)
		rollCost := ems.calculateRollCost(option, candidate, position)

		// Calculate liquidity score (mock implementation)
		liquidityScore := 0.8 // Mock value

		// Calculate risk reduction (mock implementation)
		riskReduction := 0.3 // Mock value

		rollCandidate := RollCandidate{
			OptionID:       candidate.ID,
			ExpirationDate: candidate.ExpirationDate,
			RollCost:       rollCost,
			LiquidityScore: liquidityScore,
			RiskReduction:  riskReduction,
			NetBenefit:     riskReduction - rollCost,
		}

		rollCandidates = append(rollCandidates, rollCandidate)
	}

	// Sort by net benefit (descending)
	sort.Slice(rollCandidates, func(i, j int) bool {
		return rollCandidates[i].NetBenefit > rollCandidates[j].NetBenefit
	})

	return rollCandidates, nil
}

func (ems *ExpirationManagementService) calculateRollCost(option, candidate *OptionContract, position Position) float64 {
	// Mock implementation - would use actual market data
	return 0.1 // Mock roll cost
}

func (ems *ExpirationManagementService) determineRecommendedAction(option *OptionContract, position Position, assignmentRisk float64, rollCandidates []RollCandidate) string {
	if assignmentRisk > 0.8 {
		return "CLOSE_IMMEDIATELY"
	} else if assignmentRisk > 0.5 && len(rollCandidates) > 0 {
		return "ROLL_TO_LATER_EXPIRY"
	} else if assignmentRisk > 0.3 {
		return "MONITOR_CLOSELY"
	} else {
		return "HOLD"
	}
}

// Risk Manager Implementation
func (rm *RiskManagerService) PerformSystemCheck(ctx context.Context, accountID string) (*SystemRiskAssessment, error) {
	// Mock implementation - would integrate with actual position and market data
	return &SystemRiskAssessment{
		Timestamp:     time.Now(),
		TotalExposure: 100000.0,
		LimitBreaches: []LimitBreach{
			{
				LimitType:    "MAX_POSITION_SIZE",
				CurrentValue: 15000.0,
				LimitValue:   10000.0,
				Severity:     "HIGH",
				Timestamp:    time.Now(),
			},
		},
		StressTestResults: []StressTestResult{
			{
				ScenarioName:   "Market Crash -20%",
				PortfolioValue: 80000.0,
				LossAmount:     20000.0,
				LossPercentage: 20.0,
				RecoveryTime:   30 * 24 * time.Hour,
				Severity:       "MEDIUM",
			},
		},
		ConcentrationRisks: []ConcentrationRisk{
			{
				InstrumentID:   "AAPL",
				Exposure:       25000.0,
				Percentage:     25.0,
				RiskLevel:      "MEDIUM",
				Recommendation: "Consider diversifying position",
			},
		},
		LiquidityRisks: []LiquidityRisk{
			{
				InstrumentID:   "ILLIQUID_OPTION",
				LiquidityScore: 0.2,
				RiskLevel:      "HIGH",
				Recommendation: "Reduce position size or find alternative",
			},
		},
		OverallRiskLevel: "MEDIUM",
		RecommendedActions: []string{
			"Reduce position size in AAPL",
			"Close illiquid option positions",
			"Increase portfolio diversification",
		},
	}, nil
}

func (rm *RiskManagerService) ValidateOrder(order *Order) error {
	// Mock implementation - would check against actual risk limits
	if order.Quantity > 10000 {
		return fmt.Errorf("order quantity exceeds maximum allowed")
	}
	return nil
}

func (rm *RiskManagerService) CalculateRiskMetrics(slices []ExecutionSlice) RiskMetrics {
	// Mock implementation
	return RiskMetrics{
		MaxExposure:       50000.0,
		VaR:               2500.0,
		ExpectedShortfall: 3000.0,
		LiquidityRisk:     0.1,
	}
}

// Demo function is now in derivatives_gateway_demo.go
