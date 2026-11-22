---
id: e2781266-f896-4f60-9b9f-31735f5b3d74
---

# Explainable AI

Explainable AI is the set of methods for showing why a model made a particular decision. A model can be accurate and still be hard to trust if nobody can say why it decided something. If a bank app refuses your loan, explainable AI is what lets the bank tell you which factors counted against you.

## Why interpretability matters
<!-- bite: 2738a34a-5b0f-4bdb-a252-c0447a08f0c8 -->

A model can be accurate and still unusable if no one can tell *why* it decided something. Explainability matters for:

- **Trust** — stakeholders won't deploy a black box making consequential calls (loans, medical, hiring).
- **Debugging** — a model can be right for the wrong reason (the famous case: a classifier that detected "husky vs wolf" by looking at snow in the background). Explanations expose that.
- **Fairness & bias** — checking a model isn't keying off a protected attribute ([[ai-engineering/10-safety-and-production/index|bias & fairness]]).
- **Regulation** — laws (GDPR's "right to explanation," financial/medical rules) increasingly *require* explanations for automated decisions.

## The interpretability spectrum
<!-- bite: 31e45a7b-bfb7-4c55-907d-859b5ba7a3ac -->

Models trade accuracy against transparency:

- **Intrinsically interpretable** — [[machine-learning/03-classical-ml/14-linear-models-and-regression|linear/logistic regression]] (read the weights), shallow [[machine-learning/03-classical-ml/10-decision-trees-6|decision trees]] (read the path). You get explanation for free.
- **Black boxes** — deep networks, large ensembles. Accurate but opaque; they need *post-hoc* explanation tools.

A recurring engineering decision: a slightly less accurate but interpretable model is often the better *product* choice when explanation is required — accuracy isn't the only axis ([[machine-learning/04-model-evaluation/05-validation-and-tuning|model selection]]).

## Global vs local explanations
<!-- bite: 10112585-0f5a-4788-b03e-611fa8377433 -->

- **Global** — what drives the model *overall* (which features matter most across all predictions). [[machine-learning/03-classical-ml/10-decision-trees-6|Tree feature importances]] are a simple global view.
- **Local** — why *this specific* prediction came out as it did. Usually what a user or auditor actually asks.

## SHAP and LIME — the two standard tools
<!-- bite: 9fb9dcbe-0fa6-458b-861f-3d7f3d8c6517 -->

Both explain any black-box model *after* training, model-agnostically:

- **LIME** (Local Interpretable Model-agnostic Explanations) — explains one prediction by fitting a simple interpretable model (a linear model) to the black box's behavior *in the local neighborhood* of that input. Fast, intuitive, but the explanation can be unstable (depends on how the neighborhood is sampled).
- **SHAP** (SHapley Additive exPlanations) — grounded in cooperative game theory (Shapley values): it fairly attributes the prediction among the input features, computing how much each feature pushed the output up or down from a baseline. More theoretically sound and consistent than LIME, does both local and global views, and has fast implementations for trees. The de-facto standard, especially for [[machine-learning/03-classical-ml/10-decision-trees-6|gradient-boosted models]].

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)     # per-feature contribution to each prediction
shap.summary_plot(shap_values, X)          # global view; force_plot for a single prediction
```

## The honest caveats
<!-- bite: 0b455ad2-03f2-4553-90f6-cc9d34c52069 -->

- **An explanation is an approximation**, not the model's actual reasoning — especially for LIME. Treat explanations as evidence, not ground truth.
- **Explaining LLMs is much harder** — SHAP/LIME target tabular/feature-based models. For [[ai-engineering/index|LLMs]], "interpretability" means different, less mature techniques (attention analysis, mechanistic interpretability), and in practice grounding/citation ([[ai-engineering/06-rag-and-embeddings/index|RAG]]) and [[ai-engineering/10-safety-and-production/index|evals]] do more for trust than feature attribution.

## Related
<!-- bite: 711153a3-2273-495d-b130-92e430ba3c15 -->
- [[machine-learning/03-classical-ml/10-decision-trees-6|Trees & Ensembles]] — feature importances, and SHAP's home turf
- [[machine-learning/04-model-evaluation/05-validation-and-tuning|Validation & Tuning]] — interpretability as a model-selection axis
- [[ai-engineering/10-safety-and-production/index|Safety & Production]] — bias/fairness, where explanations are checked

## About this lesson
<!-- bite: 1a192d03-9063-4f6d-9343-e1ca94671e8a -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. Making a model's decisions understandable — increasingly a requirement, not a nicety.
