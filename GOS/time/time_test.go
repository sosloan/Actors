package time

import (
	"testing"
	"time"
)

func TestTimeZone(t *testing.T) {
	tz := TimeZone{
		Name:        "UTC",
		Offset:      0,
		DisplayName: "Coordinated Universal Time",
		IsActive:    true,
		CreatedAt:   time.Now(),
	}

	if tz.Name != "UTC" {
		t.Errorf("Expected timezone name 'UTC', got '%s'", tz.Name)
	}

	if tz.Offset != 0 {
		t.Errorf("Expected offset 0, got %d", tz.Offset)
	}

	if !tz.IsActive {
		t.Error("Expected timezone to be active")
	}
}

func TestScheduledTimeEvent(t *testing.T) {
	now := time.Now()
	nextRun := now.Add(time.Hour)

	event := ScheduledTimeEvent{
		ID:          "test-event-1",
		Name:        "Test Event",
		Description: "A test scheduled event",
		EventType:   "interval",
		Schedule:    "1h",
		Timezone:    "UTC",
		IsActive:    true,
		NextRun:     &nextRun,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	if event.ID != "test-event-1" {
		t.Errorf("Expected event ID 'test-event-1', got '%s'", event.ID)
	}

	if event.EventType != "interval" {
		t.Errorf("Expected event type 'interval', got '%s'", event.EventType)
	}

	if !event.IsActive {
		t.Error("Expected event to be active")
	}

	if event.NextRun == nil {
		t.Error("Expected NextRun to be set")
	}
}

func TestTimeAnalytics(t *testing.T) {
	analytics := TimeAnalytics{
		UserID:           "user-123",
		Date:             time.Now(),
		TotalTime:        28800, // 8 hours
		ProductiveTime:   21600, // 6 hours
		BreakTime:        7200,  // 2 hours
		FocusScore:       0.85,
		EfficiencyScore:  0.78,
		PeakHours:        []int{9, 10, 11, 14, 15},
		DistractionCount: 5,
	}

	if analytics.UserID != "user-123" {
		t.Errorf("Expected user ID 'user-123', got '%s'", analytics.UserID)
	}

	if analytics.TotalTime != 28800 {
		t.Errorf("Expected total time 28800 seconds, got %d", analytics.TotalTime)
	}

	if analytics.FocusScore < 0.0 || analytics.FocusScore > 1.0 {
		t.Errorf("Focus score should be between 0.0 and 1.0, got %f", analytics.FocusScore)
	}

	if len(analytics.PeakHours) != 5 {
		t.Errorf("Expected 5 peak hours, got %d", len(analytics.PeakHours))
	}
}

func TestWorkflowContext(t *testing.T) {
	now := time.Now()
	context := WorkflowContext{
		UserID:       "user-123",
		WorkflowID:   "workflow-456",
		SessionID:    "session-789",
		StartTime:    now,
		CurrentPhase: "focus",
		State:        WorkflowStateActive,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	if context.UserID != "user-123" {
		t.Errorf("Expected user ID 'user-123', got '%s'", context.UserID)
	}

	if context.WorkflowID != "workflow-456" {
		t.Errorf("Expected workflow ID 'workflow-456', got '%s'", context.WorkflowID)
	}

	if context.CurrentPhase != "focus" {
		t.Errorf("Expected current phase 'focus', got '%s'", context.CurrentPhase)
	}

	if context.State != WorkflowStateActive {
		t.Errorf("Expected state 'active', got '%s'", context.State)
	}
}

func TestWorkflowPhase(t *testing.T) {
	now := time.Now()
	endTime := now.Add(25 * time.Minute)

	phase := WorkflowPhase{
		PhaseID:        "phase-1",
		Name:           "Focus Session",
		Type:           "focus",
		StartTime:      now,
		EndTime:        &endTime,
		Duration:       1500, // 25 minutes
		TargetDuration: 1500,
		IsCompleted:    true,
		Success:        true,
		Metrics: map[string]interface{}{
			"focus_score":  0.85,
			"distractions": 2,
		},
	}

	if phase.PhaseID != "phase-1" {
		t.Errorf("Expected phase ID 'phase-1', got '%s'", phase.PhaseID)
	}

	if phase.Type != "focus" {
		t.Errorf("Expected phase type 'focus', got '%s'", phase.Type)
	}

	if phase.Duration != 1500 {
		t.Errorf("Expected duration 1500 seconds, got %d", phase.Duration)
	}

	if !phase.IsCompleted {
		t.Error("Expected phase to be completed")
	}

	if !phase.Success {
		t.Error("Expected phase to be successful")
	}
}

func TestOrchestrationContext(t *testing.T) {
	now := time.Now()
	orchestration := OrchestrationContext{
		OrchestrationID: "orch-123",
		Name:            "Daily Workflow",
		Description:     "A daily productivity workflow",
		Type:            "sequential",
		State:           OrchestrationStateActive,
		StartTime:       now,
		CreatedAt:       now,
		UpdatedAt:       now,
	}

	if orchestration.OrchestrationID != "orch-123" {
		t.Errorf("Expected orchestration ID 'orch-123', got '%s'", orchestration.OrchestrationID)
	}

	if orchestration.Name != "Daily Workflow" {
		t.Errorf("Expected name 'Daily Workflow', got '%s'", orchestration.Name)
	}

	if orchestration.Type != "sequential" {
		t.Errorf("Expected type 'sequential', got '%s'", orchestration.Type)
	}

	if orchestration.State != OrchestrationStateActive {
		t.Errorf("Expected state 'active', got '%s'", orchestration.State)
	}
}

func TestWorkflowStateTransitions(t *testing.T) {
	// Test valid state transitions
	validTransitions := map[WorkflowState][]WorkflowState{
		WorkflowStatePending:   {WorkflowStateActive, WorkflowStateCancelled},
		WorkflowStateActive:    {WorkflowStatePaused, WorkflowStateCompleted, WorkflowStateFailed, WorkflowStateCancelled},
		WorkflowStatePaused:    {WorkflowStateActive, WorkflowStateCancelled},
		WorkflowStateCompleted: {},
		WorkflowStateFailed:    {},
		WorkflowStateCancelled: {},
	}

	for from, toStates := range validTransitions {
		for _, to := range toStates {
			// This is a conceptual test - in a real implementation,
			// you would test the actual state transition logic
			if from == to {
				t.Errorf("State transition from %s to %s should not be allowed", from, to)
			}
		}
	}
}

func TestTimeCalculations(t *testing.T) {
	// Test time duration calculations
	start := time.Now()
	end := start.Add(2*time.Hour + 30*time.Minute)
	duration := end.Sub(start)

	expectedDuration := 2*time.Hour + 30*time.Minute
	if duration != expectedDuration {
		t.Errorf("Expected duration %v, got %v", expectedDuration, duration)
	}

	// Test time zone calculations
	utc := time.UTC
	est := time.FixedZone("EST", -5*60*60) // UTC-5

	utcTime := time.Date(2024, 1, 15, 12, 0, 0, 0, utc)
	estTime := utcTime.In(est)

	expectedHour := 7 // 12 UTC = 7 EST
	if estTime.Hour() != expectedHour {
		t.Errorf("Expected EST hour %d, got %d", expectedHour, estTime.Hour())
	}
}

func TestWorkflowMetrics(t *testing.T) {
	// Test workflow efficiency calculation
	totalTime := 8 * 60 * 60      // 8 hours in seconds
	productiveTime := 6 * 60 * 60 // 6 hours in seconds
	expectedEfficiency := float64(productiveTime) / float64(totalTime)

	if expectedEfficiency != 0.75 {
		t.Errorf("Expected efficiency 0.75, got %f", expectedEfficiency)
	}

	// Test focus score calculation
	distractions := 5
	totalSessions := 20
	expectedFocusScore := 1.0 - (float64(distractions) / float64(totalSessions))

	if expectedFocusScore != 0.75 {
		t.Errorf("Expected focus score 0.75, got %f", expectedFocusScore)
	}
}

func TestSchedulingLogic(t *testing.T) {
	// Test cron-like scheduling
	now := time.Now()

	// Test hourly scheduling
	nextHour := now.Truncate(time.Hour).Add(time.Hour)
	if nextHour.Before(now) {
		t.Error("Next hour should be in the future")
	}

	// Test daily scheduling
	nextDay := now.Truncate(24 * time.Hour).Add(24 * time.Hour)
	if nextDay.Before(now) {
		t.Error("Next day should be in the future")
	}

	// Test weekly scheduling
	nextWeek := now.Truncate(7 * 24 * time.Hour).Add(7 * 24 * time.Hour)
	if nextWeek.Before(now) {
		t.Error("Next week should be in the future")
	}
}

// Benchmark tests
func BenchmarkTimeZoneCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		tz := TimeZone{
			Name:        "UTC",
			Offset:      0,
			DisplayName: "Coordinated Universal Time",
			IsActive:    true,
			CreatedAt:   time.Now(),
		}
		_ = tz
	}
}

func BenchmarkWorkflowContextCreation(b *testing.B) {
	for i := 0; i < b.N; i++ {
		context := WorkflowContext{
			UserID:       "user-123",
			WorkflowID:   "workflow-456",
			SessionID:    "session-789",
			StartTime:    time.Now(),
			CurrentPhase: "focus",
			State:        WorkflowStateActive,
			CreatedAt:    time.Now(),
			UpdatedAt:    time.Now(),
		}
		_ = context
	}
}

func BenchmarkTimeCalculations(b *testing.B) {
	start := time.Now()
	for i := 0; i < b.N; i++ {
		end := start.Add(time.Duration(i) * time.Minute)
		duration := end.Sub(start)
		_ = duration
	}
}
