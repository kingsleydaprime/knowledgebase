# Number Theory Basics

> Added after reviewing Codility's own course PDFs in `pdfs/` (`8-PrimeNumbers.pdf`, `9-Sieve.pdf`, `10-Gcd.pdf`) — none of this was covered anywhere in this vault, despite being classic, frequently-tested algorithmic building blocks.

Part of [[foundations/dsa/README|DSA fundamentals]]. Four related, genuinely useful techniques: testing whether a single number is prime, finding *every* prime up to some limit efficiently, breaking a number down into its prime factors, and finding the greatest common divisor of two numbers. Each builds a little on the idea before it.

---

## Primality testing — is this one number prime?

A prime number has exactly two divisors (1 and itself); a composite number has more than two. The naive check — try every number from 2 to n-1 as a possible divisor — is O(n). It doesn't need to be:

```python
def is_prime(n):
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True
```
**Why `i * i <= n` instead of checking up to n:** divisors come in symmetric pairs — if `a` divides `n`, so does `n/a`, and one of every such pair is always ≤ √n. So checking every candidate up to √n is enough to find *a* divisor if one exists, without ever needing to check past it. This drops the check from **O(n) to O(√n)** — a real, practical speedup, not just a theoretical one (for n around a billion, that's the difference between ~1 billion operations and ~31,000).

The same √n insight also counts *all* divisors of n efficiently, rather than just testing primality:
```python
def count_divisors(n):
    i, result = 1, 0
    while i * i < n:
        if n % i == 0:
            result += 2   # i and n/i are BOTH divisors, count the pair at once
        i += 1
    if i * i == n:
        result += 1        # n is a perfect square — its square root divisor only counts once, not twice
    return result
```

---

## Sieve of Eratosthenes — finding every prime up to n

Testing each number individually up to n costs O(n√n) total — fine for one number, wasteful for "find every prime up to a million." The **Sieve of Eratosthenes** flips the approach: instead of asking "is this number prime?" one at a time, start assuming everything's prime and cross out every multiple of each prime as you find it.

```python
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    i = 2
    while i * i <= n:
        if is_prime[i]:
            k = i * i          # start crossing out from i*i, not 2*i — every smaller multiple of i
            while k <= n:       # was already crossed out by a smaller prime factor
                is_prime[k] = False
                k += i
        i += 1
    return is_prime
```
Starting the inner crossing-out loop at `i*i` rather than `2*i` is the one detail worth internalizing: any multiple of `i` smaller than `i*i` (like `2*i`, `3*i`, ...) has already been eliminated by a *smaller* prime factor earlier in the sieve, so re-crossing it is wasted work. With this optimization the sieve runs in **O(n log log n)** — close enough to linear that "find all primes up to a million" is genuinely fast, where testing each of those million numbers individually would not be.

### Factorization — reusing the sieve to break a number into prime factors

A small modification to the sieve remembers, for every composite number crossed out, the *smallest* prime that divides it:
```python
def smallest_prime_factors(n):
    spf = [0] * (n + 1)
    i = 2
    while i * i <= n:
        if spf[i] == 0:              # i itself is prime (nothing smaller crossed it out)
            k = i * i
            while k <= n:
                if spf[k] == 0:
                    spf[k] = i
                k += i
        i += 1
    return spf

def factorize(x, spf):
    factors = []
    while spf[x] > 0:
        factors.append(spf[x])
        x //= spf[x]
    factors.append(x)               # whatever's left is itself prime
    return factors
```
Once that `spf` (smallest prime factor) table is built once — O(n log log n), same cost as the plain sieve — factorizing any number up to n costs only **O(log x)**: each step divides out one prime factor, and a number can't have more than log₂(x) prime factors (every prime factor is at least 2). Precompute once, factorize many numbers cheaply — the standard tradeoff behind this technique.

---

## GCD — the Euclidean algorithm

The **greatest common divisor** of two numbers is the largest number that divides both evenly. One of the oldest algorithms still in everyday use:

```python
def gcd(a, b):
    if a % b == 0:
        return b
    return gcd(b, a % b)
```
The insight making this work: `gcd(a, b) == gcd(b, a mod b)` — you can always replace the larger number with the remainder of dividing it by the smaller, and the GCD doesn't change. Repeat until the remainder hits zero; whatever's left is the answer.
```
gcd(24, 9) = gcd(9, 24 mod 9) = gcd(9, 6) = gcd(6, 9 mod 6) = gcd(6, 3) = gcd(3, 6 mod 3) = gcd(3, 0) → 3
```
This runs in **O(log(a+b))** — each step at least halves the numbers involved (provably tied to how fast Fibonacci numbers grow), so even huge inputs converge in a small number of steps. Contrast with the *original*, more intuitive version of Euclid's algorithm — repeated **subtraction** instead of the modulo shortcut (`gcd(a-b, b)` if `a > b`, else `gcd(a, b-a)`) — which is correct but only **O(n)** in the worst case (e.g. `gcd(x, 1)`), since it can take one full subtraction per step instead of jumping straight to the remainder.

### LCM — falls out of GCD almost for free

The **least common multiple** relates to GCD directly:
```python
def lcm(a, b):
    return a * b // gcd(a, b)
```
Same O(log(a+b)) cost as computing the GCD itself, since that's the only expensive part. For more than two numbers, apply it pairwise: `lcm(a, b, c) = lcm(a, lcm(b, c))`.

---

## Related
- [[foundations/dsa/06-patterns/09-modified-binary-search|modified-binary-search]] — another place the "√n / log n instead of n" style of insight shows up
- [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]] — GCD's recursive structure and the Fibonacci-growth proof behind its complexity are worth noticing in relation to that note
