# PART 0 — PREREQUISITE MATHEMATICS

# Week 1 — Mathematical Foundations

### The goal of Week 1

By the end of this week, you should be comfortable with the mathematical language we'll need later for:

- electrical signals
- voltage/current
- transistors
- digital logic
- computer architecture
- algorithms
- signal processing
- control systems
- robotics

The topics form roughly this dependency chain:

```text
Numbers
   ↓
Sets
   ↓
Variables
   ↓
Functions
   ↓
Equations
   ↓
Algebra
   ↓
Exponents
   ↓
Logarithms
   ↓
Graphs
   ↓
Rates of change
   ↓
Differentiation
   ↓
Integration
```

And alongside that:

```text
Numbers
   ↓
Ratios / proportions
   ↓
Units
   ↓
Dimensional analysis
   ↓
Engineering calculations
```

So let's start at the absolute bottom.

---

---

---

---

---

---

# 8. UNITS AND DIMENSIONAL ANALYSIS

This one is **very important for engineering**.

Suppose someone tells you:

$$
v=20
$$

Twenty what?

20 meters per second?

20 kilometers per hour?

20 volts?

20 kilograms?

The number alone isn't enough.

We need the **unit**.

For example:

$$
20\,m/s
$$

means velocity.

---

## Dimensional analysis

Suppose:

$$
d=vt
$$

Distance equals velocity multiplied by time.

If:

$$
v=10\,m/s
$$

and:

$$
t=5\,s
$$

then:

$$
d=(10\,m/s)(5s)
$$

The seconds cancel:

$$
d=50\,m
$$

The units themselves helped us verify that our answer makes sense.

That's dimensional analysis.

It is basically:

> **Use the units to check whether your mathematics makes physical sense.**

This is one of the habits I want you to develop strongly as a systems engineer.

---

# 9. RATIOS AND PROPORTIONS

A ratio compares quantities.

For example:

$$
2:3
$$

means:

> for every 2 units of one thing, there are 3 units of another.

We can also write:

$$
\frac23
$$

Suppose a robot travels 10 meters in 2 seconds.

Its average speed is:

$$
\frac{10m}{2s}=5m/s
$$

That's essentially a ratio.

Ratios are everywhere in engineering:

- gear ratios
- voltage ratios
- current ratios
- scaling
- sensor calibration
- mechanical systems
- probabilities

---

# 10. GRAPHS

Now we move from numbers to **relationships between numbers**.

Suppose we have:

$$
y=2x
$$

We can create a table:

| \(x\) | \(y\) |
| ----: | ----: |
|     0 |     0 |
|     1 |     2 |
|     2 |     4 |
|     3 |     6 |
|     4 |     8 |

Plot those points and you get a straight line.

genui{"learning_viz":{"type_id":"SLOPE_EQUATION","content":"m=\frac{y_2-y_1}{x_2-x_1}"}}

The **slope** tells us how quickly \(y\) changes as \(x\) changes.

Mathematically:

$$
\boxed{m=\frac{\Delta y}{\Delta x}}
$$

For example, going from:

$$
(1,2)
$$

to:

$$
(3,6)
$$

gives:

$$
m=\frac{6-2}{3-1}
$$

$$
m=\frac42
$$

$$
\boxed{m=2}
$$

Meaning:

> Every time \(x\) increases by 1, \(y\) increases by 2.

---

# 11. RATE OF CHANGE

This idea becomes extremely important for physics and engineering.

Imagine voltage changing over time.

At:

$$
t=0s,\quad V=0V
$$

At:

$$
t=2s,\quad V=10V
$$

The average rate of change is:

$$
\frac{\Delta V}{\Delta t}
$$

$$
=\frac{10V-0V}{2s}
$$

$$
=\boxed{5V/s}
$$

So voltage is changing at 5 volts per second.

And now we're getting very close to **calculus**.

---

# 12. BASIC DIFFERENTIATION

Differentiation answers a powerful question:

> **How fast is something changing right now?**

Suppose:

$$
y=x^2
$$

The derivative is:

$$
\frac{dy}{dx}=2x
$$

So at:

$$
x=3
$$

the instantaneous rate of change is:

$$
2(3)=6
$$

So the function is changing at a rate of 6 at that point.

This idea appears everywhere:

- velocity = rate of change of position
- acceleration = rate of change of velocity
- current can relate to changing charge
- control systems
- robotics
- signal processing
- optimization
- machine learning

---

# 13. BASIC INTEGRATION

Integration is, roughly speaking, the reverse perspective.

If differentiation asks:

> "How fast is this changing?"

Integration asks things like:

> "How much has accumulated?"

Suppose velocity is:

$$
v=5m/s
$$

for:

$$
10s
$$

Then the distance travelled is:

$$
d=vt
$$

$$
d=(5)(10)
$$

$$
\boxed{50m}
$$

Integration generalizes this when the velocity isn't constant.

If velocity changes over time:

$$
v=v(t)
$$

then distance can be found from:

$$
\boxed{d=\int v(t)\,dt}
$$

And now we're officially touching the mathematical machinery behind a huge amount of engineering.

---

# The BIG picture

Look at what we've built.

We started with:

```text
Numbers
```

and gradually built:

```text
Numbers
   ↓
Variables
   ↓
Equations
   ↓
Algebra
   ↓
Functions
   ↓
Graphs
   ↓
Change
   ↓
Differentiation
   ↓
Integration
```

This isn't a collection of unrelated mathematical topics.

It's a **language for describing systems**.

And that's exactly why we're doing this before we dive deeper into computers.

---

# Your first checkpoint 🧠

Don't worry about solving 50 questions. I want to see whether the concepts are actually settling.

Try these **without looking anything up**:

### 1.

Which of these are integers?

$$
-4,\quad 0,\quad \frac12,\quad 3.7,\quad 12
$$

### 2.

Is:

$$
0.333333\ldots
$$

a rational number? Why?

### 3.

If:

$$
3x+6=21
$$

find \(x\).

### 4.

Simplify:

$$
2^3\times2^4
$$

### 5.

Write:

$$
0.00000052
$$

in scientific notation.

### 6.

A robot travels \(120m\) in \(20s\). What is its average speed?

### 7.

What does the **slope** of a graph physically tell you?

### 8.

In your own words, what's the difference between **differentiation** and **integration**?

Don't worry about getting them all right. **Especially #7 and #8—I care more about your explanation than the calculation.**

Once you answer these, I'll grade them like we're actually doing the course, correct whatever needs correcting, and then we'll continue with the next part of **Week 1: functions, graphs, and mathematical relationships**.
