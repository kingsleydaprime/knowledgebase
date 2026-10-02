// Integration tests: a real server and a real database, talking over a real socket.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createApp, openDb } from "./app.mjs";

let server, base, db;

before(async () => {
  db = openDb();
  server = createApp(db).listen(0); // port 0: the OS picks a free port, so tests never collide
  await new Promise((resolve) => server.once("listening", resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(() => server.close());

const post = (body) =>
  fetch(`${base}/users`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });

test("POST /users stores the user — checked in the database, not just the response", async () => {
  const res = await post({ email: "ada@x.com", trialEndsOn: "2026-11-01" });
  assert.equal(res.status, 201);
  const { id } = await res.json();
  const row = db.prepare("SELECT email, trial_ends_on FROM users WHERE id = ?").get(id);
  assert.deepEqual({ ...row }, { email: "ada@x.com", trial_ends_on: "2026-11-01" });
});

test("a duplicate email is a 409 — even with different capitals", async () => {
  // Arrange its own data rather than relying on the test above having run first.
  assert.equal((await post({ email: "bayo@x.com", trialEndsOn: "2026-11-02" })).status, 201);
  const res = await post({ email: "BAYO@x.com", trialEndsOn: "2026-11-02" });
  assert.equal(res.status, 409);
});

test("an invalid email is a 400, and nothing is written", async () => {
  const before = db.prepare("SELECT COUNT(*) AS n FROM users").get().n;
  const res = await post({ email: "not-an-email", trialEndsOn: "2026-11-01" });
  assert.equal(res.status, 400);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM users").get().n, before);
});
