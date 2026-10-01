# Observability Fundamentals

> **[Beginner→Intermediate]** · How you answer "is it up, is it fast, and what broke?" about a system you can't step through in a debugger: metrics, logs and traces; the four golden signals; why averages lie; and SLOs and error budgets, which turn "reliable" into a number.

**[reference]**, with a grounded companion: the [[languages/01-java/03-tooling/05-logging-and-observability|Java logging & observability note]] covers the application side (SLF4J/Logback, Micrometer → Prometheus metrics, the four pipeline signals) from a real project. This note is the concepts view.

## Before you start

You can already:

- Write structured JSON logs with a request ID → [[backend/07-practices/01-backend-best-practices|backend best practices]] (the other core lesson this week).
- Read a percentage and do arithmetic with it. Nothing more mathematical than that.

After this lesson you will be able to:

1. Say what metrics, logs and traces each answer, and how a request ID connects them.
2. Compute latency percentiles and explain why the average hides the users having the worst time.
3. Define an SLI, SLO and SLA for a real endpoint, and work out its error budget.
4. Decide when an alert should wake a person up, using burn rate.

**Study route.** The kid version and §1–5, then the worked example — predict the numbers first. The practice task is the second half of SWE 101's week 6 milestone.

## The kid version

A car's dashboard doesn't tell you what's wrong with the engine. It tells you a few things that matter right now — speed, fuel, temperature — and lights a warning when one goes wrong. Then a mechanic plugs in and reads the detailed record of what the engine did. **Observability is the dashboard plus the mechanic's record, for software.** The dashboard (metrics) tells you something's wrong; the record (logs and traces) tells you what.

**Where the analogy stops working.** A car has one driver, so "the speed" is one number. A server handles thousands of requests at once, and "how fast is it?" has no single answer — most requests can be fast while one in a hundred takes ten seconds. That's why §3 matters: you measure the spread, not just one number.

## 1. Why this exists

The team dashboard shows average response time: 93ms. Everyone's happy. Meanwhile support is fielding complaints that checkout "hangs". One request in a hundred takes over two seconds, and those are mostly the users with full carts — the ones spending the most. The average stayed fine because 97 fast requests outweigh a slow one. **You can't fix what your numbers can't see**, and the most common number — the average — is the one that hides it. The worked example reproduces exactly this.

## Terms used in this lesson

1. **Monitoring**: This means watching for problems you predicted — "alert if the site is down" — with dashboards and alerts set up in advance.
2. **Observability**: This is how well you can answer *new* questions about a system from what it outputs, without shipping new code — "why are requests from this one customer slow today?"
3. **Metric**: This is a number measured over time, such as requests per second or error rate. Cheap to store and good for graphs and alerts.
4. **Log**: This is a record of one event, with details — "request 4071 failed with this error". Here, structured JSON lines.
5. **Trace**: This is the path of one request through the system, broken into timed **spans** — one per step or service — so you can see where the time went.
6. **Percentile**: This is the value below which a given percentage of measurements fall. **p99 latency** is the time that 99% of requests beat; 1% are slower.
7. **SLI (service level indicator)**: The letters stand for those three words. It is the measurement you care about, such as "the fraction of checkout requests that succeed in under 500ms".
8. **SLO (service level objective)**: The letters stand for those three words. It is your target for an SLI over a period, such as "99.9% over 30 days".
9. **SLA (service level agreement)**: The letters stand for those three words. It is a promise in a contract, with a penalty if broken. Usually looser than the SLO, to leave a margin.
10. **Error budget**: This is how much failure the SLO allows. A 99.9% SLO allows 0.1% of requests to fail; that 0.1% is the budget.
11. **Burn rate**: This is how fast the error budget is being used, compared with using it evenly. A burn rate of 1 uses exactly the whole budget by the end of the period.

## 2. The three pillars

| Pillar | Answers | Tool examples |
|---|---|---|
| **Metrics** | "how much / how many / how fast" — aggregatable numbers over time | Prometheus, Grafana |
| **Logs** | "what exactly happened" — discrete, timestamped event records | ELK, Loki, Splunk |
| **Traces** | "where did the time go" — one request's path across services | OpenTelemetry, Jaeger |

- **Metrics** are cheap numbers sampled over time. Great for dashboards and alerting; they show the shape of a problem but not the specifics.
- **Logs** are the detailed record — the raw material for working out *what* happened to a specific request. Structured logging is what makes them queryable.
- **Traces** follow one request across services through a propagated **trace ID**, showing how long each hop took. In a system with many services, "the API is slow" could be any of ten downstream calls; a trace shows which.

**They work as one workflow:** a metric alerts you that the error rate spiked, a trace localises it to one service, and that service's logs show the exact failure. The **shared ID** threading through all three is what makes that possible — which is why the request ID from last lesson matters so much.

**Monitoring vs observability.** Monitoring tells you *something* is wrong, for problems you predicted. Observability helps you find out *what*, including for problems you didn't.

## 3. Why averages lie — measure percentiles

Latency is never one number; it's a spread. The average (mean) adds every request and divides, so a few very slow requests barely move it when there are many fast ones. **Percentiles describe the spread directly:**

- **p50** (the median) — the typical request.
- **p95** — what 19 out of 20 requests beat.
- **p99** — what 99 out of 100 beat. The 1% slower than this are real users, often your heaviest ones.

**Track p50 and p99 together.** p50 tells you what most people get; p99 tells you how bad the bad experience is. And in a system where one page makes many requests, a "1 in 100" slow request is hit by far more than 1% of page loads.

## 4. The four golden signals

Google's SRE book distils "what to monitor" for any user-facing service into four signals — a better starting point than a hundred host metrics:

1. **Latency** — how long requests take, as percentiles. Track failed requests' latency separately: a fast error isn't a fast success.
2. **Traffic** — how much demand: requests per second.
3. **Errors** — the rate of failing requests.
4. **Saturation** — how full the system is: CPU, memory, connection pool, queue depth. How close to a limit.

The related **RED method** — **R**ate, **E**rrors, **D**uration — is the request-centric subset most people start with, and it's what the worked example computes.

## 5. SLOs, error budgets, and when to wake someone up

**Pick an SLI that matches what users feel**, for the routes that matter: "the fraction of checkout requests that succeed in under 500ms". Then set an **SLO**: "99.9% over 30 days". Now reliability is a number you can engineer to.

**The error budget** is what the SLO allows to fail. At 99.9% on 10 million requests a month, 10,000 can fail. Budget left → ship faster, take risks. Budget spent → slow down, fix reliability. It turns "never break" — impossible — into a trade-off you can discuss.

**Alert on symptoms, not causes.** Page a human for "users are failing, fast", not for "CPU is at 81%". Too many non-actionable alerts trains people to ignore alerts — the same failure as flaky tests.

**Burn rate** says how urgent a symptom is. It's the current error rate divided by the error rate the SLO allows:

$$\text{burn rate} = \frac{\text{error rate}}{1 - \text{SLO}}$$

At burn rate 1, you spend the whole budget in exactly the period. At 14.4, sustained for one hour, you spend 2% of a 30-day budget, because 14.4 × 1 hour ÷ 720 hours = 0.02. The SRE workbook's recommendation is to **page when the burn rate is at least 14.4 over the last hour *and* the last 5 minutes**. The hour shows it's serious; the 5 minutes show it's still happening, so nobody is woken for something that already recovered.

## Worked example — what the dashboard should have shown

The lab computes RED signals from structured log lines — the kind the backend-practices lesson produces — then works out an error budget and a paging decision.

```javascript
// signals.mjs — turn structured request logs into the numbers that answer "is it up, and is it fast?"

// The value below which `p` percent of samples fall (nearest-rank method).
export function percentile(values, p) {
  if (values.length === 0) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const rank = Math.ceil((p / 100) * sorted.length);
  return sorted[Math.max(0, rank - 1)];
}

export const mean = (values) => values.reduce((sum, v) => sum + v, 0) / values.length;

// RED: Rate, Errors, Duration — computed from one JSON log line per finished request.
export function red(logLines, windowSeconds) {
  const requests = logLines.map((line) => JSON.parse(line)).filter((e) => e.event === "request.finished");
  const durations = requests.map((e) => e.durationMs);
  const errors = requests.filter((e) => e.status >= 500).length;
  return {
    ratePerSecond: requests.length / windowSeconds,
    errorRate: requests.length ? errors / requests.length : 0,
    meanMs: Math.round(mean(durations)),
    p50Ms: percentile(durations, 50),
    p95Ms: percentile(durations, 95),
    p99Ms: percentile(durations, 99),
  };
}

// An SLO of 99.9% success over 30 days allows 0.1% of requests to fail: that allowance is the error budget.
export function errorBudget({ slo, totalRequests, failedRequests }) {
  const allowed = Math.floor(totalRequests * (1 - slo));
  return { allowed, used: failedRequests, remaining: allowed - failedRequests, spentFraction: failedRequests / allowed };
}

// Burn rate: how many times faster than "exactly on budget" errors are arriving.
// A burn rate of 1 uses the whole 30-day budget in exactly 30 days.
export const burnRate = (errorRate, slo) => errorRate / (1 - slo);

// Page a human only when the budget is burning fast, in a long window AND a short one:
// the long window shows it matters, the short one shows it's still happening.
// 14.4× sustained for an hour spends 2% of a 30-day budget (14.4 × 1h ÷ 720h).
export function shouldPage({ errorRateLastHour, errorRateLast5Min, slo }) {
  return burnRate(errorRateLastHour, slo) >= 14.4 && burnRate(errorRateLast5Min, slo) >= 14.4;
}
```

**Predict before running.** The test log has 100 requests in one minute: 97 between 20ms and 29ms, two at 1,800ms and 2,100ms, and one at 3,000ms that failed. What are the mean, p50, p95 and p99? Is the mean a fair summary?

```javascript
import { test } from "node:test";
import assert from "node:assert/strict";
import { burnRate, errorBudget, mean, percentile, red, shouldPage } from "./signals.mjs";

// 100 requests in one minute: 97 fast, 2 slow, 1 very slow that also failed.
const logs = [
  ...Array.from({ length: 97 }, (_, i) => ({ event: "request.finished", status: 200, durationMs: 20 + (i % 10) })),
  { event: "request.finished", status: 200, durationMs: 1800 },
  { event: "request.finished", status: 200, durationMs: 2100 },
  { event: "request.finished", status: 503, durationMs: 3000 },
  { event: "payment.charged" }, // not a finished request: ignored
].map((entry) => JSON.stringify(entry));

test("the average hides the slow tail; percentiles show it", () => {
  const signals = red(logs, 60);
  assert.equal(signals.meanMs, 93);    // "about 90ms" — looks fine
  assert.equal(signals.p50Ms, 24);     // the typical request
  assert.equal(signals.p95Ms, 29);     // 95 in 100 are this fast or faster
  assert.equal(signals.p99Ms, 2100);   // 1 in 100 users waits over two seconds
  assert.equal(signals.errorRate, 0.01);
  assert.equal(signals.ratePerSecond, 100 / 60);
});

test("percentile edge cases", () => {
  assert.equal(percentile([], 99), null);
  assert.equal(percentile([5], 99), 5);
  assert.equal(mean([1, 2, 3]), 2);
});

test("error budget: 99.9% over 10 million requests allows 10,000 failures", () => {
  assert.deepEqual(errorBudget({ slo: 0.999, totalRequests: 10_000_000, failedRequests: 2_500 }), {
    allowed: 10_000, used: 2_500, remaining: 7_500, spentFraction: 0.25,
  });
});

test("burn rate, and paging only on a fast burn that is still happening", () => {
  assert.equal(Math.round(burnRate(0.001, 0.999)), 1);   // exactly on budget
  assert.equal(Math.round(burnRate(0.02, 0.999)), 20);   // 2% errors: budget gone in 1.5 days
  assert.equal(shouldPage({ errorRateLastHour: 0.02, errorRateLast5Min: 0.03, slo: 0.999 }), true);
  assert.equal(shouldPage({ errorRateLastHour: 0.02, errorRateLast5Min: 0.0, slo: 0.999 }), false); // already recovered
  assert.equal(shouldPage({ errorRateLastHour: 0.005, errorRateLast5Min: 0.5, slo: 0.999 }), false); // a brief blip
});
```

**Lab:** these files are in `labs/observability/`. From the vault root, `python3 labs/run.py observability` runs them and checks this page still shows the same code.

**Run it.** From `labs/observability/`, run `node --test` (checked with Node 26). Expected:

```
ℹ tests 4
ℹ pass 4
ℹ fail 0
```

**The answers.** Mean **93ms**, p50 **24ms**, p95 **29ms**, p99 **2,100ms**. The mean is wrong about everyone. It's nearly four times what the typical request takes, and it's less than a twentieth of what the unlucky 1% wait. **p50 and p99 together** tell the true story: most requests are fast, and a few are very slow.

**Tracing the paging decision.** An error rate of 2% against a 99.9% SLO is a burn rate of 0.02 ÷ 0.001 = 20, which would spend the whole month's budget in a day and a half. With the last 5 minutes still at 3%, it pages. With the last 5 minutes at 0%, it doesn't — the incident is over, and a ticket is enough. A 50% spike lasting a few minutes, with the hour at 0.5%, doesn't page either: it's real, but it's a blip, not a fire.

**The limits.** These numbers come from logs after the fact. A real system computes them continuously from metrics, using histograms that approximate percentiles cheaply instead of sorting every value, and keeps logs for the detail.

## Common pitfalls

1. **Averaging latency** — §3. And never average percentiles across servers: the average of five p99s is not the p99 of the whole.
2. **Alerting on causes** — CPU, memory, disk — instead of what users feel. Put causes on dashboards and alert on symptoms.
3. **No shared ID** between logs, traces and responses, so the three pillars stay three separate piles.
4. **An SLO of 100%.** It forbids every deploy and every risk, and no dependency you use is 100% either.
5. **Too many alerts.** Every page should be actionable and come with a runbook — a short note on what to check first.

## Check your understanding

1. Which pillar tells you *that* something is wrong, which tells you *where*, and which tells you *what*?
2. Why is p99 more useful than the mean for latency? Give a case where the mean looks fine and users are suffering.
3. An endpoint serves 2 million requests a month with an SLO of 99.5%. How many failures does the error budget allow?
4. The error rate over the last hour is 1.5% against a 99.9% SLO, and 0% over the last 5 minutes. Page or not? Why?
5. Name the four golden signals, and one way to measure saturation for a Node API that talks to Postgres.

<details>
<summary>Answers — after your attempt</summary>

1. Metrics tell you *that* (an error-rate spike); traces tell you *where* (which service or step); logs tell you *what* (the exact error).
2. The mean blends a few slow requests into many fast ones and hides them. The worked example: mean 93ms, while 1 in 100 users waits over 2 seconds.
3. 2,000,000 × 0.005 = **10,000**.
4. Don't page. The hour's burn rate is 15, which is serious, but the last 5 minutes show it has stopped. Open a ticket to find out why, during working hours.
5. Latency, traffic, errors, saturation. For saturation: the database connection pool's usage (connections in use out of the maximum), event-loop delay, or memory.

</details>

## Practice — independent task

**The second half of SWE 101's week 6 milestone.**

1. Make the flagship log one structured `request.finished` line per request — method, route, status, duration and request ID. Middleware is the natural place.
2. Run the lab's `red()` on a day of real logs, or on a load test if traffic is low. Write down p50, p99 and the error rate.
3. Write one SLI and an SLO for the flagship's most important route, and work out its monthly error budget from real traffic.
4. Set up one alert in whatever the flagship is hosted on, based on a user-facing symptom, not a cause.

**Done when:** you can answer "is it up, is it fast, and what broke last?" for the flagship without opening the code, and the SLO is written in the README.

## Before moving on

You can name the three pillars and what connects them, compute and explain percentiles, define an SLI and SLO, and decide when an alert should page.

**Recap.** Metrics for *that*, traces for *where*, logs for *what*, joined by a shared ID. Latency, traffic, errors, saturation. Percentiles, not averages. An SLO turns reliability into a number, and the error budget is what it allows to fail. Page on a fast burn that's still happening; everything else is a ticket.

**Next.** Week 7: [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation and output encoding]].

## Related
- [[languages/01-java/03-tooling/05-logging-and-observability|Logging & observability (Java)]] — the application side, grounded in a real pipeline
- [[devops/10-observability/02-the-observability-stack|The observability stack]] — the tools that implement these pillars
- [[backend/07-practices/01-backend-best-practices|Backend best practices]] — the structured logs this lesson reads
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability and reliability]] — what "three nines" costs
