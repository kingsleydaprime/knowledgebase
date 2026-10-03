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
