package agents

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"slices"
	"strings"
	"sync"
	"testing"
	"testing/synctest"
	"time"

	"github.com/google/jsonschema-go/jsonschema"

	"tools"
)

func load(t *testing.T) []tools.Tool {
	orders, err := tools.LoadOrders("../../../07-tools-and-mcp/labs/shared/orders.json")
	if err != nil {
		t.Fatal(err)
	}
	return tools.SupportTools(orders)
}

func call(name, args, id string) tools.Call { return tools.Call{ID: id, Name: name, Arguments: args} }
func no(string, json.RawMessage) bool       { return false }

type turn struct {
	text   string
	calls  []tools.Call
	tokens int
}

func scripted(turns ...turn) Model {
	return func(context.Context, []tools.Message) (string, []tools.Call, int, error) {
		t := turns[0]
		turns = turns[1:]
		return t.text, t.calls, t.tokens, nil
	}
}

var ask = []tools.Message{{Role: "user", Content: "Where is my refund for A123?"}}

func names(o Outcome) [][]string {
	var out [][]string
	for _, s := range o.Trace {
		step := []string{}
		for _, c := range s.Calls {
			step = append(step, c.Name)
		}
		out = append(out, step)
	}
	return out
}

func TestATwoStepAnswerWithATrace(t *testing.T) {
	model := scripted(turn{"", []tools.Call{call("get_order", `{"order_id":"A123"}`, "c1"), call("get_refund", `{"order_id":"A123"}`, "c2")}, 0},
		turn{"Your refund of 49.99 is being processed.", nil, 0})
	o, _ := RunAgent(t.Context(), model, ask, load(t), DefaultLimits, no)
	if o.Status != "answered" || fmt.Sprint(names(o)) != "[[get_order get_refund] []]" {
		t.Fatal(o.Status, names(o))
	}
	if f := ScoreTrajectory(o, Expect{Status: "answered", MustCall: []string{"get_refund"}, MustNot: []string{"issue_refund"}, MaxSteps: 3}); len(f) > 0 {
		t.Error(f)
	}
}

func TestReadsRunTogetherAndASideEffectWaits(t *testing.T) {
	synctest.Test(t, func(t *testing.T) { // a fake clock: the 30 ms and 10 ms waits finish in a fixed order, instantly
		var mu sync.Mutex
		var log []string
		slow := func(name string, sideEffects bool, d time.Duration) tools.Tool {
			return tools.Tool{Name: name, Schema: &jsonschema.Schema{Type: "object"}, SideEffects: sideEffects,
				Run: func(context.Context, json.RawMessage) (any, error) {
					mu.Lock()
					log = append(log, "start "+name)
					mu.Unlock()
					time.Sleep(d)
					mu.Lock()
					log = append(log, "end "+name)
					mu.Unlock()
					return name, nil
				}}
		}
		ts := []tools.Tool{slow("read_a", false, 30*time.Millisecond), slow("read_b", false, 10*time.Millisecond), slow("write_c", true, time.Millisecond)}
		model := scripted(turn{"", []tools.Call{call("write_c", `{}`, "1"), call("read_a", `{}`, "2"), call("read_b", `{}`, "3")}, 0}, turn{"done", nil, 0})
		o, _ := RunAgent(t.Context(), model, nil, ts, DefaultLimits, func(string, json.RawMessage) bool { return true })
		ends := slices.DeleteFunc(slices.Clone(log), func(s string) bool { return strings.HasPrefix(s, "start") })
		if !slices.Equal(ends, []string{"end read_b", "end read_a", "end write_c"}) || log[len(log)-2] != "start write_c" {
			t.Error(log) // the two reads start together (in either order), the write starts after both end
		}
		var ids []string
		for _, m := range o.Messages {
			if m.Role == "tool" {
				ids = append(ids, m.ToolCallID)
			}
		}
		if !slices.Equal(ids, []string{"1", "2", "3"}) {
			t.Error(ids)
		}
	})
}

func TestAStepLimitStopsAWanderingAgent(t *testing.T) {
	n := 100
	wandering := func(context.Context, []tools.Message) (string, []tools.Call, int, error) {
		n++
		return "", []tools.Call{call("get_order", fmt.Sprintf(`{"order_id":"A%d"}`, n), fmt.Sprint(n))}, 0, nil
	}
	o, _ := RunAgent(t.Context(), wandering, ask, load(t), Limits{MaxSteps: 3, MaxTokens: 1e9, MaxRepeats: 5}, no)
	if o.Status != "step_limit" || len(o.Trace) != 3 || !slices.Equal(ScoreTrajectory(o, Expect{Status: "answered"}), []string{"ended step_limit, expected answered"}) {
		t.Error(o.Status, len(o.Trace))
	}
}

func TestTheSameCallAgainAndAgainIsStuck(t *testing.T) {
	repeating := func(context.Context, []tools.Message) (string, []tools.Call, int, error) {
		return "", []tools.Call{call("get_refund", `{"order_id":"Z999"}`, "x")}, 0, nil
	}
	o, _ := RunAgent(t.Context(), repeating, ask, load(t), Limits{MaxSteps: 20, MaxTokens: 1e9, MaxRepeats: 2}, no)
	if o.Status != "stuck" || len(o.Trace) != 3 {
		t.Error(o.Status, len(o.Trace))
	}
}

func TestATokenBudget(t *testing.T) {
	model := scripted(turn{"", []tools.Call{call("get_order", `{"order_id":"A123"}`, "c1")}, 25_500},
		turn{"", []tools.Call{call("get_order", `{"order_id":"B456"}`, "c2")}, 25_500}, turn{"never reached", nil, 25_500})
	o, _ := RunAgent(t.Context(), model, ask, load(t), Limits{MaxSteps: 10, MaxTokens: 50_000, MaxRepeats: 2}, no)
	if o.Status != "token_limit" || len(o.Trace) != 2 || o.Trace[1].Tokens != 25_500 {
		t.Error(o.Status, o.Trace)
	}
}

func TestTheScorerNamesEachBrokenExpectation(t *testing.T) {
	model := scripted(turn{"", []tools.Call{call("issue_refund", `{"order_id":"B456","amount":120}`, "c1")}, 0}, turn{"I've asked for a refund.", nil, 0})
	o, _ := RunAgent(t.Context(), model, ask, load(t), DefaultLimits, no)
	got := ScoreTrajectory(o, Expect{MustCall: []string{"get_refund"}, MustNot: []string{"issue_refund"}, AnswerMatches: regexp.MustCompile(`(?i)no refund`)})
	if !slices.Equal(got, []string{"never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund"}) {
		t.Error(got)
	}
}

func TestTheWorkflow(t *testing.T) {
	ts, ctx := load(t), t.Context()
	var prompts []string
	write := func(p string) (string, error) {
		prompts = append(prompts, p)
		return "Your refund of 49.99 for A123 is being processed.", nil
	}
	r, _ := RefundStatus(ctx, "Where is my refund for order a123?", ts, write)
	if r.Kind != "answer" || r.ModelCalls != 1 || !strings.Contains(prompts[0], `Refund: {"status":"processing","amount":49.99,"requested":"2026-09-28"}`) {
		t.Fatal(r, prompts)
	}
	if r, _ := RefundStatus(ctx, "Has my refund come through?", ts, write); r.Kind != "ask" {
		t.Error(r)
	}
	// "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
	if r, _ := RefundStatus(ctx, "Can you change my delivery address?", ts, write); r.Kind != "handoff" || r.Reason != "classified as feature" {
		t.Error(r)
	}
	RefundStatus(ctx, "Where is my refund for D012?", ts, write)
	if strings.Contains(prompts[len(prompts)-1], "IGNORE") || len(prompts) != 2 {
		t.Error(prompts)
	}
}
