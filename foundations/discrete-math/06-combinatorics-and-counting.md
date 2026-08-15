# Combinatorics and Counting

**[Intermediate]** — Counting without enumerating, and the principle that proves compression limits and hash collisions in one line.

## Why counting is a subject

"How many?" sounds trivial until the answer is $2^{128}$ and you need it without listing them.

**Counting tells you how big a search space is**, which tells you whether brute force is viable, how strong a password is, how likely a hash collision is, and how many test cases would be exhaustive.

## The two basic rules

**Product rule** — independent choices multiply.

$$k \text{ decisions with } n_1, n_2, \ldots, n_k \text{ options} \quad\Rightarrow\quad n_1 \times n_2 \times \cdots \times n_k$$

An 8-character password from 62 alphanumerics: $62^8 \approx 2.2 \times 10^{14}$.

**Sum rule** — mutually exclusive alternatives add.

**Getting these two straight is most of elementary counting.** "And" multiplies, "or" (disjoint) adds — the same structure as [[foundations/discrete-math/02-logic|logic]] and [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|probability]], which is not a coincidence.

## Permutations and combinations

**Permutation — order matters:**

$$P(n,k) = \frac{n!}{(n-k)!}$$

Arrangements of $k$ items from $n$. All $n$: just $n!$.

**Combination — order doesn't:**

$$\binom{n}{k} = \frac{n!}{k!(n-k)!}$$

**The relationship:** $\binom{n}{k} = P(n,k)/k!$ — divide out the $k!$ orderings you're now treating as the same.

**The decision procedure**, since this is where people slip:

```
Does order matter?
├── YES → permutation
└── NO  → combination

Can items repeat?
├── YES → nᵏ (ordered) or C(n+k−1, k) (unordered)
└── NO  → P(n,k) or C(n,k)
```

**Identities worth knowing:**

$$\binom{n}{k} = \binom{n}{n-k} \qquad \binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k} \qquad \sum_{k=0}^{n}\binom{n}{k} = 2^n$$

**The middle one is Pascal's rule** — and it's a recurrence, so it's the DP formulation of binomial coefficients. **The last one says the subsets of an $n$-set number $2^n$**, counted by size, which connects straight back to [[foundations/discrete-math/04-sets-relations-and-functions|power sets]].

## The pigeonhole principle

**Trivially obvious, and it proves things that aren't.**

> **If $n+1$ items go into $n$ boxes, some box holds at least two.**

**Generalised:** $n$ items into $k$ boxes forces some box to hold at least $\lceil n/k \rceil$.

**What it proves:**

**Hash collisions are unavoidable.** A hash maps arbitrary-length inputs to fixed-length outputs. **More inputs than outputs, so collisions exist** — mathematically guaranteed, not a weakness of any particular function. A good cryptographic hash only makes them hard to *find*. → [[cybersecurity/05-cryptography/03-hashing-and-integrity|Hashing and Integrity]]

**Lossless compression cannot shrink every input.** There are $2^n$ strings of length $n$ and only $2^n - 1$ shorter strings. **Any injective map must send some inputs to longer outputs.** Every "compresses anything by 50%" claim is provably false, and this is the one-line disproof.

**In any set of $n+1$ integers from $1..2n$, two are coprime** — a genuinely non-obvious result from a very obvious principle.

**Two people in London have the same number of head hairs.** Non-constructive: certainly true, and you'll never know who. → [[foundations/discrete-math/03-proof-techniques|Proof Techniques]]

## Inclusion–exclusion

Counting a union without double-counting overlaps:

$$|A \cup B| = |A| + |B| - |A\cap B|$$

$$|A\cup B\cup C| = |A|+|B|+|C| - |A\cap B| - |A\cap C| - |B\cap C| + |A\cap B\cap C|$$

**Alternating signs, and in general $2^n - 1$ terms** — which is why it's elegant and often impractical for large $n$.

**Where it shows up:** counting query results across overlapping conditions, derangements (permutations with no fixed point), and Euler's totient function in [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|number theory]].

## The birthday problem

**The most practically important counting result for a programmer**, because the answer is so much smaller than intuition suggests.

**How many people before two share a birthday, with probability > 50%?**

**23.**

$$P(\text{no collision}) = \prod_{i=0}^{k-1}\frac{365-i}{365} = \frac{365!}{(365-k)!\,365^k}$$

At $k=23$ this drops below 0.5.

**Why intuition fails:** you're not comparing yourself to 22 others — you're comparing **all $\binom{23}{2} = 253$ pairs**. Collisions scale with pairs, which is quadratic.

**The general rule, and the one to remember:**

$$\boxed{\text{Expect a collision after about } \sqrt{N} \text{ samples from } N \text{ possibilities}}$$

**The consequences are large:**

| Hash | Output bits | Brute force | **Birthday attack** |
|---|---|---|---|
| MD5 | 128 | $2^{128}$ | $2^{64}$ ← broken |
| SHA-1 | 160 | $2^{160}$ | $2^{80}$ ← broken |
| SHA-256 | 256 | $2^{256}$ | $2^{128}$ |

> **A hash with $n$ bits gives you only $n/2$ bits of collision resistance.** This is why "128-bit hash" is not 128 bits of security against collisions, why SHA-1 fell, and why you need 256 bits of output for 128 bits of collision resistance. **It's a counting fact that dictates cryptographic parameter choices.**

It's also why **UUID collisions are unlikely but not impossible** (122 random bits → expect a collision around $2^{61}$ UUIDs), and why hash tables need collision handling at far lower load factors than naive reasoning suggests.

## Counting and probability

**Discrete probability is counting divided by counting**, when outcomes are equally likely:

$$P(\text{event}) = \frac{|\text{favourable outcomes}|}{|\text{all outcomes}|}$$

Which is why combinatorics comes first. Full treatment: [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability and Statistics]].

**The link worth noting:** $\binom{n}{k}p^k(1-p)^{n-k}$ — the binomial distribution — is *literally* a combination times a product-rule probability. The $\binom{n}{k}$ counts which $k$ of the $n$ trials succeeded.

## Where counting is applied

**Security and passwords.** Entropy is $\log_2(\text{number of possibilities})$. **A 12-character random password from 94 printable ASCII characters has $\log_2(94^{12}) \approx 79$ bits.** A memorable passphrase of 5 words from a 7,776-word list has $\log_2(7776^5) \approx 65$ bits — and is far easier to remember. **Counting is how you compare them honestly.** → [[cybersecurity/06-attacks-and-threats/README|Attacks and Threats]]

**Complexity analysis.** "How many subsets?" ($2^n$) "How many permutations?" ($n!$) tells you immediately whether exhaustive search is possible. $n!$ at $n=20$ is $2.4\times10^{18}$. → [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]]

**Hash table sizing.** Expected collisions, load factor, and why you resize. → [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]]

**Test coverage.** Combinatorial explosion is why exhaustive testing is impossible and why pairwise testing exists — covering all *pairs* of parameter values is polynomial where all combinations is exponential.

**Distributed systems.** Quorum intersection is a counting argument: any two majorities of $2f+1$ nodes must overlap, because $2(f+1) > 2f+1$. **That one inequality is why quorums work.** → [[architecture/04-distributed-systems/07-consensus-and-paxos|Consensus]]

**Load balancing.** "Power of two choices" — picking the lesser-loaded of two random servers reduces maximum load from $O(\log n/\log\log n)$ to $O(\log\log n)$. A counting result with real operational impact.

## Practical notes

**Factorials explode.** $20! \approx 2.4\times10^{18}$ overflows a 64-bit signed integer at $21!$. Use logarithms, or compute $\binom{n}{k}$ incrementally rather than as a ratio of factorials.

**Compute binomials without overflow:**

```
result = 1
for i in 0..k:
    result = result * (n - i) / (i + 1)
```

Multiply then divide, in that order — the intermediate is always an integer.

**Check for double-counting.** The commonest error. Ask: could I reach the same outcome by two different paths in my counting scheme?

**Sanity-check with small cases.** Compute by hand for $n = 2, 3$ and compare against your formula. **Catches most off-by-one and order-matters errors immediately.**

---

## Related
- [[foundations/discrete-math/04-sets-relations-and-functions|Sets, Relations and Functions]] — power sets and cardinality
- [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/README|Probability and Statistics]] — where counting becomes probability
- [[cybersecurity/05-cryptography/03-hashing-and-integrity|Hashing and Integrity]] — the birthday bound applied
- [[foundations/discrete-math/README|Discrete maths map]]
