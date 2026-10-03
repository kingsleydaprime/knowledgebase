// The three join algorithms, each counting its work, and two classic estimation failures. Same model as the Python lab.

public readonly record struct Row(int Key, string Value);

public static class Joins
{
    /// <summary>For every outer row, look at every inner row: N × M comparisons.</summary>
    public static (List<(string, string)> Rows, long Work) NestedLoop(IReadOnlyList<Row> outer, IReadOnlyList<Row> inner)
    {
        var (out_, comparisons) = (new List<(string, string)>(), 0L);
        foreach (var o in outer)
            foreach (var i in inner)
            {
                comparisons++;
                if (o.Key == i.Key) out_.Add((o.Value, i.Value));
            }
        return (out_, comparisons);
    }

    /// <summary>A sorted inner side searched by halving: about N × log₂ M steps.</summary>
    public static (List<(string, string)> Rows, long Work) IndexNestedLoop(IReadOnlyList<Row> outer, IReadOnlyList<Row> innerSorted)
    {
        var (out_, steps) = (new List<(string, string)>(), 0L);
        foreach (var o in outer)
        {
            var (lo, hi) = (0, innerSorted.Count);
            while (lo < hi)
            {
                steps++;
                var mid = (lo + hi) / 2;
                if (innerSorted[mid].Key < o.Key) lo = mid + 1;
                else hi = mid;
            }
            for (; lo < innerSorted.Count && innerSorted[lo].Key == o.Key; lo++) out_.Add((o.Value, innerSorted[lo].Value));
        }
        return (out_, steps);
    }

    /// <summary>Build a lookup on the inner side, probe it once per outer row: N + M operations. Equality only.</summary>
    public static (List<(string, string)> Rows, long Work) HashJoin(IReadOnlyList<Row> outer, IReadOnlyList<Row> inner)
    {
        var table = inner.ToLookup(i => i.Key, i => i.Value); // LINQ's ToLookup is a hash table of key → values
        var rows = outer.SelectMany(o => table[o.Key].Select(v => (o.Value, v))).ToList();
        return (rows, inner.Count + outer.Count);
    }

    /// <summary>Both sides sorted by key: walk them together, about N + M steps.</summary>
    public static (List<(string, string)> Rows, long Work) MergeJoin(IReadOnlyList<Row> outerSorted, IReadOnlyList<Row> innerSorted)
    {
        var (out_, steps, i, j) = (new List<(string, string)>(), 0L, 0, 0);
        while (i < outerSorted.Count && j < innerSorted.Count)
        {
            steps++;
            var (ok, ik) = (outerSorted[i].Key, innerSorted[j].Key);
            if (ok < ik) i++;
            else if (ok > ik) j++;
            else
            {
                for (var k = j; k < innerSorted.Count && innerSorted[k].Key == ok; k++) out_.Add((outerSorted[i].Value, innerSorted[k].Value));
                i++; // the next outer row may share the key, so j stays at the start of the group
            }
        }
        return (out_, steps);
    }

    public static double IndependentEstimate(double rows, params double[] selectivities) => selectivities.Aggregate(rows, (e, s) => e * s);

    public static int RowsReadForPage(int offset, int limit, bool keyset) => keyset ? limit : offset + limit;
}
