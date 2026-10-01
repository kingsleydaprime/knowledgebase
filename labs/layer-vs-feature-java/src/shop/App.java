package shop;

import shop.orders.Order;
import shop.orders.OrdersService;
import shop.users.UsersService;

// The composition root: builds each feature and connects them.
public final class App {
    public static OrdersService wire() {
        return new OrdersService(new UsersService());
    }

    public static void main(String[] args) {
        OrdersService orders = wire();
        Order order = orders.place("u1", 500_000);
        System.out.println(order);
        try {
            orders.place("nobody", 1);
        } catch (IllegalArgumentException e) {
            System.out.println("rejected: " + e.getMessage());
        }
    }
}
