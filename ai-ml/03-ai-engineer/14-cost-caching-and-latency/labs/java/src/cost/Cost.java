package cost;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.MapperFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.json.JsonMapper;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.function.LongSupplier;
import java.util.function.Predicate;
import java.util.function.UnaryOperator;

/** Pricing with exact BigDecimal money, prefix diagnosis, canonical JSON, a cascade and latency percentiles. */
public final class Cost {
    private Cost() {}

    /** US dollars per million tokens. */
    public record Price(BigDecimal input, BigDecimal output, BigDecimal cacheWrite, BigDecimal cacheRead) {
        static Price of(String input, String output, String cacheWrite, String cacheRead) {
            return new Price(new BigDecimal(input), new BigDecimal(output), new BigDecimal(cacheWrite), new BigDecimal(cacheRead));
        }

        public Price withCacheWrite(String value) { return new Price(input, output, new BigDecimal(value), cacheRead); }
    }

    /** Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Check before relying on them. */
    public static final Map<String, Price> PRICES = Map.of(
            "claude-haiku-4-5", Price.of("1", "5", "1.25", "0.1"),
            "claude-sonnet-5-5", Price.of("2", "10", "2.5", "0.2"),
            "claude-opus-5-5", Price.of("4", "20", "5", "0.2"),
            "local", Price.of("0", "0", "0", "0"));

    /** {@code input} counts only input that was neither written to nor read from the cache. */
    public record Usage(long input, long output, long cacheWrite, long cacheRead) {}

    public static BigDecimal cost(Usage u, Price p) {
        return p.input().multiply(BigDecimal.valueOf(u.input()))
                .add(p.output().multiply(BigDecimal.valueOf(u.output())))
                .add(p.cacheWrite().multiply(BigDecimal.valueOf(u.cacheWrite())))
                .add(p.cacheRead().multiply(BigDecimal.valueOf(u.cacheRead())))
                .movePointLeft(6); // per million tokens; exact, unlike dividing a double
    }

    /** Caching n calls costs write + (n − 1) × read; not caching costs n × input. */
    public static int breakEvenCalls(Price p) {
        return p.cacheWrite().subtract(p.cacheRead()).divide(p.input().subtract(p.cacheRead()), 0, RoundingMode.FLOOR).intValueExact() + 1;
    }

    public static int sharedPrefix(String a, String b) {
        int i = 0;
        while (i < a.length() && i < b.length() && a.charAt(i) == b.charAt(i)) i++;
        return i;
    }

    /** Jackson writes map entries in the map's own order (a HashMap's is arbitrary) and record or class
     *  properties in declaration order. These two settings sort both. */
    private static final ObjectMapper STABLE = JsonMapper.builder()
            .enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS)
            .enable(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY)
            .build();

    public static String stableJson(Object value) throws JsonProcessingException {
        return STABLE.writeValueAsString(value);
    }

    public record Tier(String name, BigDecimal cost, UnaryOperator<String> answer, Predicate<String> accept) {}

    public record Answer(String answer, String by, BigDecimal spent) {}

    public static Answer cascade(String input, List<Tier> tiers) {
        BigDecimal spent = BigDecimal.ZERO;
        for (int i = 0; i < tiers.size(); i++) {
            Tier tier = tiers.get(i);
            String answer = tier.answer().apply(input);
            spent = spent.add(tier.cost()); // a rejected answer was still paid for
            if (i == tiers.size() - 1 || tier.accept().test(answer)) return new Answer(answer, tier.name(), spent);
        }
        throw new IllegalArgumentException("a cascade needs at least one tier");
    }

    /** Nearest rank: the smallest value that at least p% of the values are less than or equal to. */
    public static long percentile(List<Long> values, double p) {
        List<Long> sorted = values.stream().sorted().toList();
        return sorted.get(Math.max(0, (int) Math.ceil(p / 100 * sorted.size()) - 1));
    }

    public record Timed(String text, long ttftMs, long totalMs) {}

    /** Reads a blocking stream of chunks (HttpClient's BodyHandlers.ofLines gives one), timing the first. */
    public static Timed timeStream(Iterator<String> chunks, LongSupplier nowMs) {
        long started = nowMs.getAsLong(), ttft = -1;
        var text = new StringBuilder();
        while (chunks.hasNext()) {
            String chunk = chunks.next();
            if (ttft < 0) ttft = nowMs.getAsLong() - started;
            text.append(chunk);
        }
        long total = nowMs.getAsLong() - started;
        return new Timed(text.toString(), ttft < 0 ? total : ttft, total);
    }
}
