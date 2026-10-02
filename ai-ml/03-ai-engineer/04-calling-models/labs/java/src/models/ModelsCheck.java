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
