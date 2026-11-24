# Web Security

**Web security is making the application itself safe: the code that handles what users send, the login that decides who they are, the connection that carries it, and the browser rules that keep one site out of another.**

The network-security section locked down your VPS, but it had to leave the web ports open, because that's how people use the app. Every attack in the ethical-hacking section that worked on Juice Shop came in through those open ports. Only the application can stop them. This section is the code-level fix for each one.

## What you'll be able to do

By the end of this section you will be able to:

- fix injection and XSS structurally, with parameters, allowlists and context-aware encoding, and prove it with attack tests;
- store passwords so a stolen database is worth as little as possible, and measure that by cracking a dummy-account database both ways;
- put HTTPS on your VPS with a free, self-renewing certificate, harden it, and check it the way a pentester would;
- switch on the browser's own protections with security headers and cookie flags, and avoid the CORS mistake that turns them off.

## Reading order

1. [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|01 — Input Validation and Output Encoding]] — **[Beginner]** — allowlists, parameterised queries, encoding for each context, SSRF, with a lab of attack tests.
2. [[cybersecurity/04-web-security/02-secure-authentication|02 — Secure Authentication]] — **[Intermediate]** — slow salted hashing, breached-password checks, credential stuffing, MFA and sessions, with a hashcat lab on dummy accounts.
3. [[cybersecurity/04-web-security/03-https-and-tls|03 — HTTPS and TLS]] — **[Intermediate]** — certificates, Let's Encrypt, old versions, HSTS, and checking TLS on your own VPS.
4. [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|04 — Security Headers and the Same-Origin Policy]] — **[Intermediate]** — the same-origin policy, CORS, CSP, cookie flags and CSRF, with a lab that tests every header.

Lessons 01 and 04 are also the two core lessons of week 7 of [[learning/swe-101/index|SWE 101]].

## Related

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation concepts]] — the attacker's side of the same bugs.
- [[cybersecurity/03-network-security/index|Network security]] — the layer below: what reaches the app at all.
- [[cybersecurity/14-api-security/index|API security]] — the same principles for machine clients: BOLA, JWT, SSRF and the OWASP API Top 10.

## About this section

**How it's built:** each lesson is the code-level defence for attacks the learner already ran from the other side: SQL injection and XSS (01), offline password cracking (02), the plain-HTTP network path (03), and cross-site attacks the browser can block (04). 01 and 04 carry runnable labs checked by `labs/run.py`; 02 and 03 run against the learner's own dummy database and VPS. Rebuilt to the [[COURSE-STANDARD|course standard]]: all four lessons converted. Live runs of the commands are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
