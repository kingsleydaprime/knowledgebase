package cost

import (
	"encoding/json"
	"slices"
	"strings"
	"testing"
	"testing/synctest"
	"time"

	"evals" // the shared golden set and the keyword rules
)

var sonnet = Prices["claude-sonnet-5-5"]

func TestOutputCostsFiveTimesInput(t *testing.T) {
	if got := Cost(Usage{Input: 2000, Output: 500}, sonnet).String(); got != "0.009" {
		t.Error(got)
	}
}

func TestCachingA6000TokenPrefixAcross1000Calls(t *testing.T) {
	uncached := 1000 * Cost(Usage{Input: 6150, Output: 100}, sonnet)
	cached := Cost(Usage{CacheWrite: 6000, Input: 150, Output: 100}, sonnet)
	for range 999 {
		cached += Cost(Usage{CacheRead: 6000, Input: 150, Output: 100}, sonnet)
	}
	if uncached.String() != "13.3" || cached.String() != "2.5138" { // exact, however many calls are added up
		t.Errorf("%s %s", uncached, cached)
	}
	if share := 1000 * Cost(Usage{Output: 100}, sonnet) * 100 / cached; share != 39 { // integer division: 39.78 → 39
		t.Error(share)
	}
}

func TestACacheWritePaysForItselfOnTheSecondCall(t *testing.T) {
	oneHour := sonnet
	oneHour.CacheWrite = 4_000_000 // 1-hour entries cost 2× to write
	if BreakEvenCalls(sonnet) != 2 || BreakEvenCalls(oneHour) != 3 {
		t.Error(BreakEvenCalls(sonnet), BreakEvenCalls(oneHour))
	}
}

func TestATimestampAtTheFrontLeavesNothingToCache(t *testing.T) {
	system := strings.Repeat("You classify support tickets. Label by what the team has to do next. ", 20)
	front := func(date string) string { return "Today is " + date + ".\n" + system + "\nhelp" }
	end := func(date string) string { return system + "\nToday is " + date + ".\nhelp" }
	a, b := "2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z"
	if SharedPrefix(front(a), front(b)) != 27 || SharedPrefix(end(a), end(b)) != len(system)+28 {
		t.Error(SharedPrefix(front(a), front(b)), SharedPrefix(end(a), end(b)))
	}
}

func TestJSONBytes(t *testing.T) {
	b := map[string]any{"user": map[string]any{"id": 7, "tier": "pro"}, "tools": []string{"search"}}
	if got, _ := StableJSON(b); got != `{"tools":["search"],"user":{"id":7,"tier":"pro"}}` { // maps come out sorted
		t.Error(got)
	}
	escaped, _ := json.Marshal("<ticket>")
	plain, _ := StableJSON("<ticket>")
	if string(escaped) != `"\u003cticket\u003e"` || plain != `"<ticket>"` {
		t.Error(string(escaped), plain)
	}
}

func TestACascadeFromKeywordsToABigModel(t *testing.T) {
	golden, err := evals.LoadGolden("../../../12-evals/labs/shared/golden.jsonl")
	if err != nil {
		t.Fatal(err)
	}
	label := map[string]string{}
	for _, c := range golden {
		label[c.Ticket] = c.Label
	}
	big := Tier{"big", 2_000_000_000, func(t string) (string, error) { return label[t], nil }, func(string) bool { return true }} // $0.002, always right
	cheap := Tier{"keywords", 0, evals.Keywords, func(a string) bool { return a != "other" }}
	var escalated, wrong []string
	var total Picodollars
	for _, c := range golden {
		answer, by, spent, _ := Cascade(c.Ticket, []Tier{cheap, big})
		if by == "big" {
			escalated = append(escalated, c.ID)
		}
		if answer != c.Label {
			wrong = append(wrong, c.ID)
		}
		total += spent
	}
	if !slices.Equal(escalated, []string{"t04", "t10", "t12", "t14", "t17", "t19"}) || !slices.Equal(wrong, []string{"t15", "t20"}) || total.String() != "0.012" {
		t.Error(escalated, wrong, total)
	}
}

func TestP95ShowsTheSlowCallTheMedianHides(t *testing.T) {
	var ms []time.Duration
	for _, v := range []int{1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000} {
		ms = append(ms, time.Duration(v)*time.Millisecond)
	}
	if Percentile(ms, 50) != time.Second || Percentile(ms, 95) != 9*time.Second {
		t.Error(Percentile(ms, 50), Percentile(ms, 95))
	}
}

func TestTimeToFirstTokenIsMeasuredApart(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		chunks := make(chan string)
		go func() {
			defer close(chunks)
			time.Sleep(800 * time.Millisecond) // the model reads the prompt first
			chunks <- "Your"
			for _, w := range []string{" refund", " is", " on", " its", " way."} {
				time.Sleep(100 * time.Millisecond)
				chunks <- w
			}
		}()
		text, ttft, total := TimeStream(chunks)
		if text != "Your refund is on its way." || ttft != 800*time.Millisecond || total != 1300*time.Millisecond {
			t.Error(text, ttft, total)
		}
	})
}
