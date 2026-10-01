import { test } from "node:test";
import assert from "node:assert/strict";
import { findUserSafe, findUserUnsafe, listUsers, openDb } from "./injection.mjs";
import {
  greetingSafe, greetingUnsafe, inlineDataSafe, inlineDataUnsafe, profileLink, stripScriptTags,
} from "./encoding.mjs";

const attack = "' OR '1'='1";

test("SQL injection: concatenation turns input into syntax and returns every user", () => {
  const db = openDb();
  assert.deepEqual(findUserUnsafe(db, "ada").map((r) => ({ ...r })), [{ username: "ada", role: "member" }]);
  assert.equal(findUserUnsafe(db, attack).length, 3);    // WHERE username = '' OR '1'='1'
});

test("parameters keep input as data: the same attack matches nobody", () => {
  const db = openDb();
  assert.deepEqual(findUserSafe(db, attack).map((r) => ({ ...r })), []);
  assert.deepEqual(findUserSafe(db, "ada").map((r) => ({ ...r })), [{ username: "ada", role: "member" }]);
});

test("identifiers can't be parameters, so they come from an allowlist", () => {
  const db = openDb();
  assert.deepEqual(listUsers(db, "name"), ["ada", "admin", "bayo"]);
  assert.deepEqual(listUsers(db, "newest"), ["ada", "bayo", "admin"]);
  assert.throws(() => listUsers(db, "username; DROP TABLE users"), /cannot sort by/);
});

test("XSS: raw output runs the attacker's markup; escaped output shows it as text", () => {
  const name = `<img src=x onerror="steal(document.cookie)">`;
  assert.equal(greetingUnsafe(name), `<p>Welcome, <img src=x onerror="steal(document.cookie)"></p>`);
  assert.equal(greetingSafe(name), `<p>Welcome, &lt;img src=x onerror=&quot;steal(document.cookie)&quot;&gt;</p>`);
});

test("a denylist misses what it didn't predict", () => {
  assert.equal(stripScriptTags("<script>steal()</script>hi"), "hi");                  // the case it was written for
  assert.equal(stripScriptTags("<SCRIPT>steal()</SCRIPT>hi"), "<SCRIPT>steal()</SCRIPT>hi"); // capitals
  assert.equal(stripScriptTags(`<img src=x onerror=steal()>`), `<img src=x onerror=steal()>`); // no script tag at all
});

test("context: a javascript: URL survives HTML escaping, so the scheme is allowlisted", () => {
  assert.equal(profileLink("javascript:steal(document.cookie)"), `<a href="#">website</a>`);
  assert.equal(profileLink("https://ada.dev/?a=1&b=2"), `<a href="https://ada.dev/?a=1&amp;b=2">website</a>`);
});

test("context: </script> inside JSON ends the script block unless < is escaped", () => {
  const data = { bio: "</script><script>steal()</script>" };
  assert.match(inlineDataUnsafe(data), /<\/script><script>steal\(\)/);
  assert.equal(inlineDataSafe(data), `<script>window.DATA = {"bio":"\\u003c/script>\\u003cscript>steal()\\u003c/script>"}</script>`);
  assert.deepEqual(JSON.parse(inlineDataSafe(data).slice(22, -9)), data); // still the same data once parsed
});
