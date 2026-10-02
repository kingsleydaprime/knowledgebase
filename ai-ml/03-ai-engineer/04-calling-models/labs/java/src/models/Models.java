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
