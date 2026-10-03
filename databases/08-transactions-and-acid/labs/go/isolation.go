// Package isolation: the retry loop every Repeatable Read or Serializable transaction needs, written with pgx.
package isolation

import (
	"context"
	"errors"
	"time"

	"github.com/jackc/pgx/v5/pgconn"
)

// PostgreSQL's error codes (SQLSTATE) for the outcomes concurrency makes normal.
const (
	SerializationFailure = "40001"
	DeadlockDetected     = "40P01"
	LockNotAvailable     = "55P03"
)

// Code returns the SQLSTATE of a PostgreSQL error, however deeply it's wrapped, or "" for any other error.
func Code(err error) string {
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		return pgErr.Code
	}
	return ""
}

// WithRetry runs work again while PostgreSQL says the transaction should be retried, backing off each time.
// work must run the whole transaction, from BEGIN to COMMIT, and roll back if it fails.
func WithRetry(ctx context.Context, attempts int, work func() error) error {
	for attempt := 1; ; attempt++ {
		err := work()
		if err == nil || attempt == attempts || (Code(err) != SerializationFailure && Code(err) != DeadlockDetected) {
			return err
		}
		select {
		case <-time.After(time.Duration(10<<attempt) * time.Millisecond):
		case <-ctx.Done():
			return ctx.Err()
		}
	}
}
