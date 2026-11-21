package decoding;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.function.DoubleSupplier;

/** From a model's scores to one token. Same algorithm, seed and numbers as the TypeScript lab. */
public final class Decoding {
    private Decoding() {}

    /** One token and its score or probability. Lists keep a fixed order, so sampling is reproducible. */
    public record Entry(String token, double p) {}

    /** mulberry32. java.util.Random(seed) also repeats; this one matches every language in this companion. */
    public static DoubleSupplier seededRandom(int seed) {
        int[] a = {seed};
        return () -> {
            a[0] += 0x6d2b79f5;                       // int arithmetic wraps at 32 bits
            int t = a[0];
            t = (t ^ (t >>> 15)) * (t | 1);           // >>> is the unsigned shift, as in JavaScript
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            return Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
        };
    }

    public static List<Entry> softmax(List<Entry> scores, double temperature) {
        double top = scores.stream().mapToDouble(e -> e.p() / temperature).max().orElseThrow();
        List<Entry> exps = scores.stream().map(e -> new Entry(e.token(), Math.exp(e.p() / temperature - top))).toList();
        return renormalise(exps);
    }

    private static List<Entry> byProbability(List<Entry> dist) {
        return dist.stream().sorted(Comparator.comparingDouble(Entry::p).reversed()).toList();
    }

    public static List<Entry> topK(List<Entry> dist, int k) {
        return renormalise(byProbability(dist).stream().limit(k).toList());
    }

    public static List<Entry> topP(List<Entry> dist, double p) {
        List<Entry> kept = new ArrayList<>();
        double cumulative = 0;
        for (Entry e : byProbability(dist)) {
            kept.add(e);
            cumulative += e.p();
            if (cumulative >= p) break;
        }
        return renormalise(kept);
    }

    private static List<Entry> renormalise(List<Entry> entries) {
        double total = entries.stream().mapToDouble(Entry::p).sum();
        return entries.stream().map(e -> new Entry(e.token(), e.p() / total)).toList();
    }

    public static String sample(List<Entry> dist, DoubleSupplier random) {
        double r = random.getAsDouble();
        for (Entry e : dist) {
            r -= e.p();
            if (r < 0) return e.token();
        }
        return dist.getLast().token();
    }

    public static String greedy(List<Entry> dist) {
        return byProbability(dist).getFirst().token();
    }

    // --- checks, run with `java -ea` ---

    static final List<Entry> SCORES = List.of(new Entry("Paris", 4.0), new Entry("a", 2.0), new Entry("the", 1.5), new Entry("Lyon", 0.5));

    static List<Double> rounded(List<Entry> dist) {
        return dist.stream().map(e -> Math.round(e.p() * 1000) / 1000.0).toList();
    }

    static List<String> tokens(List<Entry> dist) {
        return dist.stream().map(Entry::token).toList();
    }

    static void check(Object got, Object want) {
        if (!got.equals(want)) throw new AssertionError("got " + got + ", want " + want);
    }

    public static void main(String[] args) {
        check(rounded(softmax(SCORES, 1)), List.of(0.802, 0.108, 0.066, 0.024));
        check(rounded(softmax(SCORES, 0.5)), List.of(0.975, 0.018, 0.007, 0.001));
        check(rounded(softmax(SCORES, 2)), List.of(0.547, 0.201, 0.157, 0.095));

        List<Entry> dist = softmax(SCORES, 1);
        check(tokens(topK(dist, 2)), List.of("Paris", "a"));
        check(tokens(topP(dist, 0.9)), List.of("Paris", "a"));
        check(tokens(topP(dist, 0.97)), List.of("Paris", "a", "the"));

        DoubleSupplier r = seededRandom(42);
        check(List.of(r.getAsDouble(), r.getAsDouble(), r.getAsDouble()), List.of(0.6011037519201636, 0.44829055899754167, 0.8524657934904099));

        DoubleSupplier r2 = seededRandom(42);
        List<String> picks = new ArrayList<>();
        for (int i = 0; i < 10; i++) picks.add(sample(dist, r2));
        check(String.join(" ", picks), "Paris Paris a Paris Paris Paris Paris Paris a Paris");
        DoubleSupplier r3 = seededRandom(42);
        int paris = 0;
        for (int i = 0; i < 1000; i++) if (sample(dist, r3).equals("Paris")) paris++;
        check(paris, 796); // about 80.2%, as expected

        check(greedy(softmax(SCORES, 2)), "Paris");
        System.out.println("ok: decoding matches the TypeScript lab");
    }
}
