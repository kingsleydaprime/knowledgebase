# Building Dapps

**The applied section.** How the contract layer connects to an actual product — and the constraints (no query language, seconds-long writes that can fail after payment, a hosted RPC in the middle) that shape every dapp architecture.

**The note that saves the most rework is [[web3/06-building-dapps/04-indexing-and-events|04-indexing-and-events]].** Discovering that you cannot query a blockchain *after* designing your product is a common and expensive surprise.

## Reading order
1. [[web3/06-building-dapps/01-the-dapp-architecture|the-dapp-architecture]] — **[Intermediate]** — the honest diagram, what belongs on-chain vs in Postgres, the stack as of 2026, and **counting the centralised components**
2. [[web3/06-building-dapps/02-wallets-and-connection|wallets-and-connection]] — **[Intermediate]** — what a wallet is, connection vs authentication, the three signature types, **and the UX problems with no good answer yet**
3. [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading-and-writing-chain-state]] — **[Intermediate]** — the RPC surface, multicall, simulate-before-send, and **the seven-state transaction machine most dapps model as two**
4. [[web3/06-building-dapps/04-indexing-and-events|indexing-and-events]] — **[Intermediate]** — **why you cannot query a blockchain**, the indexer pipeline, reorg handling, and designing contracts to be indexable
5. [[web3/06-building-dapps/05-decentralised-storage|decentralised-storage]] — **[Intermediate]** — IPFS solves integrity, not persistence; Arweave, fully on-chain, and **why NFT images disappear**
6. [[web3/06-building-dapps/06-oracles|oracles]] — **[Intermediate]** — the trust you can't avoid, the Chainlink checks everyone omits, and **why there is no safe on-chain randomness**
7. [[web3/06-building-dapps/07-account-abstraction|account-abstraction]] — **[Advanced]** — ERC-4337 and EIP-7702, sponsored gas, session keys, social recovery — and an honest status report

## Related
- [[web3/README|web3 curriculum map]]
- [[web3/frameworks/javascript/README|JS/TS for web3]] — viem, wagmi, the code
- [[frontend/README|frontend]] — the 90% of a dapp that's ordinary web development
- [[web3/03-smart-contracts-with-solidity/README|smart contracts]] — the other side of the wire
