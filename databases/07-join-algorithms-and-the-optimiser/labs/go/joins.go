// Package joins: the three join algorithms, written out, each counting its work; and the arithmetic of two
// classic estimation failures. The same model as the Python lab.
package joins

import "slices"

type Row struct {
	Key   int
	Value string
}

type Pair struct{ Outer, Inner string }

// NestedLoop looks at every inner row for every outer row: N × M comparisons.
func NestedLoop(outer, inner []Row) ([]Pair, int) {
	var out []Pair
	comparisons := 0
	for _, o := range outer {
		for _, in := range inner {
			comparisons++
			if o.Key == in.Key {
				out = append(out, Pair{o.Value, in.Value})
			}
		}
	}
	return out, comparisons
}

// IndexNestedLoop searches a sorted inner side by halving: about N × log₂ M steps.
func IndexNestedLoop(outer, innerSorted []Row) ([]Pair, int) {
	var out []Pair
	steps := 0
	for _, o := range outer {
		lo, hi := 0, len(innerSorted)
		for lo < hi {
			steps++
			mid := (lo + hi) / 2
			if innerSorted[mid].Key < o.Key {
				lo = mid + 1
			} else {
				hi = mid
			}
		}
		for ; lo < len(innerSorted) && innerSorted[lo].Key == o.Key; lo++ {
			out = append(out, Pair{o.Value, innerSorted[lo].Value})
		}
	}
	return out, steps
}

// HashJoin builds a map on the inner side and probes it once per outer row: N + M operations. Equality only.
func HashJoin(outer, inner []Row) ([]Pair, int) {
	table := map[int][]string{}
	for _, in := range inner {
		table[in.Key] = append(table[in.Key], in.Value)
	}
	var out []Pair
	for _, o := range outer {
		for _, v := range table[o.Key] {
			out = append(out, Pair{o.Value, v})
		}
	}
	return out, len(inner) + len(outer)
}

// MergeJoin walks two inputs sorted by key together: about N + M steps.
func MergeJoin(outerSorted, innerSorted []Row) ([]Pair, int) {
	var out []Pair
	steps, i, j := 0, 0, 0
	for i < len(outerSorted) && j < len(innerSorted) {
		steps++
		switch ok, ik := outerSorted[i].Key, innerSorted[j].Key; {
		case ok < ik:
			i++
		case ok > ik:
			j++
		default:
			for k := j; k < len(innerSorted) && innerSorted[k].Key == ok; k++ {
				out = append(out, Pair{outerSorted[i].Value, innerSorted[k].Value})
			}
			i++ // the next outer row may share the key, so j stays at the start of the group
		}
	}
	return out, steps
}

// SortedByKey returns a copy sorted by key; SortStableFunc keeps equal keys in their original order.
func SortedByKey(rows []Row) []Row {
	out := slices.Clone(rows)
	slices.SortStableFunc(out, func(a, b Row) int { return a.Key - b.Key })
	return out
}

// IndependentEstimate is what a planner assumes for `a AND b` without extended statistics.
func IndependentEstimate(rows float64, selectivities ...float64) float64 {
	for _, s := range selectivities {
		rows *= s
	}
	return rows
}

// RowsReadForPage: OFFSET reads every skipped row; keyset pagination starts at the right place.
func RowsReadForPage(offset, limit int, keyset bool) int {
	if keyset {
		return limit
	}
	return offset + limit
}
