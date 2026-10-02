// In ASP.NET Core apps this bus is usually MediatR notifications in-process, or MassTransit
// over a broker — whose consumers must be idempotent for the reason shown here.
var naiveBus = new Bus(deliverTwice: true);
var naive = new Orders(naiveBus, idempotent: false);
new Payments(naiveBus).RecordSuccess("o1", 500_000);
Check(naive.Paid["o1"] == 1_000_000, "naive consumer double-counts");

var bus = new Bus(deliverTwice: true);
var orders = new Orders(bus, idempotent: true);
var payments = new Payments(bus);
payments.RecordSuccess("o1", 500_000);
payments.RecordSuccess("o1", 250_000);
Check(orders.Paid["o1"] == 750_000, "idempotent consumer counts each event once");
Console.WriteLine("ok: naive consumer double-counts; idempotent one doesn't");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

record PaymentSucceeded(string EventId, string OrderId, long AmountKobo);

sealed class Bus(bool deliverTwice)
{
    private readonly List<Action<PaymentSucceeded>> _handlers = [];
    public void Subscribe(Action<PaymentSucceeded> handler) => _handlers.Add(handler);
    public void Publish(PaymentSucceeded e)
    {
        for (var round = 0; round < (deliverTwice ? 2 : 1); round++)
            foreach (var h in _handlers) h(e);
    }
}

sealed class Payments(Bus bus)
{
    private int _n;
    public void RecordSuccess(string orderId, long kobo) => bus.Publish(new($"evt_{++_n}", orderId, kobo));
}

sealed class Orders
{
    public Dictionary<string, long> Paid { get; } = [];
    private readonly HashSet<string> _seen = [];
    public Orders(Bus bus, bool idempotent) => bus.Subscribe(e =>
    {
        if (idempotent && !_seen.Add(e.EventId)) return;   // Add is false for a repeat
        Paid[e.OrderId] = Paid.GetValueOrDefault(e.OrderId) + e.AmountKobo;
    });
}
