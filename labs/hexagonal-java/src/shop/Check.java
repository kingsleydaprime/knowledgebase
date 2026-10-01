package shop;

import shop.adapters.Memory;
import shop.domain.Ports;

public final class Check {
    public static void main(String[] args) {
        var orders = new Memory.Orders();
        var order = Ports.placeOrder(orders, Memory.paymentsDecliningAbove(1_000_000), "o1", "c1", 250_000);
        assert order.paid() && orders.saved.size() == 1;
        try {
            Ports.placeOrder(orders, Memory.paymentsDecliningAbove(100), "o2", "c1", 250_000);
            throw new AssertionError("expected a decline");
        } catch (IllegalStateException expected) {
            assert orders.saved.size() == 1;
        }
        System.out.println("ok: use case runs on in-memory adapters");
    }
}
