---
id: 89218a77-9e66-462b-8440-a21af3233e03
---

# Conditional Probability & Bayes' Theorem

Conditional probability is the probability of A, given that B happened.

## What conditional probability is
<!-- bite: 50ac3b06-aeb9-4e97-9364-db4411798d19 -->

Conditional probability — "the probability of A, *given that* B happened" — is the mathematical backbone of most classification. A spam classifier is, at its core, estimating `P(spam | this email's words)`: the probability of spam, given the specific evidence in front of it.

Next: how it is written, then Bayes' theorem, then a spam example.

## Conditional probability, notated
<!-- bite: 6d6822cb-51a7-446c-b794-a3dc518ccb80 -->

`P(A | B)` reads as "the probability of A, given B." It's different from `P(A)` (the plain, unconditional probability of A) whenever B changes what you know — `P(rain)` might be 20% in general, but `P(rain | dark clouds overhead)` is much higher, because the evidence shifts the estimate.

## Bayes' theorem — flipping a conditional probability around
<!-- bite: 51839ba0-d434-4250-a742-eab37c5c0c40 -->

Often you know `P(evidence | hypothesis)` (how likely some evidence would be, if a hypothesis were true) but actually want `P(hypothesis | evidence)` (given the evidence you actually observed, how likely is the hypothesis). Bayes' theorem is the formula for making that flip:

```text
P(A | B) = P(B | A) * P(A) / P(B)
```

In plain terms: **start with a prior belief about A, then update it based on how likely the evidence B would be if A were true, weighted against how likely B is overall.**

## Worked example — spam detection
<!-- bite: 416dbffc-0959-462f-be1d-7deb8a96ba0b -->

Say you want `P(spam | contains "free money")`:

- `P(spam)` — prior probability any email is spam, say 20% (from your training data).
- `P("free money" | spam)` — how often spam emails contain that phrase, say 30%.
- `P("free money")` — how often *any* email (spam or not) contains that phrase, say 8%.

```text
P(spam | "free money") = P("free money" | spam) * P(spam) / P("free money")
                        = 0.30 * 0.20 / 0.08
                        = 0.75
```

Seeing that phrase moves the estimate from a 20% prior probability of spam up to 75% — this exact update mechanism (start with a prior, update with evidence) is what **Naive Bayes classifiers** implement directly, and it's the same conceptual structure underlying any system that needs to reason under uncertainty from evidence.

## Why "naive"
<!-- bite: c8cdf10d-fe97-4177-afba-8be704e24de0 -->

Naive Bayes classifiers assume every piece of evidence (every word in an email, say) contributes to the probability *independently* of every other piece of evidence — which is rarely strictly true (word choices aren't really independent of each other) but works surprisingly well in practice despite the simplification, which is why the method carries "naive" in its name rather than being considered fundamentally flawed.

## Gotchas
<!-- bite: 1588ecfa-e141-4e62-854f-0a05098c69c8 -->

- Ignoring the **prior** (`P(A)`) is a common reasoning mistake outside of ML too — evidence that seems damning can still leave a low overall probability if the prior probability of the hypothesis was very low to begin with (a classic case: a rare disease with a fairly accurate test can still mean "positive test result" is more likely a false positive than an actual case, if the disease is rare enough).
- `P(A | B)` and `P(B | A)` are **not the same thing** and conflating them is a common error — "probability of spam given this phrase" and "probability of this phrase given spam" answer different questions, which is exactly why Bayes' theorem (a formula for converting between them) is needed at all.

## Check your understanding
<!-- bite: 2886226c-d5cf-43f6-ae26-5c4bee487dfa -->

Try each one before you open the answer.

1. <!-- q: exact id="50434c89" answer="0.75" accept="75%|75|3/4" tolerance="0.01" -->
   P(spam) = 0.2, P("free money" | spam) = 0.3 and P("free money") = 0.08. What is P(spam | "free money")?

   <details><summary>Answer</summary>

   0.75. Bayes: 0.3 × 0.2 ÷ 0.08 = 0.06 ÷ 0.08 = 0.75. Seeing the phrase moves the estimate from 20% up to 75%.

   </details>

2. <!-- q: gap id="a020ca04" answers="given" -->
   Fill in the gap. P(A | B) is read as "the probability of A, ___ B".

   <details><summary>Answer</summary>

   Given. It is the probability of A once you know B happened.

   </details>

3. <!-- q: mcq id="8159e51a" -->
   Are P(spam | phrase) and P(phrase | spam) the same?

   - [ ] Yes, the order doesn't matter
   - [x] No, they answer different questions

   <details><summary>Answer</summary>

   No. One is "how likely is spam, given the phrase" and the other is "how often does spam contain the phrase". Bayes' theorem converts one into the other.

   </details>

4. <!-- q: mcq id="d67adc30" -->
   Why is Naive Bayes called "naive"?

   - [ ] It ignores the prior
   - [x] It assumes every piece of evidence (every word) is independent of the others
   - [ ] It only works on tiny datasets

   <details><summary>Answer</summary>

   It assumes the evidence is independent. Words in an email aren't really independent, but the method still works surprisingly well.

   </details>

5. <!-- q: open id="120d5124" -->
   A disease is very rare, and a fairly accurate test comes back positive. Why might the person still most likely not have it?

   <details><summary>Answer</summary>

   Because of the prior. If the disease is rare enough, the few true cases are outnumbered by the false positives from all the healthy people tested. Ignoring the prior P(A) makes the evidence look stronger than it is.

   </details>

## Related
<!-- bite: 8480eb11-7084-450f-aad0-db50c85122b4 -->
- [[01-distributions|distributions]]
- [[02-expectation-and-variance|expectation-and-variance]]
