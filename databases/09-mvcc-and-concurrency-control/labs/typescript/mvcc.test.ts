// MVCC through node-postgres: snapshots, blocked vacuum and a deadlock. Run through ../shared/with-postgres.sh.
import { afterEach, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import pg from "pg";

const DEADLOCK_DETECTED = "40P01";
const LOCK_NOT_AVAILABLE = "55P03";

let a: pg.Client;
let b: pg.Client;
let watcher: pg.Client;

async function value(client: pg.Client, sql: string, params: unknown[] = []): Promise<any> {
  const { rows } = await client.query(sql, params);
  return Object.values(rows[0])[0];
}

/** Waits until the session with this backend pid is waiting for a lock. */
async function waitUntilBlocked(pid: number): Promise<void> {
  for (let i = 0; i < 500; i++) {
    if ((await value(watcher, "SELECT wait_event_type FROM pg_stat_activity WHERE pid = $1", [pid])) === "Lock") return;
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error(`session ${pid} never waited for a lock`);
}

beforeEach(async () => {
  [a, b, watcher] = [new pg.Client(), new pg.Client(), new pg.Client()];
  await Promise.all([a.connect(), b.connect(), watcher.connect()]);
  await a.query(`
    CREATE EXTENSION IF NOT EXISTS pgstattuple;
    DROP TABLE IF EXISTS accounts;
    CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
    INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i;
  `);
  await a.query("VACUUM accounts"); // alone: VACUUM can't run inside a multi-statement call's transaction
});

afterEach(() => Promise.all([a.end(), b.end(), watcher.end()]));

test("readers don't block writers, and keep reading their snapshot", async () => {
  await a.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  assert.equal(await value(a, "SELECT balance FROM accounts WHERE id = 1"), 100);
  await b.query("SET lock_timeout = '100ms'");
  await b.query("UPDATE accounts SET balance = 50 WHERE id = 1"); // finishes at once
  assert.equal(await value(a, "SELECT balance FROM accounts WHERE id = 1"), 100);
  await a.query("COMMIT");
  assert.equal(await value(a, "SELECT balance FROM accounts WHERE id = 1"), 50);
});

test("writers block writers on the same row", async () => {
  await a.query("BEGIN");
  await a.query("UPDATE accounts SET balance = 90 WHERE id = 1");
  await b.query("SET lock_timeout = '100ms'");
  await assert.rejects(b.query("UPDATE accounts SET balance = 80 WHERE id = 1"), (err: any) => err.code === LOCK_NOT_AVAILABLE);
  await a.query("COMMIT");
});

test("an open snapshot stops vacuum removing anything", async () => {
  await a.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  await a.query("SELECT 1");
  await b.query("UPDATE accounts SET balance = balance + 1");
  await b.query("VACUUM accounts");
  assert.equal(await value(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')"), "1000"); // a bigint: a string
  await a.query("COMMIT");
  await b.query("VACUUM accounts");
  assert.equal(await value(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')"), "0");
});

test("a deadlock: exactly one victim", async () => {
  for (const client of [a, b]) await client.query("SET deadlock_timeout = '100ms'");
  await a.query("BEGIN");
  await b.query("BEGIN");
  await a.query("UPDATE accounts SET balance = 1 WHERE id = 1");
  await b.query("UPDATE accounts SET balance = 2 WHERE id = 2");
  // No threads needed: a query that's waiting for a lock is just a promise that hasn't settled yet.
  const aWantsRow2 = a.query("UPDATE accounts SET balance = 1 WHERE id = 2");
  await waitUntilBlocked((a as any).processID);
  const bWantsRow1 = b.query("UPDATE accounts SET balance = 2 WHERE id = 1");
  const results = await Promise.allSettled([aWantsRow2, bWantsRow1]);
  const victims = results.filter((r) => r.status === "rejected" && (r.reason as any).code === DEADLOCK_DETECTED);
  assert.equal(victims.length, 1);
  await Promise.all([a.query("ROLLBACK"), b.query("ROLLBACK")]);
});
