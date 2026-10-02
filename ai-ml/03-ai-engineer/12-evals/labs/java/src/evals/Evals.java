package evals;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.function.UnaryOperator;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/** An eval harness: the shared golden set, exact-match scoring, error bars, comparison, a gate,
 *  baselines, and the checks on an LLM judge. */
public final class Evals {
    private Evals() {}

    public record Case(String id, String ticket, String label, List<String> tags) {}

    public record CaseResult(String id, String expected, String got, String reply, boolean pass) {}

    public record Result(List<CaseResult> results, Map<String, int[]> byTag) {
        public long passed() { return results.stream().filter(CaseResult::pass).count(); }
        public double rate() { return (double) passed() / results.size(); }
    }

    public static List<Case> loadGolden(Path path) {
        ObjectMapper json = new ObjectMapper();
        try {
            List<Case> cases = new ArrayList<>();
            for (String line : Files.readAllLines(path)) {
                if (!line.isBlank()) cases.add(json.readValue(line, Case.class));
            }
            return cases;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static final Pattern LABEL = Pattern.compile("\\b(bug|billing|feature|other)\\b");

    /** The one label in the reply, or null if there are none or several. */
    public static String parseLabel(String reply) {
        var found = LABEL.matcher(reply.toLowerCase()).results().map(m -> m.group(1)).collect(Collectors.toSet());
        return found.size() == 1 ? found.iterator().next() : null;
    }

    /** Where the true pass rate probably lies (95%), given a small sample. */
    public static double[] wilson(long passed, long total) {
        if (total == 0) return new double[] {0, 1};
        double z = 1.96, n = total, p = passed / n;
        double centre = p + z * z / (2 * n);
        double spread = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n));
        return new double[] {(centre - spread) / (1 + z * z / n), (centre + spread) / (1 + z * z / n)};
    }

    public static Result runEval(Function<String, String> classify, List<Case> cases) {
        List<CaseResult> results = new ArrayList<>();
        Map<String, int[]> byTag = new LinkedHashMap<>();
        for (Case c : cases) {
            String reply = classify.apply(c.ticket());
            String got = parseLabel(reply);
            boolean pass = c.label().equals(got);
            results.add(new CaseResult(c.id(), c.label(), got, reply, pass));
            for (String tag : c.tags()) {
                int[] counts = byTag.computeIfAbsent(tag, t -> new int[2]);
                if (pass) counts[0]++;
                counts[1]++;
            }
        }
        return new Result(results, byTag);
    }

    /** What a change fixed and what it broke. */
    public static Map<String, List<String>> compare(Result before, Result after) {
        Map<String, Boolean> was = before.results().stream().collect(Collectors.toMap(CaseResult::id, CaseResult::pass));
        return Map.of(
                "fixed", after.results().stream().filter(r -> r.pass() && Boolean.FALSE.equals(was.get(r.id()))).map(CaseResult::id).toList(),
                "broke", after.results().stream().filter(r -> !r.pass() && Boolean.TRUE.equals(was.get(r.id()))).map(CaseResult::id).toList());
    }

    /** The reasons to fail the build; an empty list means the change may merge. */
    public static List<String> gate(Result result, double minRate, Result baseline, String... mustPass) {
        List<String> reasons = new ArrayList<>();
        if (result.rate() < minRate)
            reasons.add("pass rate %.0f%% is below the floor of %.0f%%".formatted(result.rate() * 100, minRate * 100));
        List<String> broke = baseline == null ? List.of() : compare(baseline, result).get("broke");
        if (!broke.isEmpty()) reasons.add("regressed on " + String.join(", ", broke));
        for (String id : mustPass) {
            if (result.results().stream().noneMatch(r -> r.id().equals(id) && r.pass())) reasons.add("must-pass case " + id + " failed");
        }
        return reasons;
    }

    /** Always the most common label. */
    public static Function<String, String> majority(List<Case> cases) {
        String top = cases.stream().collect(Collectors.groupingBy(Case::label, Collectors.counting()))
                .entrySet().stream().max(Map.Entry.comparingByValue()).orElseThrow().getKey();
        return ticket -> top;
    }

    private static final Pattern BILLING = Pattern.compile("charg|refund|invoice|pay|price|subscription|discount|receipt");
    private static final Pattern BUG = Pattern.compile("crash|error|broken|bug|blank|empty|doesn't work|not working");
    private static final Pattern FEATURE = Pattern.compile("add|would be great|should support|could you|please support");

    public static String keywords(String ticket) {
        String t = ticket.toLowerCase();
        if (BILLING.matcher(t).find()) return "billing";
        if (BUG.matcher(t).find()) return "bug";
        if (FEATURE.matcher(t).find()) return "feature";
        return "other";
    }

    private static final Pattern FIRST = Pattern.compile("\\bfirst\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern SECOND = Pattern.compile("\\bsecond\\b", Pattern.CASE_INSENSITIVE);

    /** Asks in both orders, so a judge that prefers whatever comes first is caught, not trusted. */
    public static String pairwise(UnaryOperator<String> ask, String ticket, String a, String b) {
        Function<String, String> pick = answer -> FIRST.matcher(answer).find() ? "first" : SECOND.matcher(answer).find() ? "second" : "";
        String forward = pick.apply(ask.apply(pairPrompt(ticket, a, b)));
        String backward = pick.apply(ask.apply(pairPrompt(ticket, b, a)));
        if (forward.equals("first") && backward.equals("second")) return "a";
        if (forward.equals("second") && backward.equals("first")) return "b";
        return "inconsistent";
    }

    private static String pairPrompt(String ticket, String first, String second) {
        return "Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n" + ticket
                + "\n</ticket>\n<first>\n" + first + "\n</first>\n<second>\n" + second + "\n</second>";
    }

    /** {agreement, Cohen's kappa}. Kappa removes the agreement you'd expect by chance. */
    public static double[] agreement(boolean[] judge, boolean[] human) {
        double n = judge.length, same = 0, judgeYes = 0, humanYes = 0;
        for (int i = 0; i < judge.length; i++) {
            if (judge[i] == human[i]) same++;
            if (judge[i]) judgeYes++;
            if (human[i]) humanYes++;
        }
        double agree = same / n, chance = (judgeYes / n) * (humanYes / n) + (1 - judgeYes / n) * (1 - humanYes / n);
        return new double[] {agree, chance == 1 ? 1 : (agree - chance) / (1 - chance)};
    }

}
