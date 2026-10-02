// Package models: a provider-neutral model client — the port, a fake, an OpenAI-compatible
// adapter and an SSE reader. Standard library only; openai-go or Ollama's api package are the usual adapters.
package models

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"iter"
	"net/http"
	"slices"
	"strings"
)

type Message struct {
	Role    string `json:"role"` // "system", "user" or "assistant"
	Content string `json:"content"`
}

type Options struct {
	Temperature *float64 // nil means "use the server's default"
	MaxTokens   *int
}

type ChatResult struct {
	Text         string
	FinishReason string // "stop", "length" (max tokens cut it off) or "other"
	InputTokens  int
	OutputTokens int
}

// ChatModel is the port: all the rest of the app knows about a model.
type ChatModel interface {
	Chat(ctx context.Context, messages []Message, opts Options) (ChatResult, error)
	Stream(ctx context.Context, messages []Message, opts Options) iter.Seq2[string, error]
}

// Conversation resends every earlier turn, because the model is stateless.
type Conversation struct {
	Model    ChatModel
	Messages []Message
}

func NewConversation(model ChatModel, system string) *Conversation {
	return &Conversation{Model: model, Messages: []Message{{"system", system}}}
}

func (c *Conversation) Say(ctx context.Context, content string) (string, error) {
	c.Messages = append(c.Messages, Message{"user", content})
	result, err := c.Model.Chat(ctx, c.Messages, Options{})
	if err != nil {
		return "", err
	}
	c.Messages = append(c.Messages, Message{"assistant", result.Text})
	return result.Text, nil
}

// FakeModel replies from a script and records what it was sent.
type FakeModel struct {
	Replies []string
	Calls   [][]Message
}

func (f *FakeModel) Chat(_ context.Context, messages []Message, _ Options) (ChatResult, error) {
	f.Calls = append(f.Calls, slices.Clone(messages))
	reply := f.Replies[0]
	f.Replies = f.Replies[1:]
	return ChatResult{Text: reply, FinishReason: "stop"}, nil
}

func (f *FakeModel) Stream(ctx context.Context, messages []Message, opts Options) iter.Seq2[string, error] {
	return func(yield func(string, error) bool) {
		result, err := f.Chat(ctx, messages, opts)
		if err != nil {
			yield("", err)
			return
		}
		for word := range strings.SplitAfterSeq(result.Text, " ") {
			if !yield(word, nil) {
				return
			}
		}
	}
}

// SSEData reads server-sent events. bufio.Scanner keeps a partial line until the rest arrives,
// and Go strings are bytes, so a character split between reads is joined back up for free.
func SSEData(r io.Reader) iter.Seq2[string, error] {
	return func(yield func(string, error) bool) {
		scanner := bufio.NewScanner(r)
		var data []string
		for scanner.Scan() {
			line := strings.TrimSuffix(scanner.Text(), "\r")
			if rest, ok := strings.CutPrefix(line, "data:"); ok {
				data = append(data, strings.TrimLeft(rest, " "))
				continue
			}
			if line != "" || len(data) == 0 {
				continue
			}
			event := strings.Join(data, "\n") // a blank line ends the event
			data = nil
			if event == "[DONE]" {
				return
			}
			if !yield(event, nil) {
				return
			}
		}
		if err := scanner.Err(); err != nil {
			yield("", err)
		}
	}
}

// ModelError carries the status and whether a retry could help.
type ModelError struct {
	Status int
	Body   string
}

func (e *ModelError) Error() string {
	return fmt.Sprintf("model request failed: %d %.200s", e.Status, e.Body)
}

func (e *ModelError) Retryable() bool { return e.Status == 429 || e.Status >= 500 }

// OpenAICompatible talks to any server speaking the OpenAI chat completions format.
type OpenAICompatible struct {
	BaseURL   string
	Model     string
	APIKey    string
	ExtraBody map[string]any // provider-specific fields, e.g. {"reasoning_effort": "none"}
	Client    *http.Client   // set a Timeout on it: every call needs one
}

func (m *OpenAICompatible) Chat(ctx context.Context, messages []Message, opts Options) (ChatResult, error) {
	res, err := m.post(ctx, messages, opts, false)
	if err != nil {
		return ChatResult{}, err
	}
	defer res.Body.Close()
	var data struct {
		Choices []struct {
			Message      struct{ Content string }
			FinishReason string `json:"finish_reason"`
		}
		Usage struct {
			PromptTokens     int `json:"prompt_tokens"`
			CompletionTokens int `json:"completion_tokens"`
		}
	}
	if err := json.NewDecoder(res.Body).Decode(&data); err != nil {
		return ChatResult{}, err
	}
	choice := data.Choices[0]
	reason := choice.FinishReason
	if reason != "stop" && reason != "length" {
		reason = "other"
	}
	return ChatResult{choice.Message.Content, reason, data.Usage.PromptTokens, data.Usage.CompletionTokens}, nil
}

func (m *OpenAICompatible) Stream(ctx context.Context, messages []Message, opts Options) iter.Seq2[string, error] {
	return func(yield func(string, error) bool) {
		res, err := m.post(ctx, messages, opts, true)
		if err != nil {
			yield("", err)
			return
		}
		defer res.Body.Close()
		for data, err := range SSEData(res.Body) {
			if err != nil {
				yield("", err)
				return
			}
			var chunk struct {
				Choices []struct{ Delta struct{ Content string } }
			}
			if err := json.Unmarshal([]byte(data), &chunk); err != nil {
				yield("", err)
				return
			}
			if len(chunk.Choices) > 0 && chunk.Choices[0].Delta.Content != "" && !yield(chunk.Choices[0].Delta.Content, nil) {
				return
			}
		}
	}
}

// ListModels asks the server instead of trusting a model name remembered from somewhere.
func (m *OpenAICompatible) ListModels(ctx context.Context) ([]string, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, m.BaseURL+"/models", nil)
	if err != nil {
		return nil, err
	}
	res, err := m.do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	var data struct{ Data []struct{ ID string } }
	if err := json.NewDecoder(res.Body).Decode(&data); err != nil {
		return nil, err
	}
	ids := []string{}
	for _, model := range data.Data {
		ids = append(ids, model.ID)
	}
	slices.Sort(ids)
	return ids, nil
}

func (m *OpenAICompatible) post(ctx context.Context, messages []Message, opts Options, stream bool) (*http.Response, error) {
	body := map[string]any{"model": m.Model, "messages": messages, "stream": stream}
	for k, v := range m.ExtraBody {
		body[k] = v
	}
	if opts.Temperature != nil {
		body["temperature"] = *opts.Temperature
	}
	if opts.MaxTokens != nil {
		body["max_tokens"] = *opts.MaxTokens
	}
	encoded, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, m.BaseURL+"/chat/completions", bytes.NewReader(encoded))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	return m.do(req)
}

func (m *OpenAICompatible) do(req *http.Request) (*http.Response, error) {
	if m.APIKey != "" {
		req.Header.Set("Authorization", "Bearer "+m.APIKey)
	}
	client := m.Client
	if client == nil {
		client = http.DefaultClient
	}
	res, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	if res.StatusCode >= 300 {
		defer res.Body.Close()
		body, _ := io.ReadAll(res.Body)
		return nil, &ModelError{res.StatusCode, string(body)}
	}
	return res, nil
}
