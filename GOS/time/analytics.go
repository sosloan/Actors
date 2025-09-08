package time

import (
	"encoding/json"
	"log"
	"math"
	"sort"
	"time"

	"github.com/jmoiron/sqlx"
)

// TimeReport represents a comprehensive time report
type TimeReport struct {
	UserID            string         `json:"user_id"`
	Period            string         `json:"period"` // daily, weekly, monthly, yearly
	StartDate         time.Time      `json:"start_date"`
	EndDate           time.Time      `json:"end_date"`
	TotalTime         int            `json:"total_time"`       // seconds
	ProductiveTime    int            `json:"productive_time"`  // seconds
	BreakTime         int            `json:"break_time"`       // seconds
	FocusScore        float64        `json:"focus_score"`      // 0.0 to 1.0
	EfficiencyScore   float64        `json:"efficiency_score"` // 0.0 to 1.0
	PeakHours         []int          `json:"peak_hours"`       // hours of day (0-23)
	DistractionCount  int            `json:"distraction_count"`
	CategoryBreakdown map[string]int `json:"category_breakdown"` // category -> seconds
	Trends            *TimeTrends    `json:"trends"`
	Recommendations   []string       `json:"recommendations"`
	GeneratedAt       time.Time      `json:"generated_at"`
}

// TimeTrends represents time usage trends
type TimeTrends struct {
	ProductiveTimeTrend  float64 `json:"productive_time_trend"`  // percentage change
	FocusScoreTrend      float64 `json:"focus_score_trend"`      // percentage change
	EfficiencyTrend      float64 `json:"efficiency_trend"`       // percentage change
	PeakHoursConsistency float64 `json:"peak_hours_consistency"` // 0.0 to 1.0
	WeeklyPattern        []int   `json:"weekly_pattern"`         // activity by day of week
	HourlyPattern        []int   `json:"hourly_pattern"`         // activity by hour of day
}

// TimeAnalyticsService provides advanced time analytics
type TimeAnalyticsService struct {
	db *sqlx.DB
}

// NewTimeAnalyticsService creates a new time analytics service
func NewTimeAnalyticsService(db *sqlx.DB) *TimeAnalyticsService {
	return &TimeAnalyticsService{db: db}
}

// GenerateTimeReport generates a comprehensive time report
func (s *TimeAnalyticsService) GenerateTimeReport(userID, period string, startDate, endDate time.Time) (*TimeReport, error) {
	report := &TimeReport{
		UserID:            userID,
		Period:            period,
		StartDate:         startDate,
		EndDate:           endDate,
		GeneratedAt:       time.Now().UTC(),
		CategoryBreakdown: make(map[string]int),
	}

	// Get time blocks for the period
	blocks, err := s.getTimeBlocksForPeriod(userID, startDate, endDate)
	if err != nil {
		return nil, err
	}

	// Calculate basic metrics
	s.calculateBasicMetrics(report, blocks)

	// Calculate trends
	trends, err := s.calculateTrends(userID, startDate, endDate, period)
	if err != nil {
		log.Printf("Error calculating trends: %v", err)
		trends = &TimeTrends{}
	}
	report.Trends = trends

	// Generate recommendations
	report.Recommendations = s.generateRecommendations(report)

	return report, nil
}

// getTimeBlocksForPeriod retrieves time blocks for a specific period
func (s *TimeAnalyticsService) getTimeBlocksForPeriod(userID string, startDate, endDate time.Time) ([]*TimeBlock, error) {
	query := `
	SELECT * FROM time_blocks 
	WHERE user_id = ? AND start_time >= ? AND start_time <= ?
	ORDER BY start_time ASC`

	var blocks []*TimeBlock
	err := s.db.Select(&blocks, query, userID, startDate, endDate)
	return blocks, err
}

// calculateBasicMetrics calculates basic time metrics
func (s *TimeAnalyticsService) calculateBasicMetrics(report *TimeReport, blocks []*TimeBlock) {
	totalTime := 0
	productiveTime := 0
	breakTime := 0
	completedBlocks := 0
	hourlyActivity := make([]int, 24)
	weeklyActivity := make([]int, 7)

	for _, block := range blocks {
		duration := block.Duration
		totalTime += duration

		// Categorize time
		switch block.Category {
		case "work", "study", "focus", "coding", "research":
			productiveTime += duration
		case "break", "rest", "lunch", "coffee":
			breakTime += duration
		}

		// Track completion
		if block.IsCompleted {
			completedBlocks++
		}

		// Track hourly activity
		startHour := block.StartTime.Hour()
		endHour := block.EndTime.Hour()
		for hour := startHour; hour <= endHour; hour++ {
			hourlyActivity[hour]++
		}

		// Track weekly activity
		dayOfWeek := int(block.StartTime.Weekday())
		weeklyActivity[dayOfWeek]++

		// Category breakdown
		if block.Category != "" {
			report.CategoryBreakdown[block.Category] += duration
		}
	}

	report.TotalTime = totalTime
	report.ProductiveTime = productiveTime
	report.BreakTime = breakTime

	// Calculate scores
	if totalTime > 0 {
		report.FocusScore = float64(productiveTime) / float64(totalTime)
	}

	if len(blocks) > 0 {
		report.EfficiencyScore = float64(completedBlocks) / float64(len(blocks))
	}

	// Find peak hours
	report.PeakHours = s.findPeakHours(hourlyActivity)

	// Set patterns in trends
	if report.Trends == nil {
		report.Trends = &TimeTrends{}
	}
	report.Trends.HourlyPattern = hourlyActivity
	report.Trends.WeeklyPattern = weeklyActivity
}

// calculateTrends calculates time usage trends
func (s *TimeAnalyticsService) calculateTrends(userID string, startDate, endDate time.Time, period string) (*TimeTrends, error) {
	trends := &TimeTrends{}

	// Calculate period length for comparison
	var comparisonStart, comparisonEnd time.Time
	switch period {
	case "daily":
		comparisonStart = startDate.AddDate(0, 0, -1)
		comparisonEnd = endDate.AddDate(0, 0, -1)
	case "weekly":
		comparisonStart = startDate.AddDate(0, 0, -7)
		comparisonEnd = endDate.AddDate(0, 0, -7)
	case "monthly":
		comparisonStart = startDate.AddDate(0, -1, 0)
		comparisonEnd = endDate.AddDate(0, -1, 0)
	case "yearly":
		comparisonStart = startDate.AddDate(-1, 0, 0)
		comparisonEnd = endDate.AddDate(-1, 0, 0)
	default:
		return trends, nil
	}

	// Get current period data
	currentBlocks, err := s.getTimeBlocksForPeriod(userID, startDate, endDate)
	if err != nil {
		return trends, err
	}

	// Get comparison period data
	comparisonBlocks, err := s.getTimeBlocksForPeriod(userID, comparisonStart, comparisonEnd)
	if err != nil {
		return trends, err
	}

	// Calculate current period metrics
	currentProductive := s.calculateProductiveTime(currentBlocks)
	currentFocus := s.calculateFocusScore(currentBlocks)
	currentEfficiency := s.calculateEfficiencyScore(currentBlocks)

	// Calculate comparison period metrics
	comparisonProductive := s.calculateProductiveTime(comparisonBlocks)
	comparisonFocus := s.calculateFocusScore(comparisonBlocks)
	comparisonEfficiency := s.calculateEfficiencyScore(comparisonBlocks)

	// Calculate trends (percentage change)
	trends.ProductiveTimeTrend = s.calculatePercentageChange(float64(comparisonProductive), float64(currentProductive))
	trends.FocusScoreTrend = s.calculatePercentageChange(comparisonFocus, currentFocus)
	trends.EfficiencyTrend = s.calculatePercentageChange(comparisonEfficiency, currentEfficiency)

	// Calculate peak hours consistency
	trends.PeakHoursConsistency = s.calculatePeakHoursConsistency(currentBlocks)

	return trends, nil
}

// calculateProductiveTime calculates total productive time
func (s *TimeAnalyticsService) calculateProductiveTime(blocks []*TimeBlock) int {
	productiveTime := 0
	for _, block := range blocks {
		if block.Category == "work" || block.Category == "study" || block.Category == "focus" {
			productiveTime += block.Duration
		}
	}
	return productiveTime
}

// calculateFocusScore calculates focus score
func (s *TimeAnalyticsService) calculateFocusScore(blocks []*TimeBlock) float64 {
	totalTime := 0
	productiveTime := 0

	for _, block := range blocks {
		totalTime += block.Duration
		if block.Category == "work" || block.Category == "study" || block.Category == "focus" {
			productiveTime += block.Duration
		}
	}

	if totalTime == 0 {
		return 0.0
	}
	return float64(productiveTime) / float64(totalTime)
}

// calculateEfficiencyScore calculates efficiency score
func (s *TimeAnalyticsService) calculateEfficiencyScore(blocks []*TimeBlock) float64 {
	if len(blocks) == 0 {
		return 0.0
	}

	completedBlocks := 0
	for _, block := range blocks {
		if block.IsCompleted {
			completedBlocks++
		}
	}

	return float64(completedBlocks) / float64(len(blocks))
}

// calculatePercentageChange calculates percentage change between two values
func (s *TimeAnalyticsService) calculatePercentageChange(old, new float64) float64 {
	if old == 0 {
		if new == 0 {
			return 0.0
		}
		return 100.0
	}
	return ((new - old) / old) * 100.0
}

// calculatePeakHoursConsistency calculates how consistent peak hours are
func (s *TimeAnalyticsService) calculatePeakHoursConsistency(blocks []*TimeBlock) float64 {
	hourlyActivity := make([]int, 24)

	for _, block := range blocks {
		startHour := block.StartTime.Hour()
		endHour := block.EndTime.Hour()
		for hour := startHour; hour <= endHour; hour++ {
			hourlyActivity[hour]++
		}
	}

	// Calculate variance in hourly activity
	totalActivity := 0
	for _, activity := range hourlyActivity {
		totalActivity += activity
	}

	if totalActivity == 0 {
		return 0.0
	}

	mean := float64(totalActivity) / 24.0
	variance := 0.0
	for _, activity := range hourlyActivity {
		diff := float64(activity) - mean
		variance += diff * diff
	}
	variance /= 24.0

	// Convert variance to consistency score (lower variance = higher consistency)
	// Normalize to 0-1 range
	maxVariance := mean * mean // theoretical maximum variance
	if maxVariance == 0 {
		return 1.0
	}

	consistency := 1.0 - (variance / maxVariance)
	if consistency < 0 {
		consistency = 0.0
	}
	if consistency > 1 {
		consistency = 1.0
	}

	return consistency
}

// findPeakHours finds the hours with the most activity
func (s *TimeAnalyticsService) findPeakHours(hourlyActivity []int) []int {
	type hourActivity struct {
		hour     int
		activity int
	}

	var hours []hourActivity
	for hour, activity := range hourlyActivity {
		hours = append(hours, hourActivity{hour, activity})
	}

	// Sort by activity (descending)
	sort.Slice(hours, func(i, j int) bool {
		return hours[i].activity > hours[j].activity
	})

	// Return top 3 peak hours
	peakHours := make([]int, 0, 3)
	for i := 0; i < 3 && i < len(hours); i++ {
		if hours[i].activity > 0 {
			peakHours = append(peakHours, hours[i].hour)
		}
	}

	return peakHours
}

// generateRecommendations generates personalized recommendations
func (s *TimeAnalyticsService) generateRecommendations(report *TimeReport) []string {
	var recommendations []string

	// Focus score recommendations
	if report.FocusScore < 0.5 {
		recommendations = append(recommendations, "Consider reducing distractions and focusing more on productive activities")
	} else if report.FocusScore > 0.8 {
		recommendations = append(recommendations, "Great focus! Consider taking more breaks to maintain sustainability")
	}

	// Efficiency recommendations
	if report.EfficiencyScore < 0.6 {
		recommendations = append(recommendations, "Try breaking down large tasks into smaller, manageable chunks")
	}

	// Peak hours recommendations
	if len(report.PeakHours) > 0 {
		peakHour := report.PeakHours[0]
		if peakHour >= 9 && peakHour <= 17 {
			recommendations = append(recommendations, "Your peak productivity aligns well with standard work hours")
		} else {
			recommendations = append(recommendations, "Consider scheduling important tasks during your peak hours")
		}
	}

	// Break time recommendations
	if report.BreakTime < report.TotalTime/10 { // Less than 10% break time
		recommendations = append(recommendations, "Consider taking more regular breaks to maintain productivity")
	}

	// Trend-based recommendations
	if report.Trends != nil {
		if report.Trends.ProductiveTimeTrend < -10 {
			recommendations = append(recommendations, "Productive time has decreased significantly - review your schedule")
		}
		if report.Trends.FocusScoreTrend < -15 {
			recommendations = append(recommendations, "Focus score is declining - consider time management techniques")
		}
	}

	// Category-based recommendations
	if report.CategoryBreakdown["work"] > 0 && report.CategoryBreakdown["break"] == 0 {
		recommendations = append(recommendations, "Remember to schedule regular breaks for better productivity")
	}

	return recommendations
}

// GetTimeDistribution returns time distribution by category
func (s *TimeAnalyticsService) GetTimeDistribution(userID string, startDate, endDate time.Time) (map[string]int, error) {
	blocks, err := s.getTimeBlocksForPeriod(userID, startDate, endDate)
	if err != nil {
		return nil, err
	}

	distribution := make(map[string]int)
	for _, block := range blocks {
		category := block.Category
		if category == "" {
			category = "uncategorized"
		}
		distribution[category] += block.Duration
	}

	return distribution, nil
}

// GetProductivityScore calculates an overall productivity score
func (s *TimeAnalyticsService) GetProductivityScore(userID string, startDate, endDate time.Time) (float64, error) {
	blocks, err := s.getTimeBlocksForPeriod(userID, startDate, endDate)
	if err != nil {
		return 0, err
	}

	if len(blocks) == 0 {
		return 0, nil
	}

	totalTime := 0
	productiveTime := 0
	completedBlocks := 0

	for _, block := range blocks {
		totalTime += block.Duration

		if block.Category == "work" || block.Category == "study" || block.Category == "focus" {
			productiveTime += block.Duration
		}

		if block.IsCompleted {
			completedBlocks++
		}
	}

	// Calculate weighted productivity score
	focusScore := float64(productiveTime) / float64(totalTime)
	efficiencyScore := float64(completedBlocks) / float64(len(blocks))

	// Weighted average (70% focus, 30% efficiency)
	productivityScore := (focusScore * 0.7) + (efficiencyScore * 0.3)

	return productivityScore, nil
}

// ExportTimeReport exports a time report to JSON
func (s *TimeAnalyticsService) ExportTimeReport(report *TimeReport) ([]byte, error) {
	return json.MarshalIndent(report, "", "  ")
}

// GetTimeInsights returns insights about time usage patterns
func (s *TimeAnalyticsService) GetTimeInsights(userID string, startDate, endDate time.Time) (map[string]interface{}, error) {
	insights := make(map[string]interface{})

	// Get basic metrics
	blocks, err := s.getTimeBlocksForPeriod(userID, startDate, endDate)
	if err != nil {
		return nil, err
	}

	// Calculate insights
	totalTime := 0
	productiveTime := 0
	longestBlock := 0
	shortestBlock := math.MaxInt32
	blockCount := len(blocks)

	for _, block := range blocks {
		totalTime += block.Duration

		if block.Category == "work" || block.Category == "study" || block.Category == "focus" {
			productiveTime += block.Duration
		}

		if block.Duration > longestBlock {
			longestBlock = block.Duration
		}
		if block.Duration < shortestBlock {
			shortestBlock = block.Duration
		}
	}

	insights["total_blocks"] = blockCount
	insights["total_time_hours"] = float64(totalTime) / 3600.0
	insights["productive_time_hours"] = float64(productiveTime) / 3600.0
	insights["longest_block_minutes"] = longestBlock / 60
	insights["shortest_block_minutes"] = shortestBlock / 60
	insights["average_block_minutes"] = 0
	if blockCount > 0 {
		insights["average_block_minutes"] = totalTime / blockCount / 60
	}

	// Focus score
	if totalTime > 0 {
		insights["focus_score"] = float64(productiveTime) / float64(totalTime)
	} else {
		insights["focus_score"] = 0.0
	}

	return insights, nil
}
