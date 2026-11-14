package shop.payments;

import shop.orders.Orders;

public final class Payments {
    public static String charge(int id) { return Orders.markPaid(id); } // reaches back: a cycle
}
