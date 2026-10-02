// Pricing with exact decimal money, prefix diagnosis, canonical JSON, a cascade and latency percentiles.
// The same numbers as the TypeScript lab.
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;

/// <summary>US dollars per million tokens. decimal is base-10 and exact for prices like 0.2.</summary>
public sealed record Price(decimal Input, decimal Output, decimal CacheWrite, decimal CacheRead);

/// <summary>Input counts only input that was neither written to nor read from the cache.</summary>
public sealed record Usage(long Input = 0, long Output = 0, long CacheWrite = 0, long CacheRead = 0);

public sealed record Tier(string Name, decimal Cost, Func<string, string> Answer, Func<string, bool> Accept);

public static class Costs
{
    /// <summary>Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them.</summary>
    public static readonly Dictionary<string, Price> Prices = new()
    {
        ["claude-haiku-4-5"] = new(1m, 5m, 1.25m, 0.1m),
        ["claude-sonnet-5-5"] = new(2m, 10m, 2.5m, 0.2m),
        ["claude-opus-5-5"] = new(4m, 20m, 5m, 0.2m),
        ["local"] = new(0m, 0m, 0m, 0m),
    };

    public static decimal Cost(Usage u, Price p) =>
        (u.Input * p.Input + u.Output * p.Output + u.CacheWrite * p.CacheWrite + u.CacheRead * p.CacheRead) / 1_000_000m;

    /// <summary>Caching n calls costs write + (n − 1) × read; not caching costs n × input.</summary>
    public static int BreakEvenCalls(Price p) => (int)Math.Floor((p.CacheWrite - p.CacheRead) / (p.Input - p.CacheRead)) + 1;

    public static int SharedPrefix(string a, string b)
    {
        var i = 0;
        while (i < a.Length && i < b.Length && a[i] == b[i]) i++;
        return i;
    }

    static readonly JsonSerializerOptions Relaxed = new() { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping };

    /// <summary>System.Text.Json writes properties in declaration order and dictionary entries in the
    /// dictionary's order, and has no option to sort them, so sort the tree. It also escapes &lt; and &gt;
    /// by default; the relaxed encoder writes them as they are, as Python and JavaScript do.</summary>
    public static string StableJson<T>(T value) => Sorted(JsonSerializer.SerializeToNode(value))!.ToJsonString(Relaxed);

    static JsonNode? Sorted(JsonNode? node) => node switch
    {
        JsonObject o => new JsonObject(o.OrderBy(p => p.Key, StringComparer.Ordinal)
            .Select(p => KeyValuePair.Create(p.Key, Sorted(p.Value)))),
        JsonArray a => new JsonArray(a.Select(Sorted).ToArray()),
        _ => node?.DeepClone(),
    };

    public static (string Answer, string By, decimal Spent) Cascade(string input, IReadOnlyList<Tier> tiers)
    {
        var spent = 0m;
        for (var i = 0; i < tiers.Count; i++)
        {
            var answer = tiers[i].Answer(input);
            spent += tiers[i].Cost; // a rejected answer was still paid for
            if (i == tiers.Count - 1 || tiers[i].Accept(answer)) return (answer, tiers[i].Name, spent);
        }
        throw new ArgumentException("a cascade needs at least one tier");
    }

    /// <summary>Nearest rank: the smallest value that at least p% of the values are less than or equal to.</summary>
    public static double Percentile(IEnumerable<double> values, double p)
    {
        var sorted = values.Order().ToList();
        return sorted[Math.Max(0, (int)Math.Ceiling(p / 100 * sorted.Count) - 1)];
    }

    /// <summary>Reads an async stream to the end, timing the first chunk separately.</summary>
    public static async Task<(string Text, double TtftMs, double TotalMs)> TimeStream(IAsyncEnumerable<string> chunks, Func<double> nowMs)
    {
        var started = nowMs();
        double? ttft = null;
        var text = new System.Text.StringBuilder();
        await foreach (var chunk in chunks)
        {
            ttft ??= nowMs() - started;
            text.Append(chunk);
        }
        var total = nowMs() - started;
        return (text.ToString(), ttft ?? total, total);
    }
}
