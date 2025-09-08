package time

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"sync"
	stdtime "time"

	"github.com/jmoiron/sqlx"
)

// WorkflowContext represents the context for a time-based workflow
type WorkflowContext struct {
	UserID       string                 `json:"user_id"`
	WorkflowID   string                 `json:"workflow_id"`
	SessionID    string                 `json:"session_id"`
	StartTime    stdtime.Time           `json:"start_time"`
	EndTime      *stdtime.Time          `json:"end_time,omitempty"`
	CurrentPhase string                 `json:"current_phase"`
	PhaseHistory []WorkflowPhase        `json:"phase_history"`
	Metadata     map[string]interface{} `json:"metadata"`
	State        WorkflowState          `json:"state"`
	CreatedAt    stdtime.Time           `json:"created_at"`
	UpdatedAt    stdtime.Time           `json:"updated_at"`
}

// WorkflowPhase represents a phase in a workflow
type WorkflowPhase struct {
	PhaseID        string                 `json:"phase_id"`
	Name           string                 `json:"name"`
	Type           string                 `json:"type"` // focus, break, transition, milestone
	StartTime      stdtime.Time           `json:"start_time"`
	EndTime        *stdtime.Time          `json:"end_time,omitempty"`
	Duration       int                    `json:"duration"`        // seconds
	TargetDuration int                    `json:"target_duration"` // seconds
	IsCompleted    bool                   `json:"is_completed"`
	Success        bool                   `json:"success"`
	Metrics        map[string]interface{} `json:"metrics"`
	Context        map[string]interface{} `json:"context"`
}

// WorkflowState represents the current state of a workflow
type WorkflowState string

const (
	WorkflowStatePending   WorkflowState = "pending"
	WorkflowStateActive    WorkflowState = "active"
	WorkflowStatePaused    WorkflowState = "paused"
	WorkflowStateCompleted WorkflowState = "completed"
	WorkflowStateFailed    WorkflowState = "failed"
	WorkflowStateCancelled WorkflowState = "cancelled"
)

// WorkflowDefinition defines a complete workflow
type WorkflowDefinition struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Category    string                 `json:"category"`
	Phases      []WorkflowPhaseDef     `json:"phases"`
	Conditions  []WorkflowCondition    `json:"conditions"`
	Triggers    []WorkflowTrigger      `json:"triggers"`
	Metadata    map[string]interface{} `json:"metadata"`
	CreatedAt   stdtime.Time           `json:"created_at"`
}

// WorkflowPhaseDef defines a phase in a workflow
type WorkflowPhaseDef struct {
	PhaseID         string                 `json:"phase_id"`
	Name            string                 `json:"name"`
	Type            string                 `json:"type"`
	Duration        int                    `json:"duration"`     // seconds
	MinDuration     int                    `json:"min_duration"` // minimum seconds
	MaxDuration     int                    `json:"max_duration"` // maximum seconds
	Conditions      []WorkflowCondition    `json:"conditions"`
	Transitions     []WorkflowTransition   `json:"transitions"`
	SuccessCriteria map[string]interface{} `json:"success_criteria"`
	FailureCriteria map[string]interface{} `json:"failure_criteria"`
	Metadata        map[string]interface{} `json:"metadata"`
}

// WorkflowCondition represents a condition for workflow execution
type WorkflowCondition struct {
	ID         string                 `json:"id"`
	Type       string                 `json:"type"` // time, energy, focus, external
	Expression string                 `json:"expression"`
	Parameters map[string]interface{} `json:"parameters"`
	IsRequired bool                   `json:"is_required"`
}

// WorkflowTrigger represents a trigger for workflow execution
type WorkflowTrigger struct {
	ID         string                 `json:"id"`
	Type       string                 `json:"type"` // schedule, event, manual, condition
	Expression string                 `json:"expression"`
	Parameters map[string]interface{} `json:"parameters"`
	IsActive   bool                   `json:"is_active"`
}

// WorkflowTransition represents a transition between phases
type WorkflowTransition struct {
	FromPhase   string                 `json:"from_phase"`
	ToPhase     string                 `json:"to_phase"`
	Condition   string                 `json:"condition"`
	Parameters  map[string]interface{} `json:"parameters"`
	Probability float64                `json:"probability"` // 0.0 to 1.0
}

// WorkflowEngine manages complex time-based workflows
type WorkflowEngine struct {
	timeService     *TimeService
	db              *sqlx.DB
	workflows       map[string]*WorkflowDefinition
	activeWorkflows map[string]*WorkflowContext
	workflowsMutex  sync.RWMutex
	activeMutex     sync.RWMutex
	eventHandlers   map[string][]WorkflowEventHandler
	handlersMutex   sync.RWMutex
	stopChan        chan struct{}
	isRunning       bool
	runningMutex    sync.RWMutex
}

// WorkflowEventHandler handles workflow events
type WorkflowEventHandler func(context.Context, *WorkflowContext, string, map[string]interface{}) error

// NewWorkflowEngine creates a new workflow engine
func NewWorkflowEngine(timeService *TimeService, db *sqlx.DB) *WorkflowEngine {
	engine := &WorkflowEngine{
		timeService:     timeService,
		db:              db,
		workflows:       make(map[string]*WorkflowDefinition),
		activeWorkflows: make(map[string]*WorkflowContext),
		eventHandlers:   make(map[string][]WorkflowEventHandler),
		stopChan:        make(chan struct{}),
	}

	// Initialize default workflows
	engine.initializeDefaultWorkflows()

	return engine
}

// ValidateWorkflowDefinition validates a workflow definition
func ValidateWorkflowDefinition(definition *WorkflowDefinition) error {
	if definition == nil {
		return errors.New("workflow definition cannot be nil")
	}
	if definition.ID == "" {
		return errors.New("workflow ID cannot be empty")
	}
	if definition.Name == "" {
		return errors.New("workflow name cannot be empty")
	}
	if len(definition.Phases) == 0 {
		return errors.New("workflow must have at least one phase")
	}

	// Validate each phase
	for i, phase := range definition.Phases {
		if err := ValidateWorkflowPhaseDef(&phase); err != nil {
			return fmt.Errorf("phase %d (%s): %w", i, phase.PhaseID, err)
		}
	}

	return nil
}

// ValidateWorkflowPhaseDef validates a workflow phase definition
func ValidateWorkflowPhaseDef(phaseDef *WorkflowPhaseDef) error {
	if phaseDef == nil {
		return errors.New("phase definition cannot be nil")
	}
	if phaseDef.PhaseID == "" {
		return errors.New("phase ID cannot be empty")
	}
	if phaseDef.Name == "" {
		return errors.New("phase name cannot be empty")
	}
	if phaseDef.Duration <= 0 {
		return errors.New("phase duration must be positive")
	}
	if phaseDef.MinDuration < 0 {
		return errors.New("phase minimum duration cannot be negative")
	}
	if phaseDef.MaxDuration > 0 && phaseDef.MaxDuration < phaseDef.MinDuration {
		return errors.New("phase maximum duration must be greater than minimum duration")
	}
	if phaseDef.MaxDuration > 0 && phaseDef.Duration > phaseDef.MaxDuration {
		return errors.New("phase duration cannot exceed maximum duration")
	}
	if phaseDef.Duration < phaseDef.MinDuration {
		return errors.New("phase duration cannot be less than minimum duration")
	}

	return nil
}

// initializeDefaultWorkflows sets up default workflow definitions
func (we *WorkflowEngine) initializeDefaultWorkflows() {
	// Deep Work Flow
	deepWorkFlow := &WorkflowDefinition{
		ID:          "deep_work_flow",
		Name:        "Deep Work Flow",
		Description: "A comprehensive deep work session with breaks and transitions",
		Category:    "productivity",
		Phases: []WorkflowPhaseDef{
			{
				PhaseID:     "preparation",
				Name:        "Preparation Phase",
				Type:        "transition",
				Duration:    300, // 5 minutes
				MinDuration: 180, // 3 minutes
				MaxDuration: 600, // 10 minutes
				SuccessCriteria: map[string]interface{}{
					"environment_ready":    true,
					"distractions_cleared": true,
				},
				Metadata: map[string]interface{}{
					"instructions": []string{
						"Clear your workspace",
						"Close unnecessary applications",
						"Set phone to do not disturb",
						"Review your goals for this session",
					},
				},
			},
			{
				PhaseID:     "focus_session_1",
				Name:        "First Focus Session",
				Type:        "focus",
				Duration:    1500, // 25 minutes
				MinDuration: 1200, // 20 minutes
				MaxDuration: 1800, // 30 minutes
				SuccessCriteria: map[string]interface{}{
					"focus_score":     0.8,
					"completion_rate": 0.7,
				},
				Metadata: map[string]interface{}{
					"technique": "pomodoro",
					"intensity": "high",
				},
			},
			{
				PhaseID:     "short_break_1",
				Name:        "Short Break",
				Type:        "break",
				Duration:    300, // 5 minutes
				MinDuration: 180, // 3 minutes
				MaxDuration: 600, // 10 minutes
				SuccessCriteria: map[string]interface{}{
					"energy_restored": true,
					"mind_cleared":    true,
				},
				Metadata: map[string]interface{}{
					"activities": []string{
						"Stand up and stretch",
						"Look away from screen",
						"Take deep breaths",
						"Drink water",
					},
				},
			},
			{
				PhaseID:     "focus_session_2",
				Name:        "Second Focus Session",
				Type:        "focus",
				Duration:    1500, // 25 minutes
				MinDuration: 1200, // 20 minutes
				MaxDuration: 1800, // 30 minutes
				SuccessCriteria: map[string]interface{}{
					"focus_score":     0.8,
					"completion_rate": 0.7,
				},
				Metadata: map[string]interface{}{
					"technique": "pomodoro",
					"intensity": "high",
				},
			},
			{
				PhaseID:     "long_break",
				Name:        "Long Break",
				Type:        "break",
				Duration:    900,  // 15 minutes
				MinDuration: 600,  // 10 minutes
				MaxDuration: 1200, // 20 minutes
				SuccessCriteria: map[string]interface{}{
					"energy_restored":       true,
					"motivation_maintained": true,
				},
				Metadata: map[string]interface{}{
					"activities": []string{
						"Take a walk",
						"Have a snack",
						"Check messages",
						"Plan next session",
					},
				},
			},
			{
				PhaseID:     "focus_session_3",
				Name:        "Final Focus Session",
				Type:        "focus",
				Duration:    1800, // 30 minutes
				MinDuration: 1500, // 25 minutes
				MaxDuration: 2400, // 40 minutes
				SuccessCriteria: map[string]interface{}{
					"focus_score":     0.8,
					"completion_rate": 0.8,
				},
				Metadata: map[string]interface{}{
					"technique": "deep_work",
					"intensity": "maximum",
				},
			},
			{
				PhaseID:     "completion",
				Name:        "Completion Phase",
				Type:        "milestone",
				Duration:    300, // 5 minutes
				MinDuration: 180, // 3 minutes
				MaxDuration: 600, // 10 minutes
				SuccessCriteria: map[string]interface{}{
					"goals_reviewed":      true,
					"progress_documented": true,
				},
				Metadata: map[string]interface{}{
					"activities": []string{
						"Review what was accomplished",
						"Document progress",
						"Plan next steps",
						"Celebrate achievements",
					},
				},
			},
		},
		Triggers: []WorkflowTrigger{
			{
				ID:       "manual_trigger",
				Type:     "manual",
				IsActive: true,
			},
			{
				ID:         "schedule_trigger",
				Type:       "schedule",
				Expression: "0 9 * * 1-5", // 9 AM, Monday to Friday
				IsActive:   true,
			},
		},
		CreatedAt: stdtime.Now().UTC(),
	}

	// Learning Flow
	learningFlow := &WorkflowDefinition{
		ID:          "learning_flow",
		Name:        "Learning Flow",
		Description: "Structured learning session with spaced repetition",
		Category:    "education",
		Phases: []WorkflowPhaseDef{
			{
				PhaseID:  "review",
				Name:     "Review Previous Material",
				Type:     "transition",
				Duration: 600, // 10 minutes
				SuccessCriteria: map[string]interface{}{
					"previous_material_reviewed": true,
				},
			},
			{
				PhaseID:  "new_content",
				Name:     "Learn New Content",
				Type:     "focus",
				Duration: 1800, // 30 minutes
				SuccessCriteria: map[string]interface{}{
					"comprehension_score": 0.7,
				},
			},
			{
				PhaseID:  "practice",
				Name:     "Practice and Apply",
				Type:     "focus",
				Duration: 1200, // 20 minutes
				SuccessCriteria: map[string]interface{}{
					"practice_completed": true,
				},
			},
			{
				PhaseID:  "reflection",
				Name:     "Reflection and Notes",
				Type:     "milestone",
				Duration: 300, // 5 minutes
				SuccessCriteria: map[string]interface{}{
					"notes_taken":           true,
					"key_points_identified": true,
				},
			},
		},
		CreatedAt: stdtime.Now().UTC(),
	}

	// Creative Flow
	creativeFlow := &WorkflowDefinition{
		ID:          "creative_flow",
		Name:        "Creative Flow",
		Description: "Creative work session with inspiration and execution phases",
		Category:    "creative",
		Phases: []WorkflowPhaseDef{
			{
				PhaseID:  "inspiration",
				Name:     "Inspiration Phase",
				Type:     "transition",
				Duration: 900, // 15 minutes
				SuccessCriteria: map[string]interface{}{
					"inspiration_gathered": true,
				},
			},
			{
				PhaseID:  "ideation",
				Name:     "Ideation Phase",
				Type:     "focus",
				Duration: 1200, // 20 minutes
				SuccessCriteria: map[string]interface{}{
					"ideas_generated": 5,
				},
			},
			{
				PhaseID:  "execution",
				Name:     "Execution Phase",
				Type:     "focus",
				Duration: 2400, // 40 minutes
				SuccessCriteria: map[string]interface{}{
					"work_progress": 0.6,
				},
			},
			{
				PhaseID:  "refinement",
				Name:     "Refinement Phase",
				Type:     "focus",
				Duration: 1800, // 30 minutes
				SuccessCriteria: map[string]interface{}{
					"quality_score": 0.8,
				},
			},
		},
		CreatedAt: stdtime.Now().UTC(),
	}

	// Validate and register workflows
	workflows := map[string]*WorkflowDefinition{
		"deep_work_flow": deepWorkFlow,
		"learning_flow":  learningFlow,
		"creative_flow":  creativeFlow,
	}

	we.workflowsMutex.Lock()
	for id, workflow := range workflows {
		if err := ValidateWorkflowDefinition(workflow); err != nil {
			log.Printf("Warning: Invalid workflow definition for %s: %v", id, err)
			continue
		}
		we.workflows[id] = workflow
		log.Printf("Registered validated workflow: %s", id)
	}
	we.workflowsMutex.Unlock()
}

// StartWorkflow starts a new workflow instance
func (we *WorkflowEngine) StartWorkflow(ctx context.Context, workflowID, userID string, metadata map[string]interface{}) (*WorkflowContext, error) {
	// Validate inputs
	if workflowID == "" {
		return nil, errors.New("workflow ID cannot be empty")
	}
	if userID == "" {
		return nil, errors.New("user ID cannot be empty")
	}

	we.workflowsMutex.RLock()
	definition, exists := we.workflows[workflowID]
	we.workflowsMutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("workflow %s not found", workflowID)
	}

	// Validate workflow definition
	if err := ValidateWorkflowDefinition(definition); err != nil {
		return nil, fmt.Errorf("invalid workflow definition: %w", err)
	}

	// Create workflow context
	workflowCtx := &WorkflowContext{
		UserID:       userID,
		WorkflowID:   workflowID,
		SessionID:    fmt.Sprintf("%s_%s_%d", workflowID, userID, stdtime.Now().Unix()),
		StartTime:    we.timeService.GetCurrentTime(),
		CurrentPhase: definition.Phases[0].PhaseID,
		PhaseHistory: make([]WorkflowPhase, 0),
		Metadata:     metadata,
		State:        WorkflowStateActive,
		CreatedAt:    stdtime.Now().UTC(),
		UpdatedAt:    stdtime.Now().UTC(),
	}

	// Add to active workflows
	we.activeMutex.Lock()
	we.activeWorkflows[workflowCtx.SessionID] = workflowCtx
	we.activeMutex.Unlock()

	// Create workflow start event using the new builder
	startEvent, err := CreateWorkflowStartEvent(workflowCtx, metadata)
	if err != nil {
		log.Printf("Error creating workflow start event: %v", err)
	} else {
		if err := we.timeService.AddTimeEvent(startEvent); err != nil {
			log.Printf("Error adding workflow start event: %v", err)
		}
	}

	// Start the first phase
	if err := we.startPhase(ctx, workflowCtx, definition.Phases[0]); err != nil {
		return nil, err
	}

	// Trigger workflow start event
	we.triggerEvent(ctx, workflowCtx, "workflow_started", map[string]interface{}{
		"workflow_id": workflowID,
		"user_id":     userID,
		"metadata":    metadata,
	})

	log.Printf("Started workflow %s for user %s", workflowID, userID)
	return workflowCtx, nil
}

// startPhase starts a specific phase of a workflow
func (we *WorkflowEngine) startPhase(ctx context.Context, workflowCtx *WorkflowContext, phaseDef WorkflowPhaseDef) error {
	// Create phase context
	phase := WorkflowPhase{
		PhaseID:        phaseDef.PhaseID,
		Name:           phaseDef.Name,
		Type:           phaseDef.Type,
		StartTime:      we.timeService.GetCurrentTime(),
		TargetDuration: phaseDef.Duration,
		IsCompleted:    false,
		Success:        false,
		Metrics:        make(map[string]interface{}),
		Context:        make(map[string]interface{}),
	}

	// Add phase to history
	workflowCtx.PhaseHistory = append(workflowCtx.PhaseHistory, phase)
	workflowCtx.CurrentPhase = phaseDef.PhaseID
	workflowCtx.UpdatedAt = stdtime.Now().UTC()

	// Create time block for this phase
	timeBlock := &TimeBlock{
		ID:          fmt.Sprintf("workflow_%s_%s", workflowCtx.SessionID, phaseDef.PhaseID),
		UserID:      workflowCtx.UserID,
		Title:       fmt.Sprintf("%s - %s", workflowCtx.WorkflowID, phaseDef.Name),
		Description: phaseDef.Metadata["description"].(string),
		StartTime:   phase.StartTime,
		EndTime:     phase.StartTime.Add(stdtime.Duration(phaseDef.Duration) * stdtime.Second),
		Category:    phaseDef.Type,
		Priority:    we.getPhasePriority(phaseDef.Type),
		IsCompleted: false,
	}

	if err := we.timeService.CreateTimeBlock(timeBlock); err != nil {
		log.Printf("Error creating time block for phase: %v", err)
	}

	// Create time event for phase completion using the new builder
	phaseEvent, err := CreatePhaseCompletionEvent(workflowCtx, &phaseDef, &phase)
	if err != nil {
		log.Printf("Error creating phase completion event: %v", err)
	} else {
		if err := we.timeService.AddTimeEvent(phaseEvent); err != nil {
			log.Printf("Error adding phase completion event: %v", err)
		}
	}

	// Trigger phase start event
	we.triggerEvent(ctx, workflowCtx, "phase_started", map[string]interface{}{
		"phase_id":     phaseDef.PhaseID,
		"phase_name":   phaseDef.Name,
		"phase_type":   phaseDef.Type,
		"duration":     phaseDef.Duration,
		"instructions": phaseDef.Metadata["instructions"],
	})

	return nil
}

// getPhasePriority returns priority based on phase type
func (we *WorkflowEngine) getPhasePriority(phaseType string) int {
	switch phaseType {
	case "focus":
		return 5
	case "milestone":
		return 4
	case "transition":
		return 3
	case "break":
		return 2
	default:
		return 3
	}
}

// CompletePhase completes a phase and transitions to the next one
func (we *WorkflowEngine) CompletePhase(ctx context.Context, sessionID, phaseID string, success bool, metrics map[string]interface{}) error {
	we.activeMutex.Lock()
	workflowCtx, exists := we.activeWorkflows[sessionID]
	we.activeMutex.Unlock()

	if !exists {
		return fmt.Errorf("workflow session %s not found", sessionID)
	}

	// Find and update the phase
	for i, phase := range workflowCtx.PhaseHistory {
		if phase.PhaseID == phaseID {
			endTime := we.timeService.GetCurrentTime()
			phase.EndTime = &endTime
			phase.Duration = int(phase.EndTime.Sub(phase.StartTime).Seconds())
			phase.IsCompleted = true
			phase.Success = success
			phase.Metrics = metrics
			workflowCtx.PhaseHistory[i] = phase
			break
		}
	}

	// Get workflow definition
	we.workflowsMutex.RLock()
	definition := we.workflows[workflowCtx.WorkflowID]
	we.workflowsMutex.RUnlock()

	// Find next phase
	nextPhase := we.findNextPhase(definition, phaseID, success)
	if nextPhase == nil {
		// Workflow completed
		workflowCtx.State = WorkflowStateCompleted
		endTime := we.timeService.GetCurrentTime()
		workflowCtx.EndTime = &endTime
		workflowCtx.CurrentPhase = ""

		// Create workflow end event with metrics
		metrics := &WorkflowMetrics{
			Duration:    endTime.Sub(workflowCtx.StartTime),
			StepCount:   len(workflowCtx.PhaseHistory),
			SuccessRate: we.calculateSuccessRate(workflowCtx),
		}

		endEvent, err := CreateWorkflowEndEvent(workflowCtx, "completed", metrics)
		if err != nil {
			log.Printf("Error creating workflow end event: %v", err)
		} else {
			if err := we.timeService.AddTimeEvent(endEvent); err != nil {
				log.Printf("Error adding workflow end event: %v", err)
			}
		}

		// Remove from active workflows
		we.activeMutex.Lock()
		delete(we.activeWorkflows, sessionID)
		we.activeMutex.Unlock()

		// Trigger workflow completion event
		we.triggerEvent(ctx, workflowCtx, "workflow_completed", map[string]interface{}{
			"total_duration":   workflowCtx.EndTime.Sub(workflowCtx.StartTime).Seconds(),
			"phases_completed": len(workflowCtx.PhaseHistory),
			"success_rate":     we.calculateSuccessRate(workflowCtx),
		})

		log.Printf("Workflow %s completed for user %s", workflowCtx.WorkflowID, workflowCtx.UserID)
		return nil
	}

	// Start next phase
	if err := we.startPhase(ctx, workflowCtx, *nextPhase); err != nil {
		return err
	}

	// Trigger phase completion event
	we.triggerEvent(ctx, workflowCtx, "phase_completed", map[string]interface{}{
		"phase_id":   phaseID,
		"success":    success,
		"metrics":    metrics,
		"next_phase": nextPhase.PhaseID,
	})

	return nil
}

// findNextPhase finds the next phase based on current phase and success
func (we *WorkflowEngine) findNextPhase(definition *WorkflowDefinition, currentPhaseID string, success bool) *WorkflowPhaseDef {
	for i, phase := range definition.Phases {
		if phase.PhaseID == currentPhaseID {
			// Return next phase if it exists
			if i+1 < len(definition.Phases) {
				return &definition.Phases[i+1]
			}
			break
		}
	}
	return nil
}

// calculateSuccessRate calculates the success rate of completed phases
func (we *WorkflowEngine) calculateSuccessRate(workflowCtx *WorkflowContext) float64 {
	if len(workflowCtx.PhaseHistory) == 0 {
		return 0.0
	}

	successCount := 0
	for _, phase := range workflowCtx.PhaseHistory {
		if phase.IsCompleted && phase.Success {
			successCount++
		}
	}

	return float64(successCount) / float64(len(workflowCtx.PhaseHistory))
}

// RegisterEventHandler registers an event handler for workflow events
func (we *WorkflowEngine) RegisterEventHandler(eventType string, handler WorkflowEventHandler) {
	we.handlersMutex.Lock()
	defer we.handlersMutex.Unlock()

	we.eventHandlers[eventType] = append(we.eventHandlers[eventType], handler)
}

// triggerEvent triggers a workflow event
func (we *WorkflowEngine) triggerEvent(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) {
	we.handlersMutex.RLock()
	handlers := we.eventHandlers[eventType]
	we.handlersMutex.RUnlock()

	for _, handler := range handlers {
		if err := handler(ctx, workflowCtx, eventType, data); err != nil {
			log.Printf("Error in workflow event handler: %v", err)
		}
	}
}

// GetActiveWorkflows returns all active workflows for a user
func (we *WorkflowEngine) GetActiveWorkflows(userID string) []*WorkflowContext {
	we.activeMutex.RLock()
	defer we.activeMutex.RUnlock()

	var userWorkflows []*WorkflowContext
	for _, workflow := range we.activeWorkflows {
		if workflow.UserID == userID {
			userWorkflows = append(userWorkflows, workflow)
		}
	}

	return userWorkflows
}

// GetWorkflowProgress returns the progress of a workflow
func (we *WorkflowEngine) GetWorkflowProgress(sessionID string) (map[string]interface{}, error) {
	we.activeMutex.RLock()
	workflowCtx, exists := we.activeWorkflows[sessionID]
	we.activeMutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("workflow session %s not found", sessionID)
	}

	progress := map[string]interface{}{
		"session_id":       sessionID,
		"workflow_id":      workflowCtx.WorkflowID,
		"user_id":          workflowCtx.UserID,
		"current_phase":    workflowCtx.CurrentPhase,
		"state":            workflowCtx.State,
		"start_time":       workflowCtx.StartTime,
		"phases_completed": len(workflowCtx.PhaseHistory),
		"success_rate":     we.calculateSuccessRate(workflowCtx),
		"total_duration":   we.timeService.GetCurrentTime().Sub(workflowCtx.StartTime).Seconds(),
	}

	// Get workflow definition for total phases
	we.workflowsMutex.RLock()
	definition := we.workflows[workflowCtx.WorkflowID]
	we.workflowsMutex.RUnlock()

	progress["total_phases"] = len(definition.Phases)
	progress["completion_percentage"] = float64(len(workflowCtx.PhaseHistory)) / float64(len(definition.Phases)) * 100

	return progress, nil
}

// PauseWorkflow pauses an active workflow
func (we *WorkflowEngine) PauseWorkflow(sessionID string) error {
	we.activeMutex.Lock()
	defer we.activeMutex.Unlock()

	workflowCtx, exists := we.activeWorkflows[sessionID]
	if !exists {
		return fmt.Errorf("workflow session %s not found", sessionID)
	}

	workflowCtx.State = WorkflowStatePaused
	workflowCtx.UpdatedAt = stdtime.Now().UTC()

	// Create pause event
	pauseEvent, err := CreateWorkflowPauseEvent(workflowCtx, "user_requested")
	if err != nil {
		log.Printf("Error creating pause event: %v", err)
	} else {
		if err := we.timeService.AddTimeEvent(pauseEvent); err != nil {
			log.Printf("Error adding pause event: %v", err)
		}
	}

	log.Printf("Workflow %s paused", sessionID)
	return nil
}

// ResumeWorkflow resumes a paused workflow
func (we *WorkflowEngine) ResumeWorkflow(ctx context.Context, sessionID string) error {
	we.activeMutex.Lock()
	defer we.activeMutex.Unlock()

	workflowCtx, exists := we.activeWorkflows[sessionID]
	if !exists {
		return fmt.Errorf("workflow session %s not found", sessionID)
	}

	workflowCtx.State = WorkflowStateActive
	workflowCtx.UpdatedAt = stdtime.Now().UTC()

	// Create resume event
	resumeEvent, err := CreateWorkflowResumeEvent(workflowCtx)
	if err != nil {
		log.Printf("Error creating resume event: %v", err)
	} else {
		if err := we.timeService.AddTimeEvent(resumeEvent); err != nil {
			log.Printf("Error adding resume event: %v", err)
		}
	}

	// Trigger resume event
	we.triggerEvent(ctx, workflowCtx, "workflow_resumed", map[string]interface{}{
		"session_id": sessionID,
	})

	log.Printf("Workflow %s resumed", sessionID)
	return nil
}

// CancelWorkflow cancels an active workflow
func (we *WorkflowEngine) CancelWorkflow(ctx context.Context, sessionID string, reason string) error {
	we.activeMutex.Lock()
	defer we.activeMutex.Unlock()

	workflowCtx, exists := we.activeWorkflows[sessionID]
	if !exists {
		return fmt.Errorf("workflow session %s not found", sessionID)
	}

	workflowCtx.State = WorkflowStateCancelled
	endTime := we.timeService.GetCurrentTime()
	workflowCtx.EndTime = &endTime
	workflowCtx.UpdatedAt = stdtime.Now().UTC()

	// Remove from active workflows
	delete(we.activeWorkflows, sessionID)

	// Trigger cancellation event
	we.triggerEvent(ctx, workflowCtx, "workflow_cancelled", map[string]interface{}{
		"session_id": sessionID,
		"reason":     reason,
		"duration":   workflowCtx.EndTime.Sub(workflowCtx.StartTime).Seconds(),
	})

	log.Printf("Workflow %s cancelled: %s", sessionID, reason)
	return nil
}

// GetWorkflowAnalytics returns analytics for completed workflows
func (we *WorkflowEngine) GetWorkflowAnalytics(userID string, startDate, endDate stdtime.Time) (map[string]interface{}, error) {
	// This would typically query a database for completed workflows
	// For now, we'll return a placeholder structure
	analytics := map[string]interface{}{
		"user_id":             userID,
		"period":              fmt.Sprintf("%s to %s", startDate.Format("2006-01-02"), endDate.Format("2006-01-02")),
		"total_workflows":     0,
		"completed_workflows": 0,
		"success_rate":        0.0,
		"average_duration":    0.0,
		"most_used_workflow":  "",
		"productivity_trend":  0.0,
	}

	return analytics, nil
}

// ExportWorkflowData exports workflow data
func (we *WorkflowEngine) ExportWorkflowData() ([]byte, error) {
	data := make(map[string]interface{})

	we.workflowsMutex.RLock()
	data["workflow_definitions"] = we.workflows
	we.workflowsMutex.RUnlock()

	we.activeMutex.RLock()
	data["active_workflows"] = we.activeWorkflows
	we.activeMutex.RUnlock()

	return json.MarshalIndent(data, "", "  ")
}
