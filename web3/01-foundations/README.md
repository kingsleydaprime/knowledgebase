# Web3 Foundations

**The layer everything else assumes.** What problem blockchains solve, the primitives they're built from, how state is represented, who gets to write, and how it all reaches the network. Chain-agnostic — nothing here is specific to Ethereum.

If you read only two notes in this folder, read **02** (the problem) and **05** (the answer).

## Reading order
1. [[web3/01-foundations/01-what-web3-actually-is|what-web3-actually-is]] — **[Beginner]** — the vocabulary disentangled, the one technical claim underneath all of it, what you give up to get it, and the test that kills most blockchain proposals
2. [[web3/01-foundations/02-the-double-spend-problem|the-double-spend-problem]] — **[Beginner]** — why ordering (not detection) is the hard part, why Sybil resistance is the real problem, what was tried before 2008 and why it failed
3. [[web3/01-foundations/03-cryptographic-primitives|cryptographic-primitives]] — **[Intermediate]** — hashes as *identity*, Merkle proofs, recoverable signatures, and BIP-32/39/44. Assumes [[cybersecurity/05-cryptography/README|the cryptography course]] and covers only what's blockchain-specific
4. [[web3/01-foundations/04-blocks-chains-and-state|blocks-chains-and-state]] — **[Intermediate]** — block anatomy, why immutability is economic, **UTXO vs the account model**, and why state is derived rather than stored
5. [[web3/01-foundations/05-consensus|consensus]] — **[Advanced]** — PoW, PoS and BFT read through one question: *what does an attack cost and who does it cost?* Plus what a 51% attack can and cannot do
6. [[web3/01-foundations/06-networking-and-nodes|networking-and-nodes]] — **[Intermediate]** — gossip, the public mempool, node types, client diversity, and **the RPC-provider centralisation under most dapps**
7. [[web3/01-foundations/07-tokens-coins-and-nfts|tokens-coins-and-nfts]] — **[Beginner → Intermediate]** — a token is a row in a mapping; the approve footgun; decimals; and what an NFT actually is, said plainly

## Related
- [[web3/README|web3 curriculum map]]
- [[web3/02-ethereum-and-the-evm/README|02-ethereum-and-the-evm]] — the next layer up
- [[architecture/04-distributed-systems/README|distributed systems]] — the parent field
- [[cybersecurity/05-cryptography/README|cryptography]] — the primitives, properly
