# The Ethereum Roadmap

**[Intermediate]** — what has actually shipped, what is genuinely coming, and how to read roadmap claims sceptically. Written Aug 2026; **this is the note most likely to age.**

## Why this note exists

Most blockchain material is either breathless about unshipped features or years out of date about shipped ones. The useful skill is **telling those apart** — so this note separates *done*, *specified*, and *aspirational*, and says how to check for yourself.

## Shipped, and worth knowing about

| Upgrade | When | What actually changed |
|---|---|---|
| **London** | Aug 2021 | **EIP-1559** — algorithmic base fee, burned. Fee estimation became predictable |
| **The Merge** | Sep 2022 | PoW → **proof-of-stake**. Energy use dropped ~99.95%. Issuance dropped sharply. **No throughput change whatsoever** — a persistent misconception |
| **Shapella** | Apr 2023 | Staked ETH became withdrawable. Removed the last "your stake is locked forever" risk |
| **Dencun** | Mar 2024 | **EIP-4844 "proto-danksharding"** — blobs: a separate, cheap data lane for rollups, pruned after ~18 days. **L2 fees fell by roughly an order of magnitude.** Also EIP-6780, neutering `SELFDESTRUCT` |
| **Pectra** | 2025 | **EIP-7702** — EOAs can temporarily execute contract code, bringing batching, sponsorship and session keys to ordinary wallets. Plus validator consolidation (EIP-7251) |

**The Merge is the most misreported item here.** It changed consensus, not execution. Anyone who told you it would make Ethereum fast or cheap was wrong about what it was.

## The four remaining tracks

Vitalik's framing splits the roadmap by goal rather than by release. As of Aug 2026 the honest status is:

**The Surge — scalability, via rollups.** The strategy is settled: L1 stays small and verifiable, execution happens on [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|L2s]], L1 provides data availability and settlement. Blobs shipped; **full danksharding** (many more blobs, with data-availability sampling so nodes verify availability without downloading everything) is specified but not shipped. Blob count has been raised incrementally instead.

**The Verge — stateless clients.** Replace the Merkle Patricia Trie with **Verkle trees** (or, in more recent discussion, hash-based alternatives), whose proofs are small enough that a validator can verify a block **without storing any state at all** — it receives a witness alongside the block. This would end the state-growth problem and make running a node genuinely cheap. Long-promised, repeatedly rescoped, **not shipped**.

**The Scourge — MEV and centralisation.** Enshrined proposer-builder separation, inclusion lists to resist censorship, and mitigations for liquid-staking concentration. **The least technically defined track and the most politically difficult**, because it's about power distribution rather than mechanism → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]].

**The Purge — deleting things.** State expiry, history expiry (**EIP-4444**, clients drop blocks older than a year — shifting archival to dedicated providers), and removing accumulated protocol cruft. Unglamorous and arguably the most important for long-term node viability.

*(A fifth, "the Splurge," collects everything else — EVM improvements like EOF, account abstraction, cryptographic upgrades.)*

## How to read roadmap claims

Four habits that will keep you accurate:

1. **Distinguish "an EIP exists" from "it's scheduled."** Anyone can write an EIP. Inclusion in a named upgrade is the real signal — check the upgrade's meta-EIP for the final list
2. **Assume slippage.** Every major Ethereum upgrade has shipped later than announced, several by years. This is a consequence of not being able to roll back a live system holding hundreds of billions of dollars, and it's the correct trade
3. **Watch what shipped, not what was promised.** Dencun's blob market is a bigger deal for actual users than most of what's been announced since
4. **Check primary sources.** `ethereum.org/roadmap`, the EIP repository, All Core Devs call notes. Every secondary source has an incentive

## What this means practically

**Build for rollups, not L1.** The scaling strategy is decided and blobs made it economically real. New applications with meaningful transaction volume belong on an L2, with L1 for settlement and high-value operations.

**Don't wait for anything.** Verkle trees have been "next" for years. Design for the chain as it exists.

**Expect gas semantics to shift.** Repricings happen in most upgrades. Contracts hardcoding gas amounts break — which is why hardcoded gas stipends are considered an anti-pattern, and `.transfer()`'s fixed 2300 is the canonical example of the lesson being learned the expensive way.

## Key insight

**Ethereum's roadmap is a decade-long bet that decentralisation is preserved by making verification cheap rather than execution fast.** Every track serves that: rollups move execution off L1, statelessness removes the storage requirement, history expiry removes the archival requirement. The goal isn't a fast chain — it's a chain a laptop can still verify in 2040.

## Related
- [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|layer 2s and rollups]] — where the scaling actually happens
- [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the scalability trilemma]] — the constraint being navigated
- [[web3/01-foundations/05-consensus|consensus]] — what the Merge changed
- [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|the state trie]] — what the Verge replaces

*Source: [reference] — accurate as of Aug 2026, and deliberately dated. Verify against ethereum.org/roadmap before relying on the "not shipped" claims.*
