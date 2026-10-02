package invoice

import (
	"encoding/json"
	"strings"
	"testing"
)

const good = `{"vendor":"Brightline Studio Ltd","invoice_number":"INV-2041","currency":"GBP","due_date":"2026-10-15",
"line_items":[{"description":"Logo design","amount_cents":45000},{"description":"Two revisions","amount_cents":12000},
{"description":"Brand guide PDF","amount_cents":8550}],"total_cents":65550}`

func TestOneStructGivesTheSchemaForTheModel(t *testing.T) {
	var schema map[string]any
	b, _ := json.Marshal(Schema())
	json.Unmarshal(b, &schema)
	props := schema["properties"].(map[string]any)
	if schema["additionalProperties"] != false || len(schema["required"].([]any)) != 6 ||
		len(props["currency"].(map[string]any)["enum"].([]any)) != 4 {
		t.Errorf("schema: %s", b)
	}
}

func TestAndTheTypedValueForYourCode(t *testing.T) {
	inv, err := Parse("Sure! Here it is:\n```json\n" + good + "\n```")
	if err != nil {
		t.Fatal(err)
	}
	if inv.DueDate.Format("2 January 2006") != "15 October 2026" || inv.LineItems[2].AmountCents != 8550 {
		t.Errorf("got %+v", inv)
	}
}

// with returns the good invoice with one field changed (or added).
func with(field string, value any) string {
	var inv map[string]any
	json.Unmarshal([]byte(good), &inv)
	inv[field] = value
	b, _ := json.Marshal(inv)
	return string(b)
}

func TestEachKindOfProblemIsReportedInTheModelsTerms(t *testing.T) {
	for _, c := range []struct{ reply, want string }{
		{with("currency", "pounds"), "currency must be one of GBP USD EUR NGN"},
		{with("invoice_number", ""), "invoice_number is missing"}, // a missing key decodes to "" silently; the validator notices
		{with("due_date", "15 October 2026"), "must be a date like 2026-10-15"},
		{with("total_cents", 655.5), "cannot unmarshal number 655.5"},
		{with("notes", "thanks"), `unknown field "notes"`},
		{with("total_cents", 65500), "line items add up to 65550 cents but total_cents is 65500"},
	} {
		if _, err := Parse(c.reply); err == nil || !strings.Contains(err.Error(), c.want) {
			t.Errorf("got %v, want %q", err, c.want)
		}
	}
}

func scripted(replies ...Reply) (func([]Message) Reply, *[][]Message) {
	var seen [][]Message
	return func(m []Message) Reply {
		seen = append(seen, append([]Message(nil), m...))
		return replies[len(seen)-1]
	}, &seen
}

func TestAWrongTotalIsRetriedWithTheErrorFedBack(t *testing.T) {
	model, seen := scripted(Reply{Text: with("total_cents", 65500)}, Reply{Text: good})
	out := Extract(model, "…", 3)
	last := (*seen)[1][len((*seen)[1])-1].Content
	if out.Reason != "ok" || out.Attempts != 2 || !strings.Contains(last, "total_cents is 65500") {
		t.Errorf("got %+v; feedback %q", out, last)
	}
}

func TestTruncationIsRetriedRefusalStopsAndRetriesAreCapped(t *testing.T) {
	model, seen := scripted(Reply{Text: `{"vendor": "Bright`, FinishReason: "length"}, Reply{Text: good})
	if out := Extract(model, "…", 3); out.Reason != "ok" || !strings.Contains((*seen)[1][3].Content, "cut off") {
		t.Errorf("truncation: %+v", out)
	}
	model, seen = scripted(Reply{Refusal: "I can't help with that."})
	if out := Extract(model, "…", 3); out.Reason != "refused" || len(*seen) != 1 {
		t.Errorf("refusal: %+v", out)
	}
	model, _ = scripted(Reply{Text: "nope"}, Reply{Text: "still no"}, Reply{Text: `{"vendor": 1}`})
	if out := Extract(model, "…", 3); out.Reason != "invalid" || out.Attempts != 3 || !strings.Contains(out.Detail, "cannot unmarshal number") {
		t.Errorf("cap: %+v", out)
	}
}
