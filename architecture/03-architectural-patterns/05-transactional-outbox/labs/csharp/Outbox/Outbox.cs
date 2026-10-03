// The dual-write problem, and the transactional outbox that fixes it, on a real SQLite database.
// The same scenarios as the JavaScript lab.
using System.Text.Json;
using Microsoft.Data.Sqlite;

public record Event(string EventId, string Type, string OrderId);

/// <summary>Stands in for RabbitMQ, Kafka or SQS: it records what it was sent.</summary>
public sealed class FakeBroker
{
    public List<Event> Sent { get; } = [];
    public void Publish(Event e) => Sent.Add(e);
}

public sealed class CrashException(string message) : Exception(message);

public static class Outbox
{
    public static SqliteConnection OpenDb()
    {
        var db = new SqliteConnection("Data Source=:memory:"); // the database lives as long as this connection is open
        db.Open();
        Execute(db, """
            CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0));
            CREATE TABLE outbox (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              event_id TEXT NOT NULL UNIQUE,
              type TEXT NOT NULL,
              payload TEXT NOT NULL,
              published_at TEXT
            );
            """);
        return db;
    }

    private static int Execute(SqliteConnection db, string sql, params (string Name, object Value)[] args)
    {
        using var command = db.CreateCommand(); // joins the connection's current transaction, if there is one
        command.CommandText = sql;
        foreach (var (name, value) in args) command.Parameters.AddWithValue(name, value);
        return command.ExecuteNonQuery();
    }

    public static long CountOrders(SqliteConnection db)
    {
        using var command = db.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM orders";
        return (long)command.ExecuteScalar()!;
    }

    private static void InsertOrder(SqliteConnection db, string id, int totalKobo) =>
        Execute(db, "INSERT INTO orders (id, total_kobo) VALUES ($id, $total)", ("$id", id), ("$total", totalKobo));

    // ---- The dual write: two systems, no shared transaction ----

    public static void PlaceOrderSaveThenPublish(SqliteConnection db, FakeBroker b, string id, int totalKobo, bool crashBetween = false)
    {
        InsertOrder(db, id, totalKobo);
        if (crashBetween) throw new CrashException("process died after the commit");
        b.Publish(new($"evt-{id}", "OrderPlaced", id));
    }

    public static void PlaceOrderPublishThenSave(SqliteConnection db, FakeBroker b, string id, int totalKobo)
    {
        b.Publish(new($"evt-{id}", "OrderPlaced", id));
        InsertOrder(db, id, totalKobo);
    }

    // ---- The outbox: the event is written in the SAME transaction as the order ----

    public static void PlaceOrderWithOutbox(SqliteConnection db, string id, int totalKobo)
    {
        using var tx = db.BeginTransaction(); // disposed without Commit, it rolls back
        InsertOrder(db, id, totalKobo);
        Execute(db, "INSERT INTO outbox (event_id, type, payload) VALUES ($id, $type, $payload)",
            ("$id", $"evt-{id}"), ("$type", "OrderPlaced"), ("$payload", JsonSerializer.Serialize(new { orderId = id })));
        tx.Commit();
    }

    /// <summary>Publish first, then mark as sent. A crash in between means the event is sent again: at least once.</summary>
    public static int Relay(SqliteConnection db, FakeBroker b, bool crashBeforeMark = false)
    {
        var pending = new List<(long Seq, string EventId, string Type, string Payload)>();
        using (var command = db.CreateCommand())
        {
            command.CommandText = "SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq";
            using var reader = command.ExecuteReader();
            while (reader.Read()) pending.Add((reader.GetInt64(0), reader.GetString(1), reader.GetString(2), reader.GetString(3)));
        }
        foreach (var row in pending)
        {
            var orderId = JsonDocument.Parse(row.Payload).RootElement.GetProperty("orderId").GetString()!;
            b.Publish(new(row.EventId, row.Type, orderId));
            if (crashBeforeMark) throw new CrashException("relay died after publishing, before marking");
            Execute(db, "UPDATE outbox SET published_at = datetime('now') WHERE seq = $seq", ("$seq", row.Seq));
        }
        return pending.Count;
    }
}

public sealed class IdempotentConsumer
{
    private readonly HashSet<string> _seen = [];
    public List<string> Applied { get; } = [];

    public string Handle(Event e)
    {
        if (!_seen.Add(e.EventId)) return "duplicate"; // Add returns false if it was already there
        Applied.Add(e.OrderId);
        return "applied";
    }
}
