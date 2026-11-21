---
id: 96d49579-0fcf-49dd-a1a0-c24532154273
---

# The Scalability Trilemma

The scalability trilemma is the claim that a blockchain can't easily be open to everyone, safe from attack, and fast all at once, so it usually has to pick two. It explains why Bitcoin and Ethereum are slow and costly to use while some newer chains are fast but run by fewer computers. This lesson looks at how true that claim is.

## The claim
<!-- bite: a0aa8f72-a219-471e-8536-aa9bbfd11321 -->

**Decentralisation, security, scalability — pick two.**

- **Decentralisation** — many independent participants can verify the chain on affordable hardware
- **Security** — attacking it costs more than it yields
- **Scalability** — high throughput at low cost

It's a heuristic rather than a theorem, but it captures a real constraint, and it's the single most useful lens for evaluating chain claims.

## Why the tension is real
<!-- bite: 52ab9b7a-7626-4ad6-adfa-f475fe32e37a -->

**Every node executes every transaction.** That's what makes the chain verifiable without trust — and it means **throughput is capped by what the *weakest* participating node can handle.**

To go faster you must raise the requirements: more CPU to execute, more bandwidth to receive blocks, more disk to store state. Raise them enough and home nodes drop out. **What remains is a fast chain verified by a handful of data centres** — which is a database with extra latency.

```text
raise the gas limit
   → bigger blocks
      → more bandwidth and disk needed to keep up
         → fewer people can run a node
            → fewer independent verifiers
               → decentralisation falls
```

**Note that bandwidth, not CPU, is usually the binding constraint** — which is unintuitive, and it's why "hardware is getting faster" doesn't dissolve the problem.

## How each design chooses
<!-- bite: 4485600a-cda9-4828-abc9-4186ba168463 -->

| Chain | Trade |
|---|---|
| **Bitcoin** | Maximum decentralisation and security. ~7 TPS. Deliberate, and the 2015–17 block-size war was fought precisely over refusing to trade it |
| **Ethereum L1** | Decentralisation and security first; scaling delegated to L2s. ~15–100 TPS |
| **Solana** | Scalability first. ~3,000+ real TPS, at validator hardware requirements that put a node in a data centre. **Has halted several times** |
| **BNB Chain** | Scalability, with ~40 validators. Fast, cheap, and decentralised mainly as a claim |
| **Rollups** | **Attempt to escape the trilemma** rather than trade within it — see below |

## Reading TPS claims
<!-- bite: 4f1c21a2-2c1b-4f1b-a848-2ff8bcae3d98 -->

**Almost every headline TPS figure is theoretical maximum under ideal conditions**, and the gap to reality is usually an order of magnitude. Questions that deflate most of them:

1. **How many validators, and what hardware do they need?** 21 validators on 64-core servers is a distributed database
2. **Is that sustained or peak?** Benchmarks measure bursts; state growth is what bites
3. **What are the transactions?** Simple transfers are cheap; contract calls are not. Many benchmarks measure transfers and quote the number for everything
4. **Where does state live in five years?** A chain doing 50,000 TPS accumulates state faster than consumer disks grow. **Nobody can run a node eventually** is a slow failure mode that benchmarks don't show
5. **Has it halted?** Liveness under real load is the actual test, and several high-TPS chains have failed it publicly

## The rollup escape
<!-- bite: 6e0dde7b-b2f7-4a3d-a5f1-29a8f4227a45 -->

The insight behind Ethereum's strategy: **the trilemma binds because every node re-executes everything. So don't re-execute — verify a proof instead.**

```text
Execution happens off-chain, on a rollup, with one sequencer

    ↓ posts compressed transaction data + a validity proof (or a fraud window)

L1 verifies the PROOF, not the execution
```

Verifying a zk proof is roughly constant-cost regardless of how much computation it attests to. **So L1 can secure thousands of L2 transactions for the cost of verifying one proof.** The rollup can use fast hardware and one sequencer, because its correctness is guaranteed by the proof rather than by its own decentralisation.

**What's genuinely escaped and what isn't:**

- **Escaped:** execution throughput. Real, and it works
- **Not escaped:** **data availability.** The transaction data must be published somewhere anyone can read, or nobody can reconstruct state or prove fraud. Publishing that data is now the binding constraint — which is exactly what EIP-4844 blobs addressed, and why L2 fees fell an order of magnitude in 2024
- **Not escaped:** sequencer centralisation. Most rollups run one sequencer, which can censor and reorder → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]]

## Modular vs monolithic
<!-- bite: d51af6d3-391c-47b7-9e5f-53519d443abb -->

The framing this produced:

- **Monolithic** (Solana, Bitcoin) — one chain does execution, settlement, consensus and data availability. Simpler, tightly optimised, and bounded by the trilemma
- **Modular** (Ethereum + rollups + Celestia) — each layer specialises. More scalable, more complex, and the seams between layers are where bridges live — and **bridges are where the largest losses in the field have occurred** → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]]

Neither has won. Solana's monolithic bet is the strongest counter-argument to the modular thesis, and it is doing well enough to keep the question open.

## Key insight
<!-- bite: 3fac9c7c-663d-469f-aad4-f34bdeff2967 -->

**The trilemma is really a statement about verification cost.** Decentralisation means many people can independently check the chain, and that caps throughput at the weakest checker. Rollups don't repeal it — they change what gets checked from *execution* to *a proof*, which is a genuine escape for computation and not for data availability. Any scaling claim should be read by asking: **what is a node still required to verify, and on what hardware?**

## Related
<!-- bite: 173f8841-48ca-45c6-8668-49811b571e2e -->
- [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|layer 2s and rollups]] — the escape, in detail
- [[web3/01-foundations/06-networking-and-nodes|networking and nodes]] — the bandwidth constraint
- [[web3/01-foundations/05-consensus|consensus]]
- [[architecture/04-distributed-systems/index|distributed systems]] — the general trade-offs

## About this lesson
<!-- bite: 1f44d4f8-0b48-401a-bccd-67aa97b2a677 -->

**Level:** Intermediate. **Covers:** the constraint every chain design is navigating, and how to read a "100,000 TPS" claim.

*Source: [reference] — Aug 2026.*
