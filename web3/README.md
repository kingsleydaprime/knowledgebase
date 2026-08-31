# Web3 & Blockchain

A map of this folder. Sections **01–08** are a numbered course built Aug 2026, running from *why this needed inventing* up through the EVM, Solidity, security, the multi-chain landscape, dapp architecture, the applications — and ending with an **honest assessment** that most material in this field doesn't have.

**Read [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|08/01]] early — right after foundations, not last.** Its four-question test kills most blockchain proposals in ten seconds, and holding it while you learn the rest keeps the whole domain in proportion. This folder is written for someone who wants to *understand and build* this properly, including knowing where it doesn't apply.

## Foundations **[Beginner → Advanced]**

[[web3/01-foundations/README|01-foundations/]] — the vocabulary disentangled and the one technical claim underneath all of it; why *ordering*, not detection, is the double-spend problem, and why Sybil resistance is the real difficulty; the cryptographic primitives (hashes as **identity**, Merkle proofs, recoverable signatures, BIP-32/39/44); block anatomy and **UTXO vs the account model**; PoW/PoS/BFT read through *what does an attack cost and who does it cost*; gossip, the public mempool and **the RPC-provider centralisation under most dapps**; and what a token actually is — a row in a mapping.

## Ethereum and the EVM **[Intermediate → Advanced]**

[[web3/02-ethereum-and-the-evm/README|02-ethereum-and-the-evm/]] — σ(t+1) = Υ(σ(t), T) and the account model; the EVM as a 256-bit stack machine with **four data locations whose costs drive everything**; gas as the halting problem priced, and EIP-1559's burn; the three nonce bugs and transaction types through EIP-7702; storage slots, packing, and **why reordering a variable can brick an upgrade**; and a deliberately dated roadmap note separating what shipped from what's promised.

## Smart Contracts with Solidity **[Beginner → Advanced]**

[[web3/03-smart-contracts-with-solidity/README|03-smart-contracts-with-solidity/]] — ten notes: what a smart contract is (and why "code is law" was tested once and lost); the language, assuming you can already program; **the storage-vs-memory rule that silently does nothing**; selectors, modifiers and `fallback`; events as the only push mechanism; inheritance and OpenZeppelin; token standards and **the four ways real tokens break the spec**; proxies and the argument that **upgradeability converts code-risk into key-risk**; gas optimisation; and testing, where **fuzzing and invariants are the baseline rather than advanced practice**.

## Smart Contract Security **[Intermediate → Advanced]**

[[web3/04-smart-contract-security/README|04-smart-contract-security/]] — **read this in parallel with 03, not after it.** Why the [[cybersecurity/README|appsec]] playbook doesn't transfer (no patching, no perimeter, funded adversaries); reentrancy including the three variants people miss; **access control and key management, the largest category of losses**; precision and rounding; flash loans and oracle manipulation; MEV; the audit process and how to read someone else's report; and **case studies — the single best note here**, whose table shows the money went somewhere different from where the field's attention goes.

## Beyond Ethereum **[Intermediate → Advanced]**

[[web3/05-beyond-ethereum/README|05-beyond-ethereum/]] — the scalability trilemma as a statement about **verification cost**, and how to deflate a TPS claim; rollups (optimistic vs zk, rollup vs sidechain, and the sequencer centralisation everyone glosses over); zero-knowledge proofs, where **succinctness matters more than the zero-knowledge part**; Solana's parallel-execution counter-argument, with an honest ledger of what the speed costs; Bitcoin, whose limitations are its feature set; **bridges — the worst security record in the field, and why it's structural**; and a six-question checklist for any chain you've never heard of.

## Building Dapps **[Intermediate → Advanced]**

[[web3/06-building-dapps/README|06-building-dapps/]] — the honest architecture diagram and what belongs on-chain vs in Postgres; wallets, signatures and the UX problems with no good answer yet; the RPC surface and **the seven-state transaction machine most dapps model as two**; **why you cannot query a blockchain** and the indexer everyone ends up building; storage, where IPFS solves integrity but not persistence; oracles, and why there is no safe on-chain randomness; and account abstraction.

## The Application Layer **[Intermediate → Advanced]**

[[web3/07-the-application-layer/README|07-the-application-layer/]] — DeFi's four primitives, and composability as both the feature and the systemic risk; what the NFT boom got wrong versus what the registry genuinely provides; DAOs, and why token voting is plutocracy by construction; ENS and **the Sybil problem underneath governance and lending**; and gaming, social, RWAs and supply chain — with a four-question test for any new proposal.

## The Honest Assessment **[Beginner → Intermediate]**

[[web3/08-the-honest-assessment/README|08-the-honest-assessment/]] — **the section most web3 material doesn't have.** What survives the "would a database do?" test and what doesn't; **how people actually lose money, which is mostly not smart contract exploits**; regulation, and why decentralisation is not a shield for the people around a protocol; and energy — what the Merge actually changed, and why the surviving externalities aren't environmental.

## Frameworks

[[web3/frameworks/README|frameworks/]] — the per-language implementation layer, copying the [[backend/frameworks/README|backend/frameworks]] convention: **[[web3/frameworks/solidity/README|solidity/]]** (Foundry, Hardhat, OpenZeppelin, Slither), **[[web3/frameworks/rust/README|rust/]]** (Solana/Anchor, CosmWasm, ink!, and the infrastructure clients), **[[web3/frameworks/javascript/README|javascript/]]** (viem, wagmi, Ponder — the client layer), **[[web3/frameworks/python/README|python/]]** (web3.py, and the security tooling that's genuinely best-in-class), and **[[web3/frameworks/go/README|go/]]** (geth, Cosmos SDK, backend services).

## Interview

[[web3/interview/README|interview/]] — the web3 round: fundamentals, the EVM, Solidity and security, building, and the judgement questions. Honestly labelled as course-derived rather than reps-derived.

## Build it

Three guides in [[build-your-own-shit/README|build-your-own-shit/]], ordered by depth:

- [[build-your-own-shit/14-your-own-blockchain|Your Own Blockchain]] — blocks → PoW → P2P → UTXO → wallets → fork choice. **Makes sections 01 and 05 concrete**
- [[build-your-own-shit/15-your-own-smart-contract-vm|Your Own Smart Contract VM]] — a stack machine with gas metering. **The deepest of the three**, and it pairs with [[foundations/compilers/README|compilers]]
- [[build-your-own-shit/16-your-own-token-and-wallet|Your Own Token and Wallet]] — ERC-20 from scratch, HD wallet, NFT, deployed to a testnet. **The most applied, and the best first one**

## Related
- [[web3/projects|Projects]] — **the reps for this domain**, graded 🟢🟡🔴 with a *done when* for each
- [[cybersecurity/README|cybersecurity]] — the parent security discipline, and what doesn't transfer
- [[cybersecurity/05-cryptography/README|cryptography]] — the primitives, properly
- [[architecture/04-distributed-systems/README|distributed systems]] — the field this is a subfield of
- [[foundations/compilers/09-bytecode-and-virtual-machines|bytecode VMs]] — the general category the EVM belongs to
- [[backend/README|backend]] · [[frontend/README|frontend]] — the 90% of a dapp that's ordinary web development
