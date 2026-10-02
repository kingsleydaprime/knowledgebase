package shop.orders;

import shop.users.UsersService;

// Public: the orders feature's API. Its repository stays package-private.
public final class OrdersService {
    private final UsersService users;
    private final OrdersRepository repository = new OrdersRepository();

    public OrdersService(UsersService users) {
        this.users = users;
    }

    public Order place(String userId, long totalKobo) {
        if (!users.exists(userId)) {
            throw new IllegalArgumentException("unknown user: " + userId);
        }
        return repository.insert(userId, totalKobo);
    }
}
