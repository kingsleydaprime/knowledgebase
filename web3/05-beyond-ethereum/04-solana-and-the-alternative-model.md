# Solana and the Alternative Model

**[Advanced]** — the strongest monolithic counter-argument to Ethereum's rollup strategy, and what it trades away.

## The bet

Ethereum decided L1 should stay small enough for a laptop to verify, and pushed execution to [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]].

**Solana bet the opposite: hardware gets faster, so build one chain fast enough that you never need L2s.** No fragmented liquidity, no bridges, no seven-day withdrawals — one global state everyone shares.

**It's a real engineering position, not a marketing one**, and it's the most serious challenge to the modular thesis.

## What's actually different

**1. Parallel execution — the core innovation.** Every Solana transaction **declares in advance which accounts it will read and write.** The runtime (Sealevel) then executes non-overlapping transactions simultaneously across cores.

```
tx A: writes account X          ┐ no overlap
tx B: writes account Y          ┘ → run in parallel

tx C: writes account X          → must wait for A
```

**Ethereum can't do this** because a transaction's storage accesses are only discovered by executing it. Solana made declaration mandatory, which is a real cost to developers (you must know your accounts up front) and buys genuine parallelism → [[web3/01-foundations/04-blocks-chains-and-state|state models]].

**2. Proof of History.** A verifiable delay function producing a cryptographic clock — a hash chain proving that time passed between events. **This is not consensus** (Solana uses a PoS variant called Tower BFT for that); it's a pre-agreed ordering that removes a lot of the communication normally needed to agree on time. It's what allows 400ms slots.

**3. Accounts and programs are separate.** A "program" (contract) is stateless and marked executable; all data lives in separate accounts the program owns. **The same program operates on many accounts**, so there's no per-deployment contract instance the way Ethereum has. This takes real adjustment coming from Solidity.

**4. Rent.** Accounts pay for the storage they occupy — deposit enough SOL to be "rent-exempt" or the account is reclaimed. **This directly addresses the state-bloat problem Ethereum still has**, and it is arguably Solana's most underrated design decision.

**5. Local fee markets.** Congestion in one popular program raises fees for that program's accounts, not for the whole chain. Ethereum's single global fee market means an NFT mint makes everything expensive.

## Development, concretely

**Rust, with the Anchor framework** doing what OpenZeppelin does for Solidity:

```rust
#[program]
pub mod my_program {
    use super::*;
    pub fn initialize(ctx: Context<Initialize>, value: u64) -> Result<()> {
        ctx.accounts.my_account.value = value;    // account passed IN, not looked up
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = user, space = 8 + 8)]
    pub my_account: Account<'info, MyAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}
```

**The mental shift:** the caller supplies every account the instruction touches. Your program receives them and **must validate them** — Anchor's constraints (`has_one`, `seeds`, `signer`) do this declaratively.

**The dominant vulnerability class is missing account validation.** If you don't verify that the passed account is the one you expected, an attacker passes a different one. There's no `msg.sender`-shaped implicit context to lean on; **everything is explicit, and everything unvalidated is exploitable.** This is Solana's equivalent of the access-control category, and it dominates its audit findings → [[web3/frameworks/rust/README|Rust for web3]].

## The honest ledger

**What genuinely works:** sub-second finality, fees in fractions of a cent, and thousands of real transactions per second. **For consumer applications, payments and high-frequency trading, the user experience is meaningfully better than Ethereum L1** — that's not disputable and it's why the ecosystem is large.

**What it costs:**

- **Validator hardware is data-centre class** — high core counts, hundreds of GB of RAM, fast NVMe. **You cannot run a Solana validator on a laptop, by design.** That is the trilemma trade, made deliberately
- **The chain has halted.** Multiple full outages (2021–2022), several hours each, plus severe degradation events. Ethereum has never halted. **This is the strongest empirical argument against the approach**, and the frequency has dropped substantially since
- **State growth is enormous**, mitigated by rent but still pushing archival toward specialist providers
- **Client diversity was a single point of failure for years.** The Firedancer client (Jump) is the answer, and its arrival genuinely changes the risk picture
- **Local fee markets and stake-weighted QoS** were introduced after congestion events where bots crowded out ordinary users — the design is being fixed reactively, which is a real observation about maturity

## How to hold both

**This is not a question with a settled answer, and confident partisanship in either direction is a sign someone isn't thinking.**

The genuine trade: Ethereum optimises for *anyone can verify, forever*, and accepts a worse UX today plus the complexity of a fragmented L2 ecosystem. Solana optimises for *it works well now*, and accepts that verification requires serious hardware.

**Both are defensible.** Which is right depends on whether you think the point is credible neutrality decades out, or usable applications this year. **Most of the industry's arguing is people answering different questions.**

## Key insight

**Solana's real contribution is parallel execution via declared account access** — that's a genuine advance, and Ethereum has repeatedly considered adopting the idea via access lists. The rest of the design is a coherent, explicit choice to buy performance with hardware requirements. Judge it on whether that trade is acceptable for a given application, not on whether it's "really decentralised" — a question that has no threshold anyone agrees on.

## Related
- [[web3/frameworks/rust/README|Rust for web3]] — Anchor, and the Solana programming model
- [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the trilemma]] — the trade being made
- [[web3/01-foundations/04-blocks-chains-and-state|state models]] — declared access sets
- [[languages/03-rust/README|Rust]] — the language

*Source: [reference] — Aug 2026.*
