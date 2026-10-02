package shop.domain;

// The domain: rules and the ports it owns. Nothing here imports shop.adapters.
public final class Ports {
    public record Order(String id, long totalKobo, boolean paid) {}
    public interface OrderRepository { void save(Order order); }
    public interface PaymentGateway { boolean charge(String customerId, long kobo); }

    public static Order placeOrder(OrderRepository orders, PaymentGateway payments, String id, String customerId, long kobo) {
        if (kobo <= 0) throw new IllegalArgumentException("total must be positive");
        if (!payments.charge(customerId, kobo)) throw new IllegalStateException("payment declined");
        var order = new Order(id, kobo, true);
        orders.save(order);
        return order;
    }
}
