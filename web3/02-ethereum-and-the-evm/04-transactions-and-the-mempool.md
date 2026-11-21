---
id: 4de029d4-4d2e-41dc-ac0b-cfca4abf2f23
---

# Transactions and the Mempool

## The nonce, and the three bugs it causes
<!-- bite: ef354382-ad65-46fd-8bc7-2bf408e45bdc -->

Every EOA has a nonce: a counter that must increase **by exactly one, in order**, across its transactions. It's what prevents replay and forces a per-account sequence.

**Bug 1 — the blocking gap.** Send nonces 5, 6, 7. If 5 is underpriced and stalls, **6 and 7 cannot execute** no matter what they pay. The account is stuck until 5 is mined or replaced. Users read this as "my wallet is frozen."

**Bug 2 — pending vs latest.** `eth_getTransactionCount(addr, "latest")` returns the mined count; `"pending"` includes the mempool. A backend sending several transactions quickly and querying `"latest"` will **assign the same nonce repeatedly**, and all but one fail. Any system sending concurrent transactions needs its own nonce manager with a lock, not an RPC query per send.

**Bug 3 — replacement rules.** To replace a pending transaction you resubmit with the **same nonce** and a fee bumped by at least ~10% (a client policy, not consensus). Bump too little and the replacement is silently dropped, leaving you convinced you cancelled something you didn't.

## Transaction types
<!-- bite: b419f4fe-2117-4590-9e89-6a6e6a9a0b1c -->

Ethereum's typed-transaction envelope (EIP-2718) let new formats ship without breaking old ones:

| Type | Introduced | What it added |
|---|---|---|
| **0** | genesis | Legacy: a single `gasPrice` |
| **1** | Berlin | Optional access lists (pre-declare touched slots for a cold-access discount) |
| **2** | London, 2021 | **EIP-1559**: `maxFeePerGas` / `maxPriorityFeePerGas`. The current default |
| **3** | Dencun, 2024 | **Blob-carrying** — the rollup data path |
| **4** | Pectra, 2025 | **EIP-7702**: an EOA can temporarily execute contract code, bringing much of account abstraction to ordinary accounts |

**EIP-7702 is the most consequential of these for application developers** — it lets a normal wallet batch operations, use a sponsor to pay gas, and apply session keys, without migrating to a separate smart-contract wallet → [[web3/06-building-dapps/07-account-abstraction|account abstraction]].

## The mempool is a public queue, and that is the problem
<!-- bite: 0087ce89-8f04-44bc-bece-07c6f61b52c9 -->

A pending transaction is broadcast to thousands of nodes before it executes. In that window it is **a signed, public, precise statement of what you are about to do** — and anyone can act on it first.

```
you broadcast:  "swap 100 ETH for USDC, accept up to 2% slippage"
                        │
                 everyone sees it
                        │
    a searcher: buys USDC ahead of you (price rises)
                your swap executes at the worse price
                they sell into your impact, pocket the difference
```

**That's a sandwich attack, and it is routine, automated, and legal.** It is the single most important reason to understand that the mempool is adversarial rather than a queue → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]].

Mitigations that exist today: **private transaction relays** (Flashbots Protect and similar) that bypass the public mempool and submit straight to builders; tight slippage limits; commit-reveal schemes for anything where the *content* must stay secret until execution.

## PBS — who actually builds blocks now
<!-- bite: bc1bf05a-291f-4bb7-99a8-091578ff8b83 -->

Since the Merge, block construction is separated from block proposal (**proposer-builder separation**, in practice via MEV-Boost):

```
searchers  →  bundles of profitable ordering
    ↓
builders   →  assemble full blocks, bid for the right to have theirs used
    ↓
relays     →  hold the block, reveal only after the proposer commits
    ↓
proposer   →  signs the highest-bidding header, usually without seeing its contents
```

This is worth knowing precisely because of what it implies: **most Ethereum blocks are built by a small number of specialised builders**, and the validator signing them typically has not inspected the contents. It's a real centralisation vector in an otherwise decentralised layer, openly discussed and not yet solved. Enshrined PBS and inclusion lists are the main proposed fixes.

## Reading a receipt
<!-- bite: 22523660-8622-494f-b487-a4f27414149c -->

After inclusion you get a receipt: `status` (1 success, 0 revert), `gasUsed`, `logs`, `blockNumber`, `effectiveGasPrice`.

**A receipt with `status: 0` still consumed gas and still occupies a nonce.** "The transaction failed" and "the transaction didn't happen" are different states, and conflating them is a common backend bug — a failed payment transaction is still a real, permanent, paid-for entry in history.

**Never treat one confirmation as final.** Wait for the depth your risk tolerance justifies, or for the consensus layer's `finalized` tag (~13 minutes on Ethereum), and design for the block you just processed being reorged away → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## Key insight
<!-- bite: e8a32ea9-5437-48fe-9e5a-d56b56fbe561 -->

**Between broadcast and inclusion, your transaction is public intent that others can profit from.** Everything unusual about interacting with a chain — slippage limits, deadlines, commit-reveal, private relays, nonce managers — exists because that window is adversarial rather than a queue.

## Related
<!-- bite: e6c12e84-7f1e-40f5-b543-d278ff06751f -->
- [[web3/01-foundations/06-networking-and-nodes|networking and nodes]] — how it propagates
- [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]] — the full picture
- [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas and fees]]
- [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading and writing chain state]]

## About this lesson
<!-- bite: b3a18afd-d92d-4db6-b0d6-9fdd6479534d -->

**Level:** Intermediate. **Covers:** the nonce rules that trip everyone up, transaction types, and why the gap between "sent" and "mined" is an adversarial environment.

*Source: [reference] — Aug 2026.*
