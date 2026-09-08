# DNS in Depth

**[Intermediate]** — the internet's naming system, and the single most common root cause of "the site is down." Worth real study for one reason: **DNS is a globally distributed, eventually-consistent, aggressively cached database that everything depends on and almost nobody monitors.**

## The kid version first

You know your friend's *name* but not their *house number*. So you ask someone.

- You ask the local shopkeeper (your **resolver**). They've probably been asked before and remember (**cache**).
- If not, they ask the town hall: "who knows about Nigeria?" → "ask that office over there."
- That office: "who knows about `example.com`?" → "ask *their* office."
- That office finally: "it's at 93.184.216.34."

Each office only knows **who to ask next**, not the answer — exactly like [[foundations/networking/04-routing|routing]]. And everyone writes the answer down for a while so they don't have to ask again. That "writes it down for a while" is the source of nearly every DNS problem you'll ever have.

## The resolution walk

```
browser → stub resolver (OS) → recursive resolver (ISP / 8.8.8.8 / 1.1.1.1)
                                    │
                                    ├─► root server (.)          "ask the .com servers"
                                    ├─► TLD server (.com)        "ask ns1.example.com"
                                    └─► authoritative server     "93.184.216.34"  ← the real answer
                                    
                                 caches it for TTL seconds, returns to you
```

Two words to keep straight, because interviewers love this one:

- **Recursive** — "go find the answer for me, I'll wait." What your machine asks its resolver.
- **Iterative** — "tell me what you know, I'll follow up." What the resolver does to each server in the chain. Root and TLD servers only answer iteratively — if they did recursion for everyone, they'd melt.

**Root servers** are the 13 *named* root servers (`a.root-servers.net` … `m.root-servers.net`) — a limit set by what fit in a 512-byte UDP packet, not by machine count. There are actually well over 1,000 physical instances, reachable because each name is announced by **[[foundations/networking/04-routing|anycast]]** from many locations. Your query goes to the topologically nearest one.

## Record types worth knowing

| Record | Maps | Notes |
|---|---|---|
| **A / AAAA** | name → IPv4 / IPv6 | the basic lookup |
| **CNAME** | name → another name | **cannot coexist with other records at the same name** — which is why you can't `CNAME` a bare apex domain (`example.com` must have SOA/NS records). Hence `ALIAS`/`ANAME`/"CNAME flattening" as provider-specific workarounds |
| **NS** | zone → its authoritative servers | delegation — how the hierarchy is built |
| **MX** | domain → mail servers | with priority values |
| **TXT** | arbitrary text | SPF, DKIM, DMARC, and domain-ownership verification |
| **SRV** | service → host+port | service discovery; how [[devops/05-orchestration/README\|Kubernetes]] DNS exposes ports |
| **PTR** | IP → name | reverse lookups; mail servers check these |
| **CAA** | domain → which CAs may issue certs | a real, cheap security control — set it |
| **SOA** | zone metadata | serial, refresh, and the **negative-caching TTL** |

## TTL and caching — where the pain lives

Every record carries a **TTL**. Resolvers cache for that long and will not re-ask, no matter what you do on your end. **You cannot revoke a DNS answer.** Once it's out, it's out until the TTL expires.

The operational discipline that follows:

- **Lower the TTL *before* a migration, not during.** If your TTL is 86400 and you're moving servers next week, drop it to 60 a day or two ahead (long enough for the *old* TTL to expire everywhere), migrate, then raise it back. Doing this in the wrong order is how "we changed DNS and half the traffic still went to the dead server for a day" happens.
- **Negative caching is real.** A `NXDOMAIN` is cached too, governed by the SOA's minimum field. Create a record *after* someone has looked it up and failed, and they'll keep failing for a while. This is a classic cause of "it works for me but not for my colleague" right after setting something up.
- **Nothing respects TTLs perfectly.** Browsers cache separately from the OS, which caches separately from the resolver. Some resolvers clamp TTLs to their own minimums. Plan for "roughly," never "exactly."

## Transport reality: it's UDP first

DNS uses **UDP port 53**, falling back to TCP when the response exceeds the size limit (512 bytes classically; **EDNS0** negotiates up to ~4096). Truncated responses set the `TC` bit, telling the client to retry over TCP.

Two consequences: **zone transfers** (`AXFR`) always use TCP, and firewalls that block TCP/53 "because DNS is UDP" break DNSSEC and large responses in ways that are maddening to diagnose. Also, the amplification property — small query, big answer, no handshake to prevent source spoofing — makes open resolvers a favourite [[cybersecurity/06-attacks-and-threats/README|DDoS amplifier]].

## Security: the parts that matter

DNS was designed in 1983 with **no authentication whatsoever**. A resolver believes whatever answer arrives with a matching query ID and port.

- **Cache poisoning** — race the real answer with a forged one. The **Kaminsky attack** (2008) made this dramatically practical, and the emergency mitigation was **source-port randomisation** (adding ~16 bits of entropy an attacker must guess). That's a mitigation, not a fix.
- **DNSSEC** is the real fix: cryptographically sign records, with a chain of trust from the root down. It authenticates *origin and integrity* — it does **not** encrypt anything. Adoption remains partial, largely because it's operationally unforgiving (a botched key rollover takes your domain off the internet entirely).
- **DoH / DoT** (DNS over HTTPS / over TLS) solve the *other* half: privacy from the network. Your ISP can no longer see or tamper with your lookups. They do not authenticate the answer — a lying resolver still lies, now privately. DoH is also contentious because it moves resolution from your ISP to a handful of large providers, and it bypasses network-based filtering that enterprises and parental controls relied on.

**These are orthogonal:** DNSSEC = "is this answer genuine?", DoH/DoT = "who can see me asking?" You want both, and confusing them is a common interview stumble.

## Why DNS causes so many outages

Because it's a dependency of *everything*, is cached invisibly, and fails in ways that don't look like DNS failures:

- **It's the first thing in the request path** — a slow resolver adds latency to every single connection to a new host, including your service's outbound calls to databases and APIs.
- **Load balancing via DNS is coarse.** Round-robin A records are cached at every layer, so traffic distribution is uneven and removing a failed host takes a full TTL. Fine for coarse geo-steering, bad for failover — which is why real load balancing happens at [[architecture/02-building-blocks/01-load-balancing-and-proxies|L4/L7]], with DNS only pointing at the load balancer.
- **Container/Kubernetes DNS is a notorious latency source.** `ndots:5` in the default `/etc/resolv.conf` means a lookup for `api.example.com` (3 dots, fewer than 5) is first tried with each search domain appended — several failed queries before the real one. Combined with a conntrack race in older kernels, this produced the famous intermittent 5-second DNS timeouts in Kubernetes. The fix is `ndots:2`, fully-qualified names with a trailing dot, or NodeLocal DNSCache.
- **It's a single point of failure you don't own.** The 2016 Dyn DDoS took down Twitter, GitHub, Netflix, and Reddit simultaneously — none of which were themselves attacked. Use two DNS providers if uptime genuinely matters.

## Key insight

DNS is the internet's most successful distributed system, and it achieves that by making a trade nobody would accept today: **it gives up consistency almost entirely in exchange for availability and cacheability.** Every DNS problem — stale records after a migration, negative-cache confusion, slow failover, split-brain between resolvers — is that trade presenting its bill. Think of DNS as an eventually-consistent cache with a TTL-shaped staleness bound, not as a database, and its behaviour becomes predictable.

## Related
- [[foundations/networking/04-routing|Routing]] — anycast, which DNS depends on
- [[foundations/networking/15-network-performance|Network Performance]] — DNS as the first round trip
- [[cybersecurity/03-network-security/README|Network Security]] — poisoning, DNSSEC, exfiltration over DNS
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking & Protocols (devops)]] — the operator's DNS record cheat-sheet
