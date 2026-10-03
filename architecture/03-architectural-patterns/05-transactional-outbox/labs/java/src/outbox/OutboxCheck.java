package outbox;

import java.sql.SQLException;
import java.util.List;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class OutboxCheck {
    private OutboxCheck() {}

    interface Body {
        void run() throws Exception;
    }

    private static Exception thrown(Body body) {
        try {
            body.run();
        } catch (Exception e) {
            return e;
        }
        throw new AssertionError("expected an exception");
    }

    public static void main(String[] args) throws Exception {
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            assert thrown(() -> Outbox.placeOrderSaveThenPublish(db, b, "o1", 500_000, true)) instanceof Outbox.Crash;
            assert Outbox.countOrders(db) == 1 && b.sent.isEmpty(); // the order exists, and nobody will hear of it
        }
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            var e = thrown(() -> Outbox.placeOrderPublishThenSave(db, b, "o2", -1));
            assert e instanceof SQLException && e.getMessage().contains("CHECK constraint failed") : e;
            assert Outbox.countOrders(db) == 0 && b.sent.size() == 1; // a phantom event
        }
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            Outbox.placeOrderWithOutbox(db, "o3", 500_000);
            assert Outbox.relay(db, b, false) == 1 && Outbox.relay(db, b, false) == 0;
            assert b.sent.equals(List.of(new Outbox.Event("evt-o3", "OrderPlaced", "o3"))) : b.sent;
        }
        try (var db = Outbox.openDb()) {
            var e = thrown(() -> Outbox.placeOrderWithOutbox(db, "o4", -1));
            assert e.getMessage().contains("CHECK constraint failed") : e;
            assert Outbox.countOrders(db) == 0 && Outbox.relay(db, new Outbox.FakeBroker(), false) == 0;
        }
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            Outbox.placeOrderWithOutbox(db, "o5", 500_000);
            assert thrown(() -> Outbox.relay(db, b, true)) instanceof Outbox.Crash;
            Outbox.relay(db, b, false);
            var consumer = new Outbox.IdempotentConsumer();
            assert b.sent.size() == 2 && b.sent.stream().map(consumer::handle).toList().equals(List.of("applied", "duplicate"));
            assert consumer.applied.equals(List.of("o5"));
        }
        System.out.println("all outbox checks passed");
    }
}
