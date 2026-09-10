# Multivariable Optimisation

**[Advanced]** — Finding maxima and minima of a surface, distinguishing them from saddle points, and optimising subject to a constraint.

## Before you start

- You can compute partial derivatives and the gradient — [[01-partial-derivatives|partial derivatives]].
- You can classify critical points in one variable — [[01-related-rates|applications of the derivative]].

**What you will be able to do after this lesson:**

1. Find critical points of a function of two variables.
2. Classify them using the second derivative test, including saddle points.
3. Use Lagrange multipliers for constrained optimisation.
4. Explain why saddle points matter more than local minima in high dimensions.

---

## 1. Critical points

**At an interior extremum the surface is level in every direction**, so every partial derivative vanishes:

$$\nabla f = \left(\frac{\partial f}{\partial x}, \frac{\partial f}{\partial y}\right) = (0, 0)$$

**Example:** $f(x,y) = x^2 + y^2 - 4x - 6y + 13$.

$$f_x = 2x - 4 = 0 \Rightarrow x = 2 \qquad f_y = 2y - 6 = 0 \Rightarrow y = 3$$

One critical point, at $(2,3)$.

**But as in one variable, a critical point need not be an extremum** — and in two variables there is a new possibility that has no one-dimensional analogue.

## 2. The saddle point

$$f(x,y) = x^2 - y^2$$

At the origin both partials vanish. But along the $x$-axis the surface curves **up**, and along the $y$-axis it curves **down**.

```
   a saddle: minimum in one direction,
             maximum in another

        \         /
         \.     ./
          \`._.'/          along x: a valley
           `._.'           along y: a ridge
          ./   \.
         /       \
```

**It is a minimum and a maximum at the same time, in different directions** — hence the name, from the shape of a horse's saddle. There is nothing like this in one variable, where a critical point is a max, a min, or a flat inflection.

## 3. The second derivative test

Compute the **discriminant**:

$$D = f_{xx}f_{yy} - (f_{xy})^2$$

| Condition | Conclusion |
| :--- | :--- |
| $D > 0$ and $f_{xx} > 0$ | **local minimum** |
| $D > 0$ and $f_{xx} < 0$ | **local maximum** |
| $D < 0$ | **saddle point** |
| $D = 0$ | **inconclusive** — investigate directly |

**What $D$ is measuring:** it is the determinant of the **Hessian**, the matrix of second partials

$$H = \begin{pmatrix} f_{xx} & f_{xy} \\ f_{xy} & f_{yy}\end{pmatrix}$$

**A negative determinant means the curvatures have opposite signs** — up one way, down the other — which is exactly a saddle. That is why the test works, and why it generalises to $n$ dimensions via the eigenvalues of $H$.

**Applied to $f = x^2 - y^2$:** $f_{xx}=2$, $f_{yy}=-2$, $f_{xy}=0$, so $D = -4 < 0$ — a saddle ✓

> [!NOTE]
> **In high dimensions, saddle points dominate.**
>
> For a critical point of a function of $n$ variables to be a true minimum, the surface must curve upward in **all $n$ directions** at once. If curvature directions were roughly independent, that is like requiring $n$ coin flips to all come up heads — vanishingly unlikely for large $n$.
>
> **So in a neural network with millions of parameters, almost every critical point is a saddle, not a local minimum.** This reversed a long-standing belief: training was assumed to get trapped in bad local minima, and the actual difficulty is escaping the flat regions around saddles — which is why momentum and stochastic noise help so much. See [[ai-ml/index|ai-ml]].

## 4. Constrained optimisation and Lagrange multipliers

**Often you must optimise subject to a restriction.** Maximise area given a fixed perimeter; minimise cost given a required output.

$$\text{optimise } f(x,y) \quad\text{subject to}\quad g(x,y) = c$$

**The insight:** at the constrained optimum, the contour of $f$ is **tangent** to the constraint curve.

**Why:** if they crossed rather than touched, you could slide along the constraint and move to a higher contour — so you would not be at the optimum. **Tangency means their gradients are parallel:**

$$\nabla f = \lambda \nabla g$$

**$\lambda$ is the Lagrange multiplier.** Solve that vector equation together with the constraint.

### Worked example

**Maximise $f = xy$ subject to $x + y = 10$.**

$$\nabla f = (y, x) \qquad \nabla g = (1,1)$$

$$y = \lambda, \quad x = \lambda \quad\Rightarrow\quad x = y$$

With the constraint $x + y = 10$: $x = y = 5$, giving a maximum product of **25**.

**The general result** — for a fixed sum, the product is largest when the parts are equal — falls straight out, and is more valuable than the number.

**$\lambda$ also has a meaning:** it is the rate at which the optimal value would improve if the constraint were relaxed. In economics that is the *shadow price* — what one more unit of the constrained resource is worth.

## 5. Practice — problems

1. Find and classify the critical points of $f = x^2 + y^2 - 4x - 6y + 13$.
2. Find and classify the critical points of $f = x^3 - 3xy + y^3$.
3. Show that $f = x^2 - y^2$ has a saddle at the origin, using the discriminant.
4. Use Lagrange multipliers to find the rectangle of maximum area with perimeter 20.
5. Minimise $f = x^2+y^2$ subject to $x + 2y = 5$. **Interpret the answer geometrically.**
6. **Explain** why a random critical point of a 1,000,000-parameter function is almost certainly a saddle, in one sentence about curvature directions.

<details><summary>Answers — open only after an attempt</summary>

1. Critical point $(2,3)$. $f_{xx}=2$, $f_{yy}=2$, $f_{xy}=0$, so $D = 4 > 0$ and $f_{xx} > 0$ → <strong>local minimum</strong>, value $f(2,3) = 0$.
2. $f_x = 3x^2-3y = 0$ and $f_y = -3x+3y^2 = 0$ give $y = x^2$ and $x = y^2$, so $x = x^4$, giving $x = 0$ or $x=1$. Points $(0,0)$ and $(1,1)$. $f_{xx}=6x$, $f_{yy}=6y$, $f_{xy}=-3$. At $(0,0)$: $D = 0 - 9 = -9 < 0$ → <strong>saddle</strong>. At $(1,1)$: $D = 36-9 = 27 > 0$ with $f_{xx}=6>0$ → <strong>local minimum</strong>.
3. $f_{xx}=2$, $f_{yy}=-2$, $f_{xy}=0$, so $D = -4 < 0$ → saddle ✓
4. Maximise $xy$ subject to $2x+2y=20$, i.e. $x+y=10$ — the same problem as the worked example. $x=y=5$: a <strong>square</strong> of area 25. The general result is that the optimal rectangle for a fixed perimeter is always a square.
5. $\nabla f = (2x,2y) = \lambda(1,2)$, so $2x = \lambda$ and $2y = 2\lambda$, giving $y = 2x$. With $x+2y=5$: $x=1$, $y=2$, minimum value 5. <strong>Geometrically:</strong> this is the closest point on the line to the origin, and the line from the origin to $(1,2)$ is perpendicular to the constraint — which is exactly what $\nabla f \parallel \nabla g$ says.
6. Because being a minimum requires upward curvature in <em>all</em> 1,000,000 directions simultaneously, and any single downward direction makes it a saddle — so minima are exponentially rare among critical points.
</details>

## Before moving on

- [ ] Find critical points by setting the gradient to zero.
- [ ] Classify them with the discriminant, including saddles.
- [ ] Explain what a saddle point is and why one variable has no analogue.
- [ ] Use Lagrange multipliers and explain the tangency argument.

**Recap:** Critical points of a multivariable function occur where the gradient vanishes, but in two or more variables a new possibility appears — the saddle, which is a minimum in one direction and a maximum in another. The discriminant, which is the determinant of the Hessian, distinguishes the cases, and a negative value means opposite curvatures. In high dimensions saddles vastly outnumber minima, which reshaped how neural network training is understood. Constrained optimisation uses Lagrange multipliers, resting on the observation that at the optimum the objective's contour is tangent to the constraint.

**This is the end of Calculus 3, and of the calculus sequence.**

## Related

- [[01-partial-derivatives|Partial derivatives]] · [[02-multiple-integrals|Multiple integrals]]
- [[ai-ml/index|ai-ml]] — where saddle points became a practical concern
- [[mathematics/index|Mathematics index]]
