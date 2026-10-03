// Checks: the same numbers as every other language.
using System.Globalization;
using System.Text.Json.Nodes;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var shop = JsonNode.Parse(File.ReadAllText("../shared/shop.json"))!;
var screenQuery = new Selection(("id", null), ("totalPence", null), ("customer", new(("name", null))),
    ("items", new(("quantity", null), ("product", new(("name", null))))));

var api = new RestApi(new Db(shop));
var (screen, roundTrips) = Api.OrderScreenRest(api, "o1");
Check((string?)screen["customer"]!["name"] == "Gbenga Ali", screen);
Check(api.Requests == 5 && roundTrips == 2 && api.Bytes == 912 && Api.Size(screen) == 203, (api.Requests, api.Bytes, Api.Size(screen)));
try
{
    api.Get("/refunds/r1");
    Check(false, "expected a 404");
}
catch (KeyNotFoundException)
{
    // not a resource
}

foreach (var batched in new[] { false, true })
{
    var db = new Db(shop);
    var result = Api.Execute(db.Find("orders", "o1"), screenQuery, Api.Resolvers(db, batched), "Order")[0];
    Check(JsonNode.DeepEquals(result, screen) && Api.Size(result) == 203, result);
    Check(db.Queries == (batched ? 3 : 5), (batched, db.Queries));
}

foreach (var batched in new[] { false, true })
{
    var db = new Db(shop);
    var orders = db.Find("orders", Enumerable.Range(1, 10).Select(i => $"o{i}"));
    var page = Api.Execute(orders, new Selection(("id", null), ("customer", new(("name", null))), ("items", new(("product", new(("name", null)))))),
        Api.Resolvers(db, batched), "Order");
    Check(page.Count == 10 && (string?)page[0]["customer"]!["name"] == "Gbenga Ali", page[0]);
    Check(db.Queries == (batched ? 3 : 41), (batched, db.Queries));
}

static string Hex(byte[] bytes) => Convert.ToHexString(bytes).ToLowerInvariant().Chunk(2).Select(c => new string(c)).Aggregate((a, b) => $"{a} {b}");
Check(Hex(Api.Varint(1)) == "01" && Hex(Api.Varint(150)) == "96 01" && Hex(Api.Varint(300)) == "ac 02", "varints");
Check(Hex(Api.Varint(1UL << 35)) == "80 80 80 80 80 01", "past 32 bits");
Check(Hex(Api.EncodeOrderSummary(150, "testing", 1)) == "08 96 01 12 07 74 65 73 74 69 6e 67 18 01", Hex(Api.EncodeOrderSummary(150, "testing", 1)));

Check(Api.EncodeOrderSummary(1, "Gbenga Ali", 8996).Length == 17, "protobuf");
Check(Api.Size(new JsonObject { ["id"] = 1, ["customer"] = "Gbenga Ali", ["totalPence"] = 8996 }) == 50, "json");

var c = Api.Chain(Enumerable.Repeat((0.999, 20.0), 5));
Check((c.Availability * 100).ToString("F2", CultureInfo.InvariantCulture) == "99.50" && c.SequentialMs == 100, c);
Check(Api.Chain([(1, 30), (1, 50), (1, 20)]).ParallelMs == 50, "parallel");
Console.WriteLine("all communication checks passed");
