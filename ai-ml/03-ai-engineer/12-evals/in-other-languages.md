# Evals in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/12-evals/index|evals]], which builds a golden set, an exact-match harness with Wilson intervals, a case-by-case comparison, a CI gate, two baselines and the checks on an LLM judge in TypeScript. This page builds the same harness in Python, Go, Java, Rust and C#. All of them read **the same golden set** from `labs/shared/golden.jsonl` and get **the same numbers**: 8/20 for the majority baseline, 15/20 for the keywords with the same five misses, the same gate reasons and a kappa of 0.2 for the lenient judge. It also names each ecosystem's eval tools, and shows how each keeps a slow live eval out of the fast unit tests.

## Before you start

You can already:

- Explain golden sets, baselines, Wilson intervals, the gate and Cohen's kappa → [[ai-ml/03-ai-engineer/12-evals/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Name your ecosystem's eval frameworks and statistics libraries.
2. Write the harness, the gate and the judge checks in your language.
3. Keep a slow, model-calling eval separate from the unit tests, using your test framework's own mechanism.

## The kid version

Five teachers in five schools mark the same 20 exam papers, using the same answer sheet. If they all follow the marking rules, they all give the same scores: the same 15 out of 20, the same five mistakes. If one teacher gets 14, you don't argue about which teacher is right; you go and find the rule they read differently. That's this page: one answer sheet, five languages, and identical marks as the proof that everyone marks the same way.

**Where the analogy stops working.** Teachers can disagree for good reasons. Code shouldn't. Here any difference is a bug — such as one version matching "first" inside "firstly" when the others match whole words only. That one really happened while this page was being written.

## 1. The tools, by ecosystem

| Language | Eval frameworks | Statistics | Keep the live eval out of the unit tests |
|---|---|---|---|
| TypeScript | **promptfoo** (YAML test cases, many providers), `autoevals` | by hand, as in the main lesson | a separate `live.ts` script |
| Python | **Inspect AI**, DeepEval, Ragas (RAG metrics), OpenAI Evals | **statsmodels** (`proportion_confint`, `cohens_kappa`), scikit-learn | a pytest marker, or a separate script |
| Go | none dominant; `go test` is the harness | by hand | a build tag (`//go:build eval`) or `testing.Short()` |
| Java | **Spring AI** evaluators (`RelevancyEvaluator`, `FactCheckingEvaluator`) | Apache Commons Math | a JUnit `@Tag("eval")`, excluded by default |
| Rust | none dominant; `cargo test` is the harness | by hand | `#[ignore]`, run with `cargo test -- --ignored` |
| C# | **`Microsoft.Extensions.AI.Evaluation`** (quality evaluators and reports) | by hand | an xUnit trait, filtered out by default |
| C, C++ | — | — | — |

Two points matter more than the names. First, **the harness is small**: loading cases, scoring, an interval, a comparison and a gate fit in about 150 lines in every language here. Frameworks add reporting, caching and provider plumbing on top, but they don't do anything you can't read. Second, **an eval that calls a model is slow and costs money**, so every ecosystem has a way to keep it apart from the unit tests that run on every save. Use the mechanism in the last column, and run the live eval in CI on prompt and model changes rather than on every commit.

There's no C or C++ section. Evals sit next to the application that calls the model, and that application is almost never written in C or C++, even when the inference engine underneath it is.

## 2. The shared golden set

[`labs/shared/golden.jsonl`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/12-evals/labs/shared) is JSON Lines: one case per line. That format is worth copying for your own golden sets, for three reasons. Every language reads it with a line loop and its standard JSON parser. A new case is one new line, so review diffs are clean. And a file can be appended to while a run is writing it.

Every lab asserts the same results on that file, so the five versions check each other:

| Check | Expected in every language |
|---|---|
| majority baseline | 8/20 (always "billing") |
| keyword baseline | 15/20, missing t10, t12, t14, t15 (→ feature) and t20 (→ billing) |
| Wilson interval for 17/20 | 0.64 to 0.95 |
| gate on a change that breaks t02 | "pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed" |
| pairwise with a judge that always says `FIRST` | inconsistent |
| lenient judge against the human | agreement 0.6, kappa 0.2 |

## Terms used in this lesson

1. **JSON Lines**: This is also written **JSONL**. It is a text format with one complete JSON object per line, used for datasets and logs.
2. **Eval framework**: This is a library or tool that runs eval cases against models and reports the results, such as promptfoo or Inspect AI.
3. **Test tag**: This is also called a **marker**, **trait** or **category**. It is a label on a test that lets the runner include or exclude it, so slow evals don't run with every unit test.
4. **Build tag**: In Go, this is a `//go:build` line at the top of a file. The file is only compiled when that tag is requested, for example with `go test -tags eval`.
5. **Contingency table**: This is a table counting how often two graders' answers fall into each combination: both yes, judge yes and human no, and so on. Cohen's kappa is computed from it.

## 3. Python

The harness reads like the TypeScript. The tests add something only Python makes easy: they check the hand-written Wilson interval and kappa against **statsmodels**, the standard statistics library, and get the same numbers. In your own work, call the library; write it by hand once to see what it computes.

```python
"""An eval harness: golden set, exact-match scoring, error bars, case-by-case comparison, a CI gate,
baselines, and the checks on an LLM judge. Reads the same golden set as every other language."""
import json
import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

GOLDEN = Path(__file__).parent.parent / "shared" / "golden.jsonl"
LABELS = ("bug", "billing", "feature", "other")
Classify = Callable[[str], str]  # ticket -> raw reply


def load_golden(path: Path = GOLDEN) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def parse_label(reply: str) -> str | None:
    found = set(re.findall(r"\b(bug|billing|feature|other)\b", reply.lower()))
    return found.pop() if len(found) == 1 else None


def wilson(passed: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Where the true pass rate probably lies (95%), given a small sample."""
    if total == 0:
        return 0.0, 1.0
    p = passed / total
    centre = p + z * z / (2 * total)
    spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
    return (centre - spread) / (1 + z * z / total), (centre + spread) / (1 + z * z / total)


@dataclass
class Result:
    results: list[dict]
    by_tag: dict[str, list[int]] = field(default_factory=dict)  # tag -> [passed, total]

    @property
    def passed(self) -> int:
        return sum(r["pass"] for r in self.results)

    @property
    def rate(self) -> float:
        return self.passed / len(self.results)

    @property
    def interval(self) -> tuple[float, float]:
        return wilson(self.passed, len(self.results))


def run_eval(classify: Classify, cases: list[dict]) -> Result:
    result = Result([])
    for case in cases:
        reply = classify(case["ticket"])
        got = parse_label(reply)
        result.results.append({"id": case["id"], "expected": case["label"], "got": got, "reply": reply,
                               "pass": got == case["label"]})
        for tag in case["tags"]:
            counts = result.by_tag.setdefault(tag, [0, 0])
            counts[0] += got == case["label"]
            counts[1] += 1
    return result


def compare(before: Result, after: Result) -> dict[str, list[str]]:
    was = {r["id"]: r["pass"] for r in before.results}
    return {"fixed": [r["id"] for r in after.results if r["pass"] and was.get(r["id"]) is False],
            "broke": [r["id"] for r in after.results if not r["pass"] and was.get(r["id"]) is True]}


def gate(result: Result, min_rate: float, baseline: Result | None = None, must_pass: tuple[str, ...] = ()) -> list[str]:
    """The reasons to fail the build; an empty list means the change may merge."""
    reasons = []
    if result.rate < min_rate:
        reasons.append(f"pass rate {result.rate:.0%} is below the floor of {min_rate:.0%}")
    if baseline and (broke := compare(baseline, result)["broke"]):
        reasons.append(f"regressed on {', '.join(broke)}")
    passed = {r["id"] for r in result.results if r["pass"]}
    reasons += [f"must-pass case {case_id} failed" for case_id in must_pass if case_id not in passed]
    return reasons


def majority(cases: list[dict]) -> Classify:
    top = Counter(c["label"] for c in cases).most_common(1)[0][0]
    return lambda _ticket: top


def keywords(ticket: str) -> str:
    t = ticket.lower()
    if re.search(r"charg|refund|invoice|pay|price|subscription|discount|receipt", t):
        return "billing"
    if re.search(r"crash|error|broken|bug|blank|empty|doesn't work|not working", t):
        return "bug"
    if re.search(r"add|would be great|should support|could you|please support", t):
        return "feature"
    return "other"


def pairwise(ask: Callable[[str], str], ticket: str, a: str, b: str) -> str:
    """Ask in both orders; a judge that prefers whatever comes first is caught, not trusted."""
    def prompt(first: str, second: str) -> str:
        return (f"Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n{ticket}\n"
                f"</ticket>\n<first>\n{first}\n</first>\n<second>\n{second}\n</second>")

    def pick(answer: str) -> str | None:
        return "first" if re.search(r"\bfirst\b", answer, re.I) else "second" if re.search(r"\bsecond\b", answer, re.I) else None

    forward, backward = pick(ask(prompt(a, b))), pick(ask(prompt(b, a)))
    return {("first", "second"): "a", ("second", "first"): "b"}.get((forward, backward), "inconsistent")


def agreement(judge_says: list[bool], human_says: list[bool]) -> tuple[float, float]:
    """(agreement, Cohen's kappa). Kappa removes the agreement you'd expect by chance."""
    n = len(judge_says)
    agree = sum(j == h for j, h in zip(judge_says, human_says)) / n
    judge_yes, human_yes = sum(judge_says) / n, sum(human_says) / n
    chance = judge_yes * human_yes + (1 - judge_yes) * (1 - human_yes)
    return agree, 1.0 if chance == 1 else (agree - chance) / (1 - chance)
```

```python
import unittest

from statsmodels.stats.inter_rater import cohens_kappa
from statsmodels.stats.proportion import proportion_confint

from evals import agreement, compare, gate, keywords, load_golden, majority, pairwise, parse_label, run_eval, wilson

GOLDEN = load_golden()
HUMAN = [True, True, False, False, True, False, True, False, False, True]
LENIENT = [True, True, True, True, True, True, True, True, False, True]


def with_change(ticket_part: str, label: str):
    return lambda t: label if ticket_part in t else keywords(t)


class EvalTests(unittest.TestCase):
    def test_the_shared_golden_set(self):
        self.assertEqual(len(GOLDEN), 20)
        self.assertEqual({c["label"] for c in GOLDEN}, {"bug", "billing", "feature", "other"})

    def test_parse_label(self):
        self.assertEqual(parse_label("Category: BUG"), "bug")
        self.assertIsNone(parse_label("bug or billing"))

    def test_hand_written_wilson_matches_statsmodels(self):
        for passed, total in [(17, 20), (170, 200), (8, 20), (20, 20)]:
            ours = wilson(passed, total)
            theirs = proportion_confint(passed, total, alpha=0.05, method="wilson")
            self.assertAlmostEqual(ours[0], theirs[0], places=2)
            self.assertAlmostEqual(ours[1], theirs[1], places=2)
        self.assertEqual([round(x, 2) for x in wilson(17, 20)], [0.64, 0.95])

    def test_the_baselines_give_the_same_numbers_as_every_other_language(self):
        self.assertEqual(run_eval(majority(GOLDEN), GOLDEN).passed, 8)
        rules = run_eval(keywords, GOLDEN)
        self.assertEqual(rules.passed, 15)
        self.assertEqual([f"{r['id']}:{r['got']}" for r in rules.results if not r["pass"]],
                         ["t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing"])
        self.assertEqual(rules.by_tag["other-language"], [0, 2])

    def test_compare_and_gate(self):
        base = run_eval(keywords, GOLDEN)
        self.assertEqual(compare(base, run_eval(with_change("La aplicación", "bug"), GOLDEN)), {"fixed": ["t14"], "broke": []})
        worse = run_eval(with_change("charged twice", "bug"), GOLDEN)
        self.assertEqual(gate(base, 0.6), [])
        self.assertEqual(gate(worse, 0.75, base, ("t02", "t18")),
                         ["pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed"])

    def test_pairwise_exposes_position_bias(self):
        self.assertEqual(pairwise(lambda _: "FIRST", "ticket", "reply A", "reply B"), "inconsistent")
        fair = lambda p: "FIRST" if p.index("reply B") < p.index("reply A") else "SECOND"
        self.assertEqual(pairwise(fair, "ticket", "reply A", "reply B"), "b")

    def test_hand_written_kappa_matches_statsmodels(self):
        agree, kappa = agreement(LENIENT, HUMAN)
        self.assertEqual((round(agree, 2), round(kappa, 2)), (0.6, 0.2))
        table = [[sum(j and h for j, h in zip(LENIENT, HUMAN)), sum(j and not h for j, h in zip(LENIENT, HUMAN))],
                 [sum(h and not j for j, h in zip(LENIENT, HUMAN)), sum(not j and not h for j, h in zip(LENIENT, HUMAN))]]
        self.assertAlmostEqual(cohens_kappa(table).kappa, kappa)


if __name__ == "__main__":
    unittest.main()
```

The first run took minutes, because statsmodels brings NumPy, SciPy and pandas with it. `uv` caches them, and later runs take about 2 seconds.

## 4. Go

`go test` is the eval framework: a table of cases, `t.Errorf` on a mismatch. `bufio.Scanner` reads the JSON Lines file a line at a time. A live eval in Go would go in a file starting with `//go:build eval`, so plain `go test` skips it and `go test -tags eval` runs it.

```go
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
```

```go
package evals

import (
	"math"
	"reflect"
	"strings"
	"testing"
)

func golden(t *testing.T) []Case {
	t.Helper()
	cases, err := LoadGolden("../shared/golden.jsonl")
	if err != nil {
		t.Fatal(err)
	}
	return cases
}

func round2(x float64) float64 { return math.Round(x*100) / 100 }

func withChange(part, label string) Classify {
	return func(t string) (string, error) {
		if strings.Contains(t, part) {
			return label, nil
		}
		return Keywords(t)
	}
}

func TestParseLabelAndWilson(t *testing.T) {
	if ParseLabel("Category: BUG") != "bug" || ParseLabel("bug or billing") != "" {
		t.Error("ParseLabel")
	}
	if low, high := Wilson(17, 20); round2(low) != 0.64 || round2(high) != 0.95 {
		t.Errorf("Wilson(17, 20) = %v, %v", low, high)
	}
	if low, high := Wilson(170, 200); round2(low) != 0.79 || round2(high) != 0.89 {
		t.Errorf("Wilson(170, 200) = %v, %v", low, high)
	}
}

func TestTheBaselinesGiveTheSameNumbersAsEveryOtherLanguage(t *testing.T) {
	cases := golden(t)
	if r, _ := RunEval(Majority(cases), cases); r.Passed() != 8 {
		t.Errorf("majority passed %d", r.Passed())
	}
	rules, _ := RunEval(Keywords, cases)
	var misses []string
	for _, r := range rules.Results {
		if !r.Pass {
			misses = append(misses, r.ID+":"+r.Got)
		}
	}
	if want := []string{"t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing"}; rules.Passed() != 15 || !reflect.DeepEqual(misses, want) {
		t.Errorf("keywords passed %d, missed %v", rules.Passed(), misses)
	}
	if rules.ByTag["other-language"] != [2]int{0, 2} {
		t.Errorf("by tag: %v", rules.ByTag)
	}
}

func TestCompareAndGate(t *testing.T) {
	cases := golden(t)
	base, _ := RunEval(Keywords, cases)
	better, _ := RunEval(withChange("La aplicación", "bug"), cases)
	if fixed, broke := Compare(base, better); !reflect.DeepEqual(fixed, []string{"t14"}) || broke != nil {
		t.Errorf("compare: %v %v", fixed, broke)
	}
	worse, _ := RunEval(withChange("charged twice", "bug"), cases)
	if reasons := Gate(base, 0.6, nil); reasons != nil {
		t.Errorf("base should pass: %v", reasons)
	}
	want := []string{"pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed"}
	if reasons := Gate(worse, 0.75, &base, "t02", "t18"); !reflect.DeepEqual(reasons, want) {
		t.Errorf("gate: %q", reasons)
	}
}

func TestPairwiseExposesPositionBias(t *testing.T) {
	if got := Pairwise(func(string) string { return "FIRST" }, "ticket", "reply A", "reply B"); got != "inconsistent" {
		t.Errorf("biased judge: %s", got)
	}
	fair := func(p string) string {
		if strings.Index(p, "reply B") < strings.Index(p, "reply A") {
			return "FIRST"
		}
		return "SECOND"
	}
	if got := Pairwise(fair, "ticket", "reply A", "reply B"); got != "b" {
		t.Errorf("fair judge: %s", got)
	}
}

func TestKappaCatchesALenientJudge(t *testing.T) {
	human := []bool{true, true, false, false, true, false, true, false, false, true}
	lenient := []bool{true, true, true, true, true, true, true, true, false, true}
	if agree, kappa := Agreement(lenient, human); round2(agree) != 0.6 || round2(kappa) != 0.2 {
		t.Errorf("got %v, %v", agree, kappa)
	}
}
```

## 5. Java

Records hold the cases and results, and streams do the counting. Jackson reads each line; `check.sh` downloads it once. In a Spring project, Spring AI's evaluators provide LLM-as-judge checks for relevance and factual accuracy, and the gate and baselines here still apply on top.

```java
package evals;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.function.UnaryOperator;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/** An eval harness: the shared golden set, exact-match scoring, error bars, comparison, a gate,
 *  baselines, and the checks on an LLM judge. */
public final class Evals {
    private Evals() {}

    public record Case(String id, String ticket, String label, List<String> tags) {}

    public record CaseResult(String id, String expected, String got, String reply, boolean pass) {}

    public record Result(List<CaseResult> results, Map<String, int[]> byTag) {
        public long passed() { return results.stream().filter(CaseResult::pass).count(); }
        public double rate() { return (double) passed() / results.size(); }
    }

    public static List<Case> loadGolden(Path path) {
        ObjectMapper json = new ObjectMapper();
        try {
            List<Case> cases = new ArrayList<>();
            for (String line : Files.readAllLines(path)) {
                if (!line.isBlank()) cases.add(json.readValue(line, Case.class));
            }
            return cases;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static final Pattern LABEL = Pattern.compile("\\b(bug|billing|feature|other)\\b");

    /** The one label in the reply, or null if there are none or several. */
    public static String parseLabel(String reply) {
        var found = LABEL.matcher(reply.toLowerCase()).results().map(m -> m.group(1)).collect(Collectors.toSet());
        return found.size() == 1 ? found.iterator().next() : null;
    }

    /** Where the true pass rate probably lies (95%), given a small sample. */
    public static double[] wilson(long passed, long total) {
        if (total == 0) return new double[] {0, 1};
        double z = 1.96, n = total, p = passed / n;
        double centre = p + z * z / (2 * n);
        double spread = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
        return new double[] {(centre - spread) / (1 + z * z / n), (centre + spread) / (1 + z * z / n)};
    }

    public static Result runEval(Function<String, String> classify, List<Case> cases) {
        List<CaseResult> results = new ArrayList<>();
        Map<String, int[]> byTag = new LinkedHashMap<>();
        for (Case c : cases) {
            String reply = classify.apply(c.ticket());
            String got = parseLabel(reply);
            boolean pass = c.label().equals(got);
            results.add(new CaseResult(c.id(), c.label(), got, reply, pass));
            for (String tag : c.tags()) {
                int[] counts = byTag.computeIfAbsent(tag, t -> new int[2]);
                if (pass) counts[0]++;
                counts[1]++;
            }
        }
        return new Result(results, byTag);
    }

    /** What a change fixed and what it broke. */
    public static Map<String, List<String>> compare(Result before, Result after) {
        Map<String, Boolean> was = before.results().stream().collect(Collectors.toMap(CaseResult::id, CaseResult::pass));
        return Map.of(
                "fixed", after.results().stream().filter(r -> r.pass() && Boolean.FALSE.equals(was.get(r.id()))).map(CaseResult::id).toList(),
                "broke", after.results().stream().filter(r -> !r.pass() && Boolean.TRUE.equals(was.get(r.id()))).map(CaseResult::id).toList());
    }

    /** The reasons to fail the build; an empty list means the change may merge. */
    public static List<String> gate(Result result, double minRate, Result baseline, String... mustPass) {
        List<String> reasons = new ArrayList<>();
        if (result.rate() < minRate)
            reasons.add("pass rate %.0f%% is below the floor of %.0f%%".formatted(result.rate() * 100, minRate * 100));
        List<String> broke = baseline == null ? List.of() : compare(baseline, result).get("broke");
        if (!broke.isEmpty()) reasons.add("regressed on " + String.join(", ", broke));
        for (String id : mustPass) {
            if (result.results().stream().noneMatch(r -> r.id().equals(id) && r.pass())) reasons.add("must-pass case " + id + " failed");
        }
        return reasons;
    }

    /** Always the most common label. */
    public static Function<String, String> majority(List<Case> cases) {
        String top = cases.stream().collect(Collectors.groupingBy(Case::label, Collectors.counting()))
                .entrySet().stream().max(Map.Entry.comparingByValue()).orElseThrow().getKey();
        return ticket -> top;
    }

    private static final Pattern BILLING = Pattern.compile("charg|refund|invoice|pay|price|subscription|discount|receipt");
    private static final Pattern BUG = Pattern.compile("crash|error|broken|bug|blank|empty|doesn't work|not working");
    private static final Pattern FEATURE = Pattern.compile("add|would be great|should support|could you|please support");

    public static String keywords(String ticket) {
        String t = ticket.toLowerCase();
        if (BILLING.matcher(t).find()) return "billing";
        if (BUG.matcher(t).find()) return "bug";
        if (FEATURE.matcher(t).find()) return "feature";
        return "other";
    }

    private static final Pattern FIRST = Pattern.compile("\\bfirst\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern SECOND = Pattern.compile("\\bsecond\\b", Pattern.CASE_INSENSITIVE);

    /** Asks in both orders, so a judge that prefers whatever comes first is caught, not trusted. */
    public static String pairwise(UnaryOperator<String> ask, String ticket, String a, String b) {
        Function<String, String> pick = answer -> FIRST.matcher(answer).find() ? "first" : SECOND.matcher(answer).find() ? "second" : "";
        String forward = pick.apply(ask.apply(pairPrompt(ticket, a, b)));
        String backward = pick.apply(ask.apply(pairPrompt(ticket, b, a)));
        if (forward.equals("first") && backward.equals("second")) return "a";
        if (forward.equals("second") && backward.equals("first")) return "b";
        return "inconsistent";
    }

    private static String pairPrompt(String ticket, String first, String second) {
        return "Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n" + ticket
                + "\n</ticket>\n<first>\n" + first + "\n</first>\n<second>\n" + second + "\n</second>";
    }

    /** {agreement, Cohen's kappa}. Kappa removes the agreement you'd expect by chance. */
    public static double[] agreement(boolean[] judge, boolean[] human) {
        double n = judge.length, same = 0, judgeYes = 0, humanYes = 0;
        for (int i = 0; i < judge.length; i++) {
            if (judge[i] == human[i]) same++;
            if (judge[i]) judgeYes++;
            if (human[i]) humanYes++;
        }
        double agree = same / n, chance = (judgeYes / n) * (humanYes / n) + (1 - judgeYes / n) * (1 - humanYes / n);
        return new double[] {agree, chance == 1 ? 1 : (agree - chance) / (1 - chance)};
    }

}
```

```java
package evals;

import evals.Evals.*;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

/** Checks, run with `java -ea`. */
public final class EvalsCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    static Function<String, String> withChange(String part, String label) {
        return t -> t.contains(part) ? label : Evals.keywords(t);
    }

    public static void main(String[] args) {
        List<Case> golden = Evals.loadGolden(Path.of("..", "shared", "golden.jsonl"));
        check(golden.size() == 20, golden.size());

        check("bug".equals(Evals.parseLabel("Category: BUG")) && Evals.parseLabel("bug or billing") == null, "parseLabel");
        double[] w = Evals.wilson(17, 20);
        check(round2(w[0]) == 0.64 && round2(w[1]) == 0.95, w[0] + " " + w[1]);

        check(Evals.runEval(Evals.majority(golden), golden).passed() == 8, "majority");
        Result rules = Evals.runEval(Evals::keywords, golden);
        List<String> misses = rules.results().stream().filter(r -> !r.pass()).map(r -> r.id() + ":" + r.got()).toList();
        check(rules.passed() == 15 && misses.equals(List.of("t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing")), misses);
        check(rules.byTag().get("other-language")[0] == 0 && rules.byTag().get("other-language")[1] == 2, "by tag");

        Result better = Evals.runEval(withChange("La aplicación", "bug"), golden);
        check(Evals.compare(rules, better).equals(Map.of("fixed", List.of("t14"), "broke", List.of())), Evals.compare(rules, better));
        Result worse = Evals.runEval(withChange("charged twice", "bug"), golden);
        check(Evals.gate(rules, 0.6, null).isEmpty(), "base passes");
        List<String> reasons = Evals.gate(worse, 0.75, rules, "t02", "t18");
        check(reasons.equals(List.of("pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed")), reasons);

        check(Evals.pairwise(p -> "FIRST", "ticket", "reply A", "reply B").equals("inconsistent"), "biased");
        check(Evals.pairwise(p -> p.indexOf("reply B") < p.indexOf("reply A") ? "FIRST" : "SECOND", "ticket", "reply A", "reply B").equals("b"), "fair");

        boolean[] human = {true, true, false, false, true, false, true, false, false, true};
        boolean[] lenient = {true, true, true, true, true, true, true, true, false, true};
        double[] ak = Evals.agreement(lenient, human);
        check(round2(ak[0]) == 0.6 && round2(ak[1]) == 0.2, ak[0] + " " + ak[1]);

        System.out.println("ok: the same 8/20, 15/20, gate reasons and kappa as every other language");
    }
}
```

## 6. Rust

`serde` reads each line into a `Case`. `BTreeMap` keeps the per-tag results in a stable order, so reports don't reshuffle between runs. `max_by_key` with `Reverse` on the label makes the majority baseline's tie-breaking explicit. A live eval would be a test marked `#[ignore]`, run on purpose with `cargo test -- --ignored`.

```rust
//! An eval harness: the shared golden set, exact-match scoring, error bars, case-by-case comparison,
//! a CI gate, baselines, and the checks on an LLM judge.

use regex::Regex;
use serde::Deserialize;
use std::collections::{BTreeMap, HashMap, HashSet};
use std::sync::LazyLock;

#[derive(Debug, Deserialize)]
pub struct Case {
    pub id: String,
    pub ticket: String,
    pub label: String,
    pub tags: Vec<String>,
}

pub fn load_golden(path: &str) -> Vec<Case> {
    std::fs::read_to_string(path)
        .expect("the golden set is beside the labs")
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| serde_json::from_str(line).expect("each line is a case"))
        .collect()
}

static LABEL: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(bug|billing|feature|other)\b").unwrap());

/// The one label in the reply, or None if there are none or several.
pub fn parse_label(reply: &str) -> Option<String> {
    let lower = reply.to_lowercase();
    let found: HashSet<&str> = LABEL.find_iter(&lower).map(|m| m.as_str()).collect();
    (found.len() == 1).then(|| found.into_iter().next().unwrap().to_string())
}

/// Where the true pass rate probably lies (95%), given a small sample.
pub fn wilson(passed: usize, total: usize) -> (f64, f64) {
    if total == 0 {
        return (0.0, 1.0);
    }
    let (z, n) = (1.96_f64, total as f64);
    let p = passed as f64 / n;
    let centre = p + z * z / (2.0 * n);
    let spread = z * (p * (1.0 - p) / n + z * z / (4.0 * n * n)).sqrt();
    (
        (centre - spread) / (1.0 + z * z / n),
        (centre + spread) / (1.0 + z * z / n),
    )
}

#[derive(Debug)]
pub struct CaseResult {
    pub id: String,
    pub expected: String,
    pub got: Option<String>,
    pub reply: String,
    pub pass: bool,
}

#[derive(Debug, Default)]
pub struct EvalResult {
    pub results: Vec<CaseResult>,
    pub by_tag: BTreeMap<String, (usize, usize)>, // tag -> (passed, total)
}

impl EvalResult {
    pub fn passed(&self) -> usize {
        self.results.iter().filter(|r| r.pass).count()
    }
    pub fn rate(&self) -> f64 {
        self.passed() as f64 / self.results.len() as f64
    }
}

pub fn run_eval(mut classify: impl FnMut(&str) -> String, cases: &[Case]) -> EvalResult {
    let mut result = EvalResult::default();
    for case in cases {
        let reply = classify(&case.ticket);
        let got = parse_label(&reply);
        let pass = got.as_deref() == Some(case.label.as_str());
        for tag in &case.tags {
            let counts = result.by_tag.entry(tag.clone()).or_default();
            counts.0 += usize::from(pass);
            counts.1 += 1;
        }
        result.results.push(CaseResult {
            id: case.id.clone(),
            expected: case.label.clone(),
            got,
            reply,
            pass,
        });
    }
    result
}

/// What a change fixed, and what it broke.
pub fn compare(before: &EvalResult, after: &EvalResult) -> (Vec<String>, Vec<String>) {
    let was: HashMap<&str, bool> = before
        .results
        .iter()
        .map(|r| (r.id.as_str(), r.pass))
        .collect();
    let ids = |want_pass: bool| -> Vec<String> {
        after
            .results
            .iter()
            .filter(|r| r.pass == want_pass && was.get(r.id.as_str()) == Some(&!want_pass))
            .map(|r| r.id.clone())
            .collect()
    };
    (ids(true), ids(false))
}

/// The reasons to fail the build; none means the change may merge.
pub fn gate(
    result: &EvalResult,
    min_rate: f64,
    baseline: Option<&EvalResult>,
    must_pass: &[&str],
) -> Vec<String> {
    let mut reasons = Vec::new();
    if result.rate() < min_rate {
        reasons.push(format!(
            "pass rate {:.0}% is below the floor of {:.0}%",
            result.rate() * 100.0,
            min_rate * 100.0
        ));
    }
    if let Some(base) = baseline {
        let (_, broke) = compare(base, result);
        if !broke.is_empty() {
            reasons.push(format!("regressed on {}", broke.join(", ")));
        }
    }
    for id in must_pass {
        if !result.results.iter().any(|r| r.id == *id && r.pass) {
            reasons.push(format!("must-pass case {id} failed"));
        }
    }
    reasons
}

/// Always the most common label.
pub fn majority(cases: &[Case]) -> impl FnMut(&str) -> String + use<> {
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for case in cases {
        *counts.entry(&case.label).or_default() += 1;
    }
    let top = counts
        .into_iter()
        .max_by_key(|&(label, n)| (n, std::cmp::Reverse(label)))
        .unwrap()
        .0
        .to_string();
    move |_| top.clone()
}

static BILLING: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new("charg|refund|invoice|pay|price|subscription|discount|receipt").unwrap()
});
static BUG: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new("crash|error|broken|bug|blank|empty|doesn't work|not working").unwrap()
});
static FEATURE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new("add|would be great|should support|could you|please support").unwrap()
});

pub fn keywords(ticket: &str) -> String {
    let t = ticket.to_lowercase();
    let label = if BILLING.is_match(&t) {
        "billing"
    } else if BUG.is_match(&t) {
        "bug"
    } else if FEATURE.is_match(&t) {
        "feature"
    } else {
        "other"
    };
    label.to_string()
}

static FIRST: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?i)\bfirst\b").unwrap());
static SECOND: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"(?i)\bsecond\b").unwrap());

/// Asks in both orders, so a judge that prefers whatever comes first is caught, not trusted.
pub fn pairwise(
    mut ask: impl FnMut(&str) -> String,
    ticket: &str,
    a: &str,
    b: &str,
) -> &'static str {
    let prompt = |first: &str, second: &str| {
        format!(
            "Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n{ticket}\n\
             </ticket>\n<first>\n{first}\n</first>\n<second>\n{second}\n</second>"
        )
    };
    let pick = |answer: String| {
        if FIRST.is_match(&answer) {
            "first"
        } else if SECOND.is_match(&answer) {
            "second"
        } else {
            ""
        }
    };
    match (pick(ask(&prompt(a, b))), pick(ask(&prompt(b, a)))) {
        ("first", "second") => "a",
        ("second", "first") => "b",
        _ => "inconsistent",
    }
}

/// (agreement, Cohen's kappa). Kappa removes the agreement you'd expect by chance.
pub fn agreement(judge: &[bool], human: &[bool]) -> (f64, f64) {
    let n = judge.len() as f64;
    let share = |xs: &[bool]| xs.iter().filter(|&&x| x).count() as f64 / n;
    let agree = judge.iter().zip(human).filter(|(j, h)| j == h).count() as f64 / n;
    let (j, h) = (share(judge), share(human));
    let chance = j * h + (1.0 - j) * (1.0 - h);
    (
        agree,
        if chance == 1.0 {
            1.0
        } else {
            (agree - chance) / (1.0 - chance)
        },
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn golden() -> Vec<Case> {
        load_golden("../shared/golden.jsonl")
    }

    fn round2(x: f64) -> f64 {
        (x * 100.0).round() / 100.0
    }

    fn with_change(part: &'static str, label: &'static str) -> impl FnMut(&str) -> String {
        move |t| {
            if t.contains(part) {
                label.to_string()
            } else {
                keywords(t)
            }
        }
    }

    #[test]
    fn labels_and_error_bars() {
        assert_eq!(parse_label("Category: BUG").as_deref(), Some("bug"));
        assert_eq!(parse_label("bug or billing"), None);
        let (low, high) = wilson(17, 20);
        assert_eq!((round2(low), round2(high)), (0.64, 0.95));
    }

    #[test]
    fn the_baselines_give_the_same_numbers_as_every_other_language() {
        let cases = golden();
        assert_eq!(run_eval(majority(&cases), &cases).passed(), 8);
        let rules = run_eval(keywords, &cases);
        let misses: Vec<String> = rules
            .results
            .iter()
            .filter(|r| !r.pass)
            .map(|r| format!("{}:{}", r.id, r.got.as_deref().unwrap_or("")))
            .collect();
        assert_eq!(rules.passed(), 15);
        assert_eq!(
            misses,
            [
                "t10:other",
                "t12:other",
                "t14:other",
                "t15:feature",
                "t20:billing"
            ]
        );
        assert_eq!(rules.by_tag["other-language"], (0, 2));
    }

    #[test]
    fn compare_and_gate() {
        let cases = golden();
        let base = run_eval(keywords, &cases);
        assert_eq!(
            compare(
                &base,
                &run_eval(with_change("La aplicación", "bug"), &cases)
            ),
            (vec!["t14".into()], vec![])
        );
        let worse = run_eval(with_change("charged twice", "bug"), &cases);
        assert!(gate(&base, 0.6, None, &[]).is_empty());
        assert_eq!(
            gate(&worse, 0.75, Some(&base), &["t02", "t18"]),
            [
                "pass rate 70% is below the floor of 75%",
                "regressed on t02",
                "must-pass case t02 failed"
            ]
        );
    }

    #[test]
    fn pairwise_exposes_position_bias() {
        assert_eq!(
            pairwise(|_| "FIRST".into(), "ticket", "reply A", "reply B"),
            "inconsistent"
        );
        let fair = |p: &str| {
            if p.find("reply B") < p.find("reply A") {
                "FIRST"
            } else {
                "SECOND"
            }
            .to_string()
        };
        assert_eq!(pairwise(fair, "ticket", "reply A", "reply B"), "b");
    }

    #[test]
    fn kappa_catches_a_lenient_judge() {
        let human = [
            true, true, false, false, true, false, true, false, false, true,
        ];
        let lenient = [true, true, true, true, true, true, true, true, false, true];
        let (agree, kappa) = agreement(&lenient, &human);
        assert_eq!((round2(agree), round2(kappa)), (0.6, 0.2));
    }
}
```

The pairwise picker here first used `contains("first")`, while the other languages matched whole words, so a reply like "firstly, B is better" would have been read as `FIRST`. No test caught it, because no test reply contained "firstly"; reading the five versions side by side did. It now uses a word-boundary regex like the rest, and that's a reason to compare implementations line by line, not only by their results.

## 7. C#

Records, LINQ and source-generated regexes (`[GeneratedRegex]`) keep the harness short. `CountBy`, added in .NET 9, makes the majority baseline a single line, and tuples make the per-tag counts and the gate checks read naturally. For production work, `Microsoft.Extensions.AI.Evaluation` adds quality evaluators and reports on top of the same ideas. The lab runs in the .NET SDK container with the lesson's `labs/` folder mounted, so it can read `shared/`.

```csharp
// An eval harness: the shared golden set, exact-match scoring, error bars, case-by-case comparison,
// a CI gate, baselines, and the checks on an LLM judge.
using System.Text.Json;
using System.Text.RegularExpressions;

public record Case(string Id, string Ticket, string Label, List<string> Tags);

public record CaseResult(string Id, string Expected, string? Got, string Reply, bool Pass);

public record EvalResult(List<CaseResult> Results, Dictionary<string, (int Passed, int Total)> ByTag)
{
    public int Passed => Results.Count(r => r.Pass);
    public double Rate => (double)Passed / Results.Count;
}

public static partial class Evals
{
    static readonly JsonSerializerOptions Json = new() { PropertyNameCaseInsensitive = true };

    public static List<Case> LoadGolden(string path) =>
        [.. File.ReadLines(path).Where(line => line.Trim() != "").Select(line => JsonSerializer.Deserialize<Case>(line, Json)!)];

    [GeneratedRegex(@"\b(bug|billing|feature|other)\b")]
    private static partial Regex Label();

    /// <summary>The one label in the reply, or null if there are none or several.</summary>
    public static string? ParseLabel(string reply)
    {
        var found = Label().Matches(reply.ToLowerInvariant()).Select(m => m.Value).Distinct().ToList();
        return found.Count == 1 ? found[0] : null;
    }

    /// <summary>Where the true pass rate probably lies (95%), given a small sample.</summary>
    public static (double Low, double High) Wilson(int passed, int total)
    {
        if (total == 0) return (0, 1);
        const double z = 1.96;
        double n = total, p = passed / n;
        var centre = p + z * z / (2 * n);
        var spread = z * Math.Sqrt(p * (1 - p) / n + z * z / (4 * n * n));
        return ((centre - spread) / (1 + z * z / n), (centre + spread) / (1 + z * z / n));
    }

    public static EvalResult RunEval(Func<string, string> classify, List<Case> cases)
    {
        var result = new EvalResult([], []);
        foreach (var c in cases)
        {
            var reply = classify(c.Ticket);
            var got = ParseLabel(reply);
            var pass = got == c.Label;
            result.Results.Add(new(c.Id, c.Label, got, reply, pass));
            foreach (var tag in c.Tags)
            {
                var (passed, total) = result.ByTag.GetValueOrDefault(tag);
                result.ByTag[tag] = (passed + (pass ? 1 : 0), total + 1);
            }
        }
        return result;
    }

    /// <summary>What a change fixed, and what it broke.</summary>
    public static (List<string> Fixed, List<string> Broke) Compare(EvalResult before, EvalResult after)
    {
        var was = before.Results.ToDictionary(r => r.Id, r => r.Pass);
        return ([.. after.Results.Where(r => r.Pass && was.GetValueOrDefault(r.Id, true) == false).Select(r => r.Id)],
                [.. after.Results.Where(r => !r.Pass && was.GetValueOrDefault(r.Id, false)).Select(r => r.Id)]);
    }

    /// <summary>The reasons to fail the build; none means the change may merge.</summary>
    public static List<string> Gate(EvalResult result, double minRate, EvalResult? baseline = null, params string[] mustPass)
    {
        var reasons = new List<string>();
        if (result.Rate < minRate) reasons.Add($"pass rate {result.Rate * 100:0}% is below the floor of {minRate * 100:0}%");
        if (baseline is not null && Compare(baseline, result).Broke is { Count: > 0 } broke)
            reasons.Add($"regressed on {string.Join(", ", broke)}");
        reasons.AddRange(mustPass.Where(id => !result.Results.Any(r => r.Id == id && r.Pass)).Select(id => $"must-pass case {id} failed"));
        return reasons;
    }

    /// <summary>Always the most common label.</summary>
    public static Func<string, string> Majority(List<Case> cases)
    {
        var top = cases.CountBy(c => c.Label).MaxBy(pair => pair.Value).Key;
        return _ => top;
    }

    [GeneratedRegex("charg|refund|invoice|pay|price|subscription|discount|receipt")] private static partial Regex Billing();
    [GeneratedRegex("crash|error|broken|bug|blank|empty|doesn't work|not working")] private static partial Regex Bug();
    [GeneratedRegex("add|would be great|should support|could you|please support")] private static partial Regex Feature();

    public static string Keywords(string ticket)
    {
        var t = ticket.ToLowerInvariant();
        return Billing().IsMatch(t) ? "billing" : Bug().IsMatch(t) ? "bug" : Feature().IsMatch(t) ? "feature" : "other";
    }

    [GeneratedRegex(@"\bfirst\b", RegexOptions.IgnoreCase)] private static partial Regex First();
    [GeneratedRegex(@"\bsecond\b", RegexOptions.IgnoreCase)] private static partial Regex Second();

    /// <summary>Asks in both orders, so a judge that prefers whatever comes first is caught, not trusted.</summary>
    public static string Pairwise(Func<string, string> ask, string ticket, string a, string b)
    {
        string Prompt(string first, string second) =>
            $"Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n{ticket}\n</ticket>\n" +
            $"<first>\n{first}\n</first>\n<second>\n{second}\n</second>";
        static string Pick(string answer) => First().IsMatch(answer) ? "first" : Second().IsMatch(answer) ? "second" : "";
        return (Pick(ask(Prompt(a, b))), Pick(ask(Prompt(b, a)))) switch
        {
            ("first", "second") => "a",
            ("second", "first") => "b",
            _ => "inconsistent",
        };
    }

    /// <summary>(agreement, Cohen's kappa). Kappa removes the agreement you'd expect by chance.</summary>
    public static (double Agreement, double Kappa) Agreement(bool[] judge, bool[] human)
    {
        double n = judge.Length;
        var agree = judge.Zip(human).Count(pair => pair.First == pair.Second) / n;
        double judgeYes = judge.Count(x => x) / n, humanYes = human.Count(x => x) / n;
        var chance = judgeYes * humanYes + (1 - judgeYes) * (1 - humanYes);
        return (agree, chance == 1 ? 1 : (agree - chance) / (1 - chance));
    }
}
```

```csharp
// Checks.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}
static double Round2(double x) => Math.Round(x, 2, MidpointRounding.AwayFromZero);
static Func<string, string> WithChange(string part, string label) => t => t.Contains(part) ? label : Evals.Keywords(t);

var golden = Evals.LoadGolden(Path.Combine(args.Length > 0 ? args[0] : "../shared", "golden.jsonl"));
Check(golden.Count == 20, golden.Count);

Check(Evals.ParseLabel("Category: BUG") == "bug" && Evals.ParseLabel("bug or billing") is null, "ParseLabel");
var (low, high) = Evals.Wilson(17, 20);
Check((Round2(low), Round2(high)) == (0.64, 0.95), (low, high));

Check(Evals.RunEval(Evals.Majority(golden), golden).Passed == 8, "majority");
var rules = Evals.RunEval(Evals.Keywords, golden);
var misses = rules.Results.Where(r => !r.Pass).Select(r => $"{r.Id}:{r.Got}").ToList();
Check(rules.Passed == 15 && misses.SequenceEqual(["t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing"]),
    string.Join(" ", misses));
Check(rules.ByTag["other-language"] == (0, 2), rules.ByTag["other-language"]);

var (fixedIds, brokeIds) = Evals.Compare(rules, Evals.RunEval(WithChange("La aplicación", "bug"), golden));
Check(fixedIds.SequenceEqual(["t14"]) && brokeIds.Count == 0, string.Join(",", fixedIds));
var worse = Evals.RunEval(WithChange("charged twice", "bug"), golden);
Check(Evals.Gate(rules, 0.6).Count == 0, "base passes");
var reasons = Evals.Gate(worse, 0.75, rules, "t02", "t18");
Check(reasons.SequenceEqual(["pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed"]),
    string.Join(" | ", reasons));

Check(Evals.Pairwise(_ => "FIRST", "ticket", "reply A", "reply B") == "inconsistent", "biased");
Check(Evals.Pairwise(p => p.IndexOf("reply B") < p.IndexOf("reply A") ? "FIRST" : "SECOND", "ticket", "reply A", "reply B") == "b", "fair");

bool[] human = [true, true, false, false, true, false, true, false, false, true];
bool[] lenient = [true, true, true, true, true, true, true, true, false, true];
var (agree, kappa) = Evals.Agreement(lenient, human);
Check((Round2(agree), Round2(kappa)) == (0.6, 0.2), (agree, kappa));

Console.WriteLine("ok: the same 8/20, 15/20, gate reasons and kappa as every other language");
```

**Labs:** every version is in [`ai-ml/03-ai-engineer/12-evals/labs/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/12-evals/labs), one folder per language, beside `shared/`. From the vault root, `python3 labs/run.py evals` runs them all and checks this page still shows the same code.

## Common pitfalls

1. **Running the live eval with every unit test.** It's slow and costs money, so people start skipping the whole test suite. Tag it, and run it on purpose.
2. **One golden set per language.** Copies drift apart. Keep one file and have every service read it.
3. **Two implementations that "mostly" agree.** If two versions of a scorer disagree on one case, one of them has a bug. Run both on the same set and compare per case.
4. **Hiding a tie-break.** "The most common label" needs a rule for ties, or two runs can disagree. Say what the rule is in code.
5. **Reports in random order.** Hash maps change order between runs, which makes diffs noisy. Use ordered maps, or sort before printing.
6. **Trusting hand-written statistics untested.** Check them once against a library, as the Python lab does.

## Check your understanding

1. Why does every lab assert exactly 15/20 and the same five misses for the keyword baseline?
2. What is your language's mechanism for keeping a model-calling eval out of the unit tests?
3. Why is JSON Lines a good format for a golden set?
4. The Rust pairwise picker once matched "first" anywhere in the reply. Which reply would that have misread?
5. What does the Python lab gain by comparing its Wilson interval with statsmodels?

<details>
<summary>Answers — after your attempt</summary>

1. The five versions read the same file, apply the same rules and should behave identically. Identical results are the evidence that they do; any difference points straight at a bug.
2. Go: a build tag or `testing.Short()`. Rust: `#[ignore]`. Java: a JUnit tag. C#: an xUnit trait. Python: a pytest marker or a separate script. TypeScript, here: a separate `live.ts`.
3. One case per line: any language reads it with a line loop and a JSON parser, a new case is a one-line diff, and new cases can be appended without rewriting the file.
4. Something like "Firstly, the second reply is better." It contains "first" as part of "firstly", so the picker would read it as `FIRST` even though the judge chose the second reply.
5. Confidence that the hand-written formula is correct, checked against a library many people use and test. After that, either can be used.

</details>

## Practice — independent task

**Put the live eval behind your test framework's tag.**

1. In your language's lab, add a test that classifies the golden set with the local model through Ollama, as the main lesson's `live.ts` does, and fails the gate below 80%.
2. Mark it with your framework's mechanism from §1, so the normal test command skips it.
3. Run the normal command (it should finish in seconds), then run the tagged eval on purpose when the laptop is idle.

**Done when:** the default test run never calls the model, the tagged run prints the model's pass rate with its interval and the gate result, and you can say which tickets the model got right that the keywords got wrong.

## Before moving on

You can name your ecosystem's eval tools, write the harness and gate in your language, and keep the live eval out of the unit tests.

**Recap.** An eval harness is about 150 lines in any language: load JSON Lines, score, compute an interval, compare per case, gate. Frameworks add reporting and plumbing on top. One shared golden set means every language scores the same cases, and identical results are how you know the versions agree. Keep model-calling evals behind your test framework's tag, and run them on purpose.

## Related
- [[ai-ml/03-ai-engineer/12-evals/index|Evals]] — the main lesson
- [[ai-ml/03-ai-engineer/05-prompt-engineering/in-other-languages|Prompt engineering in other languages]] — the first shared fixture, and the prompts being measured
- [[concepts/04-best-practices/04-testing-fundamentals/in-other-languages|Testing fundamentals in other languages]] — each language's test framework in general
