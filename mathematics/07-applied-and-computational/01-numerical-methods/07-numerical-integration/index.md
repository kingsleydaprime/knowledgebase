# Numerical Integration

**Working out an area when you cannot do the integral by hand** — which is the normal case, not the exception.

## Reading order

1. [[01-riemann-sums|Riemann Sums]] — **[Beginner]** — how a continuous integral becomes a finite sum you can actually loop over: step width, sample points, and the left, right, midpoint and trapezoidal rules
2. [[02-quadrature-rules|Quadrature Rules]] — **[Intermediate]** — Newton–Cotes and Simpson's rules, Gaussian quadrature, adaptive methods and Monte Carlo

## The methods, at a glance

| Rule | Where it samples | Error shrinks like |
| :--- | :--- | :--- |
| Left / right rectangle | one end of each strip | $O(h)$ |
| Midpoint | the centre of each strip | $O(h^2)$ |
| Trapezoidal | average of both ends | $O(h^2)$ |
| Simpson's 1/3 | a parabola through three points | $O(h^4)$ |
| Simpson's 3/8 | a cubic through four points | $O(h^4)$ |
| Gauss–Legendre | points chosen to be optimal | exact for degree $2n-1$ |

Lesson 1 covers the first three rows and explains why the choice of sample point is the whole story. Lesson 2 covers the rest.

## Related

- [[index|numerical-methods/]] — the parent course
- [[03-calculus-2/01-integration-by-parts|Integration]] — where the limit definition comes from
- [[08-ordinary-differential-equations|ODE solvers]] — each step of which is an integration
