package audit

import (
	"context"
	"slices"
	"sync"
	"testing"
)

// Run under -race, this test fails: two goroutines write CurrentUser with no synchronisation.
func TestBuggyServiceRaces(t *testing.T) {
	svc := &BuggyService{Log: &Log{}}
	var wg sync.WaitGroup
	for _, user := range []string{"ada", "bayo"} {
		wg.Add(1)
		go func() {
			defer wg.Done()
			svc.CurrentUser = user
			svc.Record("viewed invoice")
		}()
	}
	wg.Wait()
}

func TestServiceTakesTheUserAsAnArgument(t *testing.T) {
	log := &Log{}
	svc := &Service{Log: log}
	var wg sync.WaitGroup
	for _, user := range []string{"ada", "bayo"} {
		wg.Add(1)
		go func() {
			defer wg.Done()
			svc.RecordFromContext(WithUser(context.Background(), user), "viewed invoice")
		}()
	}
	wg.Wait()
	slices.Sort(log.Entries)
	if !slices.Equal(log.Entries, []string{"ada: viewed invoice", "bayo: viewed invoice"}) {
		t.Fatalf("entries = %v", log.Entries)
	}
}
