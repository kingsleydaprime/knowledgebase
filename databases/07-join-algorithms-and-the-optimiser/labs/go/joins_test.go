package joins

import (
	"fmt"
	"math"
	"slices"
	"testing"
)

func data() (orders, customers []Row) {
	for i := range 10_000 {
		orders = append(orders, Row{1 + i%1_000, fmt.Sprintf("order %d", i)})
	}
	for c := 1; c <= 1_000; c++ {
		customers = append(customers, Row{c, fmt.Sprintf("customer %d", c)})
	}
	return orders, customers
}

func canonical(pairs []Pair) []string {
	out := make([]string, len(pairs))
	for i, p := range pairs {
		out[i] = p.Outer + "|" + p.Inner
	}
	slices.Sort(out)
	return out
}

func TestAllThreeGiveTheSameAnswer(t *testing.T) {
	orders, customers := data()
	nl, _ := NestedLoop(orders, customers)
	inl, _ := IndexNestedLoop(orders, customers)
	hj, _ := HashJoin(orders, customers)
	mj, _ := MergeJoin(SortedByKey(orders), customers)
	want := canonical(nl)
	if len(want) != 10_000 || !slices.Equal(canonical(inl), want) || !slices.Equal(canonical(hj), want) || !slices.Equal(canonical(mj), want) {
		t.Fatal("the joins disagree")
	}
}

func TestTheyDifferEnormouslyInWork(t *testing.T) {
	orders, customers := data()
	_, a := NestedLoop(orders, customers)
	_, b := IndexNestedLoop(orders, customers)
	_, c := HashJoin(orders, customers)
	_, d := MergeJoin(SortedByKey(orders), customers)
	if got := []int{a, b, c, d}; !slices.Equal(got, []int{10_000_000, 99_780, 11_000, 10_999}) {
		t.Fatal(got)
	}
	var one []Row
	for _, o := range orders {
		if o.Key == 42 {
			one = append(one, o)
		}
	}
	_, small := IndexNestedLoop(one, customers)
	_, hashed := HashJoin(one, customers)
	if small != 100 || hashed != 1_010 {
		t.Fatal(small, hashed)
	}
}

func TestCorrelatedColumnsAndPagination(t *testing.T) {
	if math.Round(IndependentEstimate(30_000, 0.1, 0.3)) != 900 || math.Round(IndependentEstimate(30_000, 0.1)) != 3_000 {
		t.Fatal("estimates")
	}
	if RowsReadForPage(100_000, 20, false) != 100_020 || RowsReadForPage(100_000, 20, true) != 20 {
		t.Fatal("pagination")
	}
}
