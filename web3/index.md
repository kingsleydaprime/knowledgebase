# Web3 & Blockchain

## What a blockchain is

**A blockchain is a shared record of transactions, copied across thousands of computers, that nobody can secretly change and no single company controls.**

Normally a bank keeps the record of who owns what money, and you trust the bank. A blockchain removes that single keeper: thousands of computers each hold a copy, and they follow strict rules, backed by cryptography, to agree on which new transactions get added and in what order. Once something is added, changing it would mean overpowering most of the network. Bitcoin uses this to run money without a bank. Ethereum goes further and runs small programs called **smart contracts**, which hold and move money according to their code.

"Web3" is the umbrella name for apps built on blockchains. Some are genuinely new; many would work better with an ordinary database. This course teaches you to build in this field properly, and also when *not* to use a blockchain at all.

## What you'll be able to do

By the end you will be able to:
- explain how a blockchain reaches agreement without anyone in charge, and what an attack would cost;
- explain how Ethereum runs programs, and why every operation costs a fee;
- write smart contracts in Solidity, and test them thoroughly;
- recognise the common security mistakes that have cost billions, and avoid them;
- compare blockchains, and see through exaggerated speed claims;
- build a web app (a "dapp") that talks to a blockchain;
- judge honestly whether a proposed blockchain project needs a blockchain at all.

## Where to start

**Before you start:** programming, and ideally some [[backend/index|backend]] and [[cybersecurity/05-cryptography/index|cryptography]].

1. **Start with [[web3/01-foundations/index|Foundations]]:** how blockchains reach agreement, the cryptography they use, blocks, and what a token really is (a row in a table).
2. **Then read [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|What Blockchains Are Actually Good For]]** before going further. Its four-question test rules out most blockchain ideas in seconds, and keeps the rest of the course in proportion.
3. **Then the rest, in order:**
   - [[web3/02-ethereum-and-the-evm/index|Ethereum and the EVM]]: how Ethereum runs programs, fees, and how a contract's data is stored.
   - [[web3/03-smart-contracts-with-solidity/index|Smart Contracts with Solidity]]: writing contracts: the language, tokens, upgrading contracts, saving fees, and testing.
   - [[web3/04-smart-contract-security/index|Smart Contract Security]]: **read this alongside Solidity, not after it.** Contracts can't be patched once released and attackers are well funded. Ends with real case studies, the best note here.
   - [[web3/05-beyond-ethereum/index|Beyond Ethereum]]: why blockchains struggle to be fast, cheap and secure at once, the networks built on top of Ethereum, zero-knowledge proofs, Solana, Bitcoin, and bridges between chains (the worst security record in the field).
   - [[web3/06-building-dapps/index|Building Dapps]]: building an app around a blockchain: what goes on the chain and what goes in a normal database, wallets, and why you can't simply search a blockchain.
   - [[web3/07-the-application-layer/index|The Application Layer]]: finance on the blockchain (DeFi), NFTs, DAOs (groups run by token votes), and other uses, with a test for new proposals.
   - [[web3/08-the-honest-assessment/index|The Honest Assessment]]: what survives the "would a database do?" test, how people actually lose money, regulation, and energy use.

## Frameworks

- [[web3/frameworks/index|Frameworks overview]], then by language: [[web3/frameworks/solidity/index|Solidity]] (Foundry, Hardhat, OpenZeppelin), [[web3/frameworks/rust/index|Rust]] (Solana and others), [[web3/frameworks/javascript/index|JavaScript]] (connecting web apps), [[web3/frameworks/python/index|Python]] (scripting and security tools) and [[web3/frameworks/go/index|Go]] (node software and backends).

## Practice

- **Build your own,** from most applied to deepest: [[build-your-own-shit/16-your-own-token-and-wallet|your own token and wallet]] (the best first one), [[build-your-own-shit/14-your-own-blockchain|your own blockchain]], and [[build-your-own-shit/15-your-own-smart-contract-vm|your own smart contract virtual machine]].
- [[web3/projects|Projects]]: graded tasks with a clear "done when".
- [[web3/interview/index|Web3 interview prep]].

## Key ideas to remember

1. **Most blockchain ideas would work better as a database.** Ask the four questions first. → [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|The honest assessment]]
2. **The hard part isn't spotting double-spending; it's agreeing on the order of transactions** when anyone can join and fake many identities. → [[web3/01-foundations/index|Foundations]]
3. **A released contract can't be patched,** so security work happens before release. → [[web3/04-smart-contract-security/index|Security]]
4. **Making a contract upgradeable swaps the risk of buggy code for the risk of a stolen key.** → [[web3/03-smart-contracts-with-solidity/index|Solidity]]
5. **Most people lose money to scams and stolen keys,** not clever contract hacks. → [[web3/08-the-honest-assessment/index|The honest assessment]]
6. **About 90% of a blockchain app is ordinary web development.** → [[web3/06-building-dapps/index|Building Dapps]]

## Related

- [[cybersecurity/index|Cybersecurity]] and [[cybersecurity/05-cryptography/index|Cryptography]]: the security and maths underneath.
- [[architecture/04-distributed-systems/index|Distributed Systems]]: the wider field blockchains belong to.
- [[compilers/10-bytecode-and-virtual-machines|Bytecode and Virtual Machines]]: the kind of machine Ethereum runs.
- [[backend/index|Backend]] and [[frontend/index|Frontend]]: the rest of a blockchain app.

---

## About this course

- **Size:** 8 sections plus framework guides and interview prep, written in August 2026.
- **Where it came from:** reference sources. The interview questions come from the course, not from real interviews.
