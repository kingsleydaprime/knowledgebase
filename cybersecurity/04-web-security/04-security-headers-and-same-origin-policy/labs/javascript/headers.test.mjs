import { test } from "node:test";
import assert from "node:assert/strict";
import { createApp } from "./app.mjs";
import { corsReflectAnything } from "./headers.mjs";

async function start(options) {
  const server = createApp(options).listen(0);
  await new Promise((r) => server.once("listening", r));
  return { base: `http://127.0.0.1:${server.address().port}`, close: () => server.close() };
}

test("every response carries the security headers", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/me`);
  assert.equal(res.headers.get("x-content-type-options"), "nosniff");
  assert.match(res.headers.get("content-security-policy"), /frame-ancestors 'none'/);
  assert.match(res.headers.get("strict-transport-security"), /max-age=31536000/);
});

test("CORS allowlist: our app's origin is allowed, anyone else's isn't", async (t) => {
  const app = await start(); t.after(app.close);
  const ours = await fetch(`${app.base}/me`, { headers: { origin: "https://app.example.com" } });
  assert.equal(ours.headers.get("access-control-allow-origin"), "https://app.example.com");
  const evil = await fetch(`${app.base}/me`, { headers: { origin: "https://evil.example" } });
  assert.equal(evil.headers.get("access-control-allow-origin"), null); // a browser would hide the response
  assert.equal(evil.headers.get("vary"), "Origin");
});

test("the common misconfiguration: reflecting any origin, with credentials", async (t) => {
  const app = await start({ cors: corsReflectAnything }); t.after(app.close);
  const evil = await fetch(`${app.base}/me`, { headers: { origin: "https://evil.example" } });
  assert.equal(evil.headers.get("access-control-allow-origin"), "https://evil.example");
  assert.equal(evil.headers.get("access-control-allow-credentials"), "true"); // evil.example can read /me as the user
});

test("CORS is not access control: a non-browser client gets the data regardless", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/me`, { headers: { origin: "https://evil.example" } });
  assert.deepEqual(await res.json(), { email: "ada@x.com" }); // Node, curl and scripts ignore CORS entirely
});

test("preflight for an allowed origin lists what's permitted", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/me`, { method: "OPTIONS", headers: { origin: "https://app.example.com" } });
  assert.equal(res.status, 204);
  assert.equal(res.headers.get("access-control-allow-methods"), "GET, POST");
});

test("the session cookie: HttpOnly, Secure, SameSite", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/login`, { method: "POST" });
  const cookie = res.headers.get("set-cookie");
  for (const flag of ["HttpOnly", "Secure", "SameSite=Lax", "Path=/"]) assert.ok(cookie.includes(flag), flag);
});
