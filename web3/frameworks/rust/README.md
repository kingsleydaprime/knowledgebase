# Rust for Web3

**Rust is the field's second contract language and its dominant infrastructure language.** Four distinct uses, and they're genuinely different jobs.

**Assumes [[languages/03-rust/README|the Rust course]].** Ownership, traits and `Result` are prerequisites here, not topics.

## 1. Solana programs — Anchor

The largest non-EVM contract ecosystem → [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]].

```rust
use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod counter {
    use super::*;

    pub fn increment(ctx: Context<Increment>) -> Result<()> {
        let counter = &mut ctx.accounts.counter;
        counter.count = counter.count.checked_add(1).ok_or(ErrorCode::Overflow)?;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Increment<'info> {
    #[account(mut, has_one = authority)]     // ← the constraint IS the security
    pub counter: Account<'info, Counter>,
    pub authority: Signer<'info>,
}

#[account]
pub struct Counter { pub authority: Pubkey, pub count: u64 }
```

**The mental shift from Solidity:** the caller supplies every account the instruction touches. There is no implicit storage lookup and no `msg.sender`-shaped ambient context — **your program receives accounts and must validate them.**

**The dominant vulnerability class is missing account validation.** Fail to check that a passed account is the one you expected, and an attacker passes a different one. Anchor's constraints (`has_one`, `seeds`, `bump`, `signer`, `owner`) are declarative checks that generate this validation — **use them rather than hand-rolling, and treat every unconstrained account as a finding.**

**PDAs (Program Derived Addresses)** are the other core concept: deterministic addresses derived from seeds, owned by the program rather than any key. They're how a program holds state and signs on its own behalf.

```bash
cargo install --git https://github.com/coral-xyz/anchor avm --locked
avm install latest
anchor init my-program && anchor build && anchor test
```

## 2. CosmWasm — Cosmos smart contracts

Contracts compile to WebAssembly and run on Cosmos chains → [[web3/05-beyond-ethereum/07-other-chains|Cosmos]].

```rust
#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg)
    -> Result<Response, ContractError>
{
    match msg {
        ExecuteMsg::Increment {} => try_increment(deps),
    }
}
```

The model is message-passing: `instantiate`, `execute`, `query`, with explicit state via `cw-storage-plus`. **Closer to an actor model than to Solidity's synchronous calls**, and the `cw-plus` library provides the standard token and multisig implementations.

## 3. ink! — Polkadot

Contracts for Substrate chains, also WASM. Uses Rust macros heavily and feels the most idiomatically Rust of the three:

```rust
#[ink::contract]
mod counter {
    #[ink(storage)]
    pub struct Counter { value: u64 }

    impl Counter {
        #[ink(message)]
        pub fn increment(&mut self) { self.value += 1; }
    }
}
```

Smallest ecosystem of the three; interesting design.

## 4. Infrastructure — the largest use by volume

**Most of the field's serious infrastructure is Rust**, and this is where the majority of Rust web3 jobs actually are:

- **Reth** — an Ethereum execution client, and one of the better modern Rust codebases to read
- **Lighthouse** — a consensus client
- **Solana validator** and **Firedancer** (C/Rust)
- **Foundry** itself
- **Alloy** — Ethereum types and RPC in Rust, the successor to ethers-rs
- **MEV searchers and bots**, where latency matters → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]]

```rust
use alloy::providers::{Provider, ProviderBuilder};

let provider = ProviderBuilder::new().on_http(rpc_url.parse()?);
let block = provider.get_block_number().await?;
```

## Why Rust, specifically

- **No GC**, so predictable latency — it matters in validators and searchers
- **The type system catches the errors this domain punishes.** `Result` forces error handling; no null; overflow panics in debug and is explicit via `checked_*` in release
- **WASM is a first-class target**, which is why the non-EVM chains chose it
- **It compiles to something auditable and deterministic**

## Where to start

**For Solana:** the Anchor book, then build a token and an escrow. **Focus on account validation** — it's where the bugs are, and it's the part that doesn't transfer from Solidity.

**For infrastructure:** read Reth. It's well-structured, actively developed, and reading a real client teaches more about [[web3/02-ethereum-and-the-evm/README|Ethereum]] than any amount of documentation.

## Related
- [[languages/03-rust/README|Rust]] — the language
- [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]] — the model these programs run in
- [[web3/frameworks/README|web3 frameworks]]
- [[web3/05-beyond-ethereum/07-other-chains|other chains]] — Cosmos, Polkadot
