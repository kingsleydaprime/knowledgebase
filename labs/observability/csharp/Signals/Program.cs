using System.Diagnostics.Metrics;

// System.Diagnostics.Metrics is built into .NET: code records to a Histogram<T> on a Meter;
// an exporter (OpenTelemetry, Prometheus) listens and does the bucketing. Here a MeterListener
// plays the exporter, bucketing exactly as Prometheus would.
double[] bounds = [25, 50, 100, 250, 500, 1000, 2500, 5000];
var counts = new long[bounds.Length + 1];

using var meter = new Meter("Shop.Api");
var duration = meter.CreateHistogram<double>("request.duration", unit: "ms");

using var listener = new MeterListener();
listener.InstrumentPublished = (instrument, l) => { if (instrument.Meter == meter) l.EnableMeasurementEvents(instrument); };
listener.SetMeasurementEventCallback<double>((_, value, _, _) =>
{
    var i = Array.FindIndex(bounds, b => value <= b);   // "le": less than or equal
    counts[i < 0 ? bounds.Length : i]++;
});
listener.Start();

for (var i = 0; i < 97; i++) duration.Record(20 + i % 10);
foreach (var ms in new double[] { 1800, 2100, 3000 }) duration.Record(ms);

Check(Math.Abs(EstimateQuantile(0.50) - 20.83) < 0.01, "p50 from buckets");   // exact: 24
Check(EstimateQuantile(0.99) == 2500, "p99 from buckets");                     // exact: 2100
Console.WriteLine("ok: p50 ~ 20.83, p99 ~ 2500 from buckets");

double EstimateQuantile(double q)
{
    double rank = q * counts.Sum(), lower = 0, cumulative = 0;
    for (var i = 0; i < counts.Length; i++)
    {
        var before = cumulative;
        cumulative += counts[i];
        if (cumulative >= rank)
            return i == bounds.Length ? lower : lower + (bounds[i] - lower) * (rank - before) / (cumulative - before);
        if (i < bounds.Length) lower = bounds[i];
    }
    return lower;
}

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }
