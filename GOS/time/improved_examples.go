package time

import (
	"context"
	"log"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/mattn/go-sqlite3"
)

// ExampleImprovedWorkflowStructure demonstrates the improved workflow structure with validation and type safety
func ExampleImprovedWorkflowStructure() {
	log.Println("\n=== Improved Workflow Structure Example ===")

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

	// Example 1: Demonstrate validation
	exampleWorkflowValidation(workflowEngine)

	// Example 2: Demonstrate strongly-typed metadata
	exampleStronglyTypedMetadata(workflowEngine, ctx)

	// Example 3: Demonstrate safe event creation
	exampleSafeEventCreation(workflowEngine, ctx)

	// Example 4: Demonstrate error handling
	exampleErrorHandling(workflowEngine, ctx)

	log.Println("Improved workflow structure example completed")
}

// exampleWorkflowValidation demonstrates workflow validation
func exampleWorkflowValidation(_ *WorkflowEngine) {
	log.Println("\n--- Workflow Validation Example ---")

	// Test valid workflow definition
	validWorkflow := &WorkflowDefinition{
		ID:          "test_workflow",
		Name:        "Test Workflow",
		Description: "A test workflow for validation",
		Category:    "test",
		Phases: []WorkflowPhaseDef{
			{
				PhaseID:     "phase1",
				Name:        "Test Phase",
				Type:        "focus",
				Duration:    300, // 5 minutes
				MinDuration: 180, // 3 minutes
				MaxDuration: 600, // 10 minutes
				SuccessCriteria: map[string]interface{}{
					"completion_rate": 0.8,
				},
			},
		},
		CreatedAt: time.Now().UTC(),
	}

	if err := ValidateWorkflowDefinition(validWorkflow); err != nil {
		log.Printf("❌ Valid workflow failed validation: %v", err)
	} else {
		log.Printf("✅ Valid workflow passed validation")
	}

	// Test invalid workflow definitions
	invalidWorkflows := []struct {
		name     string
		workflow *WorkflowDefinition
	}{
		{
			name: "Empty ID",
			workflow: &WorkflowDefinition{
				ID:   "",
				Name: "Test",
				Phases: []WorkflowPhaseDef{
					{PhaseID: "phase1", Name: "Test", Type: "focus", Duration: 300},
				},
			},
		},
		{
			name: "No phases",
			workflow: &WorkflowDefinition{
				ID:     "test",
				Name:   "Test",
				Phases: []WorkflowPhaseDef{},
			},
		},
		{
			name: "Invalid phase duration",
			workflow: &WorkflowDefinition{
				ID:   "test",
				Name: "Test",
				Phases: []WorkflowPhaseDef{
					{PhaseID: "phase1", Name: "Test", Type: "focus", Duration: -100},
				},
			},
		},
	}

	for _, test := range invalidWorkflows {
		if err := ValidateWorkflowDefinition(test.workflow); err != nil {
			log.Printf("✅ Correctly caught invalid workflow (%s): %v", test.name, err)
		} else {
			log.Printf("❌ Failed to catch invalid workflow: %s", test.name)
		}
	}
}

// exampleStronglyTypedMetadata demonstrates strongly-typed metadata usage
func exampleStronglyTypedMetadata(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Strongly-Typed Metadata Example ---")

	// Create workflow with strongly-typed metadata
	metadata := map[string]interface{}{
		"project":      "Advanced Time System",
		"priority":     "high",
		"environment":  "development",
		"external_id":  "PROJ-123",
		"tags":         []string{"go", "workflow", "time-management"},
		"custom_field": "custom_value",
	}

	workflowCtx, err := workflowEngine.StartWorkflow(ctx, "deep_work_flow", "demo_user", metadata)
	if err != nil {
		log.Printf("Error starting workflow: %v", err)
		return
	}

	log.Printf("✅ Started workflow with strongly-typed metadata")
	log.Printf("   Project: %s", metadata["project"])
	log.Printf("   Priority: %s", metadata["priority"])
	log.Printf("   Environment: %s", metadata["environment"])
	log.Printf("   External ID: %s", metadata["external_id"])
	log.Printf("   Tags: %v", metadata["tags"])
	log.Printf("   Custom Field: %s", metadata["custom_field"])

	// Complete a phase to demonstrate phase metadata
	time.Sleep(100 * time.Millisecond)
	if err := workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "preparation", true, map[string]interface{}{
		"environment_ready":    true,
		"distractions_cleared": true,
		"focus_score":          0.85,
	}); err != nil {
		log.Printf("Error completing phase: %v", err)
	} else {
		log.Printf("✅ Completed phase with strongly-typed metadata")
	}
}

// exampleSafeEventCreation demonstrates safe event creation
func exampleSafeEventCreation(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Safe Event Creation Example ---")

	// Create a workflow context for testing
	workflowCtx := &WorkflowContext{
		UserID:     "test_user",
		WorkflowID: "test_workflow",
		SessionID:  "test_session_123",
		StartTime:  time.Now(),
		State:      WorkflowStateActive,
		CreatedAt:  time.Now().UTC(),
		UpdatedAt:  time.Now().UTC(),
	}

	// Test valid phase definition
	validPhaseDef := &WorkflowPhaseDef{
		PhaseID:     "test_phase",
		Name:        "Test Phase",
		Type:        "focus",
		Duration:    300, // 5 minutes
		MinDuration: 180, // 3 minutes
		MaxDuration: 600, // 10 minutes
		SuccessCriteria: map[string]interface{}{
			"completion_rate": 0.8,
		},
		Metadata: map[string]interface{}{
			"instructions": []string{
				"Clear your workspace",
				"Focus on the task",
				"Take breaks as needed",
			},
		},
	}

	validPhase := &WorkflowPhase{
		PhaseID:        "test_phase",
		Name:           "Test Phase",
		Type:           "focus",
		StartTime:      time.Now(),
		TargetDuration: 300,
		IsCompleted:    false,
		Success:        false,
		Metrics:        make(map[string]interface{}),
		Context:        make(map[string]interface{}),
	}

	// Test safe event creation
	event, err := CreatePhaseCompletionEvent(workflowCtx, validPhaseDef, validPhase)
	if err != nil {
		log.Printf("Error creating phase completion event: %v", err)
	} else if event != nil {
		log.Printf("✅ Successfully created phase completion event")
		log.Printf("   Event ID: %s", event.ID)
		log.Printf("   Title: %s", event.Title)
		log.Printf("   Start Time: %s", event.StartTime.Format(time.RFC3339))
		log.Printf("   End Time: %s", event.EndTime.Format(time.RFC3339))
		log.Printf("   Duration: %.0f seconds", event.EndTime.Sub(event.StartTime).Seconds())
	} else {
		log.Printf("❌ Failed to create phase completion event")
	}

	// Test invalid inputs
	log.Println("\nTesting invalid inputs:")

	// Test with nil workflow context
	nilEvent, _ := CreatePhaseCompletionEvent(nil, validPhaseDef, validPhase)
	if nilEvent == nil {
		log.Printf("✅ Correctly handled nil workflow context")
	} else {
		log.Printf("❌ Failed to handle nil workflow context")
	}

	// Test with invalid duration
	invalidPhaseDef := *validPhaseDef
	invalidPhaseDef.Duration = -100
	invalidEvent, _ := CreatePhaseCompletionEvent(workflowCtx, &invalidPhaseDef, validPhase)
	if invalidEvent == nil {
		log.Printf("✅ Correctly handled invalid duration")
	} else {
		log.Printf("❌ Failed to handle invalid duration")
	}
}

// exampleErrorHandling demonstrates comprehensive error handling
func exampleErrorHandling(workflowEngine *WorkflowEngine, ctx context.Context) {
	log.Println("\n--- Error Handling Example ---")

	// Test starting workflow with invalid inputs
	testCases := []struct {
		name        string
		workflowID  string
		userID      string
		metadata    map[string]interface{}
		expectError bool
	}{
		{
			name:        "Valid inputs",
			workflowID:  "deep_work_flow",
			userID:      "valid_user",
			metadata:    map[string]interface{}{"project": "test"},
			expectError: false,
		},
		{
			name:        "Empty workflow ID",
			workflowID:  "",
			userID:      "valid_user",
			metadata:    map[string]interface{}{},
			expectError: true,
		},
		{
			name:        "Empty user ID",
			workflowID:  "deep_work_flow",
			userID:      "",
			metadata:    map[string]interface{}{},
			expectError: true,
		},
		{
			name:        "Non-existent workflow",
			workflowID:  "non_existent_workflow",
			userID:      "valid_user",
			metadata:    map[string]interface{}{},
			expectError: true,
		},
	}

	for _, testCase := range testCases {
		_, err := workflowEngine.StartWorkflow(ctx, testCase.workflowID, testCase.userID, testCase.metadata)

		if testCase.expectError {
			if err != nil {
				log.Printf("✅ Correctly caught error for %s: %v", testCase.name, err)
			} else {
				log.Printf("❌ Expected error but got none for %s", testCase.name)
			}
		} else {
			if err != nil {
				log.Printf("❌ Unexpected error for %s: %v", testCase.name, err)
			} else {
				log.Printf("✅ Successfully started workflow for %s", testCase.name)
			}
		}
	}

	// Test phase completion with invalid session ID
	invalidSessionID := "non_existent_session"
	err := workflowEngine.CompletePhase(ctx, invalidSessionID, "preparation", true, map[string]interface{}{})
	if err != nil {
		log.Printf("✅ Correctly caught error for invalid session ID: %v", err)
	} else {
		log.Printf("❌ Expected error for invalid session ID but got none")
	}
}

// ExampleWorkflowBuilder demonstrates a builder pattern for creating workflows
func ExampleWorkflowBuilder() {
	log.Println("\n=== Workflow Builder Example ===")

	// Create a workflow using a builder-like approach
	workflow := &WorkflowDefinition{
		ID:          "custom_workflow",
		Name:        "Custom Workflow",
		Description: "A custom workflow built with validation",
		Category:    "custom",
		Phases: []WorkflowPhaseDef{
			{
				PhaseID:     "setup",
				Name:        "Setup Phase",
				Type:        "transition",
				Duration:    120, // 2 minutes
				MinDuration: 60,  // 1 minute
				MaxDuration: 300, // 5 minutes
				SuccessCriteria: map[string]interface{}{
					"environment_ready": true,
				},
				Metadata: map[string]interface{}{
					"instructions": []string{
						"Prepare your workspace",
						"Gather necessary materials",
						"Set up your environment",
					},
				},
			},
			{
				PhaseID:     "work",
				Name:        "Work Phase",
				Type:        "focus",
				Duration:    1800, // 30 minutes
				MinDuration: 900,  // 15 minutes
				MaxDuration: 3600, // 60 minutes
				SuccessCriteria: map[string]interface{}{
					"completion_rate": 0.7,
					"quality_score":   0.8,
				},
				Metadata: map[string]interface{}{
					"instructions": []string{
						"Focus on the main task",
						"Maintain high quality",
						"Take notes as needed",
					},
				},
			},
			{
				PhaseID:     "review",
				Name:        "Review Phase",
				Type:        "milestone",
				Duration:    300, // 5 minutes
				MinDuration: 180, // 3 minutes
				MaxDuration: 600, // 10 minutes
				SuccessCriteria: map[string]interface{}{
					"review_completed":        true,
					"improvements_identified": true,
				},
				Metadata: map[string]interface{}{
					"instructions": []string{
						"Review your work",
						"Identify improvements",
						"Plan next steps",
					},
				},
			},
		},
		CreatedAt: time.Now().UTC(),
	}

	// Validate the custom workflow
	if err := ValidateWorkflowDefinition(workflow); err != nil {
		log.Printf("❌ Custom workflow validation failed: %v", err)
		return
	}

	log.Printf("✅ Custom workflow validation passed")
	log.Printf("   Workflow ID: %s", workflow.ID)
	log.Printf("   Name: %s", workflow.Name)
	log.Printf("   Phases: %d", len(workflow.Phases))

	for i, phase := range workflow.Phases {
		log.Printf("   Phase %d: %s (%s) - %d seconds",
			i+1, phase.Name, phase.Type, phase.Duration)
	}

	// Demonstrate phase validation
	for i, phase := range workflow.Phases {
		if err := ValidateWorkflowPhaseDef(&phase); err != nil {
			log.Printf("❌ Phase %d validation failed: %v", i+1, err)
		} else {
			log.Printf("✅ Phase %d validation passed", i+1)
		}
	}
}
