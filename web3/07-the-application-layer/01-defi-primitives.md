---
id: 8c58a772-4417-42bf-a2f1-fb48d14c7b9c
---

# DeFi Primitives

## The kid version first
<!-- bite: 1d802733-10ac-45bf-8485-2a53a13d8244 -->

DeFi rebuilds banking as public programs. **No accounts, no applications, no approval** — just contracts anyone can call.

The clever part isn't any single product. It's that they **compose**: the token you get for lending can be collateral for a loan, whose proceeds go into a pool, whose LP token is collateral somewhere else. **That's the genuine innovation, and it's also how one bad price cascades through six protocols in a single transaction.**

## 1. AMMs — pricing without an order book
<!-- bite: 34abc4f1-2f1e-4e0d-96e8-9959a8f37eca -->

An order book needs constant quoting and cancelling, which is unaffordable on-chain. **Automated market makers price by formula instead.**

**Constant product (Uniswap V2):**

```
x · y = k          x = reserve of token A, y = reserve of token B

price of A in B = y / x

buying A: x decreases → y/x rises → price rises as you buy
```

**The pool never needs to know what anything is worth.** It only maintains an invariant. That's the elegance — and it's why Uniswap's core has no oracle and nothing to manipulate → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|oracles]].

**The consequences to understand:**

- **Slippage** is inherent: a large trade moves the price against itself along the curve. Not a fee — geometry
- **Impermanent loss** — the real cost of providing liquidity. When the price moves, the pool automatically sells the appreciating asset and buys the depreciating one. **The LP ends up worse off than simply holding**, and "impermanent" is a misnomer: it's permanent once you withdraw. Fees must exceed it for LPing to be profitable, and often don't
- **Uniswap V3's concentrated liquidity** lets LPs supply within a chosen price range — dramatically more capital-efficient, and it converts passive LPing into active position management with sharper losses when the price exits your range
- **Curve's StableSwap** uses a flatter curve for assets that should trade near 1:1, giving very low slippage between stablecoins

## 2. Lending — pooled, over-collateralised
<!-- bite: 26599e0c-0b4e-4a0a-be67-b101d9e93309 -->

Aave and Compound: deposit into a pool and earn; borrow against collateral.

**Everything is over-collateralised.** To borrow $100 you post $150. There is no credit assessment, because there is no identity and no recourse — **anonymous default is free, so only collateral can secure a loan.**

```
Health Factor = (collateral × liquidation threshold) / debt

HF > 1  → safe
HF < 1  → liquidatable: anyone repays your debt, takes your collateral plus a bonus
```

**Liquidation is permissionless and competitive** — bots race for the bonus, which is what keeps the system solvent without an operator → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]].

**Interest rates are algorithmic**, set by utilisation: as the pool empties, rates rise, attracting deposits and discouraging borrowing. A control loop, not a committee.

**This is the honest limitation of DeFi lending.** Over-collateralised borrowing is useful for leverage, shorting, and accessing liquidity without selling — **it does not do what lending does in the real economy**, which is extend credit to people who don't already have the money. Under-collateralised lending needs identity and enforcement, and remains substantially unsolved → [[web3/07-the-application-layer/04-identity-and-naming|identity]].

## 3. Stablecoins — three designs, one failure
<!-- bite: bd82be94-2c88-4ec0-8def-c359952298ee -->

| Type | Mechanism | Risk |
|---|---|---|
| **Fiat-backed** (USDC, USDT) | A company holds dollars, issues tokens | **Trust the issuer.** They can freeze you, and their reserves are their claim |
| **Crypto-backed** (DAI) | Over-collateralised crypto in contracts | Collateral crashes faster than liquidation clears |
| **Algorithmic** (UST) | Supply adjusted by mechanism | **The design failure below** |

**Fiat-backed dominate by volume, and are fully centralised** — Circle and Tether can and do freeze addresses. Using USDC means accepting an issuer with a compliance department. That's a coherent trade, and it is not decentralisation.

**Terra/UST collapsed in May 2022, destroying ~$40B in days.** UST was backed by LUNA, minted and burned to hold the peg. When confidence broke, redeeming UST minted LUNA, which crashed LUNA's price, which required minting more — **a reflexive death spiral.** The design's stability depended on the market believing it was stable.

**The lesson generalises:** a stablecoin backed by an asset whose value depends on the stablecoin's success has no backing at all. Several designs have since claimed to have fixed this; **be extremely sceptical of any stablecoin whose collateral is its own ecosystem's token.**

**DAI's evolution is instructive too** — originally ETH-collateralised and decentralised, it now holds a large fraction of USDC as collateral. **The decentralised stablecoin is substantially backed by the centralised one**, which is an honest thing to know about it.

## 4. Derivatives and perps
<!-- bite: 6a492fe0-9dfa-40b0-9cc8-63744e9b1fc7 -->

**Perpetual futures** are the dominant on-chain derivative: leveraged exposure with no expiry, held near the spot price by a **funding rate** paid between longs and shorts. When perps trade above spot, longs pay shorts, incentivising the gap closed.

Two models: **order-book** (dYdX, Hyperliquid — often on an app-chain for the throughput) and **pool-based** (GMX — traders take the other side of a shared liquidity pool).

**Perps are where most on-chain volume and most retail losses are.** Leverage plus 24/7 markets plus permissionless access is an efficient mechanism for transferring money from inexperienced traders to sophisticated ones → [[web3/08-the-honest-assessment/index|the honest assessment]].

## Composability — the feature and the risk
<!-- bite: 200556e1-c818-4284-b1c9-fc78efb59cd5 -->

```
deposit ETH → get stETH → use as collateral → borrow USDC
   → provide to a Curve pool → get LP token → stake for rewards
       → use the receipt as collateral elsewhere
```

**Each step is permissionless and needs nobody's approval. That is genuinely new, and genuinely powerful.**

It is also **leverage stacked on unaudited assumptions**. Every layer inherits every risk below it, and a failure anywhere unwinds the whole stack **in a single transaction, faster than any human can react.** Flash loans mean an attacker can assemble the entire stack with borrowed capital → [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|flash loans]].

**"DeFi Lego" is the marketing term. "Correlated systemic risk with no circuit breakers" is the same thing described accurately**, and both are true.

## Key insight
<!-- bite: 415c7bf3-7de7-4a28-8d15-b3a64db206c0 -->

**DeFi's four primitives are genuinely well-engineered — the AMM invariant, algorithmic rates and permissionless liquidation are elegant mechanism design that works without an operator.** The risk isn't in the primitives; it's in the composition, where every protocol trusts the last one's price and accounting, and a single manipulated number unwinds six layers in one transaction.

## Related
<!-- bite: 95152b8e-4205-4193-84f1-e71393b8be43 -->
- [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|price manipulation]] — how these get attacked
- [[web3/03-smart-contracts-with-solidity/07-token-standards|token standards]] — ERC-4626 vaults
- [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|what blockchains are good for]]
- [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]] — liquidations and sandwiching

## About this lesson
<!-- bite: fd9d117f-3948-445f-8cf4-209a2cf6ed4b -->

**Level:** Advanced. **Covers:** AMMs, lending, stablecoins and derivatives: the four building blocks nearly all of DeFi is assembled from.
