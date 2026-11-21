package agents;

import evals.Evals;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.BiPredicate;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import support.Tools;
import support.Tools.Message;
import support.Tools.Tool;
import support.Tools.ToolCall;
import support.Tools.ToolResult;
import tools.jackson.databind.JsonNode;

/** The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
 *  Imports the tools lab (support.Tools) and the evals lab (Evals.keywords). */
public final class Agent {
    private Agent() {}

    public record Limits(int maxSteps, int maxTokens, int maxRepeats) {
        public static final Limits DEFAULT = new Limits(8, 50_000, 2);
    }

    public record StepCall(String name, String arguments, boolean isError) {}

    public record Step(int step, int tokens, List<StepCall> calls) {}

    /** status: answered, step_limit, token_limit or stuck. */
    public record Outcome(String status, String answer, List<Step> trace, List<Message> messages) {}

    /** One model turn: text, the calls it asks for, and the tokens it used. */
    public record Turn(String content, List<ToolCall> calls, int tokens) {}

    public interface Model {
        Turn respond(List<Message> history);
    }

    public static Outcome runAgent(Model model, List<Message> messages, List<Tool> tools, Limits limits,
                                   BiPredicate<String, JsonNode> approve) throws Exception {
        var history = new ArrayList<>(messages);
        var trace = new ArrayList<Step>();
        var seen = new HashMap<String, Integer>();
        int total = 0;
        Set<String> sideEffects = tools.stream().filter(Tool::sideEffects).map(Tool::name).collect(Collectors.toSet());
        for (int step = 1; step <= limits.maxSteps(); step++) {
            Turn turn = model.respond(List.copyOf(history));
            total += turn.tokens();
            history.add(new Message("assistant", turn.content(), null, turn.calls()));
            var record = new Step(step, turn.tokens(), new ArrayList<>());
            trace.add(record);
            if (turn.calls().isEmpty()) return new Outcome("answered", turn.content(), trace, history);

            for (ToolCall c : turn.calls()) { // the same call, again and again, is going round in circles
                if (seen.merge(c.name() + " " + c.arguments(), 1, Integer::sum) > limits.maxRepeats()) {
                    return new Outcome("stuck", null, trace, history);
                }
            }

            // Read-only calls each get a virtual thread; side effects run alone, in order, after them.
            Map<String, ToolResult> results = new HashMap<>();
            try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                var reads = new HashMap<String, Future<ToolResult>>();
                for (ToolCall c : turn.calls()) {
                    if (!sideEffects.contains(c.name())) reads.put(c.id(), executor.submit(() -> Tools.execute(c, tools, approve)));
                }
                for (var e : reads.entrySet()) results.put(e.getKey(), e.getValue().get());
            }
            for (ToolCall c : turn.calls()) {
                if (sideEffects.contains(c.name())) results.put(c.id(), Tools.execute(c, tools, approve));
            }

            for (ToolCall c : turn.calls()) { // results in the order of the calls, whatever order they finished in
                ToolResult r = results.get(c.id());
                history.add(new Message("tool", r.isError() ? "ERROR: " + r.content() : r.content(), c.id(), List.of()));
                record.calls().add(new StepCall(c.name(), c.arguments(), r.isError()));
            }
            if (total > limits.maxTokens()) return new Outcome("token_limit", null, trace, history);
        }
        return new Outcome("step_limit", null, trace, history);
    }

    /** kind: answer, ask or handoff. */
    public record WorkflowResult(String kind, String text, int modelCalls) {}

    private static final Pattern ORDER_ID = Pattern.compile("\\b([A-Za-z])(\\d{3})\\b");

    /** The same question as fixed steps: route, extract, look up, then one model call with no tools. */
    public static WorkflowResult refundStatus(String question, List<Tool> tools, java.util.function.UnaryOperator<String> write) {
        String label = Evals.keywords(question);
        if (!label.equals("billing")) return new WorkflowResult("handoff", "classified as " + label, 0);
        var m = ORDER_ID.matcher(question);
        if (!m.find()) return new WorkflowResult("ask", "Could you tell me your order number? It looks like A123.", 0);
        String id = m.group(1).toUpperCase() + m.group(2);
        ToolResult refund = Tools.execute(new ToolCall("w1", "get_refund", "{\"order_id\":\"" + id + "\"}"), tools, (n, a) -> false);
        if (refund.isError()) return new WorkflowResult("ask", "I couldn't find order " + id + ". Could you check the number?", 0);
        String text = write.apply("Write a one-sentence reply to a customer about their refund, using only these facts.\n"
                + "Order: " + id + "\nRefund: " + refund.content() + "\nTheir question: " + question);
        return new WorkflowResult("answer", text, 1);
    }

    public record Expect(String status, List<String> mustCall, List<String> mustNotCall, int maxSteps, Pattern answerMatches) {}

    public static List<String> scoreTrajectory(Outcome o, Expect e) {
        var called = o.trace().stream().flatMap(s -> s.calls().stream().map(StepCall::name)).toList();
        var failures = new ArrayList<String>();
        if (e.status() != null && !o.status().equals(e.status())) failures.add("ended " + o.status() + ", expected " + e.status());
        for (String n : e.mustCall()) if (!called.contains(n)) failures.add("never called " + n);
        for (String n : e.mustNotCall()) if (called.contains(n)) failures.add("called " + n);
        if (e.maxSteps() > 0 && o.trace().size() > e.maxSteps()) failures.add("took " + o.trace().size() + " steps, expected at most " + e.maxSteps());
        if (e.answerMatches() != null && !e.answerMatches().matcher(o.answer() == null ? "" : o.answer()).find()) {
            failures.add("answer doesn't match " + e.answerMatches().pattern());
        }
        return failures;
    }
}
