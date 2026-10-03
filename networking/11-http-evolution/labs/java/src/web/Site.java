package web;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;

/**
 * The same small site as the TypeScript lab, on the JDK's built-in HTTP server. That server speaks HTTP/1.1 only;
 * the JDK's HttpClient speaks HTTP/2, but an HTTP/2 server needs a library such as Jetty or Netty.
 */
public final class Site {
    private Site() {}

    static final byte[] ASSET = "body { color: rebeccapurple; }\n".getBytes(StandardCharsets.UTF_8);
    static final String ETAG;

    static {
        try {
            ETAG = "\"" + HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(ASSET)).substring(0, 16) + "\"";
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    /** The client ports seen: each TCP connection comes from its own port, so this counts connections. */
    public static final Set<Integer> CLIENT_PORTS = ConcurrentHashMap.newKeySet();

    public static HttpServer start() throws IOException {
        var server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);
        server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());
        server.createContext("/", Site::handle);
        server.start();
        return server;
    }

    private static void handle(HttpExchange ex) throws IOException {
        CLIENT_PORTS.add(ex.getRemoteAddress().getPort());
        try (ex) {
            switch (ex.getRequestURI().getPath()) {
                case "/fast" -> send(ex, 200, "fast");
                case "/slow" -> {
                    sleep(200);
                    send(ex, 200, "slow");
                }
                case "/style.css" -> {
                    ex.getResponseHeaders().set("ETag", ETAG);
                    if (ETAG.equals(ex.getRequestHeaders().getFirst("If-None-Match"))) {
                        ex.sendResponseHeaders(304, -1); // -1: no body at all
                    } else {
                        ex.getResponseHeaders().set("Cache-Control", "max-age=60");
                        ex.sendResponseHeaders(200, ASSET.length);
                        ex.getResponseBody().write(ASSET);
                    }
                }
                case "/stream" -> {
                    ex.sendResponseHeaders(200, 0); // 0 means "length unknown": the server sends it chunked
                    var out = ex.getResponseBody();
                    out.write("hello".getBytes(StandardCharsets.UTF_8));
                    out.flush(); // send this chunk now
                    sleep(20);
                    out.write(" world".getBytes(StandardCharsets.UTF_8));
                }
                default -> ex.sendResponseHeaders(404, -1);
            }
        }
    }

    private static void send(HttpExchange ex, int status, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.sendResponseHeaders(status, bytes.length);
        ex.getResponseBody().write(bytes);
    }

    private static void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
