package rates;

import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public final class Rates {
    public interface RateSource { long rate(String base, String quote); }

    public static final class FlakyApi implements RateSource {
        public int calls;
        private final int failures;
        public FlakyApi(int failures) { this.failures = failures; }
        public long rate(String base, String quote) {
            calls++;
            if (calls <= failures) throw new IllegalStateException("503 from rates API");
            return base.equals("GBP") && quote.equals("NGN") ? 2000 : 1;
        }
    }

    // Decorators: classes that implement the interface and wrap another implementation.
    public record Retrying(RateSource inner, int attempts) implements RateSource {
        public long rate(String base, String quote) {
            RuntimeException last = null;
            for (int i = 0; i < attempts; i++) {
                try { return inner.rate(base, quote); } catch (RuntimeException e) { last = e; }
            }
            throw last;
        }
    }

    public record Caching(RateSource inner, Map<String, Long> cache) implements RateSource {
        public Caching(RateSource inner) { this(inner, new HashMap<>()); }
        public long rate(String base, String quote) {
            return cache.computeIfAbsent(base + "->" + quote, k -> inner.rate(base, quote));
        }
    }

    // A dynamic proxy: the JDK builds a class implementing any interface at runtime and sends
    // every call through one handler. Spring AOP's @Transactional and @Cacheable work this way.
    public static RateSource logging(RateSource inner, List<String> log) {
        return (RateSource) Proxy.newProxyInstance(
            RateSource.class.getClassLoader(),
            new Class<?>[] {RateSource.class},
            (proxy, method, args) -> {
                Object result = method.invoke(inner, args);
                log.add(args[0] + "->" + args[1] + " = " + result);
                return result;
            });
    }
}
