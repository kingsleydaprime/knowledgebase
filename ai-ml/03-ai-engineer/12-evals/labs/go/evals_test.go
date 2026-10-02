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
