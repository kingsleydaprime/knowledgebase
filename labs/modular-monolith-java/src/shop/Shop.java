package shop;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;

// In Spring: payments calls ApplicationEventPublisher.publishEvent(...), orders has an
// @EventListener (or @ApplicationModuleListener with Spring Modulith). Same shape, plain Java here.
public final class Shop {
    public record PaymentSucceeded(String eventId, String orderId, long amountKobo) {}

    public static class InProcessBus {
        private final List<Consumer<PaymentSucceeded>> handlers = new ArrayList<>();
        public void subscribe(Consumer<PaymentSucceeded> h) { handlers.add(h); }
        public void publish(PaymentSucceeded e) { handlers.forEach(h -> h.accept(e)); }
    }

    // What a broker may do: deliver every event twice.
    public static final class AtLeastOnceBus extends InProcessBus {
        @Override public void publish(PaymentSucceeded e) { super.publish(e); super.publish(e); }
    }

    public static final class Payments {
        private final InProcessBus bus;
        private int n;
        public Payments(InProcessBus bus) { this.bus = bus; }
        public void recordSuccess(String orderId, long kobo) { bus.publish(new PaymentSucceeded("evt_" + ++n, orderId, kobo)); }
    }

    public static final class Orders {
        public final Map<String, Long> paid = new HashMap<>();
        private final Set<String> seen = new HashSet<>();
        public Orders(InProcessBus bus, boolean idempotent) {
            bus.subscribe(e -> {
                if (idempotent && !seen.add(e.eventId())) return;   // add() is false if already seen
                paid.merge(e.orderId(), e.amountKobo(), Long::sum);
            });
        }
    }

    public static void main(String[] args) {
        var naiveBus = new AtLeastOnceBus();
        var naive = new Orders(naiveBus, false);
        new Payments(naiveBus).recordSuccess("o1", 500_000);
        assert naive.paid.get("o1") == 1_000_000 : naive.paid;

        var bus = new AtLeastOnceBus();
        var orders = new Orders(bus, true);
        var payments = new Payments(bus);
        payments.recordSuccess("o1", 500_000);
        payments.recordSuccess("o1", 250_000);
        assert orders.paid.get("o1") == 750_000 : orders.paid;
        System.out.println("ok: naive consumer double-counts; idempotent one doesn't");
    }
}
