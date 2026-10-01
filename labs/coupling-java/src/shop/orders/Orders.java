package shop.orders;

import shop.payments.Payments;

public final class Orders {
    public static String markPaid(int id) { return "order " + id + " paid"; }
    public static String checkout(int id) { return Payments.charge(id); }
}
