package scaling;

import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.function.DoubleSupplier;

/** The arithmetic behind performance and scalability. The same numbers as the TypeScript lab. */
public final class Scaling {
    private Scaling() {}

    /** Nearest rank: p99 of 1,000 samples is the 990th smallest. */
    public static double percentile(double[] samples, double p) {
        if (samples.length == 0) throw new IllegalArgumentException("no samples");
        double[] sorted = samples.clone(); // Arrays.sort sorts in place
        Arrays.sort(sorted);
        int rank = Math.max(1, (int) Math.ceil(p / 100 * sorted.length));
        return sorted[rank - 1];
    }

    public static double mean(double[] samples) {
        double total = 0;
        for (double x : samples) total += x;
        return total / samples.length;
    }

    /** mulberry32. Java's int wraps on overflow and >>> shifts without the sign, which is what it needs. */
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

    static double exponential(DoubleSupplier random, double mean) {
        return -mean * Math.log(1 - random.getAsDouble());
    }

    /** M/M/1: service time ÷ (1 − utilisation). */
    public static double responseTime(double serviceMs, double utilisation) {
        return utilisation >= 1 ? Double.POSITIVE_INFINITY : serviceMs / (1 - utilisation);
    }

    public record Summary(double mean, double p50, double p99) {}

    public static Summary simulateServer(double serviceMs, double utilisation, int requests, int seed) {
        DoubleSupplier random = seeded(seed);
        double gapMs = serviceMs / utilisation;
        double arrives = 0;
        double free = 0;
        double[] times = new double[requests];
        for (int i = 0; i < requests; i++) {
            arrives += exponential(random, gapMs);
            double starts = Math.max(arrives, free);
            free = starts + exponential(random, serviceMs);
            times[i] = free - arrives;
        }
        return new Summary(mean(times), percentile(times, 50), percentile(times, 99));
    }

    public record Stage(String name, double perSecond) {}

    /** Every request passes every stage, so the system handles only as many as its slowest. */
    public static Stage throughput(List<Stage> stages) {
        return stages.stream().min(Comparator.comparingDouble(Stage::perSecond)).orElseThrow();
    }

    public static double amdahl(double n, double serial) {
        return 1 / (serial + (1 - serial) / n);
    }

    public static double usl(double n, double alpha, double beta) {
        return n / (1 + alpha * (n - 1) + beta * n * (n - 1));
    }

    public static double uslPeak(double alpha, double beta) {
        return Math.sqrt((1 - alpha) / beta);
    }
}
