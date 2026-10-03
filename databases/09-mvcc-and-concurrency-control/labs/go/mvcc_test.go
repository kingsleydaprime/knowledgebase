package mvcc

// MVCC through pgx: snapshots, blocked vacuum and a deadlock. Run through ../shared/with-postgres.sh.

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5"
)

type session struct {
	t    *testing.T
	ctx  context.Context
	conn *pgx.Conn
}

func (s session) exec(sql string, args ...any) error {
	_, err := s.conn.Exec(s.ctx, sql, args...)
	return err
}

func (s session) must(sql string, args ...any) {
	s.t.Helper()
	if err := s.exec(sql, args...); err != nil {
		s.t.Fatal(sql, err)
	}
}

func (s session) int(sql string, args ...any) int64 {
	s.t.Helper()
	var n int64
	if err := s.conn.QueryRow(s.ctx, sql, args...).Scan(&n); err != nil {
		s.t.Fatal(sql, err)
	}
	return n
}

func sessions(t *testing.T) (session, session, session) {
	t.Helper()
	if os.Getenv("PGHOST") == "" {
		t.Skip("no PostgreSQL: run through ../shared/with-postgres.sh")
	}
	ctx := context.Background()
	open := func() session {
		conn, err := pgx.Connect(ctx, "")
		if err != nil {
			t.Fatal(err)
		}
		t.Cleanup(func() { conn.Close(ctx) })
		return session{t, ctx, conn}
	}
	a, b, watcher := open(), open(), open()
	a.must(`CREATE EXTENSION IF NOT EXISTS pgstattuple;
		DROP TABLE IF EXISTS accounts;
		CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
		INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i`)
	a.must("VACUUM accounts") // alone: VACUUM can't run inside a multi-statement call's transaction
	return a, b, watcher
}

const balance = "SELECT balance FROM accounts WHERE id = 1"

func TestReadersDontBlockWriters(t *testing.T) {
	a, b, _ := sessions(t)
	a.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	if a.int(balance) != 100 {
		t.Fatal("before")
	}
	b.must("SET lock_timeout = '100ms'")
	b.must("UPDATE accounts SET balance = 50 WHERE id = 1") // finishes at once
	if a.int(balance) != 100 {
		t.Fatal("a's snapshot changed")
	}
	a.must("COMMIT")
	if a.int(balance) != 50 {
		t.Fatal("after")
	}
}

func TestWritersBlockWriters(t *testing.T) {
	a, b, _ := sessions(t)
	a.must("BEGIN")
	a.must("UPDATE accounts SET balance = 90 WHERE id = 1")
	b.must("SET lock_timeout = '100ms'")
	if err := b.exec("UPDATE accounts SET balance = 80 WHERE id = 1"); Code(err) != LockNotAvailable {
		t.Fatal(err)
	}
	a.must("COMMIT")
}

func TestAnOpenSnapshotStopsVacuum(t *testing.T) {
	a, b, _ := sessions(t)
	a.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	a.must("SELECT 1")
	b.must("UPDATE accounts SET balance = balance + 1")
	b.must("VACUUM accounts")
	if n := b.int("SELECT dead_tuple_count FROM pgstattuple('accounts')"); n != 1000 {
		t.Fatal(n)
	}
	a.must("COMMIT")
	b.must("VACUUM accounts")
	if n := b.int("SELECT dead_tuple_count FROM pgstattuple('accounts')"); n != 0 {
		t.Fatal(n)
	}
}

func TestADeadlockHasExactlyOneVictim(t *testing.T) {
	a, b, watcher := sessions(t)
	a.must("SET deadlock_timeout = '100ms'")
	b.must("SET deadlock_timeout = '100ms'")
	a.must("BEGIN")
	b.must("BEGIN")
	a.must("UPDATE accounts SET balance = 1 WHERE id = 1")
	b.must("UPDATE accounts SET balance = 2 WHERE id = 2")
	aDone := make(chan error, 1)
	go func() { aDone <- a.exec("UPDATE accounts SET balance = 1 WHERE id = 2") }() // a pgx.Conn is used by one goroutine at a time
	for i := 0; ; i++ {
		var event *string
		watcher.conn.QueryRow(watcher.ctx, "SELECT wait_event_type FROM pg_stat_activity WHERE pid = $1", a.conn.PgConn().PID()).Scan(&event)
		if event != nil && *event == "Lock" {
			break
		}
		if i == 500 {
			t.Fatal("a never waited")
		}
		time.Sleep(10 * time.Millisecond)
	}
	bErr := b.exec("UPDATE accounts SET balance = 2 WHERE id = 1")
	aErr := <-aDone
	victims := 0
	for _, err := range []error{aErr, bErr} {
		if Code(err) == DeadlockDetected {
			victims++
		}
	}
	if victims != 1 {
		t.Fatal(aErr, bErr)
	}
	a.exec("ROLLBACK")
	b.exec("ROLLBACK")
}
