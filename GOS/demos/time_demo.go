package main

import (
	"fmt"
	stdtime "time"

	"derivatives-gateway/time"
)

func main() {
	fmt.Println("🕐 ACTORS Time Management System Demo")
	fmt.Println("=====================================")

	// Demo 1: Time Zone Management
	fmt.Println("\n1. Time Zone Management")
	demoTimeZones()

	// Demo 2: Scheduled Events
	fmt.Println("\n2. Scheduled Events")
	demoScheduledEvents()

	// Demo 3: Workflow Management
	fmt.Println("\n3. Workflow Management")
	demoWorkflowManagement()

	// Demo 4: Time Analytics
	fmt.Println("\n4. Time Analytics")
	demoTimeAnalytics()

	// Demo 5: Orchestration
	fmt.Println("\n5. Workflow Orchestration")
	demoOrchestration()

	fmt.Println("\n✅ Time Management Demo Completed!")
}

func demoTimeZones() {
	// Create time zones
	timeZones := []time.TimeZone{
		{
			Name:        "UTC",
			Offset:      0,
			DisplayName: "Coordinated Universal Time",
			IsActive:    true,
			CreatedAt:   stdtime.Now(),
		},
		{
			Name:        "PST",
			Offset:      -8 * 60 * 60,
			DisplayName: "Pacific Standard Time",
			IsActive:    true,
			CreatedAt:   stdtime.Now(),
		},
		{
			Name:        "EST",
			Offset:      -5 * 60 * 60,
			DisplayName: "Eastern Standard Time",
			IsActive:    true,
			CreatedAt:   stdtime.Now(),
		},
	}

	for _, tz := range timeZones {
		fmt.Printf("  📍 %s (%s): UTC%+d\n", tz.DisplayName, tz.Name, tz.Offset/3600)
	}
}

func demoScheduledEvents() {
	now := stdtime.Now()
	nextRun := now.Add(stdtime.Hour)

	events := []time.ScheduledTimeEvent{
		{
			ID:          "daily-standup",
			Name:        "Daily Standup",
			Description: "Daily team standup meeting",
			EventType:   "cron",
			Schedule:    "0 9 * * 1-5", // 9 AM weekdays
			Timezone:    "UTC",
			IsActive:    true,
			NextRun:     &nextRun,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		{
			ID:          "weekly-review",
			Name:        "Weekly Review",
			Description: "Weekly project review meeting",
			EventType:   "cron",
			Schedule:    "0 14 * * 5", // 2 PM Fridays
			Timezone:    "UTC",
			IsActive:    true,
			NextRun:     &nextRun,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
		{
			ID:          "health-check",
			Name:        "System Health Check",
			Description: "Automated system health check",
			EventType:   "interval",
			Schedule:    "5m", // Every 5 minutes
			Timezone:    "UTC",
			IsActive:    true,
			NextRun:     &nextRun,
			CreatedAt:   now,
			UpdatedAt:   now,
		},
	}

	for _, event := range events {
		fmt.Printf("  ⏰ %s: %s (%s)\n", event.Name, event.Schedule, event.EventType)
		if event.NextRun != nil {
			fmt.Printf("      Next run: %s\n", event.NextRun.Format("2006-01-02 15:04:05"))
		}
	}
}

func demoWorkflowManagement() {
	now := stdtime.Now()

	// Create workflow phases
	phases := []time.WorkflowPhase{
		{
			PhaseID:        "planning",
			Name:           "Planning Phase",
			Type:           "focus",
			StartTime:      now,
			Duration:       1800, // 30 minutes
			TargetDuration: 1800,
			IsCompleted:    true,
			Success:        true,
			Metrics: map[string]interface{}{
				"focus_score":  0.85,
				"distractions": 2,
			},
		},
		{
			PhaseID:        "execution",
			Name:           "Execution Phase",
			Type:           "focus",
			StartTime:      now.Add(30 * stdtime.Minute),
			Duration:       7200, // 2 hours
			TargetDuration: 7200,
			IsCompleted:    true,
			Success:        true,
			Metrics: map[string]interface{}{
				"focus_score":  0.92,
				"distractions": 1,
			},
		},
		{
			PhaseID:        "review",
			Name:           "Review Phase",
			Type:           "focus",
			StartTime:      now.Add(2*stdtime.Hour + 30*stdtime.Minute),
			Duration:       900, // 15 minutes
			TargetDuration: 900,
			IsCompleted:    false,
			Success:        false,
			Metrics: map[string]interface{}{
				"focus_score":  0.0,
				"distractions": 0,
			},
		},
	}

	// Create workflow context
	workflowCtx := time.WorkflowContext{
		UserID:       "user-123",
		WorkflowID:   "daily-productivity",
		SessionID:    "session-456",
		StartTime:    now,
		CurrentPhase: "review",
		PhaseHistory: phases,
		State:        time.WorkflowStateActive,
		CreatedAt:    now,
		UpdatedAt:    now,
	}

	fmt.Printf("  🔄 Workflow: %s\n", workflowCtx.WorkflowID)
	fmt.Printf("  👤 User: %s\n", workflowCtx.UserID)
	fmt.Printf("  📊 Current Phase: %s\n", workflowCtx.CurrentPhase)
	fmt.Printf("  📈 State: %s\n", workflowCtx.State)

	totalDuration := 0
	completedPhases := 0
	for _, phase := range phases {
		totalDuration += phase.Duration
		if phase.IsCompleted {
			completedPhases++
		}
		fmt.Printf("    - %s: %d minutes (%s)\n",
			phase.Name, phase.Duration/60,
			map[bool]string{true: "✅", false: "⏳"}[phase.IsCompleted])
	}

	fmt.Printf("  ⏱️  Total Duration: %d minutes\n", totalDuration/60)
	fmt.Printf("  📊 Completion: %d/%d phases\n", completedPhases, len(phases))
}

func demoTimeAnalytics() {
	now := stdtime.Now()

	analytics := time.TimeAnalytics{
		UserID:           "user-123",
		Date:             now.Truncate(24 * stdtime.Hour),
		TotalTime:        28800, // 8 hours
		ProductiveTime:   21600, // 6 hours
		BreakTime:        7200,  // 2 hours
		FocusScore:       0.85,
		EfficiencyScore:  0.75,
		PeakHours:        []int{9, 10, 11, 14, 15},
		DistractionCount: 5,
	}

	fmt.Printf("  📅 Date: %s\n", analytics.Date.Format("2006-01-02"))
	fmt.Printf("  ⏱️  Total Time: %d hours\n", analytics.TotalTime/3600)
	fmt.Printf("  💼 Productive Time: %d hours\n", analytics.ProductiveTime/3600)
	fmt.Printf("  ☕ Break Time: %d hours\n", analytics.BreakTime/3600)
	fmt.Printf("  🎯 Focus Score: %.1f%%\n", analytics.FocusScore*100)
	fmt.Printf("  📈 Efficiency Score: %.1f%%\n", analytics.EfficiencyScore*100)
	fmt.Printf("  🚫 Distractions: %d\n", analytics.DistractionCount)

	fmt.Printf("  📊 Peak Hours: ")
	for i, hour := range analytics.PeakHours {
		if i > 0 {
			fmt.Printf(", ")
		}
		fmt.Printf("%d:00", hour)
	}
	fmt.Println()
}

func demoOrchestration() {
	now := stdtime.Now()

	orchestration := time.OrchestrationContext{
		OrchestrationID: "daily-orchestration",
		Name:            "Daily Productivity Orchestration",
		Description:     "Orchestrates daily productivity workflow with multiple participants",
		Type:            "sequential",
		Workflows: []time.OrchestrationWorkflow{
			{
				WorkflowID:     "morning-routine",
				UserID:         "user-123",
				SessionID:      "session-456",
				StartCondition: "time:09:00",
				EndCondition:   "time:12:00",
				Priority:       1,
				IsActive:       true,
				IsCompleted:    false,
			},
			{
				WorkflowID:     "afternoon-focus",
				UserID:         "user-123",
				SessionID:      "session-789",
				StartCondition: "workflow:morning-routine:completed",
				EndCondition:   "time:17:00",
				Priority:       2,
				IsActive:       false,
				IsCompleted:    false,
			},
		},
		Participants: []time.OrchestrationParticipant{
			{
				UserID:      "user-123",
				Role:        "primary",
				Permissions: []string{"execute", "modify", "monitor"},
			},
			{
				UserID:      "user-456",
				Role:        "observer",
				Permissions: []string{"monitor"},
			},
		},
		State:     time.OrchestrationStateActive,
		StartTime: now,
		CreatedAt: now,
		UpdatedAt: now,
	}

	fmt.Printf("  🎭 Orchestration: %s\n", orchestration.Name)
	fmt.Printf("  📝 Type: %s\n", orchestration.Type)
	fmt.Printf("  📊 State: %s\n", orchestration.State)
	fmt.Printf("  🔄 Workflows: %d\n", len(orchestration.Workflows))
	fmt.Printf("  👥 Participants: %d\n", len(orchestration.Participants))

	for i, workflow := range orchestration.Workflows {
		fmt.Printf("    %d. %s (Priority: %d)\n", i+1, workflow.WorkflowID, workflow.Priority)
		fmt.Printf("       Start: %s\n", workflow.StartCondition)
		fmt.Printf("       End: %s\n", workflow.EndCondition)
		fmt.Printf("       Status: %s\n", map[bool]string{true: "🟢 Active", false: "🔴 Inactive"}[workflow.IsActive])
	}

	for _, participant := range orchestration.Participants {
		fmt.Printf("  👤 %s (%s): %v\n", participant.UserID, participant.Role, participant.Permissions)
	}
}
