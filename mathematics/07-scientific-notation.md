# 7. SCIENTIFIC NOTATION

Engineering deals with ridiculously large and ridiculously small numbers.

For example, the number of transistors in a modern processor can be **tens of billions**.

Writing:

```text
50,000,000,000
```

over and over is annoying.

So we write:

$$
5\times10^{10}
$$

That's scientific notation.

The general form is:

$$
\boxed{a\times10^n}
$$

where \(a\) is typically between 1 and 10.

For example:

$$
3000000=3\times10^6
$$

and:

$$
0.000004=4\times10^{-6}
$$

genui{"learning_viz":{"type_id":"SCIENTIFIC_NOTATION"}}

Notice the exponent tells us which direction the decimal point moves.

Positive exponent:

$$
10^6
$$

means a large number.

Negative exponent:

$$
10^{-6}
$$

means a small number.

This becomes particularly useful in electronics.

For example:

$$
1\mu m=10^{-6}m
$$

and:

$$
1nm=10^{-9}m
$$

Modern semiconductor manufacturing deals with dimensions at scales like these.
