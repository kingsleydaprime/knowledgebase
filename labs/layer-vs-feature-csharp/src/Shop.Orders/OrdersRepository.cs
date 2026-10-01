namespace Shop.Orders;

public sealed record Order(int Id, string UserId, long TotalKobo);

// internal: visible inside the Shop.Orders assembly only. That's the boundary.
internal sealed class OrdersRepository
{
    private readonly List<Order> _orders = [];

    public Order Insert(string userId, long totalKobo)
    {
        var order = new Order(_orders.Count + 1, userId, totalKobo);
        _orders.Add(order);
        return order;
    }
}
