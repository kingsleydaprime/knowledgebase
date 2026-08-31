# MEV, Front-Running and Transaction Ordering

**[Advanced]** — the value extractable purely by choosing what order transactions execute in, why it can't be eliminated, and what protects users in practice.

## The kid version first

Your transaction sits in public view for a few seconds before it runs. In that window, **anyone can read exactly what you're about to do and put their own transaction in front of it.**

If you're about to buy something and push its price up, they buy first and sell it to you higher. You still get your trade — just at a worse price. **You will never see it happen, and it is entirely legal.**

## What MEV is

**Maximal Extractable Value**: profit obtainable by including, excluding, or reordering transactions within a block, beyond the ordinary block reward and fees.

It exists because **someone must choose an order**, that choice is worth money, and there is no neutral way to make it. It is not a bug in Ethereum; it's a consequence of having a public mempool and a discretionary block producer. **Every chain with those two properties has MEV**, including ones that claim otherwise.

## The forms

**Arbitrage** — the same asset priced differently across two venues; a bot equalises them. **This is benign and useful**: it's what keeps on-chain prices honest, and it would be done by someone regardless.

**Liquidations** — a lending position goes underwater and bots race to liquidate it for the bonus. **Also necessary** — it's how lending protocols stay solvent.

**Front-running** — see a profitable transaction, submit the same action with a higher fee, execute first.

**Sandwiching** — the harmful one, and it targets ordinary users:

```
mempool:    victim swaps 100 ETH → USDC, max slippage 2%

attacker's block ordering:
  1. attacker buys USDC        → price rises
  2. VICTIM's swap executes    → at the worse price, within their 2% tolerance
  3. attacker sells USDC       → pockets the difference

the victim's transaction succeeded. They simply got less, silently.
```

**Time-bandit attacks** — reorganising *past* blocks to capture MEV in them. Rare, and the reason MEV is considered a consensus-stability risk rather than only an application-layer nuisance: if the MEV in block *N* exceeds the reward for building block *N+1*, re-mining becomes rational.

## PBS — how the market is organised now

Post-Merge, block building is separated from proposing:

```
searchers    find opportunities, submit ordered BUNDLES with a bid
    ↓
builders     assemble the most profitable full block from bundles + mempool
    ↓
relays       hold the block, reveal only after the proposer commits to it
    ↓
proposer     signs the highest-bidding header, usually WITHOUT seeing the contents
```

The design intent was democratising: without it, only sophisticated validators could capture MEV, so MEV would push validators to centralise. PBS lets a small validator sell the right to order their block and receive most of the value.

**What it actually produced:** MEV revenue is shared more broadly, and **block building concentrated into a handful of specialised builders.** Trading one centralisation for another is an honest description. Enshrined PBS and inclusion lists are the proposed next step → [[web3/02-ethereum-and-the-evm/06-the-ethereum-roadmap|the roadmap]].

## Protecting users

**1. Private transaction relays.** Flashbots Protect, MEV Blocker and similar submit straight to builders, **skipping the public mempool**. Nothing to front-run because nobody sees it pending. **This is the single most effective user-level protection**, it's free, and it's a one-line RPC change — most wallets now default to something like it.

**2. Slippage limits, set honestly.**

```solidity
function swap(uint256 amountIn, uint256 minAmountOut, uint256 deadline) external {
    require(block.timestamp <= deadline, "expired");
    // ...
    require(amountOut >= minAmountOut, "slippage");
}
```

**`minAmountOut` bounds the loss; it does not prevent the attack.** And a high tolerance is an invitation — setting 50% slippage to make a transaction "go through" is authorising a 50% theft. **`minAmountOut = 0` is a total loss waiting to happen**, and contracts that let users pass it should reject it.

**A deadline is not optional either.** Without one, a transaction can sit unmined for hours and execute at a completely different price — this is a real and frequently-flagged audit finding.

**3. Commit-reveal.** Where the *content* must be secret until execution: commit `hash(action, secret)` in one transaction, reveal in a second. Costs an extra transaction and a delay; appropriate for auctions, games and voting.

**4. Batch auctions.** CoW Swap and similar settle many orders at one uniform clearing price per batch, so there is no intra-batch ordering to exploit. **This removes sandwiching structurally**, rather than mitigating it — the strongest available answer for swaps.

## Protecting protocols

- **Don't leak intent.** Any function where knowing the parameters in advance is profitable needs commit-reveal
- **Auctions must not be "highest bid at deadline"** — that's trivially sniped. Use a batch, a Dutch auction, or a randomised close
- **Don't make liquidations first-come-first-served** at a fixed bonus; a Dutch auction on the bonus is fairer and reduces gas wars
- **Assume the ordering is adversarial.** Any invariant that holds "as long as these two transactions land in this order" does not hold

## Can it be eliminated?

**No, and claims otherwise deserve scepticism.**

- **Encrypted mempools** (threshold decryption, SUAVE) hide contents until ordering is fixed. Genuinely promising; adds latency and its own trust assumptions, and nothing is deployed at scale
- **Fair-ordering protocols** enforce first-come-first-served by consensus. "First" is not well-defined in a distributed system with no shared clock — that's a fundamental limit, not an engineering gap
- **Application-level design** (batch auctions) genuinely removes specific forms, and is the most successful approach so far

**"Our chain has no MEV" almost always means "our chain has a centralised sequencer, so the sequencer takes it all."** That's not the absence of MEV; it's MEV with one beneficiary → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]].

## Key insight

**MEV is the price of having a public mempool and a discretionary block producer — remove either and you remove MEV along with the property you wanted.** Some of it (arbitrage, liquidations) is load-bearing infrastructure the system needs. Some of it (sandwiching) is a pure transfer from ordinary users to bots. The engineering question is never "how do we eliminate MEV" but **"which forms do we want, and who captures them."**

## Related
- [[web3/02-ethereum-and-the-evm/04-transactions-and-the-mempool|the mempool]] — where the window exists
- [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|price manipulation]] — the adjacent class
- [[web3/07-the-application-layer/01-defi-primitives|DeFi primitives]] — AMMs, where sandwiching lives
- [[web3/01-foundations/05-consensus|consensus]] — why time-bandit attacks matter

*Source: [reference] — Aug 2026.*
