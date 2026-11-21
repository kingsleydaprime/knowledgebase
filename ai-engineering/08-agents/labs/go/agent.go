// Package agents: the agent loop with its controls, the same question as a workflow, and a trajectory
// scorer. Imports the tools lab (the store, the tools and Execute) and the evals lab (the keyword router).
package agents

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"slices"
	"strings"
	"sync"

	"evals"
	"tools"
)

type Limits struct{ MaxSteps, MaxTokens, MaxRepeats int }

var DefaultLimits = Limits{MaxSteps: 8, MaxTokens: 50_000, MaxRepeats: 2}

type StepCall struct {
	Name, Arguments string
	IsError         bool
}
type Step struct {
	Step, Tokens int
	Calls        []StepCall
}
type Outcome struct {
	Status   string // answered, step_limit, token_limit or stuck
	Answer   string
	Trace    []Step
	Messages []tools.Message
}

// Model returns one turn: text, the calls it asks for, and the tokens it used.
type Model func(ctx context.Context, history []tools.Message) (text string, calls []tools.Call, tokens int, err error)

func RunAgent(ctx context.Context, model Model, history []tools.Message, ts []tools.Tool, limits Limits, approve tools.Approve) (Outcome, error) {
	var trace []Step
	seen := map[string]int{}
	total := 0
	end := func(status, answer string) (Outcome, error) { return Outcome{status, answer, trace, history}, nil }
	sideEffects := map[string]bool{}
	for _, t := range ts {
		sideEffects[t.Name] = t.SideEffects
	}
	for step := 1; step <= limits.MaxSteps; step++ {
		text, calls, used, err := model(ctx, history)
		if err != nil {
			return Outcome{}, err
		}
		total += used
		history = append(history, tools.Message{Role: "assistant", Content: text, Calls: calls})
		trace = append(trace, Step{Step: step, Tokens: used})
		if len(calls) == 0 {
			return end("answered", text)
		}
		for _, c := range calls { // the same call, again and again, is going round in circles
			key := c.Name + " " + c.Arguments
			if seen[key]++; seen[key] > limits.MaxRepeats {
				return end("stuck", "")
			}
		}

		// Read-only calls run in their own goroutines; side effects run alone, in order, after them.
		results := make([]tools.Result, len(calls))
		var wg sync.WaitGroup
		for i, c := range calls {
			if !sideEffects[c.Name] {
				wg.Go(func() { results[i] = tools.Execute(ctx, c, ts, approve) }) // each writes only its own slot
			}
		}
		wg.Wait()
		for i, c := range calls {
			if sideEffects[c.Name] {
				results[i] = tools.Execute(ctx, c, ts, approve)
			}
		}

		for i, c := range calls { // results in the order of the calls, whatever order they finished in
			content := results[i].Content
			if results[i].IsError {
				content = "ERROR: " + content
			}
			history = append(history, tools.Message{Role: "tool", ToolCallID: c.ID, Content: content})
			trace[len(trace)-1].Calls = append(trace[len(trace)-1].Calls, StepCall{c.Name, c.Arguments, results[i].IsError})
		}
		if total > limits.MaxTokens {
			return end("token_limit", "")
		}
	}
	return end("step_limit", "")
}

type WorkflowResult struct {
	Kind, Text, Reason string // Kind: answer, ask or handoff
	ModelCalls         int
}

var orderID = regexp.MustCompile(`\b([A-Za-z])(\d{3})\b`)

// RefundStatus answers the same question with fixed steps: route, extract, look up, then one model
// call with no tools.
func RefundStatus(ctx context.Context, question string, ts []tools.Tool, write func(prompt string) (string, error)) (WorkflowResult, error) {
	if label, _ := evals.Keywords(question); label != "billing" {
		return WorkflowResult{Kind: "handoff", Reason: "classified as " + label}, nil
	}
	m := orderID.FindStringSubmatch(question)
	if m == nil {
		return WorkflowResult{Kind: "ask", Text: "Could you tell me your order number? It looks like A123."}, nil
	}
	id := strings.ToUpper(m[1]) + m[2]
	args, _ := json.Marshal(map[string]string{"order_id": id})
	refund := tools.Execute(ctx, tools.Call{ID: "w1", Name: "get_refund", Arguments: string(args)}, ts, func(string, json.RawMessage) bool { return false })
	if refund.IsError {
		return WorkflowResult{Kind: "ask", Text: fmt.Sprintf("I couldn't find order %s. Could you check the number?", id)}, nil
	}
	text, err := write(fmt.Sprintf("Write a one-sentence reply to a customer about their refund, using only these facts.\n"+
		"Order: %s\nRefund: %s\nTheir question: %s", id, refund.Content, question))
	return WorkflowResult{Kind: "answer", Text: text, ModelCalls: 1}, err
}

type Expect struct {
	Status            string
	MustCall, MustNot []string
	MaxSteps          int
	AnswerMatches     *regexp.Regexp
}

func ScoreTrajectory(o Outcome, e Expect) []string {
	var called, failures []string
	for _, s := range o.Trace {
		for _, c := range s.Calls {
			called = append(called, c.Name)
		}
	}
	if e.Status != "" && o.Status != e.Status {
		failures = append(failures, fmt.Sprintf("ended %s, expected %s", o.Status, e.Status))
	}
	for _, n := range e.MustCall {
		if !slices.Contains(called, n) {
			failures = append(failures, "never called "+n)
		}
	}
	for _, n := range e.MustNot {
		if slices.Contains(called, n) {
			failures = append(failures, "called "+n)
		}
	}
	if e.MaxSteps > 0 && len(o.Trace) > e.MaxSteps {
		failures = append(failures, fmt.Sprintf("took %d steps, expected at most %d", len(o.Trace), e.MaxSteps))
	}
	if e.AnswerMatches != nil && !e.AnswerMatches.MatchString(o.Answer) {
		failures = append(failures, "answer doesn't match "+e.AnswerMatches.String())
	}
	return failures
}
