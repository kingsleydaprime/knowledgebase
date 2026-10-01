using Shop.Users;

namespace Shop.Orders;

// public: the orders feature's API. Its repository stays internal.
public sealed class OrdersService(UsersService users)
{
    private readonly OrdersRepository _repository = new();

    public Order? Place(string userId, long totalKobo) =>
        users.Exists(userId) ? _repository.Insert(userId, totalKobo) : null;
}
