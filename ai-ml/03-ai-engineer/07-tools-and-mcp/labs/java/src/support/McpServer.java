package support;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import support.Tools.Tool;
import support.Tools.ToolCall;
import support.Tools.ToolResult;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.node.ObjectNode;

/** The support tools as an MCP server over stdio, protocol revision 2026-07-28, by hand.
 *  The official Java SDK (mcp 2.0.1) speaks 2025-11-25, so this one is written the way the
 *  TypeScript lab's is: one JSON-RPC message per line on stdin and stdout.
 *    java support.McpServer              all three tools
 *    java support.McpServer --read-only  only the tools that change nothing */
public final class McpServer {
    static final String VERSION = "2026-07-28", KEY = "io.modelcontextprotocol/";

    static ObjectNode handle(JsonNode message, List<Tool> tools) {
        if (!message.has("id")) return null; // a notification: nothing to reply to
        JsonNode id = message.get("id"), params = message.path("params"), meta = params.path("_meta");
        // No handshake: every request says which protocol version it speaks and what the client can do.
        if (!meta.has(KEY + "protocolVersion") || !meta.has(KEY + "clientCapabilities")) {
            return error(id, -32602, "every request must carry protocolVersion and clientCapabilities in _meta", null);
        }
        String version = meta.get(KEY + "protocolVersion").asString();
        if (!version.equals(VERSION)) {
            var data = Tools.JSON.createObjectNode().put("requested", version);
            data.putArray("supported").add(VERSION);
            return error(id, -32022, "unsupported protocol version " + version, data);
        }
        return switch (message.path("method").asString()) {
            case "server/discover" -> {
                var r = Tools.JSON.createObjectNode();
                r.putArray("supportedVersions").add(VERSION);
                r.putObject("capabilities").putObject("tools");
                r.put("instructions", "Order and refund tools for a support assistant. Look an order up before answering about it.");
                yield result(id, r.put("ttlMs", 3_600_000).put("cacheScope", "public"));
            }
            case "tools/list" -> {
                var r = Tools.JSON.createObjectNode();
                var list = r.putArray("tools"); // always the same order, for the client's cache and the model's
                for (Tool t : tools) {
                    var spec = t.spec();
                    spec.putObject("annotations").put("readOnlyHint", !t.sideEffects()).put("destructiveHint", t.sideEffects());
                    list.add(spec);
                }
                yield result(id, r.put("ttlMs", 300_000).put("cacheScope", "public"));
            }
            case "tools/call" -> {
                String name = params.path("name").asString();
                if (tools.stream().noneMatch(t -> t.name().equals(name))) yield error(id, -32602, "Unknown tool: " + name, null);
                // Approval is the host's job: it asks the person before calling a destructive tool.
                ToolResult outcome = Tools.execute(new ToolCall(id.toString(), name, params.path("arguments").toString()), tools, (n, a) -> true);
                var r = Tools.JSON.createObjectNode();
                r.putArray("content").addObject().put("type", "text").put("text", outcome.content());
                yield result(id, r.put("isError", outcome.isError()));
            }
            default -> error(id, -32601, "Method not found: " + message.path("method").asString(), null);
        };
    }

    static ObjectNode result(JsonNode id, ObjectNode body) {
        var full = Tools.JSON.createObjectNode().put("resultType", "complete");
        full.setAll(body);
        full.putObject("_meta").putObject(KEY + "serverInfo").put("name", "support-tools").put("version", "1.0.0");
        var reply = Tools.JSON.createObjectNode().put("jsonrpc", "2.0").set("id", id);
        return reply.set("result", full);
    }

    static ObjectNode error(JsonNode id, int code, String text, ObjectNode data) {
        var err = Tools.JSON.createObjectNode().put("code", code).put("message", text);
        if (data != null) err.set("data", data);
        var reply = Tools.JSON.createObjectNode().put("jsonrpc", "2.0").set("id", id);
        return reply.set("error", err);
    }

    public static void main(String[] args) throws Exception {
        var all = Tools.supportTools(Tools.loadOrders(Path.of("..", "shared", "orders.json")));
        var tools = Arrays.asList(args).contains("--read-only") ? all.stream().filter(t -> !t.sideEffects()).toList() : all;
        System.err.println("support-tools MCP server: " + String.join(", ", tools.stream().map(Tool::name).toList())); // logs: stderr only
        var in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        for (String line; (line = in.readLine()) != null; ) { // null: stdin closed, so exit
            if (line.isBlank()) continue;
            ObjectNode reply;
            try {
                reply = handle(Tools.JSON.readTree(line), tools);
            } catch (tools.jackson.core.JacksonException e) {
                reply = Tools.JSON.createObjectNode().put("jsonrpc", "2.0");
                reply.putObject("error").put("code", -32700).put("message", "Parse error");
            }
            if (reply != null) {
                System.out.println(Tools.JSON.writeValueAsString(reply));
                System.out.flush();
            }
        }
    }
}
