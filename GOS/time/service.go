package time

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/jmoiron/sqlx"
)

// TimeService is the main service that integrates all time functionality
type TimeService struct {
	AdvancedTimeService *AdvancedTimeService
	AnalyticsService    *TimeAnalyticsService
	EventSystem         *EventSystem
	Scheduler           *Scheduler
	SyncService         *TimeSyncService
	db                  *sqlx.DB
}

// NewTimeService creates a new comprehensive time service
func NewTimeService(db *sqlx.DB) *TimeService {
	return &TimeService{
		AdvancedTimeService: NewAdvancedTimeService(db),
		AnalyticsService:    NewTimeAnalyticsService(db),
		EventSystem:         NewEventSystem(),
		Scheduler:           NewScheduler(),
		SyncService:         NewTimeSyncService(),
		db:                  db,
	}
}

// Initialize initializes the time service
func (ts *TimeService) Initialize() error {
	// Initialize database schema
	if err := ts.AdvancedTimeService.InitializeSchema(); err != nil {
		return err
	}

	// Register default event handlers
	ts.registerDefaultEventHandlers()

	log.Println("Time service initialized successfully")
	return nil
}

// registerDefaultEventHandlers registers default event handlers
func (ts *TimeService) registerDefaultEventHandlers() {
	// Timer event handler
	ts.EventSystem.RegisterHandler(EventTypeTimer, func(ctx context.Context, event *TimeEvent) error {
		log.Printf("Timer completed: %s", event.Title)
		return nil
	})

	// Reminder event handler
	ts.EventSystem.RegisterHandler(EventTypeReminder, func(ctx context.Context, event *TimeEvent) error {
		log.Printf("Reminder: %s", event.Title)
		return nil
	})

	// Deadline event handler
	ts.EventSystem.RegisterHandler(EventTypeDeadline, func(ctx context.Context, event *TimeEvent) error {
		log.Printf("Deadline approaching: %s", event.Title)
		return nil
	})

	// Break event handler
	ts.EventSystem.RegisterHandler(EventTypeBreak, func(ctx context.Context, event *TimeEvent) error {
		log.Printf("Break time: %s", event.Title)
		return nil
	})

	// Focus event handler
	ts.EventSystem.RegisterHandler(EventTypeFocus, func(ctx context.Context, event *TimeEvent) error {
		log.Printf("Focus time: %s", event.Title)
		return nil
	})
}

// Start starts all time service components
func (ts *TimeService) Start(ctx context.Context) {
	log.Println("Starting time service components...")

	// Start event system
	go ts.EventSystem.Start(ctx)

	// Start scheduler
	go ts.Scheduler.Start(ctx)

	// Start auto-sync (every hour)
	go ts.SyncService.StartAutoSync(ctx, time.Hour)

	// Start advanced time service event scheduler
	go ts.AdvancedTimeService.StartEventScheduler(ctx)

	log.Println("All time service components started")
}

// Stop stops all time service components
func (ts *TimeService) Stop() {
	log.Println("Stopping time service components...")

	ts.EventSystem.Stop()
	ts.Scheduler.Stop()
	ts.SyncService.Stop()
	ts.AdvancedTimeService.Stop()

	log.Println("All time service components stopped")
}

// GetCurrentTime returns the current time with drift correction
func (ts *TimeService) GetCurrentTime() time.Time {
	return ts.SyncService.CorrectTime()
}

// CreateTimeBlock creates a new time block
func (ts *TimeService) CreateTimeBlock(block *TimeBlock) error {
	return ts.AdvancedTimeService.CreateTimeBlock(block)
}

// GetTimeBlocks retrieves time blocks for a user within a date range
func (ts *TimeService) GetTimeBlocks(userID string, startDate, endDate time.Time) ([]*TimeBlock, error) {
	return ts.AdvancedTimeService.GetTimeBlocks(userID, startDate, endDate)
}

// GenerateTimeReport generates a comprehensive time report
func (ts *TimeService) GenerateTimeReport(userID, period string, startDate, endDate time.Time) (*TimeReport, error) {
	return ts.AnalyticsService.GenerateTimeReport(userID, period, startDate, endDate)
}

// AddScheduledJob adds a new scheduled job
func (ts *TimeService) AddScheduledJob(id, name, cronExpr string, handler func(context.Context) error) (*ScheduledJob, error) {
	return ts.Scheduler.AddJob(id, name, cronExpr, handler)
}

// AddTimeEvent adds a new time event
func (ts *TimeService) AddTimeEvent(event *TimeEvent) error {
	return ts.EventSystem.AddEvent(event)
}

// GetUpcomingEvents retrieves upcoming events for a user
func (ts *TimeService) GetUpcomingEvents(userID string, within time.Duration) []*TimeEvent {
	return ts.EventSystem.GetUpcomingEvents(userID, within)
}

// SyncTime synchronizes time with external servers
func (ts *TimeService) SyncTime(ctx context.Context) (*TimeSyncResult, error) {
	return ts.SyncService.SyncWithBestServer(ctx)
}

// GetSyncStatus returns the current synchronization status
func (ts *TimeService) GetSyncStatus() map[string]interface{} {
	return ts.SyncService.GetSyncStatus()
}

// GetTimeInsights returns insights about time usage patterns
func (ts *TimeService) GetTimeInsights(userID string, startDate, endDate time.Time) (map[string]interface{}, error) {
	return ts.AnalyticsService.GetTimeInsights(userID, startDate, endDate)
}

// GetProductivityScore calculates an overall productivity score
func (ts *TimeService) GetProductivityScore(userID string, startDate, endDate time.Time) (float64, error) {
	return ts.AnalyticsService.GetProductivityScore(userID, startDate, endDate)
}

// ConvertTime converts time between timezones
func (ts *TimeService) ConvertTime(t time.Time, fromTZ, toTZ string) (time.Time, error) {
	return ts.AdvancedTimeService.ConvertTime(t, fromTZ, toTZ)
}

// CreateTimeEvent creates a new time-based event
func (ts *TimeService) CreateTimeEvent(event *TimeEvent) error {
	return ts.EventSystem.AddEvent(event)
}

// CreateScheduledTimeEvent creates a new scheduled time-based event
func (ts *TimeService) CreateScheduledTimeEvent(event *ScheduledTimeEvent) error {
	return ts.AdvancedTimeService.CreateTimeEvent(event)
}

// GetTimeAnalytics retrieves time analytics for a user within a date range
func (ts *TimeService) GetTimeAnalytics(userID string, startDate, endDate time.Time) ([]*TimeAnalytics, error) {
	return ts.AdvancedTimeService.GetTimeAnalytics(userID, startDate, endDate)
}

// SaveTimeAnalytics saves time analytics to the database
func (ts *TimeService) SaveTimeAnalytics(analytics *TimeAnalytics) error {
	return ts.AdvancedTimeService.SaveTimeAnalytics(analytics)
}

// GetServiceStatus returns the status of all time service components
func (ts *TimeService) GetServiceStatus() map[string]interface{} {
	status := make(map[string]interface{})

	// Event system status
	eventStats := ts.EventSystem.GetEventStats()
	status["event_system"] = eventStats

	// Scheduler status
	schedulerJobs := ts.Scheduler.ListJobs()
	status["scheduler"] = map[string]interface{}{
		"total_jobs": len(schedulerJobs),
		"active_jobs": func() int {
			count := 0
			for _, job := range schedulerJobs {
				if job.IsActive {
					count++
				}
			}
			return count
		}(),
	}

	// Sync service status
	syncStatus := ts.SyncService.GetSyncStatus()
	status["sync_service"] = syncStatus

	// Database status
	dbStatus := make(map[string]interface{})
	if err := ts.db.Ping(); err != nil {
		dbStatus["status"] = "disconnected"
		dbStatus["error"] = err.Error()
	} else {
		dbStatus["status"] = "connected"
	}
	status["database"] = dbStatus

	// Overall service health
	status["service_health"] = "healthy"
	status["timestamp"] = ts.GetCurrentTime()

	return status
}

// ExportAllData exports all time service data
func (ts *TimeService) ExportAllData() (map[string]interface{}, error) {
	data := make(map[string]interface{})

	// Export events
	eventsData, err := ts.EventSystem.ExportEvents()
	if err != nil {
		return nil, err
	}
	data["events"] = string(eventsData)

	// Export sync data
	syncData, err := ts.SyncService.ExportSyncData()
	if err != nil {
		return nil, err
	}
	data["sync_data"] = string(syncData)

	// Export service status
	data["service_status"] = ts.GetServiceStatus()

	return data, nil
}

// ValidateTimeAccuracy validates the accuracy of the current time
func (ts *TimeService) ValidateTimeAccuracy() (bool, float64) {
	return ts.SyncService.ValidateTimeAccuracy()
}

// GetDriftEstimate estimates the current time drift
func (ts *TimeService) GetDriftEstimate() (int64, float64) {
	return ts.SyncService.GetDriftEstimate()
}

// CreatePomodoroTimer creates a Pomodoro timer (25 minutes work, 5 minutes break)
func (ts *TimeService) CreatePomodoroTimer(userID string, cycles int) error {
	now := ts.GetCurrentTime()

	for i := 0; i < cycles; i++ {
		// Work period (25 minutes)
		workStart := now.Add(time.Duration(i*30) * time.Minute)
		workEnd := workStart.Add(25 * time.Minute)

		workEvent := &TimeEvent{
			ID:          fmt.Sprintf("pomodoro_work_%d_%d", i, now.Unix()),
			UserID:      userID,
			Type:        EventTypeFocus,
			Title:       fmt.Sprintf("Pomodoro Work Session %d", i+1),
			Description: "25-minute focused work session",
			Priority:    PriorityHigh,
			StartTime:   workStart,
			EndTime:     &workEnd,
			IsActive:    true,
			IsCompleted: false,
			Metadata: map[string]interface{}{
				"pomodoro_cycle": i + 1,
				"session_type":   "work",
			},
		}

		if err := ts.AddTimeEvent(workEvent); err != nil {
			return err
		}

		// Break period (5 minutes)
		breakStart := workEnd
		breakEnd := breakStart.Add(5 * time.Minute)

		breakEvent := &TimeEvent{
			ID:          fmt.Sprintf("pomodoro_break_%d_%d", i, now.Unix()),
			UserID:      userID,
			Type:        EventTypeBreak,
			Title:       fmt.Sprintf("Pomodoro Break %d", i+1),
			Description: "5-minute break",
			Priority:    PriorityMedium,
			StartTime:   breakStart,
			EndTime:     &breakEnd,
			IsActive:    true,
			IsCompleted: false,
			Metadata: map[string]interface{}{
				"pomodoro_cycle": i + 1,
				"session_type":   "break",
			},
		}

		if err := ts.AddTimeEvent(breakEvent); err != nil {
			return err
		}
	}

	return nil
}

// CreateDailySchedule creates a daily schedule with time blocks
func (ts *TimeService) CreateDailySchedule(userID string, date time.Time, blocks []TimeBlock) error {
	startOfDay := time.Date(date.Year(), date.Month(), date.Day(), 0, 0, 0, 0, date.Location())

	for i, block := range blocks {
		block.ID = fmt.Sprintf("daily_%s_%d_%d", userID, startOfDay.Unix(), i)
		block.UserID = userID
		block.StartTime = startOfDay.Add(time.Duration(block.StartTime.Hour()*60+block.StartTime.Minute()) * time.Minute)
		block.EndTime = startOfDay.Add(time.Duration(block.EndTime.Hour()*60+block.EndTime.Minute()) * time.Minute)
		block.CreatedAt = time.Now().UTC()
		block.UpdatedAt = time.Now().UTC()

		if err := ts.CreateTimeBlock(&block); err != nil {
			return err
		}
	}

	return nil
}
