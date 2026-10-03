// Package btree: a B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule.
// The same model as the Python lab: one node is one page, and every node visited counts as one page read.
package btree

import "math"

func Levels(rows, keysPerLeaf, fanout int) int {
	leaves := math.Ceil(float64(rows) / float64(keysPerLeaf))
	return 1 + max(0, int(math.Ceil(math.Log(leaves)/math.Log(float64(fanout))-1e-12)))
}

// node is a leaf when children is nil. Go has no sum types, so one struct holds both shapes.
type node struct {
	keys     []int
	values   []string // leaves only
	children []*node  // internal nodes only
	next     *node    // leaves only: the linked list for range scans
}

func (n *node) leaf() bool { return n.children == nil }

type BPlusTree struct {
	root    *node
	Height  int
	maxKeys int
}

func New(maxKeys int) *BPlusTree {
	return &BPlusTree{root: &node{}, Height: 1, maxKeys: maxKeys}
}

// Search returns the value, whether it was found, and the pages read: always Height.
func (t *BPlusTree) Search(key int) (string, bool, int) {
	n, pages := t.root, 1
	for !n.leaf() {
		n, pages = n.children[child(n, key)], pages+1
	}
	i := find(n.keys, key)
	if i < len(n.keys) && n.keys[i] == key {
		return n.values[i], true, pages
	}
	return "", false, pages
}

// Range returns values for lo <= key <= hi, and pages read: down the tree once, then along the leaves.
func (t *BPlusTree) Range(lo, hi int) ([]string, int) {
	n, pages := t.root, 1
	for !n.leaf() {
		n, pages = n.children[child(n, lo)], pages+1
	}
	var found []string
	for n != nil {
		for i, k := range n.keys {
			if k > hi {
				return found, pages
			}
			if k >= lo {
				found = append(found, n.values[i])
			}
		}
		if n = n.next; n != nil {
			pages++
		}
	}
	return found, pages
}

func (t *BPlusTree) Insert(key int, value string) {
	if sep, right := t.insert(t.root, key, value); right != nil {
		t.root = &node{keys: []int{sep}, children: []*node{t.root, right}} // the tree grows a level
		t.Height++
	}
}

func (t *BPlusTree) insert(n *node, key int, value string) (int, *node) {
	if n.leaf() {
		i := find(n.keys, key)
		if i < len(n.keys) && n.keys[i] == key {
			n.values[i] = value
			return 0, nil
		}
		n.keys = insertAt(n.keys, i, key)
		n.values = insertAt(n.values, i, value)
		if len(n.keys) <= t.maxKeys {
			return 0, nil
		}
		mid := len(n.keys) / 2 // the right half's first key is copied up
		right := &node{keys: clone(n.keys[mid:]), values: clone(n.values[mid:]), next: n.next}
		n.keys, n.values, n.next = n.keys[:mid:mid], n.values[:mid:mid], right
		return right.keys[0], right
	}
	i := child(n, key)
	sep, right := t.insert(n.children[i], key, value)
	if right == nil {
		return 0, nil
	}
	n.keys = insertAt(n.keys, i, sep)
	n.children = insertAt(n.children, i+1, right)
	if len(n.keys) <= t.maxKeys {
		return 0, nil
	}
	mid := len(n.keys) / 2 // an internal split moves the middle key up rather than copying it
	up := n.keys[mid]
	sibling := &node{keys: clone(n.keys[mid+1:]), children: clone(n.children[mid+1:])}
	n.keys, n.children = n.keys[:mid:mid], n.children[:mid+1:mid+1]
	return up, sibling
}

// insertAt and clone keep halves from sharing a backing array: with Go slices, appending to the left half
// after a split would otherwise overwrite the start of the right half.
func insertAt[T any](s []T, i int, v T) []T {
	var zero T
	s = append(s, zero)
	copy(s[i+1:], s[i:])
	s[i] = v
	return s
}

func clone[T any](s []T) []T { return append([]T(nil), s...) }

func find(keys []int, key int) int {
	lo, hi := 0, len(keys)
	for lo < hi {
		mid := (lo + hi) / 2
		if keys[mid] < key {
			lo = mid + 1
		} else {
			hi = mid
		}
	}
	return lo
}

func child(n *node, key int) int {
	i := 0
	for i < len(n.keys) && key >= n.keys[i] {
		i++
	}
	return i
}

// UsablePrefix returns the index columns that narrow a search: equality columns from the left, then one range.
func UsablePrefix(index []string, equal, ranges map[string]bool) []string {
	used := []string{}
	for _, c := range index {
		if equal[c] {
			used = append(used, c)
		} else if ranges[c] {
			return append(used, c)
		} else {
			break
		}
	}
	return used
}
