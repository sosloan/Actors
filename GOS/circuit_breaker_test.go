package main

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestCircuitBreakerInitialState(t *testing.T) {
	cb := NewCircuitBreaker(nil)
	if cb.GetState() != CircuitClosed {
		t.Errorf("Expected initial state CLOSED, got %s", cb.GetState())
	}
}

func TestCircuitBreakerDefaultConfig(t *testing.T) {
	cfg := DefaultCircuitBreakerConfig()
	if cfg.FailureThreshold != 5 {
		t.Errorf("Expected FailureThreshold 5, got %d", cfg.FailureThreshold)
	}
	if cfg.SuccessThreshold != 3 {
		t.Errorf("Expected SuccessThreshold 3, got %d", cfg.SuccessThreshold)
	}
	if cfg.Timeout != 30*time.Second {
		t.Errorf("Expected Timeout 30s, got %v", cfg.Timeout)
	}
	if cfg.MaxRequests != 3 {
		t.Errorf("Expected MaxRequests 3, got %d", cfg.MaxRequests)
	}
}

func TestCircuitBreakerClosedToOpen(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 3,
		SuccessThreshold: 2,
		Timeout:          100 * time.Millisecond,
		MaxRequests:      2,
	}
	cb := NewCircuitBreaker(cfg)
	errFail := errors.New("failure")
	ctx := context.Background()

	// First 2 failures: circuit stays CLOSED
	for i := 0; i < 2; i++ {
		_ = cb.Execute(ctx, func() error { return errFail })
		if cb.GetState() != CircuitClosed {
			t.Errorf("After %d failures expected CLOSED, got %s", i+1, cb.GetState())
		}
	}

	// 3rd failure: circuit opens
	_ = cb.Execute(ctx, func() error { return errFail })
	if cb.GetState() != CircuitOpen {
		t.Errorf("After threshold failures expected OPEN, got %s", cb.GetState())
	}
}

func TestCircuitBreakerOpenRejectsRequests(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 1,
		SuccessThreshold: 2,
		Timeout:          10 * time.Second, // long timeout so it stays open
		MaxRequests:      2,
	}
	cb := NewCircuitBreaker(cfg)
	ctx := context.Background()

	// Trip the circuit
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	if cb.GetState() != CircuitOpen {
		t.Fatal("Expected circuit to be OPEN")
	}

	// Should reject further requests with ErrCircuitOpen
	err := cb.Execute(ctx, func() error { return nil })
	if err == nil {
		t.Error("Expected error when circuit is OPEN, got nil")
	}
	if !errors.Is(err, ErrCircuitOpen) {
		t.Errorf("Expected ErrCircuitOpen wrapped, got %v", err)
	}
}

func TestCircuitBreakerOpenToHalfOpen(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 1,
		SuccessThreshold: 2,
		Timeout:          50 * time.Millisecond,
		MaxRequests:      3,
	}
	cb := NewCircuitBreaker(cfg)
	ctx := context.Background()

	// Trip the circuit
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	if cb.GetState() != CircuitOpen {
		t.Fatal("Expected OPEN")
	}

	// Wait for timeout to expire
	time.Sleep(100 * time.Millisecond)

	// Next request should transition to HALF_OPEN and execute the function
	called := false
	_ = cb.Execute(ctx, func() error { called = true; return nil })
	if !called {
		t.Error("Expected function to be called in HALF_OPEN state")
	}
	if cb.GetState() != CircuitHalfOpen {
		t.Errorf("Expected HALF_OPEN after timeout, got %s", cb.GetState())
	}
}

func TestCircuitBreakerHalfOpenToClosedOnSuccess(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 1,
		SuccessThreshold: 2,
		Timeout:          50 * time.Millisecond,
		MaxRequests:      5,
	}
	cb := NewCircuitBreaker(cfg)
	ctx := context.Background()

	// Trip the circuit
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	time.Sleep(100 * time.Millisecond)

	// 2 successes in half-open should close the circuit
	for i := 0; i < 2; i++ {
		err := cb.Execute(ctx, func() error { return nil })
		if err != nil {
			t.Errorf("Unexpected error in HALF_OPEN success: %v", err)
		}
	}

	if cb.GetState() != CircuitClosed {
		t.Errorf("Expected CLOSED after enough successes, got %s", cb.GetState())
	}
}

func TestCircuitBreakerHalfOpenToOpenOnFailure(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 1,
		SuccessThreshold: 3,
		Timeout:          50 * time.Millisecond,
		MaxRequests:      5,
	}
	cb := NewCircuitBreaker(cfg)
	ctx := context.Background()

	// Trip the circuit
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	time.Sleep(100 * time.Millisecond)

	// One success to enter half-open, then a failure
	_ = cb.Execute(ctx, func() error { return nil })
	_ = cb.Execute(ctx, func() error { return errors.New("fail again") })

	if cb.GetState() != CircuitOpen {
		t.Errorf("Expected OPEN after failure in HALF_OPEN, got %s", cb.GetState())
	}
}

func TestCircuitBreakerReset(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 1,
		SuccessThreshold: 2,
		Timeout:          10 * time.Second,
		MaxRequests:      2,
	}
	cb := NewCircuitBreaker(cfg)
	ctx := context.Background()

	// Trip the circuit
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	if cb.GetState() != CircuitOpen {
		t.Fatal("Expected OPEN")
	}

	cb.Reset()
	if cb.GetState() != CircuitClosed {
		t.Errorf("Expected CLOSED after Reset, got %s", cb.GetState())
	}
}

func TestCircuitBreakerMetrics(t *testing.T) {
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 3,
		SuccessThreshold: 2,
		Timeout:          50 * time.Millisecond,
		MaxRequests:      5,
	}
	cb := NewCircuitBreaker(cfg)
	ctx := context.Background()

	_ = cb.Execute(ctx, func() error { return nil })
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	_ = cb.Execute(ctx, func() error { return nil })

	m := cb.GetMetrics()
	if m.TotalRequests != 3 {
		t.Errorf("Expected 3 total requests, got %d", m.TotalRequests)
	}
	if m.SuccessfulRequests != 2 {
		t.Errorf("Expected 2 successful requests, got %d", m.SuccessfulRequests)
	}
	if m.FailedRequests != 1 {
		t.Errorf("Expected 1 failed request, got %d", m.FailedRequests)
	}
}

func TestCircuitBreakerStateString(t *testing.T) {
	tests := []struct {
		state CircuitState
		want  string
	}{
		{CircuitClosed, "CLOSED"},
		{CircuitOpen, "OPEN"},
		{CircuitHalfOpen, "HALF_OPEN"},
		{CircuitState(99), "UNKNOWN"},
	}
	for _, tc := range tests {
		if got := tc.state.String(); got != tc.want {
			t.Errorf("CircuitState(%d).String() = %q, want %q", tc.state, got, tc.want)
		}
	}
}

func TestCircuitBreakerManagerGetOrCreate(t *testing.T) {
	mgr := NewCircuitBreakerManager()
	cfg := DefaultCircuitBreakerConfig()

	cb1 := mgr.GetOrCreate("svc-a", cfg)
	cb2 := mgr.GetOrCreate("svc-a", cfg)
	if cb1 != cb2 {
		t.Error("GetOrCreate should return the same instance for the same name")
	}

	cb3 := mgr.GetOrCreate("svc-b", cfg)
	if cb1 == cb3 {
		t.Error("Different names should return different circuit breakers")
	}
}

func TestCircuitBreakerManagerGet(t *testing.T) {
	mgr := NewCircuitBreakerManager()
	cfg := DefaultCircuitBreakerConfig()

	_, ok := mgr.Get("missing")
	if ok {
		t.Error("Get on non-existent breaker should return false")
	}

	mgr.GetOrCreate("svc-a", cfg)
	_, ok = mgr.Get("svc-a")
	if !ok {
		t.Error("Get on existing breaker should return true")
	}
}

func TestCircuitBreakerManagerGetAll(t *testing.T) {
	mgr := NewCircuitBreakerManager()
	cfg := DefaultCircuitBreakerConfig()

	mgr.GetOrCreate("svc-a", cfg)
	mgr.GetOrCreate("svc-b", cfg)
	all := mgr.GetAll()
	if len(all) != 2 {
		t.Errorf("Expected 2 circuit breakers, got %d", len(all))
	}
}

func TestCircuitBreakerManagerResetAll(t *testing.T) {
	mgr := NewCircuitBreakerManager()
	cfg := &CircuitBreakerConfig{
		FailureThreshold: 1,
		SuccessThreshold: 2,
		Timeout:          10 * time.Second,
		MaxRequests:      2,
	}

	cb := mgr.GetOrCreate("svc-a", cfg)
	ctx := context.Background()
	_ = cb.Execute(ctx, func() error { return errors.New("fail") })
	if cb.GetState() != CircuitOpen {
		t.Fatal("Expected OPEN before ResetAll")
	}

	mgr.ResetAll()
	if cb.GetState() != CircuitClosed {
		t.Errorf("Expected CLOSED after ResetAll, got %s", cb.GetState())
	}
}

func TestRetryWithBackoffSuccess(t *testing.T) {
	ctx := context.Background()
	attempts := 0
	err := RetryWithBackoff(ctx, &RetryConfig{
		MaxRetries:    3,
		InitialDelay:  1 * time.Millisecond,
		MaxDelay:      10 * time.Millisecond,
		BackoffFactor: 2.0,
	}, func() error {
		attempts++
		return nil
	})
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	if attempts != 1 {
		t.Errorf("Expected 1 attempt, got %d", attempts)
	}
}

func TestRetryWithBackoffEventualSuccess(t *testing.T) {
	ctx := context.Background()
	attempts := 0
	err := RetryWithBackoff(ctx, &RetryConfig{
		MaxRetries:    3,
		InitialDelay:  1 * time.Millisecond,
		MaxDelay:      10 * time.Millisecond,
		BackoffFactor: 2.0,
	}, func() error {
		attempts++
		if attempts < 3 {
			return errors.New("transient error")
		}
		return nil
	})
	if err != nil {
		t.Errorf("Expected no error after eventual success, got %v", err)
	}
	if attempts != 3 {
		t.Errorf("Expected 3 attempts, got %d", attempts)
	}
}

func TestRetryWithBackoffMaxRetriesExceeded(t *testing.T) {
	ctx := context.Background()
	attempts := 0
	err := RetryWithBackoff(ctx, &RetryConfig{
		MaxRetries:    2,
		InitialDelay:  1 * time.Millisecond,
		MaxDelay:      10 * time.Millisecond,
		BackoffFactor: 2.0,
	}, func() error {
		attempts++
		return errors.New("persistent error")
	})
	if err == nil {
		t.Error("Expected error when max retries exceeded, got nil")
	}
	// attempts = MaxRetries+1
	if attempts != 3 {
		t.Errorf("Expected 3 attempts (0..MaxRetries), got %d", attempts)
	}
}

func TestRetryWithBackoffContextCancelled(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel() // cancel immediately

	err := RetryWithBackoff(ctx, &RetryConfig{
		MaxRetries:    5,
		InitialDelay:  1 * time.Millisecond,
		MaxDelay:      10 * time.Millisecond,
		BackoffFactor: 2.0,
	}, func() error {
		return errors.New("error")
	})
	if err == nil {
		t.Error("Expected error when context is cancelled")
	}
}

func TestRetryWithBackoffNilConfig(t *testing.T) {
	ctx := context.Background()
	calls := 0
	// Nil config should fall back to defaults without panicking
	_ = RetryWithBackoff(ctx, nil, func() error {
		calls++
		return nil
	})
	if calls == 0 {
		t.Error("Expected function to be called at least once")
	}
}

func TestAddJitter(t *testing.T) {
	base := 100 * time.Millisecond
	// Run several iterations to confirm the result is either base±25%
	for i := 0; i < 20; i++ {
		result := addJitter(base)
		low := time.Duration(float64(base) * 0.75)
		high := time.Duration(float64(base) * 1.25)
		if result < low || result > high {
			t.Errorf("addJitter(%v) = %v, want in range [%v, %v]", base, result, low, high)
		}
	}
}
