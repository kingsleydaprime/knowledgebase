package messaging;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class MessagingCheck {
    private MessagingCheck() {}

    private static Messaging.Broker broker(AtomicLong clock) {
        return new Messaging.Broker(clock::get, 30_000, 3);
    }

    private static void until(BooleanSupplier done) throws InterruptedException {
        while (!done.getAsBoolean()) Thread.sleep(1);
    }

    public static void main(String[] args) throws Exception {
        var b = broker(new AtomicLong());
        b.subscribe("orders", "invoices");
        b.subscribe("orders", "analytics");
        b.publish("orders", "order 1", null);
        b.publish("orders", "order 2", null);
        assert b.receive("invoices").orElseThrow().body().equals("order 1");
        assert b.receive("invoices").orElseThrow().body().equals("order 2");
        assert b.receive("invoices").isEmpty();
        assert b.receive("analytics").orElseThrow().body().equals("order 1");
        b.publish("refunds", "refund 1", null);
        assert b.depth("invoices") + b.depth("analytics") == 4;

        var clock = new AtomicLong();
        var r = broker(clock);
        r.subscribe("orders", "invoices");
        r.publish("orders", "order 1", null);
        assert r.receive("invoices").orElseThrow().attempt() == 1 && r.receive("invoices").isEmpty();
        clock.set(30_000);
        assert r.receive("invoices").orElseThrow().attempt() == 2;
        clock.set(60_000);
        assert r.receive("invoices").orElseThrow().attempt() == 3;
        clock.set(90_000);
        assert r.receive("invoices").isEmpty() && r.deadLetters("invoices").equals(List.of("order 1")) && r.depth("invoices") == 0;

        for (boolean safe : new boolean[] {false, true}) {
            var t = new AtomicLong();
            var p = broker(t);
            p.subscribe("orders", "payments");
            p.publish("orders", "charge £40 for order 1", null);
            var charges = new AtomicInteger();
            Consumer<String> charge = body -> charges.incrementAndGet();
            var once = Messaging.idempotent(charge, new HashSet<>());
            Consumer<Messaging.Delivery> handle = safe ? once::apply : d -> charge.accept(d.body());
            handle.accept(p.receive("payments").orElseThrow()); // charged, then a crash before the ack
            t.set(30_000);
            var again = p.receive("payments").orElseThrow();
            handle.accept(again);
            p.ack("payments", again.id());
            assert charges.get() == (safe ? 1 : 2) : safe + ": " + charges.get();
        }

        int[] spike = new int[60];
        for (int i = 0; i < 60; i++) spike[i] = i < 10 ? 300 : 20;
        assert Messaging.levelLoad(spike, 100).equals(new Messaging.Levelled(2_000, 2_000, 2_000, 35, 20));
        var four = Messaging.levelLoad(spike, 200);
        assert four.peakDepth() == 1_000 && four.clearedAfterSeconds() == 16 && four.maxWaitSeconds() == 5 : four;

        var c = new AtomicLong();
        var s = broker(c);
        s.subscribe("orders", "shipping");
        for (String e : List.of("created", "paid", "shipped")) s.publish("orders", "order 7 " + e, "order-7");
        List<String> seen = new ArrayList<>();
        for (boolean fail : new boolean[] {false, true, false}) {
            var d = s.receive("shipping").orElseThrow();
            if (!fail) {
                seen.add(d.body());
                s.ack("shipping", d.id());
            }
        }
        c.set(30_000);
        seen.add(s.receive("shipping").orElseThrow().body());
        assert seen.equals(List.of("order 7 created", "order 7 shipped", "order 7 paid")) : seen;

        var log = new Messaging.PartitionedLog(4);
        for (String e : List.of("created", "paid", "shipped")) log.append("order-7", "order 7 " + e);
        int part = Messaging.partitionFor("order-7", 4);
        List<String> inOrder = new ArrayList<>();
        boolean failedOnce = false;
        for (var m = log.poll("shipping", part); m.isPresent(); m = log.poll("shipping", part)) {
            if (m.get().endsWith("paid") && !failedOnce) {
                failedOnce = true; // no commit: the same message comes back
                continue;
            }
            inOrder.add(m.get());
            log.commit("shipping", part);
        }
        assert inOrder.equals(List.of("order 7 created", "order 7 paid", "order 7 shipped")) : inOrder;
        assert log.poll("analytics", part).orElseThrow().equals("order 7 created");

        int[] counts = new int[4];
        for (int i = 0; i < 10_000; i++) counts[Messaging.partitionFor("order-" + i, 4)]++;
        for (int n : counts) assert Math.abs(n - 2_500) < 200 : java.util.Arrays.toString(counts);

        // A bounded queue pushes back: offer refuses when full, put waits.
        var q = new ArrayBlockingQueue<Integer>(3);
        List<Boolean> accepted = new ArrayList<>();
        for (int n = 1; n <= 4; n++) accepted.add(q.offer(n));
        assert accepted.equals(List.of(true, true, true, false)) : accepted;
        assert q.take() == 1 && q.take() == 2 && q.take() == 3;
        var puts = new AtomicInteger();
        var producer = Thread.ofVirtual().start(() -> {
            try {
                for (int n = 1; n <= 5; n++) {
                    q.put(n); // waits while the queue is full
                    puts.incrementAndGet();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        until(() -> puts.get() == 3 && producer.getState() == Thread.State.WAITING); // stopped at the limit
        q.take();
        until(() -> puts.get() == 4); // one out, one more in; a fifth can't fit until the next take
        for (int i = 0; i < 4; i++) q.take();
        producer.join();
        assert puts.get() == 5 && q.isEmpty();
        System.out.println("all messaging checks passed");
    }
}
