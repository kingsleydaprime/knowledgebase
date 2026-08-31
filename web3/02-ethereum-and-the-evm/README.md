# Ethereum and the EVM

**The execution layer.** Ethereum is the reference implementation of "blockchain as a computer" rather than "blockchain as a ledger" — and the EVM is now a target that dozens of other chains implement, so learning it once transfers widely.

Read [[web3/01-foundations/README|01-foundations]] first. Notes **02** and **05** are the ones that change how you write Solidity.

## Reading order
1. [[web3/02-ethereum-and-the-evm/01-the-world-computer|the-world-computer]] — **[Intermediate]** — σ(t+1) = Υ(σ(t), T), the account model, transaction fields, and why a revert refunds state but not gas
2. [[web3/02-ethereum-and-the-evm/02-the-evm|the-evm]] — **[Advanced]** — a 256-bit stack machine: **the four data locations and their costs**, the opcodes worth knowing (especially `DELEGATECALL`), precompiles, and why deployment runs init code
3. [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas-and-fees]] — **[Intermediate]** — the halting problem priced; EIP-1559's burn; where gas actually goes; and the failure modes (out-of-gas, stuck nonces, gas griefing)
4. [[web3/02-ethereum-and-the-evm/04-transactions-and-the-mempool|transactions-and-the-mempool]] — **[Intermediate]** — the three nonce bugs, transaction types through EIP-7702, PBS, and why the mempool is adversarial
5. [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage-layout-and-the-state-trie]] — **[Advanced]** — slots, packing, how mappings are hashed, **why reordering a variable can brick an upgrade**, and the Merkle Patricia Trie
6. [[web3/02-ethereum-and-the-evm/06-the-ethereum-roadmap|the-ethereum-roadmap]] — **[Intermediate]** — what shipped vs what's promised, and how to read roadmap claims sceptically. **The note most likely to age**

## Related
- [[web3/README|web3 curriculum map]]
- [[web3/03-smart-contracts-with-solidity/README|03-smart-contracts-with-solidity]] — writing for this machine
- [[foundations/compilers/09-bytecode-and-virtual-machines|bytecode VMs]] — the general category the EVM belongs to
- [[build-your-own-shit/15-your-own-smart-contract-vm|build your own smart contract VM]] — the fastest way to make this folder concrete
