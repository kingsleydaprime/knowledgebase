// The model checks, then the PostgreSQL checks through Npgsql.
using System.Text.Json.Nodes;
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

Check(Math.Ceiling(Math.Log2(1e8)) == 27, "binary");
Check(Sizing.Levels(100_000_000, 367, 400) == 4 && Sizing.Levels(1_000_000, 367, 400) == 3, "levels");

var small = new BPlusTree(3);
for (var k = 1; k <= 10; k++) small.Insert(k, $"v{k}");
Check(small.Height == 3 && small.Root.Keys.SequenceEqual([7]), small.Height);
Check(small.Search(7) == ("v7", 3) && small.Search(99) == (null, 3), small.Search(7));
var range = small.Range(4, 8);
Check(range.Values.SequenceEqual(["v4", "v5", "v6", "v7", "v8"]) && range.Pages == 6, range.Pages);

var big = new BPlusTree(400);
for (var i = 0; i < 1_000_000; i++) big.Insert((int)((long)i * 7919 % 1_000_000), ""); // i * 7919 overflows an int
Check(big.Height == 3 && big.Search(424_242).Pages == 3, big.Height);

string[] index = ["a", "b", "c"];
List<string> Usable(string[] eq, string[] ranges) => Sizing.UsablePrefix(index, eq.ToHashSet(), ranges.ToHashSet());
Check(Usable(["a"], []).SequenceEqual(["a"]) && Usable(["a", "b", "c"], []).SequenceEqual(index) && Usable(["b"], []).Count == 0, "prefix");
Check(Usable(["a", "c"], []).SequenceEqual(["a"]) && Usable(["b"], ["a"]).SequenceEqual(["a"]) && Usable(["a"], ["b"]).SequenceEqual(["a", "b"]), "prefix");

// Npgsql over TCP: the container shares the host's network, where the throwaway database listens on 127.0.0.1.
await using var db = new NpgsqlConnection($"Host=127.0.0.1;Port={Environment.GetEnvironmentVariable("PGPORT")};Username=postgres;Database=postgres");
await db.OpenAsync();
async Task Run(string sql)
{
    await using var command = new NpgsqlCommand(sql, db);
    await command.ExecuteNonQueryAsync();
}
async Task<List<JsonNode>> Explain(string sql)
{
    await using var command = new NpgsqlCommand($"EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}", db);
    var plan = JsonNode.Parse((string)(await command.ExecuteScalarAsync())!)![0]!["Plan"]!; // json arrives as text
    var nodes = new List<JsonNode>();
    void Collect(JsonNode node)
    {
        nodes.Add(node);
        foreach (var child in node["Plans"]?.AsArray() ?? []) Collect(child!);
    }
    Collect(plan);
    return nodes;
}
static int Pages(List<JsonNode> plan) => (int)plan[0]["Shared Hit Blocks"]! + (int)plan[0]["Shared Read Blocks"]!;

foreach (var statement in File.ReadAllText("../shared/orders.sql").Split(";\n"))
    if (statement.Split('\n').Any(line => line.Trim() != "" && !line.TrimStart().StartsWith("--"))) await Run(statement); // one at a time

await using (var level = new NpgsqlCommand("SELECT level FROM bt_metap('orders_pkey')", db))
    Check((long)(await level.ExecuteScalarAsync())! == 2, "level"); // bigint arrives as long
var lookup = await Explain("SELECT * FROM orders WHERE id = 424242");
Check((string?)lookup[0]["Node Type"] == "Index Scan" && Pages(lookup) == 4, Pages(lookup));

await Run("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)");
var both = await Explain("SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'");
Check(both.Any(n => (string?)n["Index Name"] == "orders_customer_created"), "composite used");
var hour = await Explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'");
Check((string?)hour[0]["Node Type"] == "Seq Scan", hour[0]["Node Type"]);
await Run("DROP INDEX orders_customer_created");

await Run("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)");
await Run("VACUUM orders");
var clean = await Explain("SELECT total FROM orders WHERE customer_id = 42");
Check((string?)clean[0]["Node Type"] == "Index Only Scan" && (int)clean[0]["Heap Fetches"]! == 0, clean[0]["Heap Fetches"]);
await Run("UPDATE orders SET total = total + 1 WHERE customer_id = 42");
Check((int)(await Explain("SELECT total FROM orders WHERE customer_id = 42"))[0]["Heap Fetches"]! > 0, "dirty");
Console.WriteLine("all b-tree checks passed");
