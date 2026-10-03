// How a load balancer picks a server, health checks that take a failing server out and put it back, and
// consistent hashing. The same numbers as the TypeScript lab.

/// <summary>Chooses a server from how many requests each is still working on.</summary>
public delegate int Pick(int[] outstanding, Func<double> random);

public static class Balancer
{
    public static Pick RoundRobin()
    {
        var next = 0;
        return (outstanding, _) => next++ % outstanding.Length;
    }

    /// <summary>The fewest requests in progress; ties go to the lowest number.</summary>
    public static int LeastOutstanding(int[] outstanding, Func<double> _) => Array.IndexOf(outstanding, outstanding.Min());

    public static int Random(int[] outstanding, Func<double> random) => (int)(random() * outstanding.Length);

    /// <summary>Two servers at random, and the less busy of the two.</summary>
    public static int TwoChoices(int[] outstanding, Func<double> random)
    {
        var a = (int)(random() * outstanding.Length);
        var b = (int)(random() * outstanding.Length);
        return outstanding[b] < outstanding[a] ? b : a;
    }

    /// <summary>mulberry32, the same generator as week 1's lab.</summary>
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

    public record Latency(double Mean, double P50, double P99);

    /// <summary>Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms.</summary>
    public static Latency Simulate(Pick pick, int servers, double busy, int requests, uint seed)
    {
        var random = Seeded(seed);
        var meanWorkMs = 0.95 * 10 + 0.05 * 200;
        var gapMs = meanWorkMs / (busy * servers);
        var finishes = Enumerable.Range(0, servers).Select(_ => new Queue<double>()).ToArray(); // when each queued request ends
        var lastEnds = new double[servers];
        double now = 0, total = 0;
        var times = new double[requests];
        for (var i = 0; i < requests; i++)
        {
            now += -gapMs * Math.Log(1 - random());
            foreach (var queue in finishes)
                while (queue.Count > 0 && queue.Peek() <= now) queue.Dequeue();
            var s = pick(finishes.Select(q => q.Count).ToArray(), random);
            var workMs = random() < 0.05 ? 200 : 10;
            var ends = Math.Max(now, finishes[s].Count > 0 ? lastEnds[s] : 0) + workMs; // Queue<T> can't peek at its back
            finishes[s].Enqueue(ends);
            lastEnds[s] = ends;
            times[i] = ends - now;
            total += ends - now;
        }
        Array.Sort(times);
        double Percentile(double p) => times[Math.Max(1, (int)Math.Ceiling(p / 100 * times.Length)) - 1];
        static double Round(double x) => Math.Round(x, MidpointRounding.AwayFromZero); // the default rounds halves to even
        return new(Round(total / requests), Round(Percentile(50)), Round(Percentile(99)));
    }

    /// <summary>nginx's smooth weighted round-robin. An array of pairs, so the order that breaks ties is fixed.</summary>
    public static Func<string> SmoothWeighted(params (string Name, int Weight)[] servers)
    {
        var total = servers.Sum(s => s.Weight);
        var current = new int[servers.Length];
        return () =>
        {
            var best = 0;
            for (var i = 0; i < servers.Length; i++)
            {
                current[i] += servers[i].Weight;
                if (current[i] > current[best]) best = i;
            }
            current[best] -= total;
            return servers[best].Name;
        };
    }

    public static string PickHealthy(IEnumerable<(string Name, Health Health)> servers, int turn)
    {
        var up = servers.Where(s => s.Health.Up).Select(s => s.Name).ToArray();
        if (up.Length == 0) throw new InvalidOperationException("no healthy servers: answer 503");
        return up[turn % up.Length];
    }

    /// <summary>
    /// FNV-1a, then a mixing step, over UTF-16 code units like JavaScript. string.GetHashCode() can't place keys:
    /// it's randomised per process, so two servers would disagree.
    /// </summary>
    public static uint Hash(string text)
    {
        var h = 0x811c9dc5u;
        foreach (var c in text) h = (h ^ c) * 0x01000193;
        h = (h ^ (h >> 16)) * 0x85ebca6b;
        h = (h ^ (h >> 13)) * 0xc2b2ae35;
        return h ^ (h >> 16);
    }

    public static string Modulo(string key, IReadOnlyList<string> servers) => servers[(int)(Hash(key) % (uint)servers.Count)];
}

/// <summary><c>fall</c> failures in a row mark a server down; <c>rise</c> successes in a row bring it back.</summary>
public sealed class Health(int fall = 3, int rise = 2)
{
    private int _streak;
    public bool Up { get; private set; } = true;

    public void Record(bool ok)
    {
        if (ok == Up)
        {
            _streak = 0;
            return;
        }
        if (++_streak >= (Up ? fall : rise))
        {
            Up = !Up;
            _streak = 0;
        }
    }
}

/// <summary>Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it.</summary>
public sealed class HashRing
{
    private List<(uint At, string Server)> _points = [];
    private readonly int _replicas;

    public HashRing(IEnumerable<string> servers, int replicas = 100)
    {
        _replicas = replicas;
        foreach (var s in servers) Add(s);
    }

    public void Add(string server)
    {
        var added = Enumerable.Range(0, _replicas).Select(r => (At: Balancer.Hash($"{server}#{r}"), Server: server));
        _points = _points.Concat(added).OrderBy(p => p.At).ToList(); // OrderBy is stable; List.Sort isn't
    }

    public void Remove(string server) => _points.RemoveAll(p => p.Server == server);

    public string ServerFor(string key)
    {
        if (_points.Count == 0) throw new InvalidOperationException("the ring is empty");
        var h = Balancer.Hash(key);
        int lo = 0, hi = _points.Count; // binary search for the first point at or after h
        while (lo < hi)
        {
            var mid = (lo + hi) / 2;
            if (_points[mid].At < h) lo = mid + 1;
            else hi = mid;
        }
        return _points[lo % _points.Count].Server; // past the last point, wrap round to the first
    }
}
