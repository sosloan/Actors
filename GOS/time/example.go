package time

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/mattn/go-sqlite3"
)

// Example demonstrates how to use the advanced time system
func Example() {
	// Initialize database
	db, err := sqlx.Open("sqlite3", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create time service
	timeService := NewTimeService(db)

	// Initialize the service
	if err := timeService.Initialize(); err != nil {
		log.Fatal(err)
	}

	// Create context
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start the service
	timeService.Start(ctx)
	defer timeService.Stop()

	// Example 1: Create a time block
	timeBlock := &TimeBlock{
		ID:          "example_block_1",
		UserID:      "user123",
		Title:       "Morning Focus Session",
		Description: "Deep work on project",
		StartTime:   time.Now(),
		EndTime:     time.Now().Add(2 * time.Hour),
		Category:    "work",
		Priority:    3,
		IsCompleted: false,
	}

	if err := timeService.CreateTimeBlock(timeBlock); err != nil {
		log.Printf("Error creating time block: %v", err)
	}

	// Example 2: Add a scheduled job
	job, err := timeService.AddScheduledJob(
		"daily_reminder",
		"Daily Standup Reminder",
		"0 9 * * 1-5", // 9 AM, Monday to Friday
		func(ctx context.Context) error {
			log.Println("Time for daily standup!")
			return nil
		},
	)
	if err != nil {
		log.Printf("Error adding scheduled job: %v", err)
	} else {
		log.Printf("Added scheduled job: %s", job.Name)
	}

	// Example 3: Create a time event
	event := &TimeEvent{
		ID:          "meeting_reminder",
		UserID:      "user123",
		Type:        EventTypeReminder,
		Title:       "Team Meeting",
		Description: "Weekly team sync",
		Priority:    PriorityHigh,
		StartTime:   time.Now().Add(30 * time.Minute),
		EndTime:     timePtr(time.Now().Add(90 * time.Minute)),
		IsActive:    true,
		IsCompleted: false,
		Metadata: map[string]interface{}{
			"meeting_room": "Conference Room A",
			"attendees":    []string{"alice", "bob", "charlie"},
		},
	}

	if err := timeService.AddTimeEvent(event); err != nil {
		log.Printf("Error adding time event: %v", err)
	}

	// Example 4: Create a Pomodoro timer
	if err := timeService.CreatePomodoroTimer("user123", 4); err != nil {
		log.Printf("Error creating Pomodoro timer: %v", err)
	}

	// Example 5: Sync time with external servers
	syncResult, err := timeService.SyncTime(ctx)
	if err != nil {
		log.Printf("Error syncing time: %v", err)
	} else {
		log.Printf("Time synced: offset=%dms, latency=%dms", syncResult.Offset, syncResult.Latency)
	}

	// Example 6: Get current corrected time
	currentTime := timeService.GetCurrentTime()
	log.Printf("Current corrected time: %s", currentTime.Format(time.RFC3339))

	// Example 7: Get upcoming events
	upcomingEvents := timeService.GetUpcomingEvents("user123", 24*time.Hour)
	log.Printf("Upcoming events: %d", len(upcomingEvents))

	// Example 8: Generate time analytics
	startDate := time.Now().AddDate(0, 0, -7) // Last week
	endDate := time.Now()

	insights, err := timeService.GetTimeInsights("user123", startDate, endDate)
	if err != nil {
		log.Printf("Error getting time insights: %v", err)
	} else {
		log.Printf("Time insights: %+v", insights)
	}

	// Example 9: Get service status
	status := timeService.GetServiceStatus()
	log.Printf("Service status: %+v", status)

	// Example 10: Create daily schedule
	dailyBlocks := []TimeBlock{
		{
			Title:    "Morning Routine",
			Category: "personal",
			Priority: 2,
		},
		{
			Title:    "Work Session 1",
			Category: "work",
			Priority: 4,
		},
		{
			Title:    "Lunch Break",
			Category: "break",
			Priority: 1,
		},
		{
			Title:    "Work Session 2",
			Category: "work",
			Priority: 4,
		},
	}

	if err := timeService.CreateDailySchedule("user123", time.Now(), dailyBlocks); err != nil {
		log.Printf("Error creating daily schedule: %v", err)
	}

	// Wait a bit to see the system in action
	time.Sleep(5 * time.Second)

	log.Println("Advanced time system example completed!")
}

// timePtr is a helper function to create a pointer to time.Time
func timePtr(t time.Time) *time.Time {
	return &t
}

// ExampleTimeAnalytics demonstrates time analytics features
func ExampleTimeAnalytics() {
	// Initialize database
	db, err := sqlx.Open("sqlite3", ":memory:")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Create time service
	timeService := NewTimeService(db)

	// Initialize the service
	if err := timeService.Initialize(); err != nil {
		log.Fatal(err)
	}

	// Create some sample time blocks
	now := time.Now()
	userID := "analytics_user"

	// Create time blocks for the past week
	for i := 0; i < 7; i++ {
		date := now.AddDate(0, 0, -i)

		// Work blocks
		workBlock := &TimeBlock{
			ID:          fmt.Sprintf("work_%d", i),
			UserID:      userID,
			Title:       fmt.Sprintf("Work Session %d", i+1),
			Category:    "work",
			StartTime:   date.Add(9 * time.Hour),
			EndTime:     date.Add(12 * time.Hour),
			Duration:    3 * 3600, // 3 hours
			Priority:    4,
			IsCompleted: true,
		}
		timeService.CreateTimeBlock(workBlock)

		// Break blocks
		breakBlock := &TimeBlock{
			ID:          fmt.Sprintf("break_%d", i),
			UserID:      userID,
			Title:       fmt.Sprintf("Lunch Break %d", i+1),
			Category:    "break",
			StartTime:   date.Add(12 * time.Hour),
			EndTime:     date.Add(13 * time.Hour),
			Duration:    3600, // 1 hour
			Priority:    2,
			IsCompleted: true,
		}
		timeService.CreateTimeBlock(breakBlock)

		// Afternoon work
		afternoonBlock := &TimeBlock{
			ID:          fmt.Sprintf("afternoon_%d", i),
			UserID:      userID,
			Title:       fmt.Sprintf("Afternoon Work %d", i+1),
			Category:    "work",
			StartTime:   date.Add(13 * time.Hour),
			EndTime:     date.Add(17 * time.Hour),
			Duration:    4 * 3600, // 4 hours
			Priority:    4,
			IsCompleted: true,
		}
		timeService.CreateTimeBlock(afternoonBlock)
	}

	// Generate analytics
	startDate := now.AddDate(0, 0, -7)
	endDate := now

	// Get time insights
	insights, err := timeService.GetTimeInsights(userID, startDate, endDate)
	if err != nil {
		log.Printf("Error getting insights: %v", err)
	} else {
		log.Printf("Time Insights:")
		for key, value := range insights {
			log.Printf("  %s: %v", key, value)
		}
	}

	// Get productivity score
	score, err := timeService.GetProductivityScore(userID, startDate, endDate)
	if err != nil {
		log.Printf("Error getting productivity score: %v", err)
	} else {
		log.Printf("Productivity Score: %.2f", score)
	}

	// Get time distribution
	distribution, err := timeService.AnalyticsService.GetTimeDistribution(userID, startDate, endDate)
	if err != nil {
		log.Printf("Error getting time distribution: %v", err)
	} else {
		log.Printf("Time Distribution:")
		for category, seconds := range distribution {
			hours := float64(seconds) / 3600.0
			log.Printf("  %s: %.2f hours", category, hours)
		}
	}
}
