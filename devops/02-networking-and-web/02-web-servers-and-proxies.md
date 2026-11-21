---
id: 1291ce41-a7bc-4a4b-bbb8-5631985413c5
---

# Web Servers & Proxies

## What a web server does
<!-- bite: 32e10085-05cb-49d4-ac30-ffee00de9afb -->

A web server accepts HTTP(S) requests and either serves static files or hands the request to an application. In almost every real deployment it does far more than "serve files" — it **terminates TLS**, **reverse-proxies** to app processes, **load-balances**, and **caches**. Understanding those four jobs is the point of this note.

## Forward proxy vs reverse proxy
<!-- bite: b4746eae-1826-4daa-b45a-ac00ae7be519 -->

The distinction trips people up; it's about *which side* the proxy represents:

- **Forward proxy** — sits in front of *clients*, making requests on their behalf (corporate egress proxy, a VPN-ish gateway). The server doesn't know the real client.
- **Reverse proxy** — sits in front of *servers*, receiving client requests and forwarding them to backends. The client doesn't know which backend served it. **This is the DevOps workhorse** — Nginx in front of your app is a reverse proxy.

```
Client ──► [ reverse proxy: Nginx ] ──► app instance 1
                     │               ──► app instance 2   (load balancing)
                     └─ terminates TLS, caches, routes by path/host
```

A reverse proxy is where you put concerns that shouldn't live in the app: TLS termination, load balancing, caching, compression, rate limiting, and path/host-based routing to different backends.

## Nginx
<!-- bite: 8e08f251-1076-4cbc-b130-c0e23faf95ff -->

The dominant reverse proxy / web server. A minimal but realistic config showing the core jobs:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;   # TLS termination
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    location /static/ {
        root /var/www;                    # serve static files directly
        expires 30d;                      # cache headers
    }

    location / {
        proxy_pass http://app_backend;    # reverse-proxy everything else to the app
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

upstream app_backend {                    # load balance across app instances
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
}
```

That one file terminates TLS, serves static assets with caching, load-balances across two app instances, and reverse-proxies dynamic requests — the four jobs at once.

## Load balancing
<!-- bite: 0f565e81-8c25-4613-8fb7-2158de27587d -->

Spreading traffic across multiple backends for **scale** (more instances = more capacity) and **availability** (one instance dies, traffic routes to the survivors). Key ideas:

- **Algorithms** — round-robin (default), least-connections, IP-hash (sticky sessions by client).
- **Health checks** — the LB stops sending traffic to a backend that fails its health check (the same idea as k8s [[devops/10-orchestration/01-kubernetes|readiness probes]]).
- **L4 vs L7** — an L4 (transport) load balancer routes by IP/port and is fast/dumb; an L7 (application) load balancer reads HTTP and can route by path/host/header, do TLS termination, etc. Nginx is L7; cloud LBs come in both flavors.

In the cloud you often use a managed load balancer (AWS ALB/NLB, GCP LB) instead of running Nginx yourself; in Kubernetes, a Service (`LoadBalancer` type) or Ingress controller plays this role.

## Caching servers
<!-- bite: 1fad5d0e-e2bc-4b6c-934d-3b643ce1bbaa -->

Caching stores responses so repeat requests skip the expensive backend work:

- **Reverse-proxy cache** — Nginx/Varnish caching HTTP responses at the edge of your infra.
- **CDN** (Cloudflare, CloudFront) — caches static assets in edge locations near users, cutting latency and offloading origin traffic. The first reach-for scaling lever for a read-heavy site.
- **Application cache** — Redis/Memcached in front of a database (the cache-aside pattern in [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns]]).

Caching is one of the highest-leverage performance tools and one of the hardest to get right — invalidation (knowing when a cached copy is stale) is the perennial problem.

## The landscape
<!-- bite: b9033295-2a55-4df0-9f3a-673314822090 -->

| Server | Niche |
|---|---|
| **Nginx** | the default reverse proxy / load balancer; fast, event-driven |
| **Apache (httpd)** | older, module-rich, `.htaccess` per-dir config; still huge in traditional hosting |
| **Caddy** | modern, **automatic HTTPS** (fetches + renews Let's Encrypt certs itself) — least-config option |
| **HAProxy** | a dedicated high-performance load balancer (L4/L7), not a general web server |
| **Traefik** | cloud-native reverse proxy with automatic service discovery — popular as a k8s ingress controller |
| **Envoy** | the high-performance proxy underneath most [[devops/11-delivery-and-advanced/03-service-mesh\|service meshes]] |

## Related
<!-- bite: fe5b7e3f-0fac-4841-bd86-500fab1d613a -->
- [[devops/02-networking-and-web/01-networking-and-protocols|Networking & Protocols]] — the HTTP/TLS these servers speak
- [[devops/04-vps/vps-setup|VPS Setup]] — a web server fronting a real deploy
- [[devops/10-orchestration/01-kubernetes|Kubernetes]] — Services/Ingress play the LB/proxy role in a cluster

## About this lesson
<!-- bite: d3ef7047-e2d1-41de-b830-339f091bb015 -->

**[reference]**, with grounding in the [[devops/04-vps/vps-setup|VPS setup]] where a web server fronts a deployed app.
