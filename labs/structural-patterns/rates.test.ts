import { test } from "node:test";
import assert from "node:assert/strict";
import { Caching, FlakyApi, Logging, Retrying, ThirdPartyFx, ThirdPartyFxAdapter } from "./rates.ts";

test("composed: log(cache(retry(api))) — two failures, then cached", async () => {
  const api = new FlakyApi(2);
  const log: string[] = [];
  const rates = new Logging(new Caching(new Retrying(api, 3)), log);

  assert.equal(await rates.rate("GBP", "NGN"), 2000); // fails twice, third attempt succeeds
  assert.equal(await rates.rate("GBP", "NGN"), 2000); // served from cache
  assert.equal(api.calls, 3);
  assert.deepEqual(log, ["GBP->NGN = 2000", "GBP->NGN = 2000"]);
});

test("order matters: retry(cache(api)) with too few attempts still fails", async () => {
  const rates = new Retrying(new Caching(new FlakyApi(5)), 3);
  await assert.rejects(rates.rate("GBP", "NGN"), /503/);
});

test("adapter: a client with the wrong shape plugs into the same stack", async () => {
  const rates = new Caching(new ThirdPartyFxAdapter(new ThirdPartyFx()));
  assert.equal(await rates.rate("USD", "NGN"), 1500);
});
