using Shop.Adapters;
using Shop.Domain;

var orders = new InMemoryOrders();
var order = Ordering.PlaceOrder(orders, new FakePayments(1_000_000), "o1", "c1", 250_000);
if (!order.Paid || orders.Saved.Count != 1) throw new Exception("FAIL: paid order");
try
{
    Ordering.PlaceOrder(orders, new FakePayments(100), "o2", "c1", 250_000);
    throw new Exception("FAIL: expected a decline");
}
catch (PaymentDeclinedException) when (orders.Saved.Count == 1) { }
Console.WriteLine("ok: use case runs on in-memory adapters");
