# Conditional Probability & Bayes' Theorem

Conditional probability — "the probability of A, *given that* B happened" — is the mathematical backbone of most classification. A spam classifier is, at its core, estimating `P(spam | this email's words)`: the probability of spam, given the specific evidence in front of it.

## Conditional probability, notated

`P(A | B)` reads as "the probability of A, given B." It's different from `P(A)` (the plain, unconditional probability of A) whenever B changes what you know — `P(rain)` might be 20% in general, but `P(rain | dark clouds overhead)` is much higher, because the evidence shifts the estimate.

## Bayes' theorem — flipping a conditional probability around

Often you know `P(evidence | hypothesis)` (how likely some evidence would be, if a hypothesis were true) but actually want `P(hypothesis | evidence)` (given the evidence you actually observed, how likely is the hypothesis). Bayes' theorem is the formula for making that flip:

```
P(A | B) = P(B | A) * P(A) / P(B)
```

In plain terms: **start with a prior belief about A, then update it based on how likely the evidence B would be if A were true, weighted against how likely B is overall.**

## Worked example — spam detection

Say you want `P(spam | contains "free money")`:

- `P(spam)` — prior probability any email is spam, say 20% (from your training data).
- `P("free money" | spam)` — how often spam emails contain that phrase, say 30%.
- `P("free money")` — how often *any* email (spam or not) contains that phrase, say 8%.

```
P(spam | "free money") = P("free money" | spam) * P(spam) / P("free money")
                        = 0.30 * 0.20 / 0.08
                        = 0.75
```

Seeing that phrase moves the estimate from a 20% prior probability of spam up to 75% — this exact update mechanism (start with a prior, update with evidence) is what **Naive Bayes classifiers** implement directly, and it's the same conceptual structure underlying any system that needs to reason under uncertainty from evidence.

## Why "naive"

Naive Bayes classifiers assume every piece of evidence (every word in an email, say) contributes to the probability *independently* of every other piece of evidence — which is rarely strictly true (word choices aren't really independent of each other) but works surprisingly well in practice despite the simplification, which is why the method carries "naive" in its name rather than being considered fundamentally flawed.

## Gotchas

- Ignoring the **prior** (`P(A)`) is a common reasoning mistake outside of ML too — evidence that seems damning can still leave a low overall probability if the prior probability of the hypothesis was very low to begin with (a classic case: a rare disease with a fairly accurate test can still mean "positive test result" is more likely a false positive than an actual case, if the disease is rare enough).
- `P(A | B)` and `P(B | A)` are **not the same thing** and conflating them is a common error — "probability of spam given this phrase" and "probability of this phrase given spam" answer different questions, which is exactly why Bayes' theorem (a formula for converting between them) is needed at all.

## Related
- [[01-distributions|distributions]]
- [[02-expectation-and-variance|expectation-and-variance]]
