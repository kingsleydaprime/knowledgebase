# Layer 2s and Rollups

**[Advanced]** — how rollups actually work, optimistic vs zk, and the centralisation everyone glosses over.

## The kid version first

Instead of every computer in the world doing your maths, **one fast computer does it and then proves it did it right.** Everyone else checks the proof, which is much cheaper than redoing the work.

The catch is that the fast computer must also **publish everything it did**, so that if it lies, anyone can prove it lied — and so that if it disappears, everyone can rebuild the state without it.

## What makes something a rollup

Two properties, and both are required:

1. **Execution happens off-chain**, by a sequencer
2. **Transaction data is published on L1**, and correctness is enforced by L1 — either by a validity proof, or by a challenge window

**Property 2 is what separates a rollup from a sidechain.** A sidechain (Polygon PoS in its original form, BNB Chain) has its own consensus and its own security. **If a sidechain's validators collude, your funds are gone and Ethereum cannot help you.** A rollup inherits L1's security for state correctness, because L1 has the data and can verify the result.

Marketing calls both "L2." **They are not the same risk**, and it's the first thing to check about any chain claiming L2 status.

## Optimistic rollups

**Assume every batch is valid. Let anyone challenge.**

```
sequencer posts a state root + transaction data to L1
        │
   7-day challenge window
        │
   anyone can submit a FRAUD PROOF: re-execute and show the root is wrong
        │
   unchallenged → final
```

**The 7-day window is the defining cost.** Withdrawing to L1 takes a week, because that's how long the challenge period runs. Third-party "fast bridges" front the money for a fee and wait out the window themselves — a workaround, with its own counterparty risk.

**Why seven days?** It must exceed any plausible censorship attack: if an attacker could stop honest challengers from getting transactions onto L1 for the whole window, fraud goes unchallenged. Seven days is a deliberately paranoid margin.

**Arbitrum** and **Optimism / the OP Stack** are the major implementations. Both use interactive fraud proofs that bisect the disputed computation down to a single instruction, so L1 executes only that one step rather than the whole batch — an elegant trick worth understanding.

**The honest caveat:** fraud proofs were **permissioned or incomplete on major optimistic rollups for years after launch**, which meant the security model was "trust the operator" while marketed as trustless. This has improved substantially (Arbitrum's BoLD, OP's fault proofs) but check the current state per chain rather than assuming — L2Beat tracks it honestly and is the right reference.

## ZK rollups

**Prove every batch is valid. No challenge needed.**

```
sequencer executes, generates a VALIDITY PROOF (a SNARK/STARK)
        │
L1 verifies the proof — cheap and constant-cost
        │
   valid → FINAL IMMEDIATELY. No window
```

**Withdrawals are as fast as proof generation** (minutes to hours), not seven days. There is no fraud to challenge because invalid state transitions cannot be proved.

The cost is proving: generating a proof of general EVM execution is computationally expensive, which is why zk rollups took years longer to ship. **zkSync Era, Scroll, Linea, Polygon zkEVM and Starknet** are the main ones.

**"zkEVM" comes in degrees** — from bytecode-identical with Ethereum (hardest to prove, perfect compatibility) to a different VM with a Solidity compiler (fastest to prove, subtle incompatibilities). Starknet uses its own VM and language (Cairo), which is why it's fast and why porting to it is real work.

## The comparison

| | Optimistic | ZK |
|---|---|---|
| Withdrawal to L1 | **~7 days** | Minutes to hours |
| L1 cost per batch | Cheap (data only) | Data + proof verification |
| Off-chain cost | Low | **High** (proving) |
| EVM compatibility | Essentially perfect | Good to excellent, varies |
| Security rests on | ≥1 honest challenger, and censorship resistance | **Mathematics** |
| Maturity | Earlier, more TVL | Catching up fast |

**The consensus view is that zk wins long-term** — no challenge window, no liveness assumption about challengers, and proving costs keep falling. Optimistic rollups had a multi-year head start and the ecosystem lock-in that comes with it.

## The centralisation nobody advertises

**Almost every rollup runs a single sequencer, operated by the company that built it.**

What that sequencer can do:
- **Censor** your transactions — refuse to include them
- **Reorder** them, capturing all the MEV → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]]
- **Halt** the chain by going offline

What it **cannot** do: steal your funds or forge invalid state. The proof or challenge mechanism prevents that, and that is a genuinely meaningful guarantee.

**The escape hatch is `forced inclusion`:** most rollups let you submit a transaction directly to an L1 contract, which the sequencer must include within a deadline. That's the real censorship resistance, and it's why a censoring sequencer is an inconvenience rather than a capture. **Verify it exists and works before treating a rollup as trust-minimised** — the delay is typically hours to a day.

**And the upgrade keys.** Most rollups' L1 contracts are upgradeable by a multisig, which can, in principle, replace the bridge with one that drains it. **L2Beat's "Stage 0/1/2" classification tracks exactly this**, and it is the single most useful resource for reading past L2 marketing.

## Validiums, and where the data goes

A **validium** uses validity proofs but posts data **off-chain**. Much cheaper, and a different security model: if the data-availability committee withholds data, **you cannot prove your own balance and cannot withdraw.** Funds aren't stealable but can be frozen.

This is the modular-DA question: Celestia, EigenDA and Avail sell data availability as a service, cheaper than Ethereum blobs with weaker guarantees. **"L2" now spans a wide risk range, and the data-availability choice is the main axis** → [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the trilemma]].

## Practically, for building

- **Build on an L2.** Fees are cents; on L1 they're dollars. For anything with real transaction volume this isn't close
- **The EVM is the same.** Solidity, Foundry and OpenZeppelin work unchanged on EVM-equivalent L2s
- **What differs:** gas is much cheaper but **L1 data posting is a real cost component**, so calldata size matters more than execution; `block.timestamp` and `block.number` have chain-specific semantics; and **`block.number` on some L2s does not advance as you'd expect** — never use it for timing
- **Check the sequencer's uptime feed** if you use Chainlink, and handle the down case → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|oracles]]
- **Bridging is where users lose money** → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]]

## Key insight

**A rollup buys throughput by replacing "everyone re-executes" with "everyone verifies a proof", and pays for it with a centralised sequencer plus an upgrade multisig.** The state-correctness guarantee is real and mathematical; the censorship and liveness guarantees are social and improving. Read any L2 by asking three questions: **can the sequencer be bypassed, who holds the upgrade keys, and where is the data published?**

## Related
- [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge proofs]] — the machinery under zk rollups
- [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the trilemma]]
- [[web3/02-ethereum-and-the-evm/06-the-ethereum-roadmap|the Ethereum roadmap]] — why this is the strategy
- [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]]

*Source: [reference] — Aug 2026. Check L2Beat for current per-chain status; this area moves fast.*
