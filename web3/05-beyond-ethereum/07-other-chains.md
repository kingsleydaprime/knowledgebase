# The Rest of the Landscape

**[Intermediate]** — the other design families worth knowing, in one note, and how to evaluate a chain you've never heard of.

## Why one note

There are hundreds of chains. **Most are EVM forks with different validators and a marketing budget** — learning them individually teaches you almost nothing. What's worth knowing is the handful of genuinely *different* designs, and a method for assessing the rest quickly.

## The genuinely different ones

**Cosmos — application-specific chains.** Rather than one chain hosting many applications, each application gets its *own* chain, built with the Cosmos SDK and connected by **IBC** (Inter-Blockchain Communication).

IBC is the interesting part: **a light-client-based messaging protocol** where each chain verifies the other's consensus directly, in-protocol. **No multisig, no external committee** — which is precisely the model that would have prevented most bridge hacks → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]]. It works because Tendermint gives instant finality, making light-client verification tractable. Trading off: your chain needs its own validator set and its own security budget.

**Polkadot — shared security.** Parachains lease slots on a central Relay Chain, which validates all of them. **You get a custom chain without bootstrapping validators.** Elegant, and constrained by a limited number of slots that must be won at auction — a real adoption bottleneck.

**Move-based chains: Aptos, Sui.** Both from ex-Meta Diem engineers, both using **Move** — a language where **assets are first-class linear types.** A `Coin` resource cannot be copied or accidentally discarded; the type system enforces conservation of value at compile time.

**This directly attacks a whole vulnerability class.** In Solidity a token balance is just a number in a mapping, and every bug that creates value from nothing is a number being wrong. In Move that's a type error. Genuinely interesting language design, smaller ecosystem → [[foundations/programming-language-theory/07-effects-and-substructural-types|substructural types]].

Sui adds an object-centric model with parallel execution for transactions on independent objects, similar in spirit to Solana's declared accounts.

**Near — sharding, with usable accounts.** Actually-deployed sharding, plus human-readable account names and a much better onboarding story than most chains.

**Cardano — extended UTXO.** UTXO with programmability bolted on, plus a formal-methods-heavy development culture (peer-reviewed papers before implementation). Slow to ship; the eUTXO model has genuinely different properties from both Bitcoin's and Ethereum's.

**Tron.** Worth knowing for one reason: **it carries an enormous share of global USDT transfer volume**, particularly for remittances in emerging markets, on account of very low fees. Technically unremarkable and highly centralised; practically, a large amount of the world's actual stablecoin usage happens there → [[web3/07-the-application-layer/01-defi-primitives|stablecoins]].

## The EVM chains

**BNB Chain, Avalanche C-Chain, Polygon PoS, Fantom, Base, Arbitrum, Optimism** — from an application developer's view these are largely interchangeable: same Solidity, same tooling, same OpenZeppelin.

**What actually differs:** validator count and who they are; whether it's a genuine rollup or a sidechain (**very different security** → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]]); fee levels; and which liquidity and users are already there.

**"EVM-compatible" is now table stakes**, which is itself the interesting fact: the EVM became the field's de-facto standard instruction set, so a chain adopting it inherits a decade of tooling instantly. That's a strong network effect and it's why so few chains attempt their own VM.

## Evaluating an unfamiliar chain — the checklist

Six questions, in order. They resolve most chains in ten minutes:

1. **How many validators, run by how many independent entities, on what hardware?** This is the decentralisation answer, and it's usually available and usually unflattering
2. **What's the consensus, and does it halt or fork under partition?** → [[web3/01-foundations/05-consensus|consensus]]
3. **Is it a rollup, a sidechain, or an L1?** Marketing blurs this deliberately. A sidechain's security is its own validators, full stop
4. **Who can upgrade the chain or its bridge contracts, and is there a timelock?**
5. **What's the actual, sustained throughput and fee level?** Not the benchmark
6. **Where's the liquidity and where are the users?** A technically superior chain with no ecosystem is a worse place to build

**And the one that cuts through most of it:** *what does this chain do that an existing one doesn't?* For a large majority the honest answer is "the same thing, with a token we issued" — and **launching a chain has been a business model more often than a technical necessity.**

## What's actually converging

Across all the variety, the field is settling on a few things:

- **The EVM as a standard target**, with alternative VMs as a deliberate differentiator rather than a default
- **Parallel execution via declared state access** — Solana, Sui, and Ethereum's access-list discussions all point the same way
- **Proof-of-stake.** Proof-of-work outside Bitcoin is essentially finished
- **zk proofs for cross-chain verification** — the credible answer to the bridge problem
- **Rollups and app-chains over monolithic L1s** — though [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]] keeps that argument genuinely open

## Key insight

**Chain diversity is mostly business diversity, not technical diversity.** The genuinely different designs number maybe half a dozen — Bitcoin's UTXO, Ethereum's accounts, Solana's parallel execution, Move's linear types, Cosmos's app-chains with light-client messaging. Everything else is a parameter change. Learn the design families and you can place any new chain in five minutes.

## Related
- [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the trilemma]] — what they're all trading
- [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]] · [[web3/05-beyond-ethereum/05-bitcoin-and-utxo|Bitcoin]]
- [[web3/frameworks/rust/README|Rust for web3]] — Solana, CosmWasm, ink!
- [[foundations/programming-language-theory/07-effects-and-substructural-types|substructural types]] — the theory behind Move

*Source: [reference] — Aug 2026.*
