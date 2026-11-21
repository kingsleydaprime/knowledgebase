// Checks: the same numbers as every other language.
using System.Text.Json;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var sonnet = Costs.Prices["claude-sonnet-5-5"];
Check(Costs.Cost(new(Input: 2000, Output: 500), sonnet) == 0.009m, "output costs five times input");

var uncached = 1000 * Costs.Cost(new(Input: 6150, Output: 100), sonnet);
var cached = Costs.Cost(new(CacheWrite: 6000, Input: 150, Output: 100), sonnet);
for (var i = 0; i < 999; i++) cached += Costs.Cost(new(CacheRead: 6000, Input: 150, Output: 100), sonnet);
Check(uncached == 13.30m && cached == 2.5138m, (uncached, cached)); // exact; decimal == compares value, not scale
var asDouble = (double)Costs.Cost(new(CacheWrite: 6000, Input: 150, Output: 100), sonnet);
for (var i = 0; i < 999; i++) asDouble += (double)Costs.Cost(new(CacheRead: 6000, Input: 150, Output: 100), sonnet);
Check(asDouble != 2.5138 && Math.Abs(asDouble - 2.5138) < 1e-9, asDouble); // the same sum in double drifts
Check(Costs.BreakEvenCalls(sonnet) == 2 && Costs.BreakEvenCalls(sonnet with { CacheWrite = 4m }) == 3, "break-even");

var system = string.Concat(Enumerable.Repeat("You classify support tickets. Label by what the team has to do next. ", 20));
string Front(string date) => $"Today is {date}.\n{system}\nhelp";
string End(string date) => $"{system}\nToday is {date}.\nhelp";
var (a, b) = ("2026-10-02T09:00:00Z", "2026-10-02T09:00:07Z");
Check(Costs.SharedPrefix(Front(a), Front(b)) == 27 && Costs.SharedPrefix(End(a), End(b)) == system.Length + 28, "prefix");

var inserted = new Dictionary<string, object> { ["user"] = new Dictionary<string, object> { ["tier"] = "pro", ["id"] = 7 }, ["tools"] = new[] { "search" } };
Check(JsonSerializer.Serialize(inserted) == """{"user":{"tier":"pro","id":7},"tools":["search"]}""", JsonSerializer.Serialize(inserted)); // insertion order
Check(Costs.StableJson(inserted) == """{"tools":["search"],"user":{"id":7,"tier":"pro"}}""", Costs.StableJson(inserted));
Check(JsonSerializer.Serialize("<ticket>") == "\"\\u003Cticket\\u003E\"" && Costs.StableJson("<ticket>") == "\"<ticket>\"", JsonSerializer.Serialize("<ticket>"));

var golden = Evals.LoadGolden(Path.Combine(args.Length > 0 ? args[0] : "../../../12-evals/labs/shared", "golden.jsonl"));
var label = golden.ToDictionary(c => c.Ticket, c => c.Label);
Tier[] tiers = [new("keywords", 0m, Evals.Keywords, x => x != "other"), new("big", 0.002m, t => label[t], _ => true)]; // big: a stand-in that is always right
var results = golden.Select(c => (Case: c, Result: Costs.Cascade(c.Ticket, tiers))).ToList();
Check(results.Where(r => r.Result.By == "big").Select(r => r.Case.Id).SequenceEqual(["t04", "t10", "t12", "t14", "t17", "t19"]), "escalated");
Check(results.Where(r => r.Result.Answer != r.Case.Label).Select(r => r.Case.Id).SequenceEqual(["t15", "t20"]), "wrong");
Check(results.Sum(r => r.Result.Spent) == 0.012m, results.Sum(r => r.Result.Spent));

double[] ms = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000];
Check(Costs.Percentile(ms, 50) == 1000 && Costs.Percentile(ms, 95) == 9000 && ms.Average() == 1819, "percentiles");

var t = 0.0;
async IAsyncEnumerable<string> Stream()
{
    t += 800; // the model reads the prompt before the first token
    yield return "Your";
    foreach (var word in new[] { " refund", " is", " on", " its", " way." })
    {
        t += 100;
        yield return word;
    }
    await Task.CompletedTask;
}
Check(await Costs.TimeStream(Stream(), () => t) == ("Your refund is on its way.", 800, 1300), "time to first token");

Console.WriteLine("all cost checks passed");
