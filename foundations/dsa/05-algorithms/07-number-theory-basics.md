# Module: Number Theory Basics (Primes, Sieves & GCD)

Welcome to the **Number Theory Basics** module. Number theory is the branch of mathematics and computer science that deals with the properties of integers.

Understanding prime numbers, factorization, and greatest common divisors is essential for modern software engineering—powering everything from **RSA Encryption (HTTPS/SSH)** to hash table distribution and computer graphics algorithms.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine two **Alarm Clocks**:
- Alarm A rings every **12 minutes**.
- Alarm B rings every **18 minutes**.

```
Alarm A (12m):  0 ---- 12 ---- 24 ---- [ 36 ] ---- 48 ---- 60
Alarm B (18m):  0 --------- 18 -------- [ 36 ] --------- 54
```

When will both alarm clocks ring at the exact same moment for the first time?
- The answer is the **Least Common Multiple ($\text{LCM}(12, 18) = 36$ minutes)**!

### Cryptography (RSA Encryption):
Modern internet security relies on the fact that multiplying two 500-digit prime numbers together is instant ($O(1)$), but breaking that 1000-digit result back into its prime factors takes thousands of years of supercomputer brute force!

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Real-World Example |
| :--- | :--- | :--- |
| **Prime Number** | An integer $> 1$ that has no positive divisors other than $1$ and itself. | $2, 3, 5, 7, 11, 13 \dots$ |
| **Composite Number** | An integer $> 1$ that has more than two divisors. | $4, 6, 8, 9, 10, 12 \dots$ |
| **GCD** | Greatest Common Divisor (largest number that divides both $a$ and $b$). | $\text{GCD}(24, 36) = 12$. |
| **LCM** | Least Common Multiple (smallest number that is a multiple of both $a$ and $b$). | $\text{LCM}(12, 18) = 36$. |
| **Sieve of Eratosthenes** | Algorithm to generate all prime numbers up to $N$ by crossing out composite multiples. | Filtering non-prime numbers out of an array. |

---

## 3. Technical Deep Dive: The Core Number Theory Algorithms

### 1. Primality Testing ($O(\sqrt{N})$ Optimization)

> [!KEY-INSIGHT]
> **The $\sqrt{N}$ Symmetric Factor Rule**:
> Every factor pair of $N$ consists of $(a, b)$ such that $a \times b = N$.
> If both $a > \sqrt{N}$ and $b > \sqrt{N}$, then $a \times b > N$ (impossible!). Therefore, **at least one factor in every pair MUST be $\le \sqrt{N}$**.
> 
> To test if $N$ is prime, you only need to test potential divisors up to $\sqrt{N}$!

```python
def is_prime(n: int) -> bool:
    """Tests if a single integer n is prime in O(sqrt(n)) time."""
    if n <= 1:
        return False
        
    i = 2
    while i * i <= n:  # Equivalent to i <= sqrt(n)
        if n % i == 0:
            return False  # Found a factor: not prime!
        i += 1
        
    return True
```
- *Performance*: For $N = 1,000,000,000$, checking up to $N$ takes 1 billion operations. Checking up to $\sqrt{N}$ takes only **31,622 operations** (a $30,000\times$ speedup!).

---

### 2. Sieve of Eratosthenes ($O(N \log \log N)$ All Primes up to $N$)

Testing each number individually up to $N$ takes $N \times O(\sqrt{N}) = O(N \sqrt{N})$. The **Sieve of Eratosthenes** finds ALL primes up to $N$ in near-linear time by crossing out multiples of known primes:

```python
def sieve_of_eratosthenes(n: int) -> list:
    """Generates a boolean list where is_prime[x] is True if x is prime."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False  # 0 and 1 are not prime
    
    i = 2
    while i * i <= n:
        if is_prime[i]:
            # Start crossing out multiples from i*i (smaller multiples already crossed out!)
            for k in range(i * i, n + 1, i):
                is_prime[k] = False
        i += 1
        
    return is_prime
```

---

### 3. Euclidean Algorithm for GCD & LCM ($O(\log(\min(a, b)))$)

The **Euclidean Algorithm** computes the Greatest Common Divisor using the modulo identity:
$$\text{GCD}(a, b) = \text{GCD}(b, a \pmod b)$$

```python
def gcd(a: int, b: int) -> int:
    """Computes Greatest Common Divisor in O(log(min(a, b))) time."""
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    """Computes Least Common Multiple using GCD."""
    if a == 0 or b == 0:
        return 0
    return (a * b) // gcd(a, b)
```

---

## 4. Time & Space Complexity Summary

| Algorithm | Time Complexity | Auxiliary Space | Key Advantage |
| :--- | :--- | :--- | :--- |
| **Primality Check (`is_prime`)** | **$O(\sqrt{N})$** | $O(1)$ | Fast single-number check. |
| **Divisor Counting** | **$O(\sqrt{N})$** | $O(1)$ | Counts factor pairs simultaneously. |
| **Sieve of Eratosthenes** | **$O(N \log \log N)$** | $O(N)$ | Finds all primes up to $N$ at scale. |
| **Euclidean GCD (`gcd`)** | **$O(\log(\min(a, b)))$** | $O(1)$ | Instant GCD calculation. |

---

## 5. Common Pitfalls & Traps

1. **0 and 1 are NOT Prime**: The numbers 0 and 1 are neither prime nor composite. Always handle $N \le 1$ explicitly as `False`.
2. **Integer Overflow in LCM**: In languages like C++ or Java, computing `(a * b) / gcd(a, b)` can overflow 32-bit integers if $a \times b$ is large.
   - *Fix*: Divide first! Write `(a // gcd(a, b)) * b`.
3. **Starting Sieve Multiples at $2i$ instead of $i^2$**: Multiples of $i$ smaller than $i^2$ (like $2i, 3i$) have already been crossed out by smaller primes. Always start crossing out from $i^2$.

---

## 6. Check Your Understanding (University Self-Assessment)

1. **Question**: Why does checking primality only require testing potential factors up to $\sqrt{N}$ instead of $N - 1$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Factors occur in pairs $(a, b)$ such that $a \times b = N$. If both factors were strictly greater than $\sqrt{N}$, their product would exceed $N$. Therefore, at least one factor in every pair must be $\le \sqrt{N}$.</details>

2. **Question**: How do you compute the Least Common Multiple (LCM) of two numbers $a$ and $b$ using GCD?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Formula: <code>LCM(a, b) = (a * b) / GCD(a, b)</code>.</details>

3. **Question**: What is the time complexity of the Euclidean Algorithm for finding the GCD of two numbers?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>O(log(min(a, b)))</b> time. Modulo arithmetic at least halves the size of the smaller number every two steps.</details>

---

## Related Modules
- [[01-algorithms|Algorithms & Complexity Analysis]] — Asymptotic growth bounds
- [[05-searching|Searching Algorithms]] — Binary Search applications
