# Partial Derivatives

**[Intermediate → Advanced]** — Differentiation when a function has several inputs. The idea behind every gradient in machine learning.

## Before you start

- You can differentiate fluently, especially the chain rule — [[01-rules|derivative rules]].
- You know what a function of one variable is — [[01-variables|variables]].

**What you will be able to do after this lesson:**

1. Compute a partial derivative and say precisely what it measures.
2. Explain what the gradient vector is and why it points uphill.
3. Apply the multivariable chain rule.
4. Explain why gradient descent works, in terms of the gradient's direction.

---

## 1. Several inputs, one output

$$f(x,y) = x^2 + 3xy + y^2$$

**This describes a surface**, not a curve — a height above every point of the $xy$-plane.

**"How steep is it?" is now ambiguous.** Steep in which direction? Walking east may be uphill while walking north is downhill.

**So the question must be made specific.** A partial derivative answers it for one axis at a time.

## 2. The definition

$$\frac{\partial f}{\partial x} = \lim_{h\to0}\frac{f(x+h, y) - f(x,y)}{h}$$

**Note that $y$ does not change.** The partial derivative with respect to $x$ measures the rate of change *as $x$ varies and everything else is held fixed*.

**Which makes it trivially easy to compute: treat every other variable as a constant and differentiate normally.**

For $f(x,y) = x^2 + 3xy + y^2$:

$$\frac{\partial f}{\partial x} = 2x + 3y \qquad\qquad \frac{\partial f}{\partial y} = 3x + 2y$$

In the first, $3xy$ differentiates to $3y$ because $y$ is a constant multiplier, and $y^2$ differentiates to zero because it contains no $x$ at all.

**The symbol $\partial$ ("del") rather than $d$ signals that other variables exist and are being held still.**

```
   the surface z = f(x,y)

   ∂f/∂x  = the slope of the slice taken parallel to the x-axis
   ∂f/∂y  = the slope of the slice taken parallel to the y-axis

   each partial derivative is an ORDINARY derivative
   of a one-variable slice through the surface
```

## 3. The gradient

**Collect the partials into a vector:**

$$\nabla f = \left(\frac{\partial f}{\partial x},\ \frac{\partial f}{\partial y}\right)$$

**Two facts make this the central object of the subject:**

1. **$\nabla f$ points in the direction of steepest increase.**
2. **Its magnitude $|\nabla f|$ is how steep that steepest direction is.**

**Why direction 1 is true, informally:** moving a small step $(\Delta x, \Delta y)$ changes $f$ by approximately $\frac{\partial f}{\partial x}\Delta x + \frac{\partial f}{\partial y}\Delta y$ — a dot product of the gradient with your step. A dot product is largest when the two vectors point the same way, so **the step that increases $f$ most is the one aligned with $\nabla f$**.

**Example:** for $f = x^2+3xy+y^2$ at $(1,2)$:

$$\nabla f = (2(1)+3(2),\ 3(1)+2(2)) = (8, 7)$$

Steepest ascent from that point is in direction $(8,7)$, and the steepest slope is $\sqrt{64+49} \approx 10.6$.

## 4. Why this is the foundation of machine learning

**Training a model means minimising a loss function with respect to millions of parameters.**

$$L(w_1, w_2, \ldots, w_n)$$

**The gradient points uphill, so $-\nabla L$ points downhill** — the direction that reduces the loss fastest. That gives the entire algorithm:

$$w \leftarrow w - \eta\,\nabla L(w)$$

**Take a small step against the gradient, recompute, repeat.** That is gradient descent, and $\eta$ is the learning rate — how far to step.

> [!NOTE]
> **Two things follow immediately from this being a *local* rule.**
>
> **It can get stuck.** The gradient only knows the slope where you are standing. In a local minimum every direction is uphill, so the rule stops — even though a deeper valley may exist elsewhere.
>
> **The step size matters enormously.** Too small and training crawls; too large and you overshoot the valley and may diverge. Everything about learning-rate schedules, momentum and adaptive optimisers exists to manage that one tension.
>
> See [[foundations/ai-ml/index|ai-ml]], and [[build-your-own-shit/10-your-own-neural-network|build your own neural network]] where you compute these gradients by hand.

## 5. Higher-order and mixed partials

Differentiate twice:

$$\frac{\partial^2 f}{\partial x^2}, \qquad \frac{\partial^2 f}{\partial y^2}, \qquad \frac{\partial^2 f}{\partial x\,\partial y}$$

**Clairaut's theorem:** for a well-behaved function, the mixed partials are equal:

$$\frac{\partial^2 f}{\partial x\,\partial y} = \frac{\partial^2 f}{\partial y\,\partial x}$$

**The order of differentiation does not matter.** That is a genuinely surprising result — there is no obvious reason changing $x$ then $y$ should match changing $y$ then $x$ — and it fails for pathological functions, which is what "well-behaved" is doing in the statement.

## 6. The multivariable chain rule

If $z = f(x,y)$ and both $x$ and $y$ depend on $t$:

$$\frac{dz}{dt} = \frac{\partial f}{\partial x}\frac{dx}{dt} + \frac{\partial f}{\partial y}\frac{dy}{dt}$$

**Read it as: total change is the sum of the contributions through each path.** $t$ influences $z$ via $x$ and also via $y$, so both routes contribute and they add.

**This is exactly backpropagation.** In a network, a weight influences the loss through every downstream path, and the total gradient is the sum over all of them. **The single-variable chain rule multiplies along a path; the multivariable one adds across paths** — and a neural network needs both.

## 7. Practice — problems

1. Find both partials: (a) $f = 3x^2y + y^3$  (b) $f = e^{xy}$  (c) $f = \frac{x}{y}$.
2. Find $\nabla f$ for $f = x^2 + y^2$ at $(3,4)$. What is the steepest slope there, and in which direction?
3. **Explain** why $\nabla f = (0,0)$ at a maximum, a minimum *and* a saddle point — and what extra information distinguishes them.
4. Verify Clairaut's theorem for $f = x^3y^2$ by computing both mixed partials.
5. For $z = x^2 + y^2$ with $x = \cos t$, $y = \sin t$, find $\frac{dz}{dt}$ using the chain rule. **Then explain the answer geometrically.**
6. **Gradient descent by hand.** Minimise $f(x) = x^2$ starting at $x_0 = 4$ with $\eta = 0.1$. Compute three steps. What happens if $\eta = 1.1$ instead?

<details><summary>Answers — open only after an attempt</summary>

1. (a) $f_x = 6xy$, $f_y = 3x^2+3y^2$. (b) $f_x = ye^{xy}$, $f_y = xe^{xy}$. (c) $f_x = \frac1y$, $f_y = -\frac{x}{y^2}$.
2. $\nabla f = (2x, 2y) = (6,8)$. Steepest slope $= \sqrt{36+64} = 10$, in the direction $(6,8)$ — which points directly away from the origin, as expected for a bowl.
3. All three are <strong>stationary points</strong>: the surface is locally flat, so every partial is zero. The gradient alone cannot tell them apart. The <strong>second derivatives</strong> distinguish them — a saddle curves up in one direction and down in another, which the Hessian matrix captures.
4. $f_x = 3x^2y^2 \Rightarrow f_{xy} = 6x^2y$. $f_y = 2x^3y \Rightarrow f_{yx} = 6x^2y$. Equal ✓
5. $\frac{dz}{dt} = 2x(-\sin t) + 2y(\cos t) = -2\cos t\sin t + 2\sin t\cos t = \mathbf{0}$. Geometrically: $x^2+y^2 = 1$ on the unit circle, so $z$ is <strong>constant</strong> — you are walking along a contour line, and moving along a contour changes nothing.
6. $f'(x) = 2x$. Steps: $x_1 = 4 - 0.1(8) = 3.2$; $x_2 = 3.2 - 0.1(6.4) = 2.56$; $x_3 = 2.048$ — converging towards 0. With $\eta = 1.1$: $x_1 = 4 - 1.1(8) = -4.8$, then $x_2 = -4.8 + 1.1(9.6) = 5.76$ — <strong>oscillating and growing</strong>. The steps overshoot the minimum by more than they started from, so it diverges.
</details>

## Before moving on

- [ ] Compute partial derivatives and say what is held constant.
- [ ] Explain what the gradient is and why it points uphill.
- [ ] Apply the multivariable chain rule and explain the summation across paths.
- [ ] Explain gradient descent, and both ways it can fail.

**Recap:** A partial derivative measures the rate of change along one axis with all other variables held fixed, so it is computed by treating them as constants. Collecting the partials gives the gradient, which points in the direction of steepest increase with magnitude equal to that steepness — which is why stepping against it minimises a function, and why gradient descent is the algorithm behind model training. The multivariable chain rule adds contributions across paths, and applying it through a deep composition is backpropagation.

**Next:** [[02-multiple-integrals|Multiple Integrals]] — accumulation over a region rather than an interval.

## Related

- [[01-rules|Derivative rules]] · [[01-related-rates|Applications of the derivative]]
- [[foundations/ai-ml/index|ai-ml]] · [[build-your-own-shit/10-your-own-neural-network|Build your own neural network]]
