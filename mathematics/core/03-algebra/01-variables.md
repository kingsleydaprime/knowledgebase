# 3. VARIABLES

## Before you start

- You are comfortable with arithmetic and sets — [[01-sets|sets]].

**What you will be able to do after this lesson:**

1. Explain what a variable is and what it is not.
2. Distinguish a variable from a constant and from a parameter.
3. Substitute values into an expression correctly.
4. Explain how a mathematical variable differs from a programming variable.

**Study route:** read the lesson, then attempt every problem before opening the answers.

---

Now things get interesting.

Suppose I tell you:

> I have some number, but I don't know what it is.

We could call it \(x\).

So:

$$
x = \text{some unknown value}
$$

That \(x\) is a **variable**.

For example:

$$
x+5
$$

means:

> "Take whatever value \(x\) represents and add 5."

If:

$$
x=3
$$

then:

$$
x+5=8
$$

If:

$$
x=20
$$

then:

$$
x+5=25
$$

The variable is therefore a **symbol representing a value**.

---

## Practice — problems

Attempt all of these before opening the answers.

1. Evaluate $3x^2 - 2x + 7$ at $x = 0, 2, -3$.
2. Evaluate $\frac{a+b}{a-b}$ at $a=5, b=3$. What happens at $a = b$, and what is the rule being violated?
3. **Name the role** of each symbol in $A = \pi r^2$: which is a variable, which a constant, and which depends on which?
4. **The key difference.** In maths, $x = x + 1$ has no solution. In most programming languages it is a perfectly ordinary statement. Explain what `=` means in each case.
5. Write an expression for "a number is three more than twice another", naming your variables explicitly.

<details><summary>Answers — open only after an attempt</summary>

1. At $x=0$: $7$. At $x=2$: $12-4+7=15$. At $x=-3$: $27+6+7=40$.
2. $\frac{8}{2} = 4$. At $a=b$ the denominator is zero and the expression is <strong>undefined</strong> — division by zero is not a value, not even infinity.
3. $\pi$ is a <strong>constant</strong>; $r$ is the <strong>independent variable</strong>; $A$ is the <strong>dependent variable</strong>, determined by $r$.
4. In mathematics <code>=</code> asserts that two things <em>are equal</em>, so $x = x+1$ claims a number equals its own successor, which is false for every $x$. In most programming languages <code>=</code> is <strong>assignment</strong> — "compute the right side, store it in the left" — which is an instruction, not a claim. Languages that use <code>=</code> for equality (or <code>==</code>, or <code>:=</code> for assignment) are trying to keep these apart.
5. Let $n$ be the first number and $m$ the second: $n = 2m + 3$.
</details>

## Before moving on

You are done with this lesson when you can, closed-book:

- [ ] Say what a variable is without saying 'a letter'.
- [ ] Distinguish variable, constant, parameter, independent and dependent.
- [ ] Substitute values correctly, including spotting an undefined result.
- [ ] Explain the difference between mathematical equality and programming assignment.

**Recap:** A variable is a name for a quantity that may vary or is not yet known — not merely a letter. Constants hold fixed values, parameters are held fixed within a problem but vary between problems, and dependent variables are determined by independent ones. The most consequential distinction for a programmer is that mathematical `=` asserts equality while programming `=` usually commands assignment, which is why $x = x + 1$ is false in one and routine in the other.

**Next:** [[02-equations|Equations]] — once you can name an unknown, the next question is how to find it.
