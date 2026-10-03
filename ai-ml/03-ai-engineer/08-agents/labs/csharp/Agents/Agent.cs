// The agent loop with its controls, the same question as a workflow, and a trajectory scorer.
// Links the tools lab's Tools.cs (the store, the tools and Execute) and the evals lab's Evals.cs (the keyword router).
using System.Collections.Concurrent;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

public sealed record Limits(int MaxSteps = 8, int MaxTokens = 50_000, int MaxRepeats = 2);
public sealed record StepCall(string Name, string Arguments, bool IsError);
public sealed record Step(int Number, int Tokens, List<StepCall> Calls);
public enum Status { Answered, StepLimit, TokenLimit, Stuck }
public sealed record Outcome(Status Status, string? Answer, List<Step> Trace, List<Message> Messages);

/// <summary>One model turn: text, the calls it asks for, and the tokens it used.</summary>
public sealed record AgentTurn(string Content, IReadOnlyList<ToolCall> Calls, int Tokens = 0);

public abstract record WorkflowResult
{
    public sealed record Answer(string Text, int ModelCalls) : WorkflowResult;
    public sealed record Ask(string Text) : WorkflowResult;
    public sealed record Handoff(string Reason) : WorkflowResult;
}

public sealed record Expect(Status? Status = null, string[]? MustCall = null, string[]? MustNotCall = null, int? MaxSteps = null, Regex? AnswerMatches = null);

public static partial class Agent
{
    public static async Task<Outcome> Run(Func<IReadOnlyList<Message>, AgentTurn> model, IEnumerable<Message> messages,
        IReadOnlyList<Tool> tools, Limits limits, Func<string, JsonObject, bool> approve)
    {
        var history = messages.ToList();
        var trace = new List<Step>();
        var seen = new Dictionary<string, int>();
        var total = 0;
        var sideEffects = tools.Where(t => t.SideEffects).Select(t => t.Name).ToHashSet();
        for (var step = 1; step <= limits.MaxSteps; step++)
        {
            var turn = model([.. history]);
            total += turn.Tokens;
            history.Add(new("assistant", turn.Content, Calls: turn.Calls));
            var record = new Step(step, turn.Tokens, []);
            trace.Add(record);
            if (turn.Calls.Count == 0) return new(Status.Answered, turn.Content, trace, history);

            foreach (var c in turn.Calls) // the same call, again and again, is going round in circles
            {
                var key = $"{c.Name} {c.Arguments}";
                seen[key] = seen.GetValueOrDefault(key) + 1;
                if (seen[key] > limits.MaxRepeats) return new(Status.Stuck, null, trace, history);
            }

            // Read-only calls on the thread pool at the same time; side effects alone, in order, after them.
            var results = new ConcurrentDictionary<string, ToolResult>();
            await Task.WhenAll(turn.Calls.Where(c => !sideEffects.Contains(c.Name))
                .Select(c => Task.Run(() => results[c.Id] = Tools.Execute(c, tools, approve))));
            foreach (var c in turn.Calls.Where(c => sideEffects.Contains(c.Name))) results[c.Id] = Tools.Execute(c, tools, approve);

            foreach (var c in turn.Calls) // results in the order of the calls, whatever order they finished in
            {
                var r = results[c.Id];
                history.Add(new("tool", r.IsError ? $"ERROR: {r.Content}" : r.Content, c.Id));
                record.Calls.Add(new(c.Name, c.Arguments, r.IsError));
            }
            if (total > limits.MaxTokens) return new(Status.TokenLimit, null, trace, history);
        }
        return new(Status.StepLimit, null, trace, history);
    }

    [GeneratedRegex(@"\b([A-Za-z])(\d{3})\b")] private static partial Regex OrderId();

    /// <summary>The same question as fixed steps: route, extract, look up, then one model call with no tools.</summary>
    public static WorkflowResult RefundStatus(string question, IReadOnlyList<Tool> tools, Func<string, string> write)
    {
        var label = Evals.Keywords(question);
        if (label != "billing") return new WorkflowResult.Handoff($"classified as {label}");
        var m = OrderId().Match(question);
        if (!m.Success) return new WorkflowResult.Ask("Could you tell me your order number? It looks like A123.");
        var id = m.Groups[1].Value.ToUpperInvariant() + m.Groups[2].Value;
        var refund = Tools.Execute(new("w1", "get_refund", new JsonObject { ["order_id"] = id }.ToJsonString()), tools, (_, _) => false);
        if (refund.IsError) return new WorkflowResult.Ask($"I couldn't find order {id}. Could you check the number?");
        var text = write("Write a one-sentence reply to a customer about their refund, using only these facts.\n" +
            $"Order: {id}\nRefund: {refund.Content}\nTheir question: {question}");
        return new WorkflowResult.Answer(text, 1);
    }

    public static List<string> ScoreTrajectory(Outcome o, Expect e)
    {
        var called = o.Trace.SelectMany(s => s.Calls.Select(c => c.Name)).ToList();
        var failures = new List<string>();
        if (e.Status is { } status && o.Status != status) failures.Add($"ended {o.Status}, expected {status}");
        failures.AddRange((e.MustCall ?? []).Where(n => !called.Contains(n)).Select(n => $"never called {n}"));
        failures.AddRange((e.MustNotCall ?? []).Where(called.Contains).Select(n => $"called {n}"));
        if (e.MaxSteps is { } max && o.Trace.Count > max) failures.Add($"took {o.Trace.Count} steps, expected at most {max}");
        if (e.AnswerMatches is { } re && !re.IsMatch(o.Answer ?? "")) failures.Add($"answer doesn't match {re}");
        return failures;
    }
}
