// Checks: the same numbers as every other language.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var keys = Enumerable.Range(0, 10_000).Select(i => $"user:{i}").ToArray();
string[] four = ["cache-a", "cache-b", "cache-c", "cache-d"];

var pick = Balancer.RoundRobin();
int[] queues = [5, 0, 0];
Check(Enumerable.Range(0, 6).Select(_ => pick(queues, () => 0)).SequenceEqual([0, 1, 2, 0, 1, 2]), "round-robin");
Check(Balancer.LeastOutstanding(queues, () => 0) == 1, "least outstanding");

var weighted = Balancer.SmoothWeighted(("a", 5), ("b", 1), ("c", 1));
var order = string.Concat(Enumerable.Range(0, 7).Select(_ => weighted()));
Check(order == "aabacaa", order);

Check(Balancer.Simulate(Balancer.RoundRobin(), 4, 0.8, 100_000, 7) == new Balancer.Latency(214, 138, 1_158), "round-robin");
Check(Balancer.Simulate(Balancer.Random, 4, 0.8, 100_000, 7) == new Balancer.Latency(255, 159, 1_588), "random");
Check(Balancer.Simulate(Balancer.LeastOutstanding, 4, 0.8, 100_000, 7) == new Balancer.Latency(68, 17, 466), "least");
var two = Balancer.Simulate(Balancer.TwoChoices, 4, 0.8, 100_000, 7);
Check(two == new Balancer.Latency(96, 25, 495), two);

var health = new Health(3, 2);
var states = new[] { false, false, true, false, false, false, true, true }.Select(ok => { health.Record(ok); return health.Up; });
Check(states.SequenceEqual([true, true, true, true, true, false, false, true]), "fall and rise");

var servers = new[] { "app-1", "app-2", "app-3" }.Select(name => (Name: name, Health: new Health(3, 2))).ToArray();
for (var i = 0; i < 3; i++) servers[1].Health.Record(false);
Check(Enumerable.Range(0, 4).Select(t => Balancer.PickHealthy(servers, t)).SequenceEqual(["app-1", "app-3", "app-1", "app-3"]), "skips app-2");
foreach (var s in servers) for (var i = 0; i < 3; i++) s.Health.Record(false);
try
{
    Balancer.PickHealthy(servers, 0);
    Check(false, "expected no healthy servers");
}
catch (InvalidOperationException)
{
    // answer 503
}

string[] five = [.. four, "cache-e"];
var movedByModulo = keys.Count(k => Balancer.Modulo(k, four) != Balancer.Modulo(k, five));
Check(Math.Abs(movedByModulo - 8_000) < 200, movedByModulo);
var ring = new HashRing(four, 100);
var before = keys.Select(ring.ServerFor).ToArray();
ring.Add("cache-e");
var moved = keys.Where((k, i) => ring.ServerFor(k) != before[i]).ToArray();
Check(Math.Abs(moved.Length - 2_000) < 300 && moved.All(k => ring.ServerFor(k) == "cache-e"), moved.Length);
ring.Remove("cache-e");
Check(keys.Select(ring.ServerFor).SequenceEqual(before), "removing it puts the keys back");

double Busiest(int replicas)
{
    var r = new HashRing(four, replicas);
    return keys.CountBy(r.ServerFor).Max(g => g.Value) / (keys.Length / 4.0);
}
Check(Busiest(1) > 1.4 && Busiest(100) < 1.2, (Busiest(1), Busiest(100)));
Console.WriteLine("all balancing checks passed");
