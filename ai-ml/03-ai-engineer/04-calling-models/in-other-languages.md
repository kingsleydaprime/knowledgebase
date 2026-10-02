# Calling Models in Other Languages

> **[Beginner]** · A companion to [[ai-ml/03-ai-engineer/04-calling-models/index|calling models]], which builds a provider-neutral client in TypeScript: a `ChatModel` port, a fake, an OpenAI-compatible adapter, an SSE reader and a conversation that resends history. This page builds the same client in Python, Go, Java, Rust and C#, each tested against a fake server that's normal for that language. C and C++ build the parts that don't need an HTTP library: the streaming parser and, in C++, the port. It also names each ecosystem's SDKs.

## Before you start

You can already:

- Build the main lesson's client, and explain statelessness, finish reasons, retryable errors and why SSE needs a buffer → [[ai-ml/03-ai-engineer/04-calling-models/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Name your language's official SDK and its standard "chat model" abstraction, if it has one.
2. Write a model client in your language behind a port, with a fake for tests.
3. Test HTTP code the way your ecosystem does it: a real local server, `httptest`, or a fake handler.
4. Explain how your language's I/O library deals with chunks that split lines and characters.

## The kid version

Every country has a post office, and they all deliver letters, but each one has its own forms, its own stamps and its own rules for parcels. If you write your letters on your own standard paper and let a helper fill in each post office's forms, you can switch post offices without rewriting a single letter. This page builds that helper in seven languages. Each one also builds a pretend post office for practising, so you can check your letters arrive correctly without posting anything for real.

**Where the analogy stops working.** Letters arrive whole. Model replies arrive in pieces, cut wherever the network felt like cutting, sometimes through the middle of a letter of the alphabet. Each language has its own way of gluing the pieces back together, and some do it for you.

## 1. The tools, by ecosystem

| Language | Official SDK | A ready-made port (switch providers in one line) | Fake HTTP in tests |
|---|---|---|---|
| TypeScript | `openai`, `@anthropic-ai/sdk` | **Vercel AI SDK** (`ai`) | replace `fetch` |
| Python | `openai`, `anthropic` | LiteLLM, LangChain chat models | a real `http.server` on a free port, or `respx` / `responses` |
| Go | `openai-go`, `anthropic-sdk-go` | LangChainGo; Ollama's own `api` package | **`net/http/httptest`** — standard library |
| Java | `openai-java`, `anthropic-java` | **Spring AI `ChatClient`**, LangChain4j `ChatModel` | the JDK's `com.sun.net.httpserver`, WireMock |
| Rust | `async-openai` (community) | `rig`, `genai` | a `TcpListener`, `wiremock`, `mockito` |
| C# | `OpenAI`, `Anthropic` | **`Microsoft.Extensions.AI` `IChatClient`** | a fake **`HttpMessageHandler`** |
| C, C++ | none | none | — (libcurl for HTTP; llama.cpp's server for local models) |

Two of these deserve a closer look. **.NET's `IChatClient`** is exactly the port from the main lesson, standardised by Microsoft, with adapters for OpenAI, Ollama and Azure. **Spring AI's `ChatClient`** does the same for Java. In those ecosystems you'd usually depend on the standard port rather than write your own. The labs here write their own anyway, so you can see what those libraries do for you.

## 2. Who glues the chunks back together

The trickiest part of the main lesson was the SSE reader: the network splits the stream anywhere, even inside a two-byte character like `é`. How much of that your language handles for you:

| Language | Half a line between reads | Half a character between reads |
|---|---|---|
| TypeScript | your code keeps the tail | `TextDecoder` with `{ stream: true }` |
| Python | your code keeps the tail | `codecs.getincrementaldecoder("utf-8")` |
| Go | **`bufio.Scanner`** | not a problem: strings are bytes until you ask otherwise |
| Java | **`BufferedReader`** | **`InputStreamReader`** |
| Rust | **`BufReader::lines()`** | `lines()` checks UTF-8 only once a whole line has arrived |
| C# | **`StreamReader.ReadLineAsync`** | **`StreamReader`** |
| C, C++ | your code keeps the tail | not a problem: bytes are joined before anything reads them as text |

Every lab tests this the hard way: Go with the standard `iotest.OneByteReader`, Java, Rust and C# with a stream that returns one byte per read, Python with a chunk that ends halfway through `é`, and C and C++ by feeding the stream in every chunk size from 1 byte up.

## Terms used in this lesson

1. **SDK (software development kit)**: The letters stand for those three words. Here it means a provider's official library for calling its API.
2. **Iterator**: This is an object that hands out values one at a time, on request. Streaming replies are naturally iterators of text pieces.
3. **`iter.Seq2`**: This is Go's standard iterator type (since Go 1.23). It is a function that calls `yield` for each value, and here each value comes with an error.
4. **`IAsyncEnumerable`**: This is C#'s iterator for values that arrive over time. You consume one with `await foreach`.
5. **Try-with-resources**: This is Java's `try (…)` block, which closes the resource when the block ends, even after an error or an early exit.
6. **`HttpMessageHandler`**: This is the last stage in .NET's `HttpClient` pipeline, the one that actually sends the request. Replacing it gives a fake server with no network.
7. **`httptest`**: This is Go's standard-library package for HTTP tests. `httptest.NewServer` starts a real server on a free local port.
8. **Incremental parser**: This is a parser you feed in pieces, which keeps whatever is unfinished until the next piece arrives.
9. **libcurl**: This is the C library behind the `curl` command. Most C and C++ programs that make HTTP requests use it.

## 3. Python

Standard library only, so you can see every step: `urllib.request` for HTTP, `json`, and an incremental UTF-8 decoder for the stream. The fake server is a real `ThreadingHTTPServer` on port 0, so the operating system picks a free port. In a real project, the `openai` package would sit behind the same `ChatModel` protocol.

```python
"""A provider-neutral model client: the port, a fake, an OpenAI-compatible adapter and an SSE reader.
Standard library only; in a real project the `openai` package is the usual adapter."""
import codecs
import json
import urllib.error
import urllib.request
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Literal, Protocol

Message = dict[str, str]  # {"role": "system" | "user" | "assistant", "content": "..."}


@dataclass(frozen=True)
class ChatResult:
    text: str
    finish_reason: Literal["stop", "length", "other"]  # "length" means max tokens cut it off
    input_tokens: int = 0
    output_tokens: int = 0


class ChatModel(Protocol):
    """The port: all the rest of the app knows about a model."""

    def chat(self, messages: list[Message], *, temperature: float | None = None, max_tokens: int | None = None) -> ChatResult: ...
    def stream(self, messages: list[Message], *, temperature: float | None = None, max_tokens: int | None = None) -> Iterator[str]: ...


class Conversation:
    """The model is stateless: "memory" is the app resending every earlier turn on every call."""

    def __init__(self, model: ChatModel, system: str):
        self.model = model
        self.messages: list[Message] = [{"role": "system", "content": system}]

    def say(self, content: str) -> str:
        self.messages.append({"role": "user", "content": content})
        text = self.model.chat(self.messages).text
        self.messages.append({"role": "assistant", "content": text})
        return text


@dataclass
class FakeModel:
    """For tests: replies from a script and records what it was sent."""
    replies: list[str]
    calls: list[list[Message]] = field(default_factory=list)

    def chat(self, messages, **_) -> ChatResult:
        self.calls.append([dict(m) for m in messages])
        return ChatResult(self.replies.pop(0), "stop")

    def stream(self, messages, **_) -> Iterator[str]:
        yield from self.chat(messages).text.split(" ")


def sse_data(chunks: Iterable[bytes]) -> Iterator[str]:
    """Read server-sent events. Chunks can split anywhere, even inside a character, so keep the tail."""
    decoder = codecs.getincrementaldecoder("utf-8")()  # holds a half-received character until the rest arrives
    buffer = ""
    for chunk in chunks:
        buffer += decoder.decode(chunk).replace("\r\n", "\n")
        *events, buffer = buffer.split("\n\n")  # the last piece may be incomplete
        for event in events:
            data = "\n".join(line[5:].lstrip() for line in event.split("\n") if line.startswith("data:"))
            if data == "[DONE]":
                return
            if data:
                yield data


class ModelError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"model request failed: {status} {body[:200]}")
        self.status = status
        self.retryable = status == 429 or status >= 500  # rate limits and server errors; never a 400


class OpenAICompatibleModel:
    """Any server speaking the OpenAI chat completions format: OpenAI, Ollama, vLLM, LM Studio, gateways."""

    def __init__(self, base_url: str, model: str, api_key: str | None = None, extra_body: dict | None = None, timeout: float = 120):
        self.base_url, self.model, self.api_key = base_url, model, api_key
        self.extra_body, self.timeout = extra_body or {}, timeout

    def chat(self, messages, *, temperature=None, max_tokens=None) -> ChatResult:
        with self._post(messages, temperature, max_tokens, stream=False) as res:
            data = json.load(res)
        choice, usage = data["choices"][0], data.get("usage", {})
        reason = choice["finish_reason"] if choice["finish_reason"] in ("stop", "length") else "other"
        return ChatResult(choice["message"].get("content") or "", reason,
                          usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))

    def stream(self, messages, *, temperature=None, max_tokens=None) -> Iterator[str]:
        with self._post(messages, temperature, max_tokens, stream=True) as res:
            for data in sse_data(iter(lambda: res.read1(4096), b"")):
                delta = json.loads(data)["choices"][0].get("delta", {}).get("content")
                if delta:
                    yield delta

    def list_models(self) -> list[str]:
        """Never hard-code model names from memory: ask the server."""
        with self._open(urllib.request.Request(self.base_url + "/models", headers=self._headers())) as res:
            return sorted(m["id"] for m in json.load(res)["data"])

    def _post(self, messages, temperature, max_tokens, stream: bool):
        body = {"model": self.model, "messages": messages, "stream": stream, **self.extra_body}
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        headers = {**self._headers(), "content-type": "application/json"}
        return self._open(urllib.request.Request(self.base_url + "/chat/completions", json.dumps(body).encode(), headers))

    def _open(self, request):
        try:
            return urllib.request.urlopen(request, timeout=self.timeout)  # every call needs a timeout
        except urllib.error.HTTPError as e:
            raise ModelError(e.code, e.read().decode(errors="replace")) from None

    def _headers(self) -> dict[str, str]:
        return {"authorization": f"Bearer {self.api_key}"} if self.api_key else {}
```

```python
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from models import Conversation, FakeModel, ModelError, OpenAICompatibleModel, sse_data


class FakeServer:
    """A real HTTP server on a free port: records requests, answers with canned (status, body) pairs.
    Headers are kept as the server parsed them, so lookups ignore case, as HTTP does."""

    def __init__(self, *responses: tuple[int, bytes]):
        self.responses, self.requests = list(responses), []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["content-length"]))
                fake.requests.append({"path": self.path, "headers": self.headers, "body": json.loads(body)})
                self._reply()

            def do_GET(self):
                fake.requests.append({"path": self.path, "headers": self.headers, "body": None})
                self._reply()

            def _reply(self):
                status, body = fake.responses.pop(0)
                self.send_response(status)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, args=(0.01,), daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/v1"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def ok(obj) -> tuple[int, bytes]:
    return 200, json.dumps(obj).encode()


class ModelTests(unittest.TestCase):
    def serve(self, *responses):
        server = FakeServer(*responses)
        self.addCleanup(server.close)
        return server, OpenAICompatibleModel(server.url, "some-model", api_key="sk-test")

    def test_chat_sends_the_messages_format_and_reads_text_finish_reason_and_usage(self):
        server, model = self.serve(ok({"choices": [{"message": {"content": "Paris"}, "finish_reason": "stop"}],
                                       "usage": {"prompt_tokens": 21, "completion_tokens": 2}}))
        result = model.chat([{"role": "user", "content": "Capital of France?"}], temperature=0, max_tokens=5)

        self.assertEqual((result.text, result.finish_reason, result.input_tokens, result.output_tokens), ("Paris", "stop", 21, 2))
        req = server.requests[0]
        self.assertEqual(req["path"], "/v1/chat/completions")
        self.assertEqual(req["headers"]["authorization"], "Bearer sk-test")
        self.assertEqual(req["body"], {"model": "some-model", "messages": [{"role": "user", "content": "Capital of France?"}],
                                       "stream": False, "temperature": 0, "max_tokens": 5})

    def test_a_reply_cut_off_by_max_tokens_says_so(self):
        _, model = self.serve(ok({"choices": [{"message": {"content": "The capital of"}, "finish_reason": "length"}]}))
        self.assertEqual(model.chat([]).finish_reason, "length")

    def test_errors_carry_the_status_and_whether_a_retry_could_help(self):
        _, model = self.serve((429, b"slow down"), (400, b"bad model name"))
        with self.assertRaises(ModelError) as rate_limited:
            model.chat([])
        self.assertEqual((rate_limited.exception.status, rate_limited.exception.retryable), (429, True))
        with self.assertRaises(ModelError) as bad_request:
            model.chat([])
        self.assertEqual((bad_request.exception.status, bad_request.exception.retryable), (400, False))

    def test_the_sse_reader_survives_events_split_across_chunks_even_mid_character(self):
        chunks = [b'data: {"a":1}\n\nda', b'ta: {"b":"caf\xc3', b'\xa9"}\n\ndata: [DONE]\n\ndata: {"ignored":true}\n\n']
        self.assertEqual(list(sse_data(chunks)), ['{"a":1}', '{"b":"café"}'])  # "é" is 0xC3 0xA9, split in two

    def test_stream_yields_the_text_deltas_in_order(self):
        delta = lambda text: f"data: {json.dumps({'choices': [{'delta': {'content': text}}]})}\n\n"
        server, model = self.serve((200, (delta("Hel") + delta("lo") + delta(", world") + "data: [DONE]\n\n").encode()))
        self.assertEqual(list(model.stream([{"role": "user", "content": "hi"}])), ["Hel", "lo", ", world"])
        self.assertIs(server.requests[0]["body"]["stream"], True)

    def test_list_models_asks_the_server_instead_of_trusting_memory(self):
        server, model = self.serve(ok({"data": [{"id": "qwen3.5:4b"}, {"id": "gemma4:latest"}]}))
        self.assertEqual(model.list_models(), ["gemma4:latest", "qwen3.5:4b"])
        self.assertEqual(server.requests[0]["path"], "/v1/models")

    def test_the_model_is_stateless_so_a_conversation_resends_every_turn(self):
        model = FakeModel(["Hi Kingsley.", "Your name is Kingsley."])
        chat = Conversation(model, "Be brief.")
        chat.say("My name is Kingsley.")
        self.assertEqual(chat.say("What's my name?"), "Your name is Kingsley.")
        self.assertEqual(len(model.calls[0]), 2)
        self.assertEqual([m["role"] for m in model.calls[1]], ["system", "user", "assistant", "user"])


if __name__ == "__main__":
    unittest.main()
```

The first run failed in an instructive way: the test looked up the `authorization` header in a plain dictionary, but `urllib` sends `Authorization`. HTTP header names are case-insensitive, so the test now keeps the server's own header object, which ignores case the way HTTP does.

## 4. Go

The standard library covers everything here. `context.Context` carries cancellation and timeouts through every call. `Stream` returns an `iter.Seq2[string, error]`, so callers write `for part, err := range model.Stream(…)`, and the HTTP body is closed when the loop ends, even if the caller breaks out early. `httptest.NewServer` is the standard fake.

```go
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
```

```go
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
```

## 5. Java

`java.net.http.HttpClient` sends the requests, and the JDK's own `HttpServer` plays the fake server. Java has no JSON in its standard library, so the lab uses Jackson, the most common choice; `check.sh` downloads its three jars once from Maven Central. Streaming returns a `Stream<String>` whose `onClose` closes the HTTP body. Callers use try-with-resources, so the connection is released even if they stop reading early.

```java
package models;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UncheckedIOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

/** A provider-neutral model client: the port, a fake, an OpenAI-compatible adapter and an SSE reader. */
public final class Models {
    private Models() {}

    public record Message(String role, String content) {}

    /** Null fields mean "use the server's default". */
    public record Options(Double temperature, Integer maxTokens) {
        public static final Options DEFAULT = new Options(null, null);
    }

    /** finishReason is "stop", "length" (max tokens cut it off) or "other". */
    public record ChatResult(String text, String finishReason, int inputTokens, int outputTokens) {}

    /** The port: all the rest of the app knows about a model. */
    public interface ChatModel {
        ChatResult chat(List<Message> messages, Options options);
        /** Close the stream (try-with-resources) to release the connection, even if you stop early. */
        Stream<String> stream(List<Message> messages, Options options);
    }

    /** The model is stateless: "memory" is the app resending every earlier turn on every call. */
    public static final class Conversation {
        private final ChatModel model;
        private final List<Message> messages = new ArrayList<>();

        public Conversation(ChatModel model, String system) {
            this.model = model;
            messages.add(new Message("system", system));
        }

        public String say(String content) {
            messages.add(new Message("user", content));
            String text = model.chat(List.copyOf(messages), Options.DEFAULT).text();
            messages.add(new Message("assistant", text));
            return text;
        }
    }

    /** For tests: replies from a script and records what it was sent. */
    public static final class FakeModel implements ChatModel {
        private final List<String> replies;
        public final List<List<Message>> calls = new ArrayList<>();

        public FakeModel(List<String> replies) {
            this.replies = new ArrayList<>(replies);
        }

        @Override
        public ChatResult chat(List<Message> messages, Options options) {
            calls.add(List.copyOf(messages));
            return new ChatResult(replies.removeFirst(), "stop", 0, 0);
        }

        @Override
        public Stream<String> stream(List<Message> messages, Options options) {
            return Stream.of(chat(messages, options).text().split("(?<= )"));
        }
    }

    /**
     * Reads server-sent events. InputStreamReader holds a half-received character and BufferedReader
     * a half-received line, so chunk boundaries never show through.
     */
    public static Iterable<String> sseData(InputStream body) {
        BufferedReader reader = new BufferedReader(new InputStreamReader(body, StandardCharsets.UTF_8));
        return () -> new Iterator<>() {
            private String next = advance();

            private String advance() {
                try {
                    List<String> data = new ArrayList<>();
                    for (String line; (line = reader.readLine()) != null; ) { // readLine also strips \r\n
                        if (line.startsWith("data:")) data.add(line.substring(5).stripLeading());
                        else if (line.isEmpty() && !data.isEmpty()) {
                            String event = String.join("\n", data); // a blank line ends the event
                            return event.equals("[DONE]") ? null : event;
                        }
                    }
                    return null;
                } catch (IOException e) {
                    throw new UncheckedIOException(e);
                }
            }

            @Override public boolean hasNext() { return next != null; }

            @Override public String next() {
                if (next == null) throw new NoSuchElementException();
                String current = next;
                next = advance();
                return current;
            }
        };
    }

    public static final class ModelException extends RuntimeException {
        public final int status;

        public ModelException(int status, String body) {
            super("model request failed: " + status + " " + body.substring(0, Math.min(200, body.length())));
            this.status = status;
        }

        /** Rate limits and server errors are worth retrying; bad requests aren't. */
        public boolean retryable() { return status == 429 || status >= 500; }
    }

    /** Any server speaking the OpenAI chat completions format. Spring AI and LangChain4j wrap the same idea. */
    public static final class OpenAICompatibleModel implements ChatModel {
        private static final ObjectMapper JSON = new ObjectMapper();
        private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
        private final String baseUrl, model, apiKey;
        private final Map<String, Object> extraBody;

        public OpenAICompatibleModel(String baseUrl, String model, String apiKey, Map<String, Object> extraBody) {
            this.baseUrl = baseUrl;
            this.model = model;
            this.apiKey = apiKey;
            this.extraBody = extraBody;
        }

        @Override
        public ChatResult chat(List<Message> messages, Options options) {
            try (InputStream body = post(messages, options, false)) {
                JsonNode data = JSON.readTree(body);
                JsonNode choice = data.path("choices").path(0);
                String reason = switch (choice.path("finish_reason").asText()) {
                    case "stop" -> "stop";
                    case "length" -> "length";
                    default -> "other";
                };
                return new ChatResult(choice.path("message").path("content").asText(""), reason,
                        data.path("usage").path("prompt_tokens").asInt(), data.path("usage").path("completion_tokens").asInt());
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            }
        }

        @Override
        public Stream<String> stream(List<Message> messages, Options options) {
            InputStream body = post(messages, options, true);
            return StreamSupport.stream(sseData(body).spliterator(), false)
                    .map(data -> {
                        try {
                            return JSON.readTree(data).path("choices").path(0).path("delta").path("content").asText("");
                        } catch (IOException e) {
                            throw new UncheckedIOException(e);
                        }
                    })
                    .filter(delta -> !delta.isEmpty())
                    .onClose(() -> {
                        try {
                            body.close();
                        } catch (IOException e) {
                            throw new UncheckedIOException(e);
                        }
                    });
        }

        /** Never hard-code model names from memory: ask the server. */
        public List<String> listModels() {
            try (InputStream body = send(request("/models").GET().build())) {
                List<String> ids = new ArrayList<>();
                JSON.readTree(body).path("data").forEach(m -> ids.add(m.path("id").asText()));
                return ids.stream().sorted().toList();
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            }
        }

        private InputStream post(List<Message> messages, Options options, boolean stream) {
            Map<String, Object> body = new LinkedHashMap<>();
            body.put("model", model);
            body.put("messages", messages);
            body.put("stream", stream);
            body.putAll(extraBody);
            if (options.temperature() != null) body.put("temperature", options.temperature());
            if (options.maxTokens() != null) body.put("max_tokens", options.maxTokens());
            try {
                return send(request("/chat/completions").header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(JSON.writeValueAsBytes(body))).build());
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            }
        }

        private HttpRequest.Builder request(String path) {
            HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(baseUrl + path)).timeout(Duration.ofMinutes(2));
            return apiKey == null ? builder : builder.header("Authorization", "Bearer " + apiKey);
        }

        private InputStream send(HttpRequest request) {
            try {
                HttpResponse<InputStream> res = http.send(request, HttpResponse.BodyHandlers.ofInputStream());
                if (res.statusCode() >= 300) {
                    try (InputStream body = res.body()) {
                        throw new ModelException(res.statusCode(), new String(body.readAllBytes(), StandardCharsets.UTF_8));
                    }
                }
                return res.body();
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IllegalStateException(e);
            }
        }
    }
}
```

```java
package models;

import com.sun.net.httpserver.HttpServer;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import models.Models.*;

/** Checks, run with `java -ea`. The fake server is the JDK's own HttpServer on a free port. */
public final class ModelsCheck {
    record Recorded(String path, String authorization, String body) {}
    record Canned(int status, String body) {}

    static final class FakeServer implements AutoCloseable {
        final List<Recorded> requests = new ArrayList<>();
        final HttpServer server;

        FakeServer(Canned... responses) throws IOException {
            List<Canned> queue = new ArrayList<>(List.of(responses));
            server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.createContext("/", exchange -> {
                String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                requests.add(new Recorded(exchange.getRequestURI().getPath(), exchange.getRequestHeaders().getFirst("Authorization"), body));
                Canned reply = queue.removeFirst();
                byte[] bytes = reply.body().getBytes(StandardCharsets.UTF_8);
                exchange.sendResponseHeaders(reply.status(), bytes.length);
                exchange.getResponseBody().write(bytes);
                exchange.close();
            });
            server.start();
        }

        OpenAICompatibleModel model() {
            return new OpenAICompatibleModel("http://127.0.0.1:" + server.getAddress().getPort() + "/v1", "some-model", "sk-test", Map.of());
        }

        @Override public void close() { server.stop(0); }
    }

    /** One byte per read: every possible split, including inside a two-byte character. */
    static InputStream oneByteAtATime(String text) {
        InputStream all = new ByteArrayInputStream(text.getBytes(StandardCharsets.UTF_8));
        return new InputStream() {
            @Override public int read() throws IOException { return all.read(); }
            @Override public int read(byte[] b, int off, int len) throws IOException { return len == 0 ? 0 : all.read(b, off, 1); }
        };
    }

    static void check(Object got, Object want) {
        if (!got.equals(want)) throw new AssertionError("got " + got + ", want " + want);
    }

    public static void main(String[] args) throws IOException {
        try (var server = new FakeServer(new Canned(200,
                "{\"choices\":[{\"message\":{\"content\":\"Paris\"},\"finish_reason\":\"stop\"}],\"usage\":{\"prompt_tokens\":21,\"completion_tokens\":2}}"))) {
            ChatResult result = server.model().chat(List.of(new Message("user", "Capital of France?")), new Options(0.0, 5));
            check(result, new ChatResult("Paris", "stop", 21, 2));
            Recorded req = server.requests.getFirst();
            check(req.path(), "/v1/chat/completions");
            check(req.authorization(), "Bearer sk-test");
            check(req.body(), "{\"model\":\"some-model\",\"messages\":[{\"role\":\"user\",\"content\":\"Capital of France?\"}],"
                    + "\"stream\":false,\"temperature\":0.0,\"max_tokens\":5}");
        }

        try (var server = new FakeServer(new Canned(200, "{\"choices\":[{\"message\":{\"content\":\"The capital of\"},\"finish_reason\":\"length\"}]}"))) {
            check(server.model().chat(List.of(), Options.DEFAULT).finishReason(), "length");
        }

        try (var server = new FakeServer(new Canned(429, "slow down"), new Canned(400, "bad model name"))) {
            for (var want : List.of(Map.entry(429, true), Map.entry(400, false))) {
                try {
                    server.model().chat(List.of(), Options.DEFAULT);
                    throw new AssertionError("expected an error");
                } catch (ModelException e) {
                    check(Map.entry(e.status, e.retryable()), want);
                }
            }
        }

        List<String> events = new ArrayList<>();
        Models.sseData(oneByteAtATime("data: {\"a\":1}\n\ndata: {\"b\":\"café\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n")).forEach(events::add);
        check(events, List.of("{\"a\":1}", "{\"b\":\"café\"}"));

        String deltas = Stream.of("Hel", "lo", ", world")
                .map(text -> "data: {\"choices\":[{\"delta\":{\"content\":\"" + text + "\"}}]}\n\n")
                .reduce("", String::concat) + "data: [DONE]\n\n";
        try (var server = new FakeServer(new Canned(200, deltas));
             Stream<String> parts = server.model().stream(List.of(new Message("user", "hi")), Options.DEFAULT)) {
            check(parts.toList(), List.of("Hel", "lo", ", world"));
            check(server.requests.getFirst().body().contains("\"stream\":true"), true);
        }

        try (var server = new FakeServer(new Canned(200, "{\"data\":[{\"id\":\"qwen3.5:4b\"},{\"id\":\"gemma4:latest\"}]}"))) {
            check(server.model().listModels(), List.of("gemma4:latest", "qwen3.5:4b"));
            check(server.requests.getFirst().path(), "/v1/models");
        }

        var model = new FakeModel(List.of("Hi Kingsley.", "Your name is Kingsley."));
        var chat = new Conversation(model, "Be brief.");
        chat.say("My name is Kingsley.");
        check(chat.say("What's my name?"), "Your name is Kingsley.");
        check(model.calls.get(0).size(), 2);
        check(model.calls.get(1).stream().map(Message::role).toList(), List.of("system", "user", "assistant", "user"));

        System.out.println("ok: 7 checks passed");
    }
}
```

## 6. Rust

`ureq` is a small blocking HTTP client and `serde` does the JSON, with typed structs for the response. The agent is set up with `http_status_as_error(false)`, so the adapter can read an error's body and keep the status itself. `ModelError` is an enum, so `retryable` is a `match`. The fake server is a plain `TcpListener` that speaks just enough HTTP/1.1 for one request per connection.

```rust
//! A provider-neutral model client: the port, a fake, an OpenAI-compatible adapter and an SSE reader.
//! `ureq` is a small blocking HTTP client; async-openai or ollama-rs are the usual adapters.

use serde::{Deserialize, Serialize};
use serde_json::{Map, Value, json};
use std::io::{BufRead, BufReader, Read};
use std::time::Duration;

#[derive(Clone, Debug, PartialEq, Serialize)]
pub struct Message {
    pub role: &'static str, // "system", "user" or "assistant"
    pub content: String,
}

impl Message {
    pub fn new(role: &'static str, content: impl Into<String>) -> Self {
        Self {
            role,
            content: content.into(),
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct Options {
    pub temperature: Option<f64>, // None means "use the server's default"
    pub max_tokens: Option<u32>,
}

#[derive(Debug, PartialEq)]
pub struct ChatResult {
    pub text: String,
    pub finish_reason: &'static str, // "stop", "length" (max tokens cut it off) or "other"
    pub input_tokens: u32,
    pub output_tokens: u32,
}

#[derive(Debug)]
pub enum ModelError {
    Status { status: u16, body: String },
    Transport(String),
}

impl ModelError {
    /// Rate limits and server errors are worth retrying; bad requests aren't.
    pub fn retryable(&self) -> bool {
        matches!(self, ModelError::Status { status, .. } if *status == 429 || *status >= 500)
            || matches!(self, ModelError::Transport(_))
    }
}

/// Any library error (network, timeout, bad JSON) becomes `Transport`, so `?` works everywhere.
impl<E: std::error::Error> From<E> for ModelError {
    fn from(e: E) -> Self {
        ModelError::Transport(e.to_string())
    }
}

/// The port: all the rest of the app knows about a model.
pub trait ChatModel {
    fn chat(&mut self, messages: &[Message], options: Options) -> Result<ChatResult, ModelError>;
    fn stream(
        &mut self,
        messages: &[Message],
        options: Options,
    ) -> Result<Box<dyn Iterator<Item = Result<String, ModelError>>>, ModelError>;
}

/// The model is stateless: "memory" is the app resending every earlier turn on every call.
pub struct Conversation<M: ChatModel> {
    pub model: M,
    pub messages: Vec<Message>,
}

impl<M: ChatModel> Conversation<M> {
    pub fn new(model: M, system: &str) -> Self {
        Self {
            model,
            messages: vec![Message::new("system", system)],
        }
    }

    pub fn say(&mut self, content: &str) -> Result<String, ModelError> {
        self.messages.push(Message::new("user", content));
        let text = self.model.chat(&self.messages, Options::default())?.text;
        self.messages.push(Message::new("assistant", text.clone()));
        Ok(text)
    }
}

/// For tests: replies from a script and records what it was sent.
#[derive(Default)]
pub struct FakeModel {
    pub replies: Vec<String>,
    pub calls: Vec<Vec<Message>>,
}

impl ChatModel for FakeModel {
    fn chat(&mut self, messages: &[Message], _: Options) -> Result<ChatResult, ModelError> {
        self.calls.push(messages.to_vec());
        let text = self.replies.remove(0);
        Ok(ChatResult {
            text,
            finish_reason: "stop",
            input_tokens: 0,
            output_tokens: 0,
        })
    }

    fn stream(
        &mut self,
        messages: &[Message],
        options: Options,
    ) -> Result<Box<dyn Iterator<Item = Result<String, ModelError>>>, ModelError> {
        let text = self.chat(messages, options)?.text;
        let words: Vec<_> = text
            .split_inclusive(' ')
            .map(|w| Ok(w.to_string()))
            .collect();
        Ok(Box::new(words.into_iter()))
    }
}

/// Reads server-sent events. `BufReader` keeps a partial line between reads, and `lines()` only
/// checks UTF-8 once a whole line has arrived, so a character split between reads is fine.
pub fn sse_data(body: impl Read) -> impl Iterator<Item = Result<String, ModelError>> {
    let mut lines = BufReader::new(body).lines();
    std::iter::from_fn(move || {
        let mut data = Vec::new();
        loop {
            match lines.next() {
                None => return None,
                Some(Err(e)) => return Some(Err(e.into())),
                Some(Ok(line)) => {
                    if let Some(rest) = line.strip_prefix("data:") {
                        data.push(rest.trim_start().to_string());
                    } else if line.is_empty() && !data.is_empty() {
                        let event = data.join("\n"); // a blank line ends the event
                        return (event != "[DONE]").then_some(Ok(event));
                    }
                }
            }
        }
    })
}

/// Any server speaking the OpenAI chat completions format.
pub struct OpenAICompatible {
    pub base_url: String,
    pub model: String,
    pub api_key: Option<String>,
    pub extra_body: Map<String, Value>, // provider-specific fields, e.g. {"reasoning_effort": "none"}
    agent: ureq::Agent,
}

#[derive(Deserialize)]
struct Completion {
    choices: Vec<Choice>,
    #[serde(default)]
    usage: Usage,
}

#[derive(Deserialize)]
struct Choice {
    message: Content,
    finish_reason: Option<String>,
}

#[derive(Deserialize, Default)]
struct Content {
    content: Option<String>,
}

#[derive(Deserialize, Default)]
struct Usage {
    prompt_tokens: u32,
    completion_tokens: u32,
}

#[derive(Deserialize)]
struct Chunk {
    choices: Vec<DeltaChoice>,
}

#[derive(Deserialize)]
struct DeltaChoice {
    #[serde(default)]
    delta: Content,
}

impl OpenAICompatible {
    pub fn new(base_url: &str, model: &str, api_key: Option<&str>) -> Self {
        let agent = ureq::Agent::config_builder()
            .http_status_as_error(false) // read error bodies ourselves, to keep the status and the message
            .timeout_global(Some(Duration::from_secs(120))) // every call needs a timeout
            .build()
            .into();
        Self {
            base_url: base_url.into(),
            model: model.into(),
            api_key: api_key.map(Into::into),
            extra_body: Map::new(),
            agent,
        }
    }

    /// Never hard-code model names from memory: ask the server.
    pub fn list_models(&self) -> Result<Vec<String>, ModelError> {
        let mut request = self.agent.get(format!("{}/models", self.base_url));
        if let Some(key) = &self.api_key {
            request = request.header("Authorization", format!("Bearer {key}"));
        }
        let response = check(request.call()?)?;
        let data: Value = response.into_body().read_json()?;
        let mut ids: Vec<String> = data["data"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|m| m["id"].as_str().map(String::from))
            .collect();
        ids.sort();
        Ok(ids)
    }

    fn post(
        &self,
        messages: &[Message],
        options: Options,
        stream: bool,
    ) -> Result<ureq::Body, ModelError> {
        let mut body = json!({ "model": self.model, "messages": messages, "stream": stream });
        let fields = body.as_object_mut().expect("built as an object");
        fields.extend(self.extra_body.clone());
        if let Some(t) = options.temperature {
            fields.insert("temperature".into(), json!(t));
        }
        if let Some(n) = options.max_tokens {
            fields.insert("max_tokens".into(), json!(n));
        }
        let mut request = self
            .agent
            .post(format!("{}/chat/completions", self.base_url));
        if let Some(key) = &self.api_key {
            request = request.header("Authorization", format!("Bearer {key}"));
        }
        Ok(check(request.send_json(&body)?)?.into_body())
    }
}

fn check(
    response: ureq::http::Response<ureq::Body>,
) -> Result<ureq::http::Response<ureq::Body>, ModelError> {
    let status = response.status().as_u16();
    if status < 300 {
        return Ok(response);
    }
    let body = response.into_body().read_to_string().unwrap_or_default();
    Err(ModelError::Status { status, body })
}

impl ChatModel for OpenAICompatible {
    fn chat(&mut self, messages: &[Message], options: Options) -> Result<ChatResult, ModelError> {
        let data: Completion = self.post(messages, options, false)?.read_json()?;
        let choice = data
            .choices
            .into_iter()
            .next()
            .ok_or(ModelError::Transport("no choices".into()))?;
        let finish_reason = match choice.finish_reason.as_deref() {
            Some("stop") => "stop",
            Some("length") => "length",
            _ => "other",
        };
        Ok(ChatResult {
            text: choice.message.content.unwrap_or_default(),
            finish_reason,
            input_tokens: data.usage.prompt_tokens,
            output_tokens: data.usage.completion_tokens,
        })
    }

    fn stream(
        &mut self,
        messages: &[Message],
        options: Options,
    ) -> Result<Box<dyn Iterator<Item = Result<String, ModelError>>>, ModelError> {
        let body = self.post(messages, options, true)?;
        let deltas = sse_data(body.into_reader()).filter_map(|event| match event {
            Err(e) => Some(Err(e)),
            Ok(data) => match serde_json::from_str::<Chunk>(&data) {
                Err(e) => Some(Err(e.into())),
                Ok(chunk) => chunk
                    .choices
                    .into_iter()
                    .next()
                    .and_then(|c| c.delta.content)
                    .filter(|s| !s.is_empty())
                    .map(Ok),
            },
        });
        Ok(Box::new(deltas))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use std::net::TcpListener;
    use std::sync::{Arc, Mutex};

    #[derive(Debug)]
    struct Recorded {
        path: String,
        authorization: String,
        body: Value,
    }

    /// A real HTTP server on a free port, one canned (status, body) per connection.
    /// Just enough HTTP/1.1 to read one request and write one response.
    fn fake_server(responses: Vec<(u16, String)>) -> (OpenAICompatible, Arc<Mutex<Vec<Recorded>>>) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let url = format!("http://{}/v1", listener.local_addr().unwrap());
        let requests = Arc::new(Mutex::new(Vec::new()));
        let seen = Arc::clone(&requests);
        std::thread::spawn(move || {
            for (status, body) in responses {
                let (mut stream, _) = listener.accept().unwrap();
                let mut reader = BufReader::new(stream.try_clone().unwrap());
                let mut request_line = String::new();
                reader.read_line(&mut request_line).unwrap();
                let (mut length, mut authorization) = (0, String::new());
                loop {
                    let mut header = String::new();
                    reader.read_line(&mut header).unwrap();
                    let Some((name, value)) = header.trim_end().split_once(": ") else {
                        break;
                    };
                    match name.to_ascii_lowercase().as_str() {
                        "content-length" => length = value.parse().unwrap(),
                        "authorization" => authorization = value.into(),
                        _ => {}
                    }
                }
                let mut request_body = vec![0; length];
                reader.read_exact(&mut request_body).unwrap();
                seen.lock().unwrap().push(Recorded {
                    path: request_line.split(' ').nth(1).unwrap().into(),
                    authorization,
                    body: serde_json::from_slice(&request_body).unwrap_or(Value::Null),
                });
                write!(
                    stream,
                    "HTTP/1.1 {status} X\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                    body.len()
                )
                .unwrap();
            }
        });
        (
            OpenAICompatible::new(&url, "some-model", Some("sk-test")),
            requests,
        )
    }

    #[test]
    fn chat_sends_the_messages_format_and_reads_text_finish_reason_and_usage() {
        let (mut model, requests) = fake_server(vec![(
            200,
            r#"{"choices":[{"message":{"content":"Paris"},"finish_reason":"stop"}],"usage":{"prompt_tokens":21,"completion_tokens":2}}"#.into(),
        )]);
        let options = Options {
            temperature: Some(0.0),
            max_tokens: Some(5),
        };
        let result = model
            .chat(&[Message::new("user", "Capital of France?")], options)
            .unwrap();
        assert_eq!(
            result,
            ChatResult {
                text: "Paris".into(),
                finish_reason: "stop",
                input_tokens: 21,
                output_tokens: 2
            }
        );

        let requests = requests.lock().unwrap();
        assert_eq!(requests[0].path, "/v1/chat/completions");
        assert_eq!(requests[0].authorization, "Bearer sk-test");
        assert_eq!(
            requests[0].body,
            json!({"model": "some-model", "messages": [{"role": "user", "content": "Capital of France?"}],
                   "stream": false, "temperature": 0.0, "max_tokens": 5})
        );
    }

    #[test]
    fn a_reply_cut_off_by_max_tokens_says_so() {
        let body =
            r#"{"choices":[{"message":{"content":"The capital of"},"finish_reason":"length"}]}"#;
        let (mut model, _) = fake_server(vec![(200, body.into())]);
        assert_eq!(
            model.chat(&[], Options::default()).unwrap().finish_reason,
            "length"
        );
    }

    #[test]
    fn errors_carry_the_status_and_whether_a_retry_could_help() {
        let (mut model, _) = fake_server(vec![
            (429, "slow down".into()),
            (400, "bad model name".into()),
        ]);
        let rate_limited = model.chat(&[], Options::default()).unwrap_err();
        assert!(
            matches!(&rate_limited, ModelError::Status { status: 429, .. })
                && rate_limited.retryable()
        );
        let bad_request = model.chat(&[], Options::default()).unwrap_err();
        assert!(
            matches!(&bad_request, ModelError::Status { status: 400, body } if body == "bad model name")
        );
        assert!(!bad_request.retryable());
    }

    /// One byte per read: every possible split, including inside a two-byte character.
    struct OneByteAtATime<'a>(&'a [u8]);

    impl Read for OneByteAtATime<'_> {
        fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
            let Some((first, rest)) = self.0.split_first() else {
                return Ok(0);
            };
            buf[0] = *first;
            self.0 = rest;
            Ok(1)
        }
    }

    #[test]
    fn the_sse_reader_survives_events_split_across_reads_even_mid_character() {
        let raw = "data: {\"a\":1}\n\ndata: {\"b\":\"café\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";
        let events: Vec<String> = sse_data(OneByteAtATime(raw.as_bytes()))
            .map(Result::unwrap)
            .collect();
        assert_eq!(events, [r#"{"a":1}"#, r#"{"b":"café"}"#]);
    }

    #[test]
    fn stream_yields_the_text_deltas_in_order() {
        let delta = |text: &str| {
            format!(
                "data: {}\n\n",
                json!({"choices": [{"delta": {"content": text}}]})
            )
        };
        let body = format!(
            "{}{}{}data: [DONE]\n\n",
            delta("Hel"),
            delta("lo"),
            delta(", world")
        );
        let (mut model, requests) = fake_server(vec![(200, body)]);
        let parts: Vec<String> = model
            .stream(&[Message::new("user", "hi")], Options::default())
            .unwrap()
            .map(Result::unwrap)
            .collect();
        assert_eq!(parts, ["Hel", "lo", ", world"]);
        assert_eq!(requests.lock().unwrap()[0].body["stream"], json!(true));
    }

    #[test]
    fn list_models_asks_the_server_instead_of_trusting_memory() {
        let (model, requests) = fake_server(vec![(
            200,
            r#"{"data":[{"id":"qwen3.5:4b"},{"id":"gemma4:latest"}]}"#.into(),
        )]);
        assert_eq!(
            model.list_models().unwrap(),
            ["gemma4:latest", "qwen3.5:4b"]
        );
        assert_eq!(requests.lock().unwrap()[0].path, "/v1/models");
    }

    #[test]
    fn the_model_is_stateless_so_a_conversation_resends_every_turn() {
        let model = FakeModel {
            replies: vec!["Hi Kingsley.".into(), "Your name is Kingsley.".into()],
            ..Default::default()
        };
        let mut chat = Conversation::new(model, "Be brief.");
        chat.say("My name is Kingsley.").unwrap();
        assert_eq!(
            chat.say("What's my name?").unwrap(),
            "Your name is Kingsley."
        );
        assert_eq!(chat.model.calls[0].len(), 2);
        let roles: Vec<_> = chat.model.calls[1].iter().map(|m| m.role).collect();
        assert_eq!(roles, ["system", "user", "assistant", "user"]);
    }
}
```

## 7. C and C++

In C and C++ the HTTP request would go through libcurl, which hands your code each chunk of the response through a write callback, split wherever the network split it. The streaming parser is the part worth writing, and it's the part these labs test. Bytes are just bytes until something reads them as text, so a split `é` needs no special handling; a split *line* still does.

The C parser grows its buffer with `realloc` and calls a function pointer once per event. The test feeds the same stream in every chunk size from 1 byte to the whole thing.

```c
/* An incremental server-sent events parser: feed it bytes as they arrive from the network
   (libcurl's write callback, say), in chunks split anywhere, and it calls back once per event. */
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void (*on_event)(const char *data, void *context);

typedef struct {
    char *pending; /* bytes received but not yet a complete event */
    size_t length, capacity;
    bool done;     /* saw "data: [DONE]" */
    on_event callback;
    void *context;
} SseParser;

static void sse_init(SseParser *p, on_event callback, void *context) {
    *p = (SseParser){.callback = callback, .context = context};
}

static void sse_free(SseParser *p) { free(p->pending); }

/* Handle one complete event (the text between blank lines): join its "data:" lines. */
static void sse_dispatch(SseParser *p, char *event) {
    char data[4096] = "";
    size_t used = 0;
    for (char *line = strtok(event, "\n"); line; line = strtok(NULL, "\n")) {
        if (strncmp(line, "data:", 5) != 0) continue;
        const char *value = line + 5 + (line[5] == ' ');
        used += (size_t)snprintf(data + used, sizeof data - used, "%s%s", used ? "\n" : "", value);
        if (used >= sizeof data) used = sizeof data - 1; /* truncate rather than overflow */
    }
    if (strcmp(data, "[DONE]") == 0) p->done = true;
    else if (used) p->callback(data, p->context);
}

/* Bytes are bytes: a UTF-8 character split between two chunks is simply joined back up.
   Carriage returns are dropped on the way in, so "\r\n" line endings look like "\n". */
static void sse_feed(SseParser *p, const char *chunk, size_t n) {
    if (p->done) return;
    if (p->length + n + 1 > p->capacity) {
        p->capacity = (p->length + n + 1) * 2;
        char *grown = realloc(p->pending, p->capacity);
        if (!grown) abort();
        p->pending = grown;
    }
    for (size_t i = 0; i < n; i++)
        if (chunk[i] != '\r') p->pending[p->length++] = chunk[i];
    p->pending[p->length] = '\0';

    char *end;
    while (!p->done && (end = strstr(p->pending, "\n\n"))) { /* a blank line ends an event */
        *end = '\0';
        sse_dispatch(p, p->pending);
        size_t used = (size_t)(end + 2 - p->pending);
        memmove(p->pending, end + 2, p->length - used + 1);
        p->length -= used;
    }
}

/* --- checks --- */

typedef struct {
    char events[8][64];
    int count;
} Collected;

static void collect(const char *data, void *context) {
    Collected *c = context;
    snprintf(c->events[c->count++], sizeof c->events[0], "%s", data);
}

int main(void) {
    const char *raw = "data: {\"a\":1}\n\ndata: {\"b\":\"caf\xc3\xa9\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";

    /* every chunk size from 1 byte up: every possible split, including inside "é" (0xC3 0xA9) */
    for (size_t size = 1; size <= strlen(raw); size++) {
        Collected got = {0};
        SseParser p;
        sse_init(&p, collect, &got);
        for (size_t at = 0; at < strlen(raw); at += size) {
            size_t n = strlen(raw) - at < size ? strlen(raw) - at : size;
            sse_feed(&p, raw + at, n);
        }
        sse_free(&p);
        assert(got.count == 2);
        assert(strcmp(got.events[0], "{\"a\":1}") == 0);
        assert(strcmp(got.events[1], "{\"b\":\"caf\xc3\xa9\"}") == 0);
    }

    /* a multi-line event, with Windows line endings */
    Collected got = {0};
    SseParser p;
    sse_init(&p, collect, &got);
    const char *multi = "data: first\r\ndata: second\r\n\r\n";
    sse_feed(&p, multi, strlen(multi));
    sse_free(&p);
    assert(got.count == 1 && strcmp(got.events[0], "first\nsecond") == 0);

    puts("ok: every split of the stream gives the same two events");
    return 0;
}
```

The C++ version adds the port: an abstract `ChatModel` class, a fake, and the conversation. The conversation holds a *reference* to the model, so the caller must keep the model alive at least as long as the conversation. That's an ownership decision the other languages never make you write down.

```cpp
// The parts of a model client that don't need an HTTP library: the port as an abstract class,
// a fake, a stateless-model conversation, and an incremental SSE parser to feed from libcurl.
#include <cassert>
#include <deque>
#include <functional>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

struct Message {
    std::string role;  // "system", "user" or "assistant"
    std::string content;
};

struct Options {
    std::optional<double> temperature;  // empty means "use the server's default"
    std::optional<int> max_tokens;
};

struct ChatResult {
    std::string text;
    std::string finish_reason;  // "stop", "length" (max tokens cut it off) or "other"
};

// The port: all the rest of the app knows about a model.
class ChatModel {
public:
    virtual ~ChatModel() = default;
    virtual ChatResult chat(const std::vector<Message>& messages, const Options& options) = 0;
};

// For tests: replies from a script and records what it was sent.
class FakeModel : public ChatModel {
public:
    explicit FakeModel(std::deque<std::string> replies) : replies_(std::move(replies)) {}
    ChatResult chat(const std::vector<Message>& messages, const Options&) override {
        calls.push_back(messages);  // a copy: later changes to the conversation don't rewrite history
        std::string reply = replies_.front();
        replies_.pop_front();
        return {reply, "stop"};
    }
    std::vector<std::vector<Message>> calls;

private:
    std::deque<std::string> replies_;
};

// The model is stateless: "memory" is the app resending every earlier turn on every call.
class Conversation {
public:
    Conversation(ChatModel& model, std::string system) : model_(model) { messages_.push_back({"system", std::move(system)}); }
    std::string say(std::string content) {
        messages_.push_back({"user", std::move(content)});
        std::string text = model_.chat(messages_, {}).text;
        messages_.push_back({"assistant", text});
        return text;
    }

private:
    ChatModel& model_;  // borrowed: the caller owns the model and must keep it alive
    std::vector<Message> messages_;
};

// Feed bytes as they arrive, split anywhere; get one callback per complete event.
class SseParser {
public:
    explicit SseParser(std::function<void(std::string_view)> on_event) : on_event_(std::move(on_event)) {}

    void feed(std::string_view chunk) {
        for (char c : chunk)
            if (c != '\r') pending_ += c;  // "\r\n" line endings become "\n"
        for (std::size_t end; !done_ && (end = pending_.find("\n\n")) != std::string::npos;) {
            dispatch(std::string_view(pending_).substr(0, end));
            pending_.erase(0, end + 2);  // keep only the unfinished tail
        }
    }

private:
    void dispatch(std::string_view event) {
        std::string data;
        while (!event.empty()) {
            std::size_t eol = event.find('\n');
            std::string_view line = event.substr(0, eol);
            event = eol == std::string_view::npos ? std::string_view{} : event.substr(eol + 1);
            if (!line.starts_with("data:")) continue;
            line.remove_prefix(line.starts_with("data: ") ? 6 : 5);
            if (!data.empty()) data += '\n';
            data += line;
        }
        if (data == "[DONE]") done_ = true;
        else if (!data.empty()) on_event_(data);
    }

    std::function<void(std::string_view)> on_event_;
    std::string pending_;
    bool done_ = false;
};

int main() {
    // Every chunk size from 1 byte up: every split, including inside "é" (0xC3 0xA9).
    const std::string raw = "data: {\"a\":1}\n\ndata: {\"b\":\"caf\xc3\xa9\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";
    for (std::size_t size = 1; size <= raw.size(); size++) {
        std::vector<std::string> events;
        SseParser parser([&](std::string_view data) { events.emplace_back(data); });
        for (std::size_t at = 0; at < raw.size(); at += size) parser.feed(std::string_view(raw).substr(at, size));
        assert((events == std::vector<std::string>{"{\"a\":1}", "{\"b\":\"caf\xc3\xa9\"}"}));
    }

    std::vector<std::string> events;
    SseParser parser([&](std::string_view data) { events.emplace_back(data); });
    parser.feed("data: first\r\ndata: second\r\n\r\n");
    assert((events == std::vector<std::string>{"first\nsecond"}));

    FakeModel model({"Hi Kingsley.", "Your name is Kingsley."});
    Conversation chat(model, "Be brief.");
    chat.say("My name is Kingsley.");
    assert(chat.say("What's my name?") == "Your name is Kingsley.");
    assert(model.calls[0].size() == 2);
    std::vector<std::string> roles;
    for (const auto& m : model.calls[1]) roles.push_back(m.role);
    assert((roles == std::vector<std::string>{"system", "user", "assistant", "user"}));

    std::cout << "ok: every split of the stream gives the same events; the conversation resends every turn\n";
}
```

## 8. C#

`HttpClient` with a fake `HttpMessageHandler` is the standard .NET way to test HTTP code: the real client runs its whole pipeline, and only the final send is replaced. `StreamAsync` is an `IAsyncEnumerable<string>`. `HttpCompletionOption.ResponseHeadersRead` makes it return as soon as the headers arrive, so streaming starts before the body has finished. The response is disposed when the caller's `await foreach` ends.

```csharp
// A provider-neutral model client: the port, a fake, an OpenAI-compatible adapter and an SSE reader.
// In production .NET, Microsoft.Extensions.AI's IChatClient is the standard port, with adapters for
// OpenAI, Ollama and Azure; this is the same shape, written out so you can see what it does.
using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

public record Message(string Role, string Content); // Role: "system", "user" or "assistant"

public record Options(double? Temperature = null, int? MaxTokens = null); // null: the server's default

public record ChatResult(string Text, string FinishReason, int InputTokens, int OutputTokens); // "stop", "length" or "other"

/// <summary>The port: all the rest of the app knows about a model.</summary>
public interface IChatModel
{
    Task<ChatResult> ChatAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default);
    IAsyncEnumerable<string> StreamAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default);
}

/// <summary>The model is stateless: "memory" is the app resending every earlier turn on every call.</summary>
public class Conversation(IChatModel model, string system)
{
    public List<Message> Messages { get; } = [new("system", system)];

    public async Task<string> SayAsync(string content)
    {
        Messages.Add(new("user", content));
        var text = (await model.ChatAsync([.. Messages])).Text;
        Messages.Add(new("assistant", text));
        return text;
    }
}

/// <summary>For tests: replies from a script and records what it was sent.</summary>
public class FakeModel(params string[] replies) : IChatModel
{
    readonly Queue<string> _replies = new(replies);
    public List<List<Message>> Calls { get; } = [];

    public Task<ChatResult> ChatAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default)
    {
        Calls.Add([.. messages]);
        return Task.FromResult(new ChatResult(_replies.Dequeue(), "stop", 0, 0));
    }

    public async IAsyncEnumerable<string> StreamAsync(IReadOnlyList<Message> messages, Options? options = null,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        foreach (var word in (await ChatAsync(messages, options, ct)).Text.Split(' ')) yield return word;
    }
}

public class ModelException(int status, string body)
    : Exception($"model request failed: {status} {body[..Math.Min(200, body.Length)]}")
{
    public int Status { get; } = status;
    public bool Retryable => Status == 429 || Status >= 500; // rate limits and server errors; never a 400
}

public static class Sse
{
    /// <summary>Reads server-sent events. StreamReader holds half a character and half a line between
    /// reads, so chunk boundaries never show through.</summary>
    public static async IAsyncEnumerable<string> DataAsync(Stream body, [EnumeratorCancellation] CancellationToken ct = default)
    {
        using var reader = new StreamReader(body, Encoding.UTF8);
        var data = new List<string>();
        while (await reader.ReadLineAsync(ct) is { } line) // ReadLine also strips "\r\n"
        {
            if (line.StartsWith("data:")) data.Add(line[5..].TrimStart());
            else if (line.Length == 0 && data.Count > 0)
            {
                var ev = string.Join("\n", data); // a blank line ends the event
                data.Clear();
                if (ev == "[DONE]") yield break;
                yield return ev;
            }
        }
    }
}

/// <summary>Any server speaking the OpenAI chat completions format. Give the HttpClient a Timeout.</summary>
public class OpenAICompatibleModel(HttpClient http, string model, string? apiKey = null,
    IReadOnlyDictionary<string, object?>? extraBody = null) : IChatModel
{
    public async Task<ChatResult> ChatAsync(IReadOnlyList<Message> messages, Options? options = null, CancellationToken ct = default)
    {
        using var res = await PostAsync(messages, options, stream: false, ct);
        var data = JsonNode.Parse(await res.Content.ReadAsStringAsync(ct))!;
        var choice = data["choices"]![0]!;
        var reason = (string?)choice["finish_reason"] switch { "stop" => "stop", "length" => "length", _ => "other" };
        return new ChatResult((string?)choice["message"]?["content"] ?? "", reason,
            (int?)data["usage"]?["prompt_tokens"] ?? 0, (int?)data["usage"]?["completion_tokens"] ?? 0);
    }

    public async IAsyncEnumerable<string> StreamAsync(IReadOnlyList<Message> messages, Options? options = null,
        [EnumeratorCancellation] CancellationToken ct = default)
    {
        using var res = await PostAsync(messages, options, stream: true, ct); // disposed when the caller stops
        await foreach (var data in Sse.DataAsync(await res.Content.ReadAsStreamAsync(ct), ct))
            if ((string?)JsonNode.Parse(data)!["choices"]?[0]?["delta"]?["content"] is { Length: > 0 } delta)
                yield return delta;
    }

    /// <summary>Never hard-code model names from memory: ask the server.</summary>
    public async Task<List<string>> ListModelsAsync(CancellationToken ct = default)
    {
        using var res = await SendAsync(new HttpRequestMessage(HttpMethod.Get, "models"), HttpCompletionOption.ResponseContentRead, ct);
        var data = JsonNode.Parse(await res.Content.ReadAsStringAsync(ct))!;
        return [.. data["data"]!.AsArray().Select(m => (string)m!["id"]!).Order()];
    }

    Task<HttpResponseMessage> PostAsync(IReadOnlyList<Message> messages, Options? options, bool stream, CancellationToken ct)
    {
        var body = new JsonObject
        {
            ["model"] = model,
            ["messages"] = JsonSerializer.SerializeToNode(messages.Select(m => new { role = m.Role, content = m.Content })),
            ["stream"] = stream,
        };
        foreach (var (key, value) in extraBody ?? new Dictionary<string, object?>()) body[key] = JsonSerializer.SerializeToNode(value);
        if (options?.Temperature is { } t) body["temperature"] = t;
        if (options?.MaxTokens is { } n) body["max_tokens"] = n;
        var request = new HttpRequestMessage(HttpMethod.Post, "chat/completions") { Content = JsonContent.Create(body) };
        // ResponseHeadersRead: return as soon as headers arrive, so streaming starts before the body ends
        return SendAsync(request, HttpCompletionOption.ResponseHeadersRead, ct);
    }

    async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, HttpCompletionOption completion, CancellationToken ct)
    {
        if (apiKey is not null) request.Headers.Authorization = new("Bearer", apiKey);
        var res = await http.SendAsync(request, completion, ct);
        if (res.IsSuccessStatusCode) return res;
        using (res) throw new ModelException((int)res.StatusCode, await res.Content.ReadAsStringAsync(ct));
    }
}
```

```csharp
// Checks. The fake server is an HttpMessageHandler: HttpClient runs its whole pipeline, minus the network.
using System.Net;
using System.Text;
using System.Text.Json.Nodes;

static void Check<T>(T got, T want)
{
    if (!EqualityComparer<T>.Default.Equals(got, want)) throw new Exception($"got {got}, want {want}");
}
static void CheckAll<T>(IEnumerable<T> got, IEnumerable<T> want)
{
    if (!got.SequenceEqual(want)) throw new Exception($"got [{string.Join(", ", got)}], want [{string.Join(", ", want)}]");
}
static (OpenAICompatibleModel, FakeHandler) Serve(params (HttpStatusCode, string)[] responses)
{
    var handler = new FakeHandler(responses);
    var http = new HttpClient(handler) { BaseAddress = new Uri("http://model.test/v1/"), Timeout = TimeSpan.FromMinutes(2) };
    return (new OpenAICompatibleModel(http, "some-model", "sk-test"), handler);
}

{
    var (model, handler) = Serve((HttpStatusCode.OK,
        """{"choices":[{"message":{"content":"Paris"},"finish_reason":"stop"}],"usage":{"prompt_tokens":21,"completion_tokens":2}}"""));
    var result = await model.ChatAsync([new("user", "Capital of France?")], new(Temperature: 0, MaxTokens: 5));
    Check(result, new ChatResult("Paris", "stop", 21, 2));
    var req = handler.Requests[0];
    Check(req.Url, "http://model.test/v1/chat/completions");
    Check(req.Authorization, "Bearer sk-test");
    Check(req.Body, """{"model":"some-model","messages":[{"role":"user","content":"Capital of France?"}],"stream":false,"temperature":0,"max_tokens":5}""");
}
{
    var (model, _) = Serve((HttpStatusCode.OK, """{"choices":[{"message":{"content":"The capital of"},"finish_reason":"length"}]}"""));
    Check((await model.ChatAsync([])).FinishReason, "length");
}
{
    var (model, _) = Serve((HttpStatusCode.TooManyRequests, "slow down"), (HttpStatusCode.BadRequest, "bad model name"));
    foreach (var (status, retryable) in new[] { (429, true), (400, false) })
    {
        try { await model.ChatAsync([]); throw new Exception("expected an error"); }
        catch (ModelException e) { Check((e.Status, e.Retryable), (status, retryable)); }
    }
}
{
    var raw = "data: {\"a\":1}\n\ndata: {\"b\":\"café\"}\n\ndata: [DONE]\n\ndata: {\"ignored\":true}\n\n";
    var events = new List<string>();
    await foreach (var data in Sse.DataAsync(new OneByteAtATime(Encoding.UTF8.GetBytes(raw)))) events.Add(data);
    CheckAll(events, ["{\"a\":1}", "{\"b\":\"café\"}"]);
}
{
    static string Delta(string text) => $"data: {new JsonObject { ["choices"] = new JsonArray(new JsonObject { ["delta"] = new JsonObject { ["content"] = text } }) }.ToJsonString()}\n\n";
    var (model, handler) = Serve((HttpStatusCode.OK, Delta("Hel") + Delta("lo") + Delta(", world") + "data: [DONE]\n\n"));
    var parts = new List<string>();
    await foreach (var part in model.StreamAsync([new("user", "hi")])) parts.Add(part);
    CheckAll(parts, ["Hel", "lo", ", world"]);
    Check(handler.Requests[0].Body.Contains("\"stream\":true"), true);
}
{
    var (model, handler) = Serve((HttpStatusCode.OK, """{"data":[{"id":"qwen3.5:4b"},{"id":"gemma4:latest"}]}"""));
    CheckAll(await model.ListModelsAsync(), ["gemma4:latest", "qwen3.5:4b"]);
    Check(handler.Requests[0].Url, "http://model.test/v1/models");
}
{
    var model = new FakeModel("Hi Kingsley.", "Your name is Kingsley.");
    var chat = new Conversation(model, "Be brief.");
    await chat.SayAsync("My name is Kingsley.");
    Check(await chat.SayAsync("What's my name?"), "Your name is Kingsley.");
    Check(model.Calls[0].Count, 2);
    CheckAll(model.Calls[1].Select(m => m.Role), ["system", "user", "assistant", "user"]);
}
Console.WriteLine("ok: 7 checks passed");

record Recorded(string Url, string? Authorization, string Body);

class FakeHandler((HttpStatusCode Status, string Body)[] responses) : HttpMessageHandler
{
    readonly Queue<(HttpStatusCode Status, string Body)> _responses = new(responses);
    public List<Recorded> Requests { get; } = [];

    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var body = request.Content is null ? "" : await request.Content.ReadAsStringAsync(ct);
        Requests.Add(new(request.RequestUri!.ToString(), request.Headers.Authorization?.ToString(), body));
        var (status, reply) = _responses.Dequeue();
        return new HttpResponseMessage(status) { Content = new StringContent(reply) };
    }
}

/// <summary>One byte per read: every possible split, including inside a two-byte character.</summary>
class OneByteAtATime(byte[] bytes) : MemoryStream(bytes)
{
    public override int Read(byte[] buffer, int offset, int count) => base.Read(buffer, offset, Math.Min(count, 1));
    public override int Read(Span<byte> buffer) => base.Read(buffer[..Math.Min(buffer.Length, 1)]);
    public override ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken ct = default) =>
        base.ReadAsync(buffer[..Math.Min(buffer.Length, 1)], ct);
    public override Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken ct) =>
        base.ReadAsync(buffer, offset, Math.Min(count, 1), ct);
}
```

**Labs:** every version is in [`ai-ml/03-ai-engineer/04-calling-models/labs/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/04-calling-models/labs), one folder per language. From the vault root, `python3 labs/run.py calling-models` runs all eight and checks this page still shows the same code. The Java lab downloads Jackson on its first run; the C# lab runs in the .NET SDK container, through podman.

## Common pitfalls

1. **A stream nobody closes.** Stopping halfway through a streamed reply without closing it leaks a connection. Use the language's closing construct: `for range` in Go, try-with-resources in Java, `await foreach` and `using` in C#, `with` in Python.
2. **Case-sensitive header lookups.** HTTP header names ignore case. A plain dictionary doesn't.
3. **No timeout.** Go's `http.DefaultClient` and Python's `urlopen` wait forever unless you say otherwise. Set one on every client.
4. **Throwing away the error body.** Many HTTP clients raise an exception on 4xx and 5xx responses, and the provider's explanation, such as "model not found", can get lost with it. Read the body before raising your own error.
5. **Writing a port when your ecosystem has one.** In .NET and Spring, `IChatClient` and `ChatClient` already exist. Write an adapter for them instead.
6. **A dangling model in C++.** `Conversation` borrows the model by reference; destroy the model first and the next call is undefined behaviour.

## Check your understanding

1. In which languages does the standard library glue half-lines back together for you? In which do you keep the tail yourself?
2. Why does Go not need anything like `TextDecoder({ stream: true })`?
3. What does a fake `HttpMessageHandler` test in C# that replacing the whole model with `FakeModel` doesn't?
4. Why does the Java adapter return a `Stream` with `onClose`, rather than an `Iterable`?
5. What is `IChatClient`, and how does it relate to the main lesson's `ChatModel`?

<details>
<summary>Answers — after your attempt</summary>

1. Go (`bufio.Scanner`), Java (`BufferedReader`), Rust (`BufReader`) and C# (`StreamReader`) do it for you. TypeScript, Python, C and C++ keep the tail in their own code.
2. Go strings are byte sequences. Joining two halves of a character just puts the bytes back together, and nothing checks UTF-8 until you ask it to.
3. The adapter itself: the exact request body, the URL, the authorization header, how the response is parsed, and how errors are mapped. `FakeModel` replaces the adapter, so it tests the code *above* the port instead.
4. A `Stream` can carry a close action, and try-with-resources runs it even if the caller stops early. A plain `Iterable` has no way to say "I'm done", so a caller that stopped early would leak the connection.
5. It's .NET's standard port for chat models, from `Microsoft.Extensions.AI`. It plays the same role as `ChatModel`: the app depends on the interface, and adapters for OpenAI, Ollama or Azure plug in behind it.

</details>

## Practice — independent task

**Point your language's version at the real model.** Take the lab for the language you use most.

1. Write a `live` script that uses the adapter against `http://127.0.0.1:11434/v1`, lists the models, and streams one reply from `qwen3.5:4b` with `reasoning_effort: "none"` in the extra body.
2. Measure time to first token and the total time, like the main lesson's `live.ts`.
3. Then swap the hand-written adapter for that ecosystem's official SDK or standard port from §1, keeping the same `Conversation` code and tests.

**Done when:** the live script prints a reply and both times, the tests still pass after the swap, and you can say in one sentence what the SDK did that your adapter didn't.

## Before moving on

You can name your language's SDK and standard port, explain who handles split chunks in your language, and test a model client without a network.

**Recap.** Every language can build the same port, fake and adapter; the differences are in the plumbing. Go, Java, Rust and C# readers glue split lines and characters back together for you; TypeScript and Python need an incremental decoder; C and C++ work in bytes and only need to keep the unfinished line. Close streams with the language's own construct. Where the ecosystem has a standard port — `IChatClient`, Spring AI's `ChatClient` — use it.

## Related
- [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — the main lesson
- [[ai-ml/03-ai-engineer/02-how-llms-work/in-other-languages|How LLMs work in other languages]] — tokenizers and local inference by language
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/in-other-languages|Hexagonal architecture in other languages]] — ports and adapters in general
