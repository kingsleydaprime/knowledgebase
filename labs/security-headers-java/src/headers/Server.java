package headers;

import com.sun.net.httpserver.Filter;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Set;

// The JDK's built-in HTTP server with a Filter adding headers. In Spring, Spring Security's
// http.headers(...) sets these by default, and a CorsConfigurationSource holds the allowlist.
public final class Server {
    static final Set<String> ALLOWED = Set.of("https://app.example.com");

    static final class SecurityHeaders extends Filter {
        @Override public void doFilter(HttpExchange ex, Chain chain) throws IOException {
            var h = ex.getResponseHeaders();
            h.set("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'");
            h.set("X-Content-Type-Options", "nosniff");
            h.set("Referrer-Policy", "strict-origin-when-cross-origin");
            h.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
            h.add("Vary", "Origin");
            String origin = ex.getRequestHeaders().getFirst("Origin");
            if (origin != null && ALLOWED.contains(origin)) {
                h.set("Access-Control-Allow-Origin", origin);
                h.set("Access-Control-Allow-Credentials", "true");
            }
            chain.doFilter(ex);
        }
        @Override public String description() { return "security headers and CORS"; }
    }

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        var context = server.createContext("/me", ex -> {
            byte[] body = "{\"email\":\"ada@x.com\"}".getBytes(StandardCharsets.UTF_8);
            ex.getResponseHeaders().set("Content-Type", "application/json");
            ex.sendResponseHeaders(200, body.length);
            try (var out = ex.getResponseBody()) { out.write(body); }
        });
        context.getFilters().add(new SecurityHeaders());
        server.start();
        try (var client = HttpClient.newHttpClient()) {
            String base = "http://127.0.0.1:" + server.getAddress().getPort() + "/me";
            // Origin is a restricted header in java.net.http; check.sh allows it with a system property.
            HttpResponse<String> ours = client.send(request(base, "https://app.example.com"), HttpResponse.BodyHandlers.ofString());
            HttpResponse<String> evil = client.send(request(base, "https://evil.example"), HttpResponse.BodyHandlers.ofString());
            assert ours.headers().firstValue("x-content-type-options").orElse("").equals("nosniff");
            assert ours.headers().firstValue("access-control-allow-origin").orElse("").equals("https://app.example.com");
            assert evil.headers().firstValue("access-control-allow-origin").isEmpty();
            assert evil.body().contains("ada@x.com") : "CORS is not access control";
            System.out.println("ok: filter headers, CORS allowlist, and the body still reaches non-browsers");
        } finally {
            server.stop(0);
        }
    }

    static HttpRequest request(String url, String origin) {
        return HttpRequest.newBuilder(URI.create(url)).header("Origin", origin).build();
    }
}
