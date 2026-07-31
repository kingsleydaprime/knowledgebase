# Network Attacks

**[reference]** — from the roadmap.sh cyber-security roadmap. Educational/defensive: how network-layer attacks work so you can detect and prevent them. The offensive counterpart to [[cybersecurity/03-network-security/README|network security]], and it assumes the networking basics also covered in [[devops/08-networking-and-web/01-networking-and-protocols|DevOps networking & protocols]].

## Man-in-the-Middle (MITM)

The attacker secretly sits between two parties, relaying (and possibly altering) their traffic while both think they're talking directly. It's the umbrella for many attacks below. The defense is **encryption in transit** ([[cybersecurity/04-web-security/03-https-and-tls|TLS]]) — MITM can still intercept, but can't read or tamper without breaking the crypto or tricking the victim into trusting a bad certificate.

## Attacks on the local network

These exploit trusting, unauthenticated LAN protocols:

- **ARP poisoning/spoofing** — ARP (which maps IPs to MAC addresses) has no authentication, so an attacker floods forged ARP replies to make victims send *their* traffic to the attacker's machine — the classic way to establish a LAN MITM. Defense: dynamic ARP inspection, static ARP for critical hosts, network segmentation.
- **DNS poisoning/spoofing** — forging DNS responses so a legitimate domain resolves to an attacker's IP (feeding [[cybersecurity/06-attacks-and-threats/01-social-engineering|pharming]]). Defense: **DNSSEC**, trusted resolvers, DNS-over-HTTPS/TLS.
- **DHCP spoofing / rogue DHCP** — a rogue DHCP server hands victims a malicious default gateway/DNS, routing them through the attacker. Defense: DHCP snooping.
- **MAC flooding** — overwhelming a switch's MAC table so it fails open and broadcasts all traffic (letting the attacker sniff it). Defense: port security.

## Denial of Service

- **DoS** — overwhelming a service so legitimate users can't reach it (flood of requests, or a crafted packet that crashes it).
- **DDoS** — the same from many compromised machines (a **botnet**) at once — far harder to block since traffic comes from everywhere. Defense: upstream scrubbing/CDN (Cloudflare), rate limiting, over-provisioning; the [[cybersecurity/07-security-operations/README|SOC]] watches for the traffic spike.

## Wi-Fi attacks

Wireless adds physical-proximity attacks (see the existing [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi security testing]] note for the authorized-testing view):

- **Evil twin / rogue AP** — a fake access point mimicking a legitimate SSID; victims connect and route traffic through the attacker.
- **Deauthentication attack** — forging deauth frames to kick clients off a network (to force a reconnect to an evil twin, or capture the handshake for offline cracking).
- **WPS attacks / weak WPA** — exploiting weak Wi-Fi setup/crypto ([[cybersecurity/05-cryptography/README|WEP is broken; WPA2/WPA3]] are the standard).

## Other

- **Spoofing** (general) — forging a source identity: IP spoofing (fake source IP), email spoofing, caller-ID spoofing.
- **Replay attack** — capturing valid data (an auth token, a transaction) and re-sending it to impersonate the sender. Defense: nonces, timestamps, session tokens that expire.
- **Session hijacking** — stealing a valid session token (via [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|XSS]], sniffing, or fixation) to take over an authenticated session. Defense: TLS everywhere, `HttpOnly`/`Secure` cookies, rotating tokens.
- **Port scanning** — reconnaissance mapping open ports/services (nmap); not an attack itself but the precursor to one ([[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning & enumeration]]).

## The through-line

Most of these exploit **protocols that trust by default** (ARP, DNS, DHCP have no built-in authentication) or **unencrypted traffic**. The two structural defenses recur everywhere: **encrypt in transit** (TLS, IPsec, VPN — [[cybersecurity/03-network-security/03-vpns-and-encryption-in-transit|encryption in transit]]) so interception is useless, and **segment + authenticate** ([[cybersecurity/03-network-security/02-network-segmentation|segmentation]], zero-trust) so a foothold on one segment doesn't reach everything.

## Related
- [[cybersecurity/03-network-security/README|Network Security]] — the defenses against these
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking & Protocols (DevOps)]] — the protocol fundamentals these abuse
- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging & Detection]] — catching these in network telemetry
