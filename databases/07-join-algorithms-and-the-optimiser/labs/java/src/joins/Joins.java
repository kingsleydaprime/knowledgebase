package joins;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** The three join algorithms, each counting its work, and two classic estimation failures. Same model as the Python lab. */
public final class Joins {
    private Joins() {}

    public record Row(int key, String value) {}

    public record Pair(String outer, String inner) {}

    public record Result(List<Pair> rows, int work) {}

    /** For every outer row, look at every inner row: N × M comparisons. */
    public static Result nestedLoop(List<Row> outer, List<Row> inner) {
        List<Pair> out = new ArrayList<>();
        int comparisons = 0;
        for (Row o : outer) {
            for (Row in : inner) {
                comparisons++;
                if (o.key() == in.key()) out.add(new Pair(o.value(), in.value()));
            }
        }
        return new Result(out, comparisons);
    }

    /** A sorted inner side searched by halving: about N × log₂ M steps. */
    public static Result indexNestedLoop(List<Row> outer, List<Row> innerSorted) {
        List<Pair> out = new ArrayList<>();
        int steps = 0;
        for (Row o : outer) {
            int lo = 0;
            int hi = innerSorted.size();
            while (lo < hi) {
                steps++;
                int mid = (lo + hi) >>> 1;
                if (innerSorted.get(mid).key() < o.key()) lo = mid + 1;
                else hi = mid;
            }
            for (; lo < innerSorted.size() && innerSorted.get(lo).key() == o.key(); lo++) {
                out.add(new Pair(o.value(), innerSorted.get(lo).value()));
            }
        }
        return new Result(out, steps);
    }

    /** Build a HashMap on the inner side, probe it once per outer row: N + M operations. Equality only. */
    public static Result hashJoin(List<Row> outer, List<Row> inner) {
        Map<Integer, List<String>> table = new HashMap<>();
        for (Row in : inner) table.computeIfAbsent(in.key(), k -> new ArrayList<>()).add(in.value());
        List<Pair> out = new ArrayList<>();
        for (Row o : outer) {
            for (String v : table.getOrDefault(o.key(), List.of())) out.add(new Pair(o.value(), v));
        }
        return new Result(out, inner.size() + outer.size());
    }

    /** Both sides sorted by key: walk them together, about N + M steps. */
    public static Result mergeJoin(List<Row> outerSorted, List<Row> innerSorted) {
        List<Pair> out = new ArrayList<>();
        int steps = 0;
        int i = 0;
        int j = 0;
        while (i < outerSorted.size() && j < innerSorted.size()) {
            steps++;
            int ok = outerSorted.get(i).key();
            int ik = innerSorted.get(j).key();
            if (ok < ik) i++;
            else if (ok > ik) j++;
            else {
                for (int k = j; k < innerSorted.size() && innerSorted.get(k).key() == ok; k++) {
                    out.add(new Pair(outerSorted.get(i).value(), innerSorted.get(k).value()));
                }
                i++; // the next outer row may share the key, so j stays at the start of the group
            }
        }
        return new Result(out, steps);
    }

    public static double independentEstimate(double rows, double... selectivities) {
        for (double s : selectivities) rows *= s;
        return rows;
    }

    public static int rowsReadForPage(int offset, int limit, boolean keyset) {
        return keyset ? limit : offset + limit;
    }
}
