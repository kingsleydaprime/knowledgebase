package cost;

import com.fasterxml.jackson.databind.ObjectMapper;
import cost.Cost.*;
import evals.Evals;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/** Checks, run with `java -ea`. The same numbers as every other language. */
public final class CostCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    /** BigDecimal.equals also compares scale: 2.5138 and 2.51380 are "not equal". compareTo compares value. */
    static boolean same(BigDecimal a, String b) {
        return a.compareTo(new BigDecimal(b)) == 0;
    }

    public static void main(String[] args) throws Exception {
        Price sonnet = Cost.PRICES.get("claude-sonnet-5-5");
        check(same(Cost.cost(new Usage(2000, 500, 0, 0), sonnet), "0.009"), "output costs five times input");

        BigDecimal uncached = Cost.cost(new Usage(6150, 100, 0, 0), sonnet).multiply(BigDecimal.valueOf(1000));
        BigDecimal cached = Cost.cost(new Usage(150, 100, 6000, 0), sonnet);
        for (int i = 0; i < 999; i++) cached = cached.add(Cost.cost(new Usage(150, 100, 0, 6000), sonnet));
        check(same(uncached, "13.30") && same(cached, "2.5138"), uncached + " " + cached);
        check(!cached.equals(new BigDecimal("2.5138")), "equals compares scale too: " + cached); // 2.51380000...
        check(Cost.breakEvenCalls(sonnet) == 2 && Cost.breakEvenCalls(sonnet.withCacheWrite("4")) == 3, "break-even");

        String system = "You classify support tickets. Label by what the team has to do next. ".repeat(20);
        String a = "2026-10-02T09:00:00Z", b = "2026-10-02T09:00:07Z";
        check(Cost.sharedPrefix("Today is " + a + ".\n" + system, "Today is " + b + ".\n" + system) == 27, "front");
        check(Cost.sharedPrefix(system + "\nToday is " + a, system + "\nToday is " + b) == system.length() + 28, "end");

        var user = new LinkedHashMap<String, Object>();
        user.put("tier", "pro");
        user.put("id", 7);
        var inserted = new LinkedHashMap<String, Object>();
        inserted.put("user", user);
        inserted.put("tools", List.of("search"));
        String plain = new ObjectMapper().writeValueAsString(inserted);
        check(plain.equals("{\"user\":{\"tier\":\"pro\",\"id\":7},\"tools\":[\"search\"]}"), plain); // insertion order
        check(Cost.stableJson(inserted).equals("{\"tools\":[\"search\"],\"user\":{\"id\":7,\"tier\":\"pro\"}}"), Cost.stableJson(inserted));

        var golden = Evals.loadGolden(Path.of("..", "..", "..", "12-evals", "labs", "shared", "golden.jsonl"));
        Map<String, String> label = golden.stream().collect(Collectors.toMap(Evals.Case::ticket, Evals.Case::label));
        var big = new Tier("big", new BigDecimal("0.002"), label::get, x -> true); // a stand-in that is always right
        var cheap = new Tier("keywords", BigDecimal.ZERO, Evals::keywords, x -> !x.equals("other"));
        var escalated = new ArrayList<String>();
        var wrong = new ArrayList<String>();
        BigDecimal total = BigDecimal.ZERO;
        for (var c : golden) {
            Answer r = Cost.cascade(c.ticket(), List.of(cheap, big));
            if (r.by().equals("big")) escalated.add(c.id());
            if (!r.answer().equals(c.label())) wrong.add(c.id());
            total = total.add(r.spent());
        }
        check(escalated.equals(List.of("t04", "t10", "t12", "t14", "t17", "t19")) && wrong.equals(List.of("t15", "t20")) && same(total, "0.012"),
                escalated + " " + wrong + " " + total);

        List<Long> ms = List.of(1200L, 900L, 1100L, 1000L, 950L, 1050L, 980L, 1020L, 990L, 9000L);
        check(Cost.percentile(ms, 50) == 1000 && Cost.percentile(ms, 95) == 9000, "percentiles");

        long[] t = {0};
        Iterator<String> stream = new Iterator<>() {
            final List<String> words = List.of("Your", " refund", " is", " on", " its", " way.");
            int i;

            public boolean hasNext() { return i < words.size(); }

            public String next() {
                t[0] += i == 0 ? 800 : 100; // the model reads the prompt before the first token
                return words.get(i++);
            }
        };
        check(Cost.timeStream(stream, () -> t[0]).equals(new Timed("Your refund is on its way.", 800, 1300)), "time to first token");

        System.out.println("all cost checks passed");
    }
}
