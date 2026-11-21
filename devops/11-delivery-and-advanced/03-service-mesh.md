---
id: 640454ae-285c-4f15-9d8a-c1b4904772bd
---

# Service Mesh

**[reference]** — from roadmap.sh and the Istio/Linkerd docs. The most advanced networking topic in the domain, and one you should reach for only when the scale justifies it.

## The problem
<!-- bite: 79daa2ac-c850-4ea6-ae3c-3db7b6d3a33b -->

In a microservices system running on [[devops/10-orchestration/01-kubernetes|Kubernetes]], dozens of services call each other over the network. Each of those service-to-service calls needs the same cross-cutting concerns: retries and timeouts, load balancing, mutual TLS (encryption + identity between services), traffic routing (canary, A/B), and observability (metrics/traces for every hop). Building all of that into every service — in every language — is repetitive, inconsistent, and couples business code to networking plumbing.

## The idea: move it into the platform
<!-- bite: 8ba798e6-0e2f-4cb1-97b3-ded507f46795 -->

A **service mesh** extracts that networking logic out of the application and into the infrastructure. It does this with the **sidecar** pattern: a proxy (usually [[devops/02-networking-and-web/02-web-servers-and-proxies|Envoy]]) is injected next to every service instance, and *all* traffic in and out of the service flows through its sidecar. The sidecars form the **data plane**; a **control plane** configures them centrally.

```
Service A ──► [sidecar proxy] ══mTLS══► [sidecar proxy] ──► Service B
                    ▲                          ▲
                    └────── control plane configures both ──────┘
                    (routing rules, mTLS certs, telemetry collection)
```

Because every call passes through a sidecar, the mesh can transparently add — with zero application code changes:

- **mTLS everywhere** — automatic mutual-TLS between services (encryption + cryptographic identity), the backbone of zero-trust networking.
- **Traffic management** — canary rollouts, weighted routing, retries, timeouts, circuit breaking ([[devops/11-delivery-and-advanced/04-cloud-design-patterns|resilience patterns]]) configured declaratively.
- **Observability** — uniform metrics, logs, and [[devops/07-observability/index|traces]] for every service-to-service call, for free.

## The tools
<!-- bite: 9ef5855a-67b7-46ed-ada1-2bdfea204e0d -->

| Mesh | Note |
|---|---|
| **Istio** | the most powerful and feature-rich; Envoy-based; also the most complex to run |
| **Linkerd** | CNCF, deliberately lightweight and simple, its own fast Rust proxy; "the mesh you can actually operate" |
| **Consul (Connect)** | HashiCorp's mesh, strong outside pure-k8s and multi-datacenter |
| **Cilium (eBPF)** | does mesh-like functions in the kernel via eBPF, potentially without sidecars |

## The honest caveat
<!-- bite: 64262926-df66-4104-9783-75a489a8a236 -->

A service mesh is powerful but adds **real complexity and overhead** — a proxy beside every pod means more moving parts, more resource use, and more to debug (now a request failing could be the app *or* its sidecar). It's genuinely valuable at large microservice scale where uniform mTLS, traffic control, and observability across many services are hard problems. It is **overkill** for a handful of services — the classic mistake is adopting Istio before you have the scale that justifies it. Reach for a mesh when the cross-service networking concerns above become a real, repeated pain, not by default — the same "do you actually need this?" judgment as adopting [[devops/10-orchestration/01-kubernetes|Kubernetes]] itself.

## Related
<!-- bite: a4fbd687-1d98-4747-b5b5-8e915a73eac0 -->
- [[devops/10-orchestration/01-kubernetes|Kubernetes]] — what a service mesh runs on top of
- [[devops/02-networking-and-web/02-web-servers-and-proxies|Web Servers & Proxies]] — Envoy, the proxy under most meshes
- [[devops/07-observability/index|Observability]] — a mesh provides uniform telemetry
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns]] — the resilience patterns a mesh implements
