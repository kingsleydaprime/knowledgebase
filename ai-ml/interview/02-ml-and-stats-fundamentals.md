# AI/ML Interview — ML & Stats Fundamentals

From [[ai-ml/02-ml-engineer/README|02-ml-engineer]] and [[ai-ml/01-data-scientist/README|01-data-scientist]]. The fundamentals round — these come up even in AI-engineering interviews, because they test whether you can reason about a model's behaviour rather than just call an API.

---

### Q1. [Beginner→Intermediate] 🔥 Explain the bias-variance tradeoff.

**Strong answer covers:** **bias** is error from wrong assumptions — the model is too simple to capture the pattern (**underfitting**). **Variance** is sensitivity to the particular training sample — the model memorises noise (**overfitting**). Total error decomposes into bias² + variance + irreducible noise.

**The diagnostic, which is more useful than the definition:**
- **High training error** → high bias. More capacity, better features, train longer.
- **Low training error, high validation error** → high variance. More data, regularisation, simpler model, early stopping.

**The nuance worth adding:** the classic U-shaped curve isn't the whole story. **Double descent** — heavily overparameterised models (deep nets, LLMs) get *worse* then *better again* past the interpolation threshold. It's why "more parameters overfits" stopped being reliable advice.

---

### Q2. [Intermediate] 🔥 Your model is 99% accurate. Why might that be worthless?

**Strong answer covers:** **class imbalance.** If 99% of transactions are legitimate, predicting "legitimate" always scores 99% and catches zero fraud. Accuracy is nearly meaningless on imbalanced data.

**Use instead:**
- **Precision** — of those flagged, how many were real? (Cost of false positives.)
- **Recall** — of the real ones, how many did we catch? (Cost of false negatives.)
- **F1** — harmonic mean, when you need one number.
- **PR-AUC** over **ROC-AUC** for heavy imbalance — ROC looks deceptively good because the true-negative count dominates.

**The senior framing:** *"the metric follows from the cost of each error type."* Cancer screening: recall dominates — a missed case is catastrophic, a false positive means another test. Spam filtering: precision dominates — a lost legitimate email is worse than a spam that got through. **Pick the operating point from the business cost, not the F1 maximum**, and present the precision/recall curve so the decision is explicit.

---

### Q3. [Intermediate] 🔥 What is data leakage, and how does it hide?

**Strong answer covers:** information available at training time that won't be available at prediction time. It produces a model that looks brilliant offline and fails in production — the most expensive and most common ML bug.

**Where it hides:**
- **Preprocessing before splitting.** Fitting a scaler or imputer on the full dataset leaks test statistics into training. Fit on train, transform test. Use a pipeline so this is structural, not a discipline problem.
- **Temporal leakage.** Random splits on time-series data let the model see the future. **Split by time.**
- **Target leakage.** A feature that's a proxy for the outcome — `discount_applied` predicting `purchase`, or a field only populated after the event occurs.
- **Group leakage.** The same user/patient in both train and test.
- **Tuning on the test set.** Repeatedly checking test performance leaks it through *your* decisions. That's what the validation set is for.

**The tell to name:** *"suspiciously good results are a bug report, not a success."* If accuracy jumps unexpectedly, look for leakage before celebrating.

---

### Q4. [Intermediate] Explain cross-validation and when a random split is wrong.

**Strong answer covers:** k-fold CV splits into k parts, trains on k−1 and validates on the held-out one, rotating — so every point is used for validation once. Gives a **variance estimate** on your performance, not just a point estimate, which is the actual value.

**When random splitting is wrong:**
- **Time series** → forward-chaining / rolling-origin. Never let the model see the future.
- **Grouped data** → GroupKFold, so a user appears in only one fold.
- **Imbalanced classes** → StratifiedKFold, so rare classes appear in every fold.

**The three-way split point:** train / validation / test. **The test set is touched once, at the end.** Every time you look at it and make a decision, it becomes a validation set and stops being an unbiased estimate.

---

### Q5. [Intermediate] 🔥 How do you run and interpret an A/B test?

**Strong answer covers:** define **one primary metric** and the **minimum detectable effect** *before* starting; compute the required sample size from that plus your baseline rate and desired power (typically 80%); randomise at the right unit (usually user, not session/pageview — otherwise the same user lands in both arms and you break independence); run for a **pre-determined duration** covering full weekly cycles.

**The mistakes to name — this is where the interview is decided:**
- **Peeking.** Checking daily and stopping when significant inflates your false-positive rate dramatically. Fix: fix the duration up front, or use sequential testing designed for it.
- **Multiple comparisons.** Testing 20 metrics at p<0.05 gives you ~1 false positive by construction. Correct for it, or pre-register one primary metric.
- **Ignoring practical significance.** A statistically significant 0.01% lift may not be worth the complexity. **Report the confidence interval, not just the p-value** — it shows the effect *size*, which is what the decision actually needs.
- **Simpson's paradox** — an aggregate result reversing within every segment. Check segments.
- **Novelty effects** — an initial lift that decays as the novelty wears off.

**What a p-value means, precisely:** the probability of seeing data at least this extreme *if the null hypothesis were true*. **Not** the probability that the null is true, and not the probability your feature works. Getting this right is a strong signal; almost everyone gets it wrong. → [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|experimentation & A/B testing]]

---

### Q6. [Intermediate] Correlation isn't causation — so how *do* you establish causation?

**Strong answer covers:** an RCT (A/B test) when you can randomise — randomisation balances confounders in expectation, including the ones you didn't think of. That's the whole reason it works.

**When you can't randomise** (ethics, cost, or it already happened), quasi-experimental methods:
- **Difference-in-differences** — compare change over time in a treated group vs an untreated one, differencing out fixed group effects.
- **Regression discontinuity** — exploit a sharp threshold (a cutoff score) where units just above and below are otherwise comparable.
- **Instrumental variables** — find something affecting treatment but not the outcome directly.
- **Propensity score matching** — match on the probability of treatment. Weakest of these; only adjusts for observed confounders.

**The point to make:** every one of these rests on an assumption you cannot verify from the data alone (parallel trends, exclusion restriction, no unobserved confounding). **Stating the assumption is the analysis**, and an answer that names it is far stronger than one that names the method. → [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal inference]]

---

### Q7. [Intermediate] 🔥 Your model performed well in testing and is degrading in production. Why?

**Strong answer covers the drift taxonomy:**
- **Data drift** (covariate shift) — the input distribution moved. New user demographics, a changed upstream feature, a different sensor.
- **Concept drift** — the *relationship* between input and target moved. Fraud patterns adapt; user preferences shift. The model is now wrong even on familiar-looking inputs.
- **Training-serving skew** — the features are computed differently in production than in training. Extremely common, and the strongest argument for a shared feature pipeline or a feature store.
- **Feedback loops** — the model's own predictions change the data it later trains on. A recommender that only shows popular items generates data proving those items are popular.
- **A silent upstream change** — a schema change, a unit change, a nulled column. Often the actual cause.

**How you'd catch it:** monitor input feature distributions (not just output metrics), track prediction distribution, and where possible measure **delayed ground truth**. And have a retraining cadence plus a rollback path, because the question isn't whether it degrades but when.

---

### Q8. [Intermediate] Explain regularisation — L1 vs L2.

**Strong answer covers:** both penalise large coefficients to reduce variance. **L2 (Ridge)** penalises squared magnitude — shrinks coefficients smoothly toward zero, handles correlated features by spreading weight across them. **L1 (Lasso)** penalises absolute magnitude — **drives coefficients exactly to zero**, so it performs feature selection.

**Why L1 zeroes and L2 doesn't:** the L1 constraint region has corners on the axes, so the optimum frequently lands exactly on one. It's a geometric result, and being able to say *why* rather than just *that* is the differentiator here.

**Elastic net** blends both. And note the equivalents elsewhere: dropout, early stopping, data augmentation, and weight decay are all regularisation in different clothes — **anything that reduces effective model capacity or adds noise to training**.

---

### Q9. [Intermediate] When would you use a gradient-boosted tree over a neural network?

**Strong answer covers:** **on tabular data, gradient boosting (XGBoost/LightGBM/CatBoost) usually still wins** — and it's worth stating plainly because people assume deep learning dominates everywhere. It handles mixed types and missing values natively, needs little preprocessing (no scaling), trains fast on CPU, and gives usable feature importances.

**Neural networks win where structure matters** — images, audio, text, sequences — because the architecture encodes an inductive bias (locality, translation invariance, attention) that trees can't express, and because they benefit from transfer learning from large pretrained models.

**The practical rule:** start with a baseline that's almost embarrassingly simple (logistic regression, or predicting the mean). Then gradient boosting. Reach for deep learning when you have unstructured data, or a pretrained model to fine-tune, or enormous data. **A model you can't explain to a stakeholder has a real cost**, and that belongs in the decision too.

---

### Q10. [Intermediate] What does "putting a model in production" actually involve?

**Strong answer covers everything that isn't the model — which is the point:**

- **Reproducibility** — versioned data, code, and model artefacts. "Which model made this prediction?" must be answerable.
- **A feature pipeline shared between training and serving**, or you get skew (Q7).
- **Serving** — batch vs real-time, latency budget, autoscaling.
- **Monitoring** — input distributions, prediction distributions, business metrics, and ground truth when it arrives.
- **A rollback path**, and ideally shadow-mode/canary deployment so a new model is evaluated on live traffic before it decides anything.
- **Retraining** — scheduled or triggered by drift, with the same eval gate as the original.
- **Governance** — who approved it, what data it was trained on, fairness evaluation across segments, and an audit trail if it's a regulated decision.

**The line that lands:** *"the model is maybe 10% of the work; the other 90% is the system around it."* → [[project-ideas|the end-to-end MLOps project]] is the ⭐ that proves this rather than asserting it.
