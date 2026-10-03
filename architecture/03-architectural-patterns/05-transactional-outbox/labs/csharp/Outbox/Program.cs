// Checks: the same scenarios as every other language.
using Microsoft.Data.Sqlite;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static Exception Thrown(Action body)
{
    try
    {
        body();
    }
    catch (Exception e)
    {
        return e;
    }
    throw new Exception("expected an exception");
}

using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    Check(Thrown(() => Outbox.PlaceOrderSaveThenPublish(db, b, "o1", 500_000, crashBetween: true)) is CrashException, "crash");
    Check(Outbox.CountOrders(db) == 1 && b.Sent.Count == 0, "the event is lost");
}
using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    var e = Thrown(() => Outbox.PlaceOrderPublishThenSave(db, b, "o2", -1));
    Check(e is SqliteException && e.Message.Contains("CHECK constraint failed"), e.Message);
    Check(Outbox.CountOrders(db) == 0 && b.Sent.Count == 1, "a phantom event");
}
using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    Outbox.PlaceOrderWithOutbox(db, "o3", 500_000);
    Check(Outbox.Relay(db, b) == 1 && Outbox.Relay(db, b) == 0, "sent once");
    Check(b.Sent.SequenceEqual([new Event("evt-o3", "OrderPlaced", "o3")]), b.Sent.Count);
}
using (var db = Outbox.OpenDb())
{
    var e = Thrown(() => Outbox.PlaceOrderWithOutbox(db, "o4", -1));
    Check(e.Message.Contains("CHECK constraint failed"), e.Message);
    Check(Outbox.CountOrders(db) == 0 && Outbox.Relay(db, new FakeBroker()) == 0, "rolled back together");
}
using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    Outbox.PlaceOrderWithOutbox(db, "o5", 500_000);
    Check(Thrown(() => Outbox.Relay(db, b, crashBeforeMark: true)) is CrashException, "relay crash");
    Outbox.Relay(db, b);
    var consumer = new IdempotentConsumer();
    Check(b.Sent.Count == 2 && b.Sent.Select(consumer.Handle).SequenceEqual(["applied", "duplicate"]), "applied once");
    Check(consumer.Applied.SequenceEqual(["o5"]), "o5");
}
Console.WriteLine("all outbox checks passed");
