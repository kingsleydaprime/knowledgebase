# The Observability Stack

**[reference]** — from roadmap.sh and vendor docs. The three-pillar concepts are in [[devops/10-observability/01-observability-fundamentals|the fundamentals note]]; this maps the tools that implement them.

## Metrics: Prometheus + Grafana

The de-facto open-source metrics stack, and the default in the Kubernetes world.

- **Prometheus** — a time-series database that **pulls** (scrapes) metrics from your services' `/metrics` HTTP endpoints on an interval. Services expose metrics in a simple text format (via a client library like [[languages/01-java/03-tooling/05-logging-and-observability|Micrometer]] for Java). Its query language, **PromQL**, computes rates, percentiles, and aggregations:

```promql
# request error rate over 5 minutes
rate(http_requests_total{status=~"5.."}[5m])
```

  The pull model matters: Prometheus discovers targets dynamically (it auto-scrapes k8s pods), so ephemeral, autoscaling infrastructure just works — no agent has to know where to push.
- **Grafana** — the visualization layer: dashboards over Prometheus (and many other sources). It's the "single pane of glass" most teams look at.
- **Alertmanager** — Prometheus's companion: dedupes, groups, and routes alerts (to PagerDuty, Slack) based on PromQL alert rules.

Prometheus is pull-based and great for metrics but not for long-term storage or high-cardinality data at massive scale (where Thanos/Cortex/Mimir or a hosted TSDB extend it).

## Logs: ELK, Loki, and friends

Centralized logging aggregates logs from every service/host into one searchable place — essential once you have more than one machine:

- **ELK / Elastic Stack** — **E**lasticsearch (stores + indexes logs), **L**ogstash (ingests/transforms), **K**ibana (searches/visualizes), with Beats as lightweight shippers. Powerful full-text search; heavy to run.
- **Grafana Loki** — "Prometheus for logs": indexes only labels (not full text), which makes it far cheaper and lighter than Elasticsearch, and it plugs into Grafana alongside metrics. Popular in k8s stacks.
- **Graylog** — an open-source centralized logging alternative.
- The pattern regardless of tool: **structured logs** (JSON) + a shipper (Fluentd/Fluent Bit/Vector) → central store → search UI. Structured logging is what makes this queryable — the [[languages/01-java/03-tooling/05-logging-and-observability|log-table/structured-logging note]] is the app-side of this.

## Traces: OpenTelemetry + Jaeger

- **OpenTelemetry (OTel)** — the vendor-neutral **standard** for instrumenting traces (and increasingly metrics/logs). You instrument once against the OTel API and export to any backend — the important strategic choice, because it avoids lock-in to one vendor's agent. This is the SLF4J-facade idea ([[languages/01-java/03-tooling/05-logging-and-observability|logging]]) applied to all telemetry.
- **Jaeger** (and Tempo, Zipkin) — the trace **backend/UI**: stores traces and renders the per-request waterfall showing where latency went across services.

## APM and hosted platforms

Commercial all-in-one Application Performance Monitoring — metrics, logs, traces, dashboards, and alerting in one product, agent-based and low-setup, at a cost (often usage-priced and expensive at scale):

| Platform | Note |
|---|---|
| **Datadog** | the market-leading all-in-one; broad integrations |
| **New Relic** | APM pioneer, full-stack observability |
| **Dynatrace** | enterprise APM with heavy automation/AI |
| **Grafana Cloud** | hosted Prometheus/Loki/Tempo (the open stack, managed) |
| **Splunk** | log analytics heavyweight, strong in enterprise/security |

The recurring build-vs-buy decision: run the open-source stack yourself (Prometheus/Grafana/Loki/OTel — cheaper at scale, more operational work) versus buy a hosted APM (Datadog et al. — fast to set up, great UX, expensive as you grow). Many start hosted and migrate the highest-volume pillars to self-hosted as the bill climbs.

## How it fits together

```
service (OTel-instrumented)
  ├─ metrics  ─► Prometheus ─► Grafana (dashboards) + Alertmanager (paging)
  ├─ logs     ─► Loki/ELK   ─► Grafana/Kibana (search)
  └─ traces   ─► Jaeger/Tempo ─► trace waterfalls
        all correlated by a shared trace/request ID
```

Instrument once (OTel), route each pillar to its store, correlate by ID, visualize in one place — that's a modern observability stack.

## Related
- [[devops/10-observability/01-observability-fundamentals|Observability Fundamentals]] — the concepts these tools serve
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability (Java)]] — the app-side instrumentation
- [[devops/05-orchestration/01-kubernetes|Kubernetes]] — Prometheus is the default k8s monitoring stack
