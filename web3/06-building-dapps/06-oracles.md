# Oracles

**[Intermediate]** — how external facts get on-chain, the trust you can't avoid, and randomness.

## The oracle problem

**A blockchain is deterministic and sealed.** Every node must reach an identical result, so no contract can make a network call, read a file, or check the time against anything but the block header. **The chain knows only what has happened on the chain.**

But almost every useful application needs outside facts: a price, a match result, a weather reading, a shipment status, a random number.

**Something must bring that data in, and that something is trusted.** The oracle problem is not "how do we fetch data" — it's that **fetching introduces a trust assumption into a system whose entire value proposition is removing them.**

> A protocol's security is the *minimum* of its contract security and its oracle security. **Perfect contracts reading a manipulable price are not secure** → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|price manipulation]].

## How they work

Every oracle has the same shape:

```
off-chain data source(s)
        │
   oracle node(s) fetch and aggregate
        │
   sign and submit a transaction
        │
   on-chain contract stores the value
        │
   your contract reads it
```

Variants: **push** (the oracle updates on a schedule or price deviation; your read is a cheap `SLOAD`) and **pull** (you fetch a signed price off-chain and submit it with your transaction; fresher, cheaper for the oracle, more integration work — Pyth works this way).

## Chainlink, correctly

The dominant price oracle, and the thing to get right is the *reading*, not the fetching:

```solidity
AggregatorV3Interface internal feed;

function getPrice() public view returns (uint256) {
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound)
        = feed.latestRoundData();

    require(price > 0, "invalid price");
    require(updatedAt != 0, "incomplete round");
    require(block.timestamp - updatedAt <= MAX_AGE, "stale price");
    require(answeredInRound >= roundId, "stale round");

    return uint256(price);          // note: feeds have their own decimals()
}
```

**Every one of those checks corresponds to a real exploit or incident:**

- **No staleness check** → a feed that stops updating returns its last value forever. **This is the most commonly omitted check and it's a standard audit finding**
- **No positive check** → a zero or negative price sails through, and negative prices have occurred in real markets
- **Assuming 18 decimals** → Chainlink USD feeds typically use 8. Call `decimals()`
- **On an L2, not checking the sequencer uptime feed** → when a sequencer is down, feeds go stale by construction, and users can be liquidated on prices from before the outage. Chainlink publishes an uptime feed specifically for this, with a recommended grace period after recovery

**Have a fallback.** If the feed is stale or reverts, what does your protocol do? **Pausing is almost always better than proceeding on a bad number**, and "we didn't decide" means "we proceed."

## The landscape

| | Model | Notes |
|---|---|---|
| **Chainlink** | Push, decentralised node network | The default. Widest asset coverage |
| **Pyth** | Pull, first-party publishers (exchanges, market makers) | Sub-second updates, strong for derivatives |
| **Uniswap V3 TWAP** | On-chain, from AMM history | No external trust, **manipulable on thin liquidity** |
| **RedStone** | Pull, signed data in calldata | Cheap, many long-tail assets |
| **Optimistic (UMA)** | Assert a value; anyone disputes within a window | **Best for subjective facts** — "did this event occur?" — where no feed exists |

**UMA's optimistic model is worth knowing** because it answers a different question: arbitrary human-judgeable claims, resolved by economic dispute rather than by a data feed. It's how prediction markets settle → [[web3/07-the-application-layer/01-defi-primitives|DeFi]].

## Randomness — a specific, hard case

**There is no safe on-chain randomness.** Every value available to a contract is either known in advance or influenced by the block proposer:

```solidity
// EVERY ONE OF THESE IS EXPLOITABLE
uint256 bad = uint256(keccak256(abi.encode(block.timestamp, block.difficulty)));
uint256 alsoBad = uint256(blockhash(block.number - 1));
```

- **`block.timestamp`** — set by the proposer, within a tolerance
- **`block.prevrandao`** (post-Merge) — the beacon chain's RANDAO. **A proposer can choose to skip their slot** to reject an unfavourable value. Biasable by roughly one bit per slot they control, which is enough when the payout is large
- **`blockhash`** — unavailable for the current block, and only the last 256 are readable
- **Anything derived from state** — an attacker computes it in advance and only transacts when they win

**And critically: a contract can simply revert.** An attacker calls your lottery from a contract that checks the outcome and reverts if it lost, paying only gas to retry. **Any randomness resolved in the same transaction as the entry is defeated by this**, regardless of the source.

**The answers:**

**1. Chainlink VRF** — request randomness; a callback delivers it in a later transaction with a cryptographic proof that it was generated correctly and unpredictably. **The standard answer.** Costs LINK and adds a delay, and the delay is the point.

**2. Commit-reveal** — participants commit `hash(secret)`, then reveal. Combine the secrets. **Requires handling non-revealers**, who will withhold when the outcome is against them — usually with a forfeited deposit.

**3. Two-block RANDAO** — commit in block N, resolve using `prevrandao` from block N+k. **Cheap and adequate for low-value uses**; still slightly biasable and not appropriate for anything with a large payout.

**The unifying rule: never resolve randomness in the same transaction that consumes it.**

## Design guidance

- **Ask whether you need external data at all.** Uniswap's core never asks what anything is worth — it enforces an invariant. **The most secure oracle is the one you designed out**
- **Use multiple sources** for high value; take a median, or revert on disagreement
- **Bound the input.** Reject prices that moved more than X% since the last reading. Cheap, and very often absent
- **Circuit-break.** Pause on anomalies rather than transacting on a suspicious number
- **Document the trust assumption explicitly.** "This protocol assumes Chainlink's ETH/USD feed is honest and fresh" belongs in your README, because it is a real part of your security model

## Key insight

**Every oracle reintroduces trust into a trustless system, and there is no way around it** — determinism means the chain cannot see out. So the engineering goal isn't eliminating the oracle, it's making the trust explicit, minimal, redundant, and bounded: multiple sources, staleness checks, sanity limits, and a defined behaviour when the data is bad.

## Related
- [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|price manipulation]] — what goes wrong
- [[web3/07-the-application-layer/01-defi-primitives|DeFi primitives]] — the main consumer
- [[web3/03-smart-contracts-with-solidity/01-what-a-smart-contract-is|what contracts can't do]]
- [[web3/06-building-dapps/01-the-dapp-architecture|the dapp architecture]]
