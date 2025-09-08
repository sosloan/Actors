package time

import (
	"context"
	"fmt"
	"log"
	"sync"
	"time"

	"github.com/jmoiron/sqlx"
)

// WorkflowManager provides a unified interface for managing all workflow operations
type WorkflowManager struct {
	timeService    *TimeService
	workflowEngine *WorkflowEngine
	orchestrator   *WorkflowOrchestrator
	db             *sqlx.DB
	userSessions   map[string][]string // userID -> sessionIDs
	sessionsMutex  sync.RWMutex
	eventBus       *WorkflowEventBus
	stopChan       chan struct{}
	isRunning      bool
	runningMutex   sync.RWMutex
}

// WorkflowEventBus manages workflow events across the system
type WorkflowEventBus struct {
	subscribers      map[string][]WorkflowEventSubscriber
	subscribersMutex sync.RWMutex
	eventQueue       chan WorkflowEvent
	stopChan         chan struct{}
	isRunning        bool
	runningMutex     sync.RWMutex
}

// WorkflowEvent represents a workflow event
type WorkflowEvent struct {
	ID        string                 `json:"id"`
	Type      string                 `json:"type"`
	Source    string                 `json:"source"` // workflow, orchestration, system
	UserID    string                 `json:"user_id"`
	SessionID string                 `json:"session_id"`
	Data      map[string]interface{} `json:"data"`
	Timestamp time.Time              `json:"timestamp"`
	Priority  int                    `json:"priority"`
}

// WorkflowEventSubscriber handles workflow events
type WorkflowEventSubscriber interface {
	HandleEvent(ctx context.Context, event WorkflowEvent) error
	GetEventTypes() []string
	GetPriority() int
}

// NewWorkflowManager creates a new workflow manager
func NewWorkflowManager(timeService *TimeService, db *sqlx.DB) *WorkflowManager {
	workflowEngine := NewWorkflowEngine(timeService, db)
	orchestrator := NewWorkflowOrchestrator(workflowEngine, timeService, db)
	eventBus := NewWorkflowEventBus()

	manager := &WorkflowManager{
		timeService:    timeService,
		workflowEngine: workflowEngine,
		orchestrator:   orchestrator,
		db:             db,
		userSessions:   make(map[string][]string),
		eventBus:       eventBus,
		stopChan:       make(chan struct{}),
	}

	// Register default event handlers
	manager.registerDefaultEventHandlers()

	return manager
}

// NewWorkflowEventBus creates a new workflow event bus
func NewWorkflowEventBus() *WorkflowEventBus {
	return &WorkflowEventBus{
		subscribers: make(map[string][]WorkflowEventSubscriber),
		eventQueue:  make(chan WorkflowEvent, 1000),
		stopChan:    make(chan struct{}),
	}
}

// Start starts the workflow manager
func (wm *WorkflowManager) Start(ctx context.Context) {
	wm.runningMutex.Lock()
	if wm.isRunning {
		wm.runningMutex.Unlock()
		return
	}
	wm.isRunning = true
	wm.runningMutex.Unlock()

	log.Println("Starting Workflow Manager...")

	// Start event bus
	wm.eventBus.Start(ctx)

	// Start time service
	wm.timeService.Start(ctx)

	log.Println("Workflow Manager started successfully")
}

// Stop stops the workflow manager
func (wm *WorkflowManager) Stop() {
	wm.runningMutex.Lock()
	defer wm.runningMutex.Unlock()

	if wm.isRunning {
		wm.eventBus.Stop()
		wm.timeService.Stop()
		close(wm.stopChan)
		wm.isRunning = false
		log.Println("Workflow Manager stopped")
	}
}

// StartWorkflow starts a new workflow for a user
func (wm *WorkflowManager) StartWorkflow(ctx context.Context, workflowID, userID string, metadata map[string]interface{}) (*WorkflowContext, error) {
	// Start the workflow
	workflowCtx, err := wm.workflowEngine.StartWorkflow(ctx, workflowID, userID, metadata)
	if err != nil {
		return nil, err
	}

	// Track user session
	wm.sessionsMutex.Lock()
	wm.userSessions[userID] = append(wm.userSessions[userID], workflowCtx.SessionID)
	wm.sessionsMutex.Unlock()

	// Publish workflow start event
	wm.eventBus.PublishEvent(WorkflowEvent{
		ID:        fmt.Sprintf("workflow_start_%d", time.Now().UnixNano()),
		Type:      "workflow_started",
		Source:    "workflow",
		UserID:    userID,
		SessionID: workflowCtx.SessionID,
		Data: map[string]interface{}{
			"workflow_id": workflowID,
			"metadata":    metadata,
		},
		Timestamp: time.Now().UTC(),
		Priority:  3,
	})

	return workflowCtx, nil
}

// StartOrchestration starts a new orchestration
func (wm *WorkflowManager) StartOrchestration(ctx context.Context, orchestrationID string) error {
	// Start the orchestration
	err := wm.orchestrator.StartOrchestration(ctx, orchestrationID)
	if err != nil {
		return err
	}

	// Publish orchestration start event
	wm.eventBus.PublishEvent(WorkflowEvent{
		ID:     fmt.Sprintf("orchestration_start_%d", time.Now().UnixNano()),
		Type:   "orchestration_started",
		Source: "orchestration",
		Data: map[string]interface{}{
			"orchestration_id": orchestrationID,
		},
		Timestamp: time.Now().UTC(),
		Priority:  4,
	})

	return nil
}

// CreateOrchestration creates a new orchestration
func (wm *WorkflowManager) CreateOrchestration(name, description, orchestrationType string, workflows []OrchestrationWorkflow, participants []OrchestrationParticipant) (*OrchestrationContext, error) {
	return wm.orchestrator.CreateOrchestration(name, description, orchestrationType, workflows, participants)
}

// GetUserWorkflows returns all workflows for a user
func (wm *WorkflowManager) GetUserWorkflows(userID string) []*WorkflowContext {
	wm.sessionsMutex.RLock()
	sessionIDs := wm.userSessions[userID]
	wm.sessionsMutex.RUnlock()

	var workflows []*WorkflowContext
	for _, sessionID := range sessionIDs {
		if workflow, err := wm.workflowEngine.GetWorkflowProgress(sessionID); err == nil {
			// Convert progress to workflow context (simplified)
			workflowCtx := &WorkflowContext{
				SessionID: sessionID,
				UserID:    userID,
				State:     WorkflowState(workflow["state"].(string)),
			}
			workflows = append(workflows, workflowCtx)
		}
	}

	return workflows
}

// GetWorkflowAnalytics returns comprehensive workflow analytics
func (wm *WorkflowManager) GetWorkflowAnalytics(userID string, startDate, endDate time.Time) (map[string]interface{}, error) {
	analytics := make(map[string]interface{})

	// Get individual workflow analytics
	workflowAnalytics, err := wm.workflowEngine.GetWorkflowAnalytics(userID, startDate, endDate)
	if err != nil {
		log.Printf("Error getting workflow analytics: %v", err)
	} else {
		analytics["individual_workflows"] = workflowAnalytics
	}

	// Get orchestration analytics
	orchestrationAnalytics, err := wm.orchestrator.GetOrchestrationAnalytics(startDate, endDate)
	if err != nil {
		log.Printf("Error getting orchestration analytics: %v", err)
	} else {
		analytics["orchestrations"] = orchestrationAnalytics
	}

	// Get time analytics
	timeInsights, err := wm.timeService.GetTimeInsights(userID, startDate, endDate)
	if err != nil {
		log.Printf("Error getting time insights: %v", err)
	} else {
		analytics["time_insights"] = timeInsights
	}

	// Calculate overall productivity score
	productivityScore, err := wm.timeService.GetProductivityScore(userID, startDate, endDate)
	if err != nil {
		log.Printf("Error getting productivity score: %v", err)
	} else {
		analytics["productivity_score"] = productivityScore
	}

	return analytics, nil
}

// RegisterEventSubscriber registers an event subscriber
func (wm *WorkflowManager) RegisterEventSubscriber(subscriber WorkflowEventSubscriber) {
	wm.eventBus.RegisterSubscriber(subscriber)
}

// PublishEvent publishes a workflow event
func (wm *WorkflowManager) PublishEvent(event WorkflowEvent) {
	wm.eventBus.PublishEvent(event)
}

// registerDefaultEventHandlers registers default event handlers
func (wm *WorkflowManager) registerDefaultEventHandlers() {
	// Workflow event handlers
	wm.workflowEngine.RegisterEventHandler("workflow_started", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		wm.eventBus.PublishEvent(WorkflowEvent{
			ID:        fmt.Sprintf("workflow_%s_%d", eventType, time.Now().UnixNano()),
			Type:      eventType,
			Source:    "workflow",
			UserID:    workflowCtx.UserID,
			SessionID: workflowCtx.SessionID,
			Data:      data,
			Timestamp: time.Now().UTC(),
			Priority:  3,
		})
		return nil
	})

	wm.workflowEngine.RegisterEventHandler("phase_completed", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		wm.eventBus.PublishEvent(WorkflowEvent{
			ID:        fmt.Sprintf("workflow_%s_%d", eventType, time.Now().UnixNano()),
			Type:      eventType,
			Source:    "workflow",
			UserID:    workflowCtx.UserID,
			SessionID: workflowCtx.SessionID,
			Data:      data,
			Timestamp: time.Now().UTC(),
			Priority:  2,
		})
		return nil
	})

	wm.workflowEngine.RegisterEventHandler("workflow_completed", func(ctx context.Context, workflowCtx *WorkflowContext, eventType string, data map[string]interface{}) error {
		wm.eventBus.PublishEvent(WorkflowEvent{
			ID:        fmt.Sprintf("workflow_%s_%d", eventType, time.Now().UnixNano()),
			Type:      eventType,
			Source:    "workflow",
			UserID:    workflowCtx.UserID,
			SessionID: workflowCtx.SessionID,
			Data:      data,
			Timestamp: time.Now().UTC(),
			Priority:  4,
		})
		return nil
	})

	// Orchestration event handlers
	wm.orchestrator.RegisterEventHandler("orchestration_completed", func(ctx context.Context, orchestration *OrchestrationContext, eventType string, data map[string]interface{}) error {
		wm.eventBus.PublishEvent(WorkflowEvent{
			ID:        fmt.Sprintf("orchestration_%s_%d", eventType, time.Now().UnixNano()),
			Type:      eventType,
			Source:    "orchestration",
			Data:      data,
			Timestamp: time.Now().UTC(),
			Priority:  5,
		})
		return nil
	})
}

// Start starts the event bus
func (web *WorkflowEventBus) Start(ctx context.Context) {
	web.runningMutex.Lock()
	if web.isRunning {
		web.runningMutex.Unlock()
		return
	}
	web.isRunning = true
	web.runningMutex.Unlock()

	log.Println("Starting Workflow Event Bus...")

	go func() {
		for {
			select {
			case <-ctx.Done():
				log.Println("Event bus stopped by context")
				return
			case <-web.stopChan:
				log.Println("Event bus stopped")
				return
			case event := <-web.eventQueue:
				web.processEvent(ctx, event)
			}
		}
	}()
}

// Stop stops the event bus
func (web *WorkflowEventBus) Stop() {
	web.runningMutex.Lock()
	defer web.runningMutex.Unlock()

	if web.isRunning {
		close(web.stopChan)
		web.isRunning = false
		log.Println("Event bus stopped")
	}
}

// PublishEvent publishes an event to the event bus
func (web *WorkflowEventBus) PublishEvent(event WorkflowEvent) {
	select {
	case web.eventQueue <- event:
		// Event published successfully
	default:
		log.Printf("Event queue full, dropping event: %s", event.Type)
	}
}

// RegisterSubscriber registers an event subscriber
func (web *WorkflowEventBus) RegisterSubscriber(subscriber WorkflowEventSubscriber) {
	web.subscribersMutex.Lock()
	defer web.subscribersMutex.Unlock()

	for _, eventType := range subscriber.GetEventTypes() {
		web.subscribers[eventType] = append(web.subscribers[eventType], subscriber)
	}
}

// processEvent processes an event and notifies subscribers
func (web *WorkflowEventBus) processEvent(ctx context.Context, event WorkflowEvent) {
	web.subscribersMutex.RLock()
	subscribers := web.subscribers[event.Type]
	web.subscribersMutex.RUnlock()

	// Process subscribers in priority order
	for _, subscriber := range subscribers {
		go func(sub WorkflowEventSubscriber) {
			if err := sub.HandleEvent(ctx, event); err != nil {
				log.Printf("Error in event subscriber: %v", err)
			}
		}(subscriber)
	}
}

// ExampleEventSubscriber demonstrates how to create an event subscriber
type ExampleEventSubscriber struct {
	name string
}

// HandleEvent handles workflow events
func (es *ExampleEventSubscriber) HandleEvent(ctx context.Context, event WorkflowEvent) error {
	log.Printf("📡 Event Subscriber [%s]: Received %s event for user %s",
		es.name, event.Type, event.UserID)

	// Process the event based on type
	switch event.Type {
	case "workflow_started":
		log.Printf("   🚀 Workflow started: %s", event.Data["workflow_id"])
	case "phase_completed":
		log.Printf("   ✅ Phase completed: %s", event.Data["phase_id"])
	case "workflow_completed":
		log.Printf("   🎉 Workflow completed with success rate: %.2f%%",
			event.Data["success_rate"].(float64)*100)
	case "orchestration_completed":
		log.Printf("   🏁 Orchestration completed: %d workflows",
			event.Data["total_workflows"])
	}

	return nil
}

// GetEventTypes returns the event types this subscriber handles
func (es *ExampleEventSubscriber) GetEventTypes() []string {
	return []string{
		"workflow_started",
		"phase_completed",
		"workflow_completed",
		"orchestration_completed",
	}
}

// GetPriority returns the priority of this subscriber
func (es *ExampleEventSubscriber) GetPriority() int {
	return 1
}

// ExampleWorkflowManager demonstrates the complete workflow management system
func ExampleWorkflowManager() {
	log.Println("\n=== Workflow Manager Example ===")

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

	// Create workflow manager
	workflowManager := NewWorkflowManager(timeService, db)

	// Register event subscriber
	eventSubscriber := &ExampleEventSubscriber{name: "AnalyticsSubscriber"}
	workflowManager.RegisterEventSubscriber(eventSubscriber)

	// Create context
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start workflow manager
	workflowManager.Start(ctx)
	defer workflowManager.Stop()

	// Start a workflow
	workflowCtx, err := workflowManager.StartWorkflow(ctx, "deep_work_flow", "demo_user", map[string]interface{}{
		"project":  "Workflow Manager Demo",
		"priority": "high",
	})
	if err != nil {
		log.Printf("Error starting workflow: %v", err)
		return
	}

	// Complete a phase
	time.Sleep(100 * time.Millisecond)
	if err := workflowManager.workflowEngine.CompletePhase(ctx, workflowCtx.SessionID, "preparation", true, map[string]interface{}{
		"environment_ready": true,
	}); err != nil {
		log.Printf("Error completing phase: %v", err)
	}

	// Get user workflows
	userWorkflows := workflowManager.GetUserWorkflows("demo_user")
	log.Printf("User has %d active workflows", len(userWorkflows))

	// Get workflow analytics
	analytics, err := workflowManager.GetWorkflowAnalytics("demo_user", time.Now().Add(-24*time.Hour), time.Now())
	if err != nil {
		log.Printf("Error getting analytics: %v", err)
	} else {
		log.Printf("Workflow Analytics: %+v", analytics)
	}

	// Export workflow data
	workflowData, err := workflowManager.workflowEngine.ExportWorkflowData()
	if err != nil {
		log.Printf("Error exporting workflow data: %v", err)
	} else {
		log.Printf("Exported %d bytes of workflow data", len(workflowData))
	}

	log.Println("Workflow Manager example completed")
}
