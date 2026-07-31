# Load Balancing & Proxies

**[reference]** — from the roadmap.sh system-design roadmap. The traffic-routing layer that makes [[architecture/01-system-design-fundamentals/02-scalability-and-performance|horizontal scaling]] possible. Overlaps the ops view in [[devops/08-networking-and-web/02-web-servers-and-proxies|DevOps web servers & proxies]] — this is the system-design lens.

## Load balancers — the front door to horizontal scale

A **load balancer** distributes incoming requests across multiple backend servers, which is what lets you scale out (add servers) and stay available (route around dead ones). It's the single most important building block for scale — without it, "more servers" doesn't help because clients don't know they exist.

Its jobs:
- **Distribute load** across healthy backends.
- **Health checks** — stop routing to a backend that fails its check (the [[architecture/01-system-design-fundamentals/03-availability-and-reliability|failover]] mechanism).
- **Enable statelessness** — because any server can handle any request, servers hold no local state (the enabler of horizontal scaling).

### L4 vs L7

The key distinction:

- **Layer 4 (transport)** — routes by IP/port without reading the request content. Fast, simple, protocol-agnostic. Can't make content-based decisions.
- **Layer 7 (application)** — reads the HTTP request, so it can route by path/host/header, terminate TLS, and do smart things (send `/api/*` to one pool, `/images/*` to another). More capable, slightly more overhead. The common choice for web apps.

### Algorithms

How the LB picks a backend:

- **Round-robin** — each server in turn. Simple default.
- **Least connections** — the server with the fewest active connections. Better when request durations vary.
- **Weighted** — bigger servers get proportionally more.
- **IP hash / sticky sessions** — the same client always hits the same server. Needed for local session state — but it *undermines* statelessness and even load distribution, so prefer stateless servers + shared session store instead.

For availability, the LB itself must be redundant (or it's the single point of failure) — usually a pair with failover, or a managed cloud LB.

## Reverse proxy

A **reverse proxy** sits in front of servers, receiving client requests and forwarding them to backends (the client never talks to backends directly). A load balancer *is* a kind of reverse proxy; the term also covers a single proxy fronting one app. It's where you centralize concerns that don't belong in the app: **TLS termination**, caching, compression, rate limiting, request routing. (Contrast a *forward* proxy, which fronts clients — see [[devops/08-networking-and-web/02-web-servers-and-proxies|proxies]].)

## API gateway

For [[architecture/03-architectural-patterns/04-microservices-patterns|microservices]], an **API gateway** is a specialized reverse proxy that's the single entry point for all clients, handling cross-cutting concerns so each service doesn't: authentication, rate limiting, routing to the right service, request **aggregation** (combine several service calls into one response), and protocol translation. It keeps clients from needing to know the internal service topology — but it can become a bottleneck or a monolith-in-disguise if it holds business logic, so keep it thin.

## CDN

A **Content Delivery Network** is geographically-distributed caching for *static* content (images, CSS, JS, video) — servers near the user hold copies, so requests are served from the edge instead of your origin. It cuts latency (the content is physically closer) and offloads huge traffic from your servers. The first reach-for scaling lever for any read-heavy or globally-distributed site.

- **Push CDN** — you upload content to the CDN proactively (good for infrequently-changing assets).
- **Pull CDN** — the CDN fetches from your origin on the first request and caches it (good for large catalogs; the first user pays the latency).

CDNs are a special case of the [[architecture/02-building-blocks/02-caching|caching]] discussed next.

## Related
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance|Scalability & Performance]] — why load balancing enables scale
- [[architecture/02-building-blocks/02-caching|Caching]] — CDN is edge caching
- [[devops/08-networking-and-web/02-web-servers-and-proxies|Web Servers & Proxies (devops)]] — running Nginx/HAProxy in practice
