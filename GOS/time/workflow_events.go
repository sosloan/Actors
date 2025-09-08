package time

import (
	"context"
	"errors"
	"fmt"
	"log"
	"time"

	"github.com/jmoiron/sqlx"
)

// WorkflowEventCategory represents the category of workflow events
type WorkflowEventCategory string

const (
	WorkflowEventCategoryExecution WorkflowEventCategory = "execution"
	WorkflowEventCategoryPhase     WorkflowEventCategory = "phase"
	WorkflowEventCategoryMilestone WorkflowEventCategory = "milestone"
	WorkflowEventCategoryError     WorkflowEventCategory = "error"
	WorkflowEventCategoryMetrics   WorkflowEventCategory = "metrics"
)

// WorkflowEventSubCategory represents the subcategory of workflow events
type WorkflowEventSubCategory string

const (
	WorkflowEventSubCategoryStart    WorkflowEventSubCategory = "start"
	WorkflowEventSubCategoryEnd      WorkflowEventSubCategory = "end"
	WorkflowEventSubCategoryPause    WorkflowEventSubCategory = "pause"
	WorkflowEventSubCategoryResume   WorkflowEventSubCategory = "resume"
	WorkflowEventSubCategoryComplete WorkflowEventSubCategory = "complete"
	WorkflowEventSubCategoryFail     WorkflowEventSubCategory = "fail"
	WorkflowEventSubCategoryCancel   WorkflowEventSubCategory = "cancel"
)

// WorkflowMetrics represents metrics for workflow execution
type WorkflowMetrics struct {
	Duration      time.Duration  `json:"duration"`
	StepCount     int            `json:"step_count"`
	ErrorCount    int            `json:"error_count"`
	RetryCount    int            `json:"retry_count"`
	SuccessRate   float64        `json:"success_rate"`
	Efficiency    float64        `json:"efficiency"`
	ResourceUsage map[string]int `json:"resource_usage"`
}

// WorkflowEventMetadata represents enhanced metadata for workflow events
type WorkflowEventMetadata struct {
	// Core workflow information
	WorkflowID string `json:"workflow_id"`
	SessionID  string `json:"session_id"`
	PhaseID    string `json:"phase_id,omitempty"`
	Version    string `json:"version"`

	// Event categorization
	Category    WorkflowEventCategory    `json:"category"`
	SubCategory WorkflowEventSubCategory `json:"sub_category"`

	// Execution context
	UserID      string `json:"user_id"`
	Environment string `json:"environment,omitempty"`
	Project     string `json:"project,omitempty"`
	Priority    string `json:"priority,omitempty"`

	// Performance metrics
	Metrics *WorkflowMetrics `json:"metrics,omitempty"`

	// Correlation and linking
	ParentEventID string `json:"parent_event_id,omitempty"`
	CorrelationID string `json:"correlation_id"`
	TraceID       string `json:"trace_id,omitempty"`

	// Success criteria and results
	SuccessCriteria map[string]interface{} `json:"success_criteria,omitempty"`
	Results         map[string]interface{} `json:"results,omitempty"`

	// Instructions and context
	Instructions []string               `json:"instructions,omitempty"`
	Context      map[string]interface{} `json:"context,omitempty"`

	// External system integration
	ExternalID     string `json:"external_id,omitempty"`
	ExternalSystem string `json:"external_system,omitempty"`

	// Custom fields
	Custom map[string]interface{} `json:"custom,omitempty"`
}

// WorkflowEventBuilder provides a fluent interface for building workflow events
type WorkflowEventBuilder struct {
	event    *TimeEvent
	metadata *WorkflowEventMetadata
}

// NewWorkflowEventBuilder creates a new workflow event builder
func NewWorkflowEventBuilder() *WorkflowEventBuilder {
	return &WorkflowEventBuilder{
		event: &TimeEvent{
			IsRecurring: false,
			IsActive:    true,
			IsCompleted: false,
			CreatedAt:   time.Now().UTC(),
			UpdatedAt:   time.Now().UTC(),
		},
		metadata: &WorkflowEventMetadata{
			Custom: make(map[string]interface{}),
		},
	}
}

// WithID sets the event ID
func (b *WorkflowEventBuilder) WithID(id string) *WorkflowEventBuilder {
	b.event.ID = id
	return b
}

// WithUserID sets the user ID
func (b *WorkflowEventBuilder) WithUserID(userID string) *WorkflowEventBuilder {
	b.event.UserID = userID
	b.metadata.UserID = userID
	return b
}

// WithType sets the event type
func (b *WorkflowEventBuilder) WithType(eventType EventType) *WorkflowEventBuilder {
	b.event.Type = eventType
	return b
}

// WithTitle sets the event title
func (b *WorkflowEventBuilder) WithTitle(title string) *WorkflowEventBuilder {
	b.event.Title = title
	return b
}

// WithDescription sets the event description
func (b *WorkflowEventBuilder) WithDescription(description string) *WorkflowEventBuilder {
	b.event.Description = description
	return b
}

// WithPriority sets the event priority
func (b *WorkflowEventBuilder) WithPriority(priority EventPriority) *WorkflowEventBuilder {
	b.event.Priority = priority
	return b
}

// WithStartTime sets the start time
func (b *WorkflowEventBuilder) WithStartTime(startTime time.Time) *WorkflowEventBuilder {
	b.event.StartTime = startTime
	return b
}

// WithEndTime sets the end time
func (b *WorkflowEventBuilder) WithEndTime(endTime time.Time) *WorkflowEventBuilder {
	b.event.EndTime = &endTime
	return b
}

// WithDuration sets the duration
func (b *WorkflowEventBuilder) WithDuration(duration time.Duration) *WorkflowEventBuilder {
	b.event.Duration = &duration
	return b
}

// WithCategory sets the event category
func (b *WorkflowEventBuilder) WithCategory(category WorkflowEventCategory) *WorkflowEventBuilder {
	b.metadata.Category = category
	return b
}

// WithSubCategory sets the event subcategory
func (b *WorkflowEventBuilder) WithSubCategory(subCategory WorkflowEventSubCategory) *WorkflowEventBuilder {
	b.metadata.SubCategory = subCategory
	return b
}

// WithWorkflowID sets the workflow ID
func (b *WorkflowEventBuilder) WithWorkflowID(workflowID string) *WorkflowEventBuilder {
	b.metadata.WorkflowID = workflowID
	return b
}

// WithSessionID sets the session ID
func (b *WorkflowEventBuilder) WithSessionID(sessionID string) *WorkflowEventBuilder {
	b.metadata.SessionID = sessionID
	b.metadata.CorrelationID = sessionID
	return b
}

// WithPhaseID sets the phase ID
func (b *WorkflowEventBuilder) WithPhaseID(phaseID string) *WorkflowEventBuilder {
	b.metadata.PhaseID = phaseID
	return b
}

// WithVersion sets the workflow version
func (b *WorkflowEventBuilder) WithVersion(version string) *WorkflowEventBuilder {
	b.metadata.Version = version
	return b
}

// WithEnvironment sets the environment
func (b *WorkflowEventBuilder) WithEnvironment(environment string) *WorkflowEventBuilder {
	b.metadata.Environment = environment
	return b
}

// WithProject sets the project
func (b *WorkflowEventBuilder) WithProject(project string) *WorkflowEventBuilder {
	b.metadata.Project = project
	return b
}

// WithPriority sets the workflow priority
func (b *WorkflowEventBuilder) WithWorkflowPriority(priority string) *WorkflowEventBuilder {
	b.metadata.Priority = priority
	return b
}

// WithMetrics sets the workflow metrics
func (b *WorkflowEventBuilder) WithMetrics(metrics *WorkflowMetrics) *WorkflowEventBuilder {
	b.metadata.Metrics = metrics
	return b
}

// WithParentEventID sets the parent event ID
func (b *WorkflowEventBuilder) WithParentEventID(parentEventID string) *WorkflowEventBuilder {
	b.metadata.ParentEventID = parentEventID
	return b
}

// WithTraceID sets the trace ID
func (b *WorkflowEventBuilder) WithTraceID(traceID string) *WorkflowEventBuilder {
	b.metadata.TraceID = traceID
	return b
}

// WithSuccessCriteria sets the success criteria
func (b *WorkflowEventBuilder) WithSuccessCriteria(criteria map[string]interface{}) *WorkflowEventBuilder {
	b.metadata.SuccessCriteria = criteria
	return b
}

// WithResults sets the results
func (b *WorkflowEventBuilder) WithResults(results map[string]interface{}) *WorkflowEventBuilder {
	b.metadata.Results = results
	return b
}

// WithInstructions sets the instructions
func (b *WorkflowEventBuilder) WithInstructions(instructions []string) *WorkflowEventBuilder {
	b.metadata.Instructions = instructions
	return b
}

// WithContext sets the context
func (b *WorkflowEventBuilder) WithContext(context map[string]interface{}) *WorkflowEventBuilder {
	b.metadata.Context = context
	return b
}

// WithExternalID sets the external ID
func (b *WorkflowEventBuilder) WithExternalID(externalID string) *WorkflowEventBuilder {
	b.metadata.ExternalID = externalID
	return b
}

// WithExternalSystem sets the external system
func (b *WorkflowEventBuilder) WithExternalSystem(externalSystem string) *WorkflowEventBuilder {
	b.metadata.ExternalSystem = externalSystem
	return b
}

// WithCustomField sets a custom field
func (b *WorkflowEventBuilder) WithCustomField(key string, value interface{}) *WorkflowEventBuilder {
	if b.metadata.Custom == nil {
		b.metadata.Custom = make(map[string]interface{})
	}
	b.metadata.Custom[key] = value
	return b
}

// WithIsActive sets the active status
func (b *WorkflowEventBuilder) WithIsActive(isActive bool) *WorkflowEventBuilder {
	b.event.IsActive = isActive
	return b
}

// WithIsCompleted sets the completed status
func (b *WorkflowEventBuilder) WithIsCompleted(isCompleted bool) *WorkflowEventBuilder {
	b.event.IsCompleted = isCompleted
	return b
}

// Build creates the final TimeEvent with metadata
func (b *WorkflowEventBuilder) Build() (*TimeEvent, error) {
	// Validate required fields
	if b.event.ID == "" {
		return nil, errors.New("event ID is required")
	}
	if b.event.UserID == "" {
		return nil, errors.New("user ID is required")
	}
	if b.metadata.WorkflowID == "" {
		return nil, errors.New("workflow ID is required")
	}
	if b.metadata.SessionID == "" {
		return nil, errors.New("session ID is required")
	}

	// Convert metadata to map (simplified approach without JSON marshaling)
	metadataMap := b.convertMetadataToMap()
	b.event.Metadata = metadataMap

	return b.event, nil
}

// convertMetadataToMap converts the metadata struct to a map without JSON marshaling
func (b *WorkflowEventBuilder) convertMetadataToMap() map[string]interface{} {
	metadataMap := make(map[string]interface{})

	// Core workflow information
	metadataMap["workflow_id"] = b.metadata.WorkflowID
	metadataMap["session_id"] = b.metadata.SessionID
	if b.metadata.PhaseID != "" {
		metadataMap["phase_id"] = b.metadata.PhaseID
	}
	if b.metadata.Version != "" {
		metadataMap["version"] = b.metadata.Version
	}

	// Event categorization
	metadataMap["category"] = string(b.metadata.Category)
	metadataMap["sub_category"] = string(b.metadata.SubCategory)

	// Execution context
	metadataMap["user_id"] = b.metadata.UserID
	if b.metadata.Environment != "" {
		metadataMap["environment"] = b.metadata.Environment
	}
	if b.metadata.Project != "" {
		metadataMap["project"] = b.metadata.Project
	}
	if b.metadata.Priority != "" {
		metadataMap["priority"] = b.metadata.Priority
	}

	// Performance metrics
	if b.metadata.Metrics != nil {
		metadataMap["metrics"] = b.metadata.Metrics
	}

	// Correlation and linking
	if b.metadata.ParentEventID != "" {
		metadataMap["parent_event_id"] = b.metadata.ParentEventID
	}
	metadataMap["correlation_id"] = b.metadata.CorrelationID
	if b.metadata.TraceID != "" {
		metadataMap["trace_id"] = b.metadata.TraceID
	}

	// Success criteria and results
	if b.metadata.SuccessCriteria != nil {
		metadataMap["success_criteria"] = b.metadata.SuccessCriteria
	}
	if b.metadata.Results != nil {
		metadataMap["results"] = b.metadata.Results
	}

	// Instructions and context
	if len(b.metadata.Instructions) > 0 {
		metadataMap["instructions"] = b.metadata.Instructions
	}
	if b.metadata.Context != nil {
		metadataMap["context"] = b.metadata.Context
	}

	// External system integration
	if b.metadata.ExternalID != "" {
		metadataMap["external_id"] = b.metadata.ExternalID
	}
	if b.metadata.ExternalSystem != "" {
		metadataMap["external_system"] = b.metadata.ExternalSystem
	}

	// Custom fields
	if b.metadata.Custom != nil {
		for key, value := range b.metadata.Custom {
			metadataMap[key] = value
		}
	}

	return metadataMap
}

// CreateWorkflowStartEvent creates a workflow start event with enhanced metadata
func CreateWorkflowStartEvent(workflowCtx *WorkflowContext, metadata map[string]interface{}) (*TimeEvent, error) {
	if workflowCtx == nil {
		return nil, errors.New("workflow context cannot be nil")
	}

	builder := NewWorkflowEventBuilder().
		WithID(fmt.Sprintf("workflow_start_%s_%d", workflowCtx.SessionID, time.Now().UnixNano())).
		WithUserID(workflowCtx.UserID).
		WithType(EventTypeMilestone).
		WithTitle(fmt.Sprintf("Start %s Workflow", workflowCtx.WorkflowID)).
		WithDescription(fmt.Sprintf("Begin execution of %s workflow", workflowCtx.WorkflowID)).
		WithPriority(PriorityHigh).
		WithStartTime(workflowCtx.StartTime).
		WithCategory(WorkflowEventCategoryExecution).
		WithSubCategory(WorkflowEventSubCategoryStart).
		WithWorkflowID(workflowCtx.WorkflowID).
		WithSessionID(workflowCtx.SessionID).
		WithVersion("1.0").
		WithIsActive(true).
		WithIsCompleted(false)

	// Add metadata fields
	if project, ok := metadata["project"].(string); ok {
		builder.WithProject(project)
	}
	if priority, ok := metadata["priority"].(string); ok {
		builder.WithWorkflowPriority(priority)
	}
	if environment, ok := metadata["environment"].(string); ok {
		builder.WithEnvironment(environment)
	}
	if externalID, ok := metadata["external_id"].(string); ok {
		builder.WithExternalID(externalID)
	}
	if externalSystem, ok := metadata["external_system"].(string); ok {
		builder.WithExternalSystem(externalSystem)
	}

	// Add custom fields
	for key, value := range metadata {
		switch key {
		case "project", "priority", "environment", "external_id", "external_system":
			// Already handled above
		default:
			builder.WithCustomField(key, value)
		}
	}

	return builder.Build()
}

// CreateWorkflowEndEvent creates a workflow end event with metrics
func CreateWorkflowEndEvent(workflowCtx *WorkflowContext, result interface{}, metrics *WorkflowMetrics) (*TimeEvent, error) {
	if workflowCtx == nil {
		return nil, errors.New("workflow context cannot be nil")
	}

	endTime := time.Now()
	duration := endTime.Sub(workflowCtx.StartTime)

	builder := NewWorkflowEventBuilder().
		WithID(fmt.Sprintf("workflow_end_%s_%d", workflowCtx.SessionID, time.Now().UnixNano())).
		WithUserID(workflowCtx.UserID).
		WithType(EventTypeMilestone).
		WithTitle(fmt.Sprintf("Complete %s Workflow", workflowCtx.WorkflowID)).
		WithDescription(fmt.Sprintf("Finish execution of %s workflow", workflowCtx.WorkflowID)).
		WithPriority(PriorityHigh).
		WithStartTime(workflowCtx.StartTime).
		WithEndTime(endTime).
		WithDuration(duration).
		WithCategory(WorkflowEventCategoryExecution).
		WithSubCategory(WorkflowEventSubCategoryEnd).
		WithWorkflowID(workflowCtx.WorkflowID).
		WithSessionID(workflowCtx.SessionID).
		WithVersion("1.0").
		WithIsActive(false).
		WithIsCompleted(true)

	if metrics != nil {
		builder.WithMetrics(metrics)
	}

	if result != nil {
		builder.WithResults(map[string]interface{}{
			"result": result,
		})
	}

	return builder.Build()
}

// CreatePhaseCompletionEvent creates a phase completion event with enhanced metadata
func CreatePhaseCompletionEvent(workflowCtx *WorkflowContext, phaseDef *WorkflowPhaseDef, phase *WorkflowPhase) (*TimeEvent, error) {
	// Validate inputs
	if workflowCtx == nil {
		return nil, errors.New("workflow context cannot be nil")
	}
	if phaseDef == nil {
		return nil, errors.New("phase definition cannot be nil")
	}
	if phase == nil {
		return nil, errors.New("phase cannot be nil")
	}
	if phaseDef.Duration <= 0 {
		return nil, fmt.Errorf("phase duration must be positive, got %d", phaseDef.Duration)
	}

	// Calculate end time safely
	endTime := phase.StartTime.Add(time.Duration(phaseDef.Duration) * time.Second)
	duration := endTime.Sub(phase.StartTime)

	builder := NewWorkflowEventBuilder().
		WithID(fmt.Sprintf("phase_complete_%s_%s", workflowCtx.SessionID, phaseDef.PhaseID)).
		WithUserID(workflowCtx.UserID).
		WithType(EventTypeMilestone).
		WithTitle(fmt.Sprintf("Complete %s", phaseDef.Name)).
		WithDescription(fmt.Sprintf("Complete the %s phase", phaseDef.Name)).
		WithPriority(PriorityHigh).
		WithStartTime(phase.StartTime).
		WithEndTime(endTime).
		WithDuration(duration).
		WithCategory(WorkflowEventCategoryPhase).
		WithSubCategory(WorkflowEventSubCategoryComplete).
		WithWorkflowID(workflowCtx.WorkflowID).
		WithSessionID(workflowCtx.SessionID).
		WithPhaseID(phaseDef.PhaseID).
		WithVersion("1.0").
		WithIsActive(true).
		WithIsCompleted(false)

	// Add success criteria
	if phaseDef.SuccessCriteria != nil {
		builder.WithSuccessCriteria(phaseDef.SuccessCriteria)
	}

	// Add instructions if available
	if instructions, ok := phaseDef.Metadata["instructions"].([]string); ok {
		builder.WithInstructions(instructions)
	}

	// Add phase context
	phaseContext := map[string]interface{}{
		"phase_type":      phaseDef.Type,
		"target_duration": phaseDef.Duration,
		"min_duration":    phaseDef.MinDuration,
		"max_duration":    phaseDef.MaxDuration,
	}
	builder.WithContext(phaseContext)

	return builder.Build()
}

// CreateWorkflowPauseEvent creates a workflow pause event
func CreateWorkflowPauseEvent(workflowCtx *WorkflowContext, reason string) (*TimeEvent, error) {
	if workflowCtx == nil {
		return nil, errors.New("workflow context cannot be nil")
	}

	builder := NewWorkflowEventBuilder().
		WithID(fmt.Sprintf("workflow_pause_%s_%d", workflowCtx.SessionID, time.Now().UnixNano())).
		WithUserID(workflowCtx.UserID).
		WithType(EventTypeMilestone).
		WithTitle(fmt.Sprintf("Pause %s Workflow", workflowCtx.WorkflowID)).
		WithDescription(fmt.Sprintf("Pause execution of %s workflow: %s", workflowCtx.WorkflowID, reason)).
		WithPriority(PriorityMedium).
		WithStartTime(time.Now()).
		WithCategory(WorkflowEventCategoryExecution).
		WithSubCategory(WorkflowEventSubCategoryPause).
		WithWorkflowID(workflowCtx.WorkflowID).
		WithSessionID(workflowCtx.SessionID).
		WithVersion("1.0").
		WithIsActive(false).
		WithIsCompleted(false)

	if reason != "" {
		builder.WithCustomField("pause_reason", reason)
	}

	return builder.Build()
}

// CreateWorkflowResumeEvent creates a workflow resume event
func CreateWorkflowResumeEvent(workflowCtx *WorkflowContext) (*TimeEvent, error) {
	if workflowCtx == nil {
		return nil, errors.New("workflow context cannot be nil")
	}

	builder := NewWorkflowEventBuilder().
		WithID(fmt.Sprintf("workflow_resume_%s_%d", workflowCtx.SessionID, time.Now().UnixNano())).
		WithUserID(workflowCtx.UserID).
		WithType(EventTypeMilestone).
		WithTitle(fmt.Sprintf("Resume %s Workflow", workflowCtx.WorkflowID)).
		WithDescription(fmt.Sprintf("Resume execution of %s workflow", workflowCtx.WorkflowID)).
		WithPriority(PriorityMedium).
		WithStartTime(time.Now()).
		WithCategory(WorkflowEventCategoryExecution).
		WithSubCategory(WorkflowEventSubCategoryResume).
		WithWorkflowID(workflowCtx.WorkflowID).
		WithSessionID(workflowCtx.SessionID).
		WithVersion("1.0").
		WithIsActive(true).
		WithIsCompleted(false)

	return builder.Build()
}

// CreateWorkflowErrorEvent creates a workflow error event
func CreateWorkflowErrorEvent(workflowCtx *WorkflowContext, phaseID string, error error) (*TimeEvent, error) {
	if workflowCtx == nil {
		return nil, errors.New("workflow context cannot be nil")
	}

	builder := NewWorkflowEventBuilder().
		WithID(fmt.Sprintf("workflow_error_%s_%d", workflowCtx.SessionID, time.Now().UnixNano())).
		WithUserID(workflowCtx.UserID).
		WithType(EventTypeMilestone).
		WithTitle(fmt.Sprintf("Error in %s Workflow", workflowCtx.WorkflowID)).
		WithDescription(fmt.Sprintf("Error occurred in %s workflow: %v", workflowCtx.WorkflowID, error)).
		WithPriority(PriorityUrgent).
		WithStartTime(time.Now()).
		WithCategory(WorkflowEventCategoryError).
		WithSubCategory(WorkflowEventSubCategoryFail).
		WithWorkflowID(workflowCtx.WorkflowID).
		WithSessionID(workflowCtx.SessionID).
		WithVersion("1.0").
		WithIsActive(false).
		WithIsCompleted(false)

	if phaseID != "" {
		builder.WithPhaseID(phaseID)
	}

	builder.WithCustomField("error_message", error.Error())
	builder.WithCustomField("error_type", fmt.Sprintf("%T", error))

	return builder.Build()
}

// WorkflowEventReplay provides event replay capabilities
type WorkflowEventReplay struct {
	events []*TimeEvent
	db     *sqlx.DB
}

// NewWorkflowEventReplay creates a new event replay system
func NewWorkflowEventReplay(db *sqlx.DB) *WorkflowEventReplay {
	return &WorkflowEventReplay{
		events: make([]*TimeEvent, 0),
		db:     db,
	}
}

// AddEvent adds an event to the replay system
func (wer *WorkflowEventReplay) AddEvent(event *TimeEvent) {
	wer.events = append(wer.events, event)
}

// ReplayEvents replays events in chronological order
func (wer *WorkflowEventReplay) ReplayEvents(ctx context.Context, sessionID string) error {
	// Filter events by session ID
	var sessionEvents []*TimeEvent
	for _, event := range wer.events {
		if correlationID, ok := event.Metadata["correlation_id"].(string); ok && correlationID == sessionID {
			sessionEvents = append(sessionEvents, event)
		}
	}

	// Sort events by timestamp
	// (In a real implementation, you'd sort by CreatedAt or StartTime)

	log.Printf("Replaying %d events for session %s", len(sessionEvents), sessionID)

	for _, event := range sessionEvents {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			log.Printf("Replaying event: %s - %s", event.ID, event.Title)
			// In a real implementation, you'd execute the event logic here
		}
	}

	return nil
}

// GetEventSummary provides a summary of events for a session
func (wer *WorkflowEventReplay) GetEventSummary(sessionID string) map[string]interface{} {
	var sessionEvents []*TimeEvent
	for _, event := range wer.events {
		if correlationID, ok := event.Metadata["correlation_id"].(string); ok && correlationID == sessionID {
			sessionEvents = append(sessionEvents, event)
		}
	}

	summary := map[string]interface{}{
		"session_id":    sessionID,
		"total_events":  len(sessionEvents),
		"event_types":   make(map[string]int),
		"categories":    make(map[string]int),
		"subcategories": make(map[string]int),
		"duration":      0,
	}

	var startTime, endTime time.Time
	firstEvent := true

	for _, event := range sessionEvents {
		// Count event types
		eventType := string(event.Type)
		summary["event_types"].(map[string]int)[eventType]++

		// Count categories
		if category, ok := event.Metadata["category"].(string); ok {
			summary["categories"].(map[string]int)[category]++
		}

		// Count subcategories
		if subCategory, ok := event.Metadata["sub_category"].(string); ok {
			summary["subcategories"].(map[string]int)[subCategory]++
		}

		// Calculate duration
		if firstEvent {
			startTime = event.StartTime
			firstEvent = false
		}
		endTime = event.StartTime
	}

	if !firstEvent {
		summary["duration"] = endTime.Sub(startTime).Seconds()
	}

	return summary
}
