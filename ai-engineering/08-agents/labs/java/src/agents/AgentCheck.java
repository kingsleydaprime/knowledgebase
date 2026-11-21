package agents;

import agents.Agent.Expect;
import agents.Agent.Limits;
import agents.Agent.Outcome;
import agents.Agent.Turn;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.regex.Pattern;
import support.Tools;
import support.Tools.Message;
import support.Tools.Tool;
import support.Tools.ToolCall;

/** Checks, run with `java -ea`. The same scenarios and results as every other language. */
public final class AgentCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static List<Tool> load() throws Exception {
        return Tools.supportTools(Tools.loadOrders(Path.of("..", "..", "..", "07-tools-and-mcp", "labs", "shared", "orders.json")));
    }

    static ToolCall call(String name, String args, String id) {
        return new ToolCall(id, name, args);
    }

    static Agent.Model scripted(Turn... turns) {
        var queue = new ArrayDeque<>(List.of(turns));
        return history -> queue.removeFirst();
    }

    static List<List<String>> names(Outcome o) {
        return o.trace().stream().map(s -> s.calls().stream().map(Agent.StepCall::name).toList()).toList();
    }

    static final List<Message> ASK = List.of(new Message("user", "Where is my refund for A123?", null, List.of()));
    static final Expect NOTHING = new Expect(null, List.of(), List.of(), 0, null);

    public static void main(String[] args) throws Exception {
        // a two-step answer, with a trace
        var o = Agent.runAgent(scripted(
                new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1"), call("get_refund", "{\"order_id\":\"A123\"}", "c2")), 0),
                new Turn("Your refund of 49.99 is being processed.", List.of(), 0)), ASK, load(), Limits.DEFAULT, (n, a) -> false);
        check(o.status().equals("answered") && names(o).equals(List.of(List.of("get_order", "get_refund"), List.of())), names(o));
        check(Agent.scoreTrajectory(o, new Expect("answered", List.of("get_refund"), List.of("issue_refund"), 3, null)).isEmpty(), "trajectory");

        // reads run together on virtual threads; a side effect waits
        var log = Collections.synchronizedList(new ArrayList<String>());
        java.util.function.BiFunction<String, Long, Tools.Run> slow = (name, ms) -> a -> {
            log.add("start " + name);
            try {
                Thread.sleep(ms);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            log.add("end " + name);
            return name;
        };
        var any = Tools.JSON.readTree("{\"type\":\"object\"}");
        var slowTools = List.of(new Tool("read_a", "", any, false, slow.apply("read_a", 30L)),
                new Tool("read_b", "", any, false, slow.apply("read_b", 10L)), new Tool("write_c", "", any, true, slow.apply("write_c", 1L)));
        var p = Agent.runAgent(scripted(new Turn("", List.of(call("write_c", "{}", "1"), call("read_a", "{}", "2"), call("read_b", "{}", "3")), 0),
                new Turn("done", List.of(), 0)), List.of(), slowTools, Limits.DEFAULT, (n, a) -> true);
        check(log.stream().filter(s -> s.startsWith("end")).toList().equals(List.of("end read_b", "end read_a", "end write_c"))
                && log.get(4).equals("start write_c"), log);
        check(p.messages().stream().filter(m -> m.role().equals("tool")).map(Message::toolCallId).toList().equals(List.of("1", "2", "3")), "order");

        // a step limit stops a wandering agent
        int[] n = {100};
        var wandering = Agent.runAgent(h -> new Turn("", List.of(call("get_order", "{\"order_id\":\"A" + ++n[0] + "\"}", "c" + n[0])), 0),
                ASK, load(), new Limits(3, 1_000_000_000, 5), (x, a) -> false);
        check(wandering.status().equals("step_limit") && wandering.trace().size() == 3, wandering.status());
        check(Agent.scoreTrajectory(wandering, new Expect("answered", List.of(), List.of(), 0, null)).equals(List.of("ended step_limit, expected answered")), "scored");

        // the same call again and again is stuck
        var stuck = Agent.runAgent(h -> new Turn("", List.of(call("get_refund", "{\"order_id\":\"Z999\"}", "x")), 0),
                ASK, load(), new Limits(20, 1_000_000_000, 2), (x, a) -> false);
        check(stuck.status().equals("stuck") && stuck.trace().size() == 3, stuck.status());

        // a token budget
        var budget = Agent.runAgent(scripted(new Turn("", List.of(call("get_order", "{\"order_id\":\"A123\"}", "c1")), 25_500),
                new Turn("", List.of(call("get_order", "{\"order_id\":\"B456\"}", "c2")), 25_500), new Turn("never reached", List.of(), 25_500)),
                ASK, load(), new Limits(10, 50_000, 2), (x, a) -> false);
        check(budget.status().equals("token_limit") && budget.trace().stream().map(Agent.Step::tokens).toList().equals(List.of(25_500, 25_500)), budget);

        // the scorer names each broken expectation
        var refunded = Agent.runAgent(scripted(new Turn("", List.of(call("issue_refund", "{\"order_id\":\"B456\",\"amount\":120}", "c1")), 0),
                new Turn("I've asked for a refund.", List.of(), 0)), ASK, load(), Limits.DEFAULT, (x, a) -> false);
        var failures = Agent.scoreTrajectory(refunded, new Expect(null, List.of("get_refund"), List.of("issue_refund"), 0, Pattern.compile("(?i)no refund")));
        check(failures.equals(List.of("never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund")), failures);

        // the workflow
        var tools = load();
        var prompts = new ArrayList<String>();
        java.util.function.UnaryOperator<String> write = prompt -> {
            prompts.add(prompt);
            return "Your refund of 49.99 for A123 is being processed.";
        };
        var answered = Agent.refundStatus("Where is my refund for order a123?", tools, write);
        check(answered.kind().equals("answer") && answered.modelCalls() == 1, answered);
        check(prompts.getFirst().contains("Refund: {\"status\":\"processing\",\"amount\":49.99,\"requested\":\"2026-09-28\"}"), prompts.getFirst());
        check(Agent.refundStatus("Has my refund come through?", tools, write).kind().equals("ask"), "ask");
        // "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
        check(Agent.refundStatus("Can you change my delivery address?", tools, write).text().equals("classified as feature"), "handoff");
        Agent.refundStatus("Where is my refund for D012?", tools, write);
        check(!prompts.getLast().contains("IGNORE") && prompts.size() == 2, prompts);

        System.out.println("all agent checks passed");
    }
}
