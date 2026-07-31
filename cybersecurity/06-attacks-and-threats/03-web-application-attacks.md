# Web Application Attacks

**[reference]** — from the roadmap.sh cyber-security roadmap (OWASP branch). Educational/defensive: how the common web attacks work. The *defenses* are in [[cybersecurity/04-web-security/README|web security]]; this is the attacker's-eye catalog, organized around the **OWASP Top 10** — the industry-standard list of the most critical web-app risks.

## The OWASP Top 10 (the mental checklist)

Roughly, in current form:

1. **Broken Access Control** — the #1 risk: users acting outside their permissions (viewing another user's data by changing an ID in the URL — *IDOR*, insecure direct object reference; accessing admin functions without being admin). Fix: enforce authorization server-side on every request, deny by default.
2. **Cryptographic Failures** — sensitive data exposed through weak/missing [[cybersecurity/05-cryptography/README|crypto]] (plaintext passwords, no TLS, weak hashing). Fix: encrypt in transit and at rest, hash passwords properly ([[cybersecurity/04-web-security/02-secure-authentication|salting/bcrypt]]).
3. **Injection** — untrusted input interpreted as a command. The classic is **SQL injection** (`' OR '1'='1`), but also OS-command, LDAP, NoSQL injection. Fix: **parameterized queries** / prepared statements, never string-concatenate untrusted input into a query ([[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation]]).
4. **Insecure Design** — flaws in the design itself, not the implementation (missing rate limits, a password-reset flow that leaks whether an account exists). Fix: threat-model early.
5. **Security Misconfiguration** — default credentials, verbose error messages, unnecessary features enabled, missing [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|security headers]]. The most common issue in the wild.
6. **Vulnerable & Outdated Components** — using a library/framework with known CVEs (the Log4Shell class of problem). Fix: dependency scanning, patch management.
7. **Identification & Authentication Failures** — weak passwords, no MFA, session flaws, credential stuffing. Fix: [[cybersecurity/04-web-security/02-secure-authentication|strong auth + MFA]].
8. **Software & Data Integrity Failures** — trusting unverified updates/plugins, insecure deserialization, supply-chain compromise. Fix: verify signatures, SBOMs.
9. **Security Logging & Monitoring Failures** — not detecting breaches because nothing was logged/watched. Fix: [[cybersecurity/07-security-operations/02-logging-siem-and-detection|logging & SIEM]].
10. **Server-Side Request Forgery (SSRF)** — tricking the server into making requests to internal/unintended systems (fetching a URL the attacker controls, reaching cloud metadata endpoints). Fix: allowlist outbound destinations, block internal ranges.

## The injection attacks in more detail

- **SQL Injection (SQLi)** — inject SQL through an input to read/modify/destroy the database, or bypass auth. Still devastating and common. The one true fix is **parameterized queries** (the database treats input as data, never code) — input filtering alone is insufficient.
- **Cross-Site Scripting (XSS)** — inject JavaScript that runs in *other users'* browsers (stored XSS in a saved comment, reflected XSS in a URL, DOM-based in client code). Used to steal sessions, keylog, deface. Fix: **output encoding** (escape data for its context) + a strong Content-Security-Policy.
- **CSRF (Cross-Site Request Forgery)** — trick a logged-in victim's browser into making an unwanted authenticated request (transfer money, change email). Fix: anti-CSRF tokens, `SameSite` cookies.
- **Directory/Path Traversal** — `../../etc/passwd` in a file parameter to read files outside the web root. Fix: canonicalize and validate paths, never pass user input to the filesystem directly.
- **XXE, insecure deserialization, command injection** — related "untrusted input becomes execution" classes.

## The unifying lesson

Nearly every web attack reduces to one root cause: **untrusted input treated as trusted** — as code (injection/XSS), as authorization (broken access control), or as a destination (SSRF). The unifying defenses: **never trust client input**, enforce **authorization server-side on every request**, use **parameterized/encoded** boundaries so data can't become code, and assume you'll be breached so you [[cybersecurity/07-security-operations/README|log and monitor]]. Practicing these safely is what platforms like [[cybersecurity/02-ethical-hacking/12-practice-exercises|deliberately-vulnerable labs]] (DVWA, PortSwigger Academy, OWASP Juice Shop) are for.

## Related
- [[cybersecurity/04-web-security/README|Web Security]] — the defenses for every attack here
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|Input Validation & Output Encoding]] — the fix for injection/XSS
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation Concepts]] — the vulnerability-class framing
