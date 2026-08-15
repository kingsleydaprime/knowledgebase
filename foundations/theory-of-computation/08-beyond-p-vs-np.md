# Beyond P vs NP

**[Advanced]** — Randomness, quantum computing, interactive proofs, and where the theory actually touches your work.

## Randomised computation

**Adding a coin flip changes what's practical**, and the classes are worth knowing because randomised algorithms are genuinely useful.

| Class | Error allowed |
|---|---|
| **ZPP** | never wrong; **running time** is random (Las Vegas) |
| **RP** | may wrongly say *no*; never wrongly says *yes* |
| **BPP** | wrong either way with probability $\leq 1/3$ (Monte Carlo) |

**The $1/3$ is arbitrary.** Run it $k$ times and take the majority — **error drops exponentially**, so $1/3$ becomes $2^{-100}$ in a hundred runs. That's why the constant doesn't matter.

**$\text{P}\subseteq\text{BPP}$, and whether BPP is bigger is open** — but the modern belief is **$\text{BPP} = \text{P}$**, based on derandomisation results (Impagliazzo–Wigderson: if certain hard functions exist, every randomised algorithm can be derandomised).

> **The historical case study is primality testing.** Miller–Rabin (randomised, 1976) was fast and practical. **AKS (2002) proved primality is in P** — deterministic polynomial time. **The randomised algorithm is still what everyone uses**, because it's vastly faster.
>
> **That's the honest lesson: complexity class membership and practical choice are different questions.** → [[foundations/discrete-math/08-number-theory-and-modular-arithmetic|Primality testing]]

**Where randomisation earns its place in practice:**

- **Hashing** — universal hashing gives guarantees no fixed hash can, against adversarial input
- **Quicksort with a random pivot** — expected $O(n\log n)$ regardless of input, which defeats the adversarial worst case
- **Monte Carlo methods** — integration in high dimensions, where deterministic quadrature fails
- **Randomised load balancing** — power of two choices
- **Skip lists** — probabilistic balancing, far simpler than a red-black tree
- **Bloom filters** — one-sided error, huge space saving. **A "no" is certain, a "yes" is probable** → [[foundations/dsa/04-data-structures/03-hash-maps|Hash Maps]]

**The pattern in every case: randomness buys simplicity and robustness against adversarial input**, not raw asymptotic power.

## Quantum computing

**BQP** — polynomial time on a quantum computer with bounded error.

**What's known:** $\text{P}\subseteq\text{BQP}\subseteq\text{PSPACE}$. **The relationship between BQP and NP is open**, and BQP is *not* believed to contain NP.

> **The most important correction to make here:** **quantum computers are not "try all possibilities in parallel."** That's the popular description and it's wrong.
>
> A quantum state is a superposition, but **measurement collapses it to one outcome.** The trick in a quantum algorithm is **interference** — arranging the amplitudes so wrong answers cancel and right answers reinforce. **That requires exploitable structure**, which is why quantum speedups are rare and specific rather than general.

**The two algorithms that matter:**

**Shor's (1994)** — factoring and discrete log in polynomial time. **Exponential speedup.** It works because factoring reduces to *period finding*, and the quantum Fourier transform finds periods efficiently. **The structure is what's being exploited.**

**Grover's (1996)** — unstructured search in $O(\sqrt{N})$ instead of $O(N)$. **Quadratic**, and **provably optimal** for unstructured search — no quantum algorithm does better.

**What that means for security:**

| | Impact | Response |
|---|---|---|
| **RSA, ECC, Diffie–Hellman** | **broken by Shor** | migrate to post-quantum |
| **AES-128** | Grover halves it → 64-bit | **use AES-256** |
| **SHA-256** | Grover → 128-bit | acceptable |

**Symmetric crypto survives by doubling key sizes. Public-key crypto does not survive.** → [[cybersecurity/05-cryptography/04-asymmetric-encryption|Asymmetric Encryption]]

**Post-quantum cryptography** is the response, and it's already standardised: NIST selected **ML-KEM (Kyber)** for key encapsulation and **ML-DSA (Dilithium)** plus **SLH-DSA (SPHINCS+)** for signatures in 2024. Based on lattice and hash problems with no known quantum attack.

> **"Harvest now, decrypt later" is why this is urgent despite no useful quantum computer existing.** An adversary recording encrypted traffic today can decrypt it whenever a machine arrives. **Anything needing secrecy for a decade should be migrating now**, and browsers and TLS libraries have already begun deploying hybrid key exchange.

**The honest state of the hardware:** current machines have hundreds to low thousands of noisy physical qubits. **Breaking RSA-2048 needs millions of physical qubits with error correction.** Estimates for when range from a decade to never. **The cryptographic migration is prudent risk management, not a response to an existing capability.**

## Interactive proofs

**A strange and beautiful corner** with real applications.

**IP** — a prover with unlimited power tries to convince a polynomial-time verifier, over multiple rounds, with randomness.

**Shamir's theorem (1990): $\text{IP} = \text{PSPACE}$.** Interaction plus randomness is enormously powerful.

**Zero-knowledge proofs** — prove you know something **without revealing it.**

> **The classic illustration:** proving you can 3-colour a graph. Commit to a colouring with all vertices covered; the verifier picks one edge; you reveal just those two vertices, and they differ. **Repeat many times.** Each round leaks nothing (the colours are randomly permuted each time), yet cheating survives $n$ rounds with probability $2^{-n}$.

**Now genuinely deployed:**

- **zk-SNARKs / zk-STARKs** — Zcash's private transactions, Ethereum L2 rollups proving a batch of transactions is valid without re-executing them
- **Authentication without revealing a password**
- **Verifiable computation** — proving an outsourced computation was done correctly

**The PCP theorem** ($\text{NP} = \text{PCP}(\log n, 1)$) says every NP proof can be rewritten so a verifier checking **a constant number of randomly chosen bits** catches errors with high probability. **A startling result**, and it's the foundation of modern inapproximability proofs. → [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]]

## Space complexity

**L** (logarithmic space) — enough for a few counters and pointers, not to store the input. **Streaming algorithms live here.**

**Savitch's theorem: $\text{NSPACE}(f) \subseteq \text{SPACE}(f^2)$**, so $\text{NPSPACE} = \text{PSPACE}$. **Nondeterminism barely helps for space** — a sharp contrast with the open time question.

**Space–time tradeoffs** are the practically useful part: memoisation trades space for time; recomputation trades the other way. **Streaming and sketching algorithms** (HyperLogLog, Count-Min sketch) accept approximate answers in exchange for sublinear space, and they're what makes analytics over billions of events possible.

## Where this touches practice

**Being honest about which parts of this track pay rent:**

**Recognising NP-hardness — high value.** It changes what you build, immediately. **This is the main payoff of the whole domain.**

**Choosing the right tool from the hierarchy — high value.** Regex versus parser, decided by whether structure nests.

**Post-quantum migration — high value, and a live decision** for anything with long-lived secrets.

**Randomised algorithms — high value.** Bloom filters, skip lists, random pivots, sketches. You'll use these.

**Knowing why static analysis is imperfect — moderate.** Explains a class of frustrations and stops you filing impossible feature requests. → [[foundations/theory-of-computation/06-decidability|Decidability]]

**The rest — low, honestly.** The specific inclusions between PSPACE and EXPTIME will not affect your code. **They're worth knowing because they're the shared vocabulary of the literature**, not because they'll come up in a code review.

## The frontier

**Open problems, so you know what's actually unresolved:**

- **P vs NP** — the big one
- **NP vs co-NP** — is there a short proof that a formula is *un*satisfiable?
- **P vs PSPACE**, **NP vs PSPACE**
- **BQP vs NP** — can quantum computers solve NP-complete problems? **Believed no**
- **BPP = P?** — believed yes
- **Circuit lower bounds** — we cannot prove that any explicit NP problem needs super-linear circuits. **This is embarrassing and it's where the difficulty lives**

> **The state of the field, stated plainly: we believe P ≠ NP and cannot prove it, and the known proof techniques are provably insufficient.** Relativisation, natural proofs and algebrization each rule out a broad class of approaches.
>
> **A genuinely new idea is required, and nobody knows what it looks like.** That's an unusual position for a mature field, and it's part of what makes the question interesting rather than merely unsolved.

---

## Related
- [[foundations/theory-of-computation/07-complexity-classes|Complexity Classes]] — P, NP and the reductions
- [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|Cryptographic Best Practices]] — where post-quantum lands
- [[foundations/theory-of-computation/README|Theory of computation map]]
