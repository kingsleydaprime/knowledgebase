# Observability Fundamentals

**[reference]**, with a grounded companion: the [[languages/01-java/03-tooling/05-logging-and-observability|Java logging & observability note]] covers the application-side (SLF4J/Logback, Micrometer→Prometheus metrics, the four pipeline signals) from a real project. This note is the concepts/infrastructure view.

## Monitoring vs observability

**Monitoring** answers *known* questions: "is CPU above 80%? is the site up?" — predefined dashboards and alerts for failure modes you anticipated. **Observability** is the property of being able to answer *new* questions about a system's internal state from its outputs, without shipping new code — especially the "why is this specific request slow?" questions you didn't predict. Monitoring tells you *something* is wrong; observability helps you find out *what*.

## The three pillars

| Pillar | Answers | Tool examples |
|---|---|---|
| **Metrics** | "how much / how many / how fast" — aggregatable numbers over time | Prometheus, Grafana |
| **Logs** | "what exactly happened" — discrete, timestamped event records | ELK, Loki, Splunk |
| **Traces** | "where did the time go" — one request's path across services | OpenTelemetry, Jaeger |

- **Metrics** are cheap, aggregatable numbers sampled over time (request rate, error rate, latency percentiles, queue depth). Great for dashboards and alerting; they tell you the shape of a problem but not the specifics.
- **Logs** are the detailed event record — the raw material for debugging *what* happened to a specific request. **Structured logging** (JSON, not free text) is what makes logs queryable at scale (see the [[languages/01-java/03-tooling/05-logging-and-observability|log-table pattern]]).
- **Traces** follow a single request as it hops across services (via a propagated **trace ID**), showing how long each hop took. Indispensable in microservices, where "the API is slow" could be any of ten downstream calls — a trace shows exactly which.

The pillars are complementary: a metric alerts you that error rate spiked, a trace localizes it to one service, and that service's logs tell you the exact failure. **Correlation** (a shared request/trace ID threading metrics↔logs↔traces) is what turns three data sources into one debugging workflow.

## The four golden signals

Google's SRE book distills "what to monitor" for any user-facing service into four signals — a far better starting point than a hundred host metrics:

1. **Latency** — how long requests take (track *distributions*/percentiles, not averages — a p99 of 2s hides behind a 50ms average).
2. **Traffic** — how much demand (requests/sec).
3. **Errors** — the rate of failing requests.
4. **Saturation** — how full the system is (CPU, memory, queue depth) — how close to a limit.

(The related **RED** method — Rate, Errors, Duration — is the request-centric subset most people start with.)

## SLI, SLO, SLA, and error budgets

The vocabulary for defining and committing to reliability:

- **SLI** (Indicator) — a measured signal, e.g. "% of requests served in under 300ms."
- **SLO** (Objective) — your internal target for an SLI, e.g. "99.9% of requests under 300ms over 30 days." This is the number you actually engineer to.
- **SLA** (Agreement) — a *contractual* promise to customers, with consequences (refunds) if missed. Usually looser than the SLO, so you have margin.
- **Error budget** — the inverse of the SLO: 99.9% availability means a 0.1% budget to "spend" on failures/risky deploys. Budget left → ship features faster; budget exhausted → freeze and stabilize. It turns reliability into a quantified tradeoff instead of "make it never break."

## Alerting done right

Alerts should be **actionable and symptom-based** — page a human for *user-facing symptoms* ("error rate SLO burning"), not for every internal cause ("CPU 81%"). Alert fatigue (too many noisy, non-actionable pages) is a real failure mode that gets real incidents ignored. Good practice: page on SLO burn rate, route lower-severity issues to a dashboard/ticket, and make every page carry a runbook.

## Related
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability (Java)]] — the application-side, grounded in a real pipeline
- [[devops/10-observability/02-the-observability-stack|The Observability Stack]] — the tools that implement these pillars
- [[devops/05-orchestration/README|Orchestration]] — what you're most often observing
