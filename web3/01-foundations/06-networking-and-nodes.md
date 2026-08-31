# The Network Layer — Nodes, Gossip and the Mempool

**[Intermediate]** — how a transaction physically reaches a block, what kinds of node exist, and why your RPC provider is the quiet centralisation in almost every dapp.

## The kid version first

There's no server. When you send a transaction, your wallet hands it to **one computer it happens to know**, which tells its neighbours, which tell theirs — like gossip through a crowd. Within a couple of seconds most of the network has heard it. Someone building the next block picks it up and includes it.

Nothing was ever "submitted" anywhere. **It was rumoured until it stuck.**

## The lifecycle of a transaction

```
1. SIGN       wallet signs locally — the private key never moves
2. SUBMIT     sent to one node, usually via JSON-RPC eth_sendRawTransaction
3. VALIDATE   that node checks: signature, nonce, balance ≥ value+gas, fee floor
4. GOSSIP     valid → added to its mempool, forwarded to ~8-50 peers, recursively
5. PENDING    lives in thousands of mempools. PUBLIC AND VISIBLE. This is where MEV happens
6. INCLUDE    a block builder selects it — normally fee-ordered — into a block
7. PROPAGATE  the block gossips out; every node re-executes every transaction
8. FINALISE   enough attestations accumulate that reversal becomes infeasible
```

**Step 5 is the one with security consequences.** Between broadcast and inclusion, your transaction is a public statement of intent that anyone can read and react to before it executes. That gap is the entire foundation of front-running → [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]].

## The P2P layer

Chains run their own gossip protocols over TCP/UDP, not HTTP:

- **Ethereum** uses **devp2p** with **discv5** (a Kademlia-style DHT) for peer discovery, and RLPx — an encrypted, authenticated transport — for the sessions
- **Bitcoin** uses a simpler protocol with DNS seeds for bootstrap

Two properties that shape everything above them:

**Propagation is not instant.** A block takes on the order of hundreds of milliseconds to reach most of the network. That delay is *why* competing blocks and reorgs exist at all, and it's why block times are seconds rather than milliseconds — the interval must exceed propagation time by a comfortable margin or the network forks constantly.

**Bandwidth, not CPU, is usually the binding constraint** on decentralisation. Raising the gas limit raises the bandwidth needed to keep up, which prices out home nodes. "Why not just make blocks bigger" has this as its real answer, and it's a genuine engineering constraint rather than conservatism → [[foundations/networking/README|networking]].

## Node types, and what each can prove

Ethereum splits a node into **two coupled clients** since the Merge — an **execution client** (Geth, Nethermind, Reth, Erigon) and a **consensus client** (Lighthouse, Prysm, Teku, Nimbus), talking over the Engine API. Running "a node" means running one of each.

| Type | Stores | Can verify | Disk (Ethereum, 2026) |
|---|---|---|---|
| **Full (pruned)** | Recent state + all headers | Everything, from its sync point | ~1.2 TB and growing |
| **Archive** | Every historical state | Everything, plus arbitrary past queries | ~15+ TB |
| **Light** | Headers only | Its own claims, via Merkle proofs | Megabytes |

**Client diversity is a live safety issue, not a preference.** If one execution client holds a supermajority and ships a consensus bug, it can finalise an invalid chain — a correctness failure no amount of stake prevents. Geth's historical dominance has been the ecosystem's most-discussed systemic risk for years.

## The RPC problem — the quiet centralisation

Almost nobody runs a node. Wallets and dapps talk to **hosted RPC providers** — Infura, Alchemy, QuickNode, or a chain's public endpoint. So the actual topology of most "decentralised" applications is:

```
   your dapp ──► Infura ──► the network
                   ▲
          a single company, one API key,
          one terms-of-service, one outage
```

This is real and worth being blunt about:

- **They can censor.** Infura has blocked addresses and entire regions to comply with sanctions
- **They can lie.** You are trusting returned state without verifying it — the exact trust assumption blockchains exist to remove
- **They are a single point of failure.** Infura outages have taken down large parts of the ecosystem simultaneously, MetaMask included
- **They see everything.** Every address you look up, tied to your IP

**Mitigations, in order of seriousness:** run your own node (real, and increasingly practical on consumer hardware); use a light client that verifies proofs (Helios and similar verify against the consensus layer rather than trusting an RPC); or at minimum, use more than one provider and compare. Most projects do none of these — which is worth knowing when someone calls their architecture trustless → [[web3/06-building-dapps/01-the-dapp-architecture|dapp architecture]].

## Key insight

**A blockchain's decentralisation is bounded by what an ordinary person can afford to run.** Every parameter — block size, gas limit, state growth, block time — is really a knob trading throughput against how many people can independently verify. And the layer most dapps actually depend on, the hosted RPC, has quietly opted out of verification altogether.

## Related
- [[foundations/networking/README|networking]] — the P2P, TCP and DNS mechanics underneath
- [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|MEV]] — what the public mempool enables
- [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading and writing chain state]] — the JSON-RPC API in practice
- [[build-your-own-shit/14-your-own-blockchain|build your own blockchain]] — the gossip layer is milestone 5

*Source: [reference] — Aug 2026.*
