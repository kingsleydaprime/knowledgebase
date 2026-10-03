package balancing;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.function.DoubleSupplier;
import java.util.function.Supplier;

/** How a load balancer picks a server, health checks, and consistent hashing. The same numbers as the TypeScript lab. */
public final class Balancing {
    private Balancing() {}

    /** Chooses a server from how many requests each is still working on. */
    @FunctionalInterface
    public interface Pick {
        int pick(int[] outstanding, DoubleSupplier random);
    }

    public static Pick roundRobin() {
        int[] next = {0};
        return (outstanding, random) -> next[0]++ % outstanding.length;
    }

    /** The fewest requests in progress; ties go to the lowest number. */
    public static final Pick LEAST_OUTSTANDING = (outstanding, random) -> {
        int best = 0;
        for (int i = 1; i < outstanding.length; i++) if (outstanding[i] < outstanding[best]) best = i;
        return best;
    };

    public static final Pick RANDOM = (outstanding, random) -> (int) (random.getAsDouble() * outstanding.length);

    /** Two servers at random, and the less busy of the two. */
    public static final Pick TWO_CHOICES = (outstanding, random) -> {
        int a = (int) (random.getAsDouble() * outstanding.length);
        int b = (int) (random.getAsDouble() * outstanding.length);
        return outstanding[b] < outstanding[a] ? b : a;
    };

    /** mulberry32, the same generator as week 1's lab. */
    public static DoubleSupplier seeded(int seed) {
        int[] a = {seed};
        return () -> {
            a[0] += 0x6d2b79f5;
            int t = a[0];
            t = (t ^ (t >>> 15)) * (t | 1);
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            return Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
        };
    }

    public record Latency(long mean, long p50, long p99) {}

    /** Random traffic to servers that each work through their own queue. 1 in 20 requests takes 200 ms. */
    public static Latency simulate(Pick pick, int servers, double busy, int requests, int seed) {
        DoubleSupplier random = seeded(seed);
        double meanWorkMs = 0.95 * 10 + 0.05 * 200;
        double gapMs = meanWorkMs / (busy * servers);
        List<java.util.ArrayDeque<Double>> finishes = new ArrayList<>(); // per server: when each queued request ends
        for (int s = 0; s < servers; s++) finishes.add(new java.util.ArrayDeque<>());
        int[] outstanding = new int[servers];
        double now = 0;
        double total = 0;
        double[] times = new double[requests];
        for (int i = 0; i < requests; i++) {
            now += -gapMs * Math.log(1 - random.getAsDouble());
            for (int s = 0; s < servers; s++) {
                var queue = finishes.get(s);
                while (!queue.isEmpty() && queue.peekFirst() <= now) queue.pollFirst();
                outstanding[s] = queue.size();
            }
            int s = pick.pick(outstanding, random);
            double workMs = random.getAsDouble() < 0.05 ? 200 : 10;
            var queue = finishes.get(s);
            double ends = Math.max(now, queue.isEmpty() ? 0 : queue.peekLast()) + workMs;
            queue.addLast(ends);
            times[i] = ends - now;
            total += ends - now;
        }
        Arrays.sort(times);
        return new Latency(Math.round(total / requests), Math.round(percentile(times, 50)), Math.round(percentile(times, 99)));
    }

    private static double percentile(double[] sorted, double p) {
        return sorted[Math.max(1, (int) Math.ceil(p / 100 * sorted.length)) - 1];
    }

    /** nginx's smooth weighted round-robin. A LinkedHashMap keeps the servers in the order given, which breaks ties. */
    public static Supplier<String> smoothWeighted(LinkedHashMap<String, Integer> weights) {
        int total = weights.values().stream().mapToInt(Integer::intValue).sum();
        var current = new LinkedHashMap<String, Integer>();
        weights.keySet().forEach(name -> current.put(name, 0));
        return () -> {
            weights.forEach((name, weight) -> current.merge(name, weight, Integer::sum));
            String best = null;
            for (var e : current.entrySet()) if (best == null || e.getValue() > current.get(best)) best = e.getKey();
            current.merge(best, -total, Integer::sum);
            return best;
        };
    }

    /** {@code fall} failures in a row mark a server down; {@code rise} successes in a row bring it back. */
    public static final class Health {
        private boolean up = true;
        private final int fall;
        private final int rise;
        private int streak;

        public Health(int fall, int rise) {
            this.fall = fall;
            this.rise = rise;
        }

        public boolean up() {
            return up;
        }

        public void record(boolean ok) {
            if (ok == up) {
                streak = 0;
                return;
            }
            if (++streak >= (up ? fall : rise)) {
                up = !up;
                streak = 0;
            }
        }
    }

    public record Server(String name, Health health) {}

    public static String pickHealthy(List<Server> servers, int turn) {
        var up = servers.stream().filter(s -> s.health().up()).toList();
        if (up.isEmpty()) throw new IllegalStateException("no healthy servers: answer 503");
        return up.get(turn % up.size()).name();
    }

    /**
     * FNV-1a, then a mixing step. Java has no unsigned int: the bits are the same as the other languages', but
     * comparing and dividing them must use the unsigned methods, or half the values count as negative.
     */
    public static int hash(String text) {
        int h = 0x811c9dc5;
        for (int i = 0; i < text.length(); i++) h = (h ^ text.charAt(i)) * 0x01000193; // charAt is a UTF-16 unit, like JavaScript's
        h = (h ^ (h >>> 16)) * 0x85ebca6b;
        h = (h ^ (h >>> 13)) * 0xc2b2ae35;
        return h ^ (h >>> 16);
    }

    public static String modulo(String key, List<String> servers) {
        return servers.get(Integer.remainderUnsigned(hash(key), servers.size())); // hash(key) % n can be negative
    }

    private record Point(int at, String server) {}

    /** Servers and keys on one circle of hash values; a key belongs to the first server clockwise from it. */
    public static final class HashRing {
        private static final Comparator<Point> BY_POSITION = (a, b) -> Integer.compareUnsigned(a.at(), b.at());
        private final List<Point> points = new ArrayList<>();
        private final int replicas;

        public HashRing(List<String> servers, int replicas) {
            this.replicas = replicas;
            servers.forEach(this::add);
        }

        public void add(String server) {
            for (int r = 0; r < replicas; r++) points.add(new Point(hash(server + "#" + r), server));
            points.sort(BY_POSITION); // List.sort is stable, like JavaScript's
        }

        public void remove(String server) {
            points.removeIf(p -> p.server().equals(server));
        }

        public String serverFor(String key) {
            if (points.isEmpty()) throw new IllegalStateException("the ring is empty");
            int h = hash(key);
            int lo = 0;
            int hi = points.size(); // binary search for the first point at or after h
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (Integer.compareUnsigned(points.get(mid).at(), h) < 0) lo = mid + 1;
                else hi = mid;
            }
            return points.get(lo % points.size()).server(); // past the last point, wrap round to the first
        }
    }
}
