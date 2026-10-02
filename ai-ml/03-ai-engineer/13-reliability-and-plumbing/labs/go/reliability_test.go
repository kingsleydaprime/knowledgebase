package reliability

import (
	"context"
	"errors"
	"net"
	"slices"
	"testing"
	"testing/synctest"
	"time"

	"evals" // the evals lab's keyword rules, as the fallback
)

const ms = time.Millisecond

// flaky fails with each status in turn, then answers.
type flaky struct {
	statuses []int
	reply    string
	calls    []int
}

func (f *flaky) run(context.Context) (string, error) {
	if i := len(f.calls); i < len(f.statuses) {
		f.calls = append(f.calls, f.statuses[i])
		return "", &CallError{Status: f.statuses[i]}
	}
	f.calls = append(f.calls, 200)
	return f.reply, nil
}

func half() float64 { return 0.5 }
func top() float64  { return 0.999999 }

func TestOnlyFailuresASecondTryCouldFixAreRetryable(t *testing.T) {
	for _, s := range []int{408, 429, 500, 502, 503, 529} {
		if !IsRetryable(&CallError{Status: s}) {
			t.Errorf("%d should be retryable", s)
		}
	}
	for _, s := range []int{400, 401, 403, 404, 422} {
		if IsRetryable(&CallError{Status: s}) {
			t.Errorf("%d should not be retryable", s)
		}
	}
	if !IsRetryable(context.DeadlineExceeded) || !IsRetryable(&net.OpError{Op: "dial", Err: errors.New("refused")}) {
		t.Error("timeouts and connection failures should be retryable")
	}
	if IsRetryable(errors.New("a bug in our code")) {
		t.Error("an unknown error should not be retried")
	}
}

func TestRetryAfterComesAsSecondsOrADate(t *testing.T) {
	now := time.Date(2026, 10, 2, 12, 0, 0, 0, time.UTC)
	if w, _ := ParseRetryAfter("7", now); w != 7000*ms {
		t.Errorf("got %v", w)
	}
	if w, _ := ParseRetryAfter("Fri, 02 Oct 2026 12:00:30 GMT", now); w != 30_000*ms {
		t.Errorf("got %v", w)
	}
	if _, ok := ParseRetryAfter("soon", now); ok {
		t.Error("nonsense should give no wait")
	}
}

func TestBackoffCeilingsDoubleUpToACap(t *testing.T) {
	var got []time.Duration
	for n := 1; n <= 6; n++ {
		got = append(got, Backoff(n, 500*ms, 10*time.Second, top))
	}
	want := []time.Duration{500 * ms, 1000 * ms, 2000 * ms, 4000 * ms, 8000 * ms, 10000 * ms}
	if !slices.Equal(got, want) {
		t.Errorf("got %v", got)
	}
}

// Inside a synctest bubble the clock is fake: time only moves when every goroutine is blocked,
// and then it jumps straight to the next timer. Real time.Sleep, real contexts, no waiting.
func TestATransientFailureIsRetriedUntilItSucceeds(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		start := time.Now()
		model := &flaky{statuses: []int{503, 429}, reply: "billing"}
		var slept []time.Duration
		reply, err := Retry(t.Context(), RetryOptions{Random: half, OnRetry: func(_ int, w time.Duration, _ error) { slept = append(slept, w) }},
			func(ctx context.Context, _ int) (string, error) { return model.run(ctx) })
		if err != nil || reply != "billing" || !slices.Equal(model.calls, []int{503, 429, 200}) {
			t.Fatalf("got %q %v %v", reply, err, model.calls)
		}
		if !slices.Equal(slept, []time.Duration{250 * ms, 500 * ms}) || time.Since(start) != 750*ms {
			t.Errorf("slept %v, elapsed %v", slept, time.Since(start))
		}
	})
}

func TestA400FailsAtOnce(t *testing.T) {
	model := &flaky{statuses: []int{400}}
	_, err := Retry(t.Context(), RetryOptions{}, func(ctx context.Context, _ int) (string, error) { return model.run(ctx) })
	if ce, ok := errors.AsType[*CallError](err); !ok || ce.Status != 400 || len(model.calls) != 1 {
		t.Errorf("got %v after %d calls", err, len(model.calls))
	}
}

func TestRetryAfterBeatsOurGuessAndAttemptsRunOut(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		start, calls := time.Now(), 0
		_, err := Retry(t.Context(), RetryOptions{MaxAttempts: 3}, func(context.Context, int) (string, error) {
			calls++
			return "", &CallError{Status: 429, RetryAfter: 7 * time.Second}
		})
		if err == nil || calls != 3 || time.Since(start) != 14*time.Second {
			t.Errorf("err %v, %d calls, %v", err, calls, time.Since(start))
		}
	})
}

func TestTheDeadlineStopsAWaitThatWouldOverrunIt(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		ctx, cancel := context.WithTimeout(t.Context(), 5*time.Second) // the caller's deadline travels in ctx
		defer cancel()
		start, model := time.Now(), &flaky{statuses: []int{503, 503, 503, 503}}
		_, err := Retry(ctx, RetryOptions{MaxAttempts: 10, Base: time.Second, Random: top},
			func(ctx context.Context, _ int) (string, error) { return model.run(ctx) })
		if err == nil || len(model.calls) != 3 || time.Since(start) != 3*time.Second {
			t.Errorf("err %v, %d calls, %v", err, len(model.calls), time.Since(start)) // slept 1 s + 2 s; 4 s more would pass 5 s
		}
	})
}

func TestATimeoutCancelsACallThatWouldHang(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		hangs := func(ctx context.Context) (string, error) {
			<-ctx.Done() // a well-behaved call: it gives up when its context does
			return "", ctx.Err()
		}
		if _, err := WithTimeout(t.Context(), 20*ms, hangs); !errors.Is(err, context.DeadlineExceeded) {
			t.Errorf("got %v", err)
		}
	})
}

func TestTheBreakerOpensThenTestsRecoveryWithOneTrial(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		b := &Breaker{Threshold: 3, CoolDown: 30 * time.Second}
		down := &flaky{statuses: []int{503, 503, 503, 503, 503}}
		run := func() (string, error) { return down.run(t.Context()) }
		for range 3 {
			Call(b, run)
		}
		if _, err := Call(b, run); b.Current() != "open" || !errors.Is(err, ErrCircuitOpen) || len(down.calls) != 3 {
			t.Fatalf("state %s, err %v, %d calls", b.Current(), err, len(down.calls))
		}
		time.Sleep(30 * time.Second)
		if b.Current() != "half-open" {
			t.Fatal(b.Current())
		}
		if Call(b, run); b.Current() != "open" {
			t.Fatal("a failed trial should open it again")
		}
		time.Sleep(30 * time.Second)
		if reply, _ := Call(b, func() (string, error) { return "ok", nil }); reply != "ok" || b.Current() != "closed" {
			t.Fatal("a good trial should close it")
		}
	})
}

func TestA400DoesNotTripTheBreaker(t *testing.T) {
	b := &Breaker{Threshold: 2, CoolDown: time.Minute}
	bad := &flaky{statuses: []int{400, 400, 400}}
	for range 3 {
		Call(b, func() (string, error) { return bad.run(t.Context()) })
	}
	if b.Current() != "closed" {
		t.Error(b.Current())
	}
}

func TestFallbackTriesEachOptionAndWontHideABadRequest(t *testing.T) {
	var failures []string
	by, value, err := FirstThatWorks(t.Context(), []Option[string]{
		{"primary", (&flaky{statuses: []int{503}}).run},
		{"secondary", (&flaky{reply: "bug"}).run},
	}, func(name string, err error) { failures = append(failures, name+": "+err.Error()) })
	if by != "secondary" || value != "bug" || err != nil || !slices.Equal(failures, []string{"primary: HTTP 503"}) {
		t.Errorf("%s %s %v %v", by, value, err, failures)
	}
	_, _, err = FirstThatWorks(t.Context(), []Option[string]{{"primary", (&flaky{statuses: []int{400}}).run}, {"secondary", (&flaky{}).run}}, nil)
	if ce, ok := errors.AsType[*CallError](err); !ok || ce.Status != 400 {
		t.Errorf("a 400 should come straight back, got %v", err)
	}
}

func TestAllTheLayersTogether(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		var lines []string
		model := &flaky{statuses: slices.Repeat([]int{503}, 20)}
		classify := Resilient("model", func(ctx context.Context, _ string) (string, error) { return model.run(ctx) }, Layers{
			Timeout:  time.Second,
			Retry:    RetryOptions{Random: half, MaxAttempts: 3},
			Breaker:  &Breaker{Threshold: 4, CoolDown: 30 * time.Second},
			Fallback: evals.Keywords,
			Log:      func(line string) { lines = append(lines, line) },
		})
		if by, label, _ := classify(t.Context(), "I was charged twice."); by != "fallback" || label != "billing" || len(model.calls) != 3 {
			t.Fatalf("%s %s after %d calls", by, label, len(model.calls))
		}
		if by, label, _ := classify(t.Context(), "The app crashes on start."); by != "fallback" || label != "bug" || len(model.calls) != 4 {
			t.Fatalf("%s %s after %d calls", by, label, len(model.calls))
		}
		want := []string{
			"model: attempt 1 failed (HTTP 503), retrying in 250 ms",
			"model: attempt 2 failed (HTTP 503), retrying in 500 ms",
			"model: gave up (HTTP 503)",
			"model: attempt 1 failed (HTTP 503), retrying in 250 ms",
			"model: gave up (CircuitOpenError)",
		}
		if !slices.Equal(lines, want) {
			t.Errorf("got %q", lines)
		}
	})
}

func TestATokenBucketAllowsABurstThenPaces(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		start, bucket := time.Now(), NewTokenBucket(3, 1)
		var started []time.Duration
		for range 6 {
			bucket.Take(t.Context(), 1)
			started = append(started, time.Since(start))
		}
		if !slices.Equal(started, []time.Duration{0, 0, 0, 1000 * ms, 2000 * ms, 3000 * ms}) {
			t.Errorf("got %v", started)
		}
		if _, err := bucket.TryTake(5); err == nil {
			t.Error("a cost bigger than the bucket should be an error")
		}
	})
}
