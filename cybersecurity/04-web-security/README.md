# Web / Application Security

Securing the software itself — the defensive counterpart to [[07-exploitation-concepts|exploitation-concepts]]'s vulnerability categories. Where that note explains why injection, XSS, and broken access control work mechanically, this folder covers the specific controls that prevent them.

## Reading order
1. [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]] — **[Beginner]** — allowlisting, parameterized queries (the actual fix for injection), context-aware output encoding (the actual fix for XSS)
2. [[02-secure-authentication|secure-authentication]] — **[Intermediate]** — password hashing (bcrypt/Argon2), salting, MFA, session management, JWT pitfalls
3. [[03-https-and-tls|https-and-tls]] — **[Intermediate]** — the TLS handshake, certificates and the chain of trust, HSTS, common misconfigurations
4. [[04-security-headers-and-same-origin-policy|security-headers-and-same-origin-policy]] — **[Advanced]** — same-origin policy, CORS, CSP, clickjacking defenses, CSRF-protecting cookie flags

## Related
- [[cybersecurity/14-api-security/README|API security]] — the same principles for machine clients, minus the browser: BOLA, JWT, SSRF, the OWASP API Top 10
- [[cybersecurity/README|cybersecurity curriculum map]]
- [[cybersecurity/03-network-security/README|network-security]] — the network-layer counterpart to this folder's application-layer focus
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation-concepts]] — the offensive framing of the same vulnerability classes
