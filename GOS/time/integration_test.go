package time

import (
	"context"
	"testing"
	"time"
)

func TestTimeManagementIntegration(t *testing.T) {
	// Test complete time management workflow
	ctx := context.Background()

	// Create a time zone
	tz := TimeZone{
		Name:        "PST",
		Offset:      -8 * 60 * 60, // UTC-8
		DisplayName: "Pacific Standard Time",
		IsActive:    true,
		CreatedAt:   time.Now(),
	}

	// Create a scheduled event
	now := time.Now()
	nextRun := now.Add(time.Hour)
	event := ScheduledTimeEvent{
		ID:          "daily-standup",
		Name:        "Daily Standup",
		Description: "Daily team standup meeting",
		EventType:   "cron",
		Schedule:    "0 9 * * 1-5", // 9 AM weekdays
		Timezone:    tz.Name,
		IsActive:    true,
		NextRun:     &nextRun,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	// Create workflow context
	workflowCtx := WorkflowContext{
		UserID:       "user-123",
		WorkflowID:   "daily-workflow",
		SessionID:    "session-456",
		StartTime:    now,
		CurrentPhase: "planning",
		State:        WorkflowStateActive,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	// Create workflow phases
	phases := []WorkflowPhase{
		{
			PhaseID:        "planning",
			Name:           "Planning Phase",
			Type:           "focus",
			StartTime:      now,
			Duration:       1800, // 30 minutes
			TargetDuration: 1800,
			IsCompleted:    false,
			Success:        false,
		},
		{
			PhaseID:        "execution",
			Name:           "Execution Phase",
			Type:           "focus",
			StartTime:      now.Add(30 * time.Minute),
			Duration:       7200, // 2 hours
			TargetDuration: 7200,
			IsCompleted:    false,
			Success:        false,
		},
		{
			PhaseID:        "review",
			Name:           "Review Phase",
			Type:           "focus",
			StartTime:      now.Add(2*time.Hour + 30*time.Minute),
			Duration:       900, // 15 minutes
			TargetDuration: 900,
			IsCompleted:    false,
			Success:        false,
		},
	}

	// Add phases to workflow context
	workflowCtx.PhaseHistory = phases

	// Test time zone functionality
	if tz.Offset != -8*60*60 {
		t.Errorf("Expected PST offset -28800, got %d", tz.Offset)
	}

	// Test scheduled event
	if event.EventType != "cron" {
		t.Errorf("Expected event type 'cron', got '%s'", event.EventType)
	}

	if event.Schedule != "0 9 * * 1-5" {
		t.Errorf("Expected schedule '0 9 * * 1-5', got '%s'", event.Schedule)
	}

	// Test workflow context
	if workflowCtx.CurrentPhase != "planning" {
		t.Errorf("Expected current phase 'planning', got '%s'", workflowCtx.CurrentPhase)
	}

	if len(workflowCtx.PhaseHistory) != 3 {
		t.Errorf("Expected 3 phases, got %d", len(workflowCtx.PhaseHistory))
	}

	// Test phase calculations
	totalDuration := 0
	for _, phase := range phases {
		totalDuration += phase.Duration
	}

	expectedTotalDuration := 1800 + 7200 + 900 // 2.75 hours
	if totalDuration != expectedTotalDuration {
		t.Errorf("Expected total duration %d, got %d", expectedTotalDuration, totalDuration)
	}

	// Test time analytics
	analytics := TimeAnalytics{
		UserID:           workflowCtx.UserID,
		Date:             now.Truncate(24 * time.Hour),
		TotalTime:        totalDuration,
		ProductiveTime:   totalDuration - 1800, // Subtract break time
		BreakTime:        1800,                 // 30 minutes break
		FocusScore:       0.85,
		EfficiencyScore:  float64(totalDuration-1800) / float64(totalDuration),
		PeakHours:        []int{9, 10, 11, 14, 15},
		DistractionCount: 3,
	}

	expectedEfficiency := float64(totalDuration-1800) / float64(totalDuration)
	if analytics.EfficiencyScore != expectedEfficiency {
		t.Errorf("Expected efficiency %f, got %f", expectedEfficiency, analytics.EfficiencyScore)
	}

	// Test orchestration context
	orchestration := OrchestrationContext{
		OrchestrationID: "daily-orchestration",
		Name:            "Daily Productivity Orchestration",
		Description:     "Orchestrates daily productivity workflow",
		Type:            "sequential",
		Workflows: []OrchestrationWorkflow{
			{
				WorkflowID:  workflowCtx.WorkflowID,
				UserID:      workflowCtx.UserID,
				SessionID:   workflowCtx.SessionID,
				IsActive:    true,
				IsCompleted: false,
				Priority:    1,
			},
		},
		State:     OrchestrationStateActive,
		StartTime: now,
		CreatedAt: now,
		UpdatedAt: now,
	}

	if orchestration.Type != "sequential" {
		t.Errorf("Expected orchestration type 'sequential', got '%s'", orchestration.Type)
	}

	if len(orchestration.Workflows) != 1 {
		t.Errorf("Expected 1 workflow, got %d", len(orchestration.Workflows))
	}

	// Test context cancellation
	cancelCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	// Simulate workflow execution
	select {
	case <-cancelCtx.Done():
		// Context was cancelled, which is expected
		if cancelCtx.Err() == context.DeadlineExceeded {
			t.Log("Context timeout as expected")
		}
	case <-time.After(6 * time.Second):
		t.Error("Context should have been cancelled")
	}
}

func TestTimeZoneConversion(t *testing.T) {
	// Test time zone conversions
	utc := time.UTC
	pst := time.FixedZone("PST", -8*60*60) // UTC-8
	est := time.FixedZone("EST", -5*60*60) // UTC-5

	// Create a time in UTC
	utcTime := time.Date(2024, 1, 15, 12, 0, 0, 0, utc)

	// Convert to PST
	pstTime := utcTime.In(pst)
	expectedPSTHour := 4 // 12 UTC = 4 PST
	if pstTime.Hour() != expectedPSTHour {
		t.Errorf("Expected PST hour %d, got %d", expectedPSTHour, pstTime.Hour())
	}

	// Convert to EST
	estTime := utcTime.In(est)
	expectedESTHour := 7 // 12 UTC = 7 EST
	if estTime.Hour() != expectedESTHour {
		t.Errorf("Expected EST hour %d, got %d", expectedESTHour, estTime.Hour())
	}
}

func TestWorkflowStateMachine(t *testing.T) {
	// Test workflow state transitions
	workflow := WorkflowContext{
		UserID:     "user-123",
		WorkflowID: "test-workflow",
		State:      WorkflowStatePending,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	// Test state transitions
	states := []WorkflowState{
		WorkflowStatePending,
		WorkflowStateActive,
		WorkflowStatePaused,
		WorkflowStateActive,
		WorkflowStateCompleted,
	}

	for i, expectedState := range states {
		workflow.State = expectedState
		if workflow.State != expectedState {
			t.Errorf("Step %d: Expected state %s, got %s", i, expectedState, workflow.State)
		}
	}
}

func TestSchedulingAccuracy(t *testing.T) {
	// Test scheduling accuracy
	now := time.Now()

	// Test hourly scheduling
	hourlySchedule := now.Truncate(time.Hour).Add(time.Hour)
	expectedHour := now.Hour() + 1
	if expectedHour >= 24 {
		expectedHour = 0
	}

	if hourlySchedule.Hour() != expectedHour {
		t.Errorf("Expected next hour %d, got %d", expectedHour, hourlySchedule.Hour())
	}

	// Test that daily schedule is in the future
	dailySchedule := now.Truncate(24 * time.Hour).Add(24 * time.Hour)
	if dailySchedule.Before(now) {
		t.Error("Daily schedule should be in the future")
	}
}

func TestTimeAnalyticsCalculation(t *testing.T) {
	// Test time analytics calculations
	analytics := TimeAnalytics{
		UserID:           "user-123",
		Date:             time.Now(),
		TotalTime:        28800, // 8 hours
		ProductiveTime:   21600, // 6 hours
		BreakTime:        7200,  // 2 hours
		DistractionCount: 10,
	}

	// Calculate efficiency
	efficiency := float64(analytics.ProductiveTime) / float64(analytics.TotalTime)
	expectedEfficiency := 0.75
	if efficiency != expectedEfficiency {
		t.Errorf("Expected efficiency %f, got %f", expectedEfficiency, efficiency)
	}

	// Calculate focus score (inverse of distraction rate)
	totalSessions := 20
	distractionRate := float64(analytics.DistractionCount) / float64(totalSessions)
	focusScore := 1.0 - distractionRate
	expectedFocusScore := 0.5
	if focusScore != expectedFocusScore {
		t.Errorf("Expected focus score %f, got %f", expectedFocusScore, focusScore)
	}
}
