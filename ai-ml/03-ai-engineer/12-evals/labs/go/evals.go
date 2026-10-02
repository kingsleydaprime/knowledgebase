// Package evals: an eval harness — golden set, exact-match scoring, error bars, case-by-case
// comparison, a CI gate, baselines, and the checks on an LLM judge. Reads the shared golden set.
package evals

import (
	"bufio"
	"cmp"
	"encoding/json"
	"fmt"
	"maps"
	"math"
	"os"
	"regexp"
	"slices"
	"strings"
)

type Case struct {
	ID     string   `json:"id"`
	Ticket string   `json:"ticket"`
	Label  string   `json:"label"`
	Tags   []string `json:"tags"`
}

// Classify returns the model's raw reply for a ticket.
type Classify func(ticket string) (string, error)

func LoadGolden(path string) ([]Case, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var cases []Case
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		if strings.TrimSpace(scanner.Text()) == "" {
			continue
		}
		var c Case
		if err := json.Unmarshal(scanner.Bytes(), &c); err != nil {
			return nil, err
		}
		cases = append(cases, c)
	}
	return cases, scanner.Err()
}

var label = regexp.MustCompile(`\b(bug|billing|feature|other)\b`)

// ParseLabel returns the one label in the reply, or "" if there are none or several.
func ParseLabel(reply string) string {
	found := slices.Compact(slices.Sorted(slices.Values(label.FindAllString(strings.ToLower(reply), -1))))
	if len(found) != 1 {
		return ""
	}
	return found[0]
}

// Wilson gives where the true pass rate probably lies (95%), given a small sample.
func Wilson(passed, total int) (low, high float64) {
	if total == 0 {
		return 0, 1
	}
	const z = 1.96
	n, p := float64(total), float64(passed)/float64(total)
	centre := p + z*z/(2*n)
	spread := z * math.Sqrt(p*(1-p)/n+z*z/(4*n*n))
	return (centre - spread) / (1 + z*z/n), (centre + spread) / (1 + z*z/n)
}

type CaseResult struct {
	ID, Expected, Got, Reply string
	Pass                     bool
}

type Result struct {
	Results []CaseResult
	ByTag   map[string][2]int // tag -> {passed, total}
}

func (r Result) Passed() (n int) {
	for _, c := range r.Results {
		if c.Pass {
			n++
		}
	}
	return n
}

func (r Result) Rate() float64 { return float64(r.Passed()) / float64(len(r.Results)) }

func RunEval(classify Classify, cases []Case) (Result, error) {
	result := Result{ByTag: map[string][2]int{}}
	for _, c := range cases {
		reply, err := classify(c.Ticket)
		if err != nil {
			return result, fmt.Errorf("case %s: %w", c.ID, err)
		}
		got := ParseLabel(reply)
		pass := got == c.Label
		result.Results = append(result.Results, CaseResult{c.ID, c.Label, got, reply, pass})
		for _, tag := range c.Tags {
			counts := result.ByTag[tag]
			if pass {
				counts[0]++
			}
			counts[1]++
			result.ByTag[tag] = counts
		}
	}
	return result, nil
}

// Compare lists what a change fixed and what it broke.
func Compare(before, after Result) (fixed, broke []string) {
	was := map[string]bool{}
	for _, r := range before.Results {
		was[r.ID] = r.Pass
	}
	for _, r := range after.Results {
		passedBefore, seen := was[r.ID]
		switch {
		case seen && r.Pass && !passedBefore:
			fixed = append(fixed, r.ID)
		case seen && !r.Pass && passedBefore:
			broke = append(broke, r.ID)
		}
	}
	return fixed, broke
}

// Gate returns the reasons to fail the build; none means the change may merge.
func Gate(result Result, minRate float64, baseline *Result, mustPass ...string) []string {
	var reasons []string
	if result.Rate() < minRate {
		reasons = append(reasons, fmt.Sprintf("pass rate %.0f%% is below the floor of %.0f%%", result.Rate()*100, minRate*100))
	}
	if baseline != nil {
		if _, broke := Compare(*baseline, result); len(broke) > 0 {
			reasons = append(reasons, "regressed on "+strings.Join(broke, ", "))
		}
	}
	for _, id := range mustPass {
		if i := slices.IndexFunc(result.Results, func(r CaseResult) bool { return r.ID == id }); i < 0 || !result.Results[i].Pass {
			reasons = append(reasons, "must-pass case "+id+" failed")
		}
	}
	return reasons
}

// Majority always answers with the most common label (ties go to the alphabetically first).
func Majority(cases []Case) Classify {
	counts := map[string]int{}
	for _, c := range cases {
		counts[c.Label]++
	}
	labels := slices.Sorted(maps.Keys(counts))
	top := slices.MaxFunc(labels, func(a, b string) int { return cmp.Or(cmp.Compare(counts[a], counts[b]), cmp.Compare(b, a)) })
	return func(string) (string, error) { return top, nil }
}

var (
	billingWords = regexp.MustCompile(`charg|refund|invoice|pay|price|subscription|discount|receipt`)
	bugWords     = regexp.MustCompile(`crash|error|broken|bug|blank|empty|doesn't work|not working`)
	featureWords = regexp.MustCompile(`add|would be great|should support|could you|please support`)
)

// Keywords is the rule-based baseline.
func Keywords(ticket string) (string, error) {
	t := strings.ToLower(ticket)
	switch {
	case billingWords.MatchString(t):
		return "billing", nil
	case bugWords.MatchString(t):
		return "bug", nil
	case featureWords.MatchString(t):
		return "feature", nil
	}
	return "other", nil
}

var (
	firstWord  = regexp.MustCompile(`(?i)\bfirst\b`)
	secondWord = regexp.MustCompile(`(?i)\bsecond\b`)
)

// Pairwise asks in both orders, so a judge that prefers whatever comes first is caught.
func Pairwise(ask func(prompt string) string, ticket, a, b string) string {
	prompt := func(first, second string) string {
		return fmt.Sprintf("Which support reply is better for this ticket? Answer only FIRST or SECOND.\n"+
			"<ticket>\n%s\n</ticket>\n<first>\n%s\n</first>\n<second>\n%s\n</second>", ticket, first, second)
	}
	pick := func(answer string) string {
		switch {
		case firstWord.MatchString(answer):
			return "first"
		case secondWord.MatchString(answer):
			return "second"
		}
		return ""
	}
	switch [2]string{pick(ask(prompt(a, b))), pick(ask(prompt(b, a)))} {
	case [2]string{"first", "second"}:
		return "a"
	case [2]string{"second", "first"}:
		return "b"
	}
	return "inconsistent"
}

// Agreement returns the share of items two graders agree on, and Cohen's kappa.
func Agreement(judge, human []bool) (agree, kappa float64) {
	n := float64(len(judge))
	var same, judgeYes, humanYes float64
	for i := range judge {
		if judge[i] == human[i] {
			same++
		}
		if judge[i] {
			judgeYes++
		}
		if human[i] {
			humanYes++
		}
	}
	agree = same / n
	chance := (judgeYes/n)*(humanYes/n) + (1-judgeYes/n)*(1-humanYes/n)
	if chance == 1 {
		return agree, 1
	}
	return agree, (agree - chance) / (1 - chance)
}
