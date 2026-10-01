package shop.orders;

import java.util.ArrayList;
import java.util.List;

// No "public": only code in shop.orders can see this class. That's the boundary.
final class OrdersRepository {
    private final List<Order> orders = new ArrayList<>();

    Order insert(String userId, long totalKobo) {
        Order order = new Order(orders.size() + 1, userId, totalKobo);
        orders.add(order);
        return order;
    }
}
