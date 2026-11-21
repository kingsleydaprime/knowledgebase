// Package reliability: retry, timeout, circuit breaker, fallback and token bucket around a model call,
// with the deadline carried by a context.Context instead of passed around as a number.
package reliability

import (
	"cmp"
	"context"
	"errors"
	"fmt"
	"math"
	"math/rand/v2"
	"net"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// CallError is a failed model call: its HTTP status, and the Retry-After wait if the server sent one.
type CallError struct {
	Status     int
	RetryAfter time.Duration // 0 when the server didn't say
}

func (e *CallError) Error() string { return fmt.Sprintf("HTTP %d", e.Status) }

// ErrCircuitOpen is returned without calling, while the breaker is open.
var ErrCircuitOpen = errors.New("circuit open: not calling a dependency that keeps failing")

// IsRetryable: could the same request succeed if sent again?
func IsRetryable(err error) bool {
	if ce, ok := errors.AsType[*CallError](err); ok {
		return ce.Status == 408 || ce.Status == 429 || ce.Status >= 500
	}
	if errors.Is(err, context.DeadlineExceeded) {
		return true // one attempt's own timeout; Retry checks separately whether the caller's deadline has passed
	}
	_, noResponse := errors.AsType[*net.OpError](err) // DNS, refused, reset
	return noResponse
}

// ParseRetryAfter reads seconds or an HTTP date. ok is false when there is no usable value.
func ParseRetryAfter(header string, now time.Time) (wait time.Duration, ok bool) {
	header = strings.TrimSpace(header)
	if header == "" {
		return 0, false
	}
	if seconds, err := strconv.ParseFloat(header, 64); err == nil {
		return max(0, time.Duration(seconds*float64(time.Second))), true
	}
	if date, err := http.ParseTime(header); err == nil {
		return max(0, date.Sub(now)), true
	}
	return 0, false
}

// Backoff is full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)).
func Backoff(attempt int, base, cap time.Duration, random func() float64) time.Duration {
	ceiling := math.Min(float64(cap), float64(base)*math.Pow(2, float64(attempt-1)))
	return time.Duration(math.Round(random()*ceiling/1e6)) * time.Millisecond // whole milliseconds, as in the other labs
}

type RetryOptions struct {
	MaxAttempts int // every try, including the first
	Base, Cap   time.Duration
	Random      func() float64
	OnRetry     func(attempt int, wait time.Duration, err error)
}

// Retry calls until success, a permanent error, the attempt limit, or the context's deadline.
// The deadline isn't an option: it's whatever deadline the caller's context carries.
func Retry[T any](ctx context.Context, o RetryOptions, call func(ctx context.Context, attempt int) (T, error)) (T, error) {
	o.MaxAttempts = cmp.Or(o.MaxAttempts, 3)
	o.Base, o.Cap = cmp.Or(o.Base, 500*time.Millisecond), cmp.Or(o.Cap, 10*time.Second)
	if o.Random == nil {
		o.Random = rand.Float64
	}
	for attempt := 1; ; attempt++ {
		result, err := call(ctx, attempt)
		if err == nil || ctx.Err() != nil || !IsRetryable(err) || attempt >= o.MaxAttempts {
			return result, err
		}
		wait := Backoff(attempt, o.Base, o.Cap, o.Random)
		if ce, ok := errors.AsType[*CallError](err); ok && ce.RetryAfter > 0 {
			wait = ce.RetryAfter // the server knows best
		}
		if deadline, ok := ctx.Deadline(); ok && time.Now().Add(wait).After(deadline) {
			return result, err // waiting would blow the deadline: fail now
		}
		if o.OnRetry != nil {
			o.OnRetry(attempt, wait, err)
		}
		if err := sleep(ctx, wait); err != nil {
			return result, err
		}
	}
}

func sleep(ctx context.Context, d time.Duration) error {
	timer := time.NewTimer(d)
	defer timer.Stop()
	select {
	case <-timer.C:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// WithTimeout gives one attempt its own deadline. Go can't stop a goroutine from outside, so the
// call must honour ctx — http.NewRequestWithContext does, and aborts the request when it expires.
func WithTimeout[T any](ctx context.Context, d time.Duration, call func(ctx context.Context) (T, error)) (T, error) {
	ctx, cancel := context.WithTimeout(ctx, d)
	defer cancel()
	return call(ctx)
}

type Breaker struct {
	Threshold int
	CoolDown  time.Duration

	mu           sync.Mutex // many goroutines share one breaker
	state        string
	failures     int
	openedAt     time.Time
	trialRunning bool
}

func (b *Breaker) Current() string {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.current()
}

func (b *Breaker) current() string {
	if b.state == "" {
		b.state = "closed"
	}
	if b.state == "open" && time.Since(b.openedAt) >= b.CoolDown {
		b.state = "half-open"
	}
	return b.state
}

// Call runs fn unless the breaker is open. A free function because Go methods can't have type parameters.
func Call[T any](b *Breaker, fn func() (T, error)) (T, error) {
	var zero T
	b.mu.Lock()
	state := b.current()
	if state == "open" || (state == "half-open" && b.trialRunning) {
		b.mu.Unlock()
		return zero, ErrCircuitOpen
	}
	if state == "half-open" {
		b.trialRunning = true
	}
	b.mu.Unlock()

	result, err := fn()

	b.mu.Lock()
	defer b.mu.Unlock()
	if state == "half-open" {
		b.trialRunning = false
	}
	switch {
	case err == nil:
		b.state, b.failures = "closed", 0
	case IsRetryable(err): // a 400 is our bug, not the provider's outage
		b.failures++
		if state == "half-open" || b.failures >= b.Threshold {
			b.state, b.openedAt = "open", time.Now()
		}
	}
	return result, err
}

type Option[T any] struct {
	Name string
	Run  func(ctx context.Context) (T, error)
}

// FirstThatWorks tries each option in turn. A 400 or 422 is returned at once: every option would reject it.
func FirstThatWorks[T any](ctx context.Context, options []Option[T], onFailure func(name string, err error)) (string, T, error) {
	var errs []error
	for _, o := range options {
		value, err := o.Run(ctx)
		if err == nil {
			return o.Name, value, nil
		}
		if ce, ok := errors.AsType[*CallError](err); ok && (ce.Status == 400 || ce.Status == 422) {
			return "", value, err
		}
		if onFailure != nil {
			onFailure(o.Name, err)
		}
		errs = append(errs, err)
	}
	var zero T
	return "", zero, fmt.Errorf("all %d options failed: %w", len(options), errors.Join(errs...))
}

// TokenBucket paces requests under a rate limit. golang.org/x/time/rate is the production version.
type TokenBucket struct {
	mu        sync.Mutex
	capacity  float64
	perSecond float64
	tokens    float64
	last      time.Time
}

func NewTokenBucket(capacity, perSecond float64) *TokenBucket {
	return &TokenBucket{capacity: capacity, perSecond: perSecond, tokens: capacity, last: time.Now()}
}

// TryTake takes cost tokens and returns 0, or takes nothing and returns how long until there are enough.
func (b *TokenBucket) TryTake(cost float64) (time.Duration, error) {
	if cost > b.capacity {
		return 0, fmt.Errorf("a cost of %g can never fit a bucket of %g", cost, b.capacity)
	}
	b.mu.Lock()
	defer b.mu.Unlock()
	now := time.Now()
	b.tokens = min(b.capacity, b.tokens+now.Sub(b.last).Seconds()*b.perSecond)
	b.last = now
	if b.tokens >= cost {
		b.tokens -= cost
		return 0, nil
	}
	return time.Duration(math.Ceil((cost-b.tokens)/b.perSecond*1000)) * time.Millisecond, nil
}

func (b *TokenBucket) Take(ctx context.Context, cost float64) error {
	for {
		wait, err := b.TryTake(cost)
		if err != nil || wait == 0 {
			return err
		}
		if err := sleep(ctx, wait); err != nil {
			return err
		}
	}
}

type Layers struct {
	Timeout  time.Duration
	Retry    RetryOptions
	Breaker  *Breaker
	Fallback func(input string) (string, error)
	Log      func(line string)
}

// Resilient wraps call as fallback( retry( breaker( timeout( call ) ) ) ).
func Resilient(name string, call func(ctx context.Context, input string) (string, error), l Layers) func(ctx context.Context, input string) (string, string, error) {
	log := l.Log
	if log == nil {
		log = func(string) {}
	}
	retry := l.Retry
	retry.OnRetry = func(attempt int, wait time.Duration, err error) {
		log(fmt.Sprintf("%s: attempt %d failed (%s), retrying in %d ms", name, attempt, describe(err), wait.Milliseconds()))
	}
	return func(ctx context.Context, input string) (string, string, error) {
		options := []Option[string]{{Name: name, Run: func(ctx context.Context) (string, error) {
			return Retry(ctx, retry, func(ctx context.Context, _ int) (string, error) {
				return Call(l.Breaker, func() (string, error) {
					return WithTimeout(ctx, l.Timeout, func(ctx context.Context) (string, error) { return call(ctx, input) })
				})
			})
		}}}
		if l.Fallback != nil {
			options = append(options, Option[string]{Name: "fallback", Run: func(context.Context) (string, error) { return l.Fallback(input) }})
		}
		return FirstThatWorks(ctx, options, func(by string, err error) { log(fmt.Sprintf("%s: gave up (%s)", by, describe(err))) })
	}
}

func describe(err error) string {
	if ce, ok := errors.AsType[*CallError](err); ok {
		return ce.Error()
	}
	if errors.Is(err, ErrCircuitOpen) {
		return "CircuitOpenError"
	}
	return err.Error()
}
