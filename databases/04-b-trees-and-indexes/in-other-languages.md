# B-Trees and Indexes in Other Languages

**[Intermediate → Advanced]** — A companion to [[databases/04-b-trees-and-indexes/index|B-trees and indexes]], which builds a B+ tree model and then checks a million-row PostgreSQL index for real: its depth, the four pages per lookup, the composite index and index-only scan. This page does the same in TypeScript, Go, Java, Rust and C#. Each lab has the full model and the same core PostgreSQL checks through its language's driver (node-postgres, pgx, the PostgreSQL JDBC driver, the `postgres` crate, Npgsql). Two things differ more than you'd expect. One is how each language holds a tree whose leaves point sideways at each other. The other is the small, sharp ways each driver hands back what PostgreSQL sent.

## Before you start

You can already:

- Build the B+ tree model, read `EXPLAIN (ANALYZE, BUFFERS)`, and explain the leftmost-prefix rule → [[databases/04-b-trees-and-indexes/index|the main lesson]].
- Connect to a database from at least one of the languages here.

After this lesson you will be able to:

1. Represent a B+ tree with linked leaves in your language, including Rust, where the obvious version doesn't compile.
2. Connect your language's PostgreSQL driver to a local database, and run setup scripts that include `VACUUM`.
3. Read an `EXPLAIN … FORMAT JSON` plan through your driver, and know what type each value arrives as.

## The kid version

Five people are handed the same library's catalogue, written in five languages. They all find the same book in the same four steps. But one is handed page numbers as words ("twelve") instead of digits, one gets the catalogue as a single block of text to cut up themselves, and one can only get into the library by the front door, not the side entrance the others use. The library is the same; the getting in and the reading are not.

**Where the analogy stops working.** A person reading "twelve" understands it. A program comparing the text `"2"` with the number `2` gets "not equal" and fails, with no hint that the value was right all along. Knowing exactly what type your driver gives you is most of this page.

## 1. The tools, by ecosystem

| Language | Driver | Connects with | `bigint` arrives as | A `json` column arrives as |
|---|---|---|---|---|
| Python | psycopg 3 | `PG*` environment variables, socket or TCP | `int` | parsed: lists and dicts |
| TypeScript | **node-postgres** (`pg`) | `PG*` variables, socket or TCP | **a string** | parsed: arrays and objects |
| Go | **pgx** v5 | `PG*` variables (`pgx.Connect(ctx, "")`), socket or TCP | `int64` | decoded into the Go value you scan into |
| Java | **PostgreSQL JDBC** | a `jdbc:postgresql://` URL; **TCP only** | `long` | **text**: parse it yourself (Jackson) |
| Rust | the **`postgres`** crate (sync; `tokio-postgres` underneath) | a `Config` you build; it **ignores `PG*`**; a host starting with `/` is a socket | `i64` | `serde_json::Value`, with the `with-serde_json-1` feature |
| C# | **Npgsql** | a connection string; socket or TCP | `long` | **text** by default |

The labs share one setup file, `labs/shared/orders.sql`, and the same throwaway cluster script. The script now listens on a random port of `127.0.0.1` as well as a Unix socket: JDBC needs TCP, and the C# container reaches the database over the host's network. C and C++ would use libpq, PostgreSQL's own C library. psycopg wraps libpq; node-postgres, pgx, pgjdbc, Npgsql and the Rust crate each implement PostgreSQL's wire protocol themselves, which is why their small behaviours differ. C and C++ aren't where a web service's queries are usually written, so they have no lab here.

## 2. What changes between languages

### A tree whose leaves point sideways

A B+ tree's leaf is pointed to twice: by its parent, and by the leaf before it. In TypeScript, Python, Java, C# and Go, that's two ordinary references. TypeScript uses a discriminated union (`kind: "leaf" | "internal"`), Java a `sealed` interface with a pattern-matching `switch`, C# an abstract class with two subclasses, and Go one struct whose `children` is `nil` for a leaf, since Go has no sum types.

**Rust** won't let a node be owned by its parent *and* mutably reachable from its neighbour through plain references. The idiomatic answer is an **arena**: every node lives in one `Vec<Node>`, and parents and neighbours refer to each other by index. Splits push the new node onto the end of the arena, and links are just numbers.

**Go** has a subtler trap. After a split, `n.keys[:mid]` and `n.keys[mid:]` share one backing array. Append to the left half and you overwrite the start of the right half. The lab copies the right half (`clone`) and caps the left half (`n.keys[:mid:mid]`), so neither can write into the other.

**Java** stores keys as boxed `Integer`s in a `List`. Comparing one with an `int` unboxes it, which is correct; comparing two `Integer`s with `==` compares references, which happens to work for small values and silently fails for large ones. **C#**'s `List.BinarySearch` returns the insertion point's bitwise complement when a key is absent, so `~i` is where to insert.

### Several statements in one call are one transaction

The setup file ends with `VACUUM ANALYZE orders`. Every driver that sends a multi-statement string in one call sends it as one *simple query*, which PostgreSQL runs as a single implicit transaction, and `VACUUM` refuses to run inside a transaction. psycopg, node-postgres, pgx, JDBC, the Rust crate and Npgsql all behave the same way. So every lab splits the file on `";\n"` and runs the statements one at a time.

### What the plan looks like when it arrives

`EXPLAIN (… FORMAT JSON)` returns one row with one `json` value: a list holding one object, `{"Plan": {…}, "Planning Time": …, "Execution Time": …}`.

- **node-postgres** parses it for you.
- **pgx** decodes it into whatever you scan into. The first attempt at this lab scanned into `[]map[string]map[string]any`, and failed, because `"Planning Time"` is a number, not an object. The fix is `[]map[string]any` and a type assertion on `"Plan"`. JSON numbers become `float64`.
- **JDBC** and **Npgsql** hand it over as text, parsed with Jackson and `System.Text.Json.Nodes`.
- **Rust**'s crate gives a `serde_json::Value`, with the feature on.

In **PostgreSQL 18**, `Actual Rows` is a decimal (`1.00`), because it's now averaged across loops more precisely, while `Plan Rows` stays a whole number. Code that reads `Actual Rows` as an integer (`as_u64()` in Rust) breaks on 18; read it as a float.

### `bigint` in JavaScript

`bt_metap`'s `level` is a `bigint`. node-postgres returns every `bigint` as a **string**, because a JavaScript number can hold whole numbers exactly only up to 2⁵³, and silently rounding a database ID would be worse. The lab's first run failed with `'2' !== 2`. Either compare with the string, or convert deliberately with `Number(…)` or `BigInt(…)`, or configure `pg.types.setTypeParser` once for the whole application.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| levels for 10⁸ and 10⁶ rows (367 per leaf, fanout 400) | 4 and 3; a binary tree over 10⁸ needs 27 |
| keys 1–10 into nodes of at most 3 | height 3, root `[7]`; search 7 in 3 pages; range 4–8 in 6 |
| a million scrambled keys into nodes of 400 | height 3; any lookup in 3 pages |
| the leftmost-prefix cases | `[a]`, `[a b c]`, none, `[a]`, `[a]`, `[a b]` |
| `bt_metap('orders_pkey')` | level 2 |
| `WHERE id = 424242` | `Index Scan`, 4 pages |
| `(customer_id, created_at)` index | used for customer + date; the hour query is a `Seq Scan` |
| index-only scan | `Heap Fetches` 0 after `VACUUM`, above 0 after an `UPDATE` |

The companions insert the million keys in the order `i × 7919 mod 1,000,000`. That visits every key once because 7919 is prime and shares no factor with a million, and it means the same order in every language without porting a random generator. The skip-scan, selectivity, expression-index, partial-index and WAL checks are in the Python lab only.

## Terms used in this lesson

1. **Driver**: This is the library a program uses to talk to a database: it opens connections, sends queries and turns the results into the language's values.
2. **Simple query**: This is PostgreSQL's protocol message that carries one string of SQL, possibly several statements, run together in one implicit transaction.
3. **Arena**: This is a single collection that owns every node of a data structure, where nodes refer to each other by position rather than by reference.
4. **Backing array**: In Go, this is the array a slice is a window onto. Two slices of the same array see each other's writes.
5. **Boxing**: In Java and C#, this is wrapping a primitive value such as an `int` in an object, as collections require.

## 4. TypeScript

The model uses a discriminated union for nodes and `splice` for splits. The PostgreSQL checks use `pg.Client`, which reads the `PG*` variables; `pg` is a CommonJS package, so it's imported as a default export. The lab installs `pg` with `npm ci` on its first run.

```ts
// btree.ts — a B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule.
// The same model as the Python lab: one node is one page, and every node visited counts as one page read.

export function levels(rows: number, keysPerLeaf: number, fanout: number): number {
  const leaves = Math.ceil(rows / keysPerLeaf);
  return 1 + Math.max(0, Math.ceil(Math.log(leaves) / Math.log(fanout) - 1e-12));
}

interface Leaf<V> {
  kind: "leaf";
  keys: number[];
  values: V[];
  next?: Leaf<V>; // the leaves form a linked list, for range scans
}

interface Internal<V> {
  kind: "internal";
  keys: number[]; // routing only: children[i] holds keys below keys[i]
  children: Node<V>[];
}

type Node<V> = Leaf<V> | Internal<V>;

/** Keys and values live only in the leaves. A node holds at most `maxKeys` keys; one more and it splits. */
export class BPlusTree<V> {
  root: Node<V> = { kind: "leaf", keys: [], values: [] };
  height = 1;
  #maxKeys: number;

  constructor(maxKeys: number) {
    if (maxKeys < 3) throw new RangeError("maxKeys must be at least 3");
    this.#maxKeys = maxKeys;
  }

  /** The value (or undefined) and the pages read: always `height`, because every leaf is at the same depth. */
  search(key: number): [V | undefined, number] {
    let node = this.root;
    let pages = 1;
    while (node.kind === "internal") {
      node = node.children[child(node, key)];
      pages++;
    }
    const i = find(node.keys, key);
    return [node.keys[i] === key ? node.values[i] : undefined, pages];
  }

  /** Values for lo <= key <= hi, and pages read: down the tree once, then along the leaf chain. */
  range(lo: number, hi: number): [V[], number] {
    let node: Node<V> = this.root;
    let pages = 1;
    while (node.kind === "internal") {
      node = node.children[child(node, lo)];
      pages++;
    }
    const found: V[] = [];
    for (let leaf: Leaf<V> | undefined = node; leaf; ) {
      for (let i = 0; i < leaf.keys.length; i++) {
        if (leaf.keys[i] > hi) return [found, pages];
        if (leaf.keys[i] >= lo) found.push(leaf.values[i]);
      }
      leaf = leaf.next;
      if (leaf) pages++;
    }
    return [found, pages];
  }

  insert(key: number, value: V): void {
    const split = this.#insert(this.root, key, value);
    if (split) {
      this.root = { kind: "internal", keys: [split[0]], children: [this.root, split[1]] }; // the tree grows a level
      this.height++;
    }
  }

  #insert(node: Node<V>, key: number, value: V): [number, Node<V>] | undefined {
    if (node.kind === "leaf") {
      const i = find(node.keys, key);
      if (node.keys[i] === key) {
        node.values[i] = value;
        return undefined;
      }
      node.keys.splice(i, 0, key);
      node.values.splice(i, 0, value);
      if (node.keys.length <= this.#maxKeys) return undefined;
      const mid = node.keys.length >> 1; // the right half's first key is copied up
      const right: Leaf<V> = { kind: "leaf", keys: node.keys.splice(mid), values: node.values.splice(mid), next: node.next };
      node.next = right;
      return [right.keys[0], right];
    }
    const i = child(node, key);
    const split = this.#insert(node.children[i], key, value);
    if (!split) return undefined;
    node.keys.splice(i, 0, split[0]);
    node.children.splice(i + 1, 0, split[1]);
    if (node.keys.length <= this.#maxKeys) return undefined;
    const mid = node.keys.length >> 1; // an internal split moves the middle key up rather than copying it
    const up = node.keys[mid];
    const sibling: Internal<V> = { kind: "internal", keys: node.keys.splice(mid + 1), children: node.children.splice(mid + 1) };
    node.keys.pop(); // remove `up`, which now lives in the parent
    return [up, sibling];
  }
}

function find(keys: number[], key: number): number {
  let lo = 0;
  let hi = keys.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (keys[mid] < key) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function child<V>(node: Internal<V>, key: number): number {
  let i = 0;
  while (i < node.keys.length && key >= node.keys[i]) i++;
  return i;
}

/** The index columns that narrow a search: equality columns from the left, then at most one range column. */
export function usablePrefix(index: string[], equal: Set<string>, ranges: Set<string>): string[] {
  const used: string[] = [];
  for (const column of index) {
    if (equal.has(column)) used.push(column);
    else if (ranges.has(column)) {
      used.push(column);
      break;
    } else break;
  }
  return used;
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { BPlusTree, levels, usablePrefix } from "./btree.ts";

test("why not a binary tree", () => {
  assert.equal(Math.ceil(Math.log2(1e8)), 27);
  assert.deepEqual([levels(1e8, 367, 400), levels(1e6, 367, 400)], [4, 3]);
});

test("splits keep every leaf at the same depth, and a lookup reads one page per level", () => {
  const tree = new BPlusTree<string>(3);
  for (let k = 1; k <= 10; k++) tree.insert(k, `v${k}`);
  assert.equal(tree.height, 3);
  assert.deepEqual(tree.root.keys, [7]);
  assert.deepEqual(tree.search(7), ["v7", 3]);
  assert.deepEqual(tree.search(99), [undefined, 3]);
  assert.deepEqual(tree.range(4, 8), [["v4", "v5", "v6", "v7", "v8"], 6]);
});

test("a million keys, three pages", () => {
  const tree = new BPlusTree<number>(400);
  for (let i = 0; i < 1_000_000; i++) tree.insert((i * 7919) % 1_000_000, i); // every key once, in a scrambled order
  assert.equal(tree.height, 3);
  assert.equal(tree.search(424_242)[1], 3);
});

test("the leftmost prefix rule", () => {
  const index = ["a", "b", "c"];
  const check = (eq: string[], ranges: string[]) => usablePrefix(index, new Set(eq), new Set(ranges));
  assert.deepEqual(check(["a"], []), ["a"]);
  assert.deepEqual(check(["a", "b", "c"], []), ["a", "b", "c"]);
  assert.deepEqual(check(["b"], []), []);
  assert.deepEqual(check(["a", "c"], []), ["a"]);
  assert.deepEqual(check(["b"], ["a"]), ["a"]);
  assert.deepEqual(check(["a"], ["b"]), ["a", "b"]);
});
```

```ts
// The same PostgreSQL checks through node-postgres. Run through ../shared/with-postgres.sh, which sets PGHOST etc.
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import pg from "pg"; // a CommonJS package: its default export holds Client, Pool and the rest

const db = new pg.Client(); // reads PGHOST, PGPORT, PGUSER and PGDATABASE, like psql does

type PlanNode = Record<string, any> & { Plans?: PlanNode[] };

function* nodes(plan: PlanNode): Generator<PlanNode> {
  yield plan;
  for (const child of plan.Plans ?? []) yield* nodes(child);
}

async function explain(sql: string): Promise<PlanNode[]> {
  const { rows } = await db.query(`EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) ${sql}`);
  return [...nodes(rows[0]["QUERY PLAN"][0].Plan)]; // pg parses the json column for us
}

const pages = (plan: PlanNode[]) => plan[0]["Shared Hit Blocks"] + plan[0]["Shared Read Blocks"];

before(async () => {
  await db.connect();
  const setup = readFileSync(new URL("../shared/orders.sql", import.meta.url), "utf8");
  for (const statement of setup.split(";\n")) {
    if (statement.replace(/--.*$/gm, "").trim()) await db.query(statement); // one at a time, as VACUUM requires
  }
});

after(() => db.end());

test("three levels, and a lookup reads four pages", async () => {
  const { rows } = await db.query("SELECT level FROM bt_metap('orders_pkey')");
  assert.equal(rows[0].level, "2"); // a bigint arrives as a string: a JavaScript number can't hold every 64-bit value
  const plan = await explain("SELECT * FROM orders WHERE id = 424242");
  assert.deepEqual([plan[0]["Node Type"], pages(plan)], ["Index Scan", 4]);
});

test("a composite index serves its leading column, not the second alone", async () => {
  await db.query("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)");
  try {
    const both = await explain("SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'");
    assert.ok(both.some((n) => n["Index Name"] === "orders_customer_created"));
    const hour = await explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'");
    assert.equal(hour[0]["Node Type"], "Seq Scan");
  } finally {
    await db.query("DROP INDEX orders_customer_created");
  }
});

test("an index-only scan needs a vacuumed table", async () => {
  await db.query("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)");
  try {
    await db.query("VACUUM orders");
    const clean = await explain("SELECT total FROM orders WHERE customer_id = 42");
    assert.deepEqual([clean[0]["Node Type"], clean[0]["Heap Fetches"]], ["Index Only Scan", 0]);
    await db.query("UPDATE orders SET total = total + 1 WHERE customer_id = 42");
    const dirty = await explain("SELECT total FROM orders WHERE customer_id = 42");
    assert.ok(dirty[0]["Heap Fetches"] > 0);
  } finally {
    await db.query("DROP INDEX orders_customer_total");
  }
});
```

**Lab:** [`labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/typescript). `python3 labs/run.py b-trees-and-indexes/typescript`.

## 5. Go

One `node` struct serves as both leaf and internal node. `insertAt` and `clone` keep split halves from sharing a backing array. The PostgreSQL test skips without `PGHOST`, so `go test` works anywhere, and runs the checks as subtests of one test, so the million rows load once.

```go
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
```

```go
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
```

```go
package btree

// The same PostgreSQL checks through pgx. Run through ../shared/with-postgres.sh, which sets PGHOST etc.;
// without it, these tests skip.

import (
	"context"
	"os"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5"
)

type planNode = map[string]any

func nodes(plan planNode) []planNode {
	out := []planNode{plan}
	children, _ := plan["Plans"].([]any)
	for _, c := range children {
		out = append(out, nodes(c.(planNode))...)
	}
	return out
}

func connect(t *testing.T) (*pgx.Conn, context.Context) {
	t.Helper()
	if os.Getenv("PGHOST") == "" {
		t.Skip("no PostgreSQL: run through ../shared/with-postgres.sh")
	}
	ctx := context.Background()
	conn, err := pgx.Connect(ctx, "") // an empty string: take everything from the PG* environment variables
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { conn.Close(ctx) })
	setup, err := os.ReadFile("../shared/orders.sql")
	if err != nil {
		t.Fatal(err)
	}
	for _, statement := range strings.Split(string(setup), ";\n") {
		if strings.TrimSpace(stripComments(statement)) != "" {
			if _, err := conn.Exec(ctx, statement); err != nil { // one at a time, as VACUUM requires
				t.Fatal(err)
			}
		}
	}
	return conn, ctx
}

func stripComments(sql string) string {
	var lines []string
	for _, line := range strings.Split(sql, "\n") {
		if !strings.HasPrefix(strings.TrimSpace(line), "--") {
			lines = append(lines, line)
		}
	}
	return strings.Join(lines, "\n")
}

func explain(t *testing.T, conn *pgx.Conn, ctx context.Context, sql string) []planNode {
	t.Helper()
	// EXPLAIN's JSON is a list holding one object: {"Plan": {…}, "Planning Time": 0.1, …}. Its values have
	// different types, so it decodes into map[string]any, and the plan is picked out with a type assertion.
	var plans []map[string]any
	if err := conn.QueryRow(ctx, "EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) "+sql).Scan(&plans); err != nil {
		t.Fatal(err)
	}
	return nodes(plans[0]["Plan"].(planNode))
}

func pages(plan []planNode) float64 {
	return plan[0]["Shared Hit Blocks"].(float64) + plan[0]["Shared Read Blocks"].(float64) // JSON numbers are float64
}

func TestPostgres(t *testing.T) {
	conn, ctx := connect(t) // one load of the million rows for all the checks below

	t.Run("three levels, and a lookup reads four pages", func(t *testing.T) {
		var level int64
		if err := conn.QueryRow(ctx, "SELECT level FROM bt_metap('orders_pkey')").Scan(&level); err != nil || level != 2 {
			t.Fatal(level, err)
		}
		if plan := explain(t, conn, ctx, "SELECT * FROM orders WHERE id = 424242"); plan[0]["Node Type"] != "Index Scan" || pages(plan) != 4 {
			t.Fatal(plan[0]["Node Type"], pages(plan))
		}
	})

	t.Run("a composite index serves its leading column, not the second alone", func(t *testing.T) {
		conn.Exec(ctx, "CREATE INDEX orders_customer_created ON orders (customer_id, created_at)")
		defer conn.Exec(ctx, "DROP INDEX orders_customer_created")
		used := false
		for _, n := range explain(t, conn, ctx, "SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'") {
			used = used || n["Index Name"] == "orders_customer_created"
		}
		hour := explain(t, conn, ctx, "SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'")
		if !used || hour[0]["Node Type"] != "Seq Scan" {
			t.Fatal(used, hour[0]["Node Type"])
		}
	})

	t.Run("an index-only scan needs a vacuumed table", func(t *testing.T) {
		conn.Exec(ctx, "CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)")
		defer conn.Exec(ctx, "DROP INDEX orders_customer_total")
		conn.Exec(ctx, "VACUUM orders")
		clean := explain(t, conn, ctx, "SELECT total FROM orders WHERE customer_id = 42")
		conn.Exec(ctx, "UPDATE orders SET total = total + 1 WHERE customer_id = 42")
		dirty := explain(t, conn, ctx, "SELECT total FROM orders WHERE customer_id = 42")
		if clean[0]["Node Type"] != "Index Only Scan" || clean[0]["Heap Fetches"] != 0.0 || dirty[0]["Heap Fetches"].(float64) == 0 {
			t.Fatal(clean[0]["Heap Fetches"], dirty[0]["Heap Fetches"])
		}
	})
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/go). `python3 labs/run.py b-trees-and-indexes/go`.

## 6. Java

Nodes are a `sealed` interface with two final classes, and `insert` is a `switch` over them that the compiler checks is complete. The checks connect with a `jdbc:postgresql://127.0.0.1:…` URL, since pgjdbc doesn't open Unix sockets on its own. `check.sh` downloads the driver and Jackson once into the shared jar cache.

```java
package btree;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/** A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule. Same model as the Python lab. */
public final class BTree {
    private BTree() {}

    public static int levels(long rows, int keysPerLeaf, int fanout) {
        double leaves = Math.ceil((double) rows / keysPerLeaf);
        return 1 + Math.max(0, (int) Math.ceil(Math.log(leaves) / Math.log(fanout) - 1e-12));
    }

    /** A sealed interface: a node is exactly one of the two records below, and a switch can tell which. */
    sealed interface Node permits Leaf, Internal {}

    static final class Leaf implements Node {
        final List<Integer> keys = new ArrayList<>();
        final List<String> values = new ArrayList<>();
        Leaf next; // the linked list for range scans
    }

    static final class Internal implements Node {
        final List<Integer> keys = new ArrayList<>(); // routing only
        final List<Node> children = new ArrayList<>();
    }

    public record Found(String value, int pages) {}

    public record Ranged(List<String> values, int pages) {}

    public static final class BPlusTree {
        private final int maxKeys;
        Node root = new Leaf();
        public int height = 1;

        public BPlusTree(int maxKeys) {
            if (maxKeys < 3) throw new IllegalArgumentException("maxKeys must be at least 3");
            this.maxKeys = maxKeys;
        }

        /** The value (null if absent) and the pages read: always the height. */
        public Found search(int key) {
            Node node = root;
            int pages = 1;
            while (node instanceof Internal in) {
                node = in.children.get(child(in, key));
                pages++;
            }
            Leaf leaf = (Leaf) node;
            int i = find(leaf.keys, key);
            return new Found(i < leaf.keys.size() && leaf.keys.get(i) == key ? leaf.values.get(i) : null, pages);
        }

        public Ranged range(int lo, int hi) {
            Node node = root;
            int pages = 1;
            while (node instanceof Internal in) {
                node = in.children.get(child(in, lo));
                pages++;
            }
            List<String> found = new ArrayList<>();
            for (Leaf leaf = (Leaf) node; leaf != null; ) {
                for (int i = 0; i < leaf.keys.size(); i++) {
                    if (leaf.keys.get(i) > hi) return new Ranged(found, pages);
                    if (leaf.keys.get(i) >= lo) found.add(leaf.values.get(i));
                }
                leaf = leaf.next;
                if (leaf != null) pages++;
            }
            return new Ranged(found, pages);
        }

        private record Split(int separator, Node right) {}

        public void insert(int key, String value) {
            Split split = insert(root, key, value);
            if (split != null) {
                Internal top = new Internal(); // the tree grows a level
                top.keys.add(split.separator());
                top.children.add(root);
                top.children.add(split.right());
                root = top;
                height++;
            }
        }

        private Split insert(Node node, int key, String value) {
            return switch (node) {
                case Leaf leaf -> {
                    int i = find(leaf.keys, key);
                    if (i < leaf.keys.size() && leaf.keys.get(i) == key) {
                        leaf.values.set(i, value);
                        yield null;
                    }
                    leaf.keys.add(i, key);
                    leaf.values.add(i, value);
                    if (leaf.keys.size() <= maxKeys) yield null;
                    int mid = leaf.keys.size() / 2; // the right half's first key is copied up
                    Leaf right = new Leaf();
                    right.keys.addAll(leaf.keys.subList(mid, leaf.keys.size()));
                    right.values.addAll(leaf.values.subList(mid, leaf.values.size()));
                    leaf.keys.subList(mid, leaf.keys.size()).clear();
                    leaf.values.subList(mid, leaf.values.size()).clear();
                    right.next = leaf.next;
                    leaf.next = right;
                    yield new Split(right.keys.getFirst(), right);
                }
                case Internal in -> {
                    int i = child(in, key);
                    Split split = insert(in.children.get(i), key, value);
                    if (split == null) yield null;
                    in.keys.add(i, split.separator());
                    in.children.add(i + 1, split.right());
                    if (in.keys.size() <= maxKeys) yield null;
                    int mid = in.keys.size() / 2; // an internal split moves the middle key up
                    int up = in.keys.get(mid);
                    Internal sibling = new Internal();
                    sibling.keys.addAll(in.keys.subList(mid + 1, in.keys.size()));
                    sibling.children.addAll(in.children.subList(mid + 1, in.children.size()));
                    in.keys.subList(mid, in.keys.size()).clear();
                    in.children.subList(mid + 1, in.children.size()).clear();
                    yield new Split(up, sibling);
                }
            };
        }
    }

    // keys.get(i) is a boxed Integer. Compared with an int, as everywhere here, it's unboxed and compared by value.
    // Two Integers compared with == are compared as references, which is only right for small values: a classic trap.
    static int find(List<Integer> keys, int key) {
        int lo = 0;
        int hi = keys.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (keys.get(mid) < key) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    static int child(Internal node, int key) {
        int i = 0;
        while (i < node.keys.size() && key >= node.keys.get(i)) i++;
        return i;
    }

    public static List<String> usablePrefix(List<String> index, Set<String> equal, Set<String> ranges) {
        List<String> used = new ArrayList<>();
        for (String column : index) {
            if (equal.contains(column)) used.add(column);
            else if (ranges.contains(column)) {
                used.add(column);
                break;
            } else break;
        }
        return used;
    }
}
```

```java
package btree;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** The model checks, then the PostgreSQL checks through JDBC. Run through ../shared/with-postgres.sh, with -ea. */
public final class BTreeCheck {
    private BTreeCheck() {}

    public static void main(String[] args) throws Exception {
        assert Math.ceil(Math.log(1e8) / Math.log(2)) == 27;
        assert BTree.levels(100_000_000, 367, 400) == 4 && BTree.levels(1_000_000, 367, 400) == 3;

        var small = new BTree.BPlusTree(3);
        for (int k = 1; k <= 10; k++) small.insert(k, "v" + k);
        assert small.height == 3;
        assert small.search(7).equals(new BTree.Found("v7", 3)) && small.search(99).equals(new BTree.Found(null, 3));
        assert small.range(4, 8).equals(new BTree.Ranged(List.of("v4", "v5", "v6", "v7", "v8"), 6)) : small.range(4, 8);

        var big = new BTree.BPlusTree(400);
        for (int i = 0; i < 1_000_000; i++) big.insert((int) ((long) i * 7919 % 1_000_000), ""); // i * 7919 overflows an int
        assert big.height == 3 && big.search(424_242).pages() == 3;

        var index = List.of("a", "b", "c");
        assert BTree.usablePrefix(index, Set.of("a"), Set.of()).equals(List.of("a"));
        assert BTree.usablePrefix(index, Set.of("a", "b", "c"), Set.of()).equals(index);
        assert BTree.usablePrefix(index, Set.of("b"), Set.of()).isEmpty();
        assert BTree.usablePrefix(index, Set.of("a", "c"), Set.of()).equals(List.of("a"));
        assert BTree.usablePrefix(index, Set.of("b"), Set.of("a")).equals(List.of("a"));
        assert BTree.usablePrefix(index, Set.of("a"), Set.of("b")).equals(List.of("a", "b"));

        // pgjdbc connects over TCP; with-postgres.sh listens on 127.0.0.1 as well as its socket.
        String url = "jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres";
        try (Connection db = DriverManager.getConnection(url); Statement s = db.createStatement()) {
            for (String statement : Files.readString(Path.of("../shared/orders.sql")).split(";\n")) {
                if (!statement.replaceAll("(?m)^--.*$", "").isBlank()) s.execute(statement); // one at a time, for VACUUM
            }
            try (ResultSet r = s.executeQuery("SELECT level FROM bt_metap('orders_pkey')")) {
                r.next();
                assert r.getLong(1) == 2;
            }
            var lookup = explain(s, "SELECT * FROM orders WHERE id = 424242");
            assert lookup.getFirst().get("Node Type").asString().equals("Index Scan") && pages(lookup) == 4;

            s.execute("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)");
            var both = explain(s, "SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'");
            assert both.stream().anyMatch(n -> n.path("Index Name").asString("").equals("orders_customer_created"));
            var hour = explain(s, "SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'");
            assert hour.getFirst().get("Node Type").asString().equals("Seq Scan");
            s.execute("DROP INDEX orders_customer_created");

            s.execute("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)");
            s.execute("VACUUM orders");
            var clean = explain(s, "SELECT total FROM orders WHERE customer_id = 42");
            assert clean.getFirst().get("Node Type").asString().equals("Index Only Scan") && clean.getFirst().get("Heap Fetches").asInt() == 0;
            s.execute("UPDATE orders SET total = total + 1 WHERE customer_id = 42");
            assert explain(s, "SELECT total FROM orders WHERE customer_id = 42").getFirst().get("Heap Fetches").asInt() > 0;
        }
        System.out.println("all b-tree checks passed");
    }

    private static List<JsonNode> explain(Statement s, String sql) throws SQLException {
        try (ResultSet r = s.executeQuery("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) " + sql)) {
            r.next();
            List<JsonNode> out = new ArrayList<>();
            collect(JsonMapper.shared().readTree(r.getString(1)).get(0).get("Plan"), out); // JDBC hands json over as text
            return out;
        }
    }

    private static void collect(JsonNode node, List<JsonNode> out) {
        out.add(node);
        node.path("Plans").forEach(child -> collect(child, out));
    }

    private static int pages(List<JsonNode> plan) {
        return plan.getFirst().get("Shared Hit Blocks").asInt() + plan.getFirst().get("Shared Read Blocks").asInt();
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/java). `python3 labs/run.py b-trees-and-indexes/java`.

## 7. Rust

The tree is an arena: `nodes: Vec<Node>`, with `next: Option<usize>` and `children: Vec<usize>` as indexes. `binary_search` returns `Ok(i)` for a key that's present and `Err(i)` for where to insert one. The PostgreSQL test is an integration test in `tests/`, built against the `postgres` crate as a dev-dependency, so the library itself has none. It builds its `Config` from `PGHOST` and `PGPORT` by hand. The lab runs in release mode, because the million inserts are slow in a debug build.

```rust
//! A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule. Same model as the Python
//! lab. The nodes live in one Vec (an arena) and point at each other by index: a leaf is pointed to by its parent
//! and by the leaf before it, which Rust's ownership rules make awkward with references, and easy with indexes.

pub fn levels(rows: u64, keys_per_leaf: u64, fanout: u64) -> u32 {
    let leaves = rows.div_ceil(keys_per_leaf) as f64;
    1 + ((leaves.ln() / (fanout as f64).ln()) - 1e-12)
        .ceil()
        .max(0.0) as u32
}

enum Node {
    Leaf {
        keys: Vec<u32>,
        values: Vec<String>,
        next: Option<usize>,
    },
    Internal {
        keys: Vec<u32>,
        children: Vec<usize>,
    },
}

pub struct BPlusTree {
    nodes: Vec<Node>,
    root: usize,
    pub height: u32,
    max_keys: usize,
}

impl BPlusTree {
    pub fn new(max_keys: usize) -> Self {
        assert!(max_keys >= 3, "max_keys must be at least 3");
        BPlusTree {
            nodes: vec![Node::Leaf {
                keys: vec![],
                values: vec![],
                next: None,
            }],
            root: 0,
            height: 1,
            max_keys,
        }
    }

    pub fn root_keys(&self) -> &[u32] {
        match &self.nodes[self.root] {
            Node::Leaf { keys, .. } | Node::Internal { keys, .. } => keys,
        }
    }

    /// The leaf holding `key`, and the pages read to get there.
    fn descend(&self, key: u32) -> (usize, u32) {
        let (mut at, mut pages) = (self.root, 1);
        while let Node::Internal { keys, children } = &self.nodes[at] {
            at = children[keys.partition_point(|&k| key >= k)];
            pages += 1;
        }
        (at, pages)
    }

    /// The value, if present, and the pages read: always the height.
    pub fn search(&self, key: u32) -> (Option<&str>, u32) {
        let (at, pages) = self.descend(key);
        let Node::Leaf { keys, values, .. } = &self.nodes[at] else {
            unreachable!("descend stops at a leaf")
        };
        (
            keys.binary_search(&key).ok().map(|i| values[i].as_str()),
            pages,
        )
    }

    pub fn range(&self, lo: u32, hi: u32) -> (Vec<&str>, u32) {
        let (mut at, mut pages) = self.descend(lo);
        let mut found = Vec::new();
        loop {
            let Node::Leaf { keys, values, next } = &self.nodes[at] else {
                unreachable!()
            };
            for (k, v) in keys.iter().zip(values) {
                if *k > hi {
                    return (found, pages);
                }
                if *k >= lo {
                    found.push(v.as_str());
                }
            }
            match next {
                Some(n) => (at, pages) = (*n, pages + 1),
                None => return (found, pages),
            }
        }
    }

    pub fn insert(&mut self, key: u32, value: String) {
        if let Some((separator, right)) = self.insert_at(self.root, key, value) {
            self.nodes.push(Node::Internal {
                keys: vec![separator],
                children: vec![self.root, right],
            }); // a new level
            self.root = self.nodes.len() - 1;
            self.height += 1;
        }
    }

    fn insert_at(&mut self, at: usize, key: u32, value: String) -> Option<(u32, usize)> {
        let new_index = self.nodes.len(); // where a split's right half will go
        match &mut self.nodes[at] {
            Node::Leaf { keys, values, next } => {
                match keys.binary_search(&key) {
                    Ok(i) => {
                        values[i] = value;
                        return None;
                    }
                    Err(i) => {
                        keys.insert(i, key);
                        values.insert(i, value);
                    }
                }
                if keys.len() <= self.max_keys {
                    return None;
                }
                let mid = keys.len() / 2; // the right half's first key is copied up
                let right = Node::Leaf {
                    keys: keys.split_off(mid),
                    values: values.split_off(mid),
                    next: next.replace(new_index),
                };
                let separator = match &right {
                    Node::Leaf { keys, .. } => keys[0],
                    Node::Internal { .. } => unreachable!(),
                };
                self.nodes.push(right);
                Some((separator, new_index))
            }
            Node::Internal { keys, children } => {
                let i = keys.partition_point(|&k| key >= k);
                let child = children[i];
                let (separator, right) = self.insert_at(child, key, value)?;
                let new_index = self.nodes.len();
                let Node::Internal { keys, children } = &mut self.nodes[at] else {
                    unreachable!()
                };
                keys.insert(i, separator);
                children.insert(i + 1, right);
                if keys.len() <= self.max_keys {
                    return None;
                }
                let mid = keys.len() / 2; // an internal split moves the middle key up
                let sibling_keys = keys.split_off(mid + 1);
                let up = keys.pop().expect("the middle key");
                let sibling = Node::Internal {
                    keys: sibling_keys,
                    children: children.split_off(mid + 1),
                };
                self.nodes.push(sibling);
                Some((up, new_index))
            }
        }
    }
}

/// The index columns that narrow a search: equality columns from the left, then at most one range column.
pub fn usable_prefix<'a>(index: &[&'a str], equal: &[&str], ranges: &[&str]) -> Vec<&'a str> {
    let mut used = Vec::new();
    for &column in index {
        if equal.contains(&column) {
            used.push(column);
        } else {
            if ranges.contains(&column) {
                used.push(column);
            }
            break;
        }
    }
    used
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn why_not_a_binary_tree() {
        assert_eq!((1e8_f64).log2().ceil(), 27.0);
        assert_eq!(
            (levels(100_000_000, 367, 400), levels(1_000_000, 367, 400)),
            (4, 3)
        );
    }

    #[test]
    fn splits_and_page_reads() {
        let mut tree = BPlusTree::new(3);
        for k in 1..=10 {
            tree.insert(k, format!("v{k}"));
        }
        assert_eq!((tree.height, tree.root_keys()), (3, &[7][..]));
        assert_eq!(tree.search(7), (Some("v7"), 3));
        assert_eq!(tree.search(99), (None, 3));
        assert_eq!(tree.range(4, 8), (vec!["v4", "v5", "v6", "v7", "v8"], 6));
    }

    #[test]
    fn a_million_keys_three_pages() {
        let mut tree = BPlusTree::new(400);
        for i in 0..1_000_000_u64 {
            tree.insert((i * 7919 % 1_000_000) as u32, String::new()); // every key once, in a scrambled order
        }
        assert_eq!((tree.height, tree.search(424_242).1), (3, 3));
    }

    #[test]
    fn the_leftmost_prefix_rule() {
        let index = ["a", "b", "c"];
        assert_eq!(usable_prefix(&index, &["a"], &[]), ["a"]);
        assert_eq!(
            usable_prefix(&index, &["a", "b", "c"], &[]),
            ["a", "b", "c"]
        );
        assert!(usable_prefix(&index, &["b"], &[]).is_empty());
        assert_eq!(usable_prefix(&index, &["a", "c"], &[]), ["a"]);
        assert_eq!(usable_prefix(&index, &["b"], &["a"]), ["a"]);
        assert_eq!(usable_prefix(&index, &["a"], &["b"]), ["a", "b"]);
    }
}
```

```rust
//! The same PostgreSQL checks through the `postgres` crate. Run through ../shared/with-postgres.sh; without
//! PGHOST set, it does nothing.
use postgres::{Client, Config, NoTls};
use serde_json::Value;

fn nodes(plan: &Value, out: &mut Vec<Value>) {
    out.push(plan.clone());
    for child in plan["Plans"].as_array().into_iter().flatten() {
        nodes(child, out);
    }
}

fn explain(db: &mut Client, sql: &str) -> Vec<Value> {
    let row = db
        .query_one(
            &format!("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}"),
            &[],
        )
        .unwrap();
    let json: Value = row.get(0); // the with-serde_json-1 feature turns a json column into a serde_json::Value
    let mut out = Vec::new();
    nodes(&json[0]["Plan"], &mut out);
    out
}

fn pages(plan: &[Value]) -> u64 {
    plan[0]["Shared Hit Blocks"].as_u64().unwrap() + plan[0]["Shared Read Blocks"].as_u64().unwrap()
}

#[test]
fn postgres() {
    let Ok(host) = std::env::var("PGHOST") else {
        return;
    }; // no database: nothing to check
    let port: u16 = std::env::var("PGPORT").unwrap().parse().unwrap();
    // The crate doesn't read PG* variables itself. A host starting with "/" is a Unix-socket folder.
    let mut db = Config::new()
        .host(&host)
        .port(port)
        .user("postgres")
        .dbname("postgres")
        .connect(NoTls)
        .unwrap();
    let setup = std::fs::read_to_string("../shared/orders.sql").unwrap();
    for statement in setup.split(";\n") {
        let code: String = statement
            .lines()
            .filter(|l| !l.trim_start().starts_with("--"))
            .collect();
        if !code.trim().is_empty() {
            db.batch_execute(statement).unwrap(); // one at a time, as VACUUM requires
        }
    }

    let level: i64 = db
        .query_one("SELECT level FROM bt_metap('orders_pkey')", &[])
        .unwrap()
        .get(0); // bigint is i64
    assert_eq!(level, 2);
    let lookup = explain(&mut db, "SELECT * FROM orders WHERE id = 424242");
    assert_eq!(
        (lookup[0]["Node Type"].as_str(), pages(&lookup)),
        (Some("Index Scan"), 4)
    );

    db.batch_execute("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)")
        .unwrap();
    let both = explain(
        &mut db,
        "SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'",
    );
    assert!(
        both.iter()
            .any(|n| n["Index Name"] == "orders_customer_created")
    );
    let hour = explain(
        &mut db,
        "SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'",
    );
    assert_eq!(hour[0]["Node Type"], "Seq Scan");
    db.batch_execute("DROP INDEX orders_customer_created")
        .unwrap();

    db.batch_execute("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)")
        .unwrap();
    db.batch_execute("VACUUM orders").unwrap();
    let clean = explain(&mut db, "SELECT total FROM orders WHERE customer_id = 42");
    assert_eq!(
        (
            clean[0]["Node Type"].as_str(),
            clean[0]["Heap Fetches"].as_u64()
        ),
        (Some("Index Only Scan"), Some(0))
    );
    db.batch_execute("UPDATE orders SET total = total + 1 WHERE customer_id = 42")
        .unwrap();
    assert!(
        explain(&mut db, "SELECT total FROM orders WHERE customer_id = 42")[0]["Heap Fetches"]
            .as_u64()
            .unwrap()
            > 0
    );
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/rust). `python3 labs/run.py b-trees-and-indexes/rust`.

## 8. C#

`Leaf` and `Internal` subclass an abstract `Node`; `Insert` switches on the type, and ranges (`leaf.Keys[mid..]`) copy each split's right half. The checks use Npgsql over TCP: `container.sh` runs the .NET SDK container on the host's network and passes `PGPORT` in.

```csharp
// A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule. Same model as the Python lab.

public static class Sizing
{
    public static int Levels(long rows, int keysPerLeaf, int fanout)
    {
        var leaves = Math.Ceiling((double)rows / keysPerLeaf);
        return 1 + Math.Max(0, (int)Math.Ceiling(Math.Log(leaves) / Math.Log(fanout) - 1e-12));
    }

    /// <summary>The index columns that narrow a search: equality columns from the left, then at most one range.</summary>
    public static List<string> UsablePrefix(IEnumerable<string> index, ISet<string> equal, ISet<string> ranges)
    {
        var used = new List<string>();
        foreach (var column in index)
        {
            if (equal.Contains(column)) used.Add(column);
            else
            {
                if (ranges.Contains(column)) used.Add(column);
                break;
            }
        }
        return used;
    }
}

public abstract class Node
{
    public List<int> Keys { get; } = [];
}

public sealed class Leaf : Node
{
    public List<string> Values { get; } = [];
    public Leaf? Next { get; set; } // the linked list for range scans
}

public sealed class Internal : Node
{
    public List<Node> Children { get; } = []; // Keys route: Children[i] holds keys below Keys[i]
}

public sealed class BPlusTree(int maxKeys)
{
    public Node Root { get; private set; } = new Leaf();
    public int Height { get; private set; } = 1;

    /// <summary>The value (null if absent) and the pages read: always the height.</summary>
    public (string? Value, int Pages) Search(int key)
    {
        var (leaf, pages) = Descend(key);
        var i = leaf.Keys.BinarySearch(key);
        return (i >= 0 ? leaf.Values[i] : null, pages);
    }

    public (List<string> Values, int Pages) Range(int lo, int hi)
    {
        var (leaf, pages) = Descend(lo);
        var found = new List<string>();
        for (Leaf? at = leaf; at is not null;)
        {
            for (var i = 0; i < at.Keys.Count; i++)
            {
                if (at.Keys[i] > hi) return (found, pages);
                if (at.Keys[i] >= lo) found.Add(at.Values[i]);
            }
            at = at.Next;
            if (at is not null) pages++;
        }
        return (found, pages);
    }

    private (Leaf, int) Descend(int key)
    {
        var (node, pages) = (Root, 1);
        while (node is Internal internalNode)
        {
            node = internalNode.Children[Child(internalNode, key)];
            pages++;
        }
        return ((Leaf)node, pages);
    }

    public void Insert(int key, string value)
    {
        if (Insert(Root, key, value) is not var (separator, right)) return;
        var top = new Internal(); // the tree grows a level
        top.Keys.Add(separator);
        top.Children.AddRange([Root, right]);
        Root = top;
        Height++;
    }

    private (int, Node)? Insert(Node node, int key, string value)
    {
        switch (node)
        {
            case Leaf leaf:
            {
                var i = leaf.Keys.BinarySearch(key);
                if (i >= 0)
                {
                    leaf.Values[i] = value;
                    return null;
                }
                leaf.Keys.Insert(~i, key); // BinarySearch returns the complement of the insertion point
                leaf.Values.Insert(~i, value);
                if (leaf.Keys.Count <= maxKeys) return null;
                var mid = leaf.Keys.Count / 2; // the right half's first key is copied up
                var right = new Leaf { Next = leaf.Next };
                right.Keys.AddRange(leaf.Keys[mid..]);
                right.Values.AddRange(leaf.Values[mid..]);
                leaf.Keys.RemoveRange(mid, leaf.Keys.Count - mid);
                leaf.Values.RemoveRange(mid, leaf.Values.Count - mid);
                leaf.Next = right;
                return (right.Keys[0], right);
            }
            case Internal internalNode:
            {
                var i = Child(internalNode, key);
                if (Insert(internalNode.Children[i], key, value) is not var (separator, right)) return null;
                internalNode.Keys.Insert(i, separator);
                internalNode.Children.Insert(i + 1, right);
                if (internalNode.Keys.Count <= maxKeys) return null;
                var mid = internalNode.Keys.Count / 2; // an internal split moves the middle key up
                var up = internalNode.Keys[mid];
                var sibling = new Internal();
                sibling.Keys.AddRange(internalNode.Keys[(mid + 1)..]);
                sibling.Children.AddRange(internalNode.Children[(mid + 1)..]);
                internalNode.Keys.RemoveRange(mid, internalNode.Keys.Count - mid);
                internalNode.Children.RemoveRange(mid + 1, internalNode.Children.Count - mid - 1);
                return (up, sibling);
            }
            default:
                throw new InvalidOperationException("unknown node");
        }
    }

    private static int Child(Internal node, int key)
    {
        var i = 0;
        while (i < node.Keys.Count && key >= node.Keys[i]) i++;
        return i;
    }
}
```

```csharp
// The model checks, then the PostgreSQL checks through Npgsql.
using System.Text.Json.Nodes;
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

Check(Math.Ceiling(Math.Log2(1e8)) == 27, "binary");
Check(Sizing.Levels(100_000_000, 367, 400) == 4 && Sizing.Levels(1_000_000, 367, 400) == 3, "levels");

var small = new BPlusTree(3);
for (var k = 1; k <= 10; k++) small.Insert(k, $"v{k}");
Check(small.Height == 3 && small.Root.Keys.SequenceEqual([7]), small.Height);
Check(small.Search(7) == ("v7", 3) && small.Search(99) == (null, 3), small.Search(7));
var range = small.Range(4, 8);
Check(range.Values.SequenceEqual(["v4", "v5", "v6", "v7", "v8"]) && range.Pages == 6, range.Pages);

var big = new BPlusTree(400);
for (var i = 0; i < 1_000_000; i++) big.Insert((int)((long)i * 7919 % 1_000_000), ""); // i * 7919 overflows an int
Check(big.Height == 3 && big.Search(424_242).Pages == 3, big.Height);

string[] index = ["a", "b", "c"];
List<string> Usable(string[] eq, string[] ranges) => Sizing.UsablePrefix(index, eq.ToHashSet(), ranges.ToHashSet());
Check(Usable(["a"], []).SequenceEqual(["a"]) && Usable(["a", "b", "c"], []).SequenceEqual(index) && Usable(["b"], []).Count == 0, "prefix");
Check(Usable(["a", "c"], []).SequenceEqual(["a"]) && Usable(["b"], ["a"]).SequenceEqual(["a"]) && Usable(["a"], ["b"]).SequenceEqual(["a", "b"]), "prefix");

// Npgsql over TCP: the container shares the host's network, where the throwaway database listens on 127.0.0.1.
await using var db = new NpgsqlConnection($"Host=127.0.0.1;Port={Environment.GetEnvironmentVariable("PGPORT")};Username=postgres;Database=postgres");
await db.OpenAsync();
async Task Run(string sql)
{
    await using var command = new NpgsqlCommand(sql, db);
    await command.ExecuteNonQueryAsync();
}
async Task<List<JsonNode>> Explain(string sql)
{
    await using var command = new NpgsqlCommand($"EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}", db);
    var plan = JsonNode.Parse((string)(await command.ExecuteScalarAsync())!)![0]!["Plan"]!; // json arrives as text
    var nodes = new List<JsonNode>();
    void Collect(JsonNode node)
    {
        nodes.Add(node);
        foreach (var child in node["Plans"]?.AsArray() ?? []) Collect(child!);
    }
    Collect(plan);
    return nodes;
}
static int Pages(List<JsonNode> plan) => (int)plan[0]["Shared Hit Blocks"]! + (int)plan[0]["Shared Read Blocks"]!;

foreach (var statement in File.ReadAllText("../shared/orders.sql").Split(";\n"))
    if (statement.Split('\n').Any(line => line.Trim() != "" && !line.TrimStart().StartsWith("--"))) await Run(statement); // one at a time

await using (var level = new NpgsqlCommand("SELECT level FROM bt_metap('orders_pkey')", db))
    Check((long)(await level.ExecuteScalarAsync())! == 2, "level"); // bigint arrives as long
var lookup = await Explain("SELECT * FROM orders WHERE id = 424242");
Check((string?)lookup[0]["Node Type"] == "Index Scan" && Pages(lookup) == 4, Pages(lookup));

await Run("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)");
var both = await Explain("SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'");
Check(both.Any(n => (string?)n["Index Name"] == "orders_customer_created"), "composite used");
var hour = await Explain("SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'");
Check((string?)hour[0]["Node Type"] == "Seq Scan", hour[0]["Node Type"]);
await Run("DROP INDEX orders_customer_created");

await Run("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)");
await Run("VACUUM orders");
var clean = await Explain("SELECT total FROM orders WHERE customer_id = 42");
Check((string?)clean[0]["Node Type"] == "Index Only Scan" && (int)clean[0]["Heap Fetches"]! == 0, clean[0]["Heap Fetches"]);
await Run("UPDATE orders SET total = total + 1 WHERE customer_id = 42");
Check((int)(await Explain("SELECT total FROM orders WHERE customer_id = 42"))[0]["Heap Fetches"]! > 0, "dirty");
Console.WriteLine("all b-tree checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/04-b-trees-and-indexes/labs/csharp). `python3 labs/run.py b-trees-and-indexes/csharp`.

## Common pitfalls

1. **Running a setup script with `VACUUM` in one call.** It's one transaction, and `VACUUM` refuses. Split it.
2. **Comparing a `bigint` from node-postgres with a number.** It's a string. Convert deliberately, once.
3. **Decoding `EXPLAIN` JSON into a too-specific type in Go.** The top level mixes objects and numbers; decode into `map[string]any`.
4. **Reading PostgreSQL 18's `Actual Rows` as an integer.** It's a decimal now.
5. **Slicing a Go slice in two and appending to the first half.** It overwrites the second. Copy or cap.
6. **Comparing two Java `Integer`s with `==`.** It compares references. Use `equals`, or unbox.
7. **Expecting the Rust `postgres` crate or JDBC to read `PGHOST`.** They don't; pass the settings in.

## Check your understanding

1. Why does the Rust tree keep its nodes in a `Vec` and link them by index?
2. What goes wrong in Go if a leaf splits into `n.keys[:mid]` and `n.keys[mid:]` without copying, and a key is then inserted into the left half?
3. A setup script of five statements, the last `VACUUM ANALYZE`, fails in every language when sent in one call. Why?
4. Why does node-postgres return `bigint` as a string, and what are two ways to handle it?
5. Why does the Java lab connect to `127.0.0.1` when the others use a Unix socket?

<details>
<summary>Answers — after your attempt</summary>

1. A leaf is reached from its parent and from the previous leaf. With references, that's shared ownership of something that's also mutated during inserts, which the borrow checker rejects. In an arena, the `Vec` owns every node and links are plain `usize` indexes, which can be copied freely; mutation goes through the arena.
2. Both slices share one backing array. Inserting into the left half grows it into the space where the right half's first elements live, overwriting them, so the right leaf silently loses keys. Copy the right half, or cap the left half so an append must allocate.
3. The driver sends the string as one simple query, which PostgreSQL runs in one implicit transaction, and `VACUUM` can't run inside a transaction.
4. A JavaScript number holds whole numbers exactly only up to 2⁵³, and a `bigint` can exceed that, so converting silently could corrupt IDs. Either convert where you know the value is small (`Number(level)`), or use `BigInt`, or set a type parser once for the application.
5. The PostgreSQL JDBC driver speaks only TCP unless you add a Unix-socket library. The throwaway cluster also listens on a random port of 127.0.0.1, so Java connects there.

</details>

## Practice — independent task

**Add a range check to your language's PostgreSQL test.**

1. Add the hour query from the main lesson's skip-scan section, with an index on `(status, created_at)`.
2. Assert the node type, the index name, that it returns 120 rows, and that it reads fewer than 50 pages.
3. Read `Actual Rows` in the way your language needs for PostgreSQL 18's decimal.

**Done when:** your check passes alongside the existing ones, and you can say which part of the value's type you had to look up.

## Before moving on

You can represent a linked-leaf B+ tree in your language, connect its driver to the throwaway database, run setup with `VACUUM` in it, and read a JSON plan with the right types.

**Recap.** The B+ tree and the plans are the same everywhere. Rust needs an arena for the sideways leaf links; Go needs care not to share a backing array between split halves; Java's boxed `Integer`s and C#'s complemented `BinarySearch` each have a trap. Every driver runs a multi-statement call as one transaction, so `VACUUM` must go alone. Drivers differ in what they hand back: node-postgres gives `bigint` as a string, JDBC and Npgsql give JSON as text, pgx needs a target type matching the JSON's shape, and PostgreSQL 18's `Actual Rows` is a decimal. JDBC needs TCP, and the Rust crate needs its settings passed in.

## Related

- [[databases/04-b-trees-and-indexes/index|B-trees and indexes]]: the main lesson
- [[databases/07-join-algorithms-and-the-optimiser/in-other-languages|Join algorithms in other languages]]: the same drivers, reading join plans
- [[architecture/03-architectural-patterns/05-transactional-outbox/in-other-languages|Transactional outbox in other languages]]: SQLite drivers and transactions in the same languages
