// Package practices: rate limiting with golang.org/x/time/rate (the Go team's token bucket)
// and structured, redacted logging with log/slog (standard library since Go 1.21).
package practices

import (
	"io"
	"log/slog"
	"regexp"
	"time"

	"golang.org/x/time/rate"
)

// NewLimiter: bursts of 3, refilling at 0.5 tokens per second.
func NewLimiter() *rate.Limiter { return rate.NewLimiter(rate.Limit(0.5), 3) }

// Allow takes the time as an argument, so tests control the clock. It returns how long to wait if not.
func Allow(l *rate.Limiter, now time.Time) (ok bool, retryAfter time.Duration) {
	r := l.ReserveN(now, 1)
	if delay := r.DelayFrom(now); delay > 0 {
		r.CancelAt(now) // give the token back: we're refusing, not queueing
		return false, delay
	}
	return true, 0
}

var secretKey = regexp.MustCompile(`(?i)token|password|secret|authorization|card`)

// NewLogger writes one JSON object per line and redacts secret-looking keys centrally.
func NewLogger(w io.Writer) *slog.Logger {
	return slog.New(slog.NewJSONHandler(w, &slog.HandlerOptions{
		ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
			if a.Key == slog.TimeKey {
				return slog.Attr{} // drop the timestamp so the test output is stable
			}
			if secretKey.MatchString(a.Key) {
				return slog.String(a.Key, "[redacted]")
			}
			return a
		},
	}))
}
