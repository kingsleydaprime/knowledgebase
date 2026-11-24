---
id: 06688473-a9d9-482e-8d83-562e13a8ba22
---

# HTTPS and TLS

**HTTPS is ordinary web traffic sent inside TLS, a protocol that encrypts the connection, proves which server you're talking to, and catches anyone changing data on the way.**

## Before you start
<!-- bite: 0f55a874-4ed0-4d3d-989b-5e17c28e7a93 -->

You should have:

- Your VPS with nginx and a default-deny firewall that allows 80 and 443 → [[cybersecurity/03-network-security/01-firewalls|firewalls]].
- A domain name (or a free subdomain) pointing at the VPS's IP. A certificate is issued for a name, not an IP address.
- Read what encryption in transit protects → [[cybersecurity/03-network-security/03-vpns-and-encryption-in-transit|VPNs and encryption in transit]].

After this lesson you will be able to:

1. Name the three things TLS guarantees, and the things it doesn't.
2. Get a free certificate for your VPS with Let's Encrypt, and make sure it renews itself.
3. Turn off old TLS versions, redirect HTTP to HTTPS and add HSTS, then check it all the way a pentester would.
4. Watch the public certificate logs for certificates issued for your domain that you didn't ask for.

**Study route.** Kid version and §1–4, then the worked example on your VPS. How the handshake works inside, with the maths, is in [[networking/12-tls-and-transport-security/index|TLS and transport security]]; this lesson is about running it well.

## What HTTPS and TLS are
<!-- bite: a4b46146-f105-479f-9b8b-68da423c33fd -->

Remember the password from lesson 02, travelling from the login form to your server? Everything that lesson did, the slow hash, the rate limit, assumed nobody read the password on the way. On plain HTTP, anyone on the path can: the café Wi-Fi, every network between the user and your VPS.

HTTPS is what makes that assumption true. You met the idea in the network-security section: encryption in transit, for one connection. This lesson puts it on your own VPS, properly: a real certificate, no weak old versions, no plain-HTTP gap, and a way to notice if someone gets a certificate for your name.

## The kid version
<!-- bite: b17582be-b42b-4a21-90c6-f5c830b817b7 -->

Imagine sending a parcel through a courier. Three things could go wrong. Someone could open it and look inside. Someone could swap what's inside. Or a stranger could pretend to be the courier and take it from you.

HTTPS stops all three. The parcel is locked in a box only the real shop can open (nobody reads it). The box has a seal that shows if anyone tampered with it (nobody changes it). And the courier shows an ID card, issued by an office everybody trusts, that says "this really is the shop's courier" (nobody pretends).

**Where the analogy stops working.** The ID card proves the courier works for *that shop*. It doesn't prove the shop is honest. A scam website can have a perfectly valid certificate for its own scam domain. The padlock means "you're privately connected to this exact name", not "this site is safe".

## 1. The three guarantees, and what they leave out
<!-- bite: a2648b58-9246-4d1d-ac56-c123e48b04df -->

TLS gives every connection three things. You'll recognise the first two from the [[cybersecurity/01-fundamentals/02-cia-triad|CIA triad]]:

1. **Confidentiality** — the contents are encrypted. People on the path see only noise.
2. **Integrity** — any change on the way is detected, so nobody can slip a malicious script into your page in transit.
3. **Authentication** — the server proves, with its certificate, that it really is the name in the address bar.

What it leaves out matters just as much. TLS protects the connection, not the endpoints: it says nothing about whether the server is secure once you're connected, or how it stores your data. A SQL injection travels inside HTTPS just fine, and so does a phishing page on its own domain.

## 2. Certificates and who vouches for them
<!-- bite: 0ab9ac64-7ef2-48a0-a808-c4b8ea4a330b -->

A **certificate** says "this public key belongs to `lab.example.com`", and it's signed by a **certificate authority (CA)**. Your browser and operating system come with a list of CAs they trust. When you connect, the browser checks three things: the signature chains back to a trusted CA, the certificate hasn't expired, and the name on it matches the site you asked for. Fail any one and you get the full-page warning.

Certificates used to cost money and take days. **Let's Encrypt** changed that: it's a free CA that issues certificates automatically, after checking you really control the domain (it asks your server to serve a file on port 80, which is one reason your firewall keeps 80 open). Its certificates last 90 days, on purpose, so renewal has to be automatic, and so mistakes don't last long.

Every certificate a public CA issues is also recorded in public **Certificate Transparency** logs. Anyone can search them. That's a gift to defenders, and it's the detection half of the worked example.

## 3. The gaps that remain once HTTPS is on
<!-- bite: 65741cad-c2cc-4cc6-af54-320b56e11681 -->

Turning HTTPS on isn't the end. Three gaps are common, and each is a standard pentest finding:

1. **Old protocol versions.** TLS 1.0 and 1.1 (and SSL before them) have known weaknesses. Allow TLS 1.2 and 1.3 only.
2. **The plain-HTTP first visit.** A user types `lab.example.com` and the browser tries `http://` first. Your redirect to HTTPS fixes it, but that first request went out in the open, and an attacker on the café Wi-Fi can answer it themselves and keep the user on plain HTTP forever. This is called **SSL stripping**.
3. **Mixed content.** An HTTPS page that loads a script over `http://` gives the network a way to change that script. Browsers block most of it now, but it still breaks pages.

The fix for the second gap is **HSTS**, a header that tells the browser "for the next year, only ever use HTTPS for this site". After the first visit, the browser never tries plain HTTP again, so there's no request to strip.

## Terms used in this lesson
<!-- bite: 62fdeb09-5854-4b2e-835b-7eb0308a399f -->

1. **TLS (Transport Layer Security)**: The letters stand for those words. It's the protocol that encrypts and authenticates a connection. **SSL** is its old, broken predecessor; people still say "SSL certificate" out of habit.
2. **Certificate**: This is a signed statement that a public key belongs to a domain name, with an expiry date.
3. **CA (certificate authority)**: The letters stand for those words. It's an organisation your browser trusts to sign certificates, like Let's Encrypt.
4. **Chain of trust**: This is the line of signatures from your certificate, through one or more intermediate certificates, up to a CA the browser already trusts.

## Terms used in this lesson: the gaps and the guards
<!-- bite: 645000c5-ab51-44ee-87bd-6c3947d6eaa5 -->

The rest of the terms name the attacks on HTTPS and the tools that close them.

5. **HSTS (HTTP Strict Transport Security)**: The letters stand for those words. It's a header telling the browser to use only HTTPS for your site for a set time.
6. **SSL stripping**: This is an attacker on the network keeping a victim on plain HTTP by intercepting the first, unencrypted request.
7. **Certificate Transparency**: This is a set of public logs recording every certificate public CAs issue, so anyone can spot one issued for their domain without permission.
8. **ACME**: This is the protocol Let's Encrypt uses to prove you control a domain and issue a certificate automatically. `certbot` is the usual ACME client.

## 4. Seeing TLS the way a pentester does
<!-- bite: 7191d286-e789-4617-b6a7-5e8b62fbe55d -->

On an engagement, TLS is checked early, because it's quick and the findings are clear. The usual questions:

1. Which protocol versions does the server accept? (TLS 1.0 or 1.1 is a finding.)
2. Which cipher suites does it offer, and are any weak?
3. Is the certificate valid, unexpired, and for the right name?
4. Does plain HTTP redirect, and is HSTS set?

Three tools answer them. `openssl s_client` lets you try one version by hand. `nmap --script ssl-enum-ciphers` lists every version and cipher with a letter grade, and you already know nmap. `testssl.sh` runs the whole checklist and prints a report. In the worked example you run them against your own VPS, before and after, the same loop as every lesson so far.

## Worked example — get a certificate
<!-- bite: 7b7b2dda-2013-4ef8-b943-93b278470ad7 -->

On your VPS, with your domain (here `lab.example.com`) pointing at it and nginx running:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d lab.example.com --redirect
```

`certbot` proves to Let's Encrypt that you control the domain, using a temporary file served on port 80, then gets the certificate and edits your nginx config to use it. `--redirect` adds a rule sending every `http://` request to `https://`.

Renewal is automatic: the package installs a timer that runs twice a day and renews anything within 30 days of expiry. Check both:

```bash
systemctl list-timers | grep certbot      # the renewal timer is scheduled
sudo certbot renew --dry-run              # a full practice renewal, without changing anything
```

## Worked example: harden the nginx config
<!-- bite: ae90ae93-75a8-4b74-b0a4-69dfc7ade44b -->

Open the site's config (`/etc/nginx/sites-enabled/default` or the file certbot edited) and make sure the HTTPS `server` block has these lines:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
add_header Strict-Transport-Security "max-age=31536000" always;
```

The first line refuses anything older than TLS 1.2. Recent certbot versions already set it in their shared options file; writing it here makes it certain. The second line is HSTS for one year (31,536,000 seconds). `always` adds it to error pages too.

Start HSTS with this plain version. `includeSubDomains` and `preload` make it stronger, but they're hard to undo: if any subdomain can't do HTTPS yet, it breaks for a year. Add them once everything under your domain is on HTTPS.

Test and reload: `sudo nginx -t && sudo systemctl reload nginx`.

## Worked example: check it like a pentester
<!-- bite: b32bb497-4335-4f2a-b3a9-51bb3a1e0d43 -->

From your laptop, check each of §4's questions. **Predict first:** which of the TLS 1.1 and TLS 1.2 attempts will connect?

```bash
curl -sI http://lab.example.com | head -3                        # expect 301 to https://
curl -sI https://lab.example.com | grep -i strict-transport       # expect the HSTS header
openssl s_client -connect lab.example.com:443 -tls1_1 </dev/null  # expect a failure
openssl s_client -connect lab.example.com:443 -tls1_2 </dev/null  # expect success
nmap --script ssl-enum-ciphers -p 443 lab.example.com
```

The TLS 1.1 attempt fails with a handshake error, and TLS 1.2 connects and prints the certificate chain. nmap lists only `TLSv1.2` and `TLSv1.3`, each cipher with a grade, and a least-strength grade at the bottom; aim for `A`. If you have time, run `testssl.sh lab.example.com` for the full report.

## Worked example: the detection half
<!-- bite: 3f19a1d3-743a-4c8d-b8f6-f96710f5fdc9 -->

Two things to watch, both outside your server.

**Expiry.** Renewal is automatic, but automatic things break quietly. Check the date yourself, and put a reminder or a monitor on it:

```bash
echo | openssl s_client -connect lab.example.com:443 2>/dev/null | openssl x509 -noout -enddate
```

## Worked example: certificates you didn't ask for
<!-- bite: 95c17d30-1112-4ac9-8d31-362218c6ff83 -->

The second thing to watch is the public record of every certificate for your name.

**Certificates you didn't ask for.** Search the Certificate Transparency logs for your domain:

```bash
curl -s "https://crt.sh/?q=lab.example.com&output=json" | python3 -m json.tool | grep -E '"issuer_name"|"not_before"'
```

Every certificate listed should be one *you* got. One you didn't means someone convinced a CA they controlled your domain, possibly by taking over your DNS, and they can now impersonate your site with a valid padlock. That's an incident, and CT logs are how you'd find out.

## Common pitfalls and traps
<!-- bite: b85105c2-d571-4646-9be5-1f0f93c04ff4 -->

1. **"It has a padlock, so it's safe."** The padlock proves a private connection to that exact name. Scam sites have padlocks too.
2. **Leaving TLS 1.0 and 1.1 on.** Old versions stay enabled until someone turns them off. Set `ssl_protocols` yourself.
3. **Preloading HSTS too early.** `includeSubDomains; preload` breaks every subdomain that isn't on HTTPS yet, for as long as `max-age` says, and getting off the preload list takes months.
4. **Closing port 80.** It feels safer, but Let's Encrypt renewals use it, and the redirect lives there. Keep 80 open; it only ever redirects.
5. **Nobody watching expiry.** An expired certificate takes the whole site down with a warning page. Renewal timers fail quietly, so check them.
6. **Turning certificate checks off in code.** `verify=False` or `rejectUnauthorized: false` "just for testing" removes the authentication guarantee completely, and tends to stay in.

## Check your understanding
<!-- bite: 5a7156f7-79c2-48a0-97a6-c127fb4c20fa -->

Try each one before you open the answer.

1. <!-- q: mcq id="c7dfeb8c" -->
   A phishing site at `paypa1-login.com` has a valid certificate and a padlock. What does the padlock prove?

   - [ ] That the site belongs to PayPal.
   - [ ] That the site has been checked for malware.
   - [x] That your connection is encrypted and you're really talking to `paypa1-login.com`, whoever owns it.
   - [ ] Nothing, because phishing sites can't get certificates.

   <details><summary>Answer</summary>

   A certificate proves the server controls that exact name and that the connection is private. Anyone can get one for a domain they own, including a look-alike domain. The padlock says nothing about whether the owner is honest.

   </details>

2. <!-- q: mcq id="ab7199ef" -->
   A user on café Wi-Fi types `bank.example` into the address bar. The bank redirects HTTP to HTTPS, but doesn't send HSTS. What can an attacker on the same Wi-Fi do?

   - [ ] Nothing, because the bank redirects to HTTPS.
   - [x] Intercept the first plain-HTTP request and keep the user on an HTTP version of the site they control (SSL stripping).
   - [ ] Read the bank's HTTPS traffic directly.
   - [ ] Get a certificate for `bank.example`.

   <details><summary>Answer</summary>

   The first request goes out over plain HTTP before the redirect, and an attacker on the network can answer it instead of the bank. HSTS fixes this: after one visit, the browser never sends plain HTTP to that site again, so there's no first request to intercept.

   </details>

3. <!-- q: exact id="b775dc29" answer="31536000" accept="31,536,000" -->
   You want HSTS to last one year of 365 days. `max-age` is given in seconds. What number goes after `max-age=`?

   <details><summary>Answer</summary>

   31536000. 365 days × 24 hours × 60 minutes × 60 seconds = 31,536,000.

   </details>

4. <!-- q: mcq id="38479666" -->
   You run `openssl s_client -connect shop.example:443 -tls1_1` and it connects successfully, printing a certificate chain. What does that tell you?

   - [ ] The server is correctly configured.
   - [x] The server still accepts TLS 1.1, an old version that should be turned off. It's a finding.
   - [ ] The certificate has expired.
   - [ ] The server doesn't support TLS 1.3.

   <details><summary>Answer</summary>

   A successful TLS 1.1 handshake means the old version is still allowed. Modern guidance is TLS 1.2 and 1.3 only. It's a quick, standard finding in a pentest report, fixed with one config line (`ssl_protocols TLSv1.2 TLSv1.3;` in nginx).

   </details>

5. <!-- q: mcq id="6b1e2e72" -->
   A team closes port 80 on their server, "since everything is HTTPS now". A month later their Let's Encrypt renewal fails. Why?

   - [ ] Let's Encrypt only works on port 80 for HTTP sites.
   - [x] Renewal proves control of the domain by serving a file on port 80, and that check can't reach the server.
   - [ ] Closing port 80 revokes the certificate.
   - [ ] HTTPS certificates can only be renewed manually.

   <details><summary>Answer</summary>

   Let's Encrypt's usual check (HTTP-01) fetches a file from the domain on port 80. With 80 closed, the check fails and the renewal with it. Port 80 is safe to keep open when all it does is redirect to HTTPS and answer these checks.

   </details>

6. <!-- q: open id="c18157f9" -->
   You search the Certificate Transparency logs for your domain and find a certificate issued last week, by a CA you've never used, that you didn't request. Explain why this matters and what it suggests.

   <details><summary>Answer</summary>

   Someone convinced a CA that they controlled your domain, perhaps through a DNS takeover, a hijacked registrar account or a mistake at the CA. With that certificate they can impersonate your site with a valid padlock, so users get no warning. Treat it as an incident: check your DNS and registrar accounts, ask the CA to revoke the certificate, and find how control was proven. CT logs exist so this can be spotted at all.

   </details>

## Practice — HTTPS on your VPS, checked
<!-- bite: e4dc00f7-c630-4877-a99f-ed80fa23aa94 -->

**Task.** Put HTTPS on your VPS and prove every part of it.

1. Run the nmap `ssl-enum-ciphers` scan *before* you change anything, and save the output.
2. Get a certificate with certbot, with the redirect, and confirm renewal works with `--dry-run`.
3. Set `ssl_protocols` and HSTS in nginx, reload, and run every check from the worked example.
4. Search crt.sh for your domain and account for every certificate listed.

## Practice: when your HTTPS is done
<!-- bite: fd5b7df3-9079-46d7-b40e-0859b4237b10 -->

Here is how you know the task is finished, plus a stretch step.

**Done when:** plain HTTP redirects, the HSTS header is present, TLS 1.1 is refused, nmap shows only TLS 1.2 and 1.3 with a grade of `A`, the dry-run renewal succeeds, and every certificate on crt.sh is one you requested. Record the run in `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Write a short pentest-style finding for the *before* state (from step 1), using the format from [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|reporting]]: what was wrong, the risk, the fix you applied, and how you'd detect it coming back.

## Before moving on
<!-- bite: 1e1b953a-07e2-465d-8f8a-1dc265d88da4 -->

You can now name TLS's three guarantees and its limits, get and auto-renew a free certificate, refuse old protocol versions, close the plain-HTTP gap with a redirect and HSTS, check a server's TLS like a pentester, and watch Certificate Transparency logs for certificates you didn't request.

**Recap for later lookup:** TLS = confidentiality + integrity + server authentication; not endpoint security. `certbot --nginx -d NAME --redirect`; `certbot renew --dry-run`. `ssl_protocols TLSv1.2 TLSv1.3;`. HSTS `max-age=31536000`; add `includeSubDomains; preload` only when every subdomain is ready. Check with `openssl s_client -tls1_1`, `nmap --script ssl-enum-ciphers`, `testssl.sh`. Watch expiry and crt.sh. Keep port 80 open, redirecting only.

Next: [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy/index|security headers and the same-origin policy]]. HSTS was one security header; the next lesson covers the rest, and the browser rules they switch on.

## Related
<!-- bite: 1cdd9ff7-b8ba-4fe2-8ff7-9fc288bbe02f -->

- [[networking/12-tls-and-transport-security/index|TLS and transport security]] — the handshake, key exchange and the maths, in depth.
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|Digital signatures and PKI]] — how CAs sign certificates, one level deeper.
- [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|Scanning and enumeration]] — nmap, which you used here for its TLS scripts.

## About this lesson
<!-- bite: 9c3edcb8-878c-4e69-872e-4e40b6258396 -->

**Level:** Intermediate. **Covers:** TLS's three guarantees and their limits, certificates, CAs and the chain of trust, Let's Encrypt and automatic renewal, old protocol versions, SSL stripping, HSTS and its preload trap, mixed content, checking TLS with openssl, nmap and testssl.sh, and watching expiry and Certificate Transparency logs. **Where it sits:** lesson 3 of the [[cybersecurity/04-web-security/index|Web Security]] section; the operational side of what the networking TLS lesson explains. **Sources:** the original vault note, rebuilt around the lab VPS. `[reference]` — commands not yet run live; tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
