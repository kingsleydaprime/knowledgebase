package models

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"testing"
	"testing/iotest"
)

type recorded struct {
	Path, Authorization string
	Body                map[string]any
}

// fakeServer is a real HTTP server on a free port (httptest): it records requests and
// answers with the canned responses in order.
func fakeServer(t *testing.T, responses ...func(http.ResponseWriter)) (*OpenAICompatible, *[]recorded) {
	var requests []recorded
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		rec := recorded{Path: r.URL.Path, Authorization: r.Header.Get("Authorization")}
		if r.Method == http.MethodPost {
			json.NewDecoder(r.Body).Decode(&rec.Body)
		}
		requests = append(requests, rec)
		responses[0](w)
		responses = responses[1:]
	}))
	t.Cleanup(server.Close)
	return &OpenAICompatible{BaseURL: server.URL + "/v1", Model: "some-model", APIKey: "sk-test", Client: server.Client()}, &requests
}

func reply(status int, body string) func(http.ResponseWriter) {
	return func(w http.ResponseWriter) {
		w.WriteHeader(status)
		io.WriteString(w, body)
	}
}

func ptr[T any](v T) *T { return &v }

func TestChatSendsTheMessagesFormatAndReadsTextFinishReasonAndUsage(t *testing.T) {
	model, requests := fakeServer(t, reply(200, `{"choices":[{"message":{"content":"Paris"},"finish_reason":"stop"}],"usage":{"prompt_tokens":21,"completion_tokens":2}}`))
	result, err := model.Chat(context.Background(), []Message{{"user", "Capital of France?"}}, Options{Temperature: ptr(0.0), MaxTokens: ptr(5)})
	if err != nil {
		t.Fatal(err)
	}
	if want := (ChatResult{"Paris", "stop", 21, 2}); result != want {
		t.Errorf("got %+v, want %+v", result, want)
	}
	req := (*requests)[0]
	wantBody := map[string]any{"model": "some-model", "messages": []any{map[string]any{"role": "user", "content": "Capital of France?"}},
		"stream": false, "temperature": 0.0, "max_tokens": 5.0}
	if req.Path != "/v1/chat/completions" || req.Authorization != "Bearer sk-test" || !reflect.DeepEqual(req.Body, wantBody) {
		t.Errorf("got %+v", req)
	}
}

func TestAReplyCutOffByMaxTokensSaysSo(t *testing.T) {
	model, _ := fakeServer(t, reply(200, `{"choices":[{"message":{"content":"The capital of"},"finish_reason":"length"}]}`))
	if result, _ := model.Chat(context.Background(), nil, Options{}); result.FinishReason != "length" {
		t.Errorf("got %q", result.FinishReason)
	}
}

func TestErrorsCarryTheStatusAndWhetherARetryCouldHelp(t *testing.T) {
	model, _ := fakeServer(t, reply(429, "slow down"), reply(400, "bad model name"))
	for _, want := range []struct {
		status    int
		retryable bool
	}{{429, true}, {400, false}} {
		_, err := model.Chat(context.Background(), nil, Options{})
		var modelErr *ModelError
		if !errors.As(err, &modelErr) || modelErr.Status != want.status || modelErr.Retryable() != want.retryable {
			t.Errorf("got %v, want status %d retryable %v", err, want.status, want.retryable)
		}
	}
}

func TestTheSSEReaderSurvivesEventsSplitAcrossReadsEvenMidCharacter(t *testing.T) {
	raw := "data: {\"a\":1}\n\ndata: {\"b\":\"café\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n"
	var events []string
	for data, err := range SSEData(iotest.OneByteReader(strings.NewReader(raw))) { // one byte per read: every split possible
		if err != nil {
			t.Fatal(err)
		}
		events = append(events, data)
	}
	if want := []string{`{"a":1}`, `{"b":"café"}`}; !reflect.DeepEqual(events, want) {
		t.Errorf("got %q, want %q", events, want)
	}
}

func TestStreamYieldsTheTextDeltasInOrder(t *testing.T) {
	delta := func(text string) string {
		return fmt.Sprintf("data: {\"choices\":[{\"delta\":{\"content\":%q}}]}\n\n", text)
	}
	model, requests := fakeServer(t, reply(200, delta("Hel")+delta("lo")+delta(", world")+"data: [DONE]\n\n"))
	var parts []string
	for part, err := range model.Stream(context.Background(), []Message{{"user", "hi"}}, Options{}) {
		if err != nil {
			t.Fatal(err)
		}
		parts = append(parts, part)
	}
	if want := []string{"Hel", "lo", ", world"}; !reflect.DeepEqual(parts, want) || (*requests)[0].Body["stream"] != true {
		t.Errorf("got %q", parts)
	}
}

func TestListModelsAsksTheServerInsteadOfTrustingMemory(t *testing.T) {
	model, requests := fakeServer(t, reply(200, `{"data":[{"id":"qwen3.5:4b"},{"id":"gemma4:latest"}]}`))
	ids, err := model.ListModels(context.Background())
	if want := []string{"gemma4:latest", "qwen3.5:4b"}; err != nil || !reflect.DeepEqual(ids, want) || (*requests)[0].Path != "/v1/models" {
		t.Errorf("got %v, %v", ids, err)
	}
}

func TestTheModelIsStatelessSoAConversationResendsEveryTurn(t *testing.T) {
	model := &FakeModel{Replies: []string{"Hi Kingsley.", "Your name is Kingsley."}}
	chat := NewConversation(model, "Be brief.")
	ctx := context.Background()
	chat.Say(ctx, "My name is Kingsley.")
	if got, _ := chat.Say(ctx, "What's my name?"); got != "Your name is Kingsley." {
		t.Errorf("got %q", got)
	}
	var roles []string
	for _, m := range model.Calls[1] {
		roles = append(roles, m.Role)
	}
	if len(model.Calls[0]) != 2 || !reflect.DeepEqual(roles, []string{"system", "user", "assistant", "user"}) {
		t.Errorf("calls: %+v", model.Calls)
	}
}
