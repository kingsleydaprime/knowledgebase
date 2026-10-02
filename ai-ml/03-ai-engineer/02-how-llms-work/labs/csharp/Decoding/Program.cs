// From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab.

var scores = new List<Entry> { new("Paris", 4.0), new("a", 2.0), new("the", 1.5), new("Lyon", 0.5) };
static List<double> Rounded(List<Entry> d) => d.Select(e => Math.Round(e.P, 3, MidpointRounding.AwayFromZero)).ToList();
static List<string> Tokens(List<Entry> d) => d.Select(e => e.Token).ToList();

Check(Rounded(Decoder.Softmax(scores, 1)), [0.802, 0.108, 0.066, 0.024]);
Check(Rounded(Decoder.Softmax(scores, 0.5)), [0.975, 0.018, 0.007, 0.001]);
Check(Rounded(Decoder.Softmax(scores, 2)), [0.547, 0.201, 0.157, 0.095]);

var dist = Decoder.Softmax(scores, 1);
Check(Tokens(Decoder.TopK(dist, 2)), ["Paris", "a"]);
Check(Tokens(Decoder.TopP(dist, 0.9)), ["Paris", "a"]);
Check(Tokens(Decoder.TopP(dist, 0.97)), ["Paris", "a", "the"]);

var r = Decoder.SeededRandom(42);
Check([r(), r(), r()], [0.6011037519201636, 0.44829055899754167, 0.8524657934904099]);

var r2 = Decoder.SeededRandom(42);
var picks = string.Join(" ", Enumerable.Range(0, 10).Select(_ => Decoder.Sample(dist, r2)));
Check([picks], ["Paris Paris a Paris Paris Paris Paris Paris a Paris"]);
var r3 = Decoder.SeededRandom(42);
Check([Enumerable.Range(0, 1000).Count(_ => Decoder.Sample(dist, r3) == "Paris")], [796]); // about 80.2%

Check([Decoder.Greedy(Decoder.Softmax(scores, 2))], ["Paris"]);
Console.WriteLine("ok: decoding matches the TypeScript lab");

static void Check<T>(List<T> got, List<T> want)
{
    if (!got.SequenceEqual(want))
        throw new Exception($"got [{string.Join(", ", got)}], want [{string.Join(", ", want)}]");
}

/// <summary>One token and its score or probability. Lists keep a fixed order, so sampling is reproducible.</summary>
record Entry(string Token, double P);

static class Decoder
{
    /// <summary>mulberry32. new Random(seed) also repeats; this one matches every language in this companion.</summary>
    public static Func<double> SeededRandom(uint seed)
    {
        var a = seed;
        return () =>
        {
            unchecked // uint arithmetic wraps at 32 bits, like JavaScript's >>> 0
            {
                a += 0x6d2b79f5;
                var t = a;
                t = (t ^ (t >> 15)) * (t | 1);
                t ^= t + (t ^ (t >> 7)) * (t | 61);
                return (t ^ (t >> 14)) / 4294967296.0;
            }
        };
    }

    public static List<Entry> Softmax(List<Entry> scores, double temperature)
    {
        var top = scores.Max(e => e.P / temperature); // subtract the max so Math.Exp can't overflow
        return Renormalise(scores.Select(e => e with { P = Math.Exp(e.P / temperature - top) }));
    }

    static IEnumerable<Entry> ByProbability(List<Entry> dist) => dist.OrderByDescending(e => e.P); // stable

    public static List<Entry> TopK(List<Entry> dist, int k) => Renormalise(ByProbability(dist).Take(k));

    public static List<Entry> TopP(List<Entry> dist, double p)
    {
        var kept = new List<Entry>();
        var cumulative = 0.0;
        foreach (var e in ByProbability(dist))
        {
            kept.Add(e);
            if ((cumulative += e.P) >= p) break;
        }
        return Renormalise(kept);
    }

    static List<Entry> Renormalise(IEnumerable<Entry> entries)
    {
        var list = entries.ToList();
        var total = list.Sum(e => e.P);
        return list.Select(e => e with { P = e.P / total }).ToList();
    }

    public static string Sample(List<Entry> dist, Func<double> random)
    {
        var r = random();
        foreach (var e in dist)
            if ((r -= e.P) < 0) return e.Token;
        return dist[^1].Token;
    }

    public static string Greedy(List<Entry> dist) => ByProbability(dist).First().Token;
}
