---
id: e2781266-f896-4f60-9b9f-31735f5b3d74
---

# Explainable AI

Explainable AI shows why a model made a particular decision.

## What explainable AI is
<!-- bite: 01578b5a-836c-4a3b-88f7-1419b3244484 -->

Explainable AI is the set of methods for showing why a model made a particular decision. A model can be accurate and still be hard to trust if nobody can say why it decided something. If a bank app refuses your loan, explainable AI is what lets the bank tell you which factors counted against you.

Next: why that matters, then the kinds of explanation.

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

## Check your understanding
<!-- bite: a92970ed-96f1-4616-ad4d-c8b4896d7d1e -->

Try each one before you open the answer.

1. <!-- q: mcq id="85bbdde2" -->
   A user asks, "Why was my loan refused?" Which kind of explanation is that?

   - [ ] Global
   - [x] Local

   <details><summary>Answer</summary>

   Local: why this one prediction came out as it did. Global explanations describe what drives the model overall.

   </details>

2. <!-- q: gap id="b7e660cf" answers="shap;lime" -->
   Fill in the gaps. ___ is based on Shapley values from game theory. ___ explains one prediction by fitting a simple linear model in the neighbourhood of the input.

   <details><summary>Answer</summary>

   SHAP, then LIME. SHAP is more consistent and is the de facto standard, especially for gradient-boosted models.

   </details>

3. <!-- q: mcq id="f042495c" -->
   Which models are interpretable on their own, with no extra tools? Choose all that apply.

   - [x] Linear or logistic regression
   - [x] A shallow decision tree
   - [ ] A deep neural network
   - [ ] A large ensemble

   <details><summary>Answer</summary>

   Linear models (read the weights) and shallow trees (read the path). Deep networks and big ensembles are black boxes that need post-hoc tools.

   </details>

4. <!-- q: mcq id="d479a4ca" -->
   A "husky vs wolf" classifier turned out to be looking at snow in the background. Which reason for explainability does that show?

   - [x] Debugging: a model can be right for the wrong reason
   - [ ] Regulation
   - [ ] Speed

   <details><summary>Answer</summary>

   Debugging. The explanation showed the model was using the wrong evidence.

   </details>

5. <!-- q: open id="9ef6338f" -->
   Why should you treat a SHAP or LIME explanation as evidence rather than the truth?

   <details><summary>Answer</summary>

   An explanation is an approximation of what the model does, not its actual reasoning. LIME in particular can change depending on how the neighbourhood is sampled.

   </details>

## Related
<!-- bite: 711153a3-2273-495d-b130-92e430ba3c15 -->
- [[machine-learning/03-classical-ml/10-decision-trees-6|Trees & Ensembles]] — feature importances, and SHAP's home turf
- [[machine-learning/04-model-evaluation/05-validation-and-tuning|Validation & Tuning]] — interpretability as a model-selection axis
- [[ai-engineering/10-safety-and-production/index|Safety & Production]] — bias/fairness, where explanations are checked

## About this lesson
<!-- bite: 1a192d03-9063-4f6d-9343-e1ca94671e8a -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. Making a model's decisions understandable — increasingly a requirement, not a nicety.
