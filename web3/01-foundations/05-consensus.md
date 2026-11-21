---
id: 92d64d45-0b17-454e-a1b2-b150b22d9c16
---

# Consensus — Who Gets to Write

## The kid version first
<!-- bite: 01903cb9-1b42-4492-825e-4d3792649621 -->

Thousands of computers all want to add the next page to the shared notebook. **Only one page can be next.** How do they pick, when anyone can join, nobody's in charge, and some of them are lying?

Every answer has the same shape: **make trying to write cost something real, and make it so the cheapest way to profit is to follow the rules.** Proof-of-work burns electricity. Proof-of-stake risks money. The mechanism differs; the logic doesn't.

## What consensus must actually deliver
<!-- bite: 6cde6391-2c50-410e-b30d-8fe5cf339f67 -->

Three properties, and they're in tension:

1. **Safety** — no two honest nodes accept conflicting histories. "Nothing bad happens"
2. **Liveness** — the chain keeps producing blocks. "Something good eventually happens"
3. **Sybil resistance** — influence can't be bought by creating identities

[[architecture/04-distributed-systems/02-theoretical-limits|FLP]] says that in a fully asynchronous network, no deterministic protocol can guarantee consensus *terminates* if even one process may fail — so safety and liveness cannot both be guaranteed unconditionally. **Every real design picks which one to sacrifice under partition** — and that choice is the cleanest way to classify chains:

| Under a network partition | Behaviour | Examples |
|---|---|---|
| **Favour liveness** | Keeps producing blocks; may temporarily fork, resolves later. Finality is probabilistic | Bitcoin, Ethereum's fork-choice layer |
| **Favour safety** | Halts rather than risk a conflicting commit. Finality is instant and absolute | Tendermint/Cosmos, and Ethereum's finality layer |

Ethereum post-Merge is a **hybrid** running both — a fork-choice rule that keeps producing, plus a finality gadget that periodically stamps blocks as irreversible. That combination is the main thing to understand about modern PoS.

## Proof-of-Work
<!-- bite: 9ca34e4d-2fb5-4819-891e-4398b7c8af7c -->

Find a nonce such that `hash(block_header ‖ nonce) < target`. There is no method but guessing, so the only strategy is to guess fast. Difficulty auto-adjusts to hold a target block time (Bitcoin: 10 minutes, retargeting every 2016 blocks).

**Why it works:** you can't fake having done the work, and you can't do it cheaply. Influence tracks hashrate, and hashrate costs hardware and electricity — things Sybil identities can't conjure.

**Fork choice:** the valid chain with the **most cumulative work** wins. Not the longest — cumulative difficulty, which matters when difficulty changes.

**Finality is probabilistic.** Reversing *k* blocks requires out-working the network across all of them. Each confirmation makes reversal exponentially more expensive, never impossible. Six confirmations is convention, not a proof.

**The honest costs:** enormous energy use, whose magnitude is the security budget and can't be optimised away; centralisation into pools and cheap-power regions; and hardware that must keep running forever to keep the chain secure → [[web3/08-the-honest-assessment/04-energy-and-the-externalities|energy]].

## Proof-of-Stake
<!-- bite: b5cf162f-4569-4caa-b616-0ccfd9885ad6 -->

Replace "burn electricity" with "lock up capital." Validators deposit the native asset (32 ETH on Ethereum); the protocol pseudo-randomly selects proposers and committees; misbehaviour is punished by **slashing** — destroying part of the deposit.

**The key improvement over PoW is not energy. It's that the punishment is *in-protocol*.** A PoW attacker who fails loses only electricity and keeps their hardware; a PoS attacker who equivocates has their capital destroyed by the very chain they attacked. Attacks become **directly, automatically expensive** rather than merely wasteful.

**Nothing-at-stake, solved:** the early objection was that signing every competing fork costs a validator nothing. Slashing for equivocation makes it cost everything. That is the whole answer, and it's why slashing is load-bearing rather than a nicety.

**Ethereum's structure specifically** (post-Merge, 2022):
- Time is divided into 12-second **slots** and 32-slot **epochs**
- One validator proposes per slot; a committee attests
- Attestations accumulate; when two-thirds of stake attests across two consecutive epochs, blocks are **finalised** — reversal would require destroying at least a third of all staked ETH. That is finality with a price tag attached, and the price is public
- Fork choice between finality checkpoints is **LMD-GHOST**, which follows the subtree with the most attestation weight rather than simply the longest chain

**The honest costs:** wealth concentration compounds (stake earns stake); liquid-staking providers re-centralise what the design decentralised — Lido's share of staked ETH has been a live governance concern for years; and validators must stay online or bleed value, which pushes them to the same handful of cloud providers.

## Classical BFT — the third family
<!-- bite: 4a52916e-84a8-49a6-b2e9-7c64ee48ff17 -->

**PBFT and descendants (Tendermint)** run explicit voting rounds: propose → pre-vote → pre-commit, tolerating up to *f* faults among *3f+1* validators. Commit means **committed** — instant, absolute finality, no reorgs ever.

The trade: **you must know the validator set**, and message complexity is O(n²), so it doesn't scale past low hundreds of validators. If the set can't reach two-thirds, **the chain stops** — Cosmos chains have halted in production, by design rather than by failure. That's safety chosen over liveness, explicitly.

## Comparison
<!-- bite: 9ed125a4-7982-4519-9bda-91a2ece6079a -->

| | PoW | PoS (Ethereum) | BFT (Tendermint) |
|---|---|---|---|
| Sybil resistance | Hashrate | Staked capital | Known validator set |
| Finality | Probabilistic | ~13 min, economic | Instant, absolute |
| Under partition | Keeps going, forks | Keeps going, stops finalising | **Halts** |
| Validator count | Unbounded | ~1M (Ethereum, 2026) | Low hundreds |
| Attack cost | Rent hashrate | Buy + lose stake | Corrupt ⅓ of a known set |
| Energy | Enormous | Negligible | Negligible |

## The 51% attack, precisely
<!-- bite: 6bd99980-8101-4b75-bf91-99aff2538f6f -->

Majority control does **not** let an attacker steal coins or forge signatures — no amount of hashrate breaks ECDSA. What it lets them do is:

- **Reorder and censor** transactions
- **Double-spend their own coins** by publishing a longer chain that omits a transaction they already got paid for

That's the entire threat, and it's enough — it has repeatedly destroyed smaller chains. **Ethereum Classic was 51%-attacked three times in 2020**, with reorgs thousands of blocks deep. Security scales with the value securing the chain, so **small chains are cheap to attack and rentable hashpower makes it a service you can buy.**

## Key insight
<!-- bite: 472801ba-cd4d-49e5-bcdc-dcd886f4b6e5 -->

**Consensus mechanisms are not competing for correctness — they're competing on where they put the cost.** PoW puts it outside the system (energy) so attackers keep their capital when they fail. PoS puts it inside (slashable stake) so failure is punished by the protocol itself. Read every consensus design by asking *what does an attack cost, who does it cost, and is the punishment enforceable in-protocol* — that single question separates the serious designs from the rest.

## Related
<!-- bite: 7629c326-9e7d-458f-849c-dcb1a9171a5c -->
- [[web3/01-foundations/02-the-double-spend-problem|the double-spend problem]] — what this solves
- [[architecture/04-distributed-systems/07-consensus-and-paxos|classical consensus]] — Paxos/Raft, with known membership
- [[architecture/04-distributed-systems/02-theoretical-limits|theoretical limits]] — FLP and CAP, properly
- [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the scalability trilemma]]

## About this lesson
<!-- bite: cd39b3b8-f805-4586-b7f2-68e76e5b154a -->

**Level:** Advanced. **Covers:** proof-of-work, proof-of-stake, BFT, and the honest version of what "finality" and "51% attack" mean.

*Source: [reference] — Aug 2026.*
