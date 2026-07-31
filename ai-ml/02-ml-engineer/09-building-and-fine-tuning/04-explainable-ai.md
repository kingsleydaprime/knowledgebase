# Explainable AI

**[reference]** — from the roadmap.sh `machine-learning` roadmap. Making a model's decisions understandable — increasingly a requirement, not a nicety.

## Why interpretability matters

A model can be accurate and still unusable if no one can tell *why* it decided something. Explainability matters for:

- **Trust** — stakeholders won't deploy a black box making consequential calls (loans, medical, hiring).
- **Debugging** — a model can be right for the wrong reason (the famous case: a classifier that detected "husky vs wolf" by looking at snow in the background). Explanations expose that.
- **Fairness & bias** — checking a model isn't keying off a protected attribute ([[ai-ml/03-ai-engineer/10-safety-and-production|bias & fairness]]).
- **Regulation** — laws (GDPR's "right to explanation," financial/medical rules) increasingly *require* explanations for automated decisions.

## The interpretability spectrum

Models trade accuracy against transparency:

- **Intrinsically interpretable** — [[ai-ml/02-ml-engineer/03-classical-ml/01-regression|linear/logistic regression]] (read the weights), shallow [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|decision trees]] (read the path). You get explanation for free.
- **Black boxes** — deep networks, large ensembles. Accurate but opaque; they need *post-hoc* explanation tools.

A recurring engineering decision: a slightly less accurate but interpretable model is often the better *product* choice when explanation is required — accuracy isn't the only axis ([[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|model selection]]).

## Global vs local explanations

- **Global** — what drives the model *overall* (which features matter most across all predictions). [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|Tree feature importances]] are a simple global view.
- **Local** — why *this specific* prediction came out as it did. Usually what a user or auditor actually asks.

## SHAP and LIME — the two standard tools

Both explain any black-box model *after* training, model-agnostically:

- **LIME** (Local Interpretable Model-agnostic Explanations) — explains one prediction by fitting a simple interpretable model (a linear model) to the black box's behavior *in the local neighborhood* of that input. Fast, intuitive, but the explanation can be unstable (depends on how the neighborhood is sampled).
- **SHAP** (SHapley Additive exPlanations) — grounded in cooperative game theory (Shapley values): it fairly attributes the prediction among the input features, computing how much each feature pushed the output up or down from a baseline. More theoretically sound and consistent than LIME, does both local and global views, and has fast implementations for trees. The de-facto standard, especially for [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|gradient-boosted models]].

```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)     # per-feature contribution to each prediction
shap.summary_plot(shap_values, X)          # global view; force_plot for a single prediction
```

## The honest caveats

- **An explanation is an approximation**, not the model's actual reasoning — especially for LIME. Treat explanations as evidence, not ground truth.
- **Explaining LLMs is much harder** — SHAP/LIME target tabular/feature-based models. For [[ai-ml/03-ai-engineer/README|LLMs]], "interpretability" means different, less mature techniques (attention analysis, mechanistic interpretability), and in practice grounding/citation ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]]) and [[ai-ml/03-ai-engineer/10-safety-and-production|evals]] do more for trust than feature attribution.

## Related
- [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|Trees & Ensembles]] — feature importances, and SHAP's home turf
- [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|Validation & Tuning]] — interpretability as a model-selection axis
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — bias/fairness, where explanations are checked
