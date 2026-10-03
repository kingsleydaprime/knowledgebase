// The anomalies and their fixes, through node-postgres. Two clients are stepped one statement at a time.
// Run through ../shared/with-postgres.sh.
import { afterEach, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import pg from "pg";

// PostgreSQL's error codes (SQLSTATE) for the outcomes concurrency makes normal. node-postgres puts it on err.code.
const SERIALIZATION_FAILURE = "40001";
const DEADLOCK_DETECTED = "40P01";
const LOCK_NOT_AVAILABLE = "55P03";

let a: pg.Client;
let b: pg.Client;

async function value(client: pg.Client, sql: string, params: unknown[] = []): Promise<any> {
  const { rows } = await client.query(sql, params);
  return Object.values(rows[0])[0];
}

/** Runs `work` again while PostgreSQL says the transaction should be retried, backing off a little more each time. */
export async function withRetry<T>(work: () => Promise<T>, attempts = 5): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try {
      return await work();
    } catch (err: any) {
      if (attempt === attempts || ![SERIALIZATION_FAILURE, DEADLOCK_DETECTED].includes(err.code)) throw err;
      await new Promise((resolve) => setTimeout(resolve, 10 * 2 ** attempt));
    }
  }
}

beforeEach(async () => {
  [a, b] = [new pg.Client(), new pg.Client()];
  await Promise.all([a.connect(), b.connect()]);
  await a.query(`
    DROP TABLE IF EXISTS accounts, doctors;
    CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0), version int NOT NULL DEFAULT 1);
    INSERT INTO accounts (id, balance) VALUES (1, 100), (2, 50);
    CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
    INSERT INTO doctors VALUES ('alice', true), ('bob', true);
  `); // no VACUUM here, so one multi-statement call is fine
});

afterEach(() => Promise.all([a.end(), b.end()]));

const balance = () => value(a, "SELECT balance FROM accounts WHERE id = 1");

test("a lost update at Read Committed", async () => {
  await a.query("BEGIN");
  await b.query("BEGIN");
  const [seenA, seenB] = [await balance(), await value(b, "SELECT balance FROM accounts WHERE id = 1")];
  await a.query("UPDATE accounts SET balance = $1 WHERE id = 1", [seenA - 10]);
  await a.query("COMMIT");
  await b.query("UPDATE accounts SET balance = $1 WHERE id = 1", [seenB - 20]);
  await b.query("COMMIT");
  assert.equal(await balance(), 80);
});

test("Repeatable Read refuses the second write with SQLSTATE 40001", async () => {
  await a.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  await b.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  const seenB = await value(b, "SELECT balance FROM accounts WHERE id = 1");
  await a.query("UPDATE accounts SET balance = balance - 10 WHERE id = 1");
  await a.query("COMMIT");
  await assert.rejects(b.query("UPDATE accounts SET balance = $1 WHERE id = 1", [seenB - 20]), (err: any) => err.code === SERIALIZATION_FAILURE);
  await b.query("ROLLBACK");
  assert.equal(await balance(), 90);
});

test("FOR UPDATE makes the second reader wait: 55P03 under a short lock_timeout", async () => {
  await a.query("BEGIN");
  await a.query("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
  await b.query("BEGIN");
  await b.query("SET LOCAL lock_timeout = '100ms'");
  await assert.rejects(b.query("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE"), (err: any) => err.code === LOCK_NOT_AVAILABLE);
  await b.query("ROLLBACK");
  await a.query("COMMIT");
});

test("write skew: Serializable aborts one, and the retried transaction keeps the rule", async () => {
  const goOffCall = async (client: pg.Client, name: string) => {
    await client.query("BEGIN ISOLATION LEVEL SERIALIZABLE");
    if ((await value(client, "SELECT count(*)::int FROM doctors WHERE on_call")) >= 2) {
      await client.query("UPDATE doctors SET on_call = false WHERE name = $1", [name]);
    }
  };
  await goOffCall(a, "alice");
  await goOffCall(b, "bob");
  await a.query("COMMIT");
  await assert.rejects(b.query("COMMIT"), (err: any) => err.code === SERIALIZATION_FAILURE);
  await b.query("ROLLBACK").catch(() => {}); // after a failed COMMIT the transaction is already over
  await withRetry(async () => {
    try {
      await goOffCall(b, "bob");
      await b.query("COMMIT");
    } catch (err) {
      await b.query("ROLLBACK");
      throw err;
    }
  });
  assert.equal(await value(a, "SELECT string_agg(name, ',') FROM doctors WHERE on_call"), "bob");
});
