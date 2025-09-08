package time

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"strings"
	"sync"
	"time"
)

// CronExpression represents a parsed cron expression
type CronExpression struct {
	Minute     []int // 0-59
	Hour       []int // 0-23
	DayOfMonth []int // 1-31
	Month      []int // 1-12
	DayOfWeek  []int // 0-6 (Sunday = 0)
}

// Scheduler manages time-based job scheduling
type Scheduler struct {
	jobs         map[string]*ScheduledJob
	jobsMutex    sync.RWMutex
	stopChan     chan struct{}
	isRunning    bool
	runningMutex sync.RWMutex
}

// ScheduledJob represents a scheduled job
type ScheduledJob struct {
	ID           string
	Name         string
	CronExpr     *CronExpression
	NextRun      time.Time
	LastRun      *time.Time
	IsActive     bool
	Handler      func(context.Context) error
	ErrorHandler func(context.Context, error)
	Metadata     map[string]interface{}
	Mutex        sync.RWMutex
}

// NewScheduler creates a new scheduler
func NewScheduler() *Scheduler {
	return &Scheduler{
		jobs:     make(map[string]*ScheduledJob),
		stopChan: make(chan struct{}),
	}
}

// ParseCronExpression parses a cron expression string
func ParseCronExpression(expr string) (*CronExpression, error) {
	parts := strings.Fields(expr)
	if len(parts) != 5 {
		return nil, fmt.Errorf("cron expression must have 5 parts (minute hour day month weekday)")
	}

	cron := &CronExpression{}

	// Parse minute (0-59)
	minute, err := parseCronField(parts[0], 0, 59)
	if err != nil {
		return nil, fmt.Errorf("invalid minute field: %v", err)
	}
	cron.Minute = minute

	// Parse hour (0-23)
	hour, err := parseCronField(parts[1], 0, 23)
	if err != nil {
		return nil, fmt.Errorf("invalid hour field: %v", err)
	}
	cron.Hour = hour

	// Parse day of month (1-31)
	day, err := parseCronField(parts[2], 1, 31)
	if err != nil {
		return nil, fmt.Errorf("invalid day field: %v", err)
	}
	cron.DayOfMonth = day

	// Parse month (1-12)
	month, err := parseCronField(parts[3], 1, 12)
	if err != nil {
		return nil, fmt.Errorf("invalid month field: %v", err)
	}
	cron.Month = month

	// Parse day of week (0-6)
	weekday, err := parseCronField(parts[4], 0, 6)
	if err != nil {
		return nil, fmt.Errorf("invalid weekday field: %v", err)
	}
	cron.DayOfWeek = weekday

	return cron, nil
}

// parseCronField parses a single cron field
func parseCronField(field string, min, max int) ([]int, error) {
	var values []int

	// Handle wildcard
	if field == "*" {
		for i := min; i <= max; i++ {
			values = append(values, i)
		}
		return values, nil
	}

	// Handle comma-separated values
	if strings.Contains(field, ",") {
		parts := strings.Split(field, ",")
		for _, part := range parts {
			val, err := parseCronField(strings.TrimSpace(part), min, max)
			if err != nil {
				return nil, err
			}
			values = append(values, val...)
		}
		return values, nil
	}

	// Handle ranges
	if strings.Contains(field, "-") {
		parts := strings.Split(field, "-")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid range format")
		}

		start, err := strconv.Atoi(parts[0])
		if err != nil {
			return nil, fmt.Errorf("invalid range start: %v", err)
		}

		end, err := strconv.Atoi(parts[1])
		if err != nil {
			return nil, fmt.Errorf("invalid range end: %v", err)
		}

		if start < min || end > max || start > end {
			return nil, fmt.Errorf("range out of bounds")
		}

		for i := start; i <= end; i++ {
			values = append(values, i)
		}
		return values, nil
	}

	// Handle step values (e.g., */5, 0-30/5)
	if strings.Contains(field, "/") {
		parts := strings.Split(field, "/")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid step format")
		}

		step, err := strconv.Atoi(parts[1])
		if err != nil {
			return nil, fmt.Errorf("invalid step value: %v", err)
		}

		var baseValues []int
		if parts[0] == "*" {
			// Handle */step
			for i := min; i <= max; i++ {
				baseValues = append(baseValues, i)
			}
		} else {
			// Handle range/step
			baseValues, err = parseCronField(parts[0], min, max)
			if err != nil {
				return nil, err
			}
		}

		for _, val := range baseValues {
			if (val-min)%step == 0 {
				values = append(values, val)
			}
		}
		return values, nil
	}

	// Handle single value
	val, err := strconv.Atoi(field)
	if err != nil {
		return nil, fmt.Errorf("invalid value: %v", err)
	}

	if val < min || val > max {
		return nil, fmt.Errorf("value out of bounds")
	}

	return []int{val}, nil
}

// AddJob adds a new scheduled job
func (s *Scheduler) AddJob(id, name, cronExpr string, handler func(context.Context) error) (*ScheduledJob, error) {
	cron, err := ParseCronExpression(cronExpr)
	if err != nil {
		return nil, err
	}

	job := &ScheduledJob{
		ID:       id,
		Name:     name,
		CronExpr: cron,
		IsActive: true,
		Handler:  handler,
		Metadata: make(map[string]interface{}),
	}

	// Calculate next run time
	job.NextRun = s.calculateNextRun(job, time.Now())

	s.jobsMutex.Lock()
	s.jobs[id] = job
	s.jobsMutex.Unlock()

	log.Printf("Added scheduled job: %s (next run: %s)", name, job.NextRun.Format(time.RFC3339))
	return job, nil
}

// calculateNextRun calculates the next run time for a job
func (s *Scheduler) calculateNextRun(job *ScheduledJob, from time.Time) time.Time {
	// Start from the next minute
	next := from.Truncate(time.Minute).Add(time.Minute)

	for {
		// Check if this time matches the cron expression
		if s.matchesCronExpression(job.CronExpr, next) {
			return next
		}

		// Move to next minute
		next = next.Add(time.Minute)

		// Prevent infinite loop (max 1 year ahead)
		if next.Sub(from) > 365*24*time.Hour {
			return next
		}
	}
}

// matchesCronExpression checks if a time matches a cron expression
func (s *Scheduler) matchesCronExpression(cron *CronExpression, t time.Time) bool {
	minute := t.Minute()
	hour := t.Hour()
	day := t.Day()
	month := int(t.Month())
	weekday := int(t.Weekday())

	// Check minute
	if !contains(cron.Minute, minute) {
		return false
	}

	// Check hour
	if !contains(cron.Hour, hour) {
		return false
	}

	// Check day of month
	if !contains(cron.DayOfMonth, day) {
		return false
	}

	// Check month
	if !contains(cron.Month, month) {
		return false
	}

	// Check day of week
	if !contains(cron.DayOfWeek, weekday) {
		return false
	}

	return true
}

// contains checks if a slice contains a value
func contains(slice []int, value int) bool {
	for _, v := range slice {
		if v == value {
			return true
		}
	}
	return false
}

// Start starts the scheduler
func (s *Scheduler) Start(ctx context.Context) {
	s.runningMutex.Lock()
	if s.isRunning {
		s.runningMutex.Unlock()
		return
	}
	s.isRunning = true
	s.runningMutex.Unlock()

	log.Println("Starting scheduler...")

	ticker := time.NewTicker(time.Minute)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("Scheduler stopped by context")
			return
		case <-s.stopChan:
			log.Println("Scheduler stopped")
			return
		case <-ticker.C:
			s.processJobs(ctx)
		}
	}
}

// processJobs processes jobs that are due to run
func (s *Scheduler) processJobs(ctx context.Context) {
	now := time.Now()

	s.jobsMutex.RLock()
	var dueJobs []*ScheduledJob
	for _, job := range s.jobs {
		job.Mutex.RLock()
		if job.IsActive && !job.NextRun.After(now) {
			dueJobs = append(dueJobs, job)
		}
		job.Mutex.RUnlock()
	}
	s.jobsMutex.RUnlock()

	// Execute due jobs
	for _, job := range dueJobs {
		go s.executeJob(ctx, job)
	}
}

// executeJob executes a scheduled job
func (s *Scheduler) executeJob(ctx context.Context, job *ScheduledJob) {
	job.Mutex.Lock()
	defer job.Mutex.Unlock()

	log.Printf("Executing job: %s", job.Name)

	// Update last run time
	now := time.Now()
	job.LastRun = &now

	// Execute the job
	if job.Handler != nil {
		if err := job.Handler(ctx); err != nil {
			log.Printf("Job %s failed: %v", job.Name, err)
			if job.ErrorHandler != nil {
				job.ErrorHandler(ctx, err)
			}
		} else {
			log.Printf("Job %s completed successfully", job.Name)
		}
	}

	// Calculate next run time
	job.NextRun = s.calculateNextRun(job, now)
	log.Printf("Job %s next run: %s", job.Name, job.NextRun.Format(time.RFC3339))
}

// Stop stops the scheduler
func (s *Scheduler) Stop() {
	s.runningMutex.Lock()
	defer s.runningMutex.Unlock()

	if s.isRunning {
		close(s.stopChan)
		s.isRunning = false
	}
}

// GetJob retrieves a job by ID
func (s *Scheduler) GetJob(id string) (*ScheduledJob, bool) {
	s.jobsMutex.RLock()
	defer s.jobsMutex.RUnlock()

	job, exists := s.jobs[id]
	return job, exists
}

// ListJobs returns all jobs
func (s *Scheduler) ListJobs() []*ScheduledJob {
	s.jobsMutex.RLock()
	defer s.jobsMutex.RUnlock()

	jobs := make([]*ScheduledJob, 0, len(s.jobs))
	for _, job := range s.jobs {
		jobs = append(jobs, job)
	}
	return jobs
}

// RemoveJob removes a job by ID
func (s *Scheduler) RemoveJob(id string) bool {
	s.jobsMutex.Lock()
	defer s.jobsMutex.Unlock()

	_, exists := s.jobs[id]
	if exists {
		delete(s.jobs, id)
		log.Printf("Removed job: %s", id)
	}
	return exists
}

// SetJobActive sets the active status of a job
func (s *Scheduler) SetJobActive(id string, active bool) bool {
	s.jobsMutex.RLock()
	job, exists := s.jobs[id]
	s.jobsMutex.RUnlock()

	if !exists {
		return false
	}

	job.Mutex.Lock()
	job.IsActive = active
	job.Mutex.Unlock()

	log.Printf("Job %s active status set to: %v", id, active)
	return true
}

// GetNextRunTime returns the next run time for a job
func (s *Scheduler) GetNextRunTime(id string) (time.Time, bool) {
	s.jobsMutex.RLock()
	job, exists := s.jobs[id]
	s.jobsMutex.RUnlock()

	if !exists {
		return time.Time{}, false
	}

	job.Mutex.RLock()
	nextRun := job.NextRun
	job.Mutex.RUnlock()

	return nextRun, true
}
