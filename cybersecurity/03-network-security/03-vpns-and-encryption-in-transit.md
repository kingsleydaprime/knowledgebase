# VPNs & Encryption in Transit

Data moving across a network can be read (or altered) by anyone positioned along its path unless it's encrypted — encryption in transit is what protects data *while it moves*, as distinct from encryption at rest (data sitting on disk) or the document-level encryption covered in [[10-pdf-and-document-security|pdf-and-document-security]].

## What a VPN actually does

A VPN (Virtual Private Network) creates an encrypted tunnel between two points over an otherwise untrusted network (commonly the public internet), so traffic inside the tunnel is protected from anyone observing the underlying network path. Two common use shapes:

- **Site-to-site VPN** — connects two networks (e.g. a company's two office locations) so they behave as one logical network over the internet.
- **Remote-access VPN** — connects an individual device to a private network remotely (an employee working from home reaching internal company systems as if physically on-site).

## Common VPN protocols

- **IPsec** — operates at the network layer, widely used for site-to-site VPNs and supported natively by most routers/firewalls; configuration is more complex but very mature and standardized.
- **OpenVPN** — an SSL/TLS-based VPN, widely used for remote-access VPNs, runs over standard TCP/UDP ports (easy to route through most networks/firewalls) and is open-source and well audited.
- **WireGuard** — a newer protocol, deliberately much simpler (a fraction of the codebase size of IPsec/OpenVPN), which is itself a security advantage — less code means a smaller attack surface and an easier codebase to audit thoroughly. Increasingly the default choice for new deployments.

```bash
# illustrative WireGuard config shape — not a working example on its own,
# real keys/endpoints are generated per deployment
[Interface]
PrivateKey = <this device's private key>
Address = 10.0.0.2/24

[Peer]
PublicKey = <server's public key>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
```

## TLS — the encryption underneath most everyday "secure" traffic

Separately from dedicated VPNs, **TLS** (Transport Layer Security) is what encrypts individual connections directly — HTTPS is HTTP running over TLS. Covered in depth in [[03-https-and-tls|https-and-tls]] since it's specifically central to web security, but the core idea (encrypt the channel so eavesdroppers along the path see only ciphertext) is the same principle a VPN applies more broadly to all traffic between two points, not just one application's traffic.

## Why "the traffic is encrypted" doesn't mean "the connection is fully trustworthy"

Encryption in transit protects **confidentiality and integrity of the data on the wire** — it stops eavesdropping and tampering *in transit*. It says nothing about whether the endpoint you're connected to is who it claims to be (that's what certificate validation in TLS handles, see [[03-https-and-tls|https-and-tls]]), and nothing about what happens to the data once it arrives and is decrypted at the other end. A VPN to a malicious or compromised VPN provider still fully exposes your traffic *to that provider* — encryption in transit protects against a passive network observer, not against the endpoint itself.

## Gotchas

- A "free VPN" service has to make money somehow — if you're not paying for the product, the provider's own visibility into (and potential monetization of) your traffic is a real, common consideration, not a paranoid one.
- VPN split-tunneling (routing only some traffic through the VPN, the rest directly) trades some protection for performance/convenience — worth being deliberate about which traffic actually needs the VPN's protection rather than assuming full-tunnel is always required or split-tunnel is always safe.
- Encryption in transit is one layer, not a complete security posture — data still needs protecting at rest and the endpoints themselves still need to be secured; a VPN doesn't make a poorly secured endpoint safe.

## Related
- [[01-firewalls|firewalls]]
- [[03-https-and-tls|https-and-tls]]
- [[02-network-segmentation|network-segmentation]]
