# Numerical Optimisation

**[Intermediate → Advanced]** — Finding a minimum. Where numerical methods and machine learning meet, and why conditioning explains most training pathologies.

## The problem

$$\min_{\mathbf{x}} f(\mathbf{x}) \qquad\text{possibly subject to } g(\mathbf{x}) \leq 0,\ h(\mathbf{x}) = 0$$

**At an unconstrained minimum, $\nabla f = 0$** — so **optimisation is [[foundations/numerical-methods/03-root-finding|root-finding]] on the gradient**, with the extra requirement that you want a *minimum* rather than any stationary point.

**The second-order condition distinguishes them:** the Hessian $H = \nabla^2 f$ is positive definite at a minimum, negative definite at a maximum, indefinite at a **saddle point.**

## Gradient descent

$$\mathbf{x}_{k+1} = \mathbf{x}_k - \alpha\nabla f(\mathbf{x}_k)$$

**Step downhill.** First-order, cheap per step, and **linearly convergent** — which is slow.

**The convergence rate depends on conditioning:**

$$\text{rate} \propto \left(\frac{\kappa - 1}{\kappa + 1}\right)^2, \qquad \kappa = \frac{\lambda_{max}}{\lambda_{min}} \text{ of the Hessian}$$

> **This one formula explains most of what goes wrong in training.**
>
> **$\kappa = 1$** (perfectly spherical bowl) → converges in one step.
> **$\kappa = 1000$** → the classic **zigzag** down a narrow valley, taking thousands of steps.
>
> ```
>    ╭─────────────╮       ill-conditioned valley:
>   ╱  ↘         ╱          steps bounce across the walls
>  │     ↗↘    ╱             and creep along the floor
>   ╲      ↗ ╱
>    ╰──────╯
> ```
>
> **Slow convergence is usually a conditioning problem, not a learning-rate problem** — and no learning rate fixes it, because the same $\alpha$ is too large across the valley and too small along it. → [[foundations/numerical-methods/01-why-numerical-methods|Conditioning]]

**Which is why feature scaling matters so much in ML.** Features on wildly different scales produce a badly-conditioned Hessian directly. **Normalising inputs is a conditioning fix**, and it's why it's the first preprocessing step everyone is told to do without always being told why. → [[ai-ml/02-ml-engineer/02-working-with-data/README|Working with Data]]

**Momentum** damps the zigzag by averaging recent directions:

$$\mathbf{v}_{k+1} = \beta\mathbf{v}_k - \alpha\nabla f, \qquad \mathbf{x}_{k+1} = \mathbf{x}_k + \mathbf{v}_{k+1}$$

**Nesterov's accelerated gradient** improves the rate from $O(1/k)$ to $O(1/k^2)$ for convex problems — **provably optimal** for first-order methods.

## Line search and trust regions

**Choosing $\alpha$ is the practical difficulty.** Too large diverges; too small crawls.

**Line search** — pick the direction, then search for a good step length along it.

**The Wolfe conditions** are what "good" means: sufficient decrease (Armijo) plus sufficient curvature reduction. **Backtracking line search** — start with $\alpha=1$, halve until Armijo is satisfied — is five lines and dramatically more robust than a fixed step.

**Trust region** — the dual approach. Fix a radius you trust the local model within, minimise the model inside it, then **grow or shrink the radius based on how well the model predicted the actual decrease.**

> **Trust regions handle non-convexity and negative curvature more gracefully than line search**, because they never take an unboundedly large step toward a saddle. **Levenberg–Marquardt is a trust-region method**, and it's the same damping as [[robotics/07-jacobians-and-singularities|damped least squares]] — three fields, one idea.

## Newton and quasi-Newton

**Newton's method** uses curvature:

$$H\Delta\mathbf{x} = -\nabla f, \qquad \mathbf{x}_{k+1} = \mathbf{x}_k + \Delta\mathbf{x}$$

**Quadratic convergence**, and **it's invariant to linear rescaling** — so the conditioning problem above disappears entirely. Newton doesn't care about your feature scaling.

**The costs:**

**Computing $H$ is $O(n^2)$ entries**; solving is $O(n^3)$. **Impossible for a neural network with $10^9$ parameters.**

**$H$ may be indefinite** away from a minimum, in which case the Newton step heads toward a saddle. **Fixes:** modify $H$ to be positive definite, or use a trust region.

**Quasi-Newton — build up an approximation to $H^{-1}$ from gradients.**

**BFGS** is the standard, and it's excellent for smooth medium-scale problems ($n$ up to thousands). **L-BFGS** stores only the last $m$ updates (typically 5–20) instead of a full matrix — **$O(mn)$ memory**, which makes it viable for large problems.

> **L-BFGS is the default for medium-scale smooth optimisation** and it's what `scipy.optimize.minimize` uses when you don't specify. **It's also why it's *not* used for deep learning** — it needs accurate gradients, and stochastic minibatch gradients are too noisy for the curvature estimate to be meaningful.

## Stochastic methods

**When $f$ is a sum over millions of data points**, computing the full gradient per step is wasteful.

$$f(\mathbf{x}) = \frac{1}{N}\sum_{i=1}^N f_i(\mathbf{x}) \qquad\Longrightarrow\qquad \nabla f \approx \frac{1}{|B|}\sum_{i\in B}\nabla f_i$$

**SGD uses a minibatch estimate.** Noisy, and **vastly cheaper per step** — and progress per unit computation is far better.

**The noise is not purely a cost.** It helps escape saddle points, which dominate high-dimensional non-convex landscapes, and it acts as implicit regularisation.

**The adaptive family:**

**AdaGrad** — per-parameter learning rates scaled by accumulated squared gradients. **The rate decays monotonically and eventually stalls.**

**RMSProp** — exponential moving average instead of a sum, which fixes the stalling.

**Adam** — RMSProp plus momentum, with bias correction. **The default in deep learning**, and it works well enough that most people never change it.

**The honest caveat:** Adam sometimes generalises worse than well-tuned SGD with momentum, and **AdamW** (decoupled weight decay) fixes a genuine bug in how Adam interacts with L2 regularisation. → [[ai-ml/02-ml-engineer/05-deep-learning/README|Deep Learning]]

**Learning rate schedules** — warmup, cosine decay, step decay. **Often worth more than the choice of optimiser**, and consistently underrated.

## Constrained optimisation

**KKT conditions** generalise "gradient is zero" to constrained problems — the gradient of the objective must be a combination of the constraint gradients, with sign conditions on the multipliers.

**The methods:**

**Penalty methods** — add $\mu\|g(\mathbf{x})\|^2$ to the objective. Simple, and **the problem becomes ill-conditioned as $\mu\to\infty$**, which is the classic failure.

**Augmented Lagrangian** — penalty plus explicit multiplier estimates. **Converges without $\mu\to\infty$**, so no conditioning blowup. Much better.

**Interior point / barrier** — add $-\mu\sum\log(-g_i)$ to keep iterates strictly feasible, and reduce $\mu$. **The method behind modern LP and convex solvers**, and it's what made large-scale linear programming practical.

**SQP** — solve a sequence of quadratic subproblems. **Excellent for smooth nonlinear constrained problems**, and what `scipy`'s `SLSQP` implements.

**Projection** — for simple constraints (bounds, a ball, a simplex), just project back after each step. **Cheap and effective when the projection is easy.**

## Convexity

**The dividing line between "solved" and "hard".**

> **For a convex problem, every local minimum is the global minimum.** Gradient methods find *the* answer, and you can certify optimality via the duality gap.
>
> **For a non-convex problem, you find *a* local minimum and cannot generally know how good it is.**

**Convex problems:** least squares, linear and quadratic programming, logistic regression, SVMs, LASSO, semidefinite programming. **Use a convex solver** (CVXPY, Mosek, ECOS) rather than a general one — it exploits the structure and gives you a certificate.

**Non-convex:** neural networks, most inverse problems, anything combinatorial.

**The empirical result that made deep learning work:** in very high dimensions, **most critical points are saddle points, not bad local minima**, and the local minima that exist tend to have similar loss. **So "stuck in a local minimum" is largely the wrong mental model for neural network training** — the difficulty is saddle points and ill-conditioning, which is why momentum and adaptive methods help.

## Global optimisation

**When you need the global optimum of a non-convex function**, and there's no free lunch here.

**Multi-start** — run a local method from many starting points. **Embarrassingly parallel, and the honest baseline.**

**Simulated annealing** — accept uphill moves with a probability that decreases over time.

**Genetic / evolutionary algorithms** — population-based. Popular, and **frequently outperformed by well-implemented local methods with restarts.**

**Bayesian optimisation** — build a probabilistic surrogate (usually a Gaussian process) and sample where the expected improvement is highest. **The right tool when each evaluation is expensive** — hyperparameter tuning, physical experiments, simulation-based design. → [[ai-ml/02-ml-engineer/04-model-evaluation/README|Model Evaluation]]

**Branch and bound** — for problems with structure that permits pruning. The only family that **proves** global optimality.

> **Be sceptical of metaheuristics.** The literature is full of nature-inspired variants with weak baselines. **Compare against multi-start L-BFGS before believing a new algorithm is better** — it very often isn't.

## Practical notes

**Scale your variables.** The highest-value single action, and it's the conditioning fix. → [[foundations/numerical-methods/02-floating-point-and-error|Scaling]]

**Provide analytic gradients** if you can, or use automatic differentiation. **Finite-difference gradients are $n+1$ function evaluations and inherit the [[foundations/numerical-methods/07-numerical-integration|differentiation error floor]]** — accurate to about $\sqrt{\epsilon}$ at best.

**Check your gradient.** Compare against finite differences on a random point. **A gradient bug is the most common cause of an optimiser that mysteriously won't converge**, and this check takes two minutes.

**Exploit structure.** Least squares → use `least_squares` (Levenberg–Marquardt), not a general minimiser. Convex → use a convex solver. Sparse → say so.

**Set sensible convergence criteria** — gradient norm, step size, and function change, with relative tolerances.

**Try several starting points** for non-convex problems, and report the spread rather than the best.

**Watch for the optimiser exploiting a bug.** If the objective goes far below what's physically possible, **you have a bug in the objective, not a great result.** Optimisers are extremely good at finding them.

---

## Related
- [[ai-ml/00-foundations/03-mathematics/04-optimization|ML Optimisation]] — the same subject from the ML side
- [[foundations/numerical-methods/03-root-finding|Root Finding]] — minimisation is root-finding on the gradient
- [[foundations/numerical-methods/04-linear-systems|Linear Systems]] — solved inside every Newton step
- [[foundations/numerical-methods/README|Numerical methods map]]
