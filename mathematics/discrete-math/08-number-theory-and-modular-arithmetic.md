# Number Theory and Modular Arithmetic

**[Intermediate]** — Divisibility, primes and clock arithmetic. Pure mathematics until 1977, then the basis of every secure connection you make.

## Divisibility and GCD

$a \mid b$ means $a$ divides $b$ exactly.

**The greatest common divisor** $\gcd(a,b)$ is the largest number dividing both.

**Euclid's algorithm** computes it, and it's the oldest algorithm still in use — about 2,300 years old:

$$\gcd(a, b) = \gcd(b, a \bmod b), \qquad \gcd(a, 0) = a$$

```
gcd(48, 18) → gcd(18, 12) → gcd(12, 6) → gcd(6, 0) = 6
```

**It runs in $O(\log \min(a,b))$** — the worst case is consecutive Fibonacci numbers, which is a nice connection to [[foundations/discrete-math/05-induction-and-recursion|recurrences]]. **Extraordinarily fast**, and that efficiency is what makes RSA key generation practical.

**Extended Euclid** additionally finds $x, y$ with

$$ax + by = \gcd(a,b) \qquad \text{(Bézout's identity)}$$

**This is what computes modular inverses**, so it's load-bearing for RSA. Not a curiosity.

**Coprime** means $\gcd(a,b) = 1$ — no common factor.

## Primes

**A prime has exactly two divisors: 1 and itself.** (1 is not prime, by convention, and the convention exists to make the next theorem true.)

**The Fundamental Theorem of Arithmetic:** every integer > 1 has a **unique** prime factorisation.

**Euclid: there are infinitely many primes.** Assume finitely many, multiply them all and add 1 — the result is divisible by none of them. → [[foundations/discrete-math/03-proof-techniques|Proof by contradiction]]

**The Prime Number Theorem:** primes near $n$ have density about $1/\ln n$.

> **That density is why RSA works.** Around $2^{1024}$, roughly 1 in 710 odd numbers is prime — so **generating a random 1024-bit prime takes a few hundred tries**, not an astronomical search. Public-key cryptography depends on primes being *common enough to find* and *factoring being hard*, and both are facts about how primes are distributed.

**Testing primality** — and this is the important asymmetry:

**Miller–Rabin** is a probabilistic test: fast, and wrong with probability $< 4^{-k}$ for $k$ rounds. **With 40 rounds the error probability is below the chance of a hardware fault**, so it's what everything actually uses.

**AKS** (2002) is deterministic polynomial-time — a major theoretical result, too slow in practice.

> **Testing whether a number is prime is easy. Finding its factors is hard.** That gap — polynomial versus (believed) super-polynomial — is the entire foundation of RSA. **Note that it's a *believed* hardness, not a proven one**: nobody has proved factoring is hard, and Shor's algorithm factors in polynomial time on a quantum computer. → [[foundations/theory-of-computation/08-beyond-p-vs-np|Beyond P vs NP]]

## Modular arithmetic

**"Clock arithmetic."** $a \equiv b \pmod n$ means $n \mid (a - b)$ — they have the same remainder.

$$17 \equiv 5 \pmod{12}$$

**It's an [[foundations/discrete-math/04-sets-relations-and-functions|equivalence relation]]**, partitioning $\mathbb{Z}$ into $n$ residue classes, and that's what $\mathbb{Z}_n$ means.

**Arithmetic is well-defined on classes:**

$$(a+b) \bmod n, \quad (a\times b)\bmod n \quad\text{— you can reduce at any point}$$

**Practically: reduce as you go.** Computing $a^b \bmod n$ by computing $a^b$ first will overflow anything. Reducing every step keeps numbers small, and it's why modular exponentiation is feasible.

**Modular exponentiation** — square-and-multiply:

```
result = 1
while exp > 0:
    if exp is odd:  result = result * base % mod
    base = base * base % mod
    exp = exp / 2
```

**$O(\log \text{exp})$ multiplications instead of exp.** $2^{1000} \bmod n$ in ten steps. **This is the workhorse of public-key crypto**, and the reason RSA is usable at all.

### Modular inverse

$a^{-1}$ is the value with $a \cdot a^{-1} \equiv 1 \pmod n$.

> **It exists if and only if $\gcd(a,n) = 1$.** Found by extended Euclid.

**There's no division in modular arithmetic** — you multiply by the inverse instead. And when $n$ is prime, *every* nonzero element has an inverse, which makes $\mathbb{Z}_p$ a **field**. That's why cryptography and error-correcting codes work over prime moduli.

## The two theorems

**Fermat's Little Theorem** — for prime $p$ and $\gcd(a,p)=1$:

$$a^{p-1} \equiv 1 \pmod p$$

The basis of primality testing: if $a^{n-1} \not\equiv 1 \pmod n$, then $n$ is definitely composite. (The converse fails — Carmichael numbers pass for every $a$, which is why Miller–Rabin refines the test.)

**Euler's theorem** generalises it:

$$a^{\phi(n)} \equiv 1 \pmod n \quad\text{when } \gcd(a,n)=1$$

where $\phi(n)$ counts integers below $n$ coprime to it. For $n = pq$ with $p, q$ prime, $\phi(n) = (p-1)(q-1)$.

**That formula is the key to RSA**, quite literally.

**The Chinese Remainder Theorem** — a system of congruences with coprime moduli has a unique solution mod their product. Used to speed up RSA decryption by about 4×, and in secret sharing.

## RSA, in full

**The payoff, and it's short enough to state completely:**

**Key generation**
1. Pick large primes $p, q$. Let $n = pq$
2. Compute $\phi(n) = (p-1)(q-1)$
3. Choose $e$ coprime to $\phi(n)$ (usually 65537)
4. Compute $d = e^{-1} \bmod \phi(n)$ — **extended Euclid**
5. **Public key** $(n, e)$. **Private key** $(n, d)$. **Discard $p$ and $q$**

**Encrypt:** $c = m^e \bmod n$  **Decrypt:** $m = c^d \bmod n$

**Why it works:** $m^{ed} = m^{1 + k\phi(n)} = m \cdot (m^{\phi(n)})^k \equiv m \pmod n$ **by Euler's theorem.**

**Why it's secure:** recovering $d$ requires $\phi(n)$, which requires $p$ and $q$, which requires **factoring $n$**. Everyone has $n$; nobody can factor it at 2048 bits.

> **Every idea in this note appears in those eight lines** — primes, GCD, modular inverse, modular exponentiation, Euler's theorem. It's an unusually direct route from elementary number theory to infrastructure that carries the world's money.
>
> **The historical point is worth keeping.** G. H. Hardy wrote in 1940 that number theory had no practical application and was proud of it. Thirty-seven years later it became the basis of electronic commerce. **"No applications" is a statement about the present, not the subject.**

→ [[cybersecurity/05-cryptography/04-asymmetric-encryption|Asymmetric Encryption]] for the practical side — padding (textbook RSA is insecure without OAEP), key sizes, and why elliptic curves are now preferred.

## Where else it's used

**Hashing.** $h(k) = k \bmod m$ — and **choosing $m$ prime** matters, because a composite modulus lets patterns in the keys collapse onto few buckets. → [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]]

**Checksums.** ISBN, IBAN, credit card numbers (Luhn), and CRC are all modular arithmetic. **A check digit catches single-digit and transposition errors** by construction.

**Random number generators.** LCGs are $x_{n+1} = (ax_n + c) \bmod m$, and the choice of constants determines the period. → [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability]]

**Error-correcting codes.** Reed–Solomon operates over finite fields — Galois fields being modular arithmetic generalised. Used in QR codes, CDs, RAID 6, and deep-space communication.

**Circular buffers.** `index = (index + 1) % size` is modular arithmetic and is how ring buffers work.

**Diffie–Hellman key exchange** — the discrete logarithm problem: given $g^a \bmod p$, find $a$. **Easy to compute forwards, believed hard backwards** — the same one-way asymmetry as factoring, different problem. → [[cybersecurity/05-cryptography/04-asymmetric-encryption|Asymmetric Encryption]]

## Practical notes

**Negative modulo differs by language.** `-7 % 3` is `2` in Python and `-1` in C, Java and Rust. **A real cross-language bug.** For a non-negative result: `((a % n) + n) % n`.

**Overflow before reduction.** `(a * b) % n` overflows if $a\cdot b$ exceeds your integer width even when the result fits. Use a wider type, or `__int128`, or a bignum.

**Use a library for cryptography.** Everything here is implementable in an afternoon and **that implementation will be broken** — timing side channels, weak randomness, missing padding. **Implement it to understand it; use libsodium or your platform's library in production.** → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|Cryptographic Best Practices]]

**Randomness must be cryptographic.** `rand()` seeded from the clock has produced real key compromises. Use `/dev/urandom` or the OS CSPRNG.

**Constant-time comparison** for secrets. A comparison that returns early on the first differing byte leaks information through timing.

---

## Related
- [[cybersecurity/05-cryptography/04-asymmetric-encryption|Asymmetric Encryption]] — RSA and ECC in practice
- [[foundations/discrete-math/06-combinatorics-and-counting|Combinatorics]] — the birthday bound on key sizes
- [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]] — why factoring's hardness is only conjectured
- [[foundations/discrete-math/README|Discrete maths map]]
