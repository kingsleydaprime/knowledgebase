package btree

import (
	"math"
	"slices"
	"strconv"
	"testing"
)

func TestWhyNotABinaryTree(t *testing.T) {
	if math.Ceil(math.Log2(1e8)) != 27 || Levels(1e8, 367, 400) != 4 || Levels(1e6, 367, 400) != 3 {
		t.Fatal(Levels(1e8, 367, 400), Levels(1e6, 367, 400))
	}
}

func TestSplitsAndPageReads(t *testing.T) {
	tree := New(3)
	for k := 1; k <= 10; k++ {
		tree.Insert(k, "v"+strconv.Itoa(k))
	}
	if tree.Height != 3 || !slices.Equal(tree.root.keys, []int{7}) {
		t.Fatal(tree.Height, tree.root.keys)
	}
	if v, ok, pages := tree.Search(7); v != "v7" || !ok || pages != 3 {
		t.Fatal(v, ok, pages)
	}
	if _, ok, pages := tree.Search(99); ok || pages != 3 {
		t.Fatal(ok, pages)
	}
	if found, pages := tree.Range(4, 8); !slices.Equal(found, []string{"v4", "v5", "v6", "v7", "v8"}) || pages != 6 {
		t.Fatal(found, pages)
	}
}

func TestAMillionKeysThreePages(t *testing.T) {
	tree := New(400)
	for i := range 1_000_000 {
		tree.Insert(i*7919%1_000_000, "") // every key once, in a scrambled order
	}
	if _, ok, pages := tree.Search(424_242); tree.Height != 3 || !ok || pages != 3 {
		t.Fatal(tree.Height, ok, pages)
	}
}

func TestTheLeftmostPrefixRule(t *testing.T) {
	index := []string{"a", "b", "c"}
	set := func(cols ...string) map[string]bool {
		m := map[string]bool{}
		for _, c := range cols {
			m[c] = true
		}
		return m
	}
	cases := []struct {
		eq, ranges, want []string
	}{
		{[]string{"a"}, nil, []string{"a"}},
		{[]string{"a", "b", "c"}, nil, []string{"a", "b", "c"}},
		{[]string{"b"}, nil, []string{}},
		{[]string{"a", "c"}, nil, []string{"a"}},
		{[]string{"b"}, []string{"a"}, []string{"a"}},
		{[]string{"a"}, []string{"b"}, []string{"a", "b"}},
	}
	for _, c := range cases {
		if got := UsablePrefix(index, set(c.eq...), set(c.ranges...)); !slices.Equal(got, c.want) {
			t.Error(c.eq, c.ranges, got)
		}
	}
}
