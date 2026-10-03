// The arithmetic behind choosing a monolith, microservices or serverless, and a modular-monolith boundary
// checker. The same numbers as the TypeScript lab.

public record Pricing(double PerMillionRequests, double PerGbSecond);

public record Module(string Name, List<string> Imports);

public static class Architecture
{
    public static long CoordinationLinks(long people) => people * (people - 1) / 2;

    public static double ReleaseBreaks(int changes, double p) => 1 - Math.Pow(1 - p, changes);

    /// <summary>(ms added, chance all calls succeed) when a module moves behind the network.</summary>
    public static (double AddedMs, double Availability) Extract(int callsPerRequest, double networkMs, double callAvailability) =>
        (callsPerRequest * networkMs, Math.Pow(callAvailability, callsPerRequest));

    public static double ServerlessMonthly(double requests, double ms, double memoryGb, Pricing p) =>
        requests / 1e6 * p.PerMillionRequests + requests * (ms / 1000) * memoryGb * p.PerGbSecond;

    public static double BreakEvenRequests(double serverMonthly, double ms, double memoryGb, Pricing p) =>
        serverMonthly / (p.PerMillionRequests / 1e6 + (ms / 1000) * memoryGb * p.PerGbSecond);

    public static double ColdShare(double perMinute, double warmMinutes) => Math.Exp(-perMinute * warmMinutes);

    public static double SimulateColdShare(double perMinute, double warmMinutes, int requests, uint seed)
    {
        var a = seed;
        var cold = 0;
        for (var i = 0; i < requests; i++)
        {
            a += 0x6d2b79f5; // mulberry32, as in week 1's lab
            var t = (a ^ (a >> 15)) * (a | 1);
            t ^= t + (t ^ (t >> 7)) * (t | 61);
            var random = (t ^ (t >> 14)) / 4294967296.0;
            if (-Math.Log(1 - random) / perMinute > warmMinutes) cold++;
        }
        return (double)cold / requests;
    }

    /// <summary>Imports that reach inside another module. In .NET, `internal` plus one project per module enforces this.</summary>
    public static List<string> BoundaryViolations(IReadOnlyList<Module> modules)
    {
        var names = modules.Select(m => m.Name).ToHashSet();
        return [.. from m in modules
                   from imp in m.Imports
                   let target = imp.Split('/')[0]
                   where target != m.Name && names.Contains(target) && imp.Contains('/')
                   select $"{m.Name} → {imp}"];
    }

    /// <summary>A dependency cycle as a path that starts and ends at the same module, or null.</summary>
    public static List<string>? FindCycle(IReadOnlyList<Module> modules)
    {
        var deps = modules.ToDictionary(m => m.Name, m => m.Imports.Select(i => i.Split('/')[0]).Where(d => d != m.Name).Distinct().ToList());
        var state = new Dictionary<string, bool>(); // false while visiting, true when done
        var path = new List<string>();
        List<string>? Visit(string name)
        {
            if (state.TryGetValue(name, out var done)) return done ? null : [.. path[path.IndexOf(name)..], name];
            state[name] = false;
            path.Add(name);
            foreach (var d in deps.GetValueOrDefault(name) ?? [])
                if (Visit(d) is { } cycle) return cycle;
            path.RemoveAt(path.Count - 1);
            state[name] = true;
            return null;
        }
        return modules.Select(m => Visit(m.Name)).FirstOrDefault(c => c is not null);
    }
}
