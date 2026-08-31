# Oracles, Flash Loans and Price Manipulation

**[Advanced]** — the vulnerability class that has drained more DeFi protocols than reentrancy, and the uncollateralised loan that makes it cheap.

## The kid version first

Your contract needs to know what ETH is worth. It can't browse the internet, so it asks a nearby exchange: *"what's the current price?"*

An attacker walks into that exchange, **buys enough to move the price**, asks your contract to do something using the wrong price, then sells back. Total time: one transaction. Total capital required: **borrowed, and repaid before anyone notices.**

## Flash loans — why this is cheap

A flash loan is an uncollateralised loan that must be repaid **within the same transaction**. If it isn't, the whole transaction reverts and it's as if it never happened — so the lender has zero risk and charges a tiny fee.

```
[ single transaction ]
   borrow 100,000,000 USDC   ← no collateral
   ...do anything...
   repay 100,000,000 USDC + fee
   (if the repay line isn't reached, everything reverts)
```

**This is a legitimate, useful primitive** — arbitrage and collateral swaps genuinely need it. But its security consequence is absolute:

> **Any check based on a token balance, a share of supply, a governance vote weight, or a spot price is defeated for the price of a flash-loan fee.**

"Only large holders can do this" is not a security control. **Capital is rentable by the transaction**, so an attacker's apparent wealth tells you nothing.

## The core mistake: spot price as truth

```solidity
// CATASTROPHIC — do not do this
function getPrice() public view returns (uint256) {
    (uint112 r0, uint112 r1,) = pair.getReserves();
    return (uint256(r1) * 1e18) / uint256(r0);      // instantaneous AMM ratio
}
```

An AMM's reserve ratio **is** its price, and it is *designed* to move when you trade against it. So:

```
1. Flash-loan a large amount of token A
2. Swap it into the pool → the ratio moves violently → "price" of B looks 10× higher
3. Call the victim protocol, which reads that price
     e.g. deposit B as collateral, borrow far more than it's worth
4. Swap back, repay the flash loan, keep the difference
```

**Every step is a legitimate operation.** No contract was tricked into breaking its own rules — the victim did exactly what it was written to do, with a number it should not have trusted.

The same idea generalises: **manipulating any single-source, instantaneously-readable value.** Vault share prices, LP token valuations, rebasing balances, and governance vote weights read from current holdings have all been exploited this way.

## The defences, ranked

**1. Use a proper oracle.** Chainlink price feeds aggregate many off-chain sources and publish on-chain. **You cannot move a Chainlink feed by trading**, which removes the attack entirely for the assets it covers.

But check the answer:

```solidity
(, int256 price,, uint256 updatedAt, ) = feed.latestRoundData();
require(price > 0, "bad price");
require(block.timestamp - updatedAt < MAX_STALENESS, "stale price");
```

**Stale-price checks are routinely omitted, and that omission is itself an exploit** — a feed that stopped updating during volatility (or was deprecated) will happily keep returning its last value forever. Also handle the **L2 sequencer being down**, where feeds go stale by construction; Chainlink publishes an uptime feed for exactly this.

**2. TWAPs, understood properly.** A time-weighted average price (Uniswap V3's oracle) averages over a window, so manipulating it requires holding the price away from the market **for the whole window**, which is expensive and arbitrageable.

TWAPs are good, not magic:
- **Longer window = more manipulation-resistant but more lag.** During a genuine crash a 30-minute TWAP is stale in exactly the way that liquidations must not be
- **Low-liquidity pools are cheap to hold**, so a TWAP on a thin pool is barely better than spot
- **Multi-block manipulation is now practical** for a block builder → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]]

**3. Multiple independent sources.** Take the median of several oracles, or require them to agree within a tolerance and revert otherwise. Costs gas, removes single points of failure.

**4. Sanity bounds and circuit breakers.** Reject prices that moved more than X% since the last reading, and pause on anomalies. **This is the cheapest meaningful control and it is very often absent.**

**5. Don't need a price.** The strongest option. Uniswap's core never asks what anything is worth — it only enforces a constant-product invariant, so there is nothing to manipulate. **Designs that avoid needing external truth avoid this entire class.**

## Reading it in real losses

- **bZx (2020, ~$1M)** — the first well-known flash-loan price manipulation. Small money, enormous influence: it taught the field what flash loans meant
- **Harvest Finance (2020, ~$34M)** — manipulated a Curve pool's share price to mint underpriced vault shares
- **Mango Markets (2022, ~$114M)** — manipulated a thinly-traded perpetual's oracle price upward, borrowed against the inflated collateral, and left. The perpetrator argued publicly that it was a legitimate trade; the legal proceedings that followed are a landmark for whether "the code allowed it" is a defence
- **Euler (2023, ~$197M)** — a donation-based manipulation of internal accounting, not an external oracle. **Most of the funds were eventually returned after negotiation**, which is itself a notable data point about how these end

## The review checklist

- **Where does every external number come from, and who can move it?**
- **Is any price read as a spot value from an AMM?** If yes, that's the finding
- **Is staleness checked? Is the L2 sequencer's uptime checked?**
- **What happens if the oracle returns zero, a negative, or reverts?**
- **Does any logic depend on `balanceOf` or `totalSupply` at a single instant?**
- **Would this work if the attacker had a billion dollars for one transaction?** If the answer changes, that's the vulnerability

## Key insight

**A blockchain can prove what happened on it; it cannot know anything else.** Every price, rate and external fact enters through a trusted channel, and the security of the protocol is bounded by the security of that channel. Flash loans made the cost of manipulating the weakest such channel — a spot AMM price — approximately zero, which converted a theoretical weakness into the field's most reliable attack.

## Related
- [[web3/06-building-dapps/06-oracles|oracles]] — the mechanism, in depth
- [[web3/07-the-application-layer/01-defi-primitives|DeFi primitives]] — AMMs and lending
- [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]] — the adjacent ordering problem
- [[web3/04-smart-contract-security/08-case-studies|case studies]]

*Source: [reference] — Aug 2026.*
