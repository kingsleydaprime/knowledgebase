package scaling;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.function.DoubleSupplier;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class ScalingCheck {
    private ScalingCheck() {}

    private static String fixed(double x, int places) {
        return String.format(Locale.ROOT, "%." + places + "f", x); // without Locale.ROOT, a French machine prints "5,93"
    }

    public static void main(String[] args) {
        double[] tens = {10, 1, 9, 2, 8, 3, 7, 4, 6, 5};
        assert Scaling.percentile(tens, 50) == 5 && Scaling.percentile(tens, 90) == 9;
        assert Scaling.percentile(tens, 99) == 10 && Scaling.percentile(tens, 100) == 10 && tens[0] == 10;
        try {
            Scaling.percentile(new double[0], 50);
            throw new AssertionError("expected an error for no samples");
        } catch (IllegalArgumentException expected) {
            // no samples
        }

        DoubleSupplier random = Scaling.seeded(42);
        double[] latencies = new double[1_000];
        for (int i = 0; i < latencies.length; i++) {
            boolean slow = random.getAsDouble() < 0.02;
            latencies[i] = slow ? 1_500 + 1_000 * random.getAsDouble() : 40 + 20 * random.getAsDouble();
        }
        List<Long> tail = List.of(Math.round(Scaling.mean(latencies)), Math.round(Scaling.percentile(latencies, 50)),
                Math.round(Scaling.percentile(latencies, 95)), Math.round(Scaling.percentile(latencies, 99)));
        assert tail.equals(List.of(93L, 50L, 59L, 2_208L)) : tail;

        List<Long> waits = new ArrayList<>();
        for (double busy : new double[] {0.5, 0.8, 0.9, 0.95, 0.99}) waits.add(Math.round(Scaling.responseTime(10, busy)));
        assert waits.equals(List.of(20L, 50L, 100L, 200L, 1_000L)) : waits;
        assert Scaling.responseTime(10, 1) == Double.POSITIVE_INFINITY;

        for (double busy : new double[] {0.5, 0.8, 0.9}) {
            var sim = Scaling.simulateServer(10, busy, 200_000, 7);
            double model = Scaling.responseTime(10, busy);
            assert Math.abs(sim.mean() - model) / model < 0.1 : sim;
            assert Math.abs(sim.p99() / sim.mean() - Math.log(100)) < 0.5 : sim;
        }

        assert Math.round(Scaling.responseTime(300, 0.1)) == 333 && Math.round(Scaling.responseTime(10, 0.95)) == 200;
        assert Math.round(Scaling.responseTime(10, 0.95 / 2)) == 19 && Math.round(Scaling.responseTime(300, 0.05)) == 316;

        var stages = new ArrayList<>(List.of(new Scaling.Stage("load balancer", 50_000),
                new Scaling.Stage("app servers", 4 * 800), new Scaling.Stage("database writes", 2_000)));
        var want = new Scaling.Stage("database writes", 2_000);
        assert Scaling.throughput(stages).equals(want);
        stages.set(1, new Scaling.Stage("app servers", 8 * 800));
        assert Scaling.throughput(stages).equals(want);

        assert fixed(Scaling.amdahl(8, 0.05), 2).equals("5.93") && Scaling.amdahl(1_000_000, 0.05) < 20;
        assert Math.round(Scaling.uslPeak(0.05, 0.001)) == 31;
        List<String> usl = new ArrayList<>();
        for (double n : new double[] {8, 31, 60, 100}) usl.add(fixed(Scaling.usl(n, 0.05, 0.001), 1));
        assert usl.equals(List.of("5.7", "9.0", "8.0", "6.3")) : usl;
        System.out.println("all scaling checks passed");
    }
}
