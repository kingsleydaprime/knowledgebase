# Access Control and Key Management

**[Intermediate]** — the largest category of losses in the field, and the least technically interesting.

## The uncomfortable headline

**More value has been lost to "the admin key was stolen" and "that function had no modifier" than to every clever cryptographic exploit combined.** The Ronin bridge ($625M) was compromised validator keys. Harmony ($100M) was compromised multisig keys. Parity's first loss ($31M) was a missing visibility specifier.

**The exciting vulnerabilities are not where the money went.** Plan accordingly.

## The `msg.sender` vs `tx.origin` rule

```solidity
require(msg.sender == owner);    // CORRECT — the immediate caller
require(tx.origin == owner);     // EXPLOITABLE — the EOA that started the chain
```

`tx.origin` is the account that signed the transaction, no matter how many contracts deep you are. So if the owner is ever tricked into calling **any** malicious contract, that contract can call yours and the check passes:

```
owner ──► Malicious.claimAirdrop() ──► YourContract.withdrawAll()
                                        tx.origin == owner  ✓  passes
                                        msg.sender == Malicious  ✗ would have failed
```

**Never use `tx.origin` for authorisation.** Its only legitimate uses are niche (and EIP-7702 has made even those questionable).

Relatedly: **`msg.sender == tx.origin` as an "is this an EOA?" check is broken.** A contract's constructor runs before its code is stored, so `address.code.length == 0` is true for a contract calling out during construction. Both EOA checks are bypassable, and account abstraction makes the distinction meaningless anyway.

## Patterns, in order of seriousness

**Ownable** — one address, all privileges. Fine for small contracts, and a single point of failure:

```solidity
import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";
```

**Use `Ownable2Step`, not `Ownable`.** Transfer requires the new owner to *accept*, which prevents the "transferred ownership to a typo'd address, contract now permanently unowned" failure. This has happened to real protocols.

**Role-based (`AccessControl`)** — separate roles for separate powers, so no single key does everything:

```solidity
bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

function pause() external onlyRole(PAUSER_ROLE) { _pause(); }
```

**Grant least privilege, and separate the admin role from the operational ones.** A hot key that can pause is a reasonable risk; a hot key that can upgrade is not.

**Multisig (Safe)** — *m*-of-*n* signatures. The practical default for anything holding real value. The considerations that actually matter:

- **Signer independence.** 5 keys on one person's laptops is 1 key. Different people, different devices, different locations, different jurisdictions
- **The threshold is a real trade.** 2-of-3 is convenient and one compromise plus one absence from being a disaster. 4-of-7 is the usual serious answer
- **Ronin is the cautionary tale**: 5-of-9, but 4 keys were held by one entity and a 5th was reachable through a gas-subsidy agreement that had been left in place. **The multisig was 5-of-9 on paper and effectively 1-of-1.** Count *independent* signers, not keys

**Timelock** — privileged actions queue, wait, then execute. **This is the highest-value control in the list**, because it converts a silent compromise into a public one: users get a window to exit before malicious code executes. 48 hours is common; anything under 24 hours provides little practical protection.

## The initialiser trap

For upgradeable contracts, the constructor doesn't run in the proxy's context, so ownership is set in `initialize()`:

```solidity
function initialize(address owner_) public initializer { ... }
```

**Two ways this goes wrong, both of which have cost real money:**

1. **Deploy the proxy and forget to initialise it in the same transaction.** Anyone can front-run and call `initialize` themselves, becoming owner
2. **Leave the *implementation* uninitialised.** Anyone initialises it directly, becomes its owner, and — with any `delegatecall` or `selfdestruct` reachable — bricks every proxy pointing at it. **This is the Parity multisig freeze, ~$280M permanently locked**

```solidity
constructor() { _disableInitializers(); }   // on the implementation. Always
```

**And atomically initialise the proxy at deployment**, in the same transaction, via the proxy's constructor data.

## Key management, operationally

**Never in a repo, never in `.env` committed, never in a screenshot, never in a chat.** Automated scrapers watch GitHub for keys and drain them within minutes — this is a measured, industrialised process, not a hypothetical.

For real value:
- **Hardware wallets** for signing. The key never leaves the device
- **A multisig with independent signers** for treasuries and admin roles
- **A dedicated deployer key** with no ongoing privileges — deploy, then transfer ownership to the multisig
- **Foundry keystores** (`cast wallet import`) rather than raw private keys in environment variables
- **Different keys for testnet and mainnet.** Testnet keys leak constantly, and reuse is how a "harmless" leak becomes a real one

## Signature verification — the four checks

Off-chain signatures (EIP-712 permits, meta-transactions, allowlists) need all four, and each has caused real losses:

1. **Replay protection** — a nonce or a used-signature mapping. Otherwise the same signature is reusable forever
2. **Domain separation** — EIP-712's domain includes `chainId` and `verifyingContract`, so a signature for one contract on one chain isn't valid elsewhere. **Omitting `chainId` means every signature is replayable on every fork**
3. **Signature malleability** — ECDSA signatures come in pairs `(r, s)` and `(r, -s)`, both valid. If you key a "used" mapping on the signature bytes, the malleated form bypasses it. **Use OpenZeppelin's `ECDSA` library**, which rejects the high-`s` form
4. **The zero-address check** — `ecrecover` returns `address(0)` on malformed input. **`require(signer == expected)` where `expected` is uninitialised passes.** OpenZeppelin's wrapper reverts instead

**Use `ECDSA.recover` and `EIP712`, don't call `ecrecover` directly.** All four of these are handled for you.

## Key insight

**Access control failures are boring, common, and account for most of the money lost.** The discipline that prevents them is unglamorous: use `Ownable2Step` or `AccessControl`, put a timelock on every privileged action, count *independent* multisig signers rather than keys, disable initialisers on implementations, and never let one key do everything. None of that is clever, and all of it outperforms cleverness.

## Related
- [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]] — where the initialiser trap lives
- [[web3/04-smart-contract-security/08-case-studies|case studies]] — Ronin, Parity
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures]]
- [[cybersecurity/04-web-security/02-secure-authentication|authentication]] — the ordinary version

*Source: [reference] — Aug 2026.*
