# Bitcoin and the UTXO Model

**[Intermediate]** — the original design, why its limitations are deliberate, and what it does that Ethereum doesn't.

## Why this note exists

It's tempting to treat Bitcoin as "the primitive one." **It's better read as a different set of choices** — most of its apparent limitations are refusals, and understanding them clarifies what Ethereum gave up to become programmable.

## UTXO, again but properly

There are no accounts and no balances. There are **unspent transaction outputs**: discrete chunks of value, each locked by a spending condition.

```
transaction:
  inputs:  [ pointer to UTXO_a, unlocking script ]
           [ pointer to UTXO_b, unlocking script ]
  outputs: [ 4 BTC, locked to Bob's condition   ]
           [ 0.9 BTC, locked back to Alice      ]   ← change
                                                     (0.1 unaccounted = fee)
```

**Inputs are consumed entirely.** You cannot spend part of a UTXO — you spend it all and send the remainder back to yourself as change. Your "balance" is a number your wallet computes by summing the outputs it can spend; the chain stores no such number → [[web3/01-foundations/04-blocks-chains-and-state|state models]].

**Properties this buys:**

- **Parallel validation.** Transactions spending disjoint UTXOs have no shared state, so they can be validated in any order and simultaneously. This is the property Solana's declared-account model was reaching for → [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]]
- **Replay protection is structural.** An output can only be spent once, ever. **No nonce needed** — Ethereum's nonce exists precisely because the account model lost this
- **Privacy hygiene.** A fresh address per output is the natural pattern rather than an extra step
- **Stateless-ish validation.** A node needs the UTXO set, not the full history

**Costs:** no natural way to express "a contract holding funds that many users update"; change management is a persistent source of wallet bugs (including the infamous class where change was sent to an unmonitored address); and the UTXO set fragments into dust that costs more in fees to spend than it's worth.

## Script — deliberately not Turing-complete

Bitcoin has a scripting language. It is a **stack machine with no loops**, so every script terminates in bounded time.

```
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG     # standard P2PKH
```

**No loops, no recursion, no persistent state, no access to other transactions' data.** That last one is why Bitcoin has no smart contracts in the Ethereum sense: a script can validate *this* spend, and cannot maintain state across transactions.

**This is a refusal, not an oversight.** Bounded scripts mean no gas metering is needed, no infinite loops are possible, and the validation cost of any transaction is knowable in advance. **Ethereum needed gas precisely because it chose Turing-completeness** → [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas]].

What Script does support: multisig, timelocks (`OP_CHECKLOCKTIMEVERIFY`), and hash locks — which compose into **Hashed Timelock Contracts**, the primitive underneath the Lightning Network and atomic swaps. That's a meaningful amount of expressiveness inside a very small budget.

## The upgrades that matter

**SegWit (2017)** moved signature data outside the transaction body. Two consequences: it fixed **transaction malleability** (previously a transaction's ID could change before confirmation, which broke any protocol building on unconfirmed transactions — Lightning depended on this fix), and it effectively raised the block size.

**Taproot (2021)** brought Schnorr signatures — which **aggregate**, so a multisig looks identical to a single signature on-chain, improving both privacy and size — plus MAST, letting complex spending conditions be committed to but only revealed for the branch actually used.

**Ordinals and inscriptions (2023)** let arbitrary data be embedded in transactions, creating Bitcoin NFTs and BRC-20 tokens. **Contentious within the Bitcoin community** as a use of block space the design didn't intend, and a live argument about what the chain is for.

**Lightning** is Bitcoin's scaling answer: a network of bidirectional payment channels settled on-chain only when opened and closed. **Instant, near-free payments, with real trade-offs** — liquidity must be committed in advance, routing is an unsolved-ish problem at scale, and you must be online to defend against a counterparty publishing an old state.

## The culture, which explains the technology

Bitcoin's development is **conservative to a degree that looks like stagnation from outside and is a deliberate security property from inside.** Changes are rare, take years, and require overwhelming consensus.

**The 2015–2017 block-size war** is the defining episode: a years-long, bitter dispute over raising the block size to increase throughput. The small-block side won, arguing that larger blocks would price out home nodes and centralise validation. Opponents forked to Bitcoin Cash.

**Whatever you think of the outcome, it demonstrated something real:** the network refused a change that a substantial fraction of its economic and mining weight wanted. That is either admirable ossification or a failure to adapt, depending on your priors — and it's the clearest test any chain has run of "can this be changed by powerful stakeholders."

## What Bitcoin does that Ethereum doesn't

Worth stating plainly, because the ecosystems rarely acknowledge each other:

- **Credible monetary policy.** A fixed 21M supply, unchanged, with a strong social consensus against changing it. **Ethereum's issuance has changed repeatedly** by developer consensus — a real difference for anyone reasoning about the asset rather than the platform
- **Simplicity as a security property.** Far less code, far smaller attack surface, no smart contract risk. **Bitcoin's base layer has never been successfully exploited** — an extraordinary track record over sixteen years
- **The longest and most expensive security history.** More accumulated proof-of-work than anything else, by orders of magnitude

## Key insight

**Bitcoin's limitations are its feature set.** No loops means no gas. No accounts means no nonce and free replay protection. No upgrades means no upgrade risk. It is optimised for one job — being money that nobody can change the rules of — and it declines the generality that would compromise it. Reading it as "Ethereum without smart contracts" gets the design exactly backwards.

## Related
- [[web3/01-foundations/04-blocks-chains-and-state|blocks, chains and state]] — UTXO vs accounts
- [[web3/01-foundations/05-consensus|consensus]] — proof of work
- [[web3/01-foundations/02-the-double-spend-problem|the double-spend problem]] — what Bitcoin solved
- [[build-your-own-shit/14-your-own-blockchain|build your own blockchain]] — the guide builds a UTXO chain

*Source: [reference] — Aug 2026.*
