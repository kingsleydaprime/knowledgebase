// The model checks, then the PostgreSQL checks through Npgsql.
using System.Text.Json.Nodes;
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var orders = Enumerable.Range(0, 10_000).Select(i => new Row(1 + i % 1_000, $"order {i}")).ToList();
var customers = Enumerable.Range(1, 1_000).Select(c => new Row(c, $"customer {c}")).ToList();
var sortedOrders = orders.OrderBy(o => o.Key).ToList(); // OrderBy is stable
static List<string> Canonical(List<(string, string)> rows) => rows.Select(r => $"{r.Item1}|{r.Item2}").Order(StringComparer.Ordinal).ToList();

var expected = Canonical(Joins.NestedLoop(orders, customers).Rows);
Check(expected.Count == 10_000, expected.Count);
Check(Canonical(Joins.IndexNestedLoop(orders, customers).Rows).SequenceEqual(expected), "index nested loop");
Check(Canonical(Joins.HashJoin(orders, customers).Rows).SequenceEqual(expected), "hash");
Check(Canonical(Joins.MergeJoin(sortedOrders, customers).Rows).SequenceEqual(expected), "merge");

long[] work = [Joins.NestedLoop(orders, customers).Work, Joins.IndexNestedLoop(orders, customers).Work, Joins.HashJoin(orders, customers).Work, Joins.MergeJoin(sortedOrders, customers).Work];
Check(work.SequenceEqual([10_000_000L, 99_780, 11_000, 10_999]), string.Join(", ", work));
var one = orders.Where(o => o.Key == 42).ToList();
Check(Joins.IndexNestedLoop(one, customers).Work == 100 && Joins.HashJoin(one, customers).Work == 1_010, "one customer");
Check(Math.Round(Joins.IndependentEstimate(30_000, 0.1, 0.3)) == 900 && Math.Round(Joins.IndependentEstimate(30_000, 0.1)) == 3_000, "estimates");
Check(Joins.RowsReadForPage(100_000, 20, false) == 100_020 && Joins.RowsReadForPage(100_000, 20, true) == 20, "pagination");

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
    var nodes = new List<JsonNode>();
    void Collect(JsonNode node)
    {
        nodes.Add(node);
        foreach (var child in node["Plans"]?.AsArray() ?? []) Collect(child!);
    }
    Collect(JsonNode.Parse((string)(await command.ExecuteScalarAsync())!)![0]!["Plan"]!);
    return nodes;
}
async Task<int> HashBatches() =>
    (int)(await Explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id")).First(n => (string?)n["Node Type"] == "Hash")["Hash Batches"]!;

foreach (var statement in File.ReadAllText("../shared/shop.sql").Split(";\n"))
    if (statement.Split('\n').Any(line => line.Trim() != "" && !line.TrimStart().StartsWith("--"))) await Run(statement);

Check(await HashBatches() == 1, "one batch");
await Run("SET work_mem = '64kB'");
Check(await HashBatches() == 16, "sixteen batches");
await Run("RESET work_mem");

var query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
var before = (await Explain(query))[0];
Check((int)before["Plan Rows"]! == 900 && (double)before["Actual Rows"]! == 3000, before["Plan Rows"]); // actual rows is a decimal in PostgreSQL 18
await Run("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses");
await Run("ANALYZE addresses");
Check((int)(await Explain(query))[0]["Plan Rows"]! == 3000, "with statistics");

Check((double)(await Explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20"))[1]["Actual Rows"]! == 100_020, "offset");
Check((double)(await Explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20"))[1]["Actual Rows"]! == 20, "keyset");
Console.WriteLine("all join checks passed");
