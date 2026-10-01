// Package audit: dependencies are struct fields, set once, in main. No container.
package audit

import (
	"context"
	"fmt"
	"sync"
)

// Log is a dependency. Real code might write to a database; tests use this.
type Log struct {
	mu      sync.Mutex
	Entries []string
}

func (l *Log) Add(entry string) {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.Entries = append(l.Entries, entry)
}

// BuggyService stores per-request data on a value shared by every request.
type BuggyService struct {
	Log         *Log
	CurrentUser string // BUG: one field, many concurrent requests
}

func (s *BuggyService) Record(action string) {
	s.Log.Add(fmt.Sprintf("%s: %s", s.CurrentUser, action))
}

// Service takes request data as an argument — the fix.
type Service struct{ Log *Log }

func (s *Service) Record(user, action string) {
	s.Log.Add(fmt.Sprintf("%s: %s", user, action))
}

// For data every layer needs, Go passes a context.Context down every call.
type userKey struct{}

func WithUser(ctx context.Context, user string) context.Context {
	return context.WithValue(ctx, userKey{}, user)
}

func (s *Service) RecordFromContext(ctx context.Context, action string) {
	user, _ := ctx.Value(userKey{}).(string)
	s.Record(user, action)
}
