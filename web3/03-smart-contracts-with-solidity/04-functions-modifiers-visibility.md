# Functions, Modifiers and Visibility

**[Intermediate]** — the dispatch mechanism, what modifiers really compile to, and the fallback functions that catch what you didn't expect.

## Dispatch: the function selector

There is no method table. A call is **four bytes plus arguments**:

```
selector = first 4 bytes of keccak256("transfer(address,uint256)")
         = 0xa9059cbb

calldata = 0xa9059cbb
           000...0071C7656EC7ab88b098defB751B7401B5f6d8976F   ← address, padded to 32 bytes
           000...00000000000000000000000000000000000000000064 ← uint256 100
```

The compiler generates a dispatcher: compare the first four bytes against each function's selector, jump to the match, else fall through to the fallback.

Three things follow:

- **The signature string is canonical.** `uint` must be written `uint256`, no spaces, no parameter names. Get it wrong and you compute a selector for a function that doesn't exist
- **Four bytes is small enough to collide.** Different functions *can* share a selector; the compiler rejects it within one contract, but **a proxy and its implementation can collide across the boundary** — which is what the [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|transparent proxy]] pattern exists to handle
- **Argument types are not verified at runtime.** The EVM decodes bytes according to what your signature *claims*. Mismatched ABI = silently wrong values, not an error

## Visibility, precisely

| | Callable by | Notes |
|---|---|---|
| `external` | Outside only | Args can be `calldata` → **cheapest for large parameters** |
| `public` | Anywhere | Generates a getter for state variables |
| `internal` | This contract + inheritors | The default for state variables |
| `private` | This contract only | **Not inherited, and NOT confidential** |

**`private` means "not visible to other Solidity code."** The value is in a storage slot that anyone reads with `eth_getStorageAt`, and the bytecode is public. There is no privacy modifier, because there is no privacy → [[web3/03-smart-contracts-with-solidity/01-what-a-smart-contract-is|what a smart contract is]].

**Forgetting a visibility specifier used to default to `public`** — that is exactly how the first Parity multisig lost ~$31M in July 2017, via an unprotected initialiser. Solidity 0.5 made the specifier mandatory, which is a good example of a language change driven by a nine-figure loss.

## Modifiers are textual inlining

```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "not owner");
    _;                              // ← the function body goes HERE
    // code after `_` runs AFTER the body
}
```

The compiler substitutes the body at `_`. Two consequences people miss:

**Code after `_;` runs after the function**, which is how the reentrancy guard works:

```solidity
modifier nonReentrant() {
    require(_status != ENTERED, "reentrant");
    _status = ENTERED;
    _;
    _status = NOT_ENTERED;          // runs on the way out
}
```

**Modifiers duplicate their code into every function that uses them**, growing bytecode. On a contract near the 24KB deployment limit (EIP-170), converting modifiers to internal function calls is a standard size fix — `_checkOwner()` instead of inlining the check five times.

**Modifier order is execution order**, left to right. `function f() external onlyOwner nonReentrant whenNotPaused` runs the ownership check first. Where one modifier's precondition depends on another's effect, the order is load-bearing.

## `receive` and `fallback`

```solidity
receive() external payable { }             // plain ETH transfer, empty calldata
fallback() external payable { }            // unmatched selector, or ETH with no `receive`
```

Dispatch logic:

```
calldata empty?
   ├─ yes → receive() if it exists, else fallback() if payable, else REVERT
   └─ no  → matching selector? → that function
                              └─ no match → fallback(), else REVERT
```

**A contract with neither cannot receive plain ETH** — `send`/`transfer`/`call` with value will revert. That's usually what you want; accidental ETH acceptance is a real source of stuck funds.

**`fallback` is how proxies work.** Every unmatched call falls through and gets `DELEGATECALL`ed to the implementation. That is the entire mechanism.

**But ETH can still arrive uninvited**, via `SELFDESTRUCT` (in the same transaction as creation, post-EIP-6780) or by being the recipient of block rewards. So **`address(this).balance` can increase without any of your code running** — which is why invariants of the form `require(address(this).balance == expectedTotal)` are breakable, and have been broken deliberately to grief contracts.

## Sending ETH — the current correct answer

```solidity
(bool ok, ) = recipient.call{value: amount}("");
require(ok, "send failed");
```

**Not `.transfer()` and not `.send()`.** Both forward a fixed 2300-gas stipend, which was intended as reentrancy protection and instead became a compatibility bug: smart-contract wallets and multisigs commonly need more than 2300 gas in their `receive`, so `.transfer()` reverts on them. Worse, gas costs are repriced in most network upgrades, so any hardcoded stipend has a shelf life.

**Use `.call` with a [[web3/04-smart-contract-security/02-reentrancy|reentrancy guard]] and Checks-Effects-Interactions**, which is the protection that actually works. Any tutorial still recommending `.transfer()` predates 2019.

## Function types and callbacks

Solidity has function pointers (`function(uint) external returns (bool)`), rarely used directly. What you meet in practice is the **callback interface** pattern — `onERC721Received`, flash-loan callbacks, Uniswap V3's `uniswapV3SwapCallback`.

**Every callback is an entry point into your contract from a third party, mid-execution.** They must be access-controlled like any other public function — "only the pool may call this" — and forgetting that is a recurring exploit in flash-loan integrations.

## Key insight

**A function call is four bytes matched against a jump table, with no type checking and no method resolution.** Selectors can collide, arguments are decoded on trust, `private` is a compiler fiction, and any unmatched call lands in your fallback. Treat the ABI as a wire protocol you're implementing rather than a language feature you're using.

## Related
- [[web3/03-smart-contracts-with-solidity/06-inheritance-and-libraries|inheritance and libraries]]
- [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]]
- [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]] — built entirely on `fallback` + `DELEGATECALL`
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]]

*Source: [reference] — Aug 2026.*
