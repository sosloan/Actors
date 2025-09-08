package time

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"sync"
	"time"
)

// TimeServer represents a time server for synchronization
type TimeServer struct {
	URL      string `json:"url"`
	Name     string `json:"name"`
	Latency  int64  `json:"latency"` // milliseconds
	Offset   int64  `json:"offset"`  // milliseconds
	IsActive bool   `json:"is_active"`
}

// TimeSyncResult represents the result of a time synchronization
type TimeSyncResult struct {
	ServerTime time.Time `json:"server_time"`
	LocalTime  time.Time `json:"local_time"`
	Offset     int64     `json:"offset"`   // milliseconds
	Latency    int64     `json:"latency"`  // milliseconds
	Accuracy   float64   `json:"accuracy"` // estimated accuracy in milliseconds
	Server     string    `json:"server"`
	SyncTime   time.Time `json:"sync_time"`
}

// TimeSyncService provides time synchronization capabilities
type TimeSyncService struct {
	servers       []*TimeServer
	serversMutex  sync.RWMutex
	lastSync      *TimeSyncResult
	lastSyncMutex sync.RWMutex
	driftHistory  []int64 // historical drift measurements
	driftMutex    sync.RWMutex
	stopChan      chan struct{}
	isRunning     bool
	runningMutex  sync.RWMutex
}

// NewTimeSyncService creates a new time synchronization service
func NewTimeSyncService() *TimeSyncService {
	service := &TimeSyncService{
		servers:      make([]*TimeServer, 0),
		driftHistory: make([]int64, 0),
		stopChan:     make(chan struct{}),
	}

	// Initialize with default time servers
	service.initializeDefaultServers()

	return service
}

// initializeDefaultServers sets up default NTP servers
func (ts *TimeSyncService) initializeDefaultServers() {
	defaultServers := []*TimeServer{
		{URL: "https://time.google.com", Name: "Google Time", IsActive: true},
		{URL: "https://time.cloudflare.com", Name: "Cloudflare Time", IsActive: true},
		{URL: "https://time.apple.com", Name: "Apple Time", IsActive: true},
		{URL: "https://time.windows.com", Name: "Microsoft Time", IsActive: true},
	}

	ts.serversMutex.Lock()
	ts.servers = defaultServers
	ts.serversMutex.Unlock()
}

// AddTimeServer adds a new time server
func (ts *TimeSyncService) AddTimeServer(server *TimeServer) {
	ts.serversMutex.Lock()
	defer ts.serversMutex.Unlock()

	ts.servers = append(ts.servers, server)
}

// SyncWithServer synchronizes time with a specific server
func (ts *TimeSyncService) SyncWithServer(ctx context.Context, serverURL string) (*TimeSyncResult, error) {
	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	// Perform multiple measurements for accuracy
	measurements := make([]int64, 3)
	latencies := make([]int64, 3)

	for i := 0; i < 3; i++ {
		startTime := time.Now()

		req, err := http.NewRequestWithContext(ctx, "GET", serverURL, nil)
		if err != nil {
			return nil, err
		}

		// Add headers to get server time
		req.Header.Set("User-Agent", "TimeSync/1.0")

		resp, err := client.Do(req)
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()

		endTime := time.Now()
		latency := endTime.Sub(startTime).Milliseconds()
		latencies[i] = latency

		// Extract server time from response headers
		serverTimeStr := resp.Header.Get("Date")
		if serverTimeStr == "" {
			// Fallback: use current time minus half the latency
			serverTime := startTime.Add(time.Duration(-latency/2) * time.Millisecond)
			measurements[i] = serverTime.UnixMilli()
		} else {
			serverTime, err := time.Parse(time.RFC1123, serverTimeStr)
			if err != nil {
				return nil, fmt.Errorf("failed to parse server time: %v", err)
			}
			measurements[i] = serverTime.UnixMilli()
		}

		// Small delay between measurements
		time.Sleep(100 * time.Millisecond)
	}

	// Calculate average latency
	avgLatency := int64(0)
	for _, lat := range latencies {
		avgLatency += lat
	}
	avgLatency /= int64(len(latencies))

	// Calculate average server time
	avgServerTime := int64(0)
	for _, measurement := range measurements {
		avgServerTime += measurement
	}
	avgServerTime /= int64(len(measurements))

	// Calculate offset
	localTime := time.Now()
	serverTime := time.UnixMilli(avgServerTime)
	offset := serverTime.Sub(localTime).Milliseconds()

	// Estimate accuracy (based on latency and measurement variance)
	variance := ts.calculateVariance(measurements)
	accuracy := math.Sqrt(float64(variance)) + float64(avgLatency)/2

	result := &TimeSyncResult{
		ServerTime: serverTime,
		LocalTime:  localTime,
		Offset:     offset,
		Latency:    avgLatency,
		Accuracy:   accuracy,
		Server:     serverURL,
		SyncTime:   time.Now(),
	}

	// Update drift history
	ts.driftMutex.Lock()
	ts.driftHistory = append(ts.driftHistory, offset)
	if len(ts.driftHistory) > 100 { // Keep only last 100 measurements
		ts.driftHistory = ts.driftHistory[1:]
	}
	ts.driftMutex.Unlock()

	// Update last sync result
	ts.lastSyncMutex.Lock()
	ts.lastSync = result
	ts.lastSyncMutex.Unlock()

	return result, nil
}

// calculateVariance calculates the variance of measurements
func (ts *TimeSyncService) calculateVariance(measurements []int64) int64 {
	if len(measurements) == 0 {
		return 0
	}

	// Calculate mean
	sum := int64(0)
	for _, m := range measurements {
		sum += m
	}
	mean := sum / int64(len(measurements))

	// Calculate variance
	variance := int64(0)
	for _, m := range measurements {
		diff := m - mean
		variance += diff * diff
	}
	variance /= int64(len(measurements))

	return variance
}

// SyncWithBestServer synchronizes with the best available server
func (ts *TimeSyncService) SyncWithBestServer(ctx context.Context) (*TimeSyncResult, error) {
	ts.serversMutex.RLock()
	servers := make([]*TimeServer, len(ts.servers))
	copy(servers, ts.servers)
	ts.serversMutex.RUnlock()

	var bestResult *TimeSyncResult
	var bestScore float64 = math.Inf(1)

	for _, server := range servers {
		if !server.IsActive {
			continue
		}

		result, err := ts.SyncWithServer(ctx, server.URL)
		if err != nil {
			log.Printf("Failed to sync with server %s: %v", server.Name, err)
			continue
		}

		// Score based on latency and accuracy (lower is better)
		score := float64(result.Latency) + result.Accuracy

		if score < bestScore {
			bestScore = score
			bestResult = result
		}

		// Update server metrics
		server.Latency = result.Latency
		server.Offset = result.Offset
	}

	if bestResult == nil {
		return nil, fmt.Errorf("no servers available for synchronization")
	}

	return bestResult, nil
}

// StartAutoSync starts automatic time synchronization
func (ts *TimeSyncService) StartAutoSync(ctx context.Context, interval time.Duration) {
	ts.runningMutex.Lock()
	if ts.isRunning {
		ts.runningMutex.Unlock()
		return
	}
	ts.isRunning = true
	ts.runningMutex.Unlock()

	log.Printf("Starting auto-sync with interval: %v", interval)

	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			log.Println("Auto-sync stopped by context")
			return
		case <-ts.stopChan:
			log.Println("Auto-sync stopped")
			return
		case <-ticker.C:
			result, err := ts.SyncWithBestServer(ctx)
			if err != nil {
				log.Printf("Auto-sync failed: %v", err)
			} else {
				log.Printf("Auto-sync successful: offset=%dms, latency=%dms", result.Offset, result.Latency)
			}
		}
	}
}

// GetDriftEstimate estimates the current time drift
func (ts *TimeSyncService) GetDriftEstimate() (int64, float64) {
	ts.driftMutex.RLock()
	defer ts.driftMutex.RUnlock()

	if len(ts.driftHistory) == 0 {
		return 0, 0
	}

	// Calculate average drift
	sum := int64(0)
	for _, drift := range ts.driftHistory {
		sum += drift
	}
	avgDrift := sum / int64(len(ts.driftHistory))

	// Calculate drift rate (ms per hour)
	driftRate := float64(0)
	if len(ts.driftHistory) > 1 {
		// Simple linear regression to estimate drift rate
		timeSpan := len(ts.driftHistory) // assuming measurements are 1 hour apart
		if timeSpan > 1 {
			firstDrift := ts.driftHistory[0]
			lastDrift := ts.driftHistory[len(ts.driftHistory)-1]
			driftRate = float64(lastDrift-firstDrift) / float64(timeSpan-1)
		}
	}

	return avgDrift, driftRate
}

// CorrectTime applies time correction based on drift estimate
func (ts *TimeSyncService) CorrectTime() time.Time {
	ts.lastSyncMutex.RLock()
	lastSync := ts.lastSync
	ts.lastSyncMutex.RUnlock()

	if lastSync == nil {
		return time.Now()
	}

	// Calculate time since last sync
	timeSinceSync := time.Since(lastSync.SyncTime)

	// Apply offset and drift correction
	correctedTime := time.Now().Add(time.Duration(lastSync.Offset) * time.Millisecond)

	// Apply drift correction if we have drift history
	_, driftRate := ts.GetDriftEstimate()
	if driftRate != 0 {
		hoursSinceSync := timeSinceSync.Hours()
		driftCorrection := time.Duration(driftRate*hoursSinceSync) * time.Millisecond
		correctedTime = correctedTime.Add(driftCorrection)
	}

	return correctedTime
}

// GetLastSyncResult returns the last synchronization result
func (ts *TimeSyncService) GetLastSyncResult() *TimeSyncResult {
	ts.lastSyncMutex.RLock()
	defer ts.lastSyncMutex.RUnlock()

	return ts.lastSync
}

// GetSyncStatus returns the current synchronization status
func (ts *TimeSyncService) GetSyncStatus() map[string]interface{} {
	status := make(map[string]interface{})

	ts.lastSyncMutex.RLock()
	lastSync := ts.lastSync
	ts.lastSyncMutex.RUnlock()

	if lastSync != nil {
		status["last_sync"] = lastSync.SyncTime
		status["offset_ms"] = lastSync.Offset
		status["latency_ms"] = lastSync.Latency
		status["accuracy_ms"] = lastSync.Accuracy
		status["server"] = lastSync.Server
		status["time_since_sync"] = time.Since(lastSync.SyncTime).String()
	} else {
		status["last_sync"] = nil
		status["status"] = "never_synced"
	}

	drift, driftRate := ts.GetDriftEstimate()
	status["estimated_drift_ms"] = drift
	status["drift_rate_ms_per_hour"] = driftRate

	ts.serversMutex.RLock()
	status["available_servers"] = len(ts.servers)
	activeServers := 0
	for _, server := range ts.servers {
		if server.IsActive {
			activeServers++
		}
	}
	status["active_servers"] = activeServers
	ts.serversMutex.RUnlock()

	return status
}

// Stop stops the time synchronization service
func (ts *TimeSyncService) Stop() {
	ts.runningMutex.Lock()
	defer ts.runningMutex.Unlock()

	if ts.isRunning {
		close(ts.stopChan)
		ts.isRunning = false
	}
}

// ExportSyncData exports synchronization data to JSON
func (ts *TimeSyncService) ExportSyncData() ([]byte, error) {
	data := make(map[string]interface{})

	ts.lastSyncMutex.RLock()
	data["last_sync"] = ts.lastSync
	ts.lastSyncMutex.RUnlock()

	ts.driftMutex.RLock()
	data["drift_history"] = ts.driftHistory
	ts.driftMutex.RUnlock()

	ts.serversMutex.RLock()
	data["servers"] = ts.servers
	ts.serversMutex.RUnlock()

	return json.MarshalIndent(data, "", "  ")
}

// ValidateTimeAccuracy validates the accuracy of the current time
func (ts *TimeSyncService) ValidateTimeAccuracy() (bool, float64) {
	ts.lastSyncMutex.RLock()
	lastSync := ts.lastSync
	ts.lastSyncMutex.RUnlock()

	if lastSync == nil {
		return false, 0
	}

	// Check if last sync is recent (within 1 hour)
	timeSinceSync := time.Since(lastSync.SyncTime)
	if timeSinceSync > time.Hour {
		return false, 0
	}

	// Check if accuracy is within acceptable range (100ms)
	acceptableAccuracy := 100.0
	return lastSync.Accuracy <= acceptableAccuracy, lastSync.Accuracy
}
