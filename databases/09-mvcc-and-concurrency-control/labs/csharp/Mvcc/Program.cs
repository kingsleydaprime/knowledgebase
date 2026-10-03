// MVCC through Npgsql: snapshots, blocked vacuum and a deadlock.
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var connectionString = $"Host=127.0.0.1;Port={Environment.GetEnvironmentVariable("PGPORT")};Username=postgres;Database=postgres";
await using var a = new NpgsqlConnection(connectionString);
await using var b = new NpgsqlConnection(connectionString);
await using var watcher = new NpgsqlConnection(connectionString);
await Task.WhenAll(a.OpenAsync(), b.OpenAsync(), watcher.OpenAsync());

static async Task Run(NpgsqlConnection c, string sql)
{
    await using var command = new NpgsqlCommand(sql, c);
    await command.ExecuteNonQueryAsync();
}

static async Task<long> Number(NpgsqlConnection c, string sql)
{
    await using var command = new NpgsqlCommand(sql, c);
    return Convert.ToInt64(await command.ExecuteScalarAsync());
}

static async Task<string?> Failure(Func<Task> action)
{
    try
    {
        await action();
        return null;
    }
    catch (PostgresException e)
    {
        return e.SqlState;
    }
}

const string Balance = "SELECT balance FROM accounts WHERE id = 1";
async Task Reset()
{
    await Run(a, """
        CREATE EXTENSION IF NOT EXISTS pgstattuple;
        DROP TABLE IF EXISTS accounts;
        CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
        INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i
        """);
    await Run(a, "VACUUM accounts"); // alone: VACUUM can't run inside a multi-statement call's transaction
}

await Reset(); // readers don't block writers
await Run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
Check(await Number(a, Balance) == 100, "before");
await Run(b, "SET lock_timeout = '100ms'");
await Run(b, "UPDATE accounts SET balance = 50 WHERE id = 1");
Check(await Number(a, Balance) == 100, "a's snapshot");
await Run(a, "COMMIT");
Check(await Number(a, Balance) == 50, "after");

await Reset(); // writers block writers
await Run(a, "BEGIN");
await Run(a, "UPDATE accounts SET balance = 90 WHERE id = 1");
Check(await Failure(() => Run(b, "UPDATE accounts SET balance = 80 WHERE id = 1")) == PostgresErrorCodes.LockNotAvailable, "55P03");
await Run(a, "COMMIT");

await Reset(); // an open snapshot stops vacuum
await Run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
await Run(a, "SELECT 1");
await Run(b, "UPDATE accounts SET balance = balance + 1");
await Run(b, "VACUUM accounts");
Check(await Number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 1000, "kept");
await Run(a, "COMMIT");
await Run(b, "VACUUM accounts");
Check(await Number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 0, "removed");

await Reset(); // a deadlock: exactly one victim
await Run(b, "RESET lock_timeout");
foreach (var c in new[] { a, b }) await Run(c, "SET deadlock_timeout = '100ms'");
await Run(a, "BEGIN");
await Run(b, "BEGIN");
await Run(a, "UPDATE accounts SET balance = 1 WHERE id = 1");
await Run(b, "UPDATE accounts SET balance = 2 WHERE id = 2");
var aWantsRow2 = Failure(() => Run(a, "UPDATE accounts SET balance = 1 WHERE id = 2")); // started, not awaited: it's waiting
for (var i = 0; ; i++)
{
    await using var command = new NpgsqlCommand($"SELECT wait_event_type FROM pg_stat_activity WHERE pid = {a.ProcessID}", watcher);
    if (await command.ExecuteScalarAsync() is "Lock") break;
    Check(i < 500, "a never waited");
    await Task.Delay(10);
}
var bResult = await Failure(() => Run(b, "UPDATE accounts SET balance = 2 WHERE id = 1"));
var aResult = await aWantsRow2;
Check(new[] { aResult, bResult }.Count(code => code == PostgresErrorCodes.DeadlockDetected) == 1, (aResult, bResult));
await Run(a, "ROLLBACK");
await Run(b, "ROLLBACK");
Console.WriteLine("all mvcc checks passed");
