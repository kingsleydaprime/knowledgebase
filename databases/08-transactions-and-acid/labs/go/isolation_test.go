package isolation

// The anomalies and their fixes through pgx, with two connections stepped one statement at a time.
// Run through ../shared/with-postgres.sh; without PGHOST these tests skip.

import (
	"context"
	"os"
	"testing"

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

func (s session) int(sql string, args ...any) int {
	s.t.Helper()
	var n int
	if err := s.conn.QueryRow(s.ctx, sql, args...).Scan(&n); err != nil {
		s.t.Fatal(sql, err)
	}
	return n
}

func sessions(t *testing.T) (session, session) {
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
	a, b := open(), open()
	a.must(`DROP TABLE IF EXISTS accounts, doctors;
		CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
		INSERT INTO accounts VALUES (1, 100), (2, 50);
		CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
		INSERT INTO doctors VALUES ('alice', true), ('bob', true)`)
	return a, b
}

const balance = "SELECT balance FROM accounts WHERE id = 1"

func TestALostUpdateAtReadCommitted(t *testing.T) {
	a, b := sessions(t)
	a.must("BEGIN")
	b.must("BEGIN")
	seenA, seenB := a.int(balance), b.int(balance)
	a.must("UPDATE accounts SET balance = $1 WHERE id = 1", seenA-10)
	a.must("COMMIT")
	b.must("UPDATE accounts SET balance = $1 WHERE id = 1", seenB-20)
	b.must("COMMIT")
	if got := a.int(balance); got != 80 {
		t.Fatal(got)
	}
}

func TestRepeatableReadRefusesTheSecondWrite(t *testing.T) {
	a, b := sessions(t)
	a.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	b.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	seenB := b.int(balance)
	a.must("UPDATE accounts SET balance = balance - 10 WHERE id = 1")
	a.must("COMMIT")
	if err := b.exec("UPDATE accounts SET balance = $1 WHERE id = 1", seenB-20); Code(err) != SerializationFailure {
		t.Fatal(err)
	}
	b.must("ROLLBACK")
}

func TestForUpdateMakesTheSecondReaderWait(t *testing.T) {
	a, b := sessions(t)
	a.must("BEGIN")
	a.must("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
	b.must("BEGIN")
	b.must("SET LOCAL lock_timeout = '100ms'")
	if err := b.exec("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE"); Code(err) != LockNotAvailable {
		t.Fatal(err)
	}
	b.must("ROLLBACK")
	a.must("COMMIT")
}

func TestWriteSkewSerializableAndRetry(t *testing.T) {
	a, b := sessions(t)
	goOffCall := func(s session, name string) error {
		if err := s.exec("BEGIN ISOLATION LEVEL SERIALIZABLE"); err != nil {
			return err
		}
		if s.int("SELECT count(*) FROM doctors WHERE on_call") >= 2 {
			return s.exec("UPDATE doctors SET on_call = false WHERE name = $1", name)
		}
		return nil
	}
	goOffCall(a, "alice")
	goOffCall(b, "bob")
	a.must("COMMIT")
	if err := b.exec("COMMIT"); Code(err) != SerializationFailure {
		t.Fatal(err)
	}
	err := WithRetry(b.ctx, 5, func() error {
		if err := goOffCall(b, "bob"); err != nil {
			b.exec("ROLLBACK")
			return err
		}
		if err := b.exec("COMMIT"); err != nil {
			b.exec("ROLLBACK")
			return err
		}
		return nil
	})
	var name string
	a.conn.QueryRow(a.ctx, "SELECT string_agg(name, ',') FROM doctors WHERE on_call").Scan(&name)
	if err != nil || name != "bob" {
		t.Fatal(err, name)
	}
}
