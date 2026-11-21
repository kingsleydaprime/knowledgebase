// Package prompts: prompts as files, shared with every other language's lab. The files use {{name}}
// slots; Go's text/template wants {{.name}}, so a ten-line renderer fills them instead.
package prompts

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const shared = "../shared"

var slot = regexp.MustCompile(`\{\{(\w+)\}\}`)

// Render fills {{name}} slots in a shared prompt file. A missing value is an error, not "".
func Render(name string, values map[string]string) (string, error) {
	template, err := os.ReadFile(filepath.Join(shared, "prompts", name+".md"))
	if err != nil {
		return "", err
	}
	var missing []string
	out := slot.ReplaceAllStringFunc(string(template), func(s string) string {
		key := slot.FindStringSubmatch(s)[1]
		value, ok := values[key]
		if !ok {
			missing = append(missing, key)
		}
		return value
	})
	if len(missing) > 0 {
		return "", fmt.Errorf("prompt %s needs a value for {{%s}}", name, strings.Join(missing, "}}, {{"))
	}
	return out, nil
}

var reviewTag = regexp.MustCompile(`(?i)</?review>`)

// FenceUserText stops user text from closing the <review> tag early.
// It lowers the risk of prompt injection; it doesn't remove it.
func FenceUserText(text string) string {
	return reviewTag.ReplaceAllStringFunc(text, func(tag string) string { return "&lt;" + tag[1:] })
}

type Example struct {
	Review string `json:"review"`
	Label  string `json:"label"`
}

// FormatExamples writes few-shot examples in exactly the format of the real question.
func FormatExamples(examples []Example) string {
	parts := make([]string, len(examples))
	for i, e := range examples {
		parts[i] = fmt.Sprintf("<review>\n%s\n</review>\n%s", FenceUserText(e.Review), e.Label)
	}
	return strings.Join(parts, "\n\n")
}

var label = regexp.MustCompile(`\b(positive|negative|mixed)\b`)

// ParseLabel accepts "Mixed." or "Sentiment: positive"; it rejects replies naming two labels.
func ParseLabel(reply string) (string, bool) {
	found := map[string]bool{}
	for _, m := range label.FindAllString(strings.ToLower(reply), -1) {
		found[m] = true
	}
	for l := range found {
		return l, len(found) == 1
	}
	return "", false
}

func LoadReviews() (examples, cases []Example, err error) {
	raw, err := os.ReadFile(filepath.Join(shared, "reviews.json"))
	if err != nil {
		return nil, nil, err
	}
	var data struct{ Examples, Cases []Example }
	err = json.Unmarshal(raw, &data)
	return data.Examples, data.Cases, err
}

type Failure struct{ Review, Expected, Got, Reply string }

type Result struct {
	Correct, Total int
	Failures       []Failure
}

// Evaluate scores a prompt against labelled cases, so "this wording feels better" becomes a number.
func Evaluate(ask func(prompt string) (string, error), prompt string, cases, examples []Example) (Result, error) {
	result := Result{Total: len(cases)}
	for _, c := range cases {
		values := map[string]string{"review": FenceUserText(c.Review)}
		if prompt == "classify-few-shot" {
			values["examples"] = FormatExamples(examples)
		}
		text, err := Render(prompt, values)
		if err != nil {
			return result, err
		}
		reply, err := ask(text)
		if err != nil {
			return result, err
		}
		if got, ok := ParseLabel(reply); ok && got == c.Label {
			result.Correct++
		} else {
			result.Failures = append(result.Failures, Failure{c.Review, c.Label, got, reply})
		}
	}
	return result, nil
}
