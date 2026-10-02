package evals;

import evals.Evals.*;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

/** Checks, run with `java -ea`. */
public final class EvalsCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static double round2(double x) {
        return Math.round(x * 100) / 100.0;
    }

    static Function<String, String> withChange(String part, String label) {
        return t -> t.contains(part) ? label : Evals.keywords(t);
    }

    public static void main(String[] args) {
        List<Case> golden = Evals.loadGolden(Path.of("..", "shared", "golden.jsonl"));
        check(golden.size() == 20, golden.size());

        check("bug".equals(Evals.parseLabel("Category: BUG")) && Evals.parseLabel("bug or billing") == null, "parseLabel");
        double[] w = Evals.wilson(17, 20);
        check(round2(w[0]) == 0.64 && round2(w[1]) == 0.95, w[0] + " " + w[1]);

        check(Evals.runEval(Evals.majority(golden), golden).passed() == 8, "majority");
        Result rules = Evals.runEval(Evals::keywords, golden);
        List<String> misses = rules.results().stream().filter(r -> !r.pass()).map(r -> r.id() + ":" + r.got()).toList();
        check(rules.passed() == 15 && misses.equals(List.of("t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing")), misses);
        check(rules.byTag().get("other-language")[0] == 0 && rules.byTag().get("other-language")[1] == 2, "by tag");

        Result better = Evals.runEval(withChange("La aplicación", "bug"), golden);
        check(Evals.compare(rules, better).equals(Map.of("fixed", List.of("t14"), "broke", List.of())), Evals.compare(rules, better));
        Result worse = Evals.runEval(withChange("charged twice", "bug"), golden);
        check(Evals.gate(rules, 0.6, null).isEmpty(), "base passes");
        List<String> reasons = Evals.gate(worse, 0.75, rules, "t02", "t18");
        check(reasons.equals(List.of("pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed")), reasons);

        check(Evals.pairwise(p -> "FIRST", "ticket", "reply A", "reply B").equals("inconsistent"), "biased");
        check(Evals.pairwise(p -> p.indexOf("reply B") < p.indexOf("reply A") ? "FIRST" : "SECOND", "ticket", "reply A", "reply B").equals("b"), "fair");

        boolean[] human = {true, true, false, false, true, false, true, false, false, true};
        boolean[] lenient = {true, true, true, true, true, true, true, true, false, true};
        double[] ak = Evals.agreement(lenient, human);
        check(round2(ak[0]) == 0.6 && round2(ak[1]) == 0.2, ak[0] + " " + ak[1]);

        System.out.println("ok: the same 8/20, 15/20, gate reasons and kappa as every other language");
    }
}
