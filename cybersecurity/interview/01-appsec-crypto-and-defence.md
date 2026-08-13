# Security Interview — AppSec, Crypto & Defence

From [[cybersecurity/04-web-security/README|04-web-security]], [[cybersecurity/05-cryptography/README|05-cryptography]], [[cybersecurity/06-attacks-and-threats/README|06-attacks-and-threats]], [[cybersecurity/07-security-operations/README|07-security-operations]].

---

### Q1. [Intermediate] 🔥 Explain SQL injection and the *correct* fix.

**Strong answer covers:** user input is concatenated into a query, so the attacker's data is parsed as **code**. `' OR '1'='1` changes the query's meaning entirely.

**The correct fix is parameterised queries / prepared statements** — and the reason matters: the query structure is sent to the database **separately** from the values, so a value can never be re-parsed as syntax. It's not escaping done well; it's making the injection structurally impossible.

**What's *not* the fix:** escaping (encoding bugs and charset tricks defeat it), blocklists (`DROP`, `--`) which are trivially bypassed, and stored procedures — which are only safe if they *themselves* don't concatenate.

**The generalisation to state, because it's the real insight:** this is one instance of a whole class — **data being interpreted as code**. XSS, command injection, LDAP injection, template injection, XXE, deserialisation, and prompt injection are all the same bug in different interpreters. The fix is always the same shape: **separate code from data at the interface, don't try to sanitise the mixture.**

---

### Q2. [Intermediate] 🔥 XSS — the three types, and how you actually prevent it.

**Strong answer covers:**
- **Stored** — the payload is persisted (a comment) and served to every viewer. Worst impact.
- **Reflected** — the payload is in the request and echoed back; needs a crafted link.
- **DOM-based** — never touches the server; client-side JS writes attacker-controlled data into a sink like `innerHTML`.

**Prevention — and the key point is that it's context-dependent:** **output encoding at the point of use**, where the correct encoding depends on whether you're writing into HTML body, an attribute, JavaScript, a URL, or CSS. HTML-encoding data that lands inside a `<script>` block does nothing. That context-sensitivity is why hand-rolled sanitisers fail and why you use a framework that encodes by default (React, Angular) and treat every escape hatch (`dangerouslySetInnerHTML`, `v-html`, `innerHTML`) as a code-review trigger.

**Defence in depth:** a strict **Content-Security-Policy** (nonce-based, no `unsafe-inline`) turns many XSS bugs from critical to non-exploitable. `httpOnly` cookies mean XSS can't steal the session directly. Neither replaces encoding.

---

### Q3. [Intermediate] 🔥 What is CSRF and why did `SameSite` largely solve it?

**Strong answer covers:** the browser attaches cookies to requests **automatically, based on destination**, regardless of which site initiated them. So a malicious page can trigger a state-changing request to your bank, and the browser helpfully includes the session cookie. The attacker can't *read* the response (same-origin policy), but the *action* happens.

**Classic defence:** a **synchroniser token** — a per-session random value the server issues and the form must return. The attacker can't read it cross-origin, so they can't include it.

**Why it's now largely solved:** `SameSite=Lax` is the **default** in modern browsers, so cookies aren't sent on cross-site *state-changing* requests (POST, etc.). Combined with checking `Origin`/`Referer`, that covers most cases.

**The nuance worth adding:** CSRF only applies to **implicit credentials** — cookies, HTTP auth, client certs. An API using an `Authorization: Bearer` header set explicitly by JavaScript isn't vulnerable, because nothing attaches it automatically. That's a genuinely useful distinction to be able to draw.

---

### Q4. [Intermediate] 🔥 What's SSRF and why is it so severe in cloud environments?

**Strong answer covers:** you make the *server* issue a request to an attacker-chosen URL. The server is inside the network perimeter, so it can reach things the attacker can't — internal admin panels, databases, and **the cloud metadata service at `169.254.169.254`**, which historically hands out IAM credentials to anything that asks.

That's the escalation path: a webhook or image-fetch feature becomes full cloud account compromise. **Capital One (2019)** is the canonical case.

**Defence — and the point is that blocklists don't work:** DNS rebinding, redirects, IPv6 forms, decimal/octal IP encodings, and `0.0.0.0` all defeat naive filters. So:
- **Allowlist** destinations rather than blocklisting.
- Resolve the hostname and validate the **resolved IP** against private ranges, then connect to *that IP* (to defeat DNS rebinding between check and use).
- Don't follow redirects, or re-validate each hop.
- **Enforce IMDSv2** (session-token-required) — a single setting that kills the metadata escalation.
- Egress-filter at the network layer. Defence in depth, because application-layer validation will eventually be bypassed.

---

### Q5. [Intermediate] Hashing vs encryption vs encoding — when do you use each?

**Strong answer covers:** **Encoding** (base64, URL encoding) is **not security** — it's a data-format transformation, trivially reversible, for transport safety. **Hashing** is one-way, for integrity and password storage. **Encryption** is two-way with a key, for confidentiality.

**Then the specifics:** for passwords, a *slow, memory-hard* hash (Argon2id/scrypt/bcrypt) — general-purpose hashes like SHA-256 are far too fast. For integrity with authentication, an **HMAC** (a plain hash of `secret || message` is vulnerable to length-extension). For encryption, **AEAD** modes (AES-GCM, ChaCha20-Poly1305) that give confidentiality *and* integrity together — because encryption without integrity lets an attacker flip bits in ciphertext, which is how padding-oracle attacks work.

**The rule to end on:** **don't implement crypto.** Use a vetted library at the highest level of abstraction available (libsodium, your platform's AEAD API). Nearly every real-world crypto failure is a *usage* failure — reused nonces, ECB mode, hardcoded keys, no key rotation — not a broken algorithm.

---

### Q6. [Intermediate] 🔥 Walk me through securing a new web application from scratch.

**Strong answer covers, framed as threat modelling rather than a checklist:**

- **Identity** — strong password hashing, MFA available, secure session handling, rate-limited login, no user enumeration.
- **Authorisation on every request, at the data layer** — the IDOR defence. Never trust a client-supplied ID.
- **Input** — validate on the server (client validation is UX), parameterised queries, context-aware output encoding, strict file-upload handling (type by content not extension, serve from a separate origin).
- **Transport** — TLS everywhere, HSTS, secure cookie flags (`httpOnly`, `Secure`, `SameSite`).
- **Headers** — CSP, `X-Content-Type-Options: nosniff`, frame-ancestors.
- **Secrets** — in a secret manager, never in the repo, rotated. Scan history for leaked credentials.
- **Dependencies** — SCA scanning in CI, a patch cadence. Most breaches come through a known CVE in something you didn't write.
- **Logging and detection** — log auth events and authorisation failures; you can't respond to what you can't see.
- **Least privilege everywhere** — database user, cloud IAM role, container user.

**What lifts this answer:** name the **trust boundaries** first (browser ↔ API, API ↔ database, API ↔ third parties) and reason about what crosses each. That's threat modelling, and it's what they're actually testing.

---

### Q7. [Intermediate] What's the difference between a vulnerability, a threat, and a risk?

**Strong answer covers:** a **vulnerability** is a weakness. A **threat** is an actor or event that could exploit it. **Risk** = likelihood × impact — the thing you actually make decisions on.

**Why the distinction matters practically:** it's how you prioritise. A critical CVE in a component that isn't network-reachable and handles no sensitive data may be lower risk than a medium-severity bug on your login page. **CVSS is a severity score, not a risk score** — using it as a work queue means fixing loud things while real exposure sits untouched. Being able to say that clearly is a mark of someone who's done remediation rather than just scanning.

---

### Q8. [Intermediate] 🔥 What is defence in depth, and give a concrete example.

**Strong answer covers:** layered controls so no single failure is fatal — because every control eventually fails, and the question is what happens next.

**A good concrete example (SSRF, from Q4):** application-layer URL allowlisting → resolve-and-validate the IP → IMDSv2 so metadata needs a token → network egress filtering → an IAM role scoped to almost nothing → alerting on unusual metadata access. Any one of those can be bypassed; all six failing simultaneously is unlikely.

**The mindset to state:** **assume breach.** Perimeter security assumes the inside is trustworthy, which is why lateral movement is so easy once someone's in. Zero-trust means authenticating and authorising every request regardless of network position — which is what [[foundations/networking/12-tls-and-transport-security|mTLS]] and service mesh identity exist to provide. → [[cybersecurity/07-security-operations/01-defensive-architecture|defensive architecture]]

---

### Q9. [Intermediate] Walk me through incident response.

**Strong answer covers the standard phases with real content:**
1. **Preparation** — the phase that determines everything else. Runbooks, logging that exists *before* you need it, defined roles, practised communication paths.
2. **Detection & analysis** — is it real? What's the scope? Establish a timeline.
3. **Containment** — short-term (isolate the host) then long-term. **Preserve evidence before you remediate** — memory and volatile state are gone after a reboot.
4. **Eradication** — remove the foothold, close the vector. Assume persistence mechanisms.
5. **Recovery** — restore from known-good, monitor closely for reinfection.
6. **Lessons learned** — blameless, with owned action items.

**The judgement call to raise:** containment often conflicts with investigation — pulling the plug stops the bleeding but destroys the evidence and tips off the attacker. That's a *business* decision about risk tolerance, not a technical one, and knowing to escalate it rather than decide unilaterally is the senior signal. → [[cybersecurity/07-security-operations/04-incident-response|incident response]]

---

### Q10. [Intermediate] How would you detect an attacker already inside the network?

**Strong answer covers:** you're looking for **behaviour**, not signatures — a competent attacker uses legitimate tools (**living off the land**: PowerShell, `psexec`, WMI, `certutil`), so "malware detected" won't fire.

**Signals worth naming:**
- **Authentication anomalies** — impossible travel, a service account logging in interactively, a spike in failed logins followed by a success.
- **Lateral movement** — a workstation connecting to another workstation, unusual SMB/RDP patterns.
- **Discovery activity** — enumeration of AD, shares, or network scanning from an endpoint.
- **Exfiltration** — large or unusual outbound transfers, **DNS tunnelling** (long, high-entropy subdomains — an under-monitored channel precisely because DNS is usually allowed out).
- **Persistence** — new scheduled tasks, services, or registry run keys.

**The framing that scores:** map detections to **MITRE ATT&CK** so you can reason about coverage gaps systematically rather than accumulating ad-hoc rules. And mention **honeytokens** — a fake credential or file that nobody legitimate should ever touch, so an alert on it is essentially zero false-positive. Cheap and remarkably effective. → [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|threat hunting]]
