# What Web3 Actually Is

**[Beginner]** — the vocabulary, the one technical claim underneath all of it, and how to tell the engineering from the marketing. Assumes nothing.

## The kid version first

Normally, when you own something digital — money in a bank, a username, an item in a game — **one company keeps the list that says you own it.** They can edit that list. You trust them not to.

A blockchain is a way for **thousands of strangers to each keep a copy of the same list**, and agree on what it says, **without any of them being in charge.** That's it. That's the whole invention.

Everything else — coins, NFTs, DeFi, DAOs — is an application built on "we can all agree on a list without a boss."

## The terms, disentangled

The words get used interchangeably by people selling things. They are not the same:

| Term | What it actually means |
|---|---|
| **Blockchain** | A specific data structure: a chain of blocks, each committing to the previous by hash. Not inherently decentralised — a company can run one alone (and usually shouldn't) |
| **Distributed ledger** | The general category. A shared, replicated database. Blockchain is one design |
| **Cryptocurrency** | A blockchain whose ledger tracks token balances, with a native asset used to pay for writes |
| **Web3** | A marketing-adjacent umbrella term for *applications* built on public blockchains. Coined by contrast with "Web2" (platform-owned) |
| **Smart contract** | A program deployed to a blockchain, whose execution every node reproduces and agrees on |
| **DeFi** | Financial applications (lending, exchange, derivatives) as smart contracts |
| **NFT** | A token whose units are individually distinct rather than interchangeable |
| **DApp** | An application whose backend is partly a smart contract |

**"Web3" is the weakest of these terms** — it describes a vibe and an investment thesis more than a technology. The engineering underneath is real; the term is not load-bearing. This folder uses it because that's what the field is called, not because it's a good name.

## The one technical claim

Strip away everything else and a blockchain makes exactly one novel offer:

> **Verifiable state, agreed by parties who don't trust each other, with no administrator.**

Three parts, all necessary:

1. **Verifiable** — anyone can independently check the current state is the correct consequence of the history. You don't take anyone's word for it
2. **Agreed** — everyone converges on the same answer, even under network delays and active attackers
3. **No administrator** — nobody can unilaterally rewrite it, censor it, or switch it off

**Remove the third and you don't need a blockchain.** A Postgres database with an audit log and signed writes gives you (1) and (2) at a millionth of the cost. This is the single most useful test to apply to any blockchain proposal, and it kills most of them → [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|what blockchains are actually good for]].

## What you give up to get it

The trade is real and steep:

- **Throughput.** Ethereum settles on the order of 15–100 transactions per second at L1. Visa handles thousands. Every node executes every transaction — that's the point, and it's also the ceiling
- **Latency.** Finality is seconds to minutes, not microseconds
- **Cost.** You pay per unit of computation and per byte of storage, forever, to everyone
- **Privacy.** Public chains are public. Your balance and every transaction you have ever made are readable by anyone → [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge proofs]] are partly an answer to this
- **Irreversibility.** No chargebacks, no password reset, no support line. Lose the key, lose the asset. This is a feature and a catastrophe depending on the day

A blockchain is **a very slow, very expensive, very public computer that nobody owns.** You pay all of that for the "nobody owns" part. When that property is worth it, nothing else does the job. When it isn't, you have built a bad database.

## Public, private, permissioned

- **Public / permissionless** (Bitcoin, Ethereum) — anyone can read, write, and run a node. The decentralisation claim is meaningful
- **Permissioned / consortium** (Hyperledger Fabric, R3 Corda) — a known set of organisations run the nodes. Useful in narrow inter-company settlement cases; **mostly a replicated database with extra steps**, and the enterprise-blockchain wave of 2016–2020 largely ended in that realisation
- **Private** — one company, one chain. Almost always the wrong tool

This folder is about **public chains**, because that's where the interesting engineering and the actual use cases are.

## The layers, so you know where you are

```
   Application    DeFi protocols, NFT markets, DAOs, games
                  ─────────────────────────────────────────
   Contract       Smart contracts (Solidity, Rust, Move)
                  ─────────────────────────────────────────
   Execution      The VM — EVM, SVM, WASM. Deterministic, metered
                  ─────────────────────────────────────────
   Consensus      Who gets to append the next block, and when is it final
                  ─────────────────────────────────────────
   Network        P2P gossip, mempool, node discovery
                  ─────────────────────────────────────────
   Data           Blocks, hashes, Merkle trees, signatures
```

The rest of this course walks up that stack: [[web3/01-foundations/README|01-foundations]] covers data through consensus, [[web3/02-ethereum-and-the-evm/README|02]] covers execution, [[web3/03-smart-contracts-with-solidity/README|03]] the contract layer, [[web3/07-the-application-layer/README|07]] the top.

## Key insight

**The blockchain is not a better database. It's a worse database with one property no database has** — that it keeps working when the parties running it actively want to cheat each other. Every design decision in this folder, and every cost, follows from buying that one property.

## Related
- [[web3/01-foundations/02-the-double-spend-problem|the double-spend problem]] — why this needed inventing at all
- [[web3/08-the-honest-assessment/README|the honest assessment]] — read this early, not last
- [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|what makes distributed systems hard]] — the field this is a subfield of
- [[cybersecurity/05-cryptography/README|cryptography]] — the primitives this is assembled from

*Source: [reference] — Aug 2026.*
