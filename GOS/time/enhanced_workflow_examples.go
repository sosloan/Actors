package time

import (
	"context"
	"fmt"
	"log"
	"time"
	stdtime "time"

	"github.com/jmoiron/sqlx"
	_ "github.com/mattn/go-sqlite3"
)

// ExampleEnhancedWorkflowEvents demonstrates the enhanced workflow event system
func ExampleEnhancedWorkflowEvents() {
	log.Println("\n=== Enhanced Workflow Events Example ===")

	// Initialize database
	db, err := sqlx.Open("sqlite3", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create time service
	timeService := NewTimeService(db)
	if err := timeService.Initialize(); err != nil {
		log.Fatal(err)
	}

	// Create workflow engine
	workflowEngine := NewWorkflowEngine(timeService, db)

	// Create context
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start services
	timeService.Start(ctx)
	defer timeService.Stop()

	// Example 1: Demonstrate enhanced event creation
	exampleEnhancedEventCreation(workflowEngine, ctx)

	// Example 2: Demonstrate workflow lifecycle events
	exampleWorkflowLifecycleEvents(workflowEngine, ctx)

	// Example 3: Demonstrate event replay and analytics
	exampleEventReplayAndAnalytics(workflowEngine, ctx)

	// Example 4: Demonstrate error handling and recovery
	exampleErrorHandlingAndRecovery(workflowEngine, ctx)

	log.Println("Enhanced workflow events example completed")
}

// exampleEnhancedEventCreation demonstrates the enhanced event creation system
func exampleEnhancedEventCreation(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Enhanced Event Creation Example ---")

	// Create a workflow with rich metadata
	metadata := map[string]interface{}{
		"project":         "Advanced Time System",
		"priority":        "high",
		"environment":     "production",
		"external_id":     "PROJ-123",
		"external_system": "jira",
		"team":            "backend",
		"sprint":          "Sprint 42",
		"tags":            []string{"go", "workflow", "time-management", "production"},
		"custom_field":    "custom_value",
		"estimated_hours": 8,
	}

	// Start workflow
	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "deep_work_flow", "demo_user", metadata)
	if err != nil {
		log.Printf("Error starting workflow: %v", err)
		return
	}

	log.Printf("✅ Started workflow with enhanced metadata")
	log.Printf("   Session ID: %s", workflowCtx.SessionID)
	log.Printf("   Project: %s", metadata["project"])
	log.Printf("   External ID: %s", metadata["external_id"])
	log.Printf("   Tags: %v", metadata["tags"])

	// Complete a phase with detailed metrics
	time.Sleep(100 * time.Millisecond)
	phaseMetrics := map[string]interface{}{
		"environment_ready":    true,
		"distractions_cleared": true,
		"focus_score":          0.92,
		"efficiency":           0.88,
		"energy_level":         0.85,
		"mood":                 "focused",
		"tools_used":           []string{"vscode", "terminal", "browser"},
		"interruptions":        0,
	}

	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "preparation", true, phaseMetrics); err != nil {
		log.Printf("Error completing phase: %v", err)
	} else {
		log.Printf("✅ Completed phase with detailed metrics")
		log.Printf("   Focus Score: %.2f", phaseMetrics["focus_score"])
		log.Printf("   Efficiency: %.2f", phaseMetrics["efficiency"])
		log.Printf("   Tools Used: %v", phaseMetrics["tools_used"])
	}
}

// exampleWorkflowLifecycleEvents demonstrates workflow lifecycle event tracking
func exampleWorkflowLifecycleEvents(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Workflow Lifecycle Events Example ---")

	// Start a workflow
	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "learning_flow", "student_user", map[string]interface{}{
		"subject":        "Advanced Go Programming",
		"level":          "intermediate",
		"learning_style": "visual",
		"course_id":      "GO-ADV-2024",
	})
	if err != nil {
		log.Printf("Error starting workflow: %v", err)
		return
	}

	log.Printf("🚀 Workflow started: %s", workflowCtx.SessionID)

	// Complete first phase
	time.Sleep(50 * time.Millisecond)
	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "review", true, map[string]interface{}{
		"previous_material_reviewed": true,
		"comprehension_score":        0.8,
	}); err != nil {
		log.Printf("Error completing review phase: %v", err)
	}

	// Pause the workflow
	if err := workflowEngine.PauseWorkflow(workflowCtx.SessionID); err != nil {
		log.Printf("Error pausing workflow: %v", err)
	} else {
		log.Printf("⏸️ Workflow paused")
	}

	// Wait a bit
	time.Sleep(100 * time.Millisecond)

	// Resume the workflow
	if err := workflowEngine.ResumeWorkflow(ctx, workflowCtx.SessionID); err != nil {
		log.Printf("Error resuming workflow: %v", err)
	} else {
		log.Printf("▶️ Workflow resumed")
	}

	// Complete remaining phases
	phases := []struct {
		phaseID string
		success bool
		metrics map[string]interface{}
	}{
		{
			"new_content",
			true,
			map[string]interface{}{
				"comprehension_score": 0.75,
				"engagement_level":    0.85,
				"notes_taken":         15,
			},
		},
		{
			"practice",
			true,
			map[string]interface{}{
				"practice_completed": true,
				"accuracy":           0.90,
				"time_taken":         1200, // 20 minutes
			},
		},
		{
			"reflection",
			true,
			map[string]interface{}{
				"notes_taken":           true,
				"key_points_identified": true,
				"next_steps_planned":    true,
			},
		},
	}

	for _, phase := range phases {
		time.Sleep(50 * time.Millisecond)
		if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, phase.phaseID, phase.success, phase.metrics); err != nil {
			log.Printf("Error completing phase %s: %v", phase.phaseID, err)
		} else {
			log.Printf("✅ Completed phase: %s", phase.phaseID)
		}
	}

	log.Printf("🎉 Workflow lifecycle completed with full event tracking")
}

// exampleEventReplayAndAnalytics demonstrates event replay and analytics capabilities
func exampleEventReplayAndAnalytics(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Event Replay and Analytics Example ---")

	// Create event replay system
	replay := NewWorkflowEventReplay(workflowEngine.db)

	// Start multiple workflows to generate events
	workflows := []struct {
		workflowID string
		userID     string
		metadata   map[string]interface{}
	}{
		{
			"deep_work_flow",
			"user1",
			map[string]interface{}{
				"project":     "Project Alpha",
				"priority":    "high",
				"environment": "development",
			},
		},
		{
			"creative_flow",
			"user2",
			map[string]interface{}{
				"project":     "Project Beta",
				"priority":    "medium",
				"environment": "staging",
			},
		},
		{
			"learning_flow",
			"user3",
			map[string]interface{}{
				"project":     "Project Gamma",
				"priority":    "low",
				"environment": "production",
			},
		},
	}

	var sessionIDs []string

	// Start workflows and collect session IDs
	for _, wf := range workflows {
		workflowCtx, err := workflowEngine.StartWorkflow(ctx, wf.workflowID, wf.userID, wf.metadata)
		if err != nil {
			log.Printf("Error starting workflow %s: %v", wf.workflowID, err)
			continue
		}
		sessionIDs = append(sessionIDs, workflowCtx.SessionID)
		log.Printf("Started workflow: %s (Session: %s)", wf.workflowID, workflowCtx.SessionID)
	}

	// Complete some phases to generate more events
	for i, sessionID := range sessionIDs {
		time.Sleep(50 * time.Millisecond)
		phaseID := "preparation"
		if i == 1 {
			phaseID = "inspiration"
		} else if i == 2 {
			phaseID = "review"
		}

		if err := workflowEngine.CompletePhase(ctx, sessionID, phaseID, true, map[string]interface{}{
			"completion_rate": 0.8 + float64(i)*0.05,
			"quality_score":   0.85 + float64(i)*0.03,
		}); err != nil {
			log.Printf("Error completing phase: %v", err)
		}
	}

	// Demonstrate event replay for each session
	for _, sessionID := range sessionIDs {
		log.Printf("\n📊 Event Summary for Session: %s", sessionID)
		summary := replay.GetEventSummary(sessionID)
		log.Printf("   Total Events: %d", summary["total_events"])
		log.Printf("   Duration: %.2f seconds", summary["duration"])

		if eventTypes, ok := summary["event_types"].(map[string]int); ok {
			log.Printf("   Event Types:")
			for eventType, count := range eventTypes {
				log.Printf("     %s: %d", eventType, count)
			}
		}

		if categories, ok := summary["categories"].(map[string]int); ok {
			log.Printf("   Categories:")
			for category, count := range categories {
				log.Printf("     %s: %d", category, count)
			}
		}
	}

	log.Printf("✅ Event replay and analytics demonstration completed")
}

// exampleErrorHandlingAndRecovery demonstrates error handling and recovery
func exampleErrorHandlingAndRecovery(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Error Handling and Recovery Example ---")

	// Start a workflow
	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "deep_work_flow", "error_test_user", map[string]interface{}{
		"project":     "Error Handling Test",
		"priority":    "high",
		"environment": "testing",
		"retry_count": 0,
	})
	if err != nil {
		log.Printf("Error starting workflow: %v", err)
		return
	}

	log.Printf("🚀 Started workflow for error testing: %s", workflowCtx.SessionID)

	// Complete preparation phase successfully
	time.Sleep(50 * time.Millisecond)
	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "preparation", true, map[string]interface{}{
		"environment_ready": true,
	}); err != nil {
		log.Printf("Error completing preparation phase: %v", err)
	}

	// Simulate a phase failure
	log.Printf("❌ Simulating phase failure...")
	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "focus_session_1", false, map[string]interface{}{
		"error_message": "Network connectivity issues",
		"error_type":    "network_error",
		"retry_count":   1,
		"focus_score":   0.3, // Low due to interruption
	}); err != nil {
		log.Printf("Error completing focus session: %v", err)
	}

	// Demonstrate error event creation
	errorEvent, err := CreateWorkflowErrorEvent(workflowCtx, "focus_session_1", fmt.Errorf("network connectivity issues"))
	if err != nil {
		log.Printf("Error creating error event: %v", err)
	} else {
		if err := workflowEngine.timeService.AddTimeEvent(errorEvent); err != nil {
			log.Printf("Error adding error event: %v", err)
		} else {
			log.Printf("✅ Created error event: %s", errorEvent.ID)
		}
	}

	// Demonstrate recovery by completing the phase successfully on retry
	log.Printf("🔄 Attempting recovery...")
	time.Sleep(100 * time.Millisecond)
	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "focus_session_1", true, map[string]interface{}{
		"recovery_successful": true,
		"retry_count":         2,
		"focus_score":         0.88, // Good recovery
		"network_stable":      true,
	}); err != nil {
		log.Printf("Error completing recovery phase: %v", err)
	} else {
		log.Printf("✅ Recovery successful - phase completed")
	}

	// Complete remaining phases
	remainingPhases := []string{"short_break_1", "focus_session_2", "long_break", "focus_session_3", "completion"}
	for _, phaseID := range remainingPhases {
		time.Sleep(50 * time.Millisecond)
		if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, phaseID, true, map[string]interface{}{
			"completion_rate": 0.9,
			"quality_score":   0.85,
		}); err != nil {
			log.Printf("Error completing phase %s: %v", phaseID, err)
		}
	}

	log.Printf("🎉 Error handling and recovery demonstration completed")
}

// ExampleWorkflowEventBuilder demonstrates the fluent builder pattern
func ExampleWorkflowEventBuilder() {
	log.Println("\n=== Workflow Event Builder Example ===")

	// Create a custom event using the builder pattern
	builder := NewWorkflowEventBuilder().
		WithID("custom_event_123").
		WithUserID("builder_user").
		WithType(EventTypeMilestone).
		WithTitle("Custom Workflow Event").
		WithDescription("A custom event created using the builder pattern").
		WithPriority(PriorityHigh).
		WithStartTime(stdtime.Now()).
		WithEndTime(stdtime.Now().Add(30*stdtime.Minute)).
		WithDuration(30*stdtime.Minute).
		WithCategory(WorkflowEventCategoryExecution).
		WithSubCategory(WorkflowEventSubCategoryStart).
		WithWorkflowID("custom_workflow").
		WithSessionID("session_123").
		WithVersion("2.0").
		WithEnvironment("production").
		WithProject("Builder Demo").
		WithWorkflowPriority("critical").
		WithTraceID("trace_456").
		WithInstructions([]string{
			"Initialize the system",
			"Load configuration",
			"Start monitoring",
		}).
		WithContext(map[string]interface{}{
			"system_version": "1.2.3",
			"config_loaded":  true,
		}).
		WithExternalID("EXT-789").
		WithExternalSystem("monitoring").
		WithCustomField("custom_metric", 42.5).
		WithCustomField("tags", []string{"demo", "builder", "custom"}).
		WithIsActive(true).
		WithIsCompleted(false)

	// Build the event
	event, err := builder.Build()
	if err != nil {
		log.Printf("Error building event: %v", err)
		return
	}

	log.Printf("✅ Successfully created custom event using builder pattern")
	log.Printf("   Event ID: %s", event.ID)
	log.Printf("   Title: %s", event.Title)
	log.Printf("   Category: %s", event.Metadata["category"])
	log.Printf("   Sub Category: %s", event.Metadata["sub_category"])
	log.Printf("   Project: %s", event.Metadata["project"])
	log.Printf("   Environment: %s", event.Metadata["environment"])
	log.Printf("   Trace ID: %s", event.Metadata["trace_id"])
	log.Printf("   Custom Metric: %v", event.Metadata["custom_metric"])
	log.Printf("   Instructions: %v", event.Metadata["instructions"])
	log.Printf("   Context: %v", event.Metadata["context"])

	// Demonstrate validation
	log.Println("\n--- Builder Validation Example ---")

	// Try to build an invalid event (missing required fields)
	invalidBuilder := NewWorkflowEventBuilder().
		WithTitle("Invalid Event").
		WithDescription("This event is missing required fields")

	_, err = invalidBuilder.Build()
	if err != nil {
		log.Printf("✅ Correctly caught validation error: %v", err)
	} else {
		log.Printf("❌ Expected validation error but got none")
	}

	log.Println("Workflow event builder example completed")
}
