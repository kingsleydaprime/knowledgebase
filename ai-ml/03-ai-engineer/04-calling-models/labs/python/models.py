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
