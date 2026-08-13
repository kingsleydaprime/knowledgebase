# 08 — Networking & Web Servers

The network layer a DevOps engineer must actually understand: the protocols underneath everything (DNS, HTTP/S, TLS, SSH, the OSI model), and the web-serving infrastructure that sits in front of applications (Nginx, reverse proxies, load balancers, caching). Part of the [[devops/README|DevOps curriculum]].

This section overlaps the `foundations/networking/` domain (currently empty) — this is the *operational* cut (running and debugging network services), not the CS-theory cut. If that domain gets built out later, the OSI/TCP theory belongs there and this section should cross-link to it.

## Reading order

1. [[devops/08-networking-and-web/01-networking-and-protocols|Networking & Protocols]] — **[Intermediate]** — the OSI model, TCP/UDP, DNS, HTTP/HTTPS, SSL/TLS, SSH, ports, and the email protocols (SMTP/IMAP/POP3, SPF/DKIM/DMARC)
2. [[devops/08-networking-and-web/02-web-servers-and-proxies|Web Servers & Proxies]] — **[Intermediate]** — Nginx in depth, Apache/Caddy, forward vs reverse proxy, load balancing, and caching servers
3. [[devops/08-networking-and-web/03-local-https-tunnels|Local HTTPS Tunnels]] — **[Intermediate]** — exposing localhost over public HTTPS for OAuth callbacks and webhooks; cloudflared vs ngrok, named vs quick tunnels

## Related
- [[devops/01-linux/13-network-fundamentals|Linux networking fundamentals]] — the host-level view
- [[devops/01-linux/14-basic-ssh-config|SSH config]] — SSH in practice
- [[devops/09-secret-management/README|Secret Management]] — TLS certificates are secrets
- [[devops/README|DevOps curriculum map]]
