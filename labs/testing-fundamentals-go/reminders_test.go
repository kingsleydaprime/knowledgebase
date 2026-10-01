package reminders

import (
	"testing"
	"time"
)

func day(y int, m time.Month, d int) time.Time { return time.Date(y, m, d, 0, 0, 0, 0, time.UTC) }

// Table-driven: the idiomatic Go test — one function, many named cases.
func TestDayAfter(t *testing.T) {
	cases := []struct {
		name     string
		in, want time.Time
	}{
		{"month end", day(2026, 10, 31), day(2026, 11, 1)},
		{"year end", day(2026, 12, 31), day(2027, 1, 1)},
		{"leap day", day(2028, 2, 28), day(2028, 2, 29)},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := DayAfter(c.in); !got.Equal(c.want) {
				t.Fatalf("DayAfter(%v) = %v, want %v", c.in, got, c.want)
			}
		})
	}
}

// Hand-written doubles: Go's culture prefers these to mocking libraries.
type stubUsers []User

func (s stubUsers) ListOnTrial() []User { return s }

type spyMailer struct{ sent []string }

func (s *spyMailer) Send(to, subject string) { s.sent = append(s.sent, to+" | "+subject) }

func TestSendTrialReminders(t *testing.T) {
	users := stubUsers{{"ada@x.com", day(2026, 11, 1)}, {"bayo@x.com", day(2026, 11, 5)}}
	mailer := &spyMailer{}
	fakeNow := func() time.Time { return time.Date(2026, 10, 31, 12, 0, 0, 0, time.UTC) }

	if n := SendTrialReminders(users, mailer, fakeNow); n != 1 {
		t.Fatalf("sent %d, want 1", n)
	}
	if len(mailer.sent) != 1 || mailer.sent[0] != "ada@x.com | Your trial ends tomorrow" {
		t.Fatalf("mailer saw %v", mailer.sent)
	}
}
