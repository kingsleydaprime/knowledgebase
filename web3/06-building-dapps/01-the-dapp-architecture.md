# The Dapp Architecture

**[Intermediate]** — what actually goes on-chain, what doesn't, and the honest diagram of a "decentralised" application.

## The kid version first

A dapp is a **normal web app** with one unusual part: instead of your server writing to your database, **the user's wallet writes to a shared public database that nobody owns.**

Everything else — the React app, the API, the images, the search — is ordinary web development. The chain is one component, and usually the smallest one.

## The honest diagram

```
┌─ Browser ─────────────────────────────────────────────────┐
│  React/Next frontend                                      │
│      │                          │                         │
│      │ read                     │ write                   │
│      ▼                          ▼                         │
│  viem / wagmi              Wallet (MetaMask, WalletConnect)│
└──────┼──────────────────────────┼─────────────────────────┘
       │                          │ user signs — the key NEVER leaves
       ▼                          ▼
   RPC provider  ◄────────────► the chain
   (Alchemy/Infura)                 │
       ▲                            │ events
       │                            ▼
   Indexer (The Graph / Ponder) ──► Postgres ──► your API
                                                    ▲
   IPFS / Arweave ──────────────────────────────────┘
   (images, metadata, anything large)
```

**Count the centralised components.** The RPC provider, the indexer, the API, the storage gateway, the frontend host, the domain name. **A typical "decentralised app" has exactly one decentralised component: the contract.** That's not a criticism — it's the actual architecture, and pretending otherwise leads to bad decisions.

## What belongs on-chain

Storage costs 20,000 gas per slot and burdens every node forever, so the bar is high. **On-chain only if it needs the chain's guarantees:**

| On-chain | Off-chain |
|---|---|
| Ownership and balances | Images, video, documents |
| Rules that must be enforced trustlessly | User profiles, display names |
| Anything requiring censorship resistance | Search indexes, feeds |
| Settlement and value transfer | Analytics, recommendations |
| State other contracts compose with | Anything mutable and cheap |

**The test:** *does this need to be true even if my company disappears or turns hostile?* If not, use Postgres. It's a thousand times cheaper and a thousand times faster.

**Common over-application:** putting user profiles, comments, metadata or game state on-chain because it's "a web3 app." That's expensive, slow, permanently public, and unfixable. Put the *ownership* on-chain and the rest in a database.

## Reading vs writing — completely different paths

**Reads** are free, instant, and need no wallet:
```ts
const balance = await publicClient.readContract({ address, abi, functionName: 'balanceOf', args: [user] })
```
No gas, no signature, no transaction. `eth_call` simulates against current state.

**Writes** cost money, take seconds, require a signature, and **can fail after being submitted**:
```ts
const hash = await walletClient.writeContract({ address, abi, functionName: 'transfer', args: [to, amount] })
const receipt = await publicClient.waitForTransactionReceipt({ hash })
if (receipt.status === 'reverted') { /* it failed, and the user still paid */ }
```

**The write path has states no web developer's instincts cover:** signature rejected by the user, submitted but pending for minutes, mined but reverted, mined then **reorged away**. A UI that models a transaction as "loading → done" is wrong in four different ways → [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading and writing]].

## The three things that will bite you

**1. You can't query the chain.** There is no `SELECT * FROM transfers WHERE user = ?`. The chain answers "what is the state of slot X now" and nothing else. **Every list, feed, history and leaderboard requires an indexer** → [[web3/06-building-dapps/04-indexing-and-events|indexing]]. Discovering this late causes rewrites.

**2. Latency is seconds, and failure is normal.** Optimistic UI is necessary but must be reversible — the transaction may revert or be reorged. **Show pending state honestly**, and never confirm success before the receipt.

**3. Your RPC provider is a single point of failure** that can censor, lie, rate-limit, or go down — taking your "decentralised" app with it → [[web3/01-foundations/06-networking-and-nodes|nodes and RPC]].

## The stack, as of 2026

| Layer | Use |
|---|---|
| **Contracts** | Solidity + Foundry + OpenZeppelin |
| **Chain client** | **viem** (TypeScript, type-safe, the default). ethers.js is the mature alternative; web3.js is deprecated |
| **React hooks** | **wagmi** — hooks over viem for connection, reads, writes, transaction state |
| **Wallet connection** | RainbowKit or ConnectKit (over wagmi + WalletConnect) |
| **Indexing** | The Graph (hosted subgraphs) or **Ponder** (TypeScript, self-hosted) |
| **RPC** | Alchemy / QuickNode, **plus a fallback** |
| **Storage** | IPFS via Pinata, or Arweave for permanence |
| **Frontend** | Next.js — nothing web3-specific about this half |

**viem + wagmi is the current default**, and TypeScript type inference from your ABI is a genuine quality-of-life difference over ethers.

## Decentralising the rest, honestly

If it matters for your application:

- **Host the frontend on IPFS**, addressed by ENS (`yourapp.eth`). Real, and used by Uniswap
- **Run your own node**, or use a verifying light client (Helios) rather than trusting an RPC
- **Publish the contract source** and let users interact directly via Etherscan — a genuine escape hatch that costs you nothing to provide

**Most projects do none of this**, which is a defensible choice as long as it's a choice. **The question worth answering honestly at design time: if your company vanishes tomorrow, can users still get their assets out?** For a well-designed protocol the answer is yes — via Etherscan, at minimum. Making sure of that is cheap, and it's most of what "decentralised" is worth in practice.

## Key insight

**A dapp is 90% ordinary web application and 10% chain, and the 10% has completely different failure modes** — reads that are free, writes that cost money and fail after submission, no query language, and a hosted RPC in the middle of your trustless architecture. The engineering skill is knowing which 10% genuinely needs the chain, and building the rest the way you'd build anything.

## Related
- [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading and writing chain state]]
- [[web3/06-building-dapps/04-indexing-and-events|indexing and events]] — the constraint that shapes the architecture
- [[frontend/README|frontend]] — the other 90%
- [[web3/frameworks/javascript/README|JS/TS for web3]] — viem, wagmi, ethers
