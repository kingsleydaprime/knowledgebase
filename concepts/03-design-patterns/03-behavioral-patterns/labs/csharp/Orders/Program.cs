// C# has Observer in the language (`event`) and Iterator in the language (`yield return`).
var audit = new List<string>();
var order = new Order("o1");
order.Changed += (_, change) => audit.Add($"{change.From}->{change.To}");   // subscribe
foreach (var action in new[] { "pay", "ship", "deliver" }) order.Apply(action);

Check(audit.SequenceEqual(["Pending->Paid", "Paid->Shipped", "Shipped->Delivered"]), "listeners heard every change");
Check(order.History().Count() == 4, "history iterates lazily");

var shipped = new Order("o2");
shipped.Apply("pay"); shipped.Apply("ship");
try { shipped.Apply("cancel"); Check(false, "cancelled a shipped order"); }
catch (InvalidOperationException) { Check(shipped.Status == Status.Shipped, "status unchanged"); }
Console.WriteLine("ok: event, transition table and yield return");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

enum Status { Pending, Paid, Shipped, Delivered, Cancelled }
record Change(string OrderId, Status From, Status To);

sealed class Order(string id)
{
    private static readonly Dictionary<Status, Dictionary<string, Status>> Transitions = new()
    {
        [Status.Pending] = new() { ["pay"] = Status.Paid, ["cancel"] = Status.Cancelled },
        [Status.Paid] = new() { ["ship"] = Status.Shipped, ["cancel"] = Status.Cancelled },
        [Status.Shipped] = new() { ["deliver"] = Status.Delivered },
    };

    private readonly List<Status> _history = [Status.Pending];
    public Status Status { get; private set; } = Status.Pending;

    public event EventHandler<Change>? Changed;   // Observer, built into the language

    public void Apply(string action)
    {
        if (!Transitions.TryGetValue(Status, out var allowed) || !allowed.TryGetValue(action, out var next))
            throw new InvalidOperationException($"cannot {action} an order that is {Status}");
        var change = new Change(id, Status, next);
        Status = next;
        _history.Add(next);
        Changed?.Invoke(this, change);
    }

    public IEnumerable<Status> History()           // Iterator, built into the language
    {
        foreach (var s in _history) yield return s;
    }
}
