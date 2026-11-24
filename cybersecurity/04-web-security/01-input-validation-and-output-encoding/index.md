---
id: ba7b49d5-fb8e-4cef-953e-f2466e9dd1b5
---

# Input Validation & Output Encoding

**Input validation is checking that data coming in is what you expect; output encoding is making sure data going out is shown as text, never run as code.**

## Before you start
<!-- bite: 640bc4b0-94eb-4e5f-8429-990f38fe2154 -->

You can already:

- Validate a request body at the boundary and return every problem at once → [[backend/07-practices/01-backend-best-practices/index|backend best practices]].
- Write a SQL query and build an HTML string or a React component.

After this lesson you will be able to:

1. Explain why string-built SQL is injectable, show an attack working, and fix it with parameters — and with an allowlist where parameters can't be used.
2. Explain why allowlists beat denylists, using an attack a denylist misses.
3. Encode output correctly for an HTML body, an attribute holding a URL, and data inside a `<script>` block.
4. Say what server-side request forgery is, and what validating a URL needs to check.

**Study route.** The kid version and §1–6, then the worked example — every test in it is an attack, so predict whether each one gets through. The practice task is the first half of SWE 101's week 7 milestone.

## What input validation and output encoding are
<!-- bite: adb9b3f3-13a1-4665-ba7e-b84820ab8915 -->

Remember the login on Juice Shop? In the ethical-hacking section you typed `' OR 1=1--` and got in as the admin. The firewall from the network-security section couldn't stop it, because it arrived on the web port you opened on purpose. Only the code can.

Injection and XSS both happen when untrusted input gets treated as code, by a database, a shell or a browser. The fix is two separate habits that are easy to confuse: **check what comes in, and encode what goes out for the place it's going.** The attacker's view of the same bugs is in [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]].

## The kid version
<!-- bite: b64d51eb-4b7e-4a1e-b410-759f016ee0fa -->

Imagine a teacher who reads every note passed to them out loud, word for word. Someone hands in a note saying *"Please read this: class is cancelled, everyone go home."* The teacher reads it aloud — and the whole class leaves. The note was meant to be **something to read**, and it got treated as **an instruction**.

Every injection attack is that mistake. The fix is to make sure a message stays a message — "the note says: *class is cancelled…*" — however it's worded.

**Where the analogy stops working.** A teacher has one way of reading. Software has many "readers" — the database reads SQL, the browser reads HTML, the shell reads commands — and each has its own special words and symbols. Keeping input as "just a message" has to be done differently for each one. That's why §5 exists.

## 1. Why this exists
<!-- bite: 03b42b35-ce1b-42ee-9dcb-705f5c212e7b -->

A login form runs `SELECT * FROM users WHERE username = '` + the typed username + `'`. Someone types `' OR '1'='1`. The query becomes `WHERE username = '' OR '1'='1'`, which is true for every row, and they're in. Elsewhere, a profile page shows the user's display name without encoding it; someone sets theirs to an `<img>` tag whose error handler sends the visitor's session cookie to a server they control. **In both cases the code worked exactly as written — the input just got to decide what it meant.** The worked example runs both attacks against real code.

## Terms used in this lesson
<!-- bite: 84cf8887-945b-4e87-8630-c50c3a67e97a -->

1. **Untrusted input**: This is any data your code didn't create itself — request bodies, query strings, headers, uploaded files, webhook payloads, even rows another system wrote to your database.
2. **Injection**: This is an attack where input is placed into something that gets interpreted — SQL, a shell command, a template — and changes its structure instead of being treated as a value.
3. **Parameterized query**: This is also known as a **prepared statement**. The query text is fixed, with placeholders such as `?`, and the values are sent separately, so they can never become SQL syntax.
4. **XSS (cross-site scripting)**: The letters stand for those three words. It is an injection into a web page: input reaches the browser as markup or script and runs in other users' sessions.
## Terms used in this lesson: encoding, context and lists
<!-- bite: 7a08a142-4b1a-44a2-826b-67d7254dba92 -->

The last four terms are about what goes out, where it lands, and what you let in.

5. **Output encoding**: This is also known as **escaping**. It means converting characters that are special in the destination — such as `<` in HTML — into a form that is displayed literally instead of interpreted.
6. **Context**: This is the place a value ends up — the HTML body, an attribute, a URL, a JavaScript string, a SQL query. Each has different special characters, so each needs different encoding.
7. **Allowlist**: This means defining exactly what's acceptable and rejecting everything else. A **denylist** tries to list everything bad and allow the rest.
8. **SSRF (server-side request forgery)**: The letters stand for those three words. It is an attack where the attacker gets your server to make a request to a URL they chose — often one inside your private network.

## 2. Input validation — reject what doesn't fit
<!-- bite: c8a3599a-d434-4370-864a-a39d70ec7e49 -->

Check that incoming data matches what's actually expected before using it: an age is a small positive integer, a username matches a fixed pattern, an upload is the expected type. **Server-side, always** — client-side checks are skipped by anyone sending a request directly (with a tool like [[cybersecurity/02-ethical-hacking/08-common-tools|Burp Suite]], or just `curl`).

**Allowlists beat denylists.** A denylist has to predict every bad input, including variants nobody has thought of yet. An allowlist only has to describe what's legitimate, which is small and stable:

```javascript
// allowlist: exactly what a username may be — fragment
const isValidUsername = (value) => /^[a-zA-Z0-9_]{3,20}$/.test(value);
```

The worked example shows a denylist — "strip `<script>` tags" — missing both capital letters and an attack that uses no script tag at all.

## 3. Why validation alone doesn't stop injection
<!-- bite: 7d8263bc-9a69-465c-b121-6eef6e6e79eb -->

Validation narrows what gets in. It doesn't make the next step safe. A perfectly valid surname — `O'Brien` — breaks a string-built SQL query, and plenty of attacks look like valid text. **The structural fix for injection is to never build code out of input:**

- **SQL:** parameterized queries. The driver sends the query text and the values separately, so a value can't end the string and start new syntax, however it's crafted. Every ORM and query builder does this for values — the risk is in raw SQL and string-built fragments.
- **Names that can't be parameters** — table names, column names, `ORDER BY` direction — come from an **allowlist** mapping user choices to fixed SQL text.
- **Shell commands:** don't build a command string. In Node, `execFile("convert", [input, output])` passes arguments as a list, so none can become shell syntax; ``exec(`convert ${input}`)`` hands the whole string to a shell.

```python
# the same fix in Python — fragment
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

## 4. Output encoding — the fix for XSS
<!-- bite: 17f4de7f-4661-4821-a925-7e987877d285 -->

Where SQL injection targets the database's parser, XSS targets **the browser's**. The fix is to encode output for where it lands, so special characters are displayed instead of interpreted: `<` becomes `&lt;`, and the browser shows a less-than sign instead of starting a tag.

**Frameworks do this by default.** React escapes everything in `{}`; Django and Jinja templates escape variables. XSS in these frameworks almost always comes from deliberately switching it off — `dangerouslySetInnerHTML` in React, `|safe` or `mark_safe` in Django — for a value that wasn't actually safe. **Search your code for those first.** If you genuinely need to render user HTML — rich text, say — run it through a sanitiser built for that, such as DOMPurify, rather than writing your own.

## 5. Context matters — one value, different encodings
<!-- bite: fd5c1c43-8644-445f-b720-0806ed27ed5e -->

HTML-escaping is right for text in the HTML body and inside quoted attributes. It is **not enough** in two common places:

- **A URL in `href` or `src`.** `javascript:steal()` contains no characters that HTML escaping changes, and clicking it runs the script. Parse the URL and **allowlist the scheme**: `https:`, `http:`, `mailto:`.
- **Data inside a `<script>` block.** `JSON.stringify` makes valid JavaScript, but if a string contains `</script>`, the browser's HTML parser ends the block right there — before JavaScript ever sees it — and whatever follows is parsed as new HTML. Escape `<` as `\u003c` inside the JSON, or better, pass data through a `data-` attribute or a separate request instead of inlining it.

The rule: **encode for the destination, at the moment of output** — not once on input, because the same value may later land in several contexts.

## 6. SSRF — when the input is a URL your server fetches
<!-- bite: 0c5f6659-b681-4a64-98dd-9c881e8cfadf -->

Some features fetch a URL the user supplies: a webhook target, "import from link", a link preview. If you fetch it as-is, an attacker can point it at addresses only your server can reach — `http://localhost:6379` (your Redis), `http://169.254.169.254/` (the cloud metadata service, which on some setups hands out credentials), or other machines on your private network.

**Validate the destination, not just the format:** allow only `https:`, resolve the hostname, and reject private, loopback and link-local addresses — then connect to the address you checked, not a fresh lookup, or DNS can change its answer in between. Better still, send outbound fetches through a proxy that can only reach the public internet. This is easy to get subtly wrong, so it's worth using a maintained library for it.

## 7. Content Security Policy — a backstop, not a substitute
<!-- bite: 4c28614d-b358-473c-9dcd-a9b0267a1185 -->

Even with correct encoding, a **CSP** header lets the browser block scripts that didn't come from sources you approve, which limits what an XSS that slips through can do. It's defence in depth, layered on correct encoding — covered in [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|security headers and same-origin policy]], this week's other core lesson.

## Worked example — six attacks against real code
<!-- bite: 764639c6-3e75-4538-9c28-bee2c7df4817 -->

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

## Worked example: the encoding file
<!-- bite: 240cefa2-52b1-4e08-8832-fc6e5640d322 -->

The second file handles output: one function for each place a value can land.

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

## Worked example: the attacks to predict
<!-- bite: 7dd8fc78-be18-4c5b-a894-7fb25ac1f198 -->

Here are the attacks the tests throw at that code.

**Predict before running.** For each, does the attack get through?

1. `' OR '1'='1` as a username, into `findUserUnsafe`. Then into `findUserSafe`.
2. `username; DROP TABLE users` as a sort option.
3. `<SCRIPT>steal()</SCRIPT>` and `<img src=x onerror=steal()>` through `stripScriptTags`.
4. `javascript:steal(document.cookie)` as a profile website.
5. A bio of `</script><script>steal()</script>`, inlined as JSON in a page.

## Worked example: the attack tests
<!-- bite: b8c98e16-ffd8-4393-bfe9-0db4f497d745 -->

Each test is one of those attacks, run against the unsafe version and the safe one.

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

## Worked example: run it
<!-- bite: 61c9981f-f87c-4043-82b8-22ff29ad3096 -->

The code lives in a lab beside this lesson, so you can run it yourself.

**Lab:** these files are in [`cybersecurity/04-web-security/01-input-validation-and-output-encoding/labs/javascript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/cybersecurity/04-web-security/01-input-validation-and-output-encoding/labs/javascript). From the vault root, `python3 labs/run.py input-validation-and-output-encoding/javascript` runs them and checks this page still shows the same code.

**Run it.** From the lab folder, `node --test` (Node 22.5 or later; checked with Node 26). Expected:

```text
ℹ tests 7
ℹ pass 7
ℹ fail 0
```

Several tests assert that an attack **succeeds** against the unsafe version — that's the demonstration, not a bug in the tests.

## Worked example: the answers
<!-- bite: cd60a3f6-5ae4-4c79-9f2a-624f22ff78e7 -->

Here is what each attack did. Check your predictions.

**The answers.**

1. The unsafe query returns **all three users**, including `admin`. The safe one returns **nobody**: the whole string is looked up as a username, quotes and all.
2. **Rejected** — the sort option isn't in the allowlist, so no SQL is built from it.
3. **Both get through.** The denylist removes only the exact lowercase pattern it was written for.
4. **Blocked** — the scheme isn't allowed, so the link becomes `#`. Note the legitimate URL beside it: `&` is still HTML-escaped to `&amp;` inside the attribute, as it should be.
5. Unsafe: the bio **closes the script block and opens a new one**. Safe: every `<` becomes `\u003c`, the HTML parser sees no tag, and `JSON.parse` still recovers the identical data.

## Common pitfalls
<!-- bite: 98d63d68-f1bc-48f5-8e24-02bb77592874 -->

1. **Client-side-only validation** — enforced in the browser means enforced nowhere.
2. **Denylists** — stripping `<script>`, blocking the word `SELECT`. Attackers use what you didn't list.
3. **Escaping on input instead of output** — the stored value gets double-encoded in one place and unencoded in another. Store the original; encode for each destination when outputting.
4. **One encoding everywhere** — HTML escaping inside a `javascript:` URL or a `<script>` block doesn't help.
5. **Parameterising values but building identifiers from input** — `ORDER BY ${req.query.sort}` is injectable even when every value is a parameter.
6. **Turning off the framework's escaping** — `dangerouslySetInnerHTML`, `|safe` — for data that isn't actually trusted.

## Check your understanding
<!-- bite: a027a7ae-05ea-4571-9a3d-29c901cca805 -->

Try each one before you open the answer.

1. <!-- q: mcq id="8100caeb" -->
   A login runs this query, built by gluing strings together: `"SELECT * FROM users WHERE username = '" + input + "'"`. The table has 40 users. Someone types `' OR '1'='1` as their username. How many rows come back?

   - [ ] 0, because no user has that name.
   - [x] All 40, because the `WHERE` clause becomes true for every row.
   - [ ] 1, the first user only.
   - [ ] None: the database rejects the quote.

   <details><summary>Answer</summary>

   All 40. The query becomes `WHERE username = '' OR '1'='1'`, and `'1'='1'` is true for every row. The input stopped being a value and became part of the SQL.

   </details>

2. <!-- q: mcq id="7b95809f" -->
   Why does a parameterised query, such as `db.prepare("SELECT * FROM users WHERE username = ?").all(input)`, stop SQL injection when escaping quotes by hand often doesn't?

   - [ ] It removes every quote from the input.
   - [ ] It checks the input against a list of known attacks.
   - [x] The query text and the value are sent separately, so the value is never parsed as SQL.
   - [ ] It only allows letters and numbers.

   <details><summary>Answer</summary>

   The SQL text is fixed, and the value travels on its own, so however it's crafted it can't end the string and start new syntax. Hand escaping has to predict every way a value could break out (quote characters, encodings, database quirks), and one miss is enough.

   </details>

3. <!-- q: mcq id="2f90c362" -->
   An API sorts results with `ORDER BY ${req.query.sort}`. Every *value* in its queries is already a parameter. Is the sort safe, and if not, what fixes it?

   - [ ] Safe, because the other values are parameters.
   - [ ] Fix it by making `sort` a parameter too.
   - [x] Not safe; map each allowed sort name to fixed SQL text in an allowlist and reject anything else.
   - [ ] Fix it by removing semicolons from `sort`.

   <details><summary>Answer</summary>

   Column names and `ORDER BY` directions can't be parameters, only values can. So the user's choice must be looked up in an allowlist like `{ newest: "created_at DESC" }`, and anything not on it rejected. Stripping semicolons is a denylist, and denylists miss what they didn't predict.

   </details>

4. <!-- q: gap id="f724d9aa" answers="&lt;" -->
   When a value is HTML-escaped for the page body, the character `<` becomes ___, so the browser shows a less-than sign instead of starting a tag.

   <details><summary>Answer</summary>

   `&lt;`. The other characters escaped for HTML are `&` (`&amp;`), `>` (`&gt;`), `"` (`&quot;`) and `'` (`&#39;`).

   </details>

5. <!-- q: mcq id="b5d7deaf" -->
   A profile page puts the user's website into `<a href="...">`, after HTML-escaping it. A user sets their website to `javascript:steal(document.cookie)`. What happens when a visitor clicks the link?

   - [ ] Nothing, because the value was HTML-escaped.
   - [x] The script runs, because escaping changes none of its characters; the fix is to allowlist the scheme (`https:`, `http:`, `mailto:`).
   - [ ] The browser blocks every link that contains brackets.
   - [ ] The link opens a page called "javascript".

   <details><summary>Answer</summary>

   It runs. HTML escaping only changes characters like `<` and `"`, and that URL has none that matter. The danger is the scheme itself, so parse the URL and allow only known-safe schemes.

   </details>

6. <!-- q: open id="828a7816" -->
   A feature lets users enter any webhook URL, and your server sends a request to it. Name two addresses an attacker would try, and say what your server must check before it connects.

   <details><summary>Answer</summary>

   `http://localhost:...` or `http://127.0.0.1:...` to reach services on the server itself (like Redis), and `http://169.254.169.254/`, the cloud metadata service, which can hand out credentials. Check: allow only `https:`, resolve the hostname, reject private, loopback and link-local addresses, then connect to the exact address you checked, not a fresh lookup. Better still, send outbound requests through a proxy that can only reach the public internet.

   </details>

## Practice — independent task
<!-- bite: 592f58b6-aa22-4ac6-bb4e-3acb3d6462a7 -->

**The first half of SWE 101's week 7 milestone: check the flagship.**

1. Search the flagship for SQL built from strings, and for the other risky spots — from the flagship's root:

   ```bash
   grep -rnE '`(SELECT|INSERT|UPDATE|DELETE)|dangerouslySetInnerHTML|exec\(' src/
   ```

   Also look for any sort or filter column the user chooses. For each hit, write whether it's safe and why.
2. Write an attack test for the riskiest one — the way the worked example does — that fails before your fix and passes after.
3. If the flagship fetches any user-supplied URL, add destination validation and a test that `http://localhost` and `http://169.254.169.254` are rejected.
4. Add each finding to the flagship's threat model — the week 7 deliverable.

## Practice: when your check is done
<!-- bite: 32f911ad-591b-4608-a9d3-26d0552bea74 -->

Here is how you know the task is finished.

**Done when:** every hit from step 1 is either fixed with a test or documented as safe with a reason, and the attack tests pass.

## Before moving on
<!-- bite: 6a1c0c1c-eb9e-4795-a8c4-385db92673a5 -->

You can show injection and XSS working, fix them structurally, encode for the right context, and validate a URL your server will fetch.

**Recap.** Validate input with allowlists, on the server. Never build SQL, shell commands or HTML out of input: use parameters for values, allowlists for names, argument lists for commands. Encode at output, for the destination's context — HTML body, URL, script block. Check the destination of any URL your server fetches. CSP is a backstop, not a fix.

**Next.** [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|Security headers and the same-origin policy]] — what the browser enforces for you, and how to turn it on.

## Related
<!-- bite: a046fde5-8ca9-4c9b-9e15-0437adccaffe -->
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation concepts]] — the attacker's view of the same bugs
- [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|Security headers and same-origin policy]]
- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]]
- [[backend/07-practices/01-backend-best-practices/index|Backend best practices]] — validation at the boundary

## About this lesson
<!-- bite: 2f62e2ef-f1f8-46cf-aff9-d70f297edeea -->

**Level:** Beginner→Intermediate. **Covers:** allowlist validation on the server, why validation alone can't stop injection, parameterised queries and allowlisted identifiers, argument lists for shell commands, output encoding for the HTML body, URLs and script blocks, SSRF, and CSP as a backstop, with a runnable lab of attack tests. **Where it sits:** lesson 1 of the [[cybersecurity/04-web-security/index|Web Security]] section, the code-level fix for the attacks the ethical-hacking section ran; also a core lesson in week 7 of [[learning/swe-101/index|SWE 101]]. **Sources:** the original vault note, with the lab checked by `labs/run.py`.
