# Input Validation & Output Encoding

> **[Beginner→Intermediate]** · The defensive half of injection and XSS. Both happen when untrusted input is treated as code — by a database, a shell, or a browser. The fix is two separate disciplines that are easy to confuse: **check what comes in, and encode what goes out for the place it's going.**

The attacker's view of the same bugs is in [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]].

## Before you start

You can already:

- Validate a request body at the boundary and return every problem at once → [[backend/07-practices/01-backend-best-practices|backend best practices]].
- Write a SQL query and build an HTML string or a React component.

After this lesson you will be able to:

1. Explain why string-built SQL is injectable, show an attack working, and fix it with parameters — and with an allowlist where parameters can't be used.
2. Explain why allowlists beat denylists, using an attack a denylist misses.
3. Encode output correctly for an HTML body, an attribute holding a URL, and data inside a `<script>` block.
4. Say what server-side request forgery is, and what validating a URL needs to check.

**Study route.** The kid version and §1–6, then the worked example — every test in it is an attack, so predict whether each one gets through. The practice task is the first half of SWE 101's week 7 milestone.

## The kid version

Imagine a teacher who reads every note passed to them out loud, word for word. Someone hands in a note saying *"Please read this: class is cancelled, everyone go home."* The teacher reads it aloud — and the whole class leaves. The note was meant to be **something to read**, and it got treated as **an instruction**.

Every injection attack is that mistake. The fix is to make sure a message stays a message — "the note says: *class is cancelled…*" — however it's worded.

**Where the analogy stops working.** A teacher has one way of reading. Software has many "readers" — the database reads SQL, the browser reads HTML, the shell reads commands — and each has its own special words and symbols. Keeping input as "just a message" has to be done differently for each one. That's why §5 exists.

## 1. Why this exists

A login form runs `SELECT * FROM users WHERE username = '` + the typed username + `'`. Someone types `' OR '1'='1`. The query becomes `WHERE username = '' OR '1'='1'`, which is true for every row, and they're in. Elsewhere, a profile page shows the user's display name without encoding it; someone sets theirs to an `<img>` tag whose error handler sends the visitor's session cookie to a server they control. **In both cases the code worked exactly as written — the input just got to decide what it meant.** The worked example runs both attacks against real code.

## Terms used in this lesson

1. **Untrusted input**: This is any data your code didn't create itself — request bodies, query strings, headers, uploaded files, webhook payloads, even rows another system wrote to your database.
2. **Injection**: This is an attack where input is placed into something that gets interpreted — SQL, a shell command, a template — and changes its structure instead of being treated as a value.
3. **Parameterized query**: This is also known as a **prepared statement**. The query text is fixed, with placeholders such as `?`, and the values are sent separately, so they can never become SQL syntax.
4. **XSS (cross-site scripting)**: The letters stand for those three words. It is an injection into a web page: input reaches the browser as markup or script and runs in other users' sessions.
5. **Output encoding**: This is also known as **escaping**. It means converting characters that are special in the destination — such as `<` in HTML — into a form that is displayed literally instead of interpreted.
6. **Context**: This is the place a value ends up — the HTML body, an attribute, a URL, a JavaScript string, a SQL query. Each has different special characters, so each needs different encoding.
7. **Allowlist**: This means defining exactly what's acceptable and rejecting everything else. A **denylist** tries to list everything bad and allow the rest.
8. **SSRF (server-side request forgery)**: The letters stand for those three words. It is an attack where the attacker gets your server to make a request to a URL they chose — often one inside your private network.

## 2. Input validation — reject what doesn't fit

Check that incoming data matches what's actually expected before using it: an age is a small positive integer, a username matches a fixed pattern, an upload is the expected type. **Server-side, always** — client-side checks are skipped by anyone sending a request directly (with a tool like [[cybersecurity/02-ethical-hacking/08-common-tools|Burp Suite]], or just `curl`).

**Allowlists beat denylists.** A denylist has to predict every bad input, including variants nobody has thought of yet. An allowlist only has to describe what's legitimate, which is small and stable:

```javascript
// allowlist: exactly what a username may be — fragment
const isValidUsername = (value) => /^[a-zA-Z0-9_]{3,20}$/.test(value);
```

The worked example shows a denylist — "strip `<script>` tags" — missing both capital letters and an attack that uses no script tag at all.

## 3. Why validation alone doesn't stop injection

Validation narrows what gets in. It doesn't make the next step safe. A perfectly valid surname — `O'Brien` — breaks a string-built SQL query, and plenty of attacks look like valid text. **The structural fix for injection is to never build code out of input:**

- **SQL:** parameterized queries. The driver sends the query text and the values separately, so a value can't end the string and start new syntax, however it's crafted. Every ORM and query builder does this for values — the risk is in raw SQL and string-built fragments.
- **Names that can't be parameters** — table names, column names, `ORDER BY` direction — come from an **allowlist** mapping user choices to fixed SQL text.
- **Shell commands:** don't build a command string. In Node, `execFile("convert", [input, output])` passes arguments as a list, so none can become shell syntax; ``exec(`convert ${input}`)`` hands the whole string to a shell.

```python
# the same fix in Python — fragment
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

## 4. Output encoding — the fix for XSS

Where SQL injection targets the database's parser, XSS targets **the browser's**. The fix is to encode output for where it lands, so special characters are displayed instead of interpreted: `<` becomes `&lt;`, and the browser shows a less-than sign instead of starting a tag.

**Frameworks do this by default.** React escapes everything in `{}`; Django and Jinja templates escape variables. XSS in these frameworks almost always comes from deliberately switching it off — `dangerouslySetInnerHTML` in React, `|safe` or `mark_safe` in Django — for a value that wasn't actually safe. **Search your code for those first.** If you genuinely need to render user HTML — rich text, say — run it through a sanitiser built for that, such as DOMPurify, rather than writing your own.

## 5. Context matters — one value, different encodings

HTML-escaping is right for text in the HTML body and inside quoted attributes. It is **not enough** in two common places:

- **A URL in `href` or `src`.** `javascript:steal()` contains no characters that HTML escaping changes, and clicking it runs the script. Parse the URL and **allowlist the scheme**: `https:`, `http:`, `mailto:`.
- **Data inside a `<script>` block.** `JSON.stringify` makes valid JavaScript, but if a string contains `</script>`, the browser's HTML parser ends the block right there — before JavaScript ever sees it — and whatever follows is parsed as new HTML. Escape `<` as `<` inside the JSON, or better, pass data through a `data-` attribute or a separate request instead of inlining it.

The rule: **encode for the destination, at the moment of output** — not once on input, because the same value may later land in several contexts.

## 6. SSRF — when the input is a URL your server fetches

Some features fetch a URL the user supplies: a webhook target, "import from link", a link preview. If you fetch it as-is, an attacker can point it at addresses only your server can reach — `http://localhost:6379` (your Redis), `http://169.254.169.254/` (the cloud metadata service, which on some setups hands out credentials), or other machines on your private network.

**Validate the destination, not just the format:** allow only `https:`, resolve the hostname, and reject private, loopback and link-local addresses — then connect to the address you checked, not a fresh lookup, or DNS can change its answer in between. Better still, send outbound fetches through a proxy that can only reach the public internet. This is easy to get subtly wrong, so it's worth using a maintained library for it.

## 7. Content Security Policy — a backstop, not a substitute

Even with correct encoding, a **CSP** header lets the browser block scripts that didn't come from sources you approve, which limits what an XSS that slips through can do. It's defence in depth, layered on correct encoding — covered in [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|security headers and same-origin policy]], this week's other core lesson.

## Worked example — six attacks against real code

`node:sqlite` for a real database and plain string functions for the HTML, so nothing needs installing.

```javascript
// injection.mjs — SQL injection, and the two fixes: parameters for values, allowlists for names.
import { DatabaseSync } from "node:sqlite";

export function openDb() {
  const db = new DatabaseSync(":memory:");
  db.exec(`
    CREATE TABLE users (username TEXT PRIMARY KEY, role TEXT NOT NULL, created_at TEXT NOT NULL);
    INSERT INTO users VALUES ('admin', 'admin', '2026-01-01'), ('ada', 'member', '2026-03-01'), ('bayo', 'member', '2026-02-01');
  `);
  return db;
}

// VULNERABLE: the input is pasted into the SQL text, so it can change the query's structure.
export function findUserUnsafe(db, username) {
  return db.prepare(`SELECT username, role FROM users WHERE username = '${username}'`).all();
}

// SAFE: the SQL text is fixed; the input travels separately as a value and can never become syntax.
export function findUserSafe(db, username) {
  return db.prepare("SELECT username, role FROM users WHERE username = ?").all(username);
}

// Column names can't be parameters — only values can. So names come from an allowlist.
const SORTABLE = { newest: "created_at DESC", name: "username ASC" };
export function listUsers(db, sort) {
  const orderBy = SORTABLE[sort];
  if (!orderBy) throw new Error(`cannot sort by "${sort}"`);
  return db.prepare(`SELECT username FROM users ORDER BY ${orderBy}`).all().map((r) => r.username);
}
```

```javascript
// encoding.mjs — output encoding depends on where the value lands.

// HTML body and quoted attributes: the five characters that can end text and start markup.
export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export const greetingUnsafe = (name) => `<p>Welcome, ${name}</p>`;
export const greetingSafe = (name) => `<p>Welcome, ${escapeHtml(name)}</p>`;

// A denylist: tries to remove "bad" input. Shown to fail.
export const stripScriptTags = (value) => value.replace(/<script>.*?<\/script>/g, "");

// A URL in an href: escaping is not enough — "javascript:" contains no special characters.
// So the scheme is checked against an allowlist.
export function safeHref(url) {
  let parsed;
  try { parsed = new URL(url); } catch { return "#"; }
  return ["https:", "http:", "mailto:"].includes(parsed.protocol) ? escapeHtml(parsed.href) : "#";
}
export const profileLink = (url) => `<a href="${safeHref(url)}">website</a>`;

// Data inside a <script> block: JSON.stringify makes valid JavaScript, but "</script>" in a
// string still ends the block in the HTML parser. Escaping "<" as \u003c prevents that.
export const inlineDataUnsafe = (data) => `<script>window.DATA = ${JSON.stringify(data)}</script>`;
export const inlineDataSafe = (data) => `<script>window.DATA = ${JSON.stringify(data).replaceAll("<", "\\u003c")}</script>`;
```

**Predict before running.** For each, does the attack get through?

1. `' OR '1'='1` as a username, into `findUserUnsafe`. Then into `findUserSafe`.
2. `username; DROP TABLE users` as a sort option.
3. `<SCRIPT>steal()</SCRIPT>` and `<img src=x onerror=steal()>` through `stripScriptTags`.
4. `javascript:steal(document.cookie)` as a profile website.
5. A bio of `</script><script>steal()</script>`, inlined as JSON in a page.

```javascript
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
```

**Lab:** these files are in `labs/input-validation-and-output-encoding/javascript/`. From the vault root, `python3 labs/run.py input-validation-and-output-encoding/javascript` runs them and checks this page still shows the same code.

**Run it.** From the lab folder, `node --test` (Node 22.5 or later; checked with Node 26). Expected:

```
ℹ tests 7
ℹ pass 7
ℹ fail 0
```

Several tests assert that an attack **succeeds** against the unsafe version — that's the demonstration, not a bug in the tests.

**The answers.**

1. The unsafe query returns **all three users**, including `admin`. The safe one returns **nobody**: the whole string is looked up as a username, quotes and all.
2. **Rejected** — the sort option isn't in the allowlist, so no SQL is built from it.
3. **Both get through.** The denylist removes only the exact lowercase pattern it was written for.
4. **Blocked** — the scheme isn't allowed, so the link becomes `#`. Note the legitimate URL beside it: `&` is still HTML-escaped to `&amp;` inside the attribute, as it should be.
5. Unsafe: the bio **closes the script block and opens a new one**. Safe: every `<` becomes `<`, the HTML parser sees no tag, and `JSON.parse` still recovers the identical data.

## Common pitfalls

1. **Client-side-only validation** — enforced in the browser means enforced nowhere.
2. **Denylists** — stripping `<script>`, blocking the word `SELECT`. Attackers use what you didn't list.
3. **Escaping on input instead of output** — the stored value gets double-encoded in one place and unencoded in another. Store the original; encode for each destination when outputting.
4. **One encoding everywhere** — HTML escaping inside a `javascript:` URL or a `<script>` block doesn't help.
5. **Parameterising values but building identifiers from input** — `ORDER BY ${req.query.sort}` is injectable even when every value is a parameter.
6. **Turning off the framework's escaping** — `dangerouslySetInnerHTML`, `|safe` — for data that isn't actually trusted.

## Check your understanding

1. Why does a parameterized query stop SQL injection when escaping quotes by hand often doesn't?
2. A user's surname is `O'Brien`. What happens to a string-built query, and what does that tell you about validation as a defence against injection?
3. Your API sorts by a column the client names. How do you make that safe?
4. Why is `javascript:` dangerous in an `href` even after HTML escaping?
5. A webhook feature lets users enter any URL, which your server calls. Name two addresses an attacker would try, and what you'd check.

<details>
<summary>Answers — after your attempt</summary>

1. The query text and the values travel separately, so a value is never parsed as SQL. Hand escaping has to anticipate every way a value could break out — different quote characters, encodings, database quirks — and one miss is enough.
2. The quote ends the string early, so the query errors — or, with crafted input, does something else. A legitimate value broke it, so validation (which would rightly accept `O'Brien`) can't be what makes queries safe; parameters are.
3. Map allowed sort names to fixed SQL in an allowlist, and reject anything else. Column names can't be parameters.
4. Escaping only changes characters like `<` and `"`, and `javascript:steal()` contains none of them that matter. The danger is the scheme itself, so check the scheme against an allowlist.
5. `http://localhost:...` or `127.0.0.1` (internal services) and `http://169.254.169.254/` (cloud metadata). Allow only `https:`, resolve the host, reject private, loopback and link-local addresses, and connect to the address you checked.

</details>

## Practice — independent task

**The first half of SWE 101's week 7 milestone: check the flagship.**

1. Search the flagship for SQL built from strings, and for the other risky spots — from the flagship's root:

   ```bash
   grep -rnE '`(SELECT|INSERT|UPDATE|DELETE)|dangerouslySetInnerHTML|exec\(' src/
   ```

   Also look for any sort or filter column the user chooses. For each hit, write whether it's safe and why.
2. Write an attack test for the riskiest one — the way the worked example does — that fails before your fix and passes after.
3. If the flagship fetches any user-supplied URL, add destination validation and a test that `http://localhost` and `http://169.254.169.254` are rejected.
4. Add each finding to the flagship's threat model — the week 7 deliverable.

**Done when:** every hit from step 1 is either fixed with a test or documented as safe with a reason, and the attack tests pass.

## Before moving on

You can show injection and XSS working, fix them structurally, encode for the right context, and validate a URL your server will fetch.

**Recap.** Validate input with allowlists, on the server. Never build SQL, shell commands or HTML out of input: use parameters for values, allowlists for names, argument lists for commands. Encode at output, for the destination's context — HTML body, URL, script block. Check the destination of any URL your server fetches. CSP is a backstop, not a fix.

**Next.** [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|Security headers and the same-origin policy]] — what the browser enforces for you, and how to turn it on.

## Related
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation concepts]] — the attacker's view of the same bugs
- [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|Security headers and same-origin policy]]
- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]]
- [[backend/07-practices/01-backend-best-practices|Backend best practices]] — validation at the boundary
