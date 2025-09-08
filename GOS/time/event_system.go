package time

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"
)

// EventType represents the type of time event
type EventType string

const (
	EventTypeTimer     EventType = "timer"
	EventTypeReminder  EventType = "reminder"
	EventTypeDeadline  EventType = "deadline"
	EventTypeMilestone EventType = "milestone"
	EventTypeBreak     EventType = "break"
	EventTypeFocus     EventType = "focus"
)

// EventPriority represents the priority of an event
type EventPriority int

const (
	PriorityLow      EventPriority = 1
	PriorityMedium   EventPriority = 2
	PriorityHigh     EventPriority = 3
	PriorityUrgent   EventPriority = 4
	PriorityCritical EventPriority = 5
)

// TimeEvent represents a time-based event
type TimeEvent struct {
	ID          string                 `json:"id"`
	UserID      string                 `json:"user_id"`
	Type        EventType              `json:"type"`
	Title       string                 `json:"title"`
	Description string                 `json:"description"`
	Priority    EventPriority          `json:"priority"`
	StartTime   time.Time              `json:"start_time"`
	EndTime     *time.Time             `json:"end_time,omitempty"`
	Duration    *time.Duration         `json:"duration,omitempty"`
	IsRecurring bool                   `json:"is_recurring"`
	Recurrence  *RecurrenceRule        `json:"recurrence,omitempty"`
	IsActive    bool                   `json:"is_active"`
	IsCompleted bool                   `json:"is_completed"`
	Metadata    map[string]interface{} `json:"metadata"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
}

// RecurrenceRule defines how an event recurs
type RecurrenceRule struct {
	Frequency   string     `json:"frequency"`               // daily, weekly, monthly, yearly
	Interval    int        `json:"interval"`                // every N frequency units
	DaysOfWeek  []int      `json:"days_of_week,omitempty"`  // 0-6 (Sunday = 0)
	DaysOfMonth []int      `json:"days_of_month,omitempty"` // 1-31
	EndDate     *time.Time `json:"end_date,omitempty"`
	Count       *int       `json:"count,omitempty"` // number of occurrences
}

// EventHandler represents a function that handles time events
type EventHandler func(context.Context, *TimeEvent) error

// EventSystem manages time-based events
type EventSystem struct {
	events        map[string]*TimeEvent
	handlers      map[EventType][]EventHandler
	eventsMutex   sync.RWMutex
	handlersMutex sync.RWMutex
	stopChan      chan struct{}
	isRunning     bool
	runningMutex  sync.RWMutex
}

// NewEventSystem creates a new event system
func NewEventSystem() *EventSystem {
	return &EventSystem{
		events:   make(map[string]*TimeEvent),
		handlers: make(map[EventType][]EventHandler),
		stopChan: make(chan struct{}),
	}
}

// RegisterHandler registers an event handler for a specific event type
func (es *EventSystem) RegisterHandler(eventType EventType, handler EventHandler) {
	es.handlersMutex.Lock()
	defer es.handlersMutex.Unlock()

	es.handlers[eventType] = append(es.handlers[eventType], handler)
}

// AddEvent adds a new time event
func (es *EventSystem) AddEvent(event *TimeEvent) error {
	event.CreatedAt = time.Now().UTC()
	event.UpdatedAt = time.Now().UTC()

	// Calculate end time if duration is provided
	if event.Duration != nil && event.EndTime == nil {
		endTime := event.StartTime.Add(*event.Duration)
		event.EndTime = &endTime
	}

	// Generate recurring events if needed
	if event.IsRecurring && event.Recurrence != nil {
		recurringEvents, err := es.generateRecurringEvents(event)
		if err != nil {
			return err
		}

		es.eventsMutex.Lock()
		for _, recurringEvent := range recurringEvents {
			es.events[recurringEvent.ID] = recurringEvent
		}
		es.eventsMutex.Unlock()
	} else {
		es.eventsMutex.Lock()
		es.events[event.ID] = event
		es.eventsMutex.Unlock()
	}

	log.Printf("Added time event: %s (%s)", event.Title, event.Type)
	return nil
}

// generateRecurringEvents generates recurring events based on recurrence rules
func (es *EventSystem) generateRecurringEvents(baseEvent *TimeEvent) ([]*TimeEvent, error) {
	var events []*TimeEvent

	rule := baseEvent.Recurrence
	currentTime := baseEvent.StartTime
	count := 0
	maxCount := 100 // Prevent infinite loops

	if rule.Count != nil {
		maxCount = *rule.Count
	}

	for count < maxCount {
		// Check if we've exceeded the end date
		if rule.EndDate != nil && currentTime.After(*rule.EndDate) {
			break
		}

		// Create a new event instance
		event := &TimeEvent{
			ID:          fmt.Sprintf("%s_%d", baseEvent.ID, count),
			UserID:      baseEvent.UserID,
			Type:        baseEvent.Type,
			Title:       baseEvent.Title,
			Description: baseEvent.Description,
			Priority:    baseEvent.Priority,
			StartTime:   currentTime,
			Duration:    baseEvent.Duration,
			IsRecurring: false, // Individual instances are not recurring
			IsActive:    baseEvent.IsActive,
			IsCompleted: false,
			Metadata:    baseEvent.Metadata,
			CreatedAt:   time.Now().UTC(),
			UpdatedAt:   time.Now().UTC(),
		}

		// Calculate end time
		if event.Duration != nil {
			endTime := event.StartTime.Add(*event.Duration)
			event.EndTime = &endTime
		}

		events = append(events, event)
		count++

		// Calculate next occurrence
		nextTime, err := es.calculateNextOccurrence(currentTime, rule)
		if err != nil {
			return events, err
		}

		if nextTime.Equal(currentTime) {
			break // No more occurrences
		}

		currentTime = nextTime
	}

	return events, nil
}

// calculateNextOccurrence calculates the next occurrence time
func (es *EventSystem) calculateNextOccurrence(current time.Time, rule *RecurrenceRule) (time.Time, error) {
	switch rule.Frequency {
	case "daily":
		return current.AddDate(0, 0, rule.Interval), nil
	case "weekly":
		return current.AddDate(0, 0, 7*rule.Interval), nil
	case "monthly":
		return current.AddDate(0, rule.Interval, 0), nil
	case "yearly":
		return current.AddDate(rule.Interval, 0, 0), nil
	default:
		return current, fmt.Errorf("unsupported frequency: %s", rule.Frequency)
	}
}

// Start starts the event system
func (es *EventSystem) Start(ctx context.Context) {
	es.runningMutex.Lock()
	if es.isRunning {
		es.runningMutex.Unlock()
		return
	}
	es.isRunning = true
	es.runningMutex.Unlock()

	log.Println("Starting time event system...")

	ticker := time.NewTicker(time.Second) // Check every second
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("Event system stopped by context")
			return
		case <-es.stopChan:
			log.Println("Event system stopped")
			return
		case <-ticker.C:
			es.processEvents(ctx)
		}
	}
}

// processEvents processes events that are due
func (es *EventSystem) processEvents(ctx context.Context) {
	now := time.Now().UTC()

	es.eventsMutex.RLock()
	var dueEvents []*TimeEvent
	for _, event := range es.events {
		if event.IsActive && !event.IsCompleted {
			// Check if event should trigger
			if es.shouldTriggerEvent(event, now) {
				dueEvents = append(dueEvents, event)
			}
		}
	}
	es.eventsMutex.RUnlock()

	// Process due events
	for _, event := range dueEvents {
		go es.handleEvent(ctx, event)
	}
}

// shouldTriggerEvent determines if an event should trigger
func (es *EventSystem) shouldTriggerEvent(event *TimeEvent, now time.Time) bool {
	// Check if event has started
	if now.Before(event.StartTime) {
		return false
	}

	// Check if event has ended
	if event.EndTime != nil && now.After(*event.EndTime) {
		return false
	}

	// For timer events, check if duration has elapsed
	if event.Type == EventTypeTimer && event.Duration != nil {
		elapsed := now.Sub(event.StartTime)
		return elapsed >= *event.Duration
	}

	// For reminder events, check if it's time to remind
	if event.Type == EventTypeReminder {
		// Check if we're within the reminder window (e.g., 5 minutes before end)
		if event.EndTime != nil {
			reminderTime := event.EndTime.Add(-5 * time.Minute)
			return now.After(reminderTime) && now.Before(*event.EndTime)
		}
	}

	// For deadline events, check if deadline is approaching
	if event.Type == EventTypeDeadline && event.EndTime != nil {
		timeUntilDeadline := event.EndTime.Sub(now)
		// Trigger if deadline is within 1 hour
		return timeUntilDeadline <= time.Hour && timeUntilDeadline > 0
	}

	// For milestone events, check if milestone time has been reached
	if event.Type == EventTypeMilestone {
		return now.After(event.StartTime) && (event.EndTime == nil || now.Before(*event.EndTime))
	}

	// For break events, check if break time has started
	if event.Type == EventTypeBreak {
		return now.After(event.StartTime) && (event.EndTime == nil || now.Before(*event.EndTime))
	}

	// For focus events, check if focus time has started
	if event.Type == EventTypeFocus {
		return now.After(event.StartTime) && (event.EndTime == nil || now.Before(*event.EndTime))
	}

	return false
}

// handleEvent handles a triggered event
func (es *EventSystem) handleEvent(ctx context.Context, event *TimeEvent) {
	log.Printf("Handling event: %s (%s)", event.Title, event.Type)

	es.handlersMutex.RLock()
	handlers := es.handlers[event.Type]
	es.handlersMutex.RUnlock()

	// Execute all registered handlers
	for _, handler := range handlers {
		if err := handler(ctx, event); err != nil {
			log.Printf("Error handling event %s: %v", event.ID, err)
		}
	}

	// Mark event as completed if it's a one-time event
	if !event.IsRecurring {
		es.eventsMutex.Lock()
		if storedEvent, exists := es.events[event.ID]; exists {
			storedEvent.IsCompleted = true
			storedEvent.UpdatedAt = time.Now().UTC()
		}
		es.eventsMutex.Unlock()
	}
}

// GetEvent retrieves an event by ID
func (es *EventSystem) GetEvent(id string) (*TimeEvent, bool) {
	es.eventsMutex.RLock()
	defer es.eventsMutex.RUnlock()

	event, exists := es.events[id]
	return event, exists
}

// GetEventsByUser retrieves all events for a user
func (es *EventSystem) GetEventsByUser(userID string) []*TimeEvent {
	es.eventsMutex.RLock()
	defer es.eventsMutex.RUnlock()

	var userEvents []*TimeEvent
	for _, event := range es.events {
		if event.UserID == userID {
			userEvents = append(userEvents, event)
		}
	}

	return userEvents
}

// GetEventsByType retrieves all events of a specific type
func (es *EventSystem) GetEventsByType(eventType EventType) []*TimeEvent {
	es.eventsMutex.RLock()
	defer es.eventsMutex.RUnlock()

	var typeEvents []*TimeEvent
	for _, event := range es.events {
		if event.Type == eventType {
			typeEvents = append(typeEvents, event)
		}
	}

	return typeEvents
}

// GetUpcomingEvents retrieves events that are upcoming within a specified duration
func (es *EventSystem) GetUpcomingEvents(userID string, within time.Duration) []*TimeEvent {
	es.eventsMutex.RLock()
	defer es.eventsMutex.RUnlock()

	now := time.Now().UTC()
	cutoff := now.Add(within)

	var upcomingEvents []*TimeEvent
	for _, event := range es.events {
		if event.UserID == userID && event.IsActive && !event.IsCompleted {
			if event.StartTime.After(now) && event.StartTime.Before(cutoff) {
				upcomingEvents = append(upcomingEvents, event)
			}
		}
	}

	return upcomingEvents
}

// UpdateEvent updates an existing event
func (es *EventSystem) UpdateEvent(id string, updates map[string]interface{}) error {
	es.eventsMutex.Lock()
	defer es.eventsMutex.Unlock()

	event, exists := es.events[id]
	if !exists {
		return fmt.Errorf("event %s not found", id)
	}

	// Update fields based on the updates map
	if title, ok := updates["title"].(string); ok {
		event.Title = title
	}
	if description, ok := updates["description"].(string); ok {
		event.Description = description
	}
	if priority, ok := updates["priority"].(EventPriority); ok {
		event.Priority = priority
	}
	if startTime, ok := updates["start_time"].(time.Time); ok {
		event.StartTime = startTime
	}
	if endTime, ok := updates["end_time"].(*time.Time); ok {
		event.EndTime = endTime
	}
	if duration, ok := updates["duration"].(*time.Duration); ok {
		event.Duration = duration
	}
	if isActive, ok := updates["is_active"].(bool); ok {
		event.IsActive = isActive
	}
	if isCompleted, ok := updates["is_completed"].(bool); ok {
		event.IsCompleted = isCompleted
	}

	event.UpdatedAt = time.Now().UTC()

	return nil
}

// DeleteEvent deletes an event
func (es *EventSystem) DeleteEvent(id string) bool {
	es.eventsMutex.Lock()
	defer es.eventsMutex.Unlock()

	_, exists := es.events[id]
	if exists {
		delete(es.events, id)
		log.Printf("Deleted event: %s", id)
	}

	return exists
}

// Stop stops the event system
func (es *EventSystem) Stop() {
	es.runningMutex.Lock()
	defer es.runningMutex.Unlock()

	if es.isRunning {
		close(es.stopChan)
		es.isRunning = false
	}
}

// GetEventStats returns statistics about events
func (es *EventSystem) GetEventStats() map[string]interface{} {
	es.eventsMutex.RLock()
	defer es.eventsMutex.RUnlock()

	stats := make(map[string]interface{})
	stats["total_events"] = len(es.events)

	// Count by type
	typeCounts := make(map[EventType]int)
	activeCount := 0
	completedCount := 0

	for _, event := range es.events {
		typeCounts[event.Type]++
		if event.IsActive {
			activeCount++
		}
		if event.IsCompleted {
			completedCount++
		}
	}

	stats["events_by_type"] = typeCounts
	stats["active_events"] = activeCount
	stats["completed_events"] = completedCount

	return stats
}

// ExportEvents exports all events to JSON
func (es *EventSystem) ExportEvents() ([]byte, error) {
	es.eventsMutex.RLock()
	defer es.eventsMutex.RUnlock()

	return json.MarshalIndent(es.events, "", "  ")
}
