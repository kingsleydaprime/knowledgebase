// Decorators as classes implementing the same interface, composed by hand — or by the DI
// container (the Scrutor package's services.Decorate<IRateSource, Caching>() does this).
var api = new FlakyApi(failures: 2);
var log = new List<string>();
IRateSource rates = new Logging(new Caching(new Retrying(api, attempts: 3)), log);

Check(rates.Rate("GBP", "NGN") == 2000 && rates.Rate("GBP", "NGN") == 2000, "rates");
Check(api.Calls == 3, "two failures, one success, then cached");
Check(log.SequenceEqual(["GBP->NGN = 2000", "GBP->NGN = 2000"]), "logging is outermost");
Console.WriteLine("ok: interface decorators");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

interface IRateSource { long Rate(string baseCurrency, string quote); }

sealed class FlakyApi(int failures) : IRateSource
{
    public int Calls { get; private set; }
    public long Rate(string baseCurrency, string quote)
    {
        if (++Calls <= failures) throw new HttpRequestException("503 from rates API");
        return (baseCurrency, quote) == ("GBP", "NGN") ? 2000 : 1;
    }
}

sealed class Retrying(IRateSource inner, int attempts) : IRateSource
{
    public long Rate(string b, string q)
    {
        for (var i = 1; ; i++)
        {
            try { return inner.Rate(b, q); }
            catch (HttpRequestException) when (i < attempts) { }
        }
    }
}

sealed class Caching(IRateSource inner) : IRateSource
{
    private readonly Dictionary<string, long> _cache = [];
    public long Rate(string b, string q) =>
        _cache.TryGetValue($"{b}->{q}", out var v) ? v : _cache[$"{b}->{q}"] = inner.Rate(b, q);
}

sealed class Logging(IRateSource inner, List<string> log) : IRateSource
{
    public long Rate(string b, string q)
    {
        var v = inner.Rate(b, q);
        log.Add($"{b}->{q} = {v}");
        return v;
    }
}
