using Shop.Domain;

namespace Shop.Adapters;

// Driven adapters: this project references the domain to implement its ports.
public sealed class InMemoryOrders : IOrderRepository
{
    public List<Order> Saved { get; } = [];
    public void Save(Order order) => Saved.Add(order);
}

public sealed class FakePayments(long declineAbove) : IPaymentGateway
{
    public bool Charge(string customerId, long kobo) => kobo <= declineAbove;
}
