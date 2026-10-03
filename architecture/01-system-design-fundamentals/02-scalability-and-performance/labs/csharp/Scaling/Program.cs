// Checks: the same numbers as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

// Math.Round sends halves to the even number by default; JavaScript's Math.round goes up. Say which you mean.
static double Round(double x) => Math.Round(x, MidpointRounding.AwayFromZero);
static string Fixed(double x, int places) => x.ToString("F" + places, CultureInfo.InvariantCulture);

double[] tens = [10, 1, 9, 2, 8, 3, 7, 4, 6, 5];
Check(new[] { 50.0, 90, 99, 100 }.Select(p => Scaling.Percentile(tens, p)).SequenceEqual([5.0, 9, 10, 10]) && tens[0] == 10, "percentiles");
try
{
    Scaling.Percentile([], 50);
    Check(false, "expected an error for no samples");
}
catch (ArgumentException)
{
    // no samples
}

var random = Scaling.Seeded(42);
var latencies = new List<double>();
for (var i = 0; i < 1_000; i++) latencies.Add(random() < 0.02 ? 1_500 + 1_000 * random() : 40 + 20 * random());
double[] tail = [Scaling.Mean(latencies), .. new[] { 50.0, 95, 99 }.Select(p => Scaling.Percentile(latencies, p))];
Check(tail.Select(Round).SequenceEqual([93.0, 50, 59, 2_208]), string.Join(", ", tail));

Check(new[] { 0.5, 0.8, 0.9, 0.95, 0.99 }.Select(b => Round(Scaling.ResponseTime(10, b))).SequenceEqual([20.0, 50, 100, 200, 1_000]), "waits");
Check(double.IsPositiveInfinity(Scaling.ResponseTime(10, 1)), "full");

foreach (var busy in new[] { 0.5, 0.8, 0.9 })
{
    var sim = Scaling.SimulateServer(10, busy, 200_000, 7);
    var model = Scaling.ResponseTime(10, busy);
    Check(Math.Abs(sim.Mean - model) / model < 0.1 && Math.Abs(sim.P99 / sim.Mean - Math.Log(100)) < 0.5, sim);
}

double[] diagnosis = [Scaling.ResponseTime(300, 0.1), Scaling.ResponseTime(10, 0.95), Scaling.ResponseTime(10, 0.95 / 2), Scaling.ResponseTime(300, 0.05)];
Check(diagnosis.Select(Round).SequenceEqual([333.0, 200, 19, 316]), string.Join(", ", diagnosis));

var stages = new List<Scaling.Stage> { new("load balancer", 50_000), new("app servers", 4 * 800), new("database writes", 2_000) };
var want = new Scaling.Stage("database writes", 2_000);
Check(Scaling.Throughput(stages) == want, Scaling.Throughput(stages));
stages[1] = new("app servers", 8 * 800);
Check(Scaling.Throughput(stages) == want, "more app servers change nothing");

Check(Fixed(Scaling.Amdahl(8, 0.05), 2) == "5.93" && Scaling.Amdahl(1_000_000, 0.05) < 20, "amdahl");
Check(Round(Scaling.UslPeak(0.05, 0.001)) == 31, "peak");
Check(new[] { 8.0, 31, 60, 100 }.Select(n => Fixed(Scaling.Usl(n, 0.05, 0.001), 1)).SequenceEqual(["5.7", "9.0", "8.0", "6.3"]), "usl");
Console.WriteLine("all scaling checks passed");
