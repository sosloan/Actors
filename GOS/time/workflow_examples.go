package time

import (
	"context"
	"log"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/mattn/go-sqlite3"
)

// ExampleComplexWorkflows demonstrates end-to-end context-aware complex time-based workflows
func ExampleComplexWorkflows() {
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

	// Create orchestrator
	orchestrator := NewWorkflowOrchestrator(workflowEngine, timeService, db)

	// Create context
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start services
	timeService.Start(ctx)
	defer timeService.Stop()

	// Register event handlers
	registerWorkflowEventHandlers(workflowEngine)
	registerOrchestrationEventHandlers(orchestrator)

	log.Println("=== Complex Time-Based Workflow Examples ===")

	// Example 1: Individual Deep Work Flow
	exampleDeepWorkFlow(ctx, workflowEngine, timeService)

	// Example 2: Team Collaboration Workflow
	exampleTeamCollaborationWorkflow(ctx, orchestrator, timeService)

	// Example 3: Multi-Phase Project Workflow
	exampleMultiPhaseProjectWorkflow(ctx, orchestrator, timeService)

	// Example 4: Adaptive Learning Workflow
	exampleAdaptiveLearningWorkflow(ctx, workflowEngine, timeService)

	// Example 5: Creative Sprint Workflow
	exampleCreativeSprintWorkflow(ctx, orchestrator, timeService)

	log.Println("=== All Examples Completed ===")
}

// registerWorkflowEventHandlers registers event handlers for workflow events
func registerWorkflowEventHandlers(workflowEngine *WorkflowEngine) {
	// Workflow start handler
	workflowEngine.RegisterEventHandler("workflow_started", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		log.Printf("🚀 Workflow Started: %s for user %s", data["workflow_id"], data["user_id"])
		return nil
	})

	// Phase start handler
	workflowEngine.RegisterEventHandler("phase_started", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		log.Printf("📋 Phase Started: %s (%s) - Duration: %d seconds",
			data["phase_name"], data["phase_type"], data["duration"])

		if instructions, ok := data["instructions"].([]string); ok {
			log.Printf("   Instructions: %v", instructions)
		}
		return nil
	})

	// Phase completion handler
	workflowEngine.RegisterEventHandler("phase_completed", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		log.Printf("✅ Phase Completed: %s - Success: %v", data["phase_id"], data["success"])
		return nil
	})

	// Workflow completion handler
	workflowEngine.RegisterEventHandler("workflow_completed", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		log.Printf("🎉 Workflow Completed: Duration: %.2f seconds, Success Rate: %.2f%%",
			data["total_duration"], data["success_rate"].(float64)*100)
		return nil
	})
}

// registerOrchestrationEventHandlers registers event handlers for orchestration events
func registerOrchestrationEventHandlers(orchestrator *WorkflowOrchestrator) {
	// Workflow completion in orchestration
	orchestrator.RegisterEventHandler("workflow_completed", func(ctx context.Context, orchestration *OrchestrationContext, eventType string, data map[string]interface{}) error {
		log.Printf("🔄 Orchestration Workflow Completed: %s (Sequence: %d)",
			data["workflow_id"], data["sequence"])
		return nil
	})

	// Orchestration completion
	orchestrator.RegisterEventHandler("orchestration_completed", func(ctx context.Context, orchestration *OrchestrationContext, eventType string, data map[string]interface{}) error {
		log.Printf("🏁 Orchestration Completed: %s - Total Workflows: %d, Duration: %.2f seconds",
			orchestration.Name, data["total_workflows"], data["duration"])
		return nil
	})
}

// exampleDeepWorkFlow demonstrates a complex deep work flow
func exampleDeepWorkFlow(ctx context.Context, workflowEngine *WorkflowEngine, timeService *TimeService) {
	log.Println("\n=== Example 1: Deep Work Flow ===")

	// Start deep work flow
	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "deep_work_flow", "user123", map[string]interface{}{
		"project":     "Advanced Time System",
		"priority":    "high",
		"environment": "quiet_office",
	})
	if err != nil {
		log.Printf("Error starting deep work flow: %v", err)
		return
	}

	// Simulate phase completions with different success rates
	phases := []struct {
		phaseID string
		success bool
		metrics map[string]interface{}
	}{
		{"preparation", true, map[string]interface{}{"environment_ready": true, "distractions_cleared": true}},
		{"focus_session_1", true, map[string]interface{}{"focus_score": 0.85, "completion_rate": 0.75}},
		{"short_break_1", true, map[string]interface{}{"energy_restored": true, "mind_cleared": true}},
		{"focus_session_2", true, map[string]interface{}{"focus_score": 0.90, "completion_rate": 0.80}},
		{"long_break", true, map[string]interface{}{"energy_restored": true, "motivation_maintained": true}},
		{"focus_session_3", true, map[string]interface{}{"focus_score": 0.95, "completion_rate": 0.85}},
		{"completion", true, map[string]interface{}{"goals_reviewed": true, "progress_documented": true}},
	}

	// Complete each phase
	for _, phase := range phases {
		time.Sleep(100 * time.Millisecond) // Simulate time passing
		if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, phase.phaseID, phase.success, phase.metrics); err != nil {
			log.Printf("Error completing phase %s: %v", phase.phaseID, err)
		}
	}

	// Get final progress
	progress, err := workflowEngine.GetWorkflowProgress(workflowCtx.SessionID)
	if err != nil {
		log.Printf("Error getting workflow progress: %v", err)
	} else {
		log.Printf("Final Progress: %.2f%% complete, Success Rate: %.2f%%",
			progress["completion_percentage"], progress["success_rate"].(float64)*100)
	}
}

// exampleTeamCollaborationWorkflow demonstrates team collaboration orchestration
func exampleTeamCollaborationWorkflow(ctx context.Context, orchestrator *WorkflowOrchestrator, timeService *TimeService) {
	log.Println("\n=== Example 2: Team Collaboration Workflow ===")

	// Define team members and their workflows
	workflows := []OrchestrationWorkflow{
		{
			WorkflowID:     "deep_work_flow",
			UserID:         "alice",
			StartCondition: "always",
			EndCondition:   "always",
			Priority:       1,
			Metadata: map[string]interface{}{
				"role": "lead_developer",
				"task": "core_architecture",
			},
		},
		{
			WorkflowID:     "learning_flow",
			UserID:         "bob",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       2,
			Metadata: map[string]interface{}{
				"role": "junior_developer",
				"task": "learn_new_technologies",
			},
		},
		{
			WorkflowID:     "creative_flow",
			UserID:         "charlie",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       3,
			Metadata: map[string]interface{}{
				"role": "ui_designer",
				"task": "design_interface",
			},
		},
	}

	participants := []OrchestrationParticipant{
		{UserID: "alice", Role: "lead_developer", Permissions: []string{"read", "write", "admin"}},
		{UserID: "bob", Role: "junior_developer", Permissions: []string{"read", "write"}},
		{UserID: "charlie", Role: "ui_designer", Permissions: []string{"read", "write"}},
	}

	// Create orchestration
	orchestration, err := orchestrator.CreateOrchestration(
		"Team Sprint Planning",
		"Collaborative sprint planning session with sequential dependencies",
		"sequential",
		workflows,
		participants,
	)
	if err != nil {
		log.Printf("Error creating orchestration: %v", err)
		return
	}

	// Start orchestration
	if err := orchestrator.StartOrchestration(ctx, orchestration.OrchestrationID); err != nil {
		log.Printf("Error starting orchestration: %v", err)
		return
	}

	// Get orchestration status
	status, err := orchestrator.GetOrchestrationStatus(orchestration.OrchestrationID)
	if err != nil {
		log.Printf("Error getting orchestration status: %v", err)
	} else {
		log.Printf("Orchestration Status: %s, Progress: %.2f%%",
			status["state"], status["progress_percentage"])
	}
}

// exampleMultiPhaseProjectWorkflow demonstrates a complex multi-phase project
func exampleMultiPhaseProjectWorkflow(ctx context.Context, orchestrator *WorkflowOrchestrator, timeService *TimeService) {
	log.Println("\n=== Example 3: Multi-Phase Project Workflow ===")

	// Define project phases with parallel and sequential execution
	workflows := []OrchestrationWorkflow{
		// Phase 1: Research and Planning (Sequential)
		{
			WorkflowID:     "learning_flow",
			UserID:         "researcher1",
			StartCondition: "always",
			EndCondition:   "always",
			Priority:       1,
			Metadata: map[string]interface{}{
				"phase":             "research",
				"execution_pattern": "sequential",
				"task":              "market_research",
			},
		},
		{
			WorkflowID:     "deep_work_flow",
			UserID:         "planner1",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       2,
			Metadata: map[string]interface{}{
				"phase":             "planning",
				"execution_pattern": "sequential",
				"task":              "project_planning",
			},
		},
		// Phase 2: Development (Parallel)
		{
			WorkflowID:     "deep_work_flow",
			UserID:         "developer1",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       3,
			Metadata: map[string]interface{}{
				"phase":             "development",
				"execution_pattern": "parallel",
				"task":              "backend_development",
			},
		},
		{
			WorkflowID:     "creative_flow",
			UserID:         "developer2",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       3,
			Metadata: map[string]interface{}{
				"phase":             "development",
				"execution_pattern": "parallel",
				"task":              "frontend_development",
			},
		},
		// Phase 3: Testing and Deployment (Sequential)
		{
			WorkflowID:     "deep_work_flow",
			UserID:         "tester1",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       4,
			Metadata: map[string]interface{}{
				"phase":             "testing",
				"execution_pattern": "sequential",
				"task":              "quality_assurance",
			},
		},
	}

	participants := []OrchestrationParticipant{
		{UserID: "researcher1", Role: "researcher", Permissions: []string{"read", "write"}},
		{UserID: "planner1", Role: "project_manager", Permissions: []string{"read", "write", "admin"}},
		{UserID: "developer1", Role: "backend_developer", Permissions: []string{"read", "write"}},
		{UserID: "developer2", Role: "frontend_developer", Permissions: []string{"read", "write"}},
		{UserID: "tester1", Role: "qa_engineer", Permissions: []string{"read", "write"}},
	}

	// Create hybrid orchestration
	orchestration, err := orchestrator.CreateOrchestration(
		"Multi-Phase Project Development",
		"Complex project with research, planning, parallel development, and testing phases",
		"hybrid",
		workflows,
		participants,
	)
	if err != nil {
		log.Printf("Error creating orchestration: %v", err)
		return
	}

	// Start orchestration
	if err := orchestrator.StartOrchestration(ctx, orchestration.OrchestrationID); err != nil {
		log.Printf("Error starting orchestration: %v", err)
		return
	}

	// Get orchestration analytics
	analytics, err := orchestrator.GetOrchestrationAnalytics(time.Now().Add(-24*time.Hour), time.Now())
	if err != nil {
		log.Printf("Error getting orchestration analytics: %v", err)
	} else {
		log.Printf("Orchestration Analytics: %+v", analytics)
	}
}

// exampleAdaptiveLearningWorkflow demonstrates adaptive learning based on performance
func exampleAdaptiveLearningWorkflow(ctx context.Context, workflowEngine *WorkflowEngine, timeService *TimeService) {
	log.Println("\n=== Example 4: Adaptive Learning Workflow ===")

	// Start learning flow
	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "learning_flow", "student123", map[string]interface{}{
		"subject":        "Advanced Go Programming",
		"level":          "intermediate",
		"learning_style": "visual",
	})
	if err != nil {
		log.Printf("Error starting learning flow: %v", err)
		return
	}

	// Simulate adaptive learning phases with performance-based adjustments
	phases := []struct {
		phaseID  string
		success  bool
		metrics  map[string]interface{}
		adaptive bool
	}{
		{"review", true, map[string]interface{}{"previous_material_reviewed": true, "comprehension_score": 0.8}, false},
		{"new_content", true, map[string]interface{}{"comprehension_score": 0.7, "engagement_level": 0.8}, true},
		{"practice", true, map[string]interface{}{"practice_completed": true, "accuracy": 0.85}, true},
		{"reflection", true, map[string]interface{}{"notes_taken": true, "key_points_identified": true}, false},
	}

	// Complete phases with adaptive adjustments
	for i, phase := range phases {
		time.Sleep(50 * time.Millisecond) // Simulate time passing

		// Apply adaptive adjustments based on performance
		if phase.adaptive && i > 0 {
			previousPhase := phases[i-1]
			if previousPhase.metrics["comprehension_score"].(float64) < 0.6 {
				// Adjust current phase for better learning
				phase.metrics["adaptive_adjustment"] = "increased_difficulty"
				phase.metrics["additional_resources"] = true
			} else if previousPhase.metrics["comprehension_score"].(float64) > 0.9 {
				// Accelerate learning
				phase.metrics["adaptive_adjustment"] = "accelerated_pace"
				phase.metrics["advanced_topics"] = true
			}
		}

		if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, phase.phaseID, phase.success, phase.metrics); err != nil {
			log.Printf("Error completing phase %s: %v", phase.phaseID, err)
		}
	}

	// Get learning analytics
	insights, err := timeService.GetTimeInsights("student123", time.Now().Add(-7*24*time.Hour), time.Now())
	if err != nil {
		log.Printf("Error getting learning insights: %v", err)
	} else {
		log.Printf("Learning Insights: %+v", insights)
	}
}

// exampleCreativeSprintWorkflow demonstrates a creative sprint with multiple creative workflows
func exampleCreativeSprintWorkflow(ctx context.Context, orchestrator *WorkflowOrchestrator, timeService *TimeService) {
	log.Println("\n=== Example 5: Creative Sprint Workflow ===")

	// Define creative sprint workflows
	workflows := []OrchestrationWorkflow{
		{
			WorkflowID:     "creative_flow",
			UserID:         "designer1",
			StartCondition: "always",
			EndCondition:   "always",
			Priority:       1,
			Metadata: map[string]interface{}{
				"sprint": "design_sprint_1",
				"focus":  "user_interface_design",
			},
		},
		{
			WorkflowID:     "creative_flow",
			UserID:         "designer2",
			StartCondition: "always",
			EndCondition:   "always",
			Priority:       1,
			Metadata: map[string]interface{}{
				"sprint": "design_sprint_1",
				"focus":  "user_experience_design",
			},
		},
		{
			WorkflowID:     "creative_flow",
			UserID:         "content_creator",
			StartCondition: "if_previous_successful",
			EndCondition:   "always",
			Priority:       2,
			Metadata: map[string]interface{}{
				"sprint": "design_sprint_1",
				"focus":  "content_strategy",
			},
		},
	}

	participants := []OrchestrationParticipant{
		{UserID: "designer1", Role: "ui_designer", Permissions: []string{"read", "write"}},
		{UserID: "designer2", Role: "ux_designer", Permissions: []string{"read", "write"}},
		{UserID: "content_creator", Role: "content_strategist", Permissions: []string{"read", "write"}},
	}

	// Create parallel orchestration for creative sprint
	orchestration, err := orchestrator.CreateOrchestration(
		"Creative Design Sprint",
		"Parallel creative workflows for rapid design iteration",
		"parallel",
		workflows,
		participants,
	)
	if err != nil {
		log.Printf("Error creating orchestration: %v", err)
		return
	}

	// Start orchestration
	if err := orchestrator.StartOrchestration(ctx, orchestration.OrchestrationID); err != nil {
		log.Printf("Error starting orchestration: %v", err)
		return
	}

	// Monitor orchestration progress
	ticker := time.NewTicker(500 * time.Millisecond)
	defer ticker.Stop()

	timeout := time.After(5 * time.Second)
	for {
		select {
		case <-ticker.C:
			status, err := orchestrator.GetOrchestrationStatus(orchestration.OrchestrationID)
			if err != nil {
				log.Printf("Error getting status: %v", err)
				continue
			}

			log.Printf("Creative Sprint Progress: %.2f%% (%d/%d workflows completed)",
				status["progress_percentage"],
				status["completed_workflows"],
				status["total_workflows"])

			if status["state"] == "completed" {
				log.Println("Creative Sprint Completed!")
				return
			}

		case <-timeout:
			log.Println("Creative Sprint monitoring timeout")
			return
		}
	}
}

// ExampleWorkflowIntegration demonstrates integration with external systems
func ExampleWorkflowIntegration() {
	log.Println("\n=== Workflow Integration Example ===")

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

	// Register integration event handlers
	workflowEngine.RegisterEventHandler("workflow_started", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		// Integrate with external calendar system
		log.Printf("📅 Calendar Integration: Blocking time for workflow %s", data["workflow_id"])

		// Integrate with notification system
		log.Printf("🔔 Notification: Workflow started for user %s", data["user_id"])

		// Integrate with analytics system
		log.Printf("📊 Analytics: Tracking workflow start event")

		return nil
	})

	workflowEngine.RegisterEventHandler("phase_completed", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		// Integrate with project management system
		log.Printf("📋 Project Management: Updating task status for phase %s", data["phase_id"])

		// Integrate with time tracking system
		log.Printf("⏱️ Time Tracking: Recording phase completion")

		// Integrate with performance monitoring
		log.Printf("📈 Performance: Phase success rate: %v", data["success"])

		return nil
	})

	// Start a workflow to demonstrate integration
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	timeService.Start(ctx)
	defer timeService.Stop()

	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "deep_work_flow", "integration_user", map[string]interface{}{
		"external_system": "jira",
		"project_id":      "PROJ-123",
		"task_id":         "TASK-456",
	})
	if err != nil {
		log.Printf("Error starting workflow: %v", err)
		return
	}

	// Simulate phase completion
	time.Sleep(100 * time.Millisecond)
	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "preparation", true, map[string]interface{}{
		"environment_ready":          true,
		"external_systems_connected": true,
	}); err != nil {
		log.Printf("Error completing phase: %v", err)
	}

	log.Println("Integration example completed")
}
