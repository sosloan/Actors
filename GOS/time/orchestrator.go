package time

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	"github.com/jmoiron/sqlx"
)

// OrchestrationContext represents the context for workflow orchestration
type OrchestrationContext struct {
	OrchestrationID string                     `json:"orchestration_id"`
	Name            string                     `json:"name"`
	Description     string                     `json:"description"`
	Type            string                     `json:"type"` // sequential, parallel, conditional, hybrid
	Workflows       []OrchestrationWorkflow    `json:"workflows"`
	Participants    []OrchestrationParticipant `json:"participants"`
	State           OrchestrationState         `json:"state"`
	StartTime       time.Time                  `json:"start_time"`
	EndTime         *time.Time                 `json:"end_time,omitempty"`
	Metadata        map[string]interface{}     `json:"metadata"`
	CreatedAt       time.Time                  `json:"created_at"`
	UpdatedAt       time.Time                  `json:"updated_at"`
}

// OrchestrationWorkflow represents a workflow within an orchestration
type OrchestrationWorkflow struct {
	WorkflowID     string                 `json:"workflow_id"`
	UserID         string                 `json:"user_id"`
	SessionID      string                 `json:"session_id"`
	StartCondition string                 `json:"start_condition"`
	EndCondition   string                 `json:"end_condition"`
	Dependencies   []string               `json:"dependencies"`
	Priority       int                    `json:"priority"`
	IsActive       bool                   `json:"is_active"`
	IsCompleted    bool                   `json:"is_completed"`
	StartTime      *time.Time             `json:"start_time,omitempty"`
	EndTime        *time.Time             `json:"end_time,omitempty"`
	Metadata       map[string]interface{} `json:"metadata"`
}

// OrchestrationParticipant represents a participant in an orchestration
type OrchestrationParticipant struct {
	UserID      string                 `json:"user_id"`
	Role        string                 `json:"role"`
	Permissions []string               `json:"permissions"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// OrchestrationState represents the state of an orchestration
type OrchestrationState string

const (
	OrchestrationStatePending   OrchestrationState = "pending"
	OrchestrationStateActive    OrchestrationState = "active"
	OrchestrationStatePaused    OrchestrationState = "paused"
	OrchestrationStateCompleted OrchestrationState = "completed"
	OrchestrationStateFailed    OrchestrationState = "failed"
	OrchestrationStateCancelled OrchestrationState = "cancelled"
)

// OrchestrationRule represents a rule for orchestration behavior
type OrchestrationRule struct {
	ID         string                 `json:"id"`
	Type       string                 `json:"type"` // condition, action, constraint
	Expression string                 `json:"expression"`
	Parameters map[string]interface{} `json:"parameters"`
	IsActive   bool                   `json:"is_active"`
	Priority   int                    `json:"priority"`
}

// WorkflowOrchestrator manages complex multi-workflow orchestration with advanced coordination capabilities
type WorkflowOrchestrator struct {
	// Core services
	workflowEngine *WorkflowEngine
	timeService    *TimeService
	db             *sqlx.DB

	// Orchestration state management
	orchestrations      map[string]*OrchestrationContext
	orchestrationsMutex sync.RWMutex

	// Event handling system
	eventHandlers map[string][]OrchestrationEventHandler
	handlersMutex sync.RWMutex

	// Lifecycle management
	stopChan     chan struct{}
	isRunning    bool
	runningMutex sync.RWMutex

	// Configuration and limits
	maxConcurrentOrchestrations int
	defaultTimeout              time.Duration

	// Metrics and monitoring
	metrics      *OrchestrationMetrics
	metricsMutex sync.RWMutex

	// Error handling and recovery
	errorHandler OrchestrationErrorHandler
	retryPolicy  *RetryPolicy

	// Logging and debugging
	logger    *log.Logger
	debugMode bool
}

// OrchestrationEventHandler handles orchestration events
type OrchestrationEventHandler func(context.Context, *OrchestrationContext, string, map[string]interface{}) error

// OrchestrationMetrics tracks orchestration performance and statistics
type OrchestrationMetrics struct {
	TotalOrchestrations     int64         `json:"total_orchestrations"`
	ActiveOrchestrations    int64         `json:"active_orchestrations"`
	CompletedOrchestrations int64         `json:"completed_orchestrations"`
	FailedOrchestrations    int64         `json:"failed_orchestrations"`
	AverageDuration         time.Duration `json:"average_duration"`
	LastUpdated             time.Time     `json:"last_updated"`
}

// OrchestrationErrorHandler defines how to handle orchestration errors
type OrchestrationErrorHandler func(context.Context, *OrchestrationContext, error) error

// RetryPolicy defines retry behavior for failed orchestrations
type RetryPolicy struct {
	MaxRetries        int           `json:"max_retries"`
	InitialDelay      time.Duration `json:"initial_delay"`
	MaxDelay          time.Duration `json:"max_delay"`
	BackoffMultiplier float64       `json:"backoff_multiplier"`
}

// NewWorkflowOrchestrator creates a new workflow orchestrator with enhanced capabilities
func NewWorkflowOrchestrator(workflowEngine *WorkflowEngine, timeService *TimeService, db *sqlx.DB) *WorkflowOrchestrator {
	return &WorkflowOrchestrator{
		// Core services
		workflowEngine: workflowEngine,
		timeService:    timeService,
		db:             db,

		// State management
		orchestrations: make(map[string]*OrchestrationContext),
		eventHandlers:  make(map[string][]OrchestrationEventHandler),

		// Lifecycle
		stopChan:     make(chan struct{}),
		isRunning:    false,
		runningMutex: sync.RWMutex{},

		// Configuration defaults
		maxConcurrentOrchestrations: 10,
		defaultTimeout:              30 * time.Minute,

		// Metrics initialization
		metrics: &OrchestrationMetrics{
			LastUpdated: time.Now().UTC(),
		},

		// Error handling defaults
		retryPolicy: &RetryPolicy{
			MaxRetries:        3,
			InitialDelay:      1 * time.Second,
			MaxDelay:          30 * time.Second,
			BackoffMultiplier: 2.0,
		},

		// Logging
		logger:    log.New(os.Stdout, "[Orchestrator] ", log.LstdFlags|log.Lshortfile),
		debugMode: false,
	}
}

// SetMaxConcurrentOrchestrations sets the maximum number of concurrent orchestrations
func (wo *WorkflowOrchestrator) SetMaxConcurrentOrchestrations(max int) {
	wo.maxConcurrentOrchestrations = max
}

// SetDefaultTimeout sets the default timeout for orchestrations
func (wo *WorkflowOrchestrator) SetDefaultTimeout(timeout time.Duration) {
	wo.defaultTimeout = timeout
}

// SetErrorHandler sets a custom error handler for orchestrations
func (wo *WorkflowOrchestrator) SetErrorHandler(handler OrchestrationErrorHandler) {
	wo.errorHandler = handler
}

// SetRetryPolicy sets the retry policy for failed orchestrations
func (wo *WorkflowOrchestrator) SetRetryPolicy(policy *RetryPolicy) {
	wo.retryPolicy = policy
}

// SetDebugMode enables or disables debug mode
func (wo *WorkflowOrchestrator) SetDebugMode(debug bool) {
	wo.debugMode = debug
}

// GetMetrics returns current orchestration metrics
func (wo *WorkflowOrchestrator) GetMetrics() *OrchestrationMetrics {
	wo.metricsMutex.RLock()
	defer wo.metricsMutex.RUnlock()

	// Return a copy to avoid race conditions
	metrics := *wo.metrics
	return &metrics
}

// CreateOrchestration creates a new workflow orchestration
func (wo *WorkflowOrchestrator) CreateOrchestration(name, description, orchestrationType string, workflows []OrchestrationWorkflow, participants []OrchestrationParticipant) (*OrchestrationContext, error) {
	orchestration := &OrchestrationContext{
		OrchestrationID: fmt.Sprintf("orch_%d", time.Now().UnixNano()),
		Name:            name,
		Description:     description,
		Type:            orchestrationType,
		Workflows:       workflows,
		Participants:    participants,
		State:           OrchestrationStatePending,
		Metadata:        make(map[string]interface{}),
		CreatedAt:       time.Now().UTC(),
		UpdatedAt:       time.Now().UTC(),
	}

	wo.orchestrationsMutex.Lock()
	wo.orchestrations[orchestration.OrchestrationID] = orchestration
	wo.orchestrationsMutex.Unlock()

	log.Printf("Created orchestration: %s (%s)", name, orchestration.OrchestrationID)
	return orchestration, nil
}

// StartOrchestration starts a workflow orchestration
func (wo *WorkflowOrchestrator) StartOrchestration(ctx context.Context, orchestrationID string) error {
	wo.orchestrationsMutex.Lock()
	orchestration, exists := wo.orchestrations[orchestrationID]
	wo.orchestrationsMutex.Unlock()

	if !exists {
		return fmt.Errorf("orchestration %s not found", orchestrationID)
	}

	orchestration.State = OrchestrationStateActive
	orchestration.StartTime = wo.timeService.GetCurrentTime()
	orchestration.UpdatedAt = time.Now().UTC()

	// Start workflows based on orchestration type
	switch orchestration.Type {
	case "sequential":
		return wo.startSequentialOrchestration(ctx, orchestration)
	case "parallel":
		return wo.startParallelOrchestration(ctx, orchestration)
	case "conditional":
		return wo.startConditionalOrchestration(ctx, orchestration)
	case "hybrid":
		return wo.startHybridOrchestration(ctx, orchestration)
	default:
		return fmt.Errorf("unsupported orchestration type: %s", orchestration.Type)
	}
}

// startSequentialOrchestration starts workflows in sequence
func (wo *WorkflowOrchestrator) startSequentialOrchestration(ctx context.Context, orchestration *OrchestrationContext) error {
	for i, workflow := range orchestration.Workflows {
		// Start the workflow
		workflowCtx, err := wo.workflowEngine.StartWorkflow(ctx, workflow.WorkflowID, workflow.UserID, workflow.Metadata)
		if err != nil {
			log.Printf("Error starting workflow %s: %v", workflow.WorkflowID, err)
			continue
		}

		// Update orchestration workflow
		orchestration.Workflows[i].SessionID = workflowCtx.SessionID
		orchestration.Workflows[i].IsActive = true
		startTime := wo.timeService.GetCurrentTime()
		orchestration.Workflows[i].StartTime = &startTime

		// Wait for workflow completion
		wo.waitForWorkflowCompletion(ctx, workflowCtx.SessionID)

		// Mark as completed
		orchestration.Workflows[i].IsCompleted = true
		orchestration.Workflows[i].IsActive = false
		endTime := wo.timeService.GetCurrentTime()
		orchestration.Workflows[i].EndTime = &endTime

		// Trigger workflow completion event
		wo.triggerEvent(ctx, orchestration, "workflow_completed", map[string]interface{}{
			"workflow_id": workflow.WorkflowID,
			"user_id":     workflow.UserID,
			"session_id":  workflowCtx.SessionID,
			"sequence":    i + 1,
		})
	}

	// Mark orchestration as completed
	orchestration.State = OrchestrationStateCompleted
	endTime := wo.timeService.GetCurrentTime()
	orchestration.EndTime = &endTime
	orchestration.UpdatedAt = time.Now().UTC()

	wo.triggerEvent(ctx, orchestration, "orchestration_completed", map[string]interface{}{
		"total_workflows": len(orchestration.Workflows),
		"duration":        endTime.Sub(orchestration.StartTime).Seconds(),
	})

	return nil
}

// startParallelOrchestration starts workflows in parallel
func (wo *WorkflowOrchestrator) startParallelOrchestration(ctx context.Context, orchestration *OrchestrationContext) error {
	var wg sync.WaitGroup
	workflowChannels := make(map[string]chan bool)

	// Start all workflows in parallel
	for i, workflow := range orchestration.Workflows {
		workflowCtx, err := wo.workflowEngine.StartWorkflow(ctx, workflow.WorkflowID, workflow.UserID, workflow.Metadata)
		if err != nil {
			log.Printf("Error starting workflow %s: %v", workflow.WorkflowID, err)
			continue
		}

		// Update orchestration workflow
		orchestration.Workflows[i].SessionID = workflowCtx.SessionID
		orchestration.Workflows[i].IsActive = true
		startTime := wo.timeService.GetCurrentTime()
		orchestration.Workflows[i].StartTime = &startTime

		// Create completion channel
		workflowChannels[workflowCtx.SessionID] = make(chan bool, 1)

		// Start goroutine to wait for completion
		wg.Add(1)
		go func(sessionID string, workflowIndex int) {
			defer wg.Done()
			wo.waitForWorkflowCompletion(ctx, sessionID)
			workflowChannels[sessionID] <- true
		}(workflowCtx.SessionID, i)
	}

	// Wait for all workflows to complete
	wg.Wait()

	// Mark all workflows as completed
	for i := range orchestration.Workflows {
		if orchestration.Workflows[i].IsActive {
			orchestration.Workflows[i].IsCompleted = true
			orchestration.Workflows[i].IsActive = false
			endTime := wo.timeService.GetCurrentTime()
			orchestration.Workflows[i].EndTime = &endTime
		}
	}

	// Mark orchestration as completed
	orchestration.State = OrchestrationStateCompleted
	endTime := wo.timeService.GetCurrentTime()
	orchestration.EndTime = &endTime
	orchestration.UpdatedAt = time.Now().UTC()

	wo.triggerEvent(ctx, orchestration, "orchestration_completed", map[string]interface{}{
		"total_workflows": len(orchestration.Workflows),
		"duration":        endTime.Sub(orchestration.StartTime).Seconds(),
		"type":            "parallel",
	})

	return nil
}

// startConditionalOrchestration starts workflows based on conditions
func (wo *WorkflowOrchestrator) startConditionalOrchestration(ctx context.Context, orchestration *OrchestrationContext) error {
	for i, workflow := range orchestration.Workflows {
		// Evaluate start condition
		if !wo.evaluateCondition(workflow.StartCondition, orchestration) {
			log.Printf("Start condition not met for workflow %s", workflow.WorkflowID)
			continue
		}

		// Start the workflow
		workflowCtx, err := wo.workflowEngine.StartWorkflow(ctx, workflow.WorkflowID, workflow.UserID, workflow.Metadata)
		if err != nil {
			log.Printf("Error starting workflow %s: %v", workflow.WorkflowID, err)
			continue
		}

		// Update orchestration workflow
		orchestration.Workflows[i].SessionID = workflowCtx.SessionID
		orchestration.Workflows[i].IsActive = true
		startTime := wo.timeService.GetCurrentTime()
		orchestration.Workflows[i].StartTime = &startTime

		// Wait for workflow completion
		wo.waitForWorkflowCompletion(ctx, workflowCtx.SessionID)

		// Mark as completed
		orchestration.Workflows[i].IsCompleted = true
		orchestration.Workflows[i].IsActive = false
		endTime := wo.timeService.GetCurrentTime()
		orchestration.Workflows[i].EndTime = &endTime

		// Check if we should continue based on end condition
		if !wo.evaluateCondition(workflow.EndCondition, orchestration) {
			log.Printf("End condition not met, stopping orchestration")
			break
		}
	}

	// Mark orchestration as completed
	orchestration.State = OrchestrationStateCompleted
	endTime := wo.timeService.GetCurrentTime()
	orchestration.EndTime = &endTime
	orchestration.UpdatedAt = time.Now().UTC()

	wo.triggerEvent(ctx, orchestration, "orchestration_completed", map[string]interface{}{
		"total_workflows": len(orchestration.Workflows),
		"duration":        endTime.Sub(orchestration.StartTime).Seconds(),
		"type":            "conditional",
	})

	return nil
}

// startHybridOrchestration starts workflows with mixed execution patterns
func (wo *WorkflowOrchestrator) startHybridOrchestration(ctx context.Context, orchestration *OrchestrationContext) error {
	// Group workflows by execution pattern
	sequentialGroups := make([][]OrchestrationWorkflow, 0)
	parallelGroups := make([][]OrchestrationWorkflow, 0)

	// Simple grouping logic - in a real implementation, this would be more sophisticated
	currentGroup := make([]OrchestrationWorkflow, 0)
	for _, workflow := range orchestration.Workflows {
		if workflow.Metadata["execution_pattern"] == "parallel" {
			if len(currentGroup) > 0 {
				sequentialGroups = append(sequentialGroups, currentGroup)
				currentGroup = make([]OrchestrationWorkflow, 0)
			}
			parallelGroups = append(parallelGroups, []OrchestrationWorkflow{workflow})
		} else {
			currentGroup = append(currentGroup, workflow)
		}
	}
	if len(currentGroup) > 0 {
		sequentialGroups = append(sequentialGroups, currentGroup)
	}

	// Execute sequential groups
	for _, group := range sequentialGroups {
		for _, workflow := range group {
			workflowCtx, err := wo.workflowEngine.StartWorkflow(ctx, workflow.WorkflowID, workflow.UserID, workflow.Metadata)
			if err != nil {
				log.Printf("Error starting workflow %s: %v", workflow.WorkflowID, err)
				continue
			}

			wo.waitForWorkflowCompletion(ctx, workflowCtx.SessionID)
		}
	}

	// Execute parallel groups
	for _, group := range parallelGroups {
		var wg sync.WaitGroup
		for _, workflow := range group {
			wg.Add(1)
			go func(w OrchestrationWorkflow) {
				defer wg.Done()
				workflowCtx, err := wo.workflowEngine.StartWorkflow(ctx, w.WorkflowID, w.UserID, w.Metadata)
				if err != nil {
					log.Printf("Error starting workflow %s: %v", w.WorkflowID, err)
					return
				}

				wo.waitForWorkflowCompletion(ctx, workflowCtx.SessionID)
			}(workflow)
		}
		wg.Wait()
	}

	// Mark orchestration as completed
	orchestration.State = OrchestrationStateCompleted
	endTime := wo.timeService.GetCurrentTime()
	orchestration.EndTime = &endTime
	orchestration.UpdatedAt = time.Now().UTC()

	wo.triggerEvent(ctx, orchestration, "orchestration_completed", map[string]interface{}{
		"total_workflows": len(orchestration.Workflows),
		"duration":        endTime.Sub(orchestration.StartTime).Seconds(),
		"type":            "hybrid",
	})

	return nil
}

// waitForWorkflowCompletion waits for a workflow to complete
func (wo *WorkflowOrchestrator) waitForWorkflowCompletion(ctx context.Context, sessionID string) {
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			progress, err := wo.workflowEngine.GetWorkflowProgress(sessionID)
			if err != nil {
				log.Printf("Error getting workflow progress: %v", err)
				return
			}

			state := progress["state"].(string)
			if state == "completed" || state == "failed" || state == "cancelled" {
				return
			}
		}
	}
}

// evaluateCondition evaluates a condition for workflow execution
func (wo *WorkflowOrchestrator) evaluateCondition(condition string, orchestration *OrchestrationContext) bool {
	// Simple condition evaluation - in a real implementation, this would be more sophisticated
	switch condition {
	case "always":
		return true
	case "never":
		return false
	case "if_previous_successful":
		// Check if previous workflow was successful
		if len(orchestration.Workflows) > 0 {
			lastWorkflow := orchestration.Workflows[len(orchestration.Workflows)-1]
			return lastWorkflow.IsCompleted && lastWorkflow.IsActive == false
		}
		return false
	case "if_time_before_noon":
		return wo.timeService.GetCurrentTime().Hour() < 12
	case "if_time_after_noon":
		return wo.timeService.GetCurrentTime().Hour() >= 12
	default:
		return true
	}
}

// RegisterEventHandler registers an event handler for orchestration events
func (wo *WorkflowOrchestrator) RegisterEventHandler(eventType string, handler OrchestrationEventHandler) {
	wo.handlersMutex.Lock()
	defer wo.handlersMutex.Unlock()

	wo.eventHandlers[eventType] = append(wo.eventHandlers[eventType], handler)
}

// triggerEvent triggers an orchestration event
func (wo *WorkflowOrchestrator) triggerEvent(ctx context.Context, orchestration *OrchestrationContext, eventType string, data map[string]interface{}) {
	wo.handlersMutex.RLock()
	handlers := wo.eventHandlers[eventType]
	wo.handlersMutex.RUnlock()

	for _, handler := range handlers {
		if err := handler(ctx, orchestration, eventType, data); err != nil {
			log.Printf("Error in orchestration event handler: %v", err)
		}
	}
}

// GetOrchestrationStatus returns the status of an orchestration
func (wo *WorkflowOrchestrator) GetOrchestrationStatus(orchestrationID string) (map[string]interface{}, error) {
	wo.orchestrationsMutex.RLock()
	orchestration, exists := wo.orchestrations[orchestrationID]
	wo.orchestrationsMutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("orchestration %s not found", orchestrationID)
	}

	status := map[string]interface{}{
		"orchestration_id":    orchestrationID,
		"name":                orchestration.Name,
		"type":                orchestration.Type,
		"state":               orchestration.State,
		"start_time":          orchestration.StartTime,
		"end_time":            orchestration.EndTime,
		"total_workflows":     len(orchestration.Workflows),
		"active_workflows":    0,
		"completed_workflows": 0,
		"participants":        len(orchestration.Participants),
	}

	// Count workflow states
	for _, workflow := range orchestration.Workflows {
		if workflow.IsActive {
			status["active_workflows"] = status["active_workflows"].(int) + 1
		}
		if workflow.IsCompleted {
			status["completed_workflows"] = status["completed_workflows"].(int) + 1
		}
	}

	// Calculate progress
	if len(orchestration.Workflows) > 0 {
		status["progress_percentage"] = float64(status["completed_workflows"].(int)) / float64(len(orchestration.Workflows)) * 100
	} else {
		status["progress_percentage"] = 0.0
	}

	// Calculate duration
	if orchestration.StartTime.IsZero() {
		status["duration"] = 0.0
	} else {
		endTime := orchestration.EndTime
		if endTime == nil {
			currentTime := wo.timeService.GetCurrentTime()
			endTime = &currentTime
		}
		status["duration"] = endTime.Sub(orchestration.StartTime).Seconds()
	}

	return status, nil
}

// GetOrchestrationAnalytics returns analytics for orchestrations
func (wo *WorkflowOrchestrator) GetOrchestrationAnalytics(startDate, endDate time.Time) (map[string]interface{}, error) {
	wo.orchestrationsMutex.RLock()
	defer wo.orchestrationsMutex.RUnlock()

	analytics := map[string]interface{}{
		"period":                      fmt.Sprintf("%s to %s", startDate.Format("2006-01-02"), endDate.Format("2006-01-02")),
		"total_orchestrations":        0,
		"completed_orchestrations":    0,
		"failed_orchestrations":       0,
		"cancelled_orchestrations":    0,
		"average_duration":            0.0,
		"success_rate":                0.0,
		"orchestrations_by_type":      make(map[string]int),
		"workflows_per_orchestration": 0.0,
	}

	totalDuration := 0.0
	completedCount := 0

	for _, orchestration := range wo.orchestrations {
		// Filter by date range
		if orchestration.StartTime.Before(startDate) || orchestration.StartTime.After(endDate) {
			continue
		}

		analytics["total_orchestrations"] = analytics["total_orchestrations"].(int) + 1

		// Count by state
		switch orchestration.State {
		case OrchestrationStateCompleted:
			analytics["completed_orchestrations"] = analytics["completed_orchestrations"].(int) + 1
			completedCount++
		case OrchestrationStateFailed:
			analytics["failed_orchestrations"] = analytics["failed_orchestrations"].(int) + 1
		case OrchestrationStateCancelled:
			analytics["cancelled_orchestrations"] = analytics["cancelled_orchestrations"].(int) + 1
		}

		// Count by type
		typeCount := analytics["orchestrations_by_type"].(map[string]int)
		typeCount[orchestration.Type]++

		// Calculate duration
		if !orchestration.StartTime.IsZero() {
			endTime := orchestration.EndTime
			if endTime == nil {
				currentTime := wo.timeService.GetCurrentTime()
				endTime = &currentTime
			}
			duration := endTime.Sub(orchestration.StartTime).Seconds()
			totalDuration += duration
		}

		// Count workflows
		analytics["workflows_per_orchestration"] = analytics["workflows_per_orchestration"].(float64) + float64(len(orchestration.Workflows))
	}

	// Calculate averages
	if analytics["total_orchestrations"].(int) > 0 {
		analytics["average_duration"] = totalDuration / float64(analytics["total_orchestrations"].(int))
		analytics["workflows_per_orchestration"] = analytics["workflows_per_orchestration"].(float64) / float64(analytics["total_orchestrations"].(int))
	}

	if completedCount > 0 {
		analytics["success_rate"] = float64(completedCount) / float64(analytics["total_orchestrations"].(int)) * 100
	}

	return analytics, nil
}

// ExportOrchestrationData exports orchestration data
func (wo *WorkflowOrchestrator) ExportOrchestrationData() ([]byte, error) {
	wo.orchestrationsMutex.RLock()
	defer wo.orchestrationsMutex.RUnlock()

	return json.MarshalIndent(wo.orchestrations, "", "  ")
}
