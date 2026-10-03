// The arithmetic behind performance and scalability. The same numbers as the TypeScript lab, because the
// random number generator is the same one, bit for bit.
public static class Scaling
{
    /// <summary>Nearest rank: p99 of 1,000 samples is the 990th smallest.</summary>
    public static double Percentile(IReadOnlyCollection<double> samples, double p)
    {
        if (samples.Count == 0) throw new ArgumentException("no samples", nameof(samples));
        var sorted = samples.Order().ToArray(); // a sorted copy; the caller's data keeps its order
        var rank = Math.Max(1, (int)Math.Ceiling(p / 100 * sorted.Length));
        return sorted[rank - 1];
    }

    public static double Mean(IReadOnlyCollection<double> samples)
    {
        var total = 0.0;
        foreach (var x in samples) total += x;
        return total / samples.Count;
    }

    /// <summary>mulberry32. C# arithmetic is unchecked unless you ask, so uint wraps as the generator needs.</summary>
    public static Func<double> Seeded(uint seed)
    {
        var a = seed;
        return () =>
        {
            a += 0x6d2b79f5;
            var t = (a ^ (a >> 15)) * (a | 1);
            t ^= t + (t ^ (t >> 7)) * (t | 61);
            return (t ^ (t >> 14)) / 4294967296.0;
        };
    }

    static double Exponential(Func<double> random, double mean) => -mean * Math.Log(1 - random());

    /// <summary>M/M/1: service time ÷ (1 − utilisation).</summary>
    public static double ResponseTime(double serviceMs, double utilisation) =>
        utilisation >= 1 ? double.PositiveInfinity : serviceMs / (1 - utilisation);

    public record Summary(double Mean, double P50, double P99);

    public static Summary SimulateServer(double serviceMs, double utilisation, int requests, uint seed)
    {
        var random = Seeded(seed);
        var gapMs = serviceMs / utilisation;
        double arrives = 0, free = 0;
        var times = new List<double>(requests);
        for (var i = 0; i < requests; i++)
        {
            arrives += Exponential(random, gapMs);
            var starts = Math.Max(arrives, free);
            free = starts + Exponential(random, serviceMs);
            times.Add(free - arrives);
        }
        return new(Mean(times), Percentile(times, 50), Percentile(times, 99));
    }

    public record Stage(string Name, double PerSecond);

    /// <summary>Every request passes every stage, so the system handles only as many as its slowest.</summary>
    public static Stage Throughput(IEnumerable<Stage> stages) => stages.MinBy(s => s.PerSecond)!;

    public static double Amdahl(double n, double serial) => 1 / (serial + (1 - serial) / n);

    public static double Usl(double n, double alpha, double beta) => n / (1 + alpha * (n - 1) + beta * n * (n - 1));

    public static double UslPeak(double alpha, double beta) => Math.Sqrt((1 - alpha) / beta);
}
