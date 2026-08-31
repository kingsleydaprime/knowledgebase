# Python for Web3

**Scripting, analysis, security tooling and research** — not the frontend, and rarely production contracts.

**Python's real strength here is the security and analysis ecosystem**, which is the best of any language.

## web3.py

```bash
pip install web3
```

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(RPC_URL))

balance = w3.eth.get_balance(addr)                      # wei, as int
print(Web3.from_wei(balance, 'ether'))

token = w3.eth.contract(address=TOKEN, abi=ERC20_ABI)
bal = token.functions.balanceOf(addr).call()            # free read

# a write
tx = token.functions.transfer(to, amount).build_transaction({
    'from': acct.address,
    'nonce': w3.eth.get_transaction_count(acct.address),
    'maxFeePerGas': w3.eth.gas_price * 2,
    'maxPriorityFeePerGas': w3.to_wei(1, 'gwei'),
})
signed = acct.sign_transaction(tx)
h = w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(h)
assert receipt.status == 1, "mined but reverted"
```

**Python integers are arbitrary precision**, so unlike JavaScript there's no `bigint` ceremony — token amounts just work. That's a genuine ergonomic advantage for analysis work.

**Manage nonces yourself** for any script sending multiple transactions. `get_transaction_count(addr, 'pending')` per send is a race → [[web3/02-ethereum-and-the-evm/04-transactions-and-the-mempool|the three nonce bugs]].

## The security ecosystem — the real reason to use Python here

**Slither** — the standard static analyser, and it's excellent:

```bash
pip install slither-analyzer
slither .
slither . --print human-summary
slither . --print inheritance-graph
```

**Run it in CI.** It catches reentrancy, uninitialised storage, unchecked returns and shadowed variables essentially for free → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing]].

The rest of the Trail of Bits toolkit is also Python:

- **Echidna** — property-based fuzzing (Haskell, Python tooling)
- **Manticore** — symbolic execution
- **Crytic-compile** — the compilation layer underneath Slither
- **Panoramix** — decompile EVM bytecode when there's no verified source

**Halmos** (a16z) — symbolic testing that runs your Foundry tests over *all* inputs rather than samples.

## Vyper

Python-like, deliberately restricted — no inheritance, no modifiers, no inline assembly, bounded loops — on the principle that **auditability beats expressiveness**:

```python
# @version ^0.4.0

balances: public(HashMap[address, uint256])

@external
def transfer(to: address, amount: uint256) -> bool:
    assert self.balances[msg.sender] >= amount, "insufficient"
    self.balances[msg.sender] -= amount
    self.balances[to] += amount
    return True
```

Used by Curve and parts of the Ethereum ecosystem. **The 2023 Curve exploit was a Vyper compiler bug**, which is the honest counter-argument: a smaller ecosystem means fewer eyes on the compiler → [[web3/04-smart-contract-security/08-case-studies|case studies]].

## Analysis and research

Where Python is genuinely the best tool available:

```python
import pandas as pd
# pull logs, load into a DataFrame, analyse
logs = token.events.Transfer().get_logs(from_block=n, to_block=n + 5000)
df = pd.DataFrame([dict(l['args'], block=l['blockNumber']) for l in logs])
```

**Dune Analytics** (SQL over decoded chain data) is usually better than doing this yourself for anything standard. Python wins when you need custom logic, simulation, or to combine chain data with anything else → [[ai-ml/README|the data stack]].

**Note the `eth_getLogs` range limits** — providers cap them, so wide historical queries need an indexer or an archive node → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## Frameworks

- **Ape (ApeWorX)** — the modern Python contract framework: testing, deployment, plugins. The Python answer to Foundry
- **Brownie** — the predecessor, **deprecated**. Don't start here
- **Titanoboa** — a fast Vyper interpreter for testing

**For contract development, use Foundry.** Python's place in this domain is tooling, analysis and security work — where it's clearly the best option — rather than the contract build pipeline.

## Related
- [[languages/06-python/README|Python]] — the language
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]] — where Slither fits
- [[web3/frameworks/README|web3 frameworks]]
- [[cybersecurity/02-ethical-hacking/README|ethical hacking]] — the adjacent tooling mindset
