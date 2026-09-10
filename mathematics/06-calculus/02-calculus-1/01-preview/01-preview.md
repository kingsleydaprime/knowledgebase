# Calculus — A Preview

**[Beginner → Intermediate]** — What calculus is actually about, before any of the machinery. Two questions, one idea underneath both.

## Before you start

- You can manipulate algebraic expressions — [[03-algebraic-manipulation|algebraic manipulation]].
- You can read a graph and find the gradient of a straight line.
- You know what a function is — [[01-sets|sets]].

**What you will be able to do after this lesson:**

1. State the two central problems of calculus and say why each is hard.
2. Explain why the gradient of a curve is not defined the way a line's is.
3. Explain what a limit is informally, and why both problems need one.
4. Say what the Fundamental Theorem of Calculus claims, before being able to prove it.

---

## 1. Two questions that look unrelated

**The tangent problem.** How steep is a curve *at a single point*?

For a straight line this is easy: pick two points, divide the rise by the run. The answer is the same wherever you pick them.

For a curve it is not easy, and the reason is worth sitting with. **Steepness is a property of two points** — it is a ratio of change. **A single point has no change.** Asking for the gradient "at a point" is asking for $\frac{0}{0}$, which is not a number.

```
   y                      the gradient at P:
   |        ,-'              rise / run  needs TWO points
   |      ,'                 but we want ONE
   |    ,'  P
   |  ,'
   |,'
   +------------ x
```

**The area problem.** What is the area under a curve?

For a rectangle, area is base times height. For a curve, the "height" changes continuously, so there is no single height to multiply by.

**Both problems fail for the same reason:** the quantity you want to divide by, or multiply by, is not constant. Calculus is the machinery for handling exactly that.

---

## 2. The idea underneath both: approximate, then refine

**The tangent problem.** You cannot use one point, so use two — one at $P$ and one nearby. That gives a *secant* line, whose gradient is close but wrong. Then slide the second point towards $P$ and watch what the gradient approaches.

```
   secant through P and a nearby point:   gradient is close
   slide the point closer:                gradient is closer
   ...                                    approaches a value
```

**The area problem.** You cannot use one rectangle, so use many thin ones. Their total is close but wrong. Then make them thinner and watch what the total approaches.

**In both cases the answer is not computed directly. It is approached.** That approaching is called a **limit**, and it is the single idea calculus is built on. Everything else — derivatives, integrals, all the rules — is a consequence.

> [!NOTE]
> **This is why limits come first and feel unmotivated.** They are the foundation, so they are taught before the buildings that stand on them.
>
> If limits feel like pointless formalism, come back to this page. **A limit is how you answer a question whose direct calculation gives $\frac{0}{0}$ or an infinite sum** — and both of calculus's central questions do exactly that.

---

## 3. The two halves, named

| | Question | Answer | Notation |
| :--- | :--- | :--- | :--- |
| **Differential calculus** | How fast is this changing *right now*? | the **derivative** | $\frac{dy}{dx}$, $f'(x)$ |
| **Integral calculus** | How much has accumulated *in total*? | the **integral** | $\int f(x)\,dx$ |

**Differentiation** takes a quantity and gives its rate of change. Position → velocity. Velocity → acceleration.

**Integration** takes a rate and gives the accumulated total. Velocity → distance travelled. Flow rate → volume delivered.

## 4. The result that ties them together

Those two operations look like different subjects. They are not.

**The Fundamental Theorem of Calculus:** differentiation and integration are **inverse operations**. Accumulate a rate of change and you recover the original quantity; take the rate of change of an accumulation and you recover the rate.

$$\frac{d}{dx}\int_a^x f(t)\,dt = f(x)$$

**Read it in words:** if you accumulate $f$ from $a$ up to $x$, and then ask how fast that accumulation is growing at $x$, the answer is $f(x)$ itself — because $f(x)$ is precisely the rate at which you are currently accumulating.

**This is the central result of the subject**, and it is why finding areas — which sounds geometric and hard — reduces to reversing differentiation, which is largely mechanical.

---

## 5. Where you already rely on it

- **Physics.** Velocity is the derivative of position; acceleration of velocity. Every equation of motion is calculus.
- **Machine learning.** Training a model means minimising a loss function, and you minimise by following its **gradient** downhill. Backpropagation is the chain rule applied systematically — see [[ai-ml/index|ai-ml]].
- **Signal processing.** Fourier analysis is built on integrals — see [[digital-signal-processing/index|DSP]].
- **Probability.** A continuous distribution's probability is the *area* under its density curve; the total is an integral equal to 1.
- **Anything with "rate" or "total" in it.** Interest, growth, decay, flow, dosage, throughput.

## 6. What this course does and does not assume

**Assumes:** algebra, functions, graphs.

**Does not assume:** any prior calculus.

**A warning worth taking seriously:** calculus is where mathematics stops being a set of procedures to apply and starts being a structure to understand. You can pass exams by memorising rules. You cannot use it that way. **Every rule in this course is derived, and the derivations are the content.**

## Before moving on

- [ ] State the tangent problem and say why a single point has no gradient.
- [ ] State the area problem and say why one rectangle is not enough.
- [ ] Explain what "approach a limit" means informally.
- [ ] State what the Fundamental Theorem of Calculus claims.

**Recap:** Calculus answers two questions that classical algebra cannot: the exact steepness of a curve at a point, and the exact area under one. Both fail directly — one gives $\frac{0}{0}$, the other an infinite sum — and both are solved the same way: approximate with something you *can* compute, then refine and see what the answer approaches. That approaching is a limit, and it is the foundation of everything that follows. Differentiation and integration turn out to be inverses of each other, which is the Fundamental Theorem.

**Next:** [[01-definition|The Limit of a Function]] — the idea both halves depend on, made precise.

## Related

- [[mathematics/index|Mathematics index]]
- [[ai-ml/index|ai-ml]] — where derivatives do the most work
