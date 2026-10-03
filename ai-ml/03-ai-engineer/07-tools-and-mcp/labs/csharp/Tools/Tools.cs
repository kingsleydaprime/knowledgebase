// Tools for a support assistant: the same checks, round trip and results as the TypeScript lab.
// JSON is System.Text.Json's mutable JsonNode; arguments are checked with JsonSchema.Net.
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Nodes;
using Json.Schema;

public delegate JsonNode? Run(JsonObject args);

public sealed record Tool(string Name, string Description, JsonObject InputSchema, bool SideEffects, Run Run)
{
    // What the model sees: never Run or SideEffects.
    public JsonObject Spec() => new() { ["name"] = Name, ["description"] = Description, ["inputSchema"] = InputSchema.DeepClone() };
}

public sealed record ToolCall(string Id, string Name, string Arguments);
public sealed record ToolResult(string Id, string Content, bool IsError);

/// <summary>What can go wrong inside a tool, in words the model can act on.</summary>
public sealed class ToolFailure(string message) : Exception(message);

public sealed record Message(string Role, string Content, string? ToolCallId = null, IReadOnlyList<ToolCall>? Calls = null);
public sealed record Turn(string Content, IReadOnlyList<ToolCall> Calls);

public static class Tools
{
    public static List<string> Validate(JsonObject schema, JsonNode? value)
    {
        var results = JsonSchema.FromText(schema.ToJsonString())
            .Evaluate(JsonSerializer.SerializeToElement(value), new EvaluationOptions { OutputFormat = OutputFormat.List });
        return (results.Details ?? [])
            .Where(d => d.Errors is { Count: > 0 })
            // Drop the summaries ("some properties did not match") and the bare false-schema leaf: keep one line per problem.
            .SelectMany(d => d.Errors!.Where(e => e.Key is not ("properties" or "")).Select(e => $"arguments{d.InstanceLocation}: {e.Value}"))
            .ToList();
    }

    public static ToolResult Execute(ToolCall call, IReadOnlyList<Tool> tools, Func<string, JsonObject, bool> approve)
    {
        ToolResult Fail(string content) => new(call.Id, content, true);
        var tool = tools.FirstOrDefault(t => t.Name == call.Name);
        if (tool is null) return Fail($"unknown tool \"{call.Name}\"; available: {string.Join(", ", tools.Select(t => t.Name))}");
        JsonObject? args;
        try
        {
            args = JsonNode.Parse(string.IsNullOrEmpty(call.Arguments) ? "{}" : call.Arguments) as JsonObject;
        }
        catch (JsonException)
        {
            return Fail("arguments are not valid JSON");
        }
        if (args is null) return Fail("arguments are not valid JSON");
        var problems = Validate(tool.InputSchema, args);
        if (problems.Count > 0) return Fail(string.Join("; ", problems));
        if (tool.SideEffects && !approve(tool.Name, args)) return Fail("the user declined this action");
        try
        {
            var content = tool.Run(args)?.ToJsonString() ?? "null";
            return new(call.Id, content.Length > 2000 ? content[..2000] + " …[truncated]" : content, false);
        }
        catch (ToolFailure e) // the message, never a stack trace
        {
            return Fail($"{tool.Name} failed: {e.Message}");
        }
    }

    public static JsonObject LoadOrders(string path) => JsonNode.Parse(File.ReadAllText(path))!.AsObject();

    const string OrderId = """{"type": "string", "pattern": "^[A-Z][0-9]{3}$", "description": "Like A123: one capital letter, three digits"}""";

    public static List<Tool> SupportTools(JsonObject orders)
    {
        var oneId = JsonNode.Parse($$$"""{"type": "object", "properties": {"order_id": {{{OrderId}}}}, "required": ["order_id"], "additionalProperties": false}""")!.AsObject();
        var refundArgs = JsonNode.Parse($$$"""
            {"type": "object", "properties": {"order_id": {{{OrderId}}}, "amount": {"type": "number", "minimum": 0.01}},
             "required": ["order_id", "amount"], "additionalProperties": false}
            """)!.AsObject();
        JsonObject Find(JsonObject args)
        {
            var id = args["order_id"]!.GetValue<string>();
            return orders[id]?.AsObject() ?? throw new ToolFailure($"no order {id}");
        }
        static string Plain(decimal x) => x.ToString("0.##", CultureInfo.InvariantCulture); // 500, 49.99
        return
        [
            new("get_order", "Look up an order's status, total and tracking number. Use it before answering any question about an order.",
                oneId, false, args =>
                {
                    var copy = Find(args).DeepClone().AsObject();
                    copy.Remove("refund"); // the refund has its own tool
                    return copy;
                }),
            new("get_refund", "Look up the refund on an order, if there is one: its status, amount and dates.",
                oneId.DeepClone().AsObject(), false, args => Find(args)["refund"]?.DeepClone() ?? new JsonObject { ["status"] = "none" }),
            new("issue_refund", "Refund money to the customer. Only when the customer asks for a refund and none exists yet.",
                refundArgs, true, args =>
                {
                    var order = Find(args);
                    decimal amount = args["amount"]!.GetValue<decimal>(), total = order["total"]!.GetValue<decimal>();
                    if (order["refund"] is not null) throw new ToolFailure($"order {args["order_id"]} already has a refund");
                    if (amount > total) throw new ToolFailure($"refund {Plain(amount)} is more than the order total {Plain(total)}");
                    order["refund"] = new JsonObject { ["status"] = "processing", ["amount"] = amount, ["requested"] = "today" };
                    return order["refund"]!.DeepClone();
                }),
        ];
    }

    public static (string Answer, List<Message> History, int Rounds) AnswerWithTools(
        Func<IReadOnlyList<Message>, IReadOnlyList<JsonObject>, Turn> model, IEnumerable<Message> messages, IReadOnlyList<Tool> tools,
        Func<string, JsonObject, bool> approve, int maxRounds = 5)
    {
        var history = messages.ToList();
        var specs = tools.Select(t => t.Spec()).ToList();
        for (var round = 1; round <= maxRounds; round++)
        {
            var turn = model([.. history], specs);
            history.Add(new("assistant", turn.Content, Calls: turn.Calls));
            if (turn.Calls.Count == 0) return (turn.Content, history, round);
            foreach (var call in turn.Calls) // one result per call, in the order of the calls
            {
                var r = Execute(call, tools, approve);
                history.Add(new("tool", r.IsError ? $"ERROR: {r.Content}" : r.Content, call.Id));
            }
        }
        throw new InvalidOperationException($"no answer after {maxRounds} rounds of tool calls");
    }
}
