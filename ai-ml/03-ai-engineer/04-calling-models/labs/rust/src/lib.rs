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
