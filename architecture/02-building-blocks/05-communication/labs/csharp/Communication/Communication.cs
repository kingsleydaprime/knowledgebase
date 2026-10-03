// What an API style costs, counted: REST requests and bytes, a GraphQL-style query with the N+1 problem and
// batching, Protocol Buffers' varints, and synchronous chains. The same numbers as the TypeScript lab.
using System.Text;
using System.Text.Json.Nodes;

/// <summary>A tiny shop database that counts its queries.</summary>
public sealed class Db
{
    private readonly Dictionary<string, Dictionary<string, JsonNode>> _tables = [];
    public int Queries { get; private set; }

    public Db(JsonNode shop)
    {
        foreach (var table in new[] { "customers", "products", "orders" })
            _tables[table] = shop[table]!.AsArray().ToDictionary(r => (string)r!["id"]!, r => r!);
    }

    /// <summary>One query for any number of rows: SELECT … WHERE id IN (…).</summary>
    public List<JsonNode> Find(string table, params IEnumerable<string> ids)
    {
        Queries++;
        return ids.Select(id => _tables[table][id]).ToList();
    }
}

/// <summary>One whole resource per URL. Counts requests and bytes sent.</summary>
public sealed class RestApi(Db db)
{
    public int Requests { get; private set; }
    public int Bytes { get; private set; }

    public JsonNode Get(string path)
    {
        var parts = path.Split('/'); // "/orders/o1" → "", "orders", "o1"
        if (parts.Length != 3 || parts[1] is not ("orders" or "customers" or "products")) throw new KeyNotFoundException($"404 {path}");
        var body = db.Find(parts[1], parts[2])[0];
        Requests++;
        Bytes += Api.Size(body);
        return body;
    }
}

/// <summary>Fields wanted, in order: null for a plain field, a nested selection to look inside.</summary>
public sealed record Selection(params (string Field, Selection? Sub)[] Fields);

public static class Api
{
    /// <summary>Compact JSON, like JSON.stringify. The default encoder also escapes non-ASCII, which these strings don't have.</summary>
    public static int Size(JsonNode node) => node.ToJsonString().Length;

    /// <summary>The order (round trip 1), then its customer and products together (round trip 2).</summary>
    public static (JsonObject Screen, int RoundTrips) OrderScreenRest(RestApi api, string orderId)
    {
        var order = api.Get($"/orders/{orderId}");
        var customer = api.Get($"/customers/{order["customerId"]}");
        var items = new JsonArray();
        foreach (var item in order["items"]!.AsArray())
        {
            var product = api.Get($"/products/{item!["productId"]}");
            // A node can belong to only one parent, so values copied into the screen are cloned.
            items.Add(new JsonObject { ["quantity"] = item["quantity"]!.DeepClone(), ["product"] = new JsonObject { ["name"] = product["name"]!.DeepClone() } });
        }
        var screen = new JsonObject
        {
            ["id"] = order["id"]!.DeepClone(),
            ["totalPence"] = order["totalPence"]!.DeepClone(),
            ["customer"] = new JsonObject { ["name"] = customer["name"]!.DeepClone() },
            ["items"] = items,
        };
        return (screen, 2);
    }

    private static readonly Dictionary<string, string> FieldTypes = new() { ["Order.customer"] = "Customer", ["Order.items"] = "Item", ["Item.product"] = "Product" };

    /// <summary>Runs a selection over every object at one level together, so each resolver sees the whole level.</summary>
    public static List<JsonObject> Execute(IReadOnlyList<JsonNode> values, Selection selection,
        IReadOnlyDictionary<string, Func<IReadOnlyList<JsonNode>, List<JsonNode>>> resolvers, string type)
    {
        var outs = values.Select(_ => new JsonObject()).ToList();
        foreach (var (field, sub) in selection.Fields)
        {
            var children = resolvers.TryGetValue($"{type}.{field}", out var resolve) ? resolve(values) : values.Select(v => v[field]!).ToList();
            var childType = FieldTypes.GetValueOrDefault($"{type}.{field}", "");
            if (sub is null)
            {
                for (var i = 0; i < outs.Count; i++) outs[i][field] = children[i].DeepClone();
            }
            else if (children.Count > 0 && children[0] is JsonArray) // a list field: all its elements form the next level
            {
                var flat = children.SelectMany(c => c.AsArray()).Select(e => e!).ToList();
                var done = Execute(flat, sub, resolvers, childType).GetEnumerator();
                for (var i = 0; i < outs.Count; i++)
                {
                    var list = new JsonArray();
                    for (var n = 0; n < children[i].AsArray().Count && done.MoveNext(); n++) list.Add(done.Current);
                    outs[i][field] = list;
                }
            }
            else
            {
                var done = Execute(children, sub, resolvers, childType);
                for (var i = 0; i < outs.Count; i++) outs[i][field] = done[i];
            }
        }
        return outs;
    }

    /// <summary>One query per parent (the N+1 problem), or one query for the whole level.</summary>
    public static Dictionary<string, Func<IReadOnlyList<JsonNode>, List<JsonNode>>> Resolvers(Db db, bool batched)
    {
        Func<IReadOnlyList<JsonNode>, List<JsonNode>> Make(string table, string key) => parents =>
        {
            if (!batched) return parents.Select(p => db.Find(table, (string)p[key]!)[0]).ToList();
            var ids = parents.Select(p => (string)p[key]!).Distinct().ToList(); // each ID once, in first-seen order
            var rows = ids.Zip(db.Find(table, ids)).ToDictionary(r => r.First, r => r.Second);
            return parents.Select(p => rows[(string)p[key]!]).ToList();
        };
        return new() { ["Order.customer"] = Make("customers", "customerId"), ["Item.product"] = Make("products", "productId") };
    }

    /// <summary>Base-128, low bits first, top bit set if more follow.</summary>
    public static byte[] Varint(ulong n)
    {
        var bytes = new List<byte>();
        for (; n >= 0x80; n >>= 7) bytes.Add((byte)(n & 0x7f | 0x80));
        bytes.Add((byte)n);
        return [.. bytes];
    }

    public static byte[] EncodeOrderSummary(ulong id, string customer, ulong totalPence)
    {
        var text = Encoding.UTF8.GetBytes(customer); // bytes, not chars: protobuf strings are UTF-8
        return [.. Varint(1 << 3), .. Varint(id), .. Varint(2 << 3 | 2), .. Varint((ulong)text.Length), .. text, .. Varint(3 << 3), .. Varint(totalPence)];
    }

    public static (double Availability, double SequentialMs, double ParallelMs) Chain(IEnumerable<(double Availability, double Ms)> calls) =>
        calls.Aggregate((1.0, 0.0, 0.0), (c, call) => (c.Item1 * call.Availability, c.Item2 + call.Ms, Math.Max(c.Item3, call.Ms)));
}
