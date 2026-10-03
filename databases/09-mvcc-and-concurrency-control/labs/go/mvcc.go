// Package mvcc: reading a PostgreSQL error's SQLSTATE through pgx, for the outcomes MVCC makes normal.
package mvcc

import (
	"errors"

	"github.com/jackc/pgx/v5/pgconn"
)

const (
	DeadlockDetected = "40P01"
	LockNotAvailable = "55P03"
)

// Code returns the SQLSTATE of a PostgreSQL error, however deeply it's wrapped, or "" for any other error.
func Code(err error) string {
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		return pgErr.Code
	}
	return ""
}
