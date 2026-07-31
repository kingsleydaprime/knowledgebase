# Networking & Protocols

**[reference]**, with grounding in the Linux networking already covered ([[devops/01-linux/13-network-fundamentals|network fundamentals]], [[devops/01-linux/14-basic-ssh-config|SSH]]). This is the operational protocol knowledge a DevOps engineer debugs with, not a CS networking course.

## The OSI model — a debugging map

The OSI model layers networking so you can reason about *where* a problem is. You rarely need all seven, but the mental model of "which layer is broken?" is the point:

| Layer | Job | You debug here when… |
|---|---|---|
| 7 Application | HTTP, DNS, SSH, SMTP | the app protocol misbehaves (a 500, a bad DNS answer) |
| 4 Transport | TCP, UDP — ports, reliability | a port's closed, a connection won't establish |
| 3 Network | IP, routing | packets don't reach the host, routing/subnet issue |
| 2/1 Link/Physical | MAC, cables, Wi-Fi | hardware/L2 (rare in cloud) |

The practical takeaway: when something's broken, isolate the layer. "Can I resolve the DNS name?" (L7) → "can I reach the IP/port?" (`ping`/`telnet`/`nc`, L3/L4) → "is the app responding?" (L7). Most cloud debugging is DNS, ports/firewalls (L4), or the app (L7).

**TCP vs UDP** (L4): TCP is connection-oriented and reliable (handshake, ordering, retransmission) — HTTP, SSH, databases. UDP is fire-and-forget, no guarantees but low overhead — DNS queries, video, metrics. **Ports** identify a service on a host (80 HTTP, 443 HTTPS, 22 SSH, 53 DNS).

## DNS — the internet's phone book

DNS resolves names (`example.com`) to IPs. It's the source of a huge share of "it's down" incidents, so the record types matter:

| Record | Maps | Use |
|---|---|---|
| **A / AAAA** | name → IPv4 / IPv6 | the basic address lookup |
| **CNAME** | name → another name | aliasing (`www` → the apex) |
| **MX** | domain → mail server | email routing |
| **TXT** | arbitrary text | verification, SPF/DKIM/DMARC (below) |
| **NS** | domain → its nameservers | delegation |

Two operational realities: **TTL** (time-to-live) controls how long a record is cached, so DNS changes aren't instant — lower the TTL *before* a planned change. And DNS propagation delays are why a fresh deploy or cert sometimes "isn't live yet."

## HTTP / HTTPS

**HTTP** is the request/response protocol of the web: a method (`GET`/`POST`/…), a path, headers, and a body; the response carries a **status code** (2xx success, 3xx redirect, 4xx client error, 5xx server error) — reading status codes is first-line debugging. HTTP/2 and HTTP/3 add multiplexing and (in HTTP/3) run over UDP for lower latency, but the semantics are the same.

**HTTPS** is HTTP over **TLS**. The essentials a DevOps engineer must own:

- TLS provides **encryption** (eavesdroppers can't read traffic), **integrity** (it can't be tampered with), and **authentication** (the server is who it claims, via a certificate signed by a trusted CA).
- The **handshake** negotiates keys before any HTTP flows (asymmetric crypto to exchange a symmetric session key — see [[cybersecurity/05-cryptography/README|cryptography]]).
- **Certificates** expire — an expired cert is a classic, embarrassing outage. **Let's Encrypt** + automated renewal (certbot, or a reverse proxy like Caddy that does it automatically) is the standard fix. Certs and their private keys are [[devops/09-secret-management/README|secrets]].

## SSH

Secure Shell — encrypted remote access and the transport for tools like [[devops/07-infrastructure-as-code/02-configuration-management|Ansible]]. Operationally: prefer **key-based auth** over passwords (a keypair; the public key goes in the server's `authorized_keys`), disable root/password login, and use the SSH `config` and agent for convenience — the hands-on details are in [[devops/01-linux/14-basic-ssh-config|Basic SSH Config]].

## Email protocols (the roadmap's mail branch)

Rarely built from scratch, but worth recognizing: **SMTP** sends mail; **IMAP/POP3** retrieve it. The deliverability trio lives in DNS **TXT** records and exists to stop spoofing:

- **SPF** — lists which servers may send mail for your domain.
- **DKIM** — cryptographically signs outgoing mail so the recipient can verify it wasn't forged.
- **DMARC** — ties SPF+DKIM together and tells receivers what to do with mail that fails (quarantine/reject), plus reporting.

If you ever send transactional email from an app and it lands in spam, misconfigured SPF/DKIM/DMARC is almost always why.

## Related
- [[devops/01-linux/13-network-fundamentals|Linux Network Fundamentals]] — the host-level, hands-on view
- [[devops/08-networking-and-web/02-web-servers-and-proxies|Web Servers & Proxies]] — what terminates TLS and routes HTTP
- [[cybersecurity/05-cryptography/README|Cryptography]] — the crypto under TLS
- [[cybersecurity/03-network-security/README|Network Security]] — the security cut of the same protocols
