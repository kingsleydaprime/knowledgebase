package decoding

import (
	"math"
	"slices"
	"strings"
	"testing"
)

var scores = []Entry{{"Paris", 4.0}, {"a", 2.0}, {"the", 1.5}, {"Lyon", 0.5}}

func rounded(dist []Entry) []float64 {
	out := []float64{}
	for _, e := range dist {
		out = append(out, math.Round(e.P*1000)/1000)
	}
	return out
}

func tokens(dist []Entry) []string {
	out := []string{}
	for _, e := range dist {
		out = append(out, e.Token)
	}
	return out
}

func TestTemperatureReshapesTheSameScores(t *testing.T) {
	for _, c := range []struct {
		temperature float64
		want        []float64
	}{
		{1, []float64{0.802, 0.108, 0.066, 0.024}},
		{0.5, []float64{0.975, 0.018, 0.007, 0.001}},
		{2, []float64{0.547, 0.201, 0.157, 0.095}},
	} {
		if got := rounded(Softmax(scores, c.temperature)); !slices.Equal(got, c.want) {
			t.Errorf("T=%v: got %v, want %v", c.temperature, got, c.want)
		}
	}
}

func TestTopKAndTopP(t *testing.T) {
	dist := Softmax(scores, 1)
	for _, c := range []struct {
		got, want []string
	}{
		{tokens(TopK(dist, 2)), []string{"Paris", "a"}},
		{tokens(TopP(dist, 0.9)), []string{"Paris", "a"}},
		{tokens(TopP(dist, 0.97)), []string{"Paris", "a", "the"}},
	} {
		if !slices.Equal(c.got, c.want) {
			t.Errorf("got %v, want %v", c.got, c.want)
		}
	}
}

func TestSameSeedSameNumbersAsEveryOtherLanguage(t *testing.T) {
	r := SeededRandom(42)
	got := []float64{r(), r(), r()}
	if want := []float64{0.6011037519201636, 0.44829055899754167, 0.8524657934904099}; !slices.Equal(got, want) {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestSameSeedSameTokens(t *testing.T) {
	dist, r := Softmax(scores, 1), SeededRandom(42)
	picks := []string{}
	for range 10 {
		picks = append(picks, Sample(dist, r))
	}
	if got, want := strings.Join(picks, " "), "Paris Paris a Paris Paris Paris Paris Paris a Paris"; got != want {
		t.Errorf("got %q, want %q", got, want)
	}
	r, paris := SeededRandom(42), 0
	for range 1000 {
		if Sample(dist, r) == "Paris" {
			paris++
		}
	}
	if paris != 796 { // about 80.2%, as expected
		t.Errorf("Paris picked %d times, want 796", paris)
	}
}

func TestGreedy(t *testing.T) {
	if got := Greedy(Softmax(scores, 2)); got != "Paris" {
		t.Errorf("got %s", got)
	}
}
