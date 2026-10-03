package support;

import com.networknt.schema.Error;
import com.networknt.schema.SchemaRegistry;
import com.networknt.schema.SpecificationVersion;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BiPredicate;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ObjectNode;

/** Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
 *  JSON is Jackson 3; arguments are checked with networknt's json-schema-validator. */
public final class Tools {
    private Tools() {}

    public static final JsonMapper JSON = JsonMapper.shared();
    private static final SchemaRegistry SCHEMAS = SchemaRegistry.withDefaultDialect(SpecificationVersion.DRAFT_2020_12);

    /** What can go wrong inside a tool, said in words the model can act on. */
    public static final class ToolFailure extends RuntimeException {
        public ToolFailure(String message) { super(message); }
    }

    public interface Run {
        Object apply(JsonNode args);
    }

    public record Tool(String name, String description, JsonNode inputSchema, boolean sideEffects, Run run) {
        public ObjectNode spec() { // what the model sees: never run or sideEffects
            return JSON.createObjectNode().put("name", name).put("description", description).set("inputSchema", inputSchema);
        }
    }

    public record ToolCall(String id, String name, String arguments) {}

    public record ToolResult(String id, String content, boolean isError) {}

    public static List<String> validate(JsonNode schema, JsonNode value) {
        return SCHEMAS.getSchema(schema.toString()).validate(value).stream().map(Error::toString).toList();
    }

    public static ToolResult execute(ToolCall call, List<Tool> tools, BiPredicate<String, JsonNode> approve) {
        Tool tool = tools.stream().filter(t -> t.name().equals(call.name())).findFirst().orElse(null);
        if (tool == null) {
            var names = String.join(", ", tools.stream().map(Tool::name).toList());
            return fail(call, "unknown tool \"" + call.name() + "\"; available: " + names);
        }
        JsonNode args;
        try {
            args = JSON.readTree(call.arguments() == null || call.arguments().isEmpty() ? "{}" : call.arguments());
        } catch (JacksonException e) {
            return fail(call, "arguments are not valid JSON");
        }
        var problems = validate(tool.inputSchema(), args);
        if (!problems.isEmpty()) return fail(call, String.join("; ", problems));
        if (tool.sideEffects() && !approve.test(tool.name(), args)) return fail(call, "the user declined this action");
        try {
            String content = JSON.writeValueAsString(tool.run().apply(args));
            return new ToolResult(call.id(), content.length() > 2000 ? content.substring(0, 2000) + " …[truncated]" : content, false);
        } catch (ToolFailure e) { // the message, never a stack trace
            return fail(call, tool.name() + " failed: " + e.getMessage());
        }
    }

    private static ToolResult fail(ToolCall call, String content) {
        return new ToolResult(call.id(), content, true);
    }

    public static ObjectNode loadOrders(Path path) throws Exception {
        return (ObjectNode) JSON.readTree(Files.readString(path));
    }

    private static final String ORDER_ID = """
            {"type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits"}""";

    public static List<Tool> supportTools(ObjectNode orders) {
        JsonNode oneId = JSON.readTree("""
                {"type": "object", "properties": {"order_id": %s}, "required": ["order_id"], "additionalProperties": false}"""
                .formatted(ORDER_ID));
        JsonNode refundArgs = JSON.readTree("""
                {"type": "object", "properties": {"order_id": %s, "amount": {"type": "number", "minimum": 0.01}},
                 "required": ["order_id", "amount"], "additionalProperties": false}""".formatted(ORDER_ID));
        java.util.function.Function<JsonNode, ObjectNode> find = args -> {
            JsonNode order = orders.get(args.get("order_id").asString());
            if (order == null) throw new ToolFailure("no order " + args.get("order_id").asString());
            return (ObjectNode) order;
        };
        return List.of(
                new Tool("get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
                        oneId, false, args -> find.apply(args).deepCopy().without("refund")),
                new Tool("get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
                        oneId, false, args -> {
                            JsonNode refund = find.apply(args).get("refund");
                            return refund.isNull() ? JSON.createObjectNode().put("status", "none") : refund;
                        }),
                new Tool("issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
                        refundArgs, true, args -> {
                            ObjectNode order = find.apply(args);
                            double amount = args.get("amount").asDouble(), total = order.get("total").asDouble();
                            if (!order.get("refund").isNull()) throw new ToolFailure("order " + args.get("order_id").asString() + " already has a refund");
                            if (amount > total) throw new ToolFailure("refund %s is more than the order total %s".formatted(plain(amount), plain(total)));
                            order.set("refund", JSON.createObjectNode().put("status", "processing").put("amount", amount).put("requested", "today"));
                            return order.get("refund");
                        }));
    }

    /** 500.0 as "500", 49.99 as "49.99": what the other languages print. */
    static String plain(double x) {
        return new java.math.BigDecimal(Double.toString(x)).stripTrailingZeros().toPlainString();
    }

    public record Message(String role, String content, String toolCallId, List<ToolCall> toolCalls) {}

    /** One model turn: text, and zero or more calls. No calls means "this is my answer". */
    public record Turn(String content, List<ToolCall> toolCalls) {}

    public interface Model {
        Turn respond(List<Message> history, List<ObjectNode> tools);
    }

    public record Answer(String text, List<Message> history, int rounds) {}

    public static Answer answerWithTools(Model model, List<Message> messages, List<Tool> tools, BiPredicate<String, JsonNode> approve, int maxRounds) {
        var history = new ArrayList<>(messages);
        var specs = tools.stream().map(Tool::spec).toList();
        for (int round = 1; round <= maxRounds; round++) {
            Turn turn = model.respond(List.copyOf(history), specs);
            history.add(new Message("assistant", turn.content(), null, turn.toolCalls()));
            if (turn.toolCalls().isEmpty()) return new Answer(turn.content(), history, round);
            for (ToolCall call : turn.toolCalls()) { // one result per call, in the order of the calls
                ToolResult r = execute(call, tools, approve);
                history.add(new Message("tool", r.isError() ? "ERROR: " + r.content() : r.content(), call.id(), List.of()));
            }
        }
        throw new IllegalStateException("no answer after " + maxRounds + " rounds of tool calls");
    }
}
