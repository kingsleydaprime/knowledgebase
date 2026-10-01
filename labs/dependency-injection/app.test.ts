import { test } from "node:test";
import assert from "node:assert/strict";
import { compose, requestContext } from "./app.ts";

test("BUG: a per-request field on a shared instance records the wrong user", async () => {
  const { log, buggy } = compose();
  const handle = async (user: string) => {
    buggy.setUser(user);
    await buggy.record("viewed invoice");
  };
  await Promise.all([handle("ada"), handle("bayo")]); // two requests at once
  assert.deepEqual(log.entries, ["bayo: viewed invoice", "bayo: viewed invoice"]);
});

test("FIX 1: pass request data as an argument", async () => {
  const { log, audit } = compose();
  await Promise.all([audit.record("ada", "viewed invoice"), audit.record("bayo", "viewed invoice")]);
  assert.deepEqual(log.entries.sort(), ["ada: viewed invoice", "bayo: viewed invoice"]);
});

test("FIX 2: AsyncLocalStorage gives each request its own context", async () => {
  const { log, contextAudit } = compose();
  const handle = (user: string) => requestContext.run({ user }, () => contextAudit.record("viewed invoice"));
  await Promise.all([handle("ada"), handle("bayo")]);
  assert.deepEqual(log.entries.sort(), ["ada: viewed invoice", "bayo: viewed invoice"]);
});
