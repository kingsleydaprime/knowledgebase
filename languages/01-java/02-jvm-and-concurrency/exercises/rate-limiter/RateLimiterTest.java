import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimiterTest {
    static int passed = 0, failed = 0;

    public static void main(String[] args) throws Exception {
        testBurstCapacity();
        testRefillOverTime();
        testConcurrentAcquireDoesNotExceedCapacity();
        System.out.println(passed + " passed, " + failed + " failed");
        if (failed > 0) System.exit(1);
    }

    static void check(boolean condition, String message) {
        if (condition) { passed++; System.out.println("PASS: " + message); }
        else { failed++; System.out.println("FAIL: " + message); }
    }

    static void testBurstCapacity() {
        RateLimiter limiter = new RateLimiter(5.0, 5);
        int granted = 0;
        for (int i = 0; i < 5; i++) if (limiter.tryAcquire()) granted++;
        check(granted == 5, "bucket starts full: 5 immediate acquires succeed (got " + granted + ")");
        check(!limiter.tryAcquire(), "6th immediate acquire fails once the bucket is empty");
    }

    static void testRefillOverTime() throws InterruptedException {
        RateLimiter limiter = new RateLimiter(10.0, 1);
        check(limiter.tryAcquire(), "first acquire succeeds (bucket starts full)");
        check(!limiter.tryAcquire(), "immediate second acquire fails (bucket now empty)");
        Thread.sleep(150);
        check(limiter.tryAcquire(), "acquire succeeds again after enough time has passed to refill one token");
    }

    static void testConcurrentAcquireDoesNotExceedCapacity() throws InterruptedException {
        int capacity = 20;
        RateLimiter limiter = new RateLimiter(20.0, capacity);
        int threads = 50;
        AtomicInteger granted = new AtomicInteger(0);
        CountDownLatch done = new CountDownLatch(threads);
        for (int i = 0; i < threads; i++) {
            new Thread(() -> {
                if (limiter.tryAcquire()) granted.incrementAndGet();
                done.countDown();
            }).start();
        }
        done.await(2, TimeUnit.SECONDS);
        check(granted.get() <= capacity,
              "with " + threads + " threads racing at once, at most the bucket capacity (" + capacity + ") is granted (got " + granted.get() + ")");
    }
}
