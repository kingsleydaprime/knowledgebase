package tools

import (
	"context"
	"encoding/json"
	"slices"
	"strings"
	"testing"
)

const ordersPath = "../shared/orders.json"

func load(t *testing.T) map[string]*Order {
	orders, err := LoadOrders(ordersPath)
	if err != nil {
		t.Fatal(err)
	}
	return orders
}

func call(name, args, id string) Call { return Call{ID: id, Name: name, Arguments: args} }
func no(string, json.RawMessage) bool { return false }

// scripted plays back a list of turns and records what the model was sent.
func scripted(turns [][]Call, texts []string, seen *[][]Message) Model {
	return func(_ context.Context, history []Message, _ []Tool) (string, []Call, error) {
		*seen = append(*seen, slices.Clone(history))
		i := len(*seen) - 1
		return texts[i], turns[i], nil
	}
}

func TestTheSchemaComesFromTheType(t *testing.T) {
	b, _ := json.Marshal(SchemaFor[RefundArgs]())
	want := `{"type":"object","properties":{"order_id":{"type":"string","description":"Like A123: one capital letter, three digits","pattern":"^[A-Z][0-9]{3}$"},"amount":{"type":"number","minimum":0.01}},"required":["order_id","amount"],"additionalProperties":false}`
	if string(b) != want {
		t.Error(string(b))
	}
}

func TestEveryFailureBecomesAResult(t *testing.T) {
	tools, ctx := SupportTools(load(t)), t.Context()
	if r := Execute(ctx, call("get_order", `{"order_id":"B456"}`, "c1"), tools, no); r.Content != `{"status":"shipped","total":120,"tracking":"LG-88213"}` || r.IsError {
		t.Error(r)
	}
	for args, want := range map[[2]string]string{
		{"delete_order", `{}`}:                               `unknown tool "delete_order"; available: get_order, get_refund, issue_refund`,
		{"get_order", `{order_id: A123`}:                     "arguments are not valid JSON",
		{"get_order", `{"order_id":"Z999"}`}:                 "get_order failed: no order Z999",
		{"issue_refund", `{"order_id":"B456","amount":120}`}: "the user declined this action",
		{"get_order", `{"order_id":"a-1"}`}:                  `validating /properties/order_id: pattern: "a-1" does not match regular expression "^[A-Z][0-9]{3}$"`,
	} {
		if r := Execute(ctx, call(args[0], args[1], "c1"), tools, no); r.Content != want || !r.IsError {
			t.Errorf("%v: got %q", args, r.Content)
		}
	}
}

func TestASideEffectNeedsValidArgumentsThenApprovalThenItsOwnRules(t *testing.T) {
	orders := load(t)
	tools, ctx := SupportTools(orders), t.Context()
	var asked []string
	yes := func(name string, args json.RawMessage) bool {
		asked = append(asked, name+" "+string(args))
		return true
	}
	if r := Execute(ctx, call("issue_refund", `{"order_id":"B456","amount":-5}`, "c1"), tools, yes); !r.IsError || len(asked) != 0 {
		t.Fatal("a malformed call must never reach the person", r)
	}
	if r := Execute(ctx, call("issue_refund", `{"order_id":"B456","amount":120}`, "c1"), tools, yes); r.IsError || orders["B456"].Refund.Status != "processing" {
		t.Fatal(r)
	}
	if !slices.Equal(asked, []string{`issue_refund {"order_id":"B456","amount":120}`}) {
		t.Error(asked)
	}
	if r := Execute(ctx, call("issue_refund", `{"order_id":"B456","amount":120}`, "c1"), tools, yes); r.Content != "issue_refund failed: order B456 already has a refund" {
		t.Error(r.Content)
	}
}

func TestTheRoundTrip(t *testing.T) {
	var seen [][]Message
	model := scripted([][]Call{{call("get_order", `{"order_id":"A123"}`, "c1"), call("get_refund", `{"order_id":"A123"}`, "c2")}, nil},
		[]string{"", "Your refund of 49.99 is being processed."}, &seen)
	answer, history, err := AnswerWithTools(t.Context(), model, []Message{{Role: "user", Content: "Where is my refund for A123?"}}, SupportTools(load(t)), no, 5)
	if err != nil || len(history) != 5 || !strings.Contains(answer, "49.99") {
		t.Fatal(err, len(history), answer)
	}
	if seen[1][2].Content != `{"status":"delivered","total":49.99}` || seen[1][3].Content != `{"status":"processing","amount":49.99,"requested":"2026-09-28"}` {
		t.Error(seen[1][2:])
	}
}

func TestTextInAToolResultCannotApproveAnything(t *testing.T) {
	orders := load(t)
	var seen [][]Message
	model := scripted([][]Call{{call("get_order", `{"order_id":"D012"}`, "c1")}, {call("issue_refund", `{"order_id":"D012","amount":500}`, "c2")}, nil},
		[]string{"", "", "I can't issue that refund."}, &seen)
	AnswerWithTools(t.Context(), model, []Message{{Role: "user", Content: "Check D012"}}, SupportTools(orders), no, 5)
	if !strings.Contains(seen[1][2].Content, "IGNORE ALL PREVIOUS INSTRUCTIONS") || seen[2][4].Content != "ERROR: the user declined this action" || orders["D012"].Refund != nil {
		t.Fatal(seen)
	}
	approved := Execute(t.Context(), call("issue_refund", `{"order_id":"D012","amount":500}`, "c3"), SupportTools(orders), func(string, json.RawMessage) bool { return true })
	if approved.Content != "issue_refund failed: refund 500 is more than the order total 30" {
		t.Error(approved.Content)
	}
}

func TestAModelThatNeverStopsIsCutOff(t *testing.T) {
	forever := func(context.Context, []Message, []Tool) (string, []Call, error) {
		return "", []Call{call("get_order", `{"order_id":"A123"}`, "c1")}, nil
	}
	_, _, err := AnswerWithTools(t.Context(), forever, []Message{{Role: "user", Content: "?"}}, SupportTools(load(t)), no, 3)
	if err == nil || err.Error() != "no answer after 3 rounds of tool calls" {
		t.Error(err)
	}
}
