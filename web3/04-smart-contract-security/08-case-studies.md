---
id: 61ead275-18e0-4bae-a13d-ba59bca11f26
---

# Case Studies — Where the Money Actually Went

**Read this note before the technical ones if you like.** Nothing motivates the practices in this folder like seeing what happens without them.

## The DAO — June 2016, ~3.6M ETH
<!-- bite: 4105b479-f83d-46b4-83cb-2449848f3f51 -->

**What:** A recursive `withdraw` — the balance was zeroed *after* the external call, so the recipient's fallback re-entered and drained the contract → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]].

**Why it matters far beyond the bug:** the response. The Ethereum community hard-forked the chain to reverse the theft. Those who refused continued the original chain as **Ethereum Classic**.

**The lesson is philosophical.** "Code is law" — the field's founding principle — was tested once, at scale, and the community chose not to honour it. **Every subsequent claim of immutability is made against that precedent.** Ethereum's history is not immutable; it was changed, deliberately, when enough people wanted it changed badly enough.

## Parity multisig — 2017, twice
<!-- bite: 77718259-c9cc-4230-a572-8fa130ca3de7 -->

**July, ~$31M stolen.** The wallet library's `initWallet` was public and unprotected. Anyone could call it and become the owner. **A missing visibility specifier.**

**November, ~$280M frozen forever.** After the first hack, someone noticed the *library* contract itself had never been initialised. They initialised it, became its owner, and called `selfdestruct` — **destroying the library that every deployed Parity multisig delegated to.** Hundreds of wallets became permanently inert, holding funds nobody can ever move.

**Lessons:** always specify visibility (Solidity 0.5 made it mandatory *because of this*); **always `_disableInitializers()` on implementation contracts**; and a shared dependency is a single point of failure for everything that depends on it → [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]].

## bZx — February 2020, ~$1M
<!-- bite: 7f620057-abb9-4387-8957-f30b6ffb7916 -->

Two attacks in a week using **flash loans** to manipulate a thin oracle price, then borrowing against the false valuation.

**Small money, outsized influence.** It was the moment the field learned that **capital is rentable by the transaction**, so no security assumption may rest on an attacker's wealth → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|price manipulation]].

## Ronin Bridge — March 2022, ~$625M
<!-- bite: 45f06348-fa8c-4c2e-ba0d-bc359928ce17 -->

**The largest crypto theft to date, and there was no smart contract bug at all.**

The bridge used a 5-of-9 multisig. **Four keys were held by Sky Mavis** (one entity). A fifth was reachable because Sky Mavis had been granted signing rights by the Axie DAO to handle load months earlier — **and that access was never revoked.** An attacker (later attributed to North Korea's Lazarus Group) compromised Sky Mavis via a spear-phishing campaign and had five keys.

**It went unnoticed for six days**, discovered only when a user reported a failed withdrawal.

**Lessons:** count *independent* signers, not keys; **revoke temporary access, and audit permissions on a schedule**; monitor for large withdrawals. The most expensive failure in the field's history was operational security, not code.

## Wormhole — February 2022, ~$326M
<!-- bite: 1ade6bea-b5ad-4d68-8508-8a3b55105b5e -->

A signature verification flaw in the Solana side let an attacker forge a "valid" guardian approval and mint 120,000 wETH backed by nothing.

**Bridges hold enormous concentrated value and their security reduces to their message-verification scheme.** Nearly every top-ten loss in the field is a bridge → [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]].

## Nomad Bridge — August 2022, ~$190M
<!-- bite: eed158dd-7940-491d-a635-11ef565674a3 -->

A routine upgrade initialised a trusted root to `0x00`. The effect was that **every message verified as valid** — no proof required.

**Then it became a free-for-all.** The first exploiter's transaction was public, so hundreds of ordinary users copied it, swapped in their own address, and drained the rest. **A "crowdsourced" hack**, and a vivid demonstration that on a public chain, an exploit is a broadcast tutorial.

**Lessons:** treat upgrade parameters as critical (a zero value should never be a valid trusted root); and **once an exploit is on-chain, you have minutes, not hours.**

## Euler Finance — March 2023, ~$197M
<!-- bite: 4d0f0469-db89-43fa-9ade-c77e4462377a -->

A donation-based manipulation of internal accounting: a missing health check in a `donateToReserves` function let an attacker self-liquidate at a profit. **Euler had been audited multiple times, including a formal verification engagement.**

**Then something unusual: after weeks of public negotiation, the attacker returned essentially all of it.** A meaningful data point about how large on-chain thefts actually end — the funds are traceable forever, and cashing out a nine-figure sum is genuinely hard.

## Curve — July 2023, ~$70M
<!-- bite: b07a7df2-33ee-4d37-b845-e9f0f33a20ef -->

**A compiler bug.** Specific Vyper versions generated reentrancy guards that didn't work, so pools believed to be protected were not → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]].

**Your security depends on your toolchain**, and "we used the standard guard" assumes the compiler implemented it. Pin your compiler version, and treat compiler advisories as security advisories.

## Mango Markets — October 2022, ~$114M
<!-- bite: 60b12da7-32f0-453f-b896-663d560e9299 -->

An attacker manipulated the price of a thinly-traded perpetual upward, borrowed against the inflated collateral, and walked away — then argued publicly it was a legitimate trading strategy the protocol permitted.

**The subsequent US federal prosecution is the landmark:** "the code allowed it" is not a defence against fraud and market-manipulation law. **Being on-chain does not place conduct outside legal jurisdiction**, and the industry's assumption otherwise has not survived contact with courts → [[web3/08-the-honest-assessment/03-regulation-and-the-legal-layer|regulation]].

## The pattern
<!-- bite: 3914d877-9338-4d88-96a8-e48afb62e2bf -->

| Exploit | Root cause | Category |
|---|---|---|
| The DAO | Effects after interactions | Reentrancy |
| Parity ×2 | Missing visibility; uninitialised library | **Access control** |
| bZx | Spot price as truth | **Oracle** |
| Ronin | Compromised keys, stale permissions | **Operational** |
| Wormhole | Broken signature verification | **Bridge** |
| Nomad | Bad upgrade parameter | **Operational** |
| Euler | Missing health check | Logic |
| Curve | Compiler bug | Toolchain |
| Mango | Manipulable thin market | **Oracle** |

**Read the right-hand column.** Access control, operational failures, oracles and bridges dominate. **Reentrancy — the vulnerability the field talks about most — appears twice, and one of those was a compiler bug.**

The uncomfortable summary: **most of the money was lost to boring failures.** Stolen keys, unrevoked permissions, missing modifiers, trusting a manipulable number, and bridges. The engineering effort goes toward clever vulnerability classes; the losses come from operations and from trusting the wrong input.

## Key insight
<!-- bite: b191a32f-d2f4-4e2d-967c-6cef7d4e738f -->

**Every major loss traces back to something the team believed was true and wasn't** — that a function was restricted, that a price was honest, that a permission had been revoked, that a guard worked, that a signature had been checked. Security here is not primarily about knowing vulnerability classes. It's about enumerating your assumptions, writing them down, and then trying to break each one.

## Related
<!-- bite: 8bdea261-b349-407c-9236-dc94d4c183d2 -->
- [[web3/04-smart-contract-security/index|smart contract security]] — the whole section
- [[web3/04-smart-contract-security/01-why-this-is-different|why security is different here]]
- [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges]] — the largest losses
- [[cybersecurity/07-security-operations/index|security operations]] — the discipline Ronin needed

## About this lesson
<!-- bite: 29c32d2b-7ca9-443a-9037-3b3fce9381df -->

**Level:** Intermediate. **Covers:** the exploits worth knowing, what each taught the field, and the pattern across all of them.

*Source: [reference] — Aug 2026. Figures are USD at time of exploit and are approximate.*
