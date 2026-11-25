---
id: 7b8a895d-bd69-47ff-9da5-7647829e10a8
---

# Causal Inference & Econometrics

Causal inference is working out whether one thing actually causes another, not just whether the two tend to happen together. It matters when you want to change something and know what will happen as a result. For example, people who carry umbrellas get wet more often, but the umbrella is not the cause. Rain causes both.

## Prediction vs causation — a fundamental split
<!-- bite: 44eaad75-049b-44ac-a0ae-e752fef947f5 -->

Most of [[machine-learning/index|ML]] answers **prediction**: given these features, what's the likely outcome? Causal inference answers **intervention**: if we *change* this, what happens to the outcome? These are different questions with different methods, and conflating them is dangerous:

- A model can *predict* churn brilliantly using "number of support tickets" — but that doesn't mean *reducing tickets* reduces churn (both may be driven by an unhappy customer). Acting on a predictive feature as if it were causal is a classic, costly mistake.
- Prediction cares about *accuracy*; causation cares about *unbiased effect estimates*, which need entirely different validation.

## Why correlation isn't causation — the three explanations
<!-- bite: 11e125ce-ea75-4efa-ad97-63f467f2e923 -->

When X and Y correlate ([[data-science/02-descriptive-statistics|correlation]]), exactly one isn't always the reason:

1. **X causes Y** (what you hope).
2. **Y causes X** (reverse causation).
3. **A confounder Z causes both** — the killer. Ice-cream sales and drownings correlate because *summer* drives both. Control for the confounder and the correlation vanishes.
4. Pure **chance** (spurious).

A **confounder** is a variable that influences both the supposed cause and the effect, creating a misleading association. The entire game of causal inference is *ruling out confounders* so a remaining association can be trusted as causal.

## The gold standard, and why we often can't use it
<!-- bite: 26e90f19-d200-424c-b7f0-41310c98b1d7 -->

A [[data-science/06-experimentation-and-ab-testing|randomized experiment]] eliminates confounders by design — randomization makes the groups equivalent on *everything*, known and unknown. But you often **can't randomize**: you can't randomly assign people to smoke, or randomly impose a minimum wage on some cities. So econometrics and causal inference developed methods to approximate an experiment from **observational data**.

## Quasi-experimental methods
<!-- bite: c6810682-4525-49dd-a147-e2b6c418784a -->

Each exploits some source of "as-if random" variation:

- **Difference-in-Differences (DiD)** — compare the *change* in an outcome for a group that got a treatment vs a similar group that didn't, before and after. Cancels out fixed differences between groups and common time trends. (Did the state that raised its minimum wage see employment change *differently* than a comparable state that didn't?)
- **Regression Discontinuity (RDD)** — when treatment is assigned by a sharp cutoff (a scholarship for scores ≥ 90), people *just above* and *just below* the cutoff are near-identical except for the treatment — a local natural experiment.
- **Instrumental Variables (IV)** — find an "instrument" that affects the treatment but only influences the outcome *through* it, isolating causal variation. Powerful but fragile (finding a valid instrument is hard).
- **Matching / propensity scores** — pair treated and untreated units with similar observed characteristics, mimicking a randomized comparison — but only controls for confounders you *measured* (its key weakness).

The universal caveat: these control for *observed* confounders. An **unobserved** confounder you didn't measure can still bias the result — which is why a real experiment, when possible, remains stronger.

## Regression for inference (vs prediction)
<!-- bite: 2f9784e2-1873-4038-990b-1e838e3b7b3a -->

The same [[machine-learning/03-classical-ml/15-linear-models-and-regression|linear regression]] from the ML track is used very differently here. In ML you care about predictive accuracy; in econometrics you care about a single **coefficient** as a causal effect — "controlling for age, income, and region, each extra year of education is associated with X% higher earnings." That shifts the emphasis entirely: unbiasedness over accuracy, careful choice of what to control for (controlling for the wrong variable — a "collider" or a mediator — can *introduce* bias), interpretable coefficients with confidence intervals, and checking assumptions. This inferential use of regression is the heart of classical econometrics.

## Time series (the econometrics staple)
<!-- bite: 481655ac-1ca6-470e-88c6-f27da71c3f2f -->

Much economic/business data is a sequence over time (sales, prices, GDP), which breaks the "independent observations" assumption most methods rely on. Key ideas worth recognizing: **trend** and **seasonality** (decompose them out), **autocorrelation** (today depends on yesterday), **stationarity** (statistical properties stable over time — usually required, achieved by differencing), and models like **ARIMA** (classical) or Prophet/ML approaches for forecasting. Critically, time-series validation must respect order — you can't [[machine-learning/04-model-evaluation/05-validation-and-tuning|validate]] on the past using a model trained on the future.

## The honest bottom line
<!-- bite: b2c7cd76-af50-4d2f-b6fd-f49812547d77 -->

Causal claims from observational data are *always* weaker than from a randomized experiment and rest on assumptions that can't be fully verified. A good data scientist is explicit about this — states the assumptions, tests their sensitivity, and calibrates confidence accordingly — rather than dressing a correlation up as causation with fancy methods. Knowing *when you can and can't* make a causal claim is itself the expertise.

## Related
<!-- bite: 88dec4a3-9052-4663-bb46-8bbeed42fcca -->
- [[data-science/06-experimentation-and-ab-testing|Experimentation & A/B Testing]] — the gold standard these methods approximate
- [[data-science/02-descriptive-statistics|Descriptive Statistics]] — correlation vs causation, introduced
- [[machine-learning/03-classical-ml/15-linear-models-and-regression|Regression (ML-engineer)]] — the same tool, used for prediction there vs inference here

## About this lesson
<!-- bite: 05a05701-f259-467a-ac0b-752c52d637e2 -->

**Level:** reference. **Covers:** from the roadmap.sh `ai-data-scientist` roadmap. The most intellectually demanding part of the path: establishing **cause and effect** from data, especially when you *can't* run a clean [[data-science/06-experimentation-and-ab-testing|experiment]]. This is what separates "we found a correlation" from "we know what will happen if we act."
