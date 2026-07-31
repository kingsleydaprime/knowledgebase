# Microservices Patterns

**[reference]** — from the roadmap.sh system-design roadmap. The infrastructure patterns that make a [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|microservices]] architecture actually workable — the machinery you inherit the moment you split a system across the network.

## The problem: coordination at a distance

Split one app into dozens of services and you create new problems the monolith never had: *how do services find each other? how do clients avoid knowing the internal topology? how do cross-cutting concerns get handled without duplicating them in every service?* These patterns answer those.

## Service Discovery

Services scale up/down and move (new instances, failures, [[devops/05-orchestration/01-kubernetes|k8s]] reschedules), so their addresses aren't fixed. **Service discovery** lets a service find the current healthy instances of another by *name* rather than a hardcoded IP:

- **Server-side** — the caller hits a [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancer]] that knows the instances (k8s Services work this way).
- **Client-side** — the caller queries a **service registry** (Consul, etcd, Eureka) and picks an instance itself.

The registry is kept current by health checks. This is what makes "call the payment service" resolve to a live instance despite constant churn — and it relies on [[architecture/04-distributed-systems/README|distributed-systems]] machinery underneath.

## API Gateway

The single entry point for external clients (from [[architecture/02-building-blocks/01-load-balancing-and-proxies|load balancing]]): it routes to the right service and centralizes cross-cutting concerns — authentication, rate limiting, TLS, logging — so each service doesn't reimplement them. Two related patterns:

- **Gateway aggregation** — combine multiple service calls into one client response (so the client makes one request, not six).
- **Gateway offloading** — move shared functionality (auth, SSL) into the gateway.

Keep the gateway *thin* (routing + cross-cutting only) — business logic in the gateway recreates a monolith and a bottleneck.

## Backends for Frontends (BFF)

Instead of one API serving all clients, give each client type (web, mobile, third-party) its *own* gateway/backend tailored to its needs — the mobile BFF returns lean payloads, the web BFF returns richer ones. Avoids the compromise of a one-size-fits-all API (the over/under-fetching problem [[architecture/02-building-blocks/05-communication|GraphQL]] also addresses). Relevant to your [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|full-stack]] work where one product has web + mobile clients (Arete).

## Sidecar & Ambassador

Deploy a helper *alongside* each service (in the same [[devops/05-orchestration/01-kubernetes|pod]]) to handle infrastructure concerns, so the service code stays focused on business logic:

- **Sidecar** — a companion container adding capabilities (logging, config, TLS, metrics) without changing the service. The basis of a [[devops/11-delivery-and-advanced/03-service-mesh|service mesh]] (an Envoy sidecar per service handling all networking — mTLS, retries, observability — transparently).
- **Ambassador** — a sidecar specifically for *outbound* calls (proxying/managing connections to external services).

## Leader Election

When multiple instances of a service run for availability but only *one* should perform a task at a time (a scheduled job, a coordinator), they must agree on a **leader** — and re-elect if it dies. This is a [[architecture/04-distributed-systems/04-consensus|consensus]] problem, and you almost never implement it by hand: you lean on a coordination service (etcd, ZooKeeper, or the platform) that provides it. It's the bridge where microservices patterns meet distributed-systems theory.

## Cross-cutting: observability

The pattern that makes microservices *operable*: because a request now spans many services, you *need* distributed [[devops/10-observability/README|tracing]] (a request/trace ID threaded through every hop), centralized logging, and per-service health endpoints — or debugging becomes impossible. This isn't optional the way it is in a monolith; it's the price of admission.

## The honest summary

These patterns are powerful, but note what they represent: **a whole platform of complexity that a monolith gets for free** (in-process calls need no discovery, one process needs no gateway, one app needs no distributed tracing). That's the real cost of microservices ([[architecture/03-architectural-patterns/01-monolith-microservices-serverless|when to adopt them]]) — you're signing up to build and run all of this. Managed platforms ([[devops/05-orchestration/README|Kubernetes]], [[devops/11-delivery-and-advanced/03-service-mesh|service meshes]]) provide much of it, which is exactly why they exist.

## Related
- [[architecture/03-architectural-patterns/01-monolith-microservices-serverless|Monolith / Microservices / Serverless]] — whether to take this on at all
- [[devops/05-orchestration/README|Orchestration (devops)]] — the platform that provides these
- [[architecture/04-distributed-systems/04-consensus|Consensus]] — the theory under service discovery & leader election
