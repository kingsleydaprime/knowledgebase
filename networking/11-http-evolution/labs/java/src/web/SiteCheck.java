package web;

import java.io.ByteArrayOutputStream;
import java.net.Socket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

/** The same checks as every other language. Run with -ea. */
public final class SiteCheck {
    private SiteCheck() {}

    public static void main(String[] args) throws Exception {
        var server = Site.start();
        int port = server.getAddress().getPort();
        URI base = URI.create("http://127.0.0.1:" + port);
        try {
            // Keep-alive: one HttpClient reuses its connection; a new client per request (a common mistake) can't.
            for (boolean shared : new boolean[] {false, true}) {
                Site.CLIENT_PORTS.clear();
                var one = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
                for (int i = 0; i < 10; i++) {
                    var client = shared ? one : HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
                    var res = client.send(HttpRequest.newBuilder(base.resolve("/fast")).build(), HttpResponse.BodyHandlers.ofString());
                    assert res.body().equals("fast");
                    if (!shared) client.close(); // HttpClient is AutoCloseable since Java 21
                }
                one.close();
                assert Site.CLIENT_PORTS.size() == (shared ? 1 : 10) : shared + ": " + Site.CLIENT_PORTS.size();
            }

            // Head-of-line blocking: two requests pipelined on one connection come back in order, slow first.
            String pipelined = raw(port, "GET /slow HTTP/1.1\r\nHost: shop\r\n\r\nGET /fast HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n");
            assert pipelined.indexOf("slow") < pipelined.indexOf("fast") : pipelined;

            // Revalidation: the second request carries the ETag and gets a 304 with no body.
            try (var client = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build()) {
                var first = client.send(HttpRequest.newBuilder(base.resolve("/style.css")).build(), HttpResponse.BodyHandlers.ofString());
                assert first.statusCode() == 200 && first.headers().firstValue("Cache-Control").orElseThrow().equals("max-age=60");
                var again = client.send(HttpRequest.newBuilder(base.resolve("/style.css"))
                        .header("If-None-Match", first.headers().firstValue("ETag").orElseThrow()).build(), HttpResponse.BodyHandlers.ofString());
                assert again.statusCode() == 304 && again.body().isEmpty();
            }

            // Chunked encoding, as bytes on the wire.
            String stream = raw(port, "GET /stream HTTP/1.1\r\nHost: shop\r\nConnection: close\r\n\r\n");
            String head = stream.substring(0, stream.indexOf("\r\n\r\n"));
            String body = stream.substring(stream.indexOf("\r\n\r\n") + 4);
            assert head.toLowerCase().contains("transfer-encoding: chunked") : head;
            assert body.equals("5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n") : body;
        } finally {
            server.stop(0);
        }
        System.out.println("all http checks passed");
    }

    /** Sends raw bytes on a fresh connection and reads until the server closes it. */
    static String raw(int port, String request) throws Exception {
        try (var socket = new Socket("127.0.0.1", port)) {
            socket.getOutputStream().write(request.getBytes(StandardCharsets.US_ASCII));
            var out = new ByteArrayOutputStream();
            socket.getInputStream().transferTo(out);
            return out.toString(StandardCharsets.US_ASCII);
        }
    }
}
