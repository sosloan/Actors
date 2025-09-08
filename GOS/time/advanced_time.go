package time

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sort"
	"sync"
	"time"

	"github.com/jmoiron/sqlx"
)

// TimeZone represents a timezone with metadata
type TimeZone struct {
	Name        string    `json:"name" db:"name"`
	Offset      int       `json:"offset" db:"offset"` // seconds from UTC
	DisplayName string    `json:"display_name" db:"display_name"`
	IsActive    bool      `json:"is_active" db:"is_active"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

// ScheduledTimeEvent represents a scheduled time-based event
type ScheduledTimeEvent struct {
	ID          string                 `json:"id" db:"id"`
	Name        string                 `json:"name" db:"name"`
	Description string                 `json:"description" db:"description"`
	EventType   string                 `json:"event_type" db:"event_type"` // cron, interval, one-time
	Schedule    string                 `json:"schedule" db:"schedule"`     // cron expression or duration
	Timezone    string                 `json:"timezone" db:"timezone"`
	IsActive    bool                   `json:"is_active" db:"is_active"`
	LastRun     *time.Time             `json:"last_run" db:"last_run"`
	NextRun     *time.Time             `json:"next_run" db:"next_run"`
	Metadata    map[string]interface{} `json:"metadata" db:"metadata"`
	CreatedAt   time.Time              `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at" db:"updated_at"`
}

// TimeAnalytics represents time usage analytics
type TimeAnalytics struct {
	UserID           string    `json:"user_id" db:"user_id"`
	Date             time.Time `json:"date" db:"date"`
	TotalTime        int       `json:"total_time" db:"total_time"`             // seconds
	ProductiveTime   int       `json:"productive_time" db:"productive_time"`   // seconds
	BreakTime        int       `json:"break_time" db:"break_time"`             // seconds
	FocusScore       float64   `json:"focus_score" db:"focus_score"`           // 0.0 to 1.0
	EfficiencyScore  float64   `json:"efficiency_score" db:"efficiency_score"` // 0.0 to 1.0
	PeakHours        []int     `json:"peak_hours" db:"peak_hours"`             // hours of day (0-23)
	DistractionCount int       `json:"distraction_count" db:"distraction_count"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
}

// TimeBlock represents a focused time block
type TimeBlock struct {
	ID          string    `json:"id" db:"id"`
	UserID      string    `json:"user_id" db:"user_id"`
	Title       string    `json:"title" db:"title"`
	Description string    `json:"description" db:"description"`
	StartTime   time.Time `json:"start_time" db:"start_time"`
	EndTime     time.Time `json:"end_time" db:"end_time"`
	Duration    int       `json:"duration" db:"duration"` // seconds
	Category    string    `json:"category" db:"category"`
	Priority    int       `json:"priority" db:"priority"` // 1-5
	IsCompleted bool      `json:"is_completed" db:"is_completed"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// AdvancedTimeService provides comprehensive time management
type AdvancedTimeService struct {
	db            *sqlx.DB
	events        map[string]*ScheduledTimeEvent
	eventMutex    sync.RWMutex
	timezones     map[string]*TimeZone
	timezoneMutex sync.RWMutex
	stopChan      chan struct{}
}

// NewAdvancedTimeService creates a new advanced time service
func NewAdvancedTimeService(db *sqlx.DB) *AdvancedTimeService {
	service := &AdvancedTimeService{
		db:        db,
		events:    make(map[string]*ScheduledTimeEvent),
		timezones: make(map[string]*TimeZone),
		stopChan:  make(chan struct{}),
	}

	// Initialize default timezones
	service.initializeDefaultTimezones()

	return service
}

// InitializeSchema creates the necessary database tables
func (s *AdvancedTimeService) InitializeSchema() error {
	schema := `
	-- Time zones table
	CREATE TABLE IF NOT EXISTS time_zones (
		name TEXT PRIMARY KEY,
		offset INTEGER NOT NULL,
		display_name TEXT NOT NULL,
		is_active BOOLEAN DEFAULT true,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Time events table
	CREATE TABLE IF NOT EXISTS time_events (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		description TEXT,
		event_type TEXT NOT NULL,
		schedule TEXT NOT NULL,
		timezone TEXT NOT NULL,
		is_active BOOLEAN DEFAULT true,
		last_run TIMESTAMP,
		next_run TIMESTAMP,
		metadata TEXT,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Time analytics table
	CREATE TABLE IF NOT EXISTS time_analytics (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		user_id TEXT NOT NULL,
		date DATE NOT NULL,
		total_time INTEGER DEFAULT 0,
		productive_time INTEGER DEFAULT 0,
		break_time INTEGER DEFAULT 0,
		focus_score REAL DEFAULT 0.0,
		efficiency_score REAL DEFAULT 0.0,
		peak_hours TEXT,
		distraction_count INTEGER DEFAULT 0,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		UNIQUE(user_id, date)
	);

	-- Time blocks table
	CREATE TABLE IF NOT EXISTS time_blocks (
		id TEXT PRIMARY KEY,
		user_id TEXT NOT NULL,
		title TEXT NOT NULL,
		description TEXT,
		start_time TIMESTAMP NOT NULL,
		end_time TIMESTAMP NOT NULL,
		duration INTEGER NOT NULL,
		category TEXT,
		priority INTEGER DEFAULT 3,
		is_completed BOOLEAN DEFAULT false,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Indexes
	CREATE INDEX IF NOT EXISTS idx_time_events_next_run ON time_events(next_run);
	CREATE INDEX IF NOT EXISTS idx_time_analytics_user_date ON time_analytics(user_id, date);
	CREATE INDEX IF NOT EXISTS idx_time_blocks_user ON time_blocks(user_id);
	CREATE INDEX IF NOT EXISTS idx_time_blocks_start_time ON time_blocks(start_time);

	-- Triggers
	CREATE TRIGGER IF NOT EXISTS update_time_events_timestamp
	AFTER UPDATE ON time_events
	BEGIN
		UPDATE time_events SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
	END;

	CREATE TRIGGER IF NOT EXISTS update_time_blocks_timestamp
	AFTER UPDATE ON time_blocks
	BEGIN
		UPDATE time_blocks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
	END;`

	_, err := s.db.Exec(schema)
	return err
}

// initializeDefaultTimezones sets up common timezones
func (s *AdvancedTimeService) initializeDefaultTimezones() {
	defaultTimezones := []*TimeZone{
		{Name: "UTC", Offset: 0, DisplayName: "Coordinated Universal Time", IsActive: true},
		{Name: "PST", Offset: -8 * 3600, DisplayName: "Pacific Standard Time", IsActive: true},
		{Name: "PDT", Offset: -7 * 3600, DisplayName: "Pacific Daylight Time", IsActive: true},
		{Name: "EST", Offset: -5 * 3600, DisplayName: "Eastern Standard Time", IsActive: true},
		{Name: "EDT", Offset: -4 * 3600, DisplayName: "Eastern Daylight Time", IsActive: true},
		{Name: "CET", Offset: 1 * 3600, DisplayName: "Central European Time", IsActive: true},
		{Name: "JST", Offset: 9 * 3600, DisplayName: "Japan Standard Time", IsActive: true},
	}

	for _, tz := range defaultTimezones {
		s.timezoneMutex.Lock()
		s.timezones[tz.Name] = tz
		s.timezoneMutex.Unlock()
	}
}

// ConvertTime converts time between timezones
func (s *AdvancedTimeService) ConvertTime(t time.Time, fromTZ, toTZ string) (time.Time, error) {
	s.timezoneMutex.RLock()
	fromZone, fromExists := s.timezones[fromTZ]
	toZone, toExists := s.timezones[toTZ]
	s.timezoneMutex.RUnlock()

	if !fromExists {
		return time.Time{}, fmt.Errorf("source timezone %s not found", fromTZ)
	}
	if !toExists {
		return time.Time{}, fmt.Errorf("destination timezone %s not found", toTZ)
	}

	// Convert to UTC first
	utcTime := t.Add(-time.Duration(fromZone.Offset) * time.Second)

	// Convert to destination timezone
	resultTime := utcTime.Add(time.Duration(toZone.Offset) * time.Second)

	return resultTime, nil
}

// CreateTimeEvent creates a new time-based event
func (s *AdvancedTimeService) CreateTimeEvent(event *ScheduledTimeEvent) error {
	event.CreatedAt = time.Now().UTC()
	event.UpdatedAt = time.Now().UTC()

	// Calculate next run time
	if err := s.calculateNextRun(event); err != nil {
		return err
	}

	query := `
	INSERT INTO time_events 
	(id, name, description, event_type, schedule, timezone, is_active, next_run, metadata, created_at, updated_at)
	VALUES (:id, :name, :description, :event_type, :schedule, :timezone, :is_active, :next_run, :metadata, :created_at, :updated_at)`

	metadataJSON, _ := json.Marshal(event.Metadata)
	event.Metadata = map[string]interface{}{"json": string(metadataJSON)}

	_, err := s.db.NamedExec(query, event)
	if err != nil {
		return err
	}

	// Add to in-memory cache
	s.eventMutex.Lock()
	s.events[event.ID] = event
	s.eventMutex.Unlock()

	return nil
}

// calculateNextRun calculates the next run time for an event
func (s *AdvancedTimeService) calculateNextRun(event *ScheduledTimeEvent) error {
	now := time.Now().UTC()

	switch event.EventType {
	case "interval":
		duration, err := time.ParseDuration(event.Schedule)
		if err != nil {
			return err
		}
		event.NextRun = &now
		*event.NextRun = event.NextRun.Add(duration)

	case "one-time":
		// Parse the schedule as a specific time
		scheduledTime, err := time.Parse(time.RFC3339, event.Schedule)
		if err != nil {
			return err
		}
		event.NextRun = &scheduledTime

	case "cron":
		// For now, implement simple cron-like scheduling
		// In a full implementation, you'd use a proper cron parser
		event.NextRun = &now
		*event.NextRun = event.NextRun.Add(time.Hour) // Default to hourly

	default:
		return fmt.Errorf("unsupported event type: %s", event.EventType)
	}

	return nil
}

// StartEventScheduler starts the background event scheduler
func (s *AdvancedTimeService) StartEventScheduler(ctx context.Context) {
	ticker := time.NewTicker(time.Minute) // Check every minute
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-s.stopChan:
			return
		case <-ticker.C:
			s.processScheduledEvents()
		}
	}
}

// processScheduledEvents processes events that are due to run
func (s *AdvancedTimeService) processScheduledEvents() {
	now := time.Now().UTC()

	query := `
	SELECT * FROM time_events 
	WHERE is_active = true AND next_run <= ? AND next_run IS NOT NULL`

	var events []ScheduledTimeEvent
	err := s.db.Select(&events, query, now)
	if err != nil {
		log.Printf("Error querying scheduled events: %v", err)
		return
	}

	for _, event := range events {
		s.executeEvent(&event)
	}
}

// executeEvent executes a time event
func (s *AdvancedTimeService) executeEvent(event *ScheduledTimeEvent) {
	log.Printf("Executing time event: %s", event.Name)

	// Update last run time
	now := time.Now().UTC()
	event.LastRun = &now

	// Calculate next run time
	if err := s.calculateNextRun(event); err != nil {
		log.Printf("Error calculating next run for event %s: %v", event.ID, err)
		return
	}

	// Update database
	query := `
	UPDATE time_events 
	SET last_run = ?, next_run = ?, updated_at = CURRENT_TIMESTAMP
	WHERE id = ?`

	_, err := s.db.Exec(query, event.LastRun, event.NextRun, event.ID)
	if err != nil {
		log.Printf("Error updating event %s: %v", event.ID, err)
		return
	}

	// Update in-memory cache
	s.eventMutex.Lock()
	s.events[event.ID] = event
	s.eventMutex.Unlock()
}

// CreateTimeBlock creates a new time block
func (s *AdvancedTimeService) CreateTimeBlock(block *TimeBlock) error {
	block.CreatedAt = time.Now().UTC()
	block.UpdatedAt = time.Now().UTC()
	block.Duration = int(block.EndTime.Sub(block.StartTime).Seconds())

	query := `
	INSERT INTO time_blocks 
	(id, user_id, title, description, start_time, end_time, duration, category, priority, is_completed, created_at, updated_at)
	VALUES (:id, :user_id, :title, :description, :start_time, :end_time, :duration, :category, :priority, :is_completed, :created_at, :updated_at)`

	_, err := s.db.NamedExec(query, block)
	return err
}

// GetTimeBlocks retrieves time blocks for a user within a date range
func (s *AdvancedTimeService) GetTimeBlocks(userID string, startDate, endDate time.Time) ([]*TimeBlock, error) {
	query := `
	SELECT * FROM time_blocks 
	WHERE user_id = ? AND start_time >= ? AND start_time <= ?
	ORDER BY start_time ASC`

	var blocks []*TimeBlock
	err := s.db.Select(&blocks, query, userID, startDate, endDate)
	return blocks, err
}

// CalculateTimeAnalytics calculates analytics for a user on a specific date
func (s *AdvancedTimeService) CalculateTimeAnalytics(userID string, date time.Time) (*TimeAnalytics, error) {
	startOfDay := time.Date(date.Year(), date.Month(), date.Day(), 0, 0, 0, 0, date.Location())
	endOfDay := startOfDay.Add(24 * time.Hour)

	// Get time blocks for the day
	blocks, err := s.GetTimeBlocks(userID, startOfDay, endOfDay)
	if err != nil {
		return nil, err
	}

	analytics := &TimeAnalytics{
		UserID:    userID,
		Date:      startOfDay,
		CreatedAt: time.Now().UTC(),
	}

	// Calculate metrics
	totalTime := 0
	productiveTime := 0
	hourlyActivity := make([]int, 24)

	for _, block := range blocks {
		totalTime += block.Duration

		// Categorize as productive or break time
		if block.Category == "work" || block.Category == "study" || block.Category == "focus" {
			productiveTime += block.Duration
		} else if block.Category == "break" || block.Category == "rest" {
			analytics.BreakTime += block.Duration
		}

		// Track hourly activity
		startHour := block.StartTime.Hour()
		endHour := block.EndTime.Hour()
		for hour := startHour; hour <= endHour; hour++ {
			hourlyActivity[hour]++
		}
	}

	analytics.TotalTime = totalTime
	analytics.ProductiveTime = productiveTime

	// Calculate focus score (productive time / total time)
	if totalTime > 0 {
		analytics.FocusScore = float64(productiveTime) / float64(totalTime)
	}

	// Calculate efficiency score (based on completed blocks)
	completedBlocks := 0
	for _, block := range blocks {
		if block.IsCompleted {
			completedBlocks++
		}
	}
	if len(blocks) > 0 {
		analytics.EfficiencyScore = float64(completedBlocks) / float64(len(blocks))
	}

	// Find peak hours (hours with most activity)
	analytics.PeakHours = s.findPeakHours(hourlyActivity)

	return analytics, nil
}

// findPeakHours finds the hours with the most activity
func (s *AdvancedTimeService) findPeakHours(hourlyActivity []int) []int {
	// Create a slice of hour indices with their activity counts
	type hourActivity struct {
		hour     int
		activity int
	}

	var hours []hourActivity
	for hour, activity := range hourlyActivity {
		hours = append(hours, hourActivity{hour, activity})
	}

	// Sort by activity (descending)
	sort.Slice(hours, func(i, j int) bool {
		return hours[i].activity > hours[j].activity
	})

	// Return top 3 peak hours
	peakHours := make([]int, 0, 3)
	for i := 0; i < 3 && i < len(hours); i++ {
		if hours[i].activity > 0 {
			peakHours = append(peakHours, hours[i].hour)
		}
	}

	return peakHours
}

// SaveTimeAnalytics saves time analytics to the database
func (s *AdvancedTimeService) SaveTimeAnalytics(analytics *TimeAnalytics) error {
	peakHoursJSON, _ := json.Marshal(analytics.PeakHours)

	query := `
	INSERT OR REPLACE INTO time_analytics 
	(user_id, date, total_time, productive_time, break_time, focus_score, efficiency_score, peak_hours, distraction_count, created_at)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		analytics.UserID,
		analytics.Date,
		analytics.TotalTime,
		analytics.ProductiveTime,
		analytics.BreakTime,
		analytics.FocusScore,
		analytics.EfficiencyScore,
		string(peakHoursJSON),
		analytics.DistractionCount,
		analytics.CreatedAt)

	return err
}

// GetTimeAnalytics retrieves time analytics for a user within a date range
func (s *AdvancedTimeService) GetTimeAnalytics(userID string, startDate, endDate time.Time) ([]*TimeAnalytics, error) {
	query := `
	SELECT * FROM time_analytics 
	WHERE user_id = ? AND date >= ? AND date <= ?
	ORDER BY date ASC`

	var analytics []*TimeAnalytics
	err := s.db.Select(&analytics, query, userID, startDate, endDate)

	// Parse peak_hours JSON for each analytics record
	for _, a := range analytics {
		if a.PeakHours == nil {
			a.PeakHours = []int{}
		}
	}

	return analytics, err
}

// Stop stops the time service
func (s *AdvancedTimeService) Stop() {
	close(s.stopChan)
}
