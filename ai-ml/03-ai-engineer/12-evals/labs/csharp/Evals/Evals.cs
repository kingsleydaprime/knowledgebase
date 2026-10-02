// An eval harness: the shared golden set, exact-match scoring, error bars, case-by-case comparison,
// a CI gate, baselines, and the checks on an LLM judge.
using System.Text.Json;
using System.Text.RegularExpressions;

public record Case(string Id, string Ticket, string Label, List<string> Tags);

public record CaseResult(string Id, string Expected, string? Got, string Reply, bool Pass);

public record EvalResult(List<CaseResult> Results, Dictionary<string, (int Passed, int Total)> ByTag)
{
    public int Passed => Results.Count(r => r.Pass);
    public double Rate => (double)Passed / Results.Count;
}

public static partial class Evals
{
    static readonly JsonSerializerOptions Json = new() { PropertyNameCaseInsensitive = true };

    public static List<Case> LoadGolden(string path) =>
        [.. File.ReadLines(path).Where(line => line.Trim() != "").Select(line => JsonSerializer.Deserialize<Case>(line, Json)!)];

    [GeneratedRegex(@"\b(bug|billing|feature|other)\b")]
    private static partial Regex Label();

    /// <summary>The one label in the reply, or null if there are none or several.</summary>
    public static string? ParseLabel(string reply)
    {
        var found = Label().Matches(reply.ToLowerInvariant()).Select(m => m.Value).Distinct().ToList();
        return found.Count == 1 ? found[0] : null;
    }

    /// <summary>Where the true pass rate probably lies (95%), given a small sample.</summary>
    public static (double Low, double High) Wilson(int passed, int total)
    {
        if (total == 0) return (0, 1);
        const double z = 1.96;
        double n = total, p = passed / n;
        var centre = p + z * z / (2 * n);
        var spread = z * Math.Sqrt(p * (1 - p) / n + z * z / (4 * n * n));
        return ((centre - spread) / (1 + z * z / n), (centre + spread) / (1 + z * z / n));
    }

    public static EvalResult RunEval(Func<string, string> classify, List<Case> cases)
    {
        var result = new EvalResult([], []);
        foreach (var c in cases)
        {
            var reply = classify(c.Ticket);
            var got = ParseLabel(reply);
            var pass = got == c.Label;
            result.Results.Add(new(c.Id, c.Label, got, reply, pass));
            foreach (var tag in c.Tags)
            {
                var (passed, total) = result.ByTag.GetValueOrDefault(tag);
                result.ByTag[tag] = (passed + (pass ? 1 : 0), total + 1);
            }
        }
        return result;
    }

    /// <summary>What a change fixed, and what it broke.</summary>
    public static (List<string> Fixed, List<string> Broke) Compare(EvalResult before, EvalResult after)
    {
        var was = before.Results.ToDictionary(r => r.Id, r => r.Pass);
        return ([.. after.Results.Where(r => r.Pass && was.GetValueOrDefault(r.Id, true) == false).Select(r => r.Id)],
                [.. after.Results.Where(r => !r.Pass && was.GetValueOrDefault(r.Id, false)).Select(r => r.Id)]);
    }

    /// <summary>The reasons to fail the build; none means the change may merge.</summary>
    public static List<string> Gate(EvalResult result, double minRate, EvalResult? baseline = null, params string[] mustPass)
    {
        var reasons = new List<string>();
        if (result.Rate < minRate) reasons.Add($"pass rate {result.Rate * 100:0}% is below the floor of {minRate * 100:0}%");
        if (baseline is not null && Compare(baseline, result).Broke is { Count: > 0 } broke)
            reasons.Add($"regressed on {string.Join(", ", broke)}");
        reasons.AddRange(mustPass.Where(id => !result.Results.Any(r => r.Id == id && r.Pass)).Select(id => $"must-pass case {id} failed"));
        return reasons;
    }

    /// <summary>Always the most common label.</summary>
    public static Func<string, string> Majority(List<Case> cases)
    {
        var top = cases.CountBy(c => c.Label).MaxBy(pair => pair.Value).Key;
        return _ => top;
    }

    [GeneratedRegex("charg|refund|invoice|pay|price|subscription|discount|receipt")] private static partial Regex Billing();
    [GeneratedRegex("crash|error|broken|bug|blank|empty|doesn't work|not working")] private static partial Regex Bug();
    [GeneratedRegex("add|would be great|should support|could you|please support")] private static partial Regex Feature();

    public static string Keywords(string ticket)
    {
        var t = ticket.ToLowerInvariant();
        return Billing().IsMatch(t) ? "billing" : Bug().IsMatch(t) ? "bug" : Feature().IsMatch(t) ? "feature" : "other";
    }

    [GeneratedRegex(@"\bfirst\b", RegexOptions.IgnoreCase)] private static partial Regex First();
    [GeneratedRegex(@"\bsecond\b", RegexOptions.IgnoreCase)] private static partial Regex Second();

    /// <summary>Asks in both orders, so a judge that prefers whatever comes first is caught, not trusted.</summary>
    public static string Pairwise(Func<string, string> ask, string ticket, string a, string b)
    {
        string Prompt(string first, string second) =>
            $"Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n{ticket}\n</ticket>\n" +
            $"<first>\n{first}\n</first>\n<second>\n{second}\n</second>";
        static string Pick(string answer) => First().IsMatch(answer) ? "first" : Second().IsMatch(answer) ? "second" : "";
        return (Pick(ask(Prompt(a, b))), Pick(ask(Prompt(b, a)))) switch
        {
            ("first", "second") => "a",
            ("second", "first") => "b",
            _ => "inconsistent",
        };
    }

    /// <summary>(agreement, Cohen's kappa). Kappa removes the agreement you'd expect by chance.</summary>
    public static (double Agreement, double Kappa) Agreement(bool[] judge, bool[] human)
    {
        double n = judge.Length;
        var agree = judge.Zip(human).Count(pair => pair.First == pair.Second) / n;
        double judgeYes = judge.Count(x => x) / n, humanYes = human.Count(x => x) / n;
        var chance = judgeYes * humanYes + (1 - judgeYes) * (1 - humanYes);
        return (agree, chance == 1 ? 1 : (agree - chance) / (1 - chance));
    }
}
