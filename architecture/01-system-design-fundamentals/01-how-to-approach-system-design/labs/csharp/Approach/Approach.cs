// Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps.
// The same numbers as the TypeScript lab.
using System.Globalization;

public record Assumptions(double DailyActiveUsers, double WritesPerUserPerDay, double ReadsPerUserPerDay,
    double PeakToAverage, double BytesPerWrite, double KeptForDays, double BytesPerRead);

public record Rate(double Average, double Peak);

public record Estimate(Rate WritesPerSecond, Rate ReadsPerSecond, double ReadsPerWrite, double StorageBytes,
    double PeakEgressBytesPerSecond);

public static class Sizing
{
    public const double SecondsPerDay = 86_400;

    public static Estimate Estimate(Assumptions a)
    {
        var writes = a.DailyActiveUsers * a.WritesPerUserPerDay / SecondsPerDay;
        var reads = a.DailyActiveUsers * a.ReadsPerUserPerDay / SecondsPerDay;
        return new(
            new(writes, writes * a.PeakToAverage),
            new(reads, reads * a.PeakToAverage),
            a.ReadsPerUserPerDay / a.WritesPerUserPerDay,
            a.DailyActiveUsers * a.WritesPerUserPerDay * a.BytesPerWrite * a.KeptForDays,
            reads * a.PeakToAverage * a.BytesPerRead);
    }

    /// <summary>Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB".</summary>
    public static string HumanBytes(double n)
    {
        string[] units = ["B", "KB", "MB", "GB", "TB", "PB"];
        var i = 0;
        while (n >= 1000 && i < units.Length - 1)
        {
            n /= 1000;
            i++;
        }
        // "G2" gives "9.1E+02" for 910; parse it back. InvariantCulture, or a German machine prints "6,9".
        var inv = CultureInfo.InvariantCulture;
        return $"{double.Parse(n.ToString("G2", inv), inv).ToString(inv)} {units[i]}";
    }
}

/// <summary>Each player's best score, and a Fenwick tree of how many players have each score.</summary>
public sealed class Leaderboard(int maxScore)
{
    private readonly Dictionary<string, int> _best = [];
    private readonly int[] _tree = new int[maxScore + 2];
    public int Steps { get; private set; } // the work the last Rank did

    public int Players => _best.Count;

    /// <summary>Only a player's best counts. A score can't be 2.5: the int type rules it out.</summary>
    public bool Submit(string player, int score)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(score);
        ArgumentOutOfRangeException.ThrowIfGreaterThan(score, maxScore);
        var seen = _best.TryGetValue(player, out var old);
        if (seen && score <= old) return false;
        if (seen) Add(old, -1);
        Add(score, +1);
        _best[player] = score;
        return true;
    }

    public int? Rank(string player)
    {
        if (!_best.TryGetValue(player, out var score)) return null;
        Steps = 0;
        return 1 + Players - CountAtMost(score);
    }

    private void Add(int score, int delta)
    {
        for (var i = score + 1; i < _tree.Length; i += i & -i) _tree[i] += delta;
    }

    private int CountAtMost(int score)
    {
        var count = 0;
        for (var i = score + 1; i > 0; i -= i & -i)
        {
            count += _tree[i];
            Steps++;
        }
        return count;
    }

    /// <summary>The obvious way: look at every player.</summary>
    public static (int Rank, int Steps) RankByScan(int[] scores, int mine) =>
        (1 + scores.Count(s => s > mine), scores.Length);
}
