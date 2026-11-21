package support;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import support.Tools.Message;
import support.Tools.ToolCall;
import support.Tools.Turn;
import tools.jackson.databind.JsonNode;

/** Checks, run with `java -ea`. The same results as every other language. */
public final class ToolsCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static final Path ORDERS = Path.of("..", "shared", "orders.json");

    static ToolCall call(String name, String args, String id) {
        return new ToolCall(id, name, args);
    }

    /** A pretend model that plays back a script of turns and records what it was sent. */
    static Tools.Model scripted(List<Turn> turns, List<List<Message>> seen) {
        var script = new ArrayList<>(turns);
        return (history, tools) -> {
            seen.add(history);
            return script.removeFirst();
        };
    }

    public static void main(String[] args) throws Exception {
        var tools = Tools.supportTools(Tools.loadOrders(ORDERS));
        check(tools.stream().map(t -> t.spec().propertyNames().stream().toList()).toList().getFirst()
                .equals(List.of("name", "description", "inputSchema")), "the model sees specs, never functions");

        var problems = Tools.validate(tools.get(2).inputSchema(), Tools.JSON.readTree("{\"order_id\":\"a-1\",\"amount\":0,\"note\":\"hi\"}"));
        check(problems.size() == 3, problems); // networknt's own wording, every problem found
        System.out.println("validation: " + String.join(" | ", problems));

        var ok = Tools.execute(call("get_order", "{\"order_id\":\"B456\"}", "c1"), tools, (n, a) -> false);
        check(ok.content().equals("{\"status\":\"shipped\",\"total\":120.0,\"tracking\":\"LG-88213\"}"), ok); // 120.0, like Python
        java.util.function.Function<ToolCall, String> content = c -> Tools.execute(c, tools, (n, a) -> false).content();
        check(content.apply(call("delete_order", "{}", "c1")).equals("unknown tool \"delete_order\"; available: get_order, get_refund, issue_refund"), "unknown");
        check(content.apply(call("get_order", "{order_id: A123", "c1")).equals("arguments are not valid JSON"), "bad JSON");
        check(content.apply(call("get_order", "{\"order_id\":\"Z999\"}", "c1")).equals("get_order failed: no order Z999"), "no order");
        check(content.apply(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1")).equals("the user declined this action"), "declined");

        // a side effect: valid arguments, then approval, then the tool's own rules
        var orders = Tools.loadOrders(ORDERS);
        var fresh = Tools.supportTools(orders);
        var asked = new ArrayList<String>();
        java.util.function.BiPredicate<String, JsonNode> yes = (n, a) -> asked.add(n + " " + a);
        check(Tools.execute(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":-5}", "c1"), fresh, yes).isError() && asked.isEmpty(), "malformed");
        check(!Tools.execute(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1"), fresh, yes).isError(), "approved");
        check(asked.equals(List.of("issue_refund {\"order_id\":\"B456\",\"amount\":120}")), asked);
        check(Tools.execute(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1"), fresh, yes).content()
                .equals("issue_refund failed: order B456 already has a refund"), "twice");

        // the round trip
        var seen = new ArrayList<List<Message>>();
        var model = scripted(List.of(
                new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1"), call("get_refund", "{\"order_id\":\"A123\"}", "c2"))),
                new Turn("Your refund of 49.99 is being processed.", List.of())), seen);
        var answer = Tools.answerWithTools(model, List.of(new Message("user", "Where is my refund for A123?", null, List.of())), tools, (n, a) -> false, 5);
        check(answer.rounds() == 2 && answer.history().size() == 5, answer);
        check(seen.get(1).get(2).content().equals("{\"status\":\"delivered\",\"total\":49.99}"), seen.get(1).get(2));
        check(seen.get(1).get(3).content().equals("{\"status\":\"processing\",\"amount\":49.99,\"requested\":\"2026-09-28\"}"), seen.get(1).get(3));

        // text in a tool result can't approve anything
        var injected = Tools.loadOrders(ORDERS);
        var seen2 = new ArrayList<List<Message>>();
        var fooled = scripted(List.of(
                new Turn("", List.of(call("get_order", "{\"order_id\":\"D012\"}", "c1"))),
                new Turn("", List.of(call("issue_refund", "{\"order_id\":\"D012\",\"amount\":500}", "c2"))),
                new Turn("I can't issue that refund.", List.of())), seen2);
        Tools.answerWithTools(fooled, List.of(new Message("user", "Check D012", null, List.of())), Tools.supportTools(injected), (n, a) -> false, 5);
        check(seen2.get(1).getLast().content().contains("IGNORE ALL PREVIOUS INSTRUCTIONS"), "the injection reached the model");
        check(seen2.get(2).getLast().content().equals("ERROR: the user declined this action") && injected.get("D012").get("refund").isNull(), "declined");
        check(Tools.execute(call("issue_refund", "{\"order_id\":\"D012\",\"amount\":500}", "c3"), Tools.supportTools(injected), (n, a) -> true).content()
                .equals("issue_refund failed: refund 500 is more than the order total 30"), "the tool's own rule");

        // a model that never stops is cut off
        Tools.Model forever = (h, t) -> new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1")));
        try {
            Tools.answerWithTools(forever, List.of(new Message("user", "?", null, List.of())), tools, (n, a) -> false, 3);
            check(false, "should have stopped");
        } catch (IllegalStateException e) {
            check(e.getMessage().equals("no answer after 3 rounds of tool calls"), e.getMessage());
        }
        System.out.println("all tools checks passed");
    }
}
