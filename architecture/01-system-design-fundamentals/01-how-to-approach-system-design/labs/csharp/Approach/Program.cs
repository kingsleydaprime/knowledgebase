// Checks: the same numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Math.Round sends halves to the even number by default; JavaScript's Math.round goes up. Say which you mean.
static double Round(double x) => Math.Round(x, MidpointRounding.AwayFromZero);

var game = Sizing.Estimate(new(10_000_000, 5, 10, 3, 50, 365, 2_000));
Check(Round(game.WritesPerSecond.Average) == 579 && Round(game.WritesPerSecond.Peak) == 1736, game.WritesPerSecond);
Check(Round(game.ReadsPerSecond.Peak) == 3472 && game.ReadsPerWrite == 2, game.ReadsPerSecond);
Check(Sizing.HumanBytes(game.StorageBytes) == "910 GB", Sizing.HumanBytes(game.StorageBytes));
Check(Sizing.HumanBytes(game.PeakEgressBytesPerSecond) == "6.9 MB", Sizing.HumanBytes(game.PeakEgressBytesPerSecond));

// Why the scan can't work. int arithmetic wraps silently unless you ask for checked.
var peakReads = (int)Round(game.ReadsPerSecond.Peak);
var players = 50_000_000;
Check(unchecked(peakReads * players) == 1_801_308_160, "wraps to a wrong number");
Check((long)peakReads * players == 173_600_000_000, "widen first");
try
{
    _ = checked(peakReads * players);
    Check(false, "expected an overflow");
}
catch (OverflowException)
{
    // checked refuses instead of wrapping
}
Check(Sizing.HumanBytes(players * 100.0) == "5 GB", "5 GB");

var board = new Leaderboard(1_000);
foreach (var (p, s) in new[] { ("ada", 100), ("bo", 250), ("cy", 250), ("di", 90) }) board.Submit(p, s);
int?[] Ranks(params string[] names) => names.Select(board.Rank).ToArray();
Check(Ranks("bo", "cy", "ada", "di").SequenceEqual(new int?[] { 1, 1, 3, 4 }), "ties share a rank");
Check(!board.Submit("ada", 80) && board.Submit("ada", 300), "only the best counts");
Check(Ranks("ada", "bo", "cy", "di").SequenceEqual(new int?[] { 1, 2, 2, 4 }), "after a new best");
Check(board.Rank("nobody") is null, "unknown player");
try
{
    board.Submit("ed", 1_001);
    Check(false, "expected a rejected score");
}
catch (ArgumentOutOfRangeException)
{
    // above the maximum
}

const int maxScore = 1_000_000;
var big = new Leaderboard(maxScore);
var scores = Enumerable.Range(0, 200_000).Select(i => i * 7_919 % (maxScore + 1)).ToArray();
for (var i = 0; i < scores.Length; i++) big.Submit($"p{i}", scores[i]);
foreach (var i in new[] { 0, 1, 12_345, 199_999 })
{
    var scan = Leaderboard.RankByScan(scores, scores[i]);
    Check(big.Rank($"p{i}") == scan.Rank && big.Steps <= 20 && scan.Steps == 200_000, (i, big.Steps));
}
Console.WriteLine("all approach checks passed");
