// Checks: the same numbers as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static string Fixed(double x, int places) => x.ToString("F" + places, CultureInfo.InvariantCulture);

Check(new long[] { 4, 8, 50 }.Select(Architecture.CoordinationLinks).SequenceEqual([6L, 28, 1_225]), "links");
Check(Fixed(Architecture.ReleaseBreaks(40, 0.01) * 100, 1) == "33.1" && Fixed(Architecture.ReleaseBreaks(5, 0.01) * 100, 1) == "4.9", "release");

var chatty = Architecture.Extract(40, 1, 0.9999);
var coarse = Architecture.Extract(1, 1, 0.9999);
Check(chatty.AddedMs == 40 && Fixed(chatty.Availability * 100, 2) == "99.60", chatty);
Check(coarse.AddedMs == 1 && Fixed(coarse.Availability * 100, 2) == "99.99", coarse);

var price = new Pricing(0.2, 0.0000166667);
Check(Fixed(Architecture.ServerlessMonthly(1_000_000, 200, 0.5, price), 2) == "1.87", "a million");
Check(Fixed(Architecture.ServerlessMonthly(50_000_000, 200, 0.5, price), 2) == "93.33", "fifty million");
Check(Math.Round(Architecture.BreakEvenRequests(30, 200, 0.5, price) / 1e5, MidpointRounding.AwayFromZero) / 10 == 16.1, "break-even");

Check(new[] { 10, 1, 0.1 }.Select(r => Fixed(Architecture.ColdShare(r, 5) * 100, 2)).SequenceEqual(["0.00", "0.67", "60.65"]), "cold");
foreach (var rate in new[] { 1, 0.1 })
    Check(Math.Abs(Architecture.SimulateColdShare(rate, 5, 100_000, 7) - Architecture.ColdShare(rate, 5)) < 0.005, rate);

var shop = new List<Module>
{
    new("orders", ["billing", "catalog/internal/prices"]),
    new("billing", ["customers"]),
    new("catalog", ["catalog/internal/prices"]),
    new("customers", []),
};
Check(Architecture.BoundaryViolations(shop).SequenceEqual(["orders → catalog/internal/prices"]), "violations");
Check(Architecture.FindCycle(shop) is null, "no cycle yet");
shop[3].Imports.Add("orders");
Check(Architecture.FindCycle(shop)?.SequenceEqual(["orders", "billing", "customers", "orders"]) == true, string.Join(",", Architecture.FindCycle(shop) ?? []));
Console.WriteLine("all architecture checks passed");
