# Upgradeability and Proxies

**[Advanced]** — how to change immutable code, the storage rules that make it survivable, and the honest argument that upgradeability is a centralisation decision rather than a technical one.

## The kid version first

Deployed code can't change. So instead of one contract, you deploy **two**: a permanent front door with all the money and data in it, and a swappable back room with the logic. The front door forwards every call to the back room, but **the back room runs using the front door's data.**

Swap the back room and you've "upgraded." **Which also means whoever can swap it can replace your contract with one that empties it.**

## The mechanism: `DELEGATECALL`

```
user ──call──►  Proxy  ──DELEGATECALL──►  Implementation
                  │                              │
             holds storage                  holds code
             holds ETH                      holds NO state
             holds the address of ──────────────┘
```

`DELEGATECALL` runs the target's code **in the caller's context**: the proxy's storage, the proxy's balance, and the *original* `msg.sender` and `msg.value`. The implementation is a code library that believes it's the proxy.

The proxy is essentially just a fallback:

```solidity
fallback() external payable {
    address impl = _implementation();
    assembly {
        calldatacopy(0, 0, calldatasize())
        let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
        returndatacopy(0, 0, returndatasize())
        switch result
        case 0 { revert(0, returndatasize()) }
        default { return(0, returndatasize()) }
    }
}
```

That's the whole pattern. Everything else is safety scaffolding around it.

## The three rules you cannot break

**1. Storage layout is append-only.** The implementation's variable declarations determine which of the *proxy's* slots it reads. Reorder, retype or remove a variable and the new code reads old data as something else → [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]]. Reserve `uint256[50] private __gap;` in every base contract so inheritance can grow. **Run a layout diff in CI** — `forge inspect` or the OpenZeppelin upgrades plugin. This is the check that actually prevents the disaster.

**2. No constructors. Use initialisers.** A constructor runs at *the implementation's* deployment and writes to *its* storage — which the proxy never reads. So state must be set through an `initialize()` function called on the proxy:

```solidity
function initialize(address owner_) public initializer {   // `initializer` = once only
    __Ownable_init(owner_);
}
```

Use `@openzeppelin/contracts-upgradeable`, not the standard package.

**3. Lock the implementation.** An uninitialised implementation contract is directly callable, and **anyone can initialise it and become its owner.** With a `selfdestruct`-capable or `delegatecall`-capable function, they can then destroy it and brick every proxy pointing at it. **This is the Parity multisig freeze of November 2017 — ~$280M rendered permanently inaccessible**, and the mechanism was exactly this.

```solidity
constructor() { _disableInitializers(); }   // on the implementation. Non-negotiable
```

## The patterns

| Pattern | Where the upgrade logic lives | Notes |
|---|---|---|
| **Transparent (ERC-1967)** | In the proxy | The admin can't call implementation functions, avoiding selector collisions. Costs an extra `SLOAD` per call. Largely superseded |
| **UUPS (ERC-1822)** | In the **implementation** | Cheaper calls, smaller proxy. **Risk: ship an implementation without `_authorizeUpgrade` and the contract is permanently frozen** |
| **Beacon** | In a shared beacon contract | One upgrade updates many proxies at once. Right for factory-deployed contracts |
| **Diamond (ERC-2535)** | Per-function routing table | Routes each selector to a different "facet". Escapes the 24KB limit. **Complex, harder to audit, and the ecosystem has largely moved away from it** |

**UUPS is the current default.** Use OpenZeppelin's implementation rather than writing one.

**ERC-1967 fixes the collision problem** by storing the implementation address at `keccak256("eip1967.proxy.implementation") - 1` — a slot no compiler will assign, so proxy metadata can never collide with application variables. Any hand-rolled proxy that puts the implementation address in slot 0 has a live bug.

## The honest argument

**An upgradeable contract is not immutable. It is a contract that a specific party can replace with arbitrary code.**

That party can, at any moment:
- Replace the logic with a version that transfers all funds to itself
- Do it in one transaction, with no warning
- Do it because they chose to, or because their key was stolen

**So the security of an "immutable, trustless" upgradeable protocol reduces entirely to the security of its upgrade key.** All the auditing in the world sits behind that one door.

Mitigations, and they are real:
- **A multisig** (Safe) rather than an EOA — several keys required
- **A timelock** on upgrades: queue, wait 48 hours, execute. Users get a window to exit if the queued code is malicious. **This is the single most valuable mitigation**, because it converts a silent rug into a public one
- **Governance-controlled** upgrades → [[web3/07-the-application-layer/03-daos-and-governance|DAOs]]
- **Renouncing upgradeability** once the protocol is stable — genuinely immutable, genuinely unfixable

**And the real question, asked first:** does this need to be upgradeable at all? Uniswap's core contracts are immutable; new versions are new deployments users migrate to voluntarily. That is a coherent alternative — it trades "we can fix bugs" for "we cannot rug you," and for a protocol holding other people's money it is often the better trade.

**When you evaluate any protocol, find the upgrade key and the timelock delay before reading anything else.** It tells you more about your actual risk than the audit report does.

## Key insight

**Upgradeability converts a code-risk into a key-risk.** Immutable contracts can be exploited but never rugged; upgradeable ones can be patched but always trusted. Neither is correct in general — but pretending an upgradeable protocol is trustless is a category error, and it's the most common one in the field.

## Related
- [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]] — the rules' origin
- [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]] — securing the upgrade key
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — Parity, in full
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — `DELEGATECALL`

*Source: [reference] — OpenZeppelin v5, ERC-1967/1822. Aug 2026.*
