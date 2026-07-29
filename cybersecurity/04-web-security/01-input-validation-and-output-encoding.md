# Input Validation & Output Encoding

The defensive counterpart to [[07-exploitation-concepts|exploitation-concepts]]'s injection and XSS categories: those vulnerability classes exist because untrusted input was trusted as if it were code or safe markup. The fix is two distinct disciplines that are often conflated but solve different halves of the problem.

## Input validation — reject or normalize what comes in

Checking that incoming data matches what's actually expected *before* using it anywhere — an age field should be a small positive integer, an email field should match a valid email shape, a file upload should match an expected type. Validation should happen server-side, always, even if client-side validation also exists for a smoother user experience — client-side checks are trivially bypassed (an attacker doesn't have to use your form at all; they can send a request directly, see [[08-common-tools|Burp Suite]]).

```python
# allowlist validation: define what IS allowed, reject everything else
import re
def is_valid_username(username):
    return bool(re.fullmatch(r"[a-zA-Z0-9_]{3,20}", username))
```

**Allowlisting** (defining exactly what's acceptable) is more robust than **denylisting** (trying to block known-bad patterns) — a denylist has to anticipate every possible malicious variant in advance, while an allowlist only has to define what's legitimately expected, which is a much smaller and more stable target.

## Why validation alone doesn't fully solve injection

Validation reduces the attack surface but doesn't structurally eliminate injection — a value that passes validation as "a normal-looking string" can still be dangerous if it's later concatenated directly into a SQL query or shell command. The actual fix for injection specifically is **parameterized queries / prepared statements** (see [[07-exploitation-concepts|exploitation-concepts]] for why the underlying vulnerability exists):

```python
# vulnerable: string concatenation lets input become part of the query's syntax
cursor.execute("SELECT * FROM users WHERE username = '" + username + "'")

# safe: input is passed as data, never interpreted as SQL syntax, regardless of its content
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

Parameterized queries work because the database driver keeps the query structure and the data completely separate at the protocol level — there's no way for a value, however crafted, to break out of being "just data."

## Output encoding — the fix for XSS specifically

Where injection is about data reaching an interpreter unsafely, XSS is about data reaching **the browser's HTML/JS parser** unsafely. The fix is encoding output for the context it's being placed into, so special characters are displayed literally instead of being interpreted as markup or script:

```python
# vulnerable: raw user input dropped directly into HTML
html = f"<p>Welcome, {username}</p>"

# safe: HTML-encode before embedding — '<', '>', '&', '"' become their literal-safe entity equivalents
import html as html_lib
safe_output = f"<p>Welcome, {html_lib.escape(username)}</p>"
```

Most modern web frameworks (React, Vue, Django templates) HTML-encode output by default automatically — XSS vulnerabilities in these frameworks usually happen specifically where a developer deliberately opts out of that default (`dangerouslySetInnerHTML` in React, `|safe` in Django templates) for a value that isn't actually safe.

## Context matters — the same data needs different encoding in different places

The correct encoding depends on *where* the data is being placed — data going into an HTML attribute, a URL parameter, a JavaScript string literal, and a SQL query each need different escaping rules, because each context has different special characters and different escape syntax. Using HTML-encoding everywhere regardless of context is a common mistake that leaves gaps — e.g. HTML-encoding alone doesn't protect a value being embedded inside a `<script>` block.

## Content Security Policy — a backstop, not a substitute

Even with correct output encoding, **CSP** (covered in [[04-security-headers-and-same-origin-policy|security-headers-and-same-origin-policy]]) adds a browser-enforced backstop that limits what an XSS payload could do even if one somehow slips through — defense in depth, not a replacement for encoding output correctly in the first place.

## Gotchas

- Validating input at the point it enters the system doesn't remove the need to also encode it correctly at every point it's later *output* — these are two separate controls addressing two separate risks (injection into an interpreter vs. rendering into a browser), and skipping either one leaves a gap.
- Relying only on denylisting specific "known bad" characters or patterns is fragile — attackers routinely find encoding tricks or edge cases a denylist didn't anticipate; allowlisting what's valid is the more durable approach.
- Trusting client-side-only validation is one of the most common beginner mistakes — anything enforced only in the browser is enforced nowhere, from an attacker's perspective, since they can bypass the browser UI entirely.

## Related
- [[07-exploitation-concepts|exploitation-concepts]]
- [[04-security-headers-and-same-origin-policy|security-headers-and-same-origin-policy]]
- [[02-secure-authentication|secure-authentication]]
