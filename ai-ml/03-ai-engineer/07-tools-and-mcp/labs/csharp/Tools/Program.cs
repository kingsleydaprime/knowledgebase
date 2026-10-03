// Checks: the same results as every other language. `dotnet Tools.dll serve` runs the MCP server instead.
using System.Text.Json.Nodes;

if (args.FirstOrDefault() == "serve")
{
    await Server.Run(args[1..]);
    return;
}

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

const string Orders = "../shared/orders.json";
static ToolCall Call(string name, string args, string id = "c1") => new(id, name, args);
static bool No(string name, JsonObject args) => false;

// A pretend model that plays back a script of turns and records what it was sent.
static Func<IReadOnlyList<Message>, IReadOnlyList<JsonObject>, Turn> Scripted(Queue<Turn> turns, List<IReadOnlyList<Message>> seen) =>
    (history, _) =>
    {
        seen.Add(history);
        return turns.Dequeue();
    };

var tools = Tools.SupportTools(Tools.LoadOrders(Orders));
Check(string.Join(",", tools[0].Spec().Select(p => p.Key)) == "name,description,inputSchema", "the model sees specs, never functions");

var problems = Tools.Validate(tools[2].InputSchema, JsonNode.Parse("""{"order_id":"a-1","amount":0,"note":"hi"}"""));
Console.WriteLine("validation: " + string.Join(" | ", problems));
Check(problems.Count == 3, problems.Count); // JsonSchema.Net's own wording, every problem found

var ok = Tools.Execute(Call("get_order", """{"order_id":"B456"}"""), tools, No);
Check(ok.Content == """{"status":"shipped","total":120.00,"tracking":"LG-88213"}""", ok.Content); // the number exactly as the file wrote it
string Content(ToolCall c) => Tools.Execute(c, tools, No).Content;
Check(Content(Call("delete_order", "{}")) == "unknown tool \"delete_order\"; available: get_order, get_refund, issue_refund", "unknown");
Check(Content(Call("get_order", "{order_id: A123")) == "arguments are not valid JSON", "bad JSON");
Check(Content(Call("get_order", """{"order_id":"Z999"}""")) == "get_order failed: no order Z999", "no order");
Check(Content(Call("issue_refund", """{"order_id":"B456","amount":120}""")) == "the user declined this action", "declined");

// a side effect: valid arguments, then approval, then the tool's own rules
var orders = Tools.LoadOrders(Orders);
var fresh = Tools.SupportTools(orders);
var asked = new List<string>();
bool Yes(string name, JsonObject args) { asked.Add($"{name} {args.ToJsonString()}"); return true; }
Check(Tools.Execute(Call("issue_refund", """{"order_id":"B456","amount":-5}"""), fresh, Yes).IsError && asked.Count == 0, "malformed");
Check(!Tools.Execute(Call("issue_refund", """{"order_id":"B456","amount":120}"""), fresh, Yes).IsError, "approved");
Check(asked.SequenceEqual(["""issue_refund {"order_id":"B456","amount":120}"""]), string.Join(" ", asked));
Check(Tools.Execute(Call("issue_refund", """{"order_id":"B456","amount":120}"""), fresh, Yes).Content == "issue_refund failed: order B456 already has a refund", "twice");

// the round trip
var seen = new List<IReadOnlyList<Message>>();
var model = Scripted(new([
    new("", [Call("get_order", """{"order_id":"A123"}""", "c1"), Call("get_refund", """{"order_id":"A123"}""", "c2")]),
    new("Your refund of 49.99 is being processed.", []),
]), seen);
var (answer, history, rounds) = Tools.AnswerWithTools(model, [new("user", "Where is my refund for A123?")], tools, No);
Check(rounds == 2 && history.Count == 5, (rounds, history.Count));
Check(seen[1][2].Content == """{"status":"delivered","total":49.99}""", seen[1][2].Content);
Check(seen[1][3].Content == """{"status":"processing","amount":49.99,"requested":"2026-09-28"}""", seen[1][3].Content);

// text in a tool result can't approve anything
var injected = Tools.LoadOrders(Orders);
var seen2 = new List<IReadOnlyList<Message>>();
var fooled = Scripted(new([
    new("", [Call("get_order", """{"order_id":"D012"}""")]),
    new("", [Call("issue_refund", """{"order_id":"D012","amount":500}""", "c2")]),
    new("I can't issue that refund.", []),
]), seen2);
Tools.AnswerWithTools(fooled, [new("user", "Check D012")], Tools.SupportTools(injected), No);
Check(seen2[1][^1].Content.Contains("IGNORE ALL PREVIOUS INSTRUCTIONS"), "the injection reached the model");
Check(seen2[2][^1].Content == "ERROR: the user declined this action" && injected["D012"]!["refund"] is null, "declined");
var approved = Tools.Execute(Call("issue_refund", """{"order_id":"D012","amount":500}""", "c3"), Tools.SupportTools(injected), (_, _) => true);
Check(approved.Content == "issue_refund failed: refund 500 is more than the order total 30", approved.Content);

// a model that never stops is cut off
try
{
    Tools.AnswerWithTools((_, _) => new("", [Call("get_order", """{"order_id":"A123"}""")]), [new("user", "?")], tools, No, maxRounds: 3);
    Check(false, "should have stopped");
}
catch (InvalidOperationException e)
{
    Check(e.Message == "no answer after 3 rounds of tool calls", e.Message);
}

Console.WriteLine("all tools checks passed");
