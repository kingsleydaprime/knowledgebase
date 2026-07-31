import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public class BoundedBlockingQueueTest {
    static int passed = 0, failed = 0;

    public static void main(String[] args) throws Exception {
        testFifoOrder();
        testBlocksWhenFull();
        testBlocksWhenEmpty();
        testConcurrentProducersConsumers();
        System.out.println(passed + " passed, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }

    static void check(boolean condition, String message) {
        if (condition) { passed++; System.out.println("PASS: " + message); }
        else { failed++; System.out.println("FAIL: " + message); }
    }

    static void testFifoOrder() throws InterruptedException {
        BoundedBlockingQueue<Integer> q = new BoundedBlockingQueue<>(3);
        q.put(1); q.put(2); q.put(3);
        check(q.take() == 1, "FIFO: first take returns first put");
        check(q.take() == 2, "FIFO: second take returns second put");
        check(q.take() == 3, "FIFO: third take returns third put");
    }

    static void testBlocksWhenFull() throws InterruptedException {
        BoundedBlockingQueue<Integer> q = new BoundedBlockingQueue<>(2);
        q.put(1); q.put(2);
        AtomicBoolean putReturned = new AtomicBoolean(false);
        Thread producer = new Thread(() -> {
            try { q.put(3); putReturned.set(true); } catch (InterruptedException ignored) {}
        });
        producer.start();
        Thread.sleep(200);
        check(!putReturned.get(), "put() blocks when the queue is full");
        q.take();
        producer.join(1000);
        check(putReturned.get(), "put() unblocks once space is available");
    }

    static void testBlocksWhenEmpty() throws InterruptedException {
        BoundedBlockingQueue<Integer> q = new BoundedBlockingQueue<>(2);
        AtomicInteger result = new AtomicInteger(-1);
        Thread consumer = new Thread(() -> {
            try { result.set(q.take()); } catch (InterruptedException ignored) {}
        });
        consumer.start();
        Thread.sleep(200);
        check(result.get() == -1, "take() blocks when the queue is empty");
        q.put(42);
        consumer.join(1000);
        check(result.get() == 42, "take() unblocks once an item is available");
    }

    static void testConcurrentProducersConsumers() throws InterruptedException {
        final int PRODUCERS = 4, CONSUMERS = 4, ITEMS_PER_PRODUCER = 2000;
        final int TOTAL = PRODUCERS * ITEMS_PER_PRODUCER;

        BoundedBlockingQueue<Integer> q = new BoundedBlockingQueue<>(50);
        Set<Integer> seen = ConcurrentHashMap.newKeySet();
        AtomicInteger claimed = new AtomicInteger(0);
        CountDownLatch consumersDone = new CountDownLatch(CONSUMERS);

        for (int p = 0; p < PRODUCERS; p++) {
            final int base = p * ITEMS_PER_PRODUCER;
            new Thread(() -> {
                try {
                    for (int i = 0; i < ITEMS_PER_PRODUCER; i++) q.put(base + i);
                } catch (InterruptedException ignored) {}
            }).start();
        }

        for (int c = 0; c < CONSUMERS; c++) {
            new Thread(() -> {
                try {
                    while (true) {
                        int myIndex = claimed.getAndIncrement();
                        if (myIndex >= TOTAL) break;
                        seen.add(q.take());
                    }
                } catch (InterruptedException ignored) {
                } finally {
                    consumersDone.countDown();
                }
            }).start();
        }

        boolean finished = consumersDone.await(10, TimeUnit.SECONDS);
        check(finished, "concurrent test completes within the timeout (no deadlock)");
        check(seen.size() == TOTAL,
              "all " + TOTAL + " items consumed exactly once, no loss or duplication (saw " + seen.size() + ")");
    }
}
