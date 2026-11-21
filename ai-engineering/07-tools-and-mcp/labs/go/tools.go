// Package tools: tools for a support assistant, with the same checks, round trip and results as the
// TypeScript lab. Each tool's schema is inferred from a Go struct, with the jsonschema-go package the
// official MCP Go SDK uses, and the same package validates the arguments.
package tools

import (
	"cmp"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/google/jsonschema-go/jsonschema"
)

// IDArgs and RefundArgs are the argument types: their fields are the schema.
type IDArgs struct {
	OrderID string `json:"order_id" jsonschema:"Like A123: one capital letter, three digits"`
}
type RefundArgs struct {
	OrderID string  `json:"order_id" jsonschema:"Like A123: one capital letter, three digits"`
	Amount  float64 `json:"amount"`
}

// SchemaFor infers a schema from T, then adds the rules a Go type can't express.
func SchemaFor[T any]() *jsonschema.Schema {
	s, err := jsonschema.For[T](nil) // fields without omitempty are required; no other properties allowed
	if err != nil {
		panic(err)
	}
	s.Properties["order_id"].Pattern = "^[A-Z][0-9]{3}$"
	if amount, ok := s.Properties["amount"]; ok {
		amount.Minimum = new(0.01)
	}
	return s
}

type Tool struct {
	Name        string
	Description string
	Schema      *jsonschema.Schema
	SideEffects bool
	Run         func(ctx context.Context, args json.RawMessage) (any, error)
}

type Call struct{ ID, Name, Arguments string }
type Result struct {
	ID      string
	Content string
	IsError bool
}

// Approve is asked before any tool with side effects runs.
type Approve func(name string, args json.RawMessage) bool

func Execute(ctx context.Context, call Call, tools []Tool, approve Approve) Result {
	fail := func(format string, a ...any) Result { return Result{call.ID, fmt.Sprintf(format, a...), true} }
	var tool *Tool
	var names []string
	for i := range tools {
		names = append(names, tools[i].Name)
		if tools[i].Name == call.Name {
			tool = &tools[i]
		}
	}
	if tool == nil {
		return fail("unknown tool %q; available: %s", call.Name, strings.Join(names, ", "))
	}
	raw := json.RawMessage(cmp.Or(call.Arguments, "{}"))
	var value any
	if json.Unmarshal(raw, &value) != nil {
		return fail("arguments are not valid JSON")
	}
	resolved, err := tool.Schema.Resolve(nil)
	if err != nil {
		return fail("%s has an invalid schema: %v", tool.Name, err)
	}
	if err := resolved.Validate(value); err != nil {
		return fail("%s", strings.TrimPrefix(err.Error(), "validating root: ")) // the library's words, first problem only
	}
	if tool.SideEffects && !approve(tool.Name, raw) {
		return fail("the user declined this action")
	}
	out, err := tool.Run(ctx, raw)
	if err != nil {
		return fail("%s failed: %v", tool.Name, err)
	}
	content, _ := json.Marshal(out)
	if len(content) > 2000 {
		return Result{call.ID, string(content[:2000]) + " …[truncated]", false}
	}
	return Result{call.ID, string(content), false}
}

type Refund struct {
	Status    string  `json:"status"`
	Amount    float64 `json:"amount,omitempty"`
	Requested string  `json:"requested,omitempty"`
	Paid      string  `json:"paid,omitempty"`
}

type Order struct {
	Status   string  `json:"status"`
	Total    float64 `json:"total"`
	Tracking string  `json:"tracking,omitempty"`
	Refund   *Refund `json:"refund"`
	Note     string  `json:"note,omitempty"`
}

func LoadOrders(path string) (map[string]*Order, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var orders map[string]*Order
	return orders, json.Unmarshal(data, &orders)
}

func SupportTools(orders map[string]*Order) []Tool {
	find := func(id string) (*Order, error) {
		if o, ok := orders[id]; ok {
			return o, nil
		}
		return nil, fmt.Errorf("no order %s", id)
	}
	byID := func(f func(*Order) any) func(context.Context, json.RawMessage) (any, error) {
		return func(_ context.Context, raw json.RawMessage) (any, error) {
			var a IDArgs
			if err := json.Unmarshal(raw, &a); err != nil {
				return nil, err
			}
			o, err := find(a.OrderID)
			if err != nil {
				return nil, err
			}
			return f(o), nil
		}
	}
	return []Tool{
		{"get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
			SchemaFor[IDArgs](), false, byID(func(o *Order) any {
				return struct { // everything but the refund, which has its own tool
					Status   string  `json:"status"`
					Total    float64 `json:"total"`
					Tracking string  `json:"tracking,omitempty"`
					Note     string  `json:"note,omitempty"`
				}{o.Status, o.Total, o.Tracking, o.Note}
			})},
		{"get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
			SchemaFor[IDArgs](), false, byID(func(o *Order) any {
				if o.Refund == nil {
					return Refund{Status: "none"}
				}
				return o.Refund
			})},
		{"issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
			SchemaFor[RefundArgs](), true, func(_ context.Context, raw json.RawMessage) (any, error) {
				var a RefundArgs
				if err := json.Unmarshal(raw, &a); err != nil {
					return nil, err
				}
				o, err := find(a.OrderID)
				switch {
				case err != nil:
					return nil, err
				case o.Refund != nil:
					return nil, fmt.Errorf("order %s already has a refund", a.OrderID)
				case a.Amount > o.Total:
					return nil, fmt.Errorf("refund %g is more than the order total %g", a.Amount, o.Total)
				}
				o.Refund = &Refund{Status: "processing", Amount: a.Amount, Requested: "today"}
				return o.Refund, nil
			}},
	}
}

type Message struct {
	Role, Content, ToolCallID string
	Calls                     []Call
}

// Model returns one turn: text, and zero or more calls. No calls means "this is my answer".
type Model func(ctx context.Context, history []Message, tools []Tool) (string, []Call, error)

func AnswerWithTools(ctx context.Context, model Model, history []Message, tools []Tool, approve Approve, maxRounds int) (string, []Message, error) {
	for round := 1; round <= maxRounds; round++ {
		text, calls, err := model(ctx, history, tools)
		if err != nil {
			return "", history, err
		}
		history = append(history, Message{Role: "assistant", Content: text, Calls: calls})
		if len(calls) == 0 {
			return text, history, nil
		}
		for _, c := range calls { // one result per call, in the order of the calls
			r := Execute(ctx, c, tools, approve)
			content := r.Content
			if r.IsError {
				content = "ERROR: " + content
			}
			history = append(history, Message{Role: "tool", ToolCallID: c.ID, Content: content})
		}
	}
	return "", history, fmt.Errorf("no answer after %d rounds of tool calls", maxRounds)
}
