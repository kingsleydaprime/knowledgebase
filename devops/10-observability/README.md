# 10 — Observability

You cannot operate what you cannot see. Observability is how you know whether a system is healthy, and how you diagnose it when it isn't — through metrics, logs, and traces. Part of the [[devops/README|DevOps curriculum]].

Partly grounded: the [[languages/01-java/03-tooling/05-logging-and-observability|Java logging note]] already covers SLF4J/Logback and a Micrometer→Prometheus path from a real pipeline; this section is the infrastructure-side, tool-and-concept view. The specific stacks are otherwise `[reference]`.

## Reading order

1. [[devops/10-observability/01-observability-fundamentals|Observability Fundamentals]] — **[Advanced]** — the three pillars (metrics, logs, traces), monitoring vs observability, SLIs/SLOs/SLAs and error budgets, alerting, and the four golden signals
2. [[devops/10-observability/02-the-observability-stack|The Observability Stack]] — **[Advanced]** — Prometheus + Grafana (metrics), the ELK stack / Loki / Graylog (logs), OpenTelemetry + Jaeger (tracing), and the APM landscape (Datadog, New Relic, Dynatrace)

## Related
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability (Java)]] — the application-side view, grounded in a real pipeline
- [[devops/05-orchestration/README|Orchestration]] — Prometheus is the de-facto k8s monitoring stack
- [[devops/README|DevOps curriculum map]]
