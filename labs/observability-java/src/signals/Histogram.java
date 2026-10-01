package signals;

import java.util.Arrays;

// A Prometheus-style histogram: fixed upper bounds, a count per bucket. In Spring Boot,
// Micrometer's Timer with publishPercentileHistogram() exports exactly this to Prometheus.
public final class Histogram {
    private final double[] bounds;       // upper bounds, ascending; the last bucket is +Inf
    private final long[] counts;         // per bucket, not cumulative

    public Histogram(double... bounds) {
        this.bounds = bounds.clone();
        this.counts = new long[bounds.length + 1];
    }

    public void observe(double value) {
        int i = 0;
        while (i < bounds.length && value > bounds[i]) i++;   // "le": less than or equal
        counts[i]++;
    }

    // Prometheus's histogram_quantile: find the bucket holding rank q×total, interpolate inside it.
    public double estimateQuantile(double q) {
        double total = Arrays.stream(counts).sum();
        double rank = q * total, lower = 0, cumulative = 0;
        for (int i = 0; i < counts.length; i++) {
            double before = cumulative;
            cumulative += counts[i];
            if (cumulative >= rank) {
                if (i == bounds.length) return lower;                 // the +Inf bucket
                return lower + (bounds[i] - lower) * (rank - before) / (cumulative - before);
            }
            if (i < bounds.length) lower = bounds[i];
        }
        return lower;
    }

    public static void main(String[] args) {
        var h = new Histogram(25, 50, 100, 250, 500, 1000, 2500, 5000);
        for (int i = 0; i < 97; i++) h.observe(20 + i % 10);
        for (double ms : new double[] {1800, 2100, 3000}) h.observe(ms);
        assert Math.abs(h.estimateQuantile(0.50) - 20.83) < 0.01 : h.estimateQuantile(0.50);   // exact: 24
        assert h.estimateQuantile(0.99) == 2500 : h.estimateQuantile(0.99);                    // exact: 2100
        System.out.println("ok: p50 ~ 20.83, p99 ~ 2500 from buckets");
    }
}
