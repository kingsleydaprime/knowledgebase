package shop.adapters;

import java.util.ArrayList;
import java.util.List;
import shop.domain.Ports;

// Driven adapters: they import the domain to implement its ports.
public final class Memory {
    public static final class Orders implements Ports.OrderRepository {
        public final List<Ports.Order> saved = new ArrayList<>();
        public void save(Ports.Order order) { saved.add(order); }
    }

    public static Ports.PaymentGateway paymentsDecliningAbove(long limit) {
        return (customerId, kobo) -> kobo <= limit;
    }
}
