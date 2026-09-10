# The Precise Definition of a Limit

**[Advanced]** — Making "arbitrarily close" mean something exact. The definition that turned calculus from a working technique into rigorous mathematics.

## Before you start

- You are comfortable with limits informally — [[01-definition|the limit of a function]], [[01-laws|limit laws]].
- You can manipulate inequalities and absolute values.

**What you will be able to do after this lesson:**

1. State the $\varepsilon$–$\delta$ definition and read each quantifier correctly.
2. Explain why "gets close to" is not good enough as a definition.
3. Prove a simple limit from the definition.
4. Explain why this definition was needed historically.

> **This lesson is harder than the ones around it, and you can build on the rest of calculus without it.** Read it for why the subject is trustworthy rather than to acquire a technique.

---

## 1. Why the informal definition is not enough

"$f(x)$ gets close to $L$ as $x$ gets close to $a$."

**How close? Close enough for what?**

Consider $f(x) = \frac{1}{x}$ near $x = 0$. As $x$ gets close to 0, $f(x)$ gets close to... a million? It does pass near a million. It also passes near a billion. **"Gets close to" is satisfied by many values, so it cannot pick one out.**

Calculus worked for 150 years on this vague footing — Newton and Leibniz both used "infinitesimals", quantities that were somehow non-zero when you divided by them and zero when you added them. **Berkeley mocked them in 1734 as "the ghosts of departed quantities"**, and he was right that nobody could say what they were.

**Cauchy and Weierstrass fixed it in the 1800s** by replacing "infinitely small" with a definition using only ordinary numbers and inequalities. That definition is below.

## 2. The definition

$$\lim_{x\to a} f(x) = L$$

means:

> **For every** $\varepsilon > 0$, **there exists** a $\delta > 0$ such that **whenever** $0 < |x - a| < \delta$, it follows that $|f(x) - L| < \varepsilon$.

**Read it as a game**, which is genuinely the best way to understand it:

- **A challenger picks $\varepsilon$** — a tolerance. "Can you get $f(x)$ within $0.001$ of $L$?"
- **You must respond with $\delta$** — a neighbourhood. "Yes: keep $x$ within $\delta$ of $a$ and I guarantee it."
- **You win if you can answer *every* challenge**, no matter how small the tolerance.

**The limit is $L$ exactly when you have a winning strategy** — a way of producing a suitable $\delta$ for any $\varepsilon$ handed to you.

**The order of the quantifiers is everything.** $\varepsilon$ comes first and $\delta$ is chosen in response, so $\delta$ is allowed to depend on $\varepsilon$. Swapping them would demand one $\delta$ that works for all tolerances, which is a completely different and usually false claim.

**And note $0 < |x-a|$** — the strict inequality excludes $x = a$ itself, which is the formal version of the exclusion from [[01-definition|the first limits lesson]].

## 3. What the symbols mean geometrically

```
   f(x)
     |          .-'
   L+ε |- - - - - - - - -
     |        ,'
   L |- - - -o
     |      ,'
   L-ε |- -'- - - - - - -
     |    ,'
     +----+----+-----------  x
        a-δ  a  a+δ

   the challenger fixes a horizontal band of half-height ε
   you must find a vertical strip of half-width δ
   such that the graph stays inside the band throughout the strip
```

**Narrower band → you generally need a narrower strip.** That dependence is the whole content.

## 4. A proof from the definition

**Claim:** $\lim_{x\to 3}(2x + 1) = 7$.

**Scratch work — find $\delta$ first, then write the proof forwards.** We need $|(2x+1) - 7| < \varepsilon$:

$$|2x - 6| < \varepsilon \quad\Longleftrightarrow\quad 2|x - 3| < \varepsilon \quad\Longleftrightarrow\quad |x-3| < \frac{\varepsilon}{2}$$

So $\delta = \frac{\varepsilon}{2}$ will work.

**The proof.** Let $\varepsilon > 0$ be given. Choose $\delta = \frac{\varepsilon}{2}$. Then whenever $0 < |x - 3| < \delta$:

$$|(2x+1) - 7| = |2x-6| = 2|x-3| < 2\delta = 2\cdot\frac{\varepsilon}{2} = \varepsilon$$

Since $\varepsilon$ was arbitrary, the limit is 7. ∎

**Notice the shape:** the scratch work runs backwards from what you want; the written proof runs forwards from the choice of $\delta$. **Doing the algebra backwards and presenting it forwards is the standard technique**, and it is why these proofs look like they were pulled from nowhere.

## 5. Why anyone should care

**Three reasons, and the third is the real one:**

1. **It removes the appeal to intuition.** Every theorem in calculus is provable from this definition and ordinary arithmetic. Nothing rests on "infinitely small".
2. **It handles pathological cases.** Functions like $\sin\frac{1}{x}$ near 0, or the function that is 1 on rationals and 0 elsewhere, break intuition entirely. The definition still decides them.
3. **It generalises.** Replace $|x - a|$ with any notion of distance and you have limits in the plane, in function spaces, in metric spaces generally. **The whole of analysis is built on this one pattern**, and calculus is its first instance.

> [!NOTE]
> **Rigour arrived 150 years after the results.** Newton and Leibniz got the answers right in the 1660s–70s; the definition justifying them dates from the 1820s onward.
>
> That ordering is normal in mathematics and worth knowing: **useful techniques usually precede their foundations**. The foundations matter because they tell you exactly when a technique is allowed to be trusted — which is precisely what nobody could say about infinitesimals.

## 6. Practice — problems

1. Prove from the definition that $\lim_{x\to 2}(3x - 1) = 5$. Show the scratch work, then the forward proof.
2. Prove that $\lim_{x\to 4} 7 = 7$ (a constant function). What is unusual about the $\delta$ you can choose?
3. For $\lim_{x\to 1}(4x+2) = 6$, find a $\delta$ that works for $\varepsilon = 0.01$. Then find the general $\delta$ in terms of $\varepsilon$.
4. **Explain the quantifier order.** What would "there exists $\delta > 0$ such that for every $\varepsilon > 0$..." claim instead, and why is it almost never true?
5. **Why does the definition use $0 < |x-a|$ rather than $|x-a|$?** Give a function for which it matters.
6. Sketch how you would prove $\lim_{x\to 2} x^2 = 4$. Why is this harder than the linear cases, and what extra step is needed?

<details><summary>Answers — open only after an attempt</summary>

1. Scratch: $|3x-1-5| = 3|x-2| < \varepsilon$ needs $|x-2| < \frac{\varepsilon}{3}$. Proof: given $\varepsilon>0$ choose $\delta = \frac{\varepsilon}{3}$; then $0<|x-2|<\delta$ gives $|3x-6| = 3|x-2| < 3\delta = \varepsilon$. ∎
2. $|7 - 7| = 0 < \varepsilon$ always. <strong>Any $\delta$ works</strong> — the choice is unconstrained, because the function never moves. This is the degenerate case, and it is a useful sanity check that the definition behaves sensibly.
3. $|4x+2-6| = 4|x-1| < 0.01$ needs $\delta = 0.0025$. In general $\delta = \frac{\varepsilon}{4}$.
4. It would claim <strong>one single $\delta$ works for every tolerance</strong>, however small — which would force $f$ to be exactly $L$ throughout that whole neighbourhood. True only for constant functions near that point. <strong>The order encodes "you may adapt your answer to the challenge"</strong>, and without it the definition is useless.
5. Because the limit must not depend on $f(a)$. Take $f(x) = \frac{x^2-1}{x-1}$ at $x=1$: it is undefined there, so any condition involving $x = a$ could never be satisfied and the limit would fail to exist — even though it plainly approaches 2.
6. $|x^2 - 4| = |x-2||x+2|$. The $|x-2|$ factor is controlled by $\delta$, but $|x+2|$ is not — it varies with $x$. <strong>The extra step is to bound it first</strong>: restrict $\delta \le 1$, so $1 < x < 3$ and $|x+2| < 5$; then choose $\delta = \min(1, \frac{\varepsilon}{5})$. Taking the minimum of a bounding constraint and an $\varepsilon$-constraint is the standard move for non-linear cases.
</details>

## Before moving on

- [ ] State the definition with the quantifiers in the right order.
- [ ] Explain the $\varepsilon$–$\delta$ challenge-and-response reading.
- [ ] Prove a linear limit from the definition.
- [ ] Explain why the quantifier order and the strict $0 < |x-a|$ both matter.

**Recap:** The precise definition replaces "gets close to" with a challenge and response: for every tolerance $\varepsilon$ a matching neighbourhood $\delta$ must exist, and the limit holds exactly when you can always answer. The order of quantifiers lets $\delta$ depend on $\varepsilon$, which is what makes the definition usable, and the strict inequality excludes the point itself so the limit never depends on the function's value there. This definition arrived 150 years after the techniques it justifies, and it is the pattern all of analysis is built on.

**Next:** [[01-definition|Defining the Derivative]] — the first thing this machinery was built to support.

## Related

- [[01-definition|The limit of a function]] · [[01-laws|Limit laws]]
- [[mathematics/02-discrete-math/03-proof-techniques|discrete-math/proof techniques]] — the proof style used here
