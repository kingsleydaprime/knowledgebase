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
