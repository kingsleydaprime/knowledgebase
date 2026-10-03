# Join Algorithms and the Optimiser in Other Languages

**[Advanced]** — A companion to [[databases/07-join-algorithms-and-the-optimiser/index|join algorithms and the optimiser]], which writes out the nested loop, index nested loop, hash join and merge join with their step counts, and checks PostgreSQL's choices: a hash join spilling to 16 batches, a correlated-columns misestimate fixed by `CREATE STATISTICS`, and `OFFSET` against keyset pagination. This page does the same in TypeScript, Go, Java, Rust and C#, with the same counts in every language and the same PostgreSQL checks through each driver. The algorithms are where the languages' own data structures show: what a hash join's table is in each language, and why a merge join needs a *stable* sort to give the same answer everywhere.

## Before you start

You can already:

- Trace the four join algorithms and read a plan's estimated and actual rows → [[databases/07-join-algorithms-and-the-optimiser/index|the main lesson]].
- Connect your language's PostgreSQL driver and read a JSON plan → [[databases/04-b-trees-and-indexes/in-other-languages|B-trees and indexes in other languages]].

After this lesson you will be able to:

1. Write a hash join with your language's hash map, and say what its build side costs in memory.
2. Explain why the merge join is given input sorted with a stable sort, and what an unstable sort would change.
3. Run the planner experiments (`work_mem`, `CREATE STATISTICS`, keyset pagination) from your language.

## The kid version

Five classes each match 10,000 lunch orders to 1,000 pupils. Every class gets the same 10,000 matches, and every class that uses the same method does the same amount of work, whatever language the instructions were written in. What differs is the equipment: one class's "hash table" is a set of labelled trays, another's a filing cabinet. The answer and the count of steps don't change; how you write it down does.

**Where the analogy stops working.** Trays don't need memory budgets. A real hash join's table must fit in memory, `work_mem` in PostgreSQL and the heap in your program, and a build side that doesn't fit changes how the join runs, as the 16-batch plan shows.

## 1. The tools, by ecosystem

| Language | The hash join's table | A stable sort for the merge join | Driver |
|---|---|---|---|
| Python | `defaultdict(list)` | `sorted` (stable) | psycopg |
| TypeScript | `Map<number, string[]>` | `Array.prototype.sort` (stable since ES2019) | node-postgres |
| Go | `map[int][]string` | **`slices.SortStableFunc`** (`slices.Sort` isn't stable) | pgx |
| Java | `HashMap` with `computeIfAbsent` | `Comparator` sort on a stream (stable) | PostgreSQL JDBC |
| Rust | `HashMap<u32, Vec<&str>>`, borrowing the inner side's strings | **`sort_by_key`** (stable; `sort_unstable_by_key` isn't) | `postgres` crate |
| C# | LINQ's **`ToLookup`**, a ready-made key → values table | **`OrderBy`** (stable; `List.Sort` isn't) | Npgsql |

The labs share `labs/shared/shop.sql` and the throwaway cluster script, as the B-trees companion does. C and C++ have no lab, for the same reason: libpq is where they'd start, and services aren't usually written there.

## 2. What changes between languages

### The hash table is the language's own

Every lab builds the same table: inner key to a list of inner values, then one probe per outer row, 11,000 operations in all. The interesting differences are in memory:

- **Rust's** table holds `&str` borrowed from the inner rows rather than copies, so building it costs no string allocations. The borrow checker makes sure the inner rows outlive the table.
- **C#'s** `ToLookup` returns an immutable lookup whose indexer gives an empty sequence for a missing key, so the probe needs no "is it there?" branch.
- **Go**'s map, **Java**'s `HashMap` and **TypeScript**'s `Map` all copy references to the strings, which is cheap, but each entry still costs a few dozen bytes of overhead. That's why a database estimates the build side's size before choosing a hash join, and spills when it's wrong.

### Why the merge join's input is sorted stably

The merge join is given orders sorted by customer ID. Ten orders share each ID, and their order *within* an ID doesn't change the joined rows or the 10,999 steps. But it does change the order in which matches are produced, and the labs compare results after sorting them, so any sort would pass. They use a stable sort anyway, because it's deterministic: the same input gives the same output in every language and every run. Go's `slices.Sort`, Rust's `sort_unstable_by_key` and C#'s `List.Sort` don't promise that, and a test that compares unsorted output would then pass or fail by chance.

### Integers that overflow, again

The step counts fit easily in 32 bits. The PostgreSQL setup computes `i::bigint * 7919 % 10000`, because `i * 7919` overflows PostgreSQL's 32-bit `integer` at a million rows, the same overflow as [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/in-other-languages|week 1's companion]]. The Java and C# B-tree labs widen with `(long) i * 7919` for the same reason.

### Reading the planner's numbers

The checks read four kinds of value from the JSON plan:

- **`Hash Batches`** is a whole number.
- **`Plan Rows`** is a whole number.
- **`Actual Rows`** is a **decimal** in PostgreSQL 18.
- **Node types** are strings.

Go's pgx gives every JSON number as `float64`, so the Go test compares with `16.0` and `3000.0`. Rust's `serde_json::Value` distinguishes integers from floats, so `as_u64()` works for `Plan Rows` and `Hash Batches` but not for `Actual Rows`, which needs `as_f64()`. Java's Jackson converts with `asInt()` either way, and C# casts `JsonNode` to `int` or `double` explicitly.

### Session settings travel with the connection

`SET work_mem = '64kB'` and `RESET work_mem` change only the current session, which in these labs is the one connection each test holds. With a connection *pool*, as in a real application, a `SET` lands on whichever pooled connection ran it and stays there for the next borrower. That's why pooled code uses `SET LOCAL` inside a transaction, or sets `work_mem` per role, not per query.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| 10,000 orders joined to 1,000 customers | the same 10,000 rows from all four algorithms |
| steps: nested loop, indexed, hash, merge | 10,000,000; 99,780; 11,000; 10,999 |
| one customer's 10 orders: indexed nested loop, hash | 100; 1,010 |
| independence estimate; the truth | 900; 3,000 |
| `OFFSET 100000 LIMIT 20`; keyset | 100,020 rows read; 20 |
| PostgreSQL hash batches, default and at 64 kB | 1; 16 |
| PostgreSQL estimate before and after `CREATE STATISTICS` | 900 then 3,000 (actual 3,000) |
| PostgreSQL rows under each `Limit` | 100,020 for `OFFSET`, 20 for keyset |

The nested-loop-through-an-index, inequality-join and forced merge-join plans are checked in the Python lab only.

## Terms used in this lesson

1. **Stable sort**: This is a sort that keeps items with equal keys in the order they were in before sorting.
2. **Lookup**: In .NET, this is an immutable collection mapping each key to a sequence of values, built in one pass by `ToLookup`.
3. **Borrowed string**: In Rust, this is a `&str` that refers to text owned elsewhere, so it costs no copy and can't outlive its owner.
4. **Session setting**: This is a PostgreSQL setting changed with `SET`, which lasts for the rest of that connection's session.
5. **Connection pool**: This is a set of open connections an application reuses, handing one to each piece of work in turn.

## 4. TypeScript

Rows are readonly tuples, and the hash join's table is a `Map` of arrays. The tests sort with `Array.prototype.sort`, stable since ES2019, and compare canonical sorted strings. The PostgreSQL checks reuse the B-trees lab's pattern: `pg.Client` from the environment, the setup file run statement by statement.

```ts
// joins.ts — the three join algorithms, written out, each counting its work; and the arithmetic of two classic
// estimation failures. The same model as the Python lab. Rows are [key, value] pairs.

export type Row = readonly [number, string];
export type Joined = [string, string][];

/** For every outer row, look at every inner row: N × M comparisons. */
export function nestedLoop(outer: readonly Row[], inner: readonly Row[]): [Joined, number] {
  const out: Joined = [];
  let comparisons = 0;
  for (const [ok, ov] of outer) {
    for (const [ik, iv] of inner) {
      comparisons++;
      if (ok === ik) out.push([ov, iv]);
    }
  }
  return [out, comparisons];
}

/** The inner side has an index (a sorted list searched by halving): about N × log₂ M steps. */
export function indexNestedLoop(outer: readonly Row[], innerSorted: readonly Row[]): [Joined, number] {
  const out: Joined = [];
  let steps = 0;
  for (const [ok, ov] of outer) {
    let lo = 0;
    let hi = innerSorted.length;
    while (lo < hi) {
      steps++;
      const mid = (lo + hi) >> 1;
      if (innerSorted[mid][0] < ok) lo = mid + 1;
      else hi = mid;
    }
    for (; lo < innerSorted.length && innerSorted[lo][0] === ok; lo++) out.push([ov, innerSorted[lo][1]]);
  }
  return [out, steps];
}

/** Build a hash table on the inner side, probe it once per outer row: N + M operations. Equality only. */
export function hashJoin(outer: readonly Row[], inner: readonly Row[]): [Joined, number] {
  const table = new Map<number, string[]>();
  for (const [ik, iv] of inner) table.set(ik, [...(table.get(ik) ?? []), iv]);
  const out: Joined = [];
  for (const [ok, ov] of outer) for (const iv of table.get(ok) ?? []) out.push([ov, iv]);
  return [out, inner.length + outer.length];
}

/** Both sides sorted by key: walk them together like merging two sorted lists, about N + M steps. */
export function mergeJoin(outerSorted: readonly Row[], innerSorted: readonly Row[]): [Joined, number] {
  const out: Joined = [];
  let steps = 0;
  let i = 0;
  let j = 0;
  while (i < outerSorted.length && j < innerSorted.length) {
    steps++;
    const [ok, ik] = [outerSorted[i][0], innerSorted[j][0]];
    if (ok < ik) i++;
    else if (ok > ik) j++;
    else {
      for (let k = j; k < innerSorted.length && innerSorted[k][0] === ok; k++) out.push([outerSorted[i][1], innerSorted[k][1]]);
      i++; // the next outer row may share the key, so j stays at the start of the group
    }
  }
  return [out, steps];
}

/** What a planner assumes for `a AND b` without extended statistics: the selectivities multiply. */
export function independentEstimate(rows: number, ...selectivities: number[]): number {
  return selectivities.reduce((estimate, s) => estimate * s, rows);
}

/** OFFSET reads and discards every skipped row; keyset pagination starts at the right place. */
export function rowsReadForPage(offset: number, limit: number, keyset: boolean): number {
  return keyset ? limit : offset + limit;
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { hashJoin, indexNestedLoop, independentEstimate, mergeJoin, nestedLoop, rowsReadForPage, type Row } from "./joins.ts";

const ORDERS: Row[] = Array.from({ length: 10_000 }, (_, i) => [1 + (i % 1_000), `order ${i}`]);
const CUSTOMERS: Row[] = Array.from({ length: 1_000 }, (_, i) => [i + 1, `customer ${i + 1}`]);
const byKey = (rows: readonly Row[]) => [...rows].sort((a, b) => a[0] - b[0]); // sort is stable: equal keys keep their order
const canonical = (rows: [string, string][]) => rows.map((r) => r.join("|")).sort();

test("all three algorithms give the same answer", () => {
  const expected = canonical(nestedLoop(ORDERS, CUSTOMERS)[0]);
  assert.equal(expected.length, 10_000);
  assert.deepEqual(canonical(indexNestedLoop(ORDERS, CUSTOMERS)[0]), expected);
  assert.deepEqual(canonical(hashJoin(ORDERS, CUSTOMERS)[0]), expected);
  assert.deepEqual(canonical(mergeJoin(byKey(ORDERS), CUSTOMERS)[0]), expected);
});

test("they differ enormously in work", () => {
  assert.deepEqual(
    [nestedLoop(ORDERS, CUSTOMERS)[1], indexNestedLoop(ORDERS, CUSTOMERS)[1], hashJoin(ORDERS, CUSTOMERS)[1], mergeJoin(byKey(ORDERS), CUSTOMERS)[1]],
    [10_000_000, 99_780, 11_000, 10_999],
  );
});

test("a small outer side makes the indexed nested loop cheapest", () => {
  const oneCustomer = ORDERS.filter(([k]) => k === 42);
  assert.deepEqual([indexNestedLoop(oneCustomer, CUSTOMERS)[1], hashJoin(oneCustomer, CUSTOMERS)[1]], [100, 1_010]);
});

test("correlated columns and pagination", () => {
  assert.deepEqual([Math.round(independentEstimate(30_000, 0.1, 0.3)), Math.round(independentEstimate(30_000, 0.1))], [900, 3_000]);
  assert.deepEqual([rowsReadForPage(100_000, 20, false), rowsReadForPage(100_000, 20, true)], [100_020, 20]);
});
```

```ts
// The PostgreSQL checks through node-postgres. Run through ../shared/with-postgres.sh.
import { after, before, test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import pg from "pg";

const db = new pg.Client();
type PlanNode = Record<string, any> & { Plans?: PlanNode[] };

function* nodes(plan: PlanNode): Generator<PlanNode> {
  yield plan;
  for (const child of plan.Plans ?? []) yield* nodes(child);
}

async function explain(sql: string): Promise<PlanNode[]> {
  const { rows } = await db.query(`EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) ${sql}`);
  return [...nodes(rows[0]["QUERY PLAN"][0].Plan)];
}

before(async () => {
  await db.connect();
  for (const statement of readFileSync(new URL("../shared/shop.sql", import.meta.url), "utf8").split(";\n")) {
    if (statement.replace(/--.*$/gm, "").trim()) await db.query(statement);
  }
});

after(() => db.end());

test("a hash join in one batch, or sixteen when work_mem is too small", async () => {
  const join = "SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id";
  const batches = async () => (await explain(join)).find((n) => n["Node Type"] === "Hash")!["Hash Batches"];
  assert.equal(await batches(), 1);
  await db.query("SET work_mem = '64kB'");
  try {
    assert.equal(await batches(), 16);
  } finally {
    await db.query("RESET work_mem");
  }
});

test("correlated columns: 900 estimated, 3,000 after CREATE STATISTICS", async () => {
  const query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
  const rows = async () => {
    const [top] = await explain(query);
    return [top["Plan Rows"], top["Actual Rows"]];
  };
  assert.deepEqual(await rows(), [900, 3000]);
  await db.query("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses");
  await db.query("ANALYZE addresses");
  assert.deepEqual(await rows(), [3000, 3000]);
});

test("OFFSET reads every row it skips; keyset pagination doesn't", async () => {
  const offset = await explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20");
  const keyset = await explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20");
  assert.deepEqual([offset[1]["Actual Rows"], keyset[1]["Actual Rows"]], [100020, 20]);
});
```

**Lab:** [`labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/typescript). `python3 labs/run.py join-algorithms-and-the-optimiser/typescript`.

## 5. Go

`MergeJoin` uses a `switch` with an initialiser to compare the two keys once. `SortedByKey` uses `slices.SortStableFunc`. The PostgreSQL test compares JSON numbers as `float64`.

```go
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
```

```go
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
```

```go
package joins

// The PostgreSQL checks through pgx. Run through ../shared/with-postgres.sh; without it, these tests skip.

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

func TestPostgres(t *testing.T) {
	if os.Getenv("PGHOST") == "" {
		t.Skip("no PostgreSQL: run through ../shared/with-postgres.sh")
	}
	ctx := context.Background()
	db, err := pgx.Connect(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close(ctx)
	setup, _ := os.ReadFile("../shared/shop.sql")
	for _, statement := range strings.Split(string(setup), ";\n") {
		code := ""
		for _, line := range strings.Split(statement, "\n") {
			if !strings.HasPrefix(strings.TrimSpace(line), "--") {
				code += line
			}
		}
		if strings.TrimSpace(code) != "" {
			if _, err := db.Exec(ctx, statement); err != nil {
				t.Fatal(err)
			}
		}
	}
	explain := func(sql string) []planNode {
		var plans []map[string]any
		if err := db.QueryRow(ctx, "EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) "+sql).Scan(&plans); err != nil {
			t.Fatal(err)
		}
		return nodes(plans[0]["Plan"].(planNode))
	}

	batches := func() any {
		for _, n := range explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id") {
			if n["Node Type"] == "Hash" {
				return n["Hash Batches"]
			}
		}
		return nil
	}
	if b := batches(); b != 1.0 {
		t.Fatal("batches with the default work_mem:", b)
	}
	db.Exec(ctx, "SET work_mem = '64kB'")
	if b := batches(); b != 16.0 {
		t.Fatal("batches with 64kB:", b)
	}
	db.Exec(ctx, "RESET work_mem")

	query := "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'"
	if top := explain(query)[0]; top["Plan Rows"] != 900.0 || top["Actual Rows"] != 3000.0 {
		t.Fatal(top["Plan Rows"], top["Actual Rows"])
	}
	db.Exec(ctx, "CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses")
	db.Exec(ctx, "ANALYZE addresses")
	if top := explain(query)[0]; top["Plan Rows"] != 3000.0 {
		t.Fatal(top["Plan Rows"])
	}

	offset := explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20")
	keyset := explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20")
	if offset[1]["Actual Rows"] != 100020.0 || keyset[1]["Actual Rows"] != 20.0 {
		t.Fatal(offset[1]["Actual Rows"], keyset[1]["Actual Rows"])
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/go). `python3 labs/run.py join-algorithms-and-the-optimiser/go`.

## 6. Java

`Row`, `Pair` and `Result` are records; the hash join's table is a `HashMap` filled with `computeIfAbsent`. The checks connect over TCP with JDBC and parse plans with Jackson, as in the B-trees companion.

```java
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
```

```java
package joins;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.IntStream;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** The model checks, then the PostgreSQL checks through JDBC. Run through ../shared/with-postgres.sh, with -ea. */
public final class JoinsCheck {
    private JoinsCheck() {}

    public static void main(String[] args) throws Exception {
        List<Joins.Row> orders = IntStream.range(0, 10_000).mapToObj(i -> new Joins.Row(1 + i % 1_000, "order " + i)).toList();
        List<Joins.Row> customers = IntStream.rangeClosed(1, 1_000).mapToObj(c -> new Joins.Row(c, "customer " + c)).toList();
        List<Joins.Row> sortedOrders = orders.stream().sorted(Comparator.comparingInt(Joins.Row::key)).toList(); // a stable sort

        var expected = canonical(Joins.nestedLoop(orders, customers).rows());
        assert expected.size() == 10_000;
        assert canonical(Joins.indexNestedLoop(orders, customers).rows()).equals(expected);
        assert canonical(Joins.hashJoin(orders, customers).rows()).equals(expected);
        assert canonical(Joins.mergeJoin(sortedOrders, customers).rows()).equals(expected);

        var work = List.of(Joins.nestedLoop(orders, customers).work(), Joins.indexNestedLoop(orders, customers).work(),
                Joins.hashJoin(orders, customers).work(), Joins.mergeJoin(sortedOrders, customers).work());
        assert work.equals(List.of(10_000_000, 99_780, 11_000, 10_999)) : work;
        var one = orders.stream().filter(o -> o.key() == 42).toList();
        assert Joins.indexNestedLoop(one, customers).work() == 100 && Joins.hashJoin(one, customers).work() == 1_010;

        assert Math.round(Joins.independentEstimate(30_000, 0.1, 0.3)) == 900 && Math.round(Joins.independentEstimate(30_000, 0.1)) == 3_000;
        assert Joins.rowsReadForPage(100_000, 20, false) == 100_020 && Joins.rowsReadForPage(100_000, 20, true) == 20;

        String url = "jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres";
        try (Connection db = DriverManager.getConnection(url); Statement s = db.createStatement()) {
            for (String statement : Files.readString(Path.of("../shared/shop.sql")).split(";\n")) {
                if (!statement.replaceAll("(?m)^--.*$", "").isBlank()) s.execute(statement);
            }
            String join = "SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id";
            assert hashBatches(s, join) == 1;
            s.execute("SET work_mem = '64kB'");
            assert hashBatches(s, join) == 16;
            s.execute("RESET work_mem");

            String query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
            var before = explain(s, query).getFirst();
            assert before.get("Plan Rows").asInt() == 900 && before.get("Actual Rows").asInt() == 3000;
            s.execute("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses");
            s.execute("ANALYZE addresses");
            assert explain(s, query).getFirst().get("Plan Rows").asInt() == 3000;

            assert explain(s, "SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20").get(1).get("Actual Rows").asInt() == 100_020;
            assert explain(s, "SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20").get(1).get("Actual Rows").asInt() == 20;
        }
        System.out.println("all join checks passed");
    }

    private static List<String> canonical(List<Joins.Pair> rows) {
        return rows.stream().map(p -> p.outer() + "|" + p.inner()).sorted().toList();
    }

    private static int hashBatches(Statement s, String sql) throws SQLException {
        return explain(s, sql).stream().filter(n -> n.get("Node Type").asString().equals("Hash")).findFirst().orElseThrow().get("Hash Batches").asInt();
    }

    private static List<JsonNode> explain(Statement s, String sql) throws SQLException {
        try (ResultSet r = s.executeQuery("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) " + sql)) {
            r.next();
            List<JsonNode> out = new ArrayList<>();
            collect(JsonMapper.shared().readTree(r.getString(1)).get(0).get("Plan"), out);
            return out;
        }
    }

    private static void collect(JsonNode node, List<JsonNode> out) {
        out.add(node);
        node.path("Plans").forEach(child -> collect(child, out));
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/java). `python3 labs/run.py join-algorithms-and-the-optimiser/java`.

## 7. Rust

Rows are `(u32, String)` tuples. The hash join's table borrows `&str` from the inner rows, and the merge join matches on `Ordering`. The PostgreSQL test reads `Actual Rows` with `as_f64()`, and sends `CREATE STATISTICS` and `ANALYZE` together in one `batch_execute`. That's fine here: neither refuses to run in a transaction.

```rust
//! The three join algorithms, each counting its work, and two classic estimation failures. Same model as the
//! Python lab. Rows are (key, value) pairs; joins return (outer value, inner value) pairs.
use std::collections::HashMap;

pub type Row = (u32, String);
pub type Joined = Vec<(String, String)>;

/// For every outer row, look at every inner row: N × M comparisons.
pub fn nested_loop(outer: &[Row], inner: &[Row]) -> (Joined, u64) {
    let (mut out, mut comparisons) = (Vec::new(), 0);
    for (ok, ov) in outer {
        for (ik, iv) in inner {
            comparisons += 1;
            if ok == ik {
                out.push((ov.clone(), iv.clone()));
            }
        }
    }
    (out, comparisons)
}

/// A sorted inner side searched by halving: about N × log₂ M steps.
pub fn index_nested_loop(outer: &[Row], inner_sorted: &[Row]) -> (Joined, u64) {
    let (mut out, mut steps) = (Vec::new(), 0);
    for (ok, ov) in outer {
        let (mut lo, mut hi) = (0, inner_sorted.len());
        while lo < hi {
            steps += 1;
            let mid = (lo + hi) / 2;
            if inner_sorted[mid].0 < *ok {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        out.extend(
            inner_sorted[lo..]
                .iter()
                .take_while(|(k, _)| k == ok)
                .map(|(_, iv)| (ov.clone(), iv.clone())),
        );
    }
    (out, steps)
}

/// Build a HashMap on the inner side, probe it once per outer row: N + M operations. Equality only.
pub fn hash_join(outer: &[Row], inner: &[Row]) -> (Joined, u64) {
    let mut table: HashMap<u32, Vec<&str>> = HashMap::new();
    for (ik, iv) in inner {
        table.entry(*ik).or_default().push(iv);
    }
    let out = outer
        .iter()
        .flat_map(|(ok, ov)| {
            table
                .get(ok)
                .into_iter()
                .flatten()
                .map(move |iv| (ov.clone(), iv.to_string()))
        })
        .collect();
    (out, (inner.len() + outer.len()) as u64)
}

/// Both sides sorted by key: walk them together, about N + M steps.
pub fn merge_join(outer_sorted: &[Row], inner_sorted: &[Row]) -> (Joined, u64) {
    let (mut out, mut steps, mut i, mut j) = (Vec::new(), 0, 0, 0);
    while i < outer_sorted.len() && j < inner_sorted.len() {
        steps += 1;
        let (ok, ik) = (outer_sorted[i].0, inner_sorted[j].0);
        match ok.cmp(&ik) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                let group = inner_sorted[j..].iter().take_while(|(k, _)| *k == ok);
                out.extend(group.map(|(_, iv)| (outer_sorted[i].1.clone(), iv.clone())));
                i += 1; // the next outer row may share the key, so j stays at the start of the group
            }
        }
    }
    (out, steps)
}

pub fn independent_estimate(rows: f64, selectivities: &[f64]) -> f64 {
    selectivities.iter().fold(rows, |estimate, s| estimate * s)
}

pub fn rows_read_for_page(offset: u64, limit: u64, keyset: bool) -> u64 {
    if keyset { limit } else { offset + limit }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn data() -> (Vec<Row>, Vec<Row>) {
        let orders = (0..10_000)
            .map(|i| (1 + i % 1_000, format!("order {i}")))
            .collect();
        let customers = (1..=1_000).map(|c| (c, format!("customer {c}"))).collect();
        (orders, customers)
    }

    fn canonical(mut rows: Joined) -> Joined {
        rows.sort();
        rows
    }

    fn by_key(rows: &[Row]) -> Vec<Row> {
        let mut sorted = rows.to_vec();
        sorted.sort_by_key(|r| r.0); // stable
        sorted
    }

    #[test]
    fn all_three_give_the_same_answer() {
        let (orders, customers) = data();
        let expected = canonical(nested_loop(&orders, &customers).0);
        assert_eq!(expected.len(), 10_000);
        assert_eq!(
            canonical(index_nested_loop(&orders, &customers).0),
            expected
        );
        assert_eq!(canonical(hash_join(&orders, &customers).0), expected);
        assert_eq!(
            canonical(merge_join(&by_key(&orders), &customers).0),
            expected
        );
    }

    #[test]
    fn they_differ_enormously_in_work() {
        let (orders, customers) = data();
        let work = [
            nested_loop(&orders, &customers).1,
            index_nested_loop(&orders, &customers).1,
            hash_join(&orders, &customers).1,
            merge_join(&by_key(&orders), &customers).1,
        ];
        assert_eq!(work, [10_000_000, 99_780, 11_000, 10_999]);
        let one: Vec<Row> = orders.iter().filter(|r| r.0 == 42).cloned().collect();
        assert_eq!(
            (
                index_nested_loop(&one, &customers).1,
                hash_join(&one, &customers).1
            ),
            (100, 1_010)
        );
    }

    #[test]
    fn correlated_columns_and_pagination() {
        assert_eq!(independent_estimate(30_000.0, &[0.1, 0.3]).round(), 900.0);
        assert_eq!(independent_estimate(30_000.0, &[0.1]).round(), 3_000.0);
        assert_eq!(
            (
                rows_read_for_page(100_000, 20, false),
                rows_read_for_page(100_000, 20, true)
            ),
            (100_020, 20)
        );
    }
}
```

```rust
//! The PostgreSQL checks through the `postgres` crate. Run through ../shared/with-postgres.sh; without PGHOST
//! set, it does nothing.
use postgres::{Client, Config, NoTls};
use serde_json::Value;

fn nodes(plan: &Value, out: &mut Vec<Value>) {
    out.push(plan.clone());
    for child in plan["Plans"].as_array().into_iter().flatten() {
        nodes(child, out);
    }
}

fn explain(db: &mut Client, sql: &str) -> Vec<Value> {
    let json: Value = db
        .query_one(
            &format!("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) {sql}"),
            &[],
        )
        .unwrap()
        .get(0);
    let mut out = Vec::new();
    nodes(&json[0]["Plan"], &mut out);
    out
}

fn hash_batches(db: &mut Client) -> u64 {
    let plan = explain(
        db,
        "SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id",
    );
    plan.iter().find(|n| n["Node Type"] == "Hash").unwrap()["Hash Batches"]
        .as_u64()
        .unwrap()
}

#[test]
fn postgres() {
    let Ok(host) = std::env::var("PGHOST") else {
        return;
    };
    let port: u16 = std::env::var("PGPORT").unwrap().parse().unwrap();
    let mut db = Config::new()
        .host(&host)
        .port(port)
        .user("postgres")
        .dbname("postgres")
        .connect(NoTls)
        .unwrap();
    for statement in std::fs::read_to_string("../shared/shop.sql")
        .unwrap()
        .split(";\n")
    {
        let code: String = statement
            .lines()
            .filter(|l| !l.trim_start().starts_with("--"))
            .collect();
        if !code.trim().is_empty() {
            db.batch_execute(statement).unwrap();
        }
    }

    assert_eq!(hash_batches(&mut db), 1);
    db.batch_execute("SET work_mem = '64kB'").unwrap();
    assert_eq!(hash_batches(&mut db), 16);
    db.batch_execute("RESET work_mem").unwrap();

    let query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
    let before = &explain(&mut db, query)[0];
    assert_eq!(
        (before["Plan Rows"].as_u64(), before["Actual Rows"].as_f64()),
        (Some(900), Some(3000.0))
    ); // actual rows: a decimal in PostgreSQL 18
    db.batch_execute("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses; ANALYZE addresses").unwrap();
    assert_eq!(explain(&mut db, query)[0]["Plan Rows"].as_u64(), Some(3000));

    let offset = explain(
        &mut db,
        "SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20",
    );
    let keyset = explain(
        &mut db,
        "SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20",
    );
    assert_eq!(
        (
            offset[1]["Actual Rows"].as_f64(),
            keyset[1]["Actual Rows"].as_f64()
        ),
        (Some(100_020.0), Some(20.0))
    );
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/rust). `python3 labs/run.py join-algorithms-and-the-optimiser/rust`.

## 8. C#

`Row` is a `readonly record struct`, so a list of them is one block of memory with no per-row objects. The hash join is `ToLookup` and `SelectMany`. The tests sort with `OrderBy`, which is stable, and compare with an ordinal string comparer, so the result doesn't depend on the machine's culture. It runs in the .NET SDK container on the host's network.

```csharp
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
```

```csharp
// The model checks, then the PostgreSQL checks through Npgsql.
using System.Text.Json.Nodes;
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var orders = Enumerable.Range(0, 10_000).Select(i => new Row(1 + i % 1_000, $"order {i}")).ToList();
var customers = Enumerable.Range(1, 1_000).Select(c => new Row(c, $"customer {c}")).ToList();
var sortedOrders = orders.OrderBy(o => o.Key).ToList(); // OrderBy is stable
static List<string> Canonical(List<(string, string)> rows) => rows.Select(r => $"{r.Item1}|{r.Item2}").Order(StringComparer.Ordinal).ToList();

var expected = Canonical(Joins.NestedLoop(orders, customers).Rows);
Check(expected.Count == 10_000, expected.Count);
Check(Canonical(Joins.IndexNestedLoop(orders, customers).Rows).SequenceEqual(expected), "index nested loop");
Check(Canonical(Joins.HashJoin(orders, customers).Rows).SequenceEqual(expected), "hash");
Check(Canonical(Joins.MergeJoin(sortedOrders, customers).Rows).SequenceEqual(expected), "merge");

long[] work = [Joins.NestedLoop(orders, customers).Work, Joins.IndexNestedLoop(orders, customers).Work, Joins.HashJoin(orders, customers).Work, Joins.MergeJoin(sortedOrders, customers).Work];
Check(work.SequenceEqual([10_000_000L, 99_780, 11_000, 10_999]), string.Join(", ", work));
var one = orders.Where(o => o.Key == 42).ToList();
Check(Joins.IndexNestedLoop(one, customers).Work == 100 && Joins.HashJoin(one, customers).Work == 1_010, "one customer");
Check(Math.Round(Joins.IndependentEstimate(30_000, 0.1, 0.3)) == 900 && Math.Round(Joins.IndependentEstimate(30_000, 0.1)) == 3_000, "estimates");
Check(Joins.RowsReadForPage(100_000, 20, false) == 100_020 && Joins.RowsReadForPage(100_000, 20, true) == 20, "pagination");

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
    var nodes = new List<JsonNode>();
    void Collect(JsonNode node)
    {
        nodes.Add(node);
        foreach (var child in node["Plans"]?.AsArray() ?? []) Collect(child!);
    }
    Collect(JsonNode.Parse((string)(await command.ExecuteScalarAsync())!)![0]!["Plan"]!);
    return nodes;
}
async Task<int> HashBatches() =>
    (int)(await Explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id")).First(n => (string?)n["Node Type"] == "Hash")["Hash Batches"]!;

foreach (var statement in File.ReadAllText("../shared/shop.sql").Split(";\n"))
    if (statement.Split('\n').Any(line => line.Trim() != "" && !line.TrimStart().StartsWith("--"))) await Run(statement);

Check(await HashBatches() == 1, "one batch");
await Run("SET work_mem = '64kB'");
Check(await HashBatches() == 16, "sixteen batches");
await Run("RESET work_mem");

var query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
var before = (await Explain(query))[0];
Check((int)before["Plan Rows"]! == 900 && (double)before["Actual Rows"]! == 3000, before["Plan Rows"]); // actual rows is a decimal in PostgreSQL 18
await Run("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses");
await Run("ANALYZE addresses");
Check((int)(await Explain(query))[0]["Plan Rows"]! == 3000, "with statistics");

Check((double)(await Explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20"))[1]["Actual Rows"]! == 100_020, "offset");
Check((double)(await Explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20"))[1]["Actual Rows"]! == 20, "keyset");
Console.WriteLine("all join checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/07-join-algorithms-and-the-optimiser/labs/csharp). `python3 labs/run.py join-algorithms-and-the-optimiser/csharp`.

## Common pitfalls

1. **An unstable sort where output order matters.** `slices.Sort`, `sort_unstable` and `List.Sort` can order equal keys differently each time. Use the stable form, or don't depend on the order.
2. **`SET` on a pooled connection.** It leaks to the next borrower. Use `SET LOCAL` inside a transaction.
3. **Integer `Actual Rows`.** It's a decimal in PostgreSQL 18.
4. **Comparing strings with the machine's culture in C#.** `Order()` with the default comparer can sort differently on another machine. Use `StringComparer.Ordinal` for anything compared byte for byte.
5. **`i * 7919` in SQL or in a 32-bit language.** It overflows at a million rows. Widen first.

## Check your understanding

1. Why does Rust's hash join table hold `&str` rather than `String`, and what guarantees it's safe?
2. The merge join gives the same 10,999 steps whatever the order of orders within one customer. Why use a stable sort at all?
3. A web handler runs `SET work_mem = '256MB'` before a report query, through a connection pool. What can go wrong, and what's the fix?
4. Why does the Go test compare `Hash Batches` with `16.0` rather than `16`?
5. What does C#'s `ToLookup` give for a key that isn't in it, and how does that simplify the probe?

<details>
<summary>Answers — after your attempt</summary>

1. Borrowing avoids copying every customer name into the table. The borrow checker guarantees the inner rows live at least as long as the table, so a borrowed `&str` can never point at freed memory.
2. To make the output's order deterministic: the same rows in the same order in every language and run. The step count doesn't depend on it, but anything that compares unsorted output, or shows it to a user, does.
3. The setting stays on that pooled connection after the handler returns it, so later, unrelated queries borrowing the connection run with 256 MB of `work_mem` per operation, which can exhaust memory under load. Use `SET LOCAL` inside a transaction, which ends with the transaction, or set it per role.
4. pgx decodes JSON numbers into `float64`, so the value is an `any` holding `float64(16)`. Comparing an `any` with the untyped constant `16` converts the constant to its default type, `int`, and an `any` holding `int(16)` isn't equal to one holding `float64(16)`: the check would fail with the right value. Writing `16.0` makes the constant a `float64`.
5. An empty sequence. The probe can always loop over `table[key]` without first checking whether the key exists.

</details>

## Practice — independent task

**Add the nested-loop plan check to your language's PostgreSQL test.**

1. Run the main lesson's "one customer's orders, with names" query through `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`.
2. Assert the top node is a `Nested Loop`, that it returns 20 rows, and that it reads fewer than 50 pages.
3. Then wrap the query in a function that takes the customer ID as a query parameter (`$1`, `?` or `@id`, depending on the driver), and check the plan is the same.

**Done when:** both checks pass, and you can name your driver's parameter placeholder and say why parameters beat building the SQL string yourself.

## Before moving on

You can write a hash join with your language's map and say what it costs in memory, explain why the labs sort stably, and run the planner experiments through your driver, reading each number as the type it arrives as.

**Recap.** The algorithms give the same rows and step counts in every language; what changes is the equipment. Each language's hash map is the build table: Rust borrows strings to avoid copying, and C#'s `ToLookup` needs no missing-key check. Use a stable sort so output is deterministic, and remember which sorts aren't: `slices.Sort`, `sort_unstable`, `List.Sort`. Read plan numbers as the types they arrive as, with `Actual Rows` a decimal in PostgreSQL 18, and keep session settings off pooled connections with `SET LOCAL`.

## Related

- [[databases/07-join-algorithms-and-the-optimiser/index|Join algorithms and the optimiser]]: the main lesson
- [[databases/04-b-trees-and-indexes/in-other-languages|B-trees and indexes in other languages]]: the same drivers, and the B+ tree in each language
- [[dsa/02-data-structures/03-hash-maps|Hash maps]]: the structure behind the hash join
