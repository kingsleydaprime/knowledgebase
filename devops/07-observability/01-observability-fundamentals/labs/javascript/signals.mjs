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
