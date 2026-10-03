// Checks: the same numbers as every other language.
using System.Threading.Channels;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

long clock = 0;
Broker NewBroker() => new(() => Interlocked.Read(ref clock), 30_000, 3);

var b = NewBroker();
b.Subscribe("orders", "invoices");
b.Subscribe("orders", "analytics");
b.Publish("orders", "order 1");
b.Publish("orders", "order 2");
Check(b.Receive("invoices")?.Body == "order 1" && b.Receive("invoices")?.Body == "order 2" && b.Receive("invoices") is null, "one consumer each");
Check(b.Receive("analytics")?.Body == "order 1" && b.Receive("analytics")?.Body == "order 2", "every subscription");
b.Publish("refunds", "refund 1");
Check(b.Depth("invoices") + b.Depth("analytics") == 4, "nobody keeps refunds");

clock = 0;
var r = NewBroker();
r.Subscribe("orders", "invoices");
r.Publish("orders", "order 1");
Check(r.Receive("invoices")?.Attempt == 1 && r.Receive("invoices") is null, "hidden while worked on");
clock = 30_000;
Check(r.Receive("invoices")?.Attempt == 2, "redelivered");
clock = 60_000;
Check(r.Receive("invoices")?.Attempt == 3, "redelivered again");
clock = 90_000;
Check(r.Receive("invoices") is null && r.DeadLetters("invoices").SequenceEqual(["order 1"]) && r.Depth("invoices") == 0, "dead-lettered");

foreach (var safe in new[] { false, true })
{
    clock = 0;
    var p = NewBroker();
    p.Subscribe("orders", "payments");
    p.Publish("orders", "charge £40 for order 1");
    var charges = 0;
    Action<string> charge = _ => charges++;
    var once = Messages.Idempotent(charge, new HashSet<string>());
    Action<Delivery> handle = safe ? d => once(d) : d => charge(d.Body);
    handle(p.Receive("payments")!); // charged, then a crash before the ack
    clock = 30_000;
    var again = p.Receive("payments")!;
    handle(again);
    p.Ack("payments", again.Id);
    Check(charges == (safe ? 1 : 2), (safe, charges));
}

int[] spike = [.. Enumerable.Repeat(300, 10), .. Enumerable.Repeat(20, 50)];
Check(Messages.LevelLoad(spike, 100) == new Messages.Levelled(2_000, 2_000, 2_000, 35, 20), Messages.LevelLoad(spike, 100));
var four = Messages.LevelLoad(spike, 200);
Check(four.PeakDepth == 1_000 && four.ClearedAfterSeconds == 16 && four.MaxWaitSeconds == 5, four);

clock = 0;
var s = NewBroker();
s.Subscribe("orders", "shipping");
foreach (var e in new[] { "created", "paid", "shipped" }) s.Publish("orders", $"order 7 {e}", "order-7");
var seen = new List<string>();
foreach (var fail in new[] { false, true, false })
{
    var d = s.Receive("shipping")!;
    if (fail) continue;
    seen.Add(d.Body);
    s.Ack("shipping", d.Id);
}
clock = 30_000;
seen.Add(s.Receive("shipping")!.Body);
Check(seen.SequenceEqual(["order 7 created", "order 7 shipped", "order 7 paid"]), string.Join(", ", seen));

var log = new PartitionedLog(4);
foreach (var e in new[] { "created", "paid", "shipped" }) log.Append("order-7", $"order 7 {e}");
var part = Messages.PartitionFor("order-7", 4);
var inOrder = new List<string>();
var failedOnce = false;
for (var m = log.Poll("shipping", part); m is not null; m = log.Poll("shipping", part))
{
    if (m.EndsWith("paid") && !failedOnce)
    {
        failedOnce = true; // no commit: the same message comes back
        continue;
    }
    inOrder.Add(m);
    log.Commit("shipping", part);
}
Check(inOrder.SequenceEqual(["order 7 created", "order 7 paid", "order 7 shipped"]), string.Join(", ", inOrder));
Check(log.Poll("analytics", part) == "order 7 created", "a new group replays");

var counts = new int[4];
for (var i = 0; i < 10_000; i++) counts[Messages.PartitionFor($"order-{i}", 4)]++;
Check(counts.All(n => Math.Abs(n - 2_500) < 200), string.Join(", ", counts));

// A bounded channel pushes back: TryWrite refuses when full, WriteAsync waits.
var q = Channel.CreateBounded<int>(new BoundedChannelOptions(3) { FullMode = BoundedChannelFullMode.Wait });
Check(new[] { 1, 2, 3, 4 }.Select(n => q.Writer.TryWrite(n)).SequenceEqual([true, true, true, false]), "fourth refused");
Check(await q.Reader.ReadAsync() == 1 && await q.Reader.ReadAsync() == 2 && await q.Reader.ReadAsync() == 3, "drained");
var puts = 0;
var producer = Task.Run(async () =>
{
    for (var n = 1; n <= 5; n++)
    {
        await q.Writer.WriteAsync(n); // waits while the channel is full
        Interlocked.Increment(ref puts);
    }
});
while (Volatile.Read(ref puts) < 3) await Task.Delay(1); // it can't get past 3 until something is read
Check(await q.Reader.ReadAsync() == 1, "first out");
while (Volatile.Read(ref puts) < 4) await Task.Delay(1);
Check(Volatile.Read(ref puts) == 4, "one out, one more in");
for (var i = 2; i <= 5; i++) Check(await q.Reader.ReadAsync() == i, i);
await producer;
Console.WriteLine("all messaging checks passed");
