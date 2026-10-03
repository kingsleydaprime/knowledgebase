// Checks: the same scenarios and results as every other language.
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static List<Tool> Load() => Tools.SupportTools(Tools.LoadOrders("../../../07-tools-and-mcp/labs/shared/orders.json"));
static ToolCall Call(string name, string args, string id) => new(id, name, args);
static bool No(string name, JsonObject args) => false;
static Func<IReadOnlyList<Message>, AgentTurn> Scripted(params AgentTurn[] turns)
{
    var queue = new Queue<AgentTurn>(turns);
    return _ => queue.Dequeue();
}
static string Names(Outcome o) => string.Join(" | ", o.Trace.Select(s => string.Join(",", s.Calls.Select(c => c.Name))));
Message[] ask = [new("user", "Where is my refund for A123?")];

// a two-step answer, with a trace
var o = await Agent.Run(Scripted(
    new("", [Call("get_order", """{"order_id":"A123"}""", "c1"), Call("get_refund", """{"order_id":"A123"}""", "c2")]),
    new("Your refund of 49.99 is being processed.", [])), ask, Load(), new(), No);
Check(o.Status == Status.Answered && Names(o) == "get_order,get_refund | ", Names(o));
Check(Agent.ScoreTrajectory(o, new(Status.Answered, ["get_refund"], ["issue_refund"], 3)).Count == 0, "trajectory");

// reads run together on the thread pool; a side effect waits
var log = new List<string>();
var gate = new Lock();
Run Slow(string name, int ms) => _ =>
{
    lock (gate) log.Add($"start {name}");
    Thread.Sleep(ms);
    lock (gate) log.Add($"end {name}");
    return name;
};
var any = new JsonObject { ["type"] = "object" };
List<Tool> slow = [new("read_a", "", any, false, Slow("read_a", 30)), new("read_b", "", any.DeepClone().AsObject(), false, Slow("read_b", 10)),
    new("write_c", "", any.DeepClone().AsObject(), true, Slow("write_c", 1))];
var p = await Agent.Run(Scripted(new("", [Call("write_c", "{}", "1"), Call("read_a", "{}", "2"), Call("read_b", "{}", "3")]), new("done", [])),
    [], slow, new(), (_, _) => true);
Check(log.Where(s => s.StartsWith("end")).SequenceEqual(["end read_b", "end read_a", "end write_c"]) && log[4] == "start write_c", string.Join(", ", log));
Check(p.Messages.Where(m => m.Role == "tool").Select(m => m.ToolCallId).SequenceEqual(["1", "2", "3"]), "results in call order");

// a step limit stops a wandering agent
var n = 100;
var wandering = await Agent.Run(_ => { n++; return new("", [Call("get_order", $$"""{"order_id":"A{{n}}"}""", $"c{n}")]); },
    ask, Load(), new(MaxSteps: 3, MaxTokens: int.MaxValue, MaxRepeats: 5), No);
Check(wandering.Status == Status.StepLimit && wandering.Trace.Count == 3, wandering.Status);
Check(Agent.ScoreTrajectory(wandering, new(Status.Answered)).SequenceEqual(["ended StepLimit, expected Answered"]), "scored");

// the same call again and again is stuck
var stuck = await Agent.Run(_ => new("", [Call("get_refund", """{"order_id":"Z999"}""", "x")]), ask, Load(), new(MaxSteps: 20, MaxTokens: int.MaxValue), No);
Check(stuck.Status == Status.Stuck && stuck.Trace.Count == 3, stuck.Status);

// a token budget
var budget = await Agent.Run(Scripted(new("", [Call("get_order", """{"order_id":"A123"}""", "c1")], 25_500),
    new("", [Call("get_order", """{"order_id":"B456"}""", "c2")], 25_500), new("never reached", [], 25_500)), ask, Load(), new(MaxSteps: 10), No);
Check(budget.Status == Status.TokenLimit && budget.Trace.Select(s => s.Tokens).SequenceEqual([25_500, 25_500]), budget.Status);

// the scorer names each broken expectation
var refunded = await Agent.Run(Scripted(new("", [Call("issue_refund", """{"order_id":"B456","amount":120}""", "c1")]), new("I've asked for a refund.", [])),
    ask, Load(), new(), No);
var failures = Agent.ScoreTrajectory(refunded, new(MustCall: ["get_refund"], MustNotCall: ["issue_refund"], AnswerMatches: new Regex("(?i)no refund")));
Check(failures.SequenceEqual(["never called get_refund", "called issue_refund", "answer doesn't match (?i)no refund"]), string.Join(" | ", failures));

// the workflow
var tools = Load();
var prompts = new List<string>();
string Write(string prompt) { prompts.Add(prompt); return "Your refund of 49.99 for A123 is being processed."; }
Check(Agent.RefundStatus("Where is my refund for order a123?", tools, Write) == new WorkflowResult.Answer("Your refund of 49.99 for A123 is being processed.", 1), "answer");
Check(prompts[0].Contains("""Refund: {"status":"processing","amount":49.99,"requested":"2026-09-28"}"""), prompts[0]);
Check(Agent.RefundStatus("Has my refund come through?", tools, Write) is WorkflowResult.Ask, "ask");
// "address" contains "add": the keyword rules' known flaw, harmless when every other branch goes to a person
Check(Agent.RefundStatus("Can you change my delivery address?", tools, Write) == new WorkflowResult.Handoff("classified as feature"), "handoff");
Agent.RefundStatus("Where is my refund for D012?", tools, Write);
Check(!prompts[^1].Contains("IGNORE") && prompts.Count == 2, string.Join("\n", prompts));

Console.WriteLine("all agent checks passed");
