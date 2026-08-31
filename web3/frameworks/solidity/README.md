# Solidity Toolchain

**The language is covered in [[web3/03-smart-contracts-with-solidity/README|section 03]].** This is the tooling around it.

## Foundry — the default

Rust-based, fast, and tests are written in Solidity.

```bash
curl -L https://foundry.paradigm.xyz | bash && foundryup

forge init my-project
forge build
forge test -vvv                 # -vvv gives traces on failures
forge test --gas-report
forge coverage
forge fmt
forge snapshot --diff           # gas regressions — put this in CI
```

**The four binaries:**

- **`forge`** — build, test, deploy, script
- **`cast`** — CLI chain interaction: `cast call`, `cast send`, `cast storage`, `cast 4byte`, `cast wallet`
- **`anvil`** — local node. **`anvil --fork-url $RPC`** forks mainnet locally, which is the single most useful development feature here
- **`chisel`** — a Solidity REPL

`foundry.toml`:

```toml
[profile.default]
solc_version = "0.8.24"
optimizer = true
optimizer_runs = 200
via_ir = true
fs_permissions = [{ access = "read", path = "./deployments" }]

[rpc_endpoints]
mainnet = "${MAINNET_RPC_URL}"
base = "${BASE_RPC_URL}"
```

**Deployment scripts are Solidity**, which keeps one language across the project:

```solidity
contract Deploy is Script {
    function run() external {
        vm.startBroadcast();
        new MyContract(msg.sender);
        vm.stopBroadcast();
    }
}
```

```bash
forge script script/Deploy.s.sol --rpc-url base --broadcast --verify
```

**Use a keystore, not a raw key in an env var:**
```bash
cast wallet import deployer --interactive     # then --account deployer
```

## Hardhat — the JS/TS alternative

Choose it when your deployment pipeline is already TypeScript, or you need its plugin ecosystem (notably the OpenZeppelin upgrades plugin, which validates storage layouts across upgrades).

```bash
npx hardhat test
npx hardhat node
npx hardhat ignition deploy ./ignition/modules/MyContract.ts
```

**The two coexist happily in one repo** — Foundry for tests, Hardhat for deployment — and that's a common setup.

## OpenZeppelin — the de facto standard library

```bash
forge install OpenZeppelin/openzeppelin-contracts
```

```solidity
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuardTransient} from "@openzeppelin/contracts/utils/ReentrancyGuardTransient.sol";
```

**Use it rather than reimplementing primitives** → [[web3/03-smart-contracts-with-solidity/06-inheritance-and-libraries|inheritance and libraries]]. Two notes: **v5 has breaking changes** from v4 (`Ownable` takes an explicit owner; `_beforeTokenTransfer` became `_update`), and **use `contracts-upgradeable` for proxies**.

**Solady** is the gas-optimised alternative — assembly-heavy, less readable, meaningfully cheaper. Reasonable when gas dominates.

## Security tooling

```bash
pip install slither-analyzer && slither .      # run this in CI
cargo install aderyn && aderyn .
```

Beyond static analysis: **Echidna** and Foundry's built-in invariant testing for fuzzing; **Halmos** and **Certora** for formal verification; **Tenderly** for simulating and debugging live transactions → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]].

## Vyper — the alternative EVM language

Python-like, deliberately restricted (no inheritance, no modifiers, no inline assembly, bounded loops) on the principle that **auditability beats expressiveness.** Used by Curve and parts of the Ethereum ecosystem.

**The 2023 Curve exploit was a Vyper compiler bug** in the reentrancy guard, which is a genuine argument against the smaller ecosystem: fewer users means fewer eyes on the compiler → [[web3/04-smart-contract-security/08-case-studies|case studies]].

## A workable setup

```
forge init                          Foundry as the base
forge install OpenZeppelin/openzeppelin-contracts
slither in CI                       static analysis on every PR
forge snapshot --diff in CI         gas regressions surface at review
anvil --fork-url                    develop against real mainnet state
Etherscan verification              on every deployment, always
```

## Related
- [[web3/03-smart-contracts-with-solidity/README|smart contracts with Solidity]] — the language
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]] — the techniques
- [[web3/frameworks/README|web3 frameworks]]
