package rag

import (
	"fmt"
	"math"
	"slices"
	"strings"
	"testing"
)

func items(t *testing.T) []Item {
	docs, err := LoadJSON[[]Doc]("../shared/help.json")
	if err != nil {
		t.Fatal(err)
	}
	var out []Item
	for _, d := range docs {
		for _, c := range ChunkDoc(d, 60) {
			out = append(out, Item{c.ID, WithContext(c, d.Title)})
		}
	}
	return out
}

func rounded(ranked []Scored) string {
	var parts []string
	for _, r := range ranked {
		parts = append(parts, fmt.Sprintf("%s:%.4f", r.ID, r.Score))
	}
	return strings.Join(parts, " ")
}

func TestChunks(t *testing.T) {
	its := items(t)
	var ids []string
	for _, it := range its {
		ids = append(ids, it.ID)
	}
	want := []string{"refunds#1", "refunds#2", "refunds#3", "password#1", "password#2", "export#1", "export#2", "appearance#1", "shipping#1", "shipping#2"}
	if !slices.Equal(ids, want) || its[1].Text != "Refunds > How long a refund takes\nMost refunds arrive within 5 to 10 working days. Your bank may take a few more days to show it." {
		t.Fatal(ids, its[1].Text)
	}
	long := ChunkDoc(Doc{"long", "Long", "## Part\none two three four\n\nfive six seven eight\n\nnine ten eleven twelve"}, 8)
	if long[0].Text != "one two three four\n\nfive six seven eight" || long[1].Text != "five six seven eight\n\nnine ten eleven twelve" {
		t.Error(long)
	}
}

func TestCosineAndTheHandMadeEmbedding(t *testing.T) {
	if Cosine([]float64{1, 0}, []float64{5, 0}) != 1 || Cosine([]float64{1, 0}, []float64{0, 1}) != 0 ||
		math.Round(Cosine([]float64{1, 0}, []float64{1, 1})*1000)/1000 != 0.707 || Cosine([]float64{0, 0}, []float64{1, 1}) != 0 {
		t.Error("cosine")
	}
	if !slices.Equal(ToyEmbed("My login doesn't work any more."), []float64{1, 0, 0, 0, 0, 0}) || !slices.Equal(ToyEmbed("What does E1042 mean?"), make([]float64, 6)) {
		t.Error("toy embed")
	}
}

func TestTheSameRankingsAndScoresAsTypeScript(t *testing.T) {
	its := items(t)
	k := BM25("My login doesn't work any more.", its)
	v := VectorSearch("My login doesn't work any more.", its, ToyEmbed)
	if rounded(k) != "refunds#2:1.8951 refunds#1:1.6952" || rounded(v) != "password#1:0.9864 password#2:0.9701" {
		t.Fatal(rounded(k), rounded(v))
	}
	var fused []string
	for _, r := range RRF(k, v) {
		fused = append(fused, r.ID)
	}
	if !slices.Equal(fused, []string{"refunds#2", "password#1", "refunds#1", "password#2"}) {
		t.Error(fused)
	}
	if got := rounded(BM25("What does E1042 mean?", its)); got != "export#2:2.8115" {
		t.Error(got)
	}
	if got := rounded(BM25("Can I make the app darker?", its)[:3]); got != "refunds#1:1.8249 appearance#1:1.2348 password#2:1.1894" {
		t.Error(got)
	}
}

func TestRetrievalMetrics(t *testing.T) {
	its := items(t)
	questions, _ := LoadJSON[[]Question]("../shared/questions.json")
	results := map[string]map[string][]string{"keyword": {}, "vector": {}, "hybrid": {}}
	for _, q := range questions {
		k, v := BM25(q.Question, its), VectorSearch(q.Question, its, ToyEmbed)
		results["keyword"][q.ID], results["vector"][q.ID], results["hybrid"][q.ID] = DocsOf(k), DocsOf(v), DocsOf(RRF(k, v))
	}
	for name, want := range map[string]string{"keyword": "0.6 0.8 0.700", "vector": "0.8 0.8 0.800", "hybrid": "0.8 1 0.900"} {
		r := results[name]
		if got := fmt.Sprintf("%g %g %.3f", RecallAtK(r, questions, 1), RecallAtK(r, questions, 3), MRR(r, questions)); got != want {
			t.Errorf("%s: %s", name, got)
		}
	}
}

func TestPromptAndCitations(t *testing.T) {
	prompt := GroundedPrompt("How long?", []Source{{"refunds#2", "Most refunds arrive within 5 to 10 working days."}})
	if !strings.Contains(prompt, "[S1] (refunds#2)\nMost refunds arrive within 5 to 10 working days.") {
		t.Error(prompt)
	}
	for answer, want := range map[string]string{
		"Within 5 to 10 working days [S1].": "[]",
		"I don't know.":                     "[]",
		"Refunds are instant.":              "[no citations]",
		"A week [S3].":                      "[cites S3, which wasn't given]",
	} {
		if got := fmt.Sprint(CheckCitations(answer, 2)); got != want {
			t.Errorf("%q: %s", answer, got)
		}
	}
}
