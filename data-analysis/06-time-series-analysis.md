# Time Series Analysis

**[Intermediate → Advanced]** — data that arrives in time order, why it breaks ordinary statistics, and how to separate a real trend from noise and seasonality.

## The kid version first

A huge amount of business data is a **time series** — a number measured repeatedly over time: daily revenue, hourly traffic, monthly signups. It looks simple, but it has a trap: **the points aren't independent** (today depends on yesterday), which breaks the ordinary statistics that assume they are. And the eye is easily fooled — a "spike" might just be Monday, a "trend" might just be Christmas. Time series analysis is the toolkit for telling a real signal from the rhythm and the noise.

This is the analyst-and-business side of time; the signal-processing side (Fourier, filters) lives in [[foundations/digital-signal-processing/README|DSP]].

## Why time series is its own thing

Ordinary statistics assumes observations are **independent** — one data point tells you nothing about the next. Time series violates this completely: **autocorrelation** means today's value is correlated with yesterday's. That single fact has big consequences:

- **You can't shuffle or randomly sample** — the order *is* the information
- **Standard significance tests overstate confidence** — they assume independence you don't have, so they see "significant" changes that are just the series' natural momentum
- **You can forecast** — precisely *because* the past predicts the future here, which isn't true of independent data

## The decomposition — the core mental model

**Any time series can be broken into components, and understanding them is 80% of the value:**

```
   observed  =  trend  +  seasonality  +  noise
                  │           │            │
            long-term    repeating     random,
            direction     pattern    unexplained
```

- **Trend** — the long-term direction (is the business actually growing, ignoring the wiggles?)
- **Seasonality** — regular, repeating patterns: daily (traffic peaks at lunch), weekly (B2B drops at weekends), yearly (retail spikes at Christmas). **Often the *largest* component, and the one that fools people most**
- **Noise / residual** — the random variation left over

**Why this matters enormously for analysts:** most "the number changed!" panics are **seasonality, not a real change**. Sales "dropped" on Saturday because it's Saturday; traffic "spiked" because it's Black Friday. **Decomposing — or just comparing like-with-like (this Saturday vs last Saturday, this December vs last December) — is what stops you from investigating a pattern that repeats every week** → [[data-analysis/04-exploratory-and-diagnostic-analysis|confirm the change is real]].

## The everyday techniques

Most analyst time-series work is simple and high-value, not heavy modelling:

**Moving averages / rolling windows** — smooth out noise and seasonality to see the trend. A 7-day moving average of daily data removes the day-of-week pattern, revealing whether the underlying trend is up or down. **The single most useful time-series tool for an analyst**, and one line of SQL or pandas → [[data-analysis/02-sql-for-analysis|window functions]].

**Year-over-year / period-over-period comparison** — compare the same period across cycles (this December vs last December) to control for seasonality without modelling it. The pragmatic analyst's answer to "is this normal?"

**Growth rates** — absolute change, percentage change, and CAGR (compound annual growth rate) for smoothing multi-period growth into one comparable number.

**Indexing to a baseline** — rebase everything to 100 at a start point to compare *relative* movements of series with different scales.

## Forecasting — predicting the future

When you need to project forward (demand planning, capacity, budgets), forecasting methods, roughly in order of complexity:

- **Naive / seasonal-naive** — "tomorrow ≈ today," or "next December ≈ last December." **Surprisingly hard to beat, and the baseline every fancier method must outperform** — always start here
- **Moving average / exponential smoothing** — weight recent observations more; Holt-Winters handles trend *and* seasonality. The workhorse for stable business series
- **ARIMA** — the classical statistical model (autoregressive + moving average on a differenced series). Powerful, requires the series to be **stationary** (below), more involved to tune
- **Prophet** (Meta) — designed for business time series with strong seasonality and holidays; robust, forgiving, popular with analysts because it "just works" on messy real data
- **ML approaches** — gradient boosting or neural nets (LSTMs) for complex, multi-variate cases → [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/README|sequence models]]. Usually overkill for a single business metric

**The honest guidance: start with the naive baseline and simple smoothing.** Most business forecasting needs are met by seasonal-naive or exponential smoothing, and reaching for ARIMA or an LSTM on a series that a moving average handles is the analyst version of over-engineering → [[data-engineering/06-distributed-processing|the "you probably don't need it" instinct]].

## Stationarity — the concept ARIMA needs

**A stationary series has constant statistical properties over time** — its mean and variance don't drift. Many methods (ARIMA especially) assume it, because you can't model a moving target. A series with a trend or growing variance isn't stationary, so you **difference** it (model the *change* rather than the level) to make it so. You don't need the full theory, but you need to know the word and the idea: *if the mean is drifting, model the differences.*

## The traps

Time series has specific, common footguns:

- **Mistaking seasonality for a trend** — the #1 analyst error; always compare like-with-like or decompose first
- **Spurious correlation** — two unrelated series that both trend upward will correlate strongly (ice-cream sales and drownings both rise in summer). **Trending series correlate by default; it means nothing** → [[data-analysis/04-exploratory-and-diagnostic-analysis|correlation ≠ causation]]
- **Overfitting a forecast** — a model that fits history perfectly often predicts the future terribly; validate on held-out *later* data, never a random split (that leaks the future)
- **Ignoring changepoints** — a real structural break (a new pricing model, a pandemic) means the past no longer predicts the future, and a naive forecast sails straight through it
- **Anomaly vs noise** — flagging normal variation as an "anomaly." Set thresholds against the series' actual seasonal variation, not a flat line → [[foundations/digital-signal-processing/07-spectral-analysis|the same signal-vs-noise problem]]

## Key insight

**Time series is data whose order is the information — points aren't independent, which breaks ordinary statistics and enables forecasting — and the core skill is decomposition: separating a real trend from repeating seasonality and random noise.** Most "the metric changed!" alarms are seasonality, so comparing like-with-like (this Saturday vs last) or taking a moving average is the highest-value everyday tool. For forecasting, start with the naive seasonal baseline that fancier methods must beat, and reach for ARIMA or ML only when simple smoothing genuinely fails. Throughout, remember that trending series correlate by default, which means nothing.

## Related
- [[data-analysis/04-exploratory-and-diagnostic-analysis|diagnostic analysis]] — "is this change real or seasonal?"
- [[data-analysis/02-sql-for-analysis|SQL for analysis]] — moving averages and period-over-period in SQL
- [[foundations/digital-signal-processing/README|DSP]] — the signal-processing side of time (Fourier, filters)
- [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|econometrics]] — time series for causal inference

*Source: [reference] — Sep 2026.*
