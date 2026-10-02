package orders;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

// State: an enum and an EnumMap transition table. Observer: Consumer listeners.
public final class Order implements Iterable<Order.Status> {
    public enum Status { PENDING, PAID, SHIPPED, DELIVERED, CANCELLED }
    public record Change(String orderId, Status from, Status to) {}

    private static final Map<Status, Map<String, Status>> TRANSITIONS = new EnumMap<>(Map.of(
        Status.PENDING, Map.of("pay", Status.PAID, "cancel", Status.CANCELLED),
        Status.PAID, Map.of("ship", Status.SHIPPED, "cancel", Status.CANCELLED),
        Status.SHIPPED, Map.of("deliver", Status.DELIVERED),
        Status.DELIVERED, Map.of(),
        Status.CANCELLED, Map.of()));

    public final String id;
    private Status status = Status.PENDING;
    private final List<Consumer<Change>> listeners = new ArrayList<>();
    private final List<Status> history = new ArrayList<>(List.of(Status.PENDING));

    public Order(String id) { this.id = id; }
    public Status status() { return status; }
    public void onChange(Consumer<Change> listener) { listeners.add(listener); }

    public void apply(String action) {
        Status next = TRANSITIONS.get(status).get(action);
        if (next == null) throw new IllegalStateException("cannot " + action + " an order that is " + status);
        Change change = new Change(id, status, next);
        status = next;
        history.add(next);
        listeners.forEach(l -> l.accept(change));
    }

    // Iterator: implementing Iterable lets callers use for-each.
    @Override public java.util.Iterator<Status> iterator() { return List.copyOf(history).iterator(); }
}
