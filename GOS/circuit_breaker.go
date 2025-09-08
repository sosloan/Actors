package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// CircuitState represents the state of a circuit breaker
type CircuitState int

const (
	CircuitClosed CircuitState = iota
	CircuitOpen
	CircuitHalfOpen
)

// String returns the string representation of the circuit state
func (cs CircuitState) String() string {
	switch cs {
	case CircuitClosed:
		return "CLOSED"
	case CircuitOpen:
		return "OPEN"
	case CircuitHalfOpen:
		return "HALF_OPEN"
	default:
		return "UNKNOWN"
	}
}

// CircuitBreakerConfig holds configuration for a circuit breaker
type CircuitBreakerConfig struct {
	FailureThreshold int           // Number of failures before opening circuit
	SuccessThreshold int           // Number of successes needed to close circuit from half-open
	Timeout          time.Duration // How long to wait before trying half-open
	MaxRequests      int           // Max requests allowed in half-open state
}

// DefaultCircuitBreakerConfig returns a sensible default configuration
func DefaultCircuitBreakerConfig() *CircuitBreakerConfig {
	return &CircuitBreakerConfig{
		FailureThreshold: 5,
		SuccessThreshold: 3,
		Timeout:          30 * time.Second,
		MaxRequests:      3,
	}
}

// CircuitBreaker implements the circuit breaker pattern
type CircuitBreaker struct {
	config        *CircuitBreakerConfig
	state         CircuitState
	failureCount  int
	successCount  int
	lastFailure   time.Time
	halfOpenCount int
	mutex         sync.RWMutex
	metrics       *CircuitBreakerMetrics
}

// CircuitBreakerMetrics tracks circuit breaker performance
type CircuitBreakerMetrics struct {
	TotalRequests      int64
	SuccessfulRequests int64
	FailedRequests     int64
	CircuitOpens       int64
	CircuitCloses      int64
	LastStateChange    time.Time
}

// NewCircuitBreaker creates a new circuit breaker with the given configuration
func NewCircuitBreaker(config *CircuitBreakerConfig) *CircuitBreaker {
	if config == nil {
		config = DefaultCircuitBreakerConfig()
	}

	return &CircuitBreaker{
		config:  config,
		state:   CircuitClosed,
		metrics: &CircuitBreakerMetrics{},
	}
}

// Execute runs a function through the circuit breaker
func (cb *CircuitBreaker) Execute(ctx context.Context, fn func() error) error {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.metrics.TotalRequests++

	// Check if circuit is open and should remain open
	if cb.state == CircuitOpen {
		if time.Since(cb.lastFailure) < cb.config.Timeout {
			cb.metrics.FailedRequests++
			return fmt.Errorf("circuit breaker is OPEN: %w", ErrCircuitOpen)
		}
		// Time to try half-open
		cb.state = CircuitHalfOpen
		cb.halfOpenCount = 0
		cb.metrics.LastStateChange = time.Now()
	}

	// Check if circuit is half-open and at max requests
	if cb.state == CircuitHalfOpen && cb.halfOpenCount >= cb.config.MaxRequests {
		cb.metrics.FailedRequests++
		return fmt.Errorf("circuit breaker is HALF_OPEN at max requests: %w", ErrCircuitHalfOpenMaxRequests)
	}

	// Execute the function
	err := fn()

	if err != nil {
		cb.recordFailure()
		cb.metrics.FailedRequests++
		return err
	}

	cb.recordSuccess()
	cb.metrics.SuccessfulRequests++
	return nil
}

// recordFailure records a failure and updates circuit state
func (cb *CircuitBreaker) recordFailure() {
	cb.failureCount++
	cb.lastFailure = time.Now()
	cb.successCount = 0

	if cb.state == CircuitHalfOpen {
		// Half-open failed, go back to open
		cb.state = CircuitOpen
		cb.halfOpenCount = 0
		cb.metrics.CircuitOpens++
		cb.metrics.LastStateChange = time.Now()
	} else if cb.failureCount >= cb.config.FailureThreshold {
		// Closed circuit failed too many times, open it
		cb.state = CircuitOpen
		cb.metrics.CircuitOpens++
		cb.metrics.LastStateChange = time.Now()
	}
}

// recordSuccess records a success and updates circuit state
func (cb *CircuitBreaker) recordSuccess() {
	cb.successCount++
	cb.failureCount = 0

	if cb.state == CircuitHalfOpen {
		cb.halfOpenCount++
		if cb.successCount >= cb.config.SuccessThreshold {
			// Half-open succeeded enough times, close circuit
			cb.state = CircuitClosed
			cb.halfOpenCount = 0
			cb.metrics.CircuitCloses++
			cb.metrics.LastStateChange = time.Now()
		}
	}
}

// GetState returns the current state of the circuit breaker
func (cb *CircuitBreaker) GetState() CircuitState {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()
	return cb.state
}

// GetMetrics returns the current metrics for the circuit breaker
func (cb *CircuitBreaker) GetMetrics() CircuitBreakerMetrics {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()
	return *cb.metrics
}

// Reset resets the circuit breaker to closed state
func (cb *CircuitBreaker) Reset() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.state = CircuitClosed
	cb.failureCount = 0
	cb.successCount = 0
	cb.halfOpenCount = 0
	cb.metrics.LastStateChange = time.Now()
}

// Custom errors for circuit breaker
var (
	ErrCircuitOpen                = fmt.Errorf("circuit breaker is open")
	ErrCircuitHalfOpenMaxRequests = fmt.Errorf("circuit breaker half-open at max requests")
)

// RetryConfig holds configuration for retry logic
type RetryConfig struct {
	MaxRetries      int
	InitialDelay    time.Duration
	MaxDelay        time.Duration
	BackoffFactor   float64
	Jitter          bool
	RetryableErrors []error
}

// DefaultRetryConfig returns a sensible default retry configuration
func DefaultRetryConfig() *RetryConfig {
	return &RetryConfig{
		MaxRetries:    3,
		InitialDelay:  100 * time.Millisecond,
		MaxDelay:      5 * time.Second,
		BackoffFactor: 2.0,
		Jitter:        true,
	}
}

// RetryWithBackoff executes a function with exponential backoff retry logic
func RetryWithBackoff(ctx context.Context, config *RetryConfig, fn func() error) error {
	if config == nil {
		config = DefaultRetryConfig()
	}

	var lastErr error
	delay := config.InitialDelay

	for attempt := 0; attempt <= config.MaxRetries; attempt++ {
		// Check context cancellation
		select {
		case <-ctx.Done():
			return fmt.Errorf("context cancelled: %w", ctx.Err())
		default:
		}

		// Execute the function
		err := fn()
		if err == nil {
			return nil
		}

		lastErr = err

		// Check if error is retryable
		if !isRetryableError(err, config.RetryableErrors) {
			return err
		}

		// Don't sleep after the last attempt
		if attempt == config.MaxRetries {
			break
		}

		// Calculate delay with jitter
		sleepDuration := delay
		if config.Jitter {
			sleepDuration = addJitter(delay)
		}

		// Sleep with context cancellation support
		select {
		case <-ctx.Done():
			return fmt.Errorf("context cancelled during retry: %w", ctx.Err())
		case <-time.After(sleepDuration):
		}

		// Calculate next delay
		delay = time.Duration(float64(delay) * config.BackoffFactor)
		if delay > config.MaxDelay {
			delay = config.MaxDelay
		}
	}

	return fmt.Errorf("max retries exceeded (%d): %w", config.MaxRetries, lastErr)
}

// isRetryableError checks if an error is retryable
func isRetryableError(err error, retryableErrors []error) bool {
	// If no specific retryable errors are defined, retry all errors
	if len(retryableErrors) == 0 {
		return true
	}

	// Check if error matches any retryable error types
	for _, retryableErr := range retryableErrors {
		if err == retryableErr {
			return true
		}
	}

	return false
}

// addJitter adds random jitter to a duration to avoid thundering herd
func addJitter(duration time.Duration) time.Duration {
	// Add ±25% jitter
	jitter := time.Duration(float64(duration) * 0.25 * float64(2*time.Now().UnixNano()%2-1))
	return duration + jitter
}

// CircuitBreakerManager manages multiple circuit breakers
type CircuitBreakerManager struct {
	breakers map[string]*CircuitBreaker
	mutex    sync.RWMutex
}

// NewCircuitBreakerManager creates a new circuit breaker manager
func NewCircuitBreakerManager() *CircuitBreakerManager {
	return &CircuitBreakerManager{
		breakers: make(map[string]*CircuitBreaker),
	}
}

// GetOrCreate gets an existing circuit breaker or creates a new one
func (cbm *CircuitBreakerManager) GetOrCreate(name string, config *CircuitBreakerConfig) *CircuitBreaker {
	cbm.mutex.Lock()
	defer cbm.mutex.Unlock()

	if breaker, exists := cbm.breakers[name]; exists {
		return breaker
	}

	breaker := NewCircuitBreaker(config)
	cbm.breakers[name] = breaker
	return breaker
}

// Get returns an existing circuit breaker
func (cbm *CircuitBreakerManager) Get(name string) (*CircuitBreaker, bool) {
	cbm.mutex.RLock()
	defer cbm.mutex.RUnlock()

	breaker, exists := cbm.breakers[name]
	return breaker, exists
}

// GetAll returns all circuit breakers
func (cbm *CircuitBreakerManager) GetAll() map[string]*CircuitBreaker {
	cbm.mutex.RLock()
	defer cbm.mutex.RUnlock()

	result := make(map[string]*CircuitBreaker)
	for name, breaker := range cbm.breakers {
		result[name] = breaker
	}
	return result
}

// ResetAll resets all circuit breakers
func (cbm *CircuitBreakerManager) ResetAll() {
	cbm.mutex.Lock()
	defer cbm.mutex.Unlock()

	for _, breaker := range cbm.breakers {
		breaker.Reset()
	}
}
