---
id: 553ce055-2052-4dc5-b76f-bdda175b554a
---

# Zero-Knowledge Proofs

**[Advanced]** — proving you know something without revealing it, why the *succinctness* matters more than the zero-knowledge part, and what's actually deployed.

## The kid version first
<!-- bite: 1f34938e-92f6-4def-8ef9-68d655a5d56b -->

You want to prove you know the password without saying the password. Or prove you're over 18 without showing your birthday. Or — the one that actually matters here — **prove you ran a million computations correctly, using a proof so small the checker can verify it in milliseconds without redoing any of the work.**

That last one is why blockchains care. The privacy is a bonus; **the compression of computation is the product.**

## The two properties, and which one pays
<!-- bite: 2f66ee02-f842-48b1-b71a-aeb3f545840c -->

A **zk-SNARK** (Succinct Non-interactive ARgument of Knowledge) gives you:

1. **Zero-knowledge** — the verifier learns nothing except that the statement is true
2. **Succinctness** — the proof is small (hundreds of bytes) and fast to verify (milliseconds), **regardless of how much computation it attests to**

**Property 2 is what rollups are built on.** Proving "I executed 10,000 transactions and this is the resulting state root" produces the same size proof as proving one transaction. **Verification cost decouples from computation cost**, and that is the entire scaling argument → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]].

Most "zk rollups" barely use property 1. They're **validity rollups** — public data, public transactions, just proved. The name stuck for historical reasons and it confuses people constantly.

## The intuition, without the maths
<!-- bite: 1b1fd99c-86f6-49d9-8ea7-b9d9385eaa5e -->

Three moves, each of which is a whole research area:

**1. Arithmetisation.** Turn "this program ran correctly" into "these polynomial equations hold." A computation becomes a set of constraints — a **circuit** — where a valid execution trace is exactly a solution.

**2. Polynomial commitment.** Commit to a polynomial with a short value, such that you can later be challenged to reveal its value at any point and cannot lie. KZG commitments (used by Ethereum's blobs, incidentally) and FRI are the two main families.

**3. Random challenge.** The verifier picks random points and asks for evaluations. **Two different polynomials agree at very few points**, so passing a handful of random checks means the prover almost certainly has the real thing. The Fiat–Shamir transform replaces the interactive verifier with a hash, making it non-interactive — which is what lets a proof be posted to a chain and checked by anyone later.

**Where the cost goes:** proving is expensive (seconds to minutes, lots of RAM), verifying is cheap. **The asymmetry is the point.** Ethereum's BN254 pairing precompiles exist specifically to make on-chain verification affordable → [[web3/02-ethereum-and-the-evm/02-the-evm|precompiles]].

## SNARKs vs STARKs
<!-- bite: 1dc45db7-75e5-42a3-a064-167e35e052f5 -->

| | SNARK (Groth16, PLONK) | STARK |
|---|---|---|
| Proof size | **~200 bytes** | ~50–200 KB |
| Verification | Cheapest | More expensive |
| Trusted setup | **Groth16: per-circuit. PLONK: universal** | **None** |
| Post-quantum | No (elliptic curves) | **Yes** (hashes only) |
| Prover speed | Slower | Faster, scales better |
| Used by | zkSync, Scroll, Polygon | Starknet, Polygon Miden |

**The trusted setup is the awkward part of SNARKs.** Some schemes need a one-time ceremony producing public parameters from secret randomness that **must** be destroyed — anyone retaining it can forge proofs. Mitigated by multi-party ceremonies where **only one participant needs to have been honest** (Ethereum's KZG ceremony had over 140,000 contributors). It's a real assumption, adequately addressed, and a legitimate reason to prefer STARKs.

## What's actually deployed
<!-- bite: 9b09b40d-99ec-47a9-8263-22bae3810b4c -->

**Scaling — the dominant use.** Every zk rollup. This is where the money and the engineering are.

**Private payments.** Zcash (shielded transactions) and Tornado Cash (an Ethereum mixer). **Tornado Cash is the cautionary tale**: OFAC-sanctioned in August 2022, and a developer was prosecuted and convicted in the Netherlands. **Writing privacy software has demonstrated legal risk**, which is a fact about the field rather than an opinion about it → [[web3/08-the-honest-assessment/03-regulation-and-the-legal-layer|regulation]].

**Identity and credentials.** Prove "I am over 18" or "I am on this allowlist" without revealing which member you are. Semaphore, and Ethereum's zk-email work. **The most promising non-financial application**, and still mostly early.

**Light clients and bridges.** Prove one chain's consensus to another without trusting a committee — the most credible answer to the bridge problem → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]].

**zkML.** Proving a model produced a given output. Real research, largely impractical at useful model sizes as of 2026.

## Writing them
<!-- bite: 39ba9c74-27a0-48cd-bd88-7e7bb1461afb -->

You don't implement the cryptography; you write **circuits**:

- **Circom** — a low-level circuit DSL. Most control, most footguns
- **Noir** (Aztec) — Rust-like, the most approachable entry point today
- **Cairo** (Starknet) — a full language whose execution is provable by construction
- **Halo2**, **RISC Zero**, **SP1** — the zkVM approach: **write ordinary Rust, prove its execution.** Much easier, less efficient, and the direction the field is clearly heading

**The dominant footgun is under-constraining.** A circuit that doesn't fully constrain its witness accepts proofs of false statements — and it **passes all your tests**, because tests exercise valid inputs. This is the zk equivalent of a missing access-control check, it's the main finding in zk audits, and it requires specialist review.

## The honest assessment
<!-- bite: 8e62ea60-e83e-4d81-9d54-bd7164c8984c -->

**Genuinely transformative:** verifiable computation with constant-cost verification is a real primitive that didn't exist before, and rollups have made it economically significant.

**Genuinely hard:** proving costs, developer experience, and a very small pool of engineers who can audit circuits.

**Genuinely overhyped:** "zk" is applied as a marketing prefix to things that use no proofs at all. And **privacy applications face regulatory pressure that has nothing to do with whether the cryptography works** — which is the constraint that has actually limited deployment, not the maths.

## Key insight
<!-- bite: 5ae32209-72e1-413e-8d09-d869ec890a38 -->

**The valuable property is succinctness, not zero-knowledge.** A short, cheap-to-verify proof that arbitrary computation was performed correctly decouples verification cost from execution cost — and that is what makes blockchain scaling possible without giving up verifiability. The privacy property is real, powerful, and, in practice, the one that attracts prosecutions.

## Related
<!-- bite: 18d950ea-6af9-416b-b569-565dff283ba3 -->
- [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]] — the main application
- [[cybersecurity/05-cryptography/index|cryptography]] — the foundations
- [[mathematics/02-discrete-math/08-number-theory-and-modular-arithmetic|number theory]] — the maths underneath
- [[theory-of-computation/08-beyond-p-vs-np|beyond P vs NP]] — the complexity-theory framing of "verifying is easier than solving"

*Source: [reference] — Aug 2026.*
