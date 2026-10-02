namespace Shop.Domain;

public sealed record Order(string Id, long TotalKobo, bool Paid);

// Ports: interfaces the domain owns.
public interface IOrderRepository { void Save(Order order); }
public interface IPaymentGateway { bool Charge(string customerId, long kobo); }

public sealed class PaymentDeclinedException(string orderId) : Exception($"payment declined for {orderId}");

public static class Ordering
{
    public static Order PlaceOrder(IOrderRepository orders, IPaymentGateway payments, string id, string customerId, long kobo)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(kobo);
        if (!payments.Charge(customerId, kobo)) throw new PaymentDeclinedException(id);
        var order = new Order(id, kobo, Paid: true);
        orders.Save(order);
        return order;
    }
}
