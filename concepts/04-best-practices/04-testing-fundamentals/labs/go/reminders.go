// Package reminders: the clock is a function value; collaborators are small interfaces.
package reminders

import "time"

type User struct {
	Email       string
	TrialEndsOn time.Time // midnight UTC
}

type UserSource interface{ ListOnTrial() []User }
type Mailer interface{ Send(to, subject string) }

func DayAfter(t time.Time) time.Time {
	y, m, d := t.UTC().Date()
	return time.Date(y, m, d+1, 0, 0, 0, 0, time.UTC) // time.Date normalises day 32
}

func SendTrialReminders(users UserSource, mailer Mailer, now func() time.Time) int {
	target := DayAfter(now())
	sent := 0
	for _, u := range users.ListOnTrial() {
		if u.TrialEndsOn.Equal(target) {
			mailer.Send(u.Email, "Your trial ends tomorrow")
			sent++
		}
	}
	return sent
}
