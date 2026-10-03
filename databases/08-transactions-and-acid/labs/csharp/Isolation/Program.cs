// The anomalies and their fixes through Npgsql, two connections stepped one statement at a time.
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var connectionString = $"Host=127.0.0.1;Port={Environment.GetEnvironmentVariable("PGPORT")};Username=postgres;Database=postgres";
await using var a = new NpgsqlConnection(connectionString);
await using var b = new NpgsqlConnection(connectionString);
await a.OpenAsync();
await b.OpenAsync();

static async Task Run(NpgsqlConnection c, string sql, params object[] values)
{
    await using var command = new NpgsqlCommand(sql, c);
    foreach (var v in values) command.Parameters.Add(new NpgsqlParameter { Value = v }); // $1, $2, … in order
    await command.ExecuteNonQueryAsync();
}

static async Task<long> Number(NpgsqlConnection c, string sql)
{
    await using var command = new NpgsqlCommand(sql, c);
    return Convert.ToInt64(await command.ExecuteScalarAsync());
}

// The SQLSTATE an action fails with, or null. Npgsql names the codes in PostgresErrorCodes.
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

// Runs work again while PostgreSQL says the transaction should be retried, backing off each time.
static async Task WithRetry(int attempts, Func<Task> work)
{
    for (var attempt = 1; ; attempt++)
    {
        try
        {
            await work();
            return;
        }
        catch (PostgresException e) when (attempt < attempts && e.SqlState is PostgresErrorCodes.SerializationFailure or PostgresErrorCodes.DeadlockDetected)
        {
            await Task.Delay(10 << attempt);
        }
    }
}

const string Balance = "SELECT balance FROM accounts WHERE id = 1";
async Task Reset() => await Run(a, """
    DROP TABLE IF EXISTS accounts, doctors;
    CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
    INSERT INTO accounts VALUES (1, 100), (2, 50);
    CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
    INSERT INTO doctors VALUES ('alice', true), ('bob', true)
    """);

await Reset(); // a lost update at Read Committed
await Run(a, "BEGIN");
await Run(b, "BEGIN");
var (seenA, seenB) = (await Number(a, Balance), await Number(b, Balance));
await Run(a, "UPDATE accounts SET balance = $1 WHERE id = 1", (int)seenA - 10);
await Run(a, "COMMIT");
await Run(b, "UPDATE accounts SET balance = $1 WHERE id = 1", (int)seenB - 20);
await Run(b, "COMMIT");
Check(await Number(a, Balance) == 80, "lost update");

await Reset(); // Repeatable Read refuses the second write
await Run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
await Run(b, "BEGIN ISOLATION LEVEL REPEATABLE READ");
var seen = await Number(b, Balance);
await Run(a, "UPDATE accounts SET balance = balance - 10 WHERE id = 1");
await Run(a, "COMMIT");
Check(await Failure(() => Run(b, "UPDATE accounts SET balance = $1 WHERE id = 1", (int)seen - 20)) == PostgresErrorCodes.SerializationFailure, "40001");
await Run(b, "ROLLBACK");

await Reset(); // FOR UPDATE makes the second reader wait
await Run(a, "BEGIN");
await Run(a, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
await Run(b, "BEGIN");
await Run(b, "SET LOCAL lock_timeout = '100ms'");
Check(await Failure(() => Run(b, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")) == PostgresErrorCodes.LockNotAvailable, "55P03");
await Run(b, "ROLLBACK");
await Run(a, "COMMIT");

await Reset(); // write skew: Serializable aborts one, and the retry keeps the rule
async Task GoOffCall(NpgsqlConnection c, string name)
{
    await Run(c, "BEGIN ISOLATION LEVEL SERIALIZABLE");
    if (await Number(c, "SELECT count(*) FROM doctors WHERE on_call") >= 2) await Run(c, "UPDATE doctors SET on_call = false WHERE name = $1", name);
}
await GoOffCall(a, "alice");
await GoOffCall(b, "bob");
await Run(a, "COMMIT");
Check(await Failure(() => Run(b, "COMMIT")) == PostgresErrorCodes.SerializationFailure, "commit refused");
await WithRetry(5, async () =>
{
    try
    {
        await GoOffCall(b, "bob");
        await Run(b, "COMMIT");
    }
    catch (PostgresException)
    {
        await Run(b, "ROLLBACK");
        throw;
    }
});
Check(await Number(a, "SELECT count(*) FROM doctors WHERE on_call AND name = 'bob'") == 1 && await Number(a, "SELECT count(*) FROM doctors WHERE on_call") == 1, "bob stays");
Console.WriteLine("all isolation checks passed");
