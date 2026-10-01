package orders;

import java.util.ArrayList;
import java.util.List;

public final class Check {
    public static void main(String[] args) {
        List<String> audit = new ArrayList<>();
        Order order = new Order("o1");
        order.onChange(c -> audit.add(c.from() + "->" + c.to()));
        for (String a : List.of("pay", "ship", "deliver")) order.apply(a);
        assert audit.equals(List.of("PENDING->PAID", "PAID->SHIPPED", "SHIPPED->DELIVERED")) : audit;
        List<Order.Status> seen = new ArrayList<>();
        for (Order.Status s : order) seen.add(s);
        assert seen.size() == 4;

        Order shipped = new Order("o2");
        shipped.apply("pay"); shipped.apply("ship");
        try { shipped.apply("cancel"); throw new AssertionError("cancelled a shipped order"); }
        catch (IllegalStateException expected) { assert shipped.status() == Order.Status.SHIPPED; }
        System.out.println("ok: transitions, listeners and for-each history");
    }
}
