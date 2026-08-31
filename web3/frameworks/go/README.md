# Go for Web3

**Infrastructure, not contracts.** Go is where the clients and the backend services are.

## go-ethereum (geth)

**The reference Ethereum execution client**, and the most-read Go codebase in the field. Historically the dominant client — which is itself a **client diversity risk**, since a consensus bug in a supermajority client could finalise an invalid chain → [[web3/01-foundations/06-networking-and-nodes|nodes]].

**Reading geth is one of the better ways to actually learn Ethereum.** `core/vm/` is the EVM implementation, and it's more readable than the Yellow Paper.

As a library:

```go
import (
    "github.com/ethereum/go-ethereum/ethclient"
    "github.com/ethereum/go-ethereum/common"
)

client, err := ethclient.Dial(rpcURL)
balance, err := client.BalanceAt(ctx, common.HexToAddress(addr), nil)
```

**`abigen` generates typed Go bindings from an ABI** — the idiomatic way to call contracts:

```bash
abigen --abi=Token.abi --pkg=token --out=token.go
```

```go
tok, _ := token.NewToken(common.HexToAddress(TOKEN), client)
bal, _ := tok.BalanceOf(&bind.CallOpts{}, addr)
```

## Cosmos SDK

**The framework for building application-specific chains**, and the main reason to learn Go for web3 beyond geth. You write modules; the SDK provides consensus (CometBFT), networking, staking and IBC → [[web3/05-beyond-ethereum/07-other-chains|Cosmos]].

```bash
ignite scaffold chain mychain
```

**If you want to build a chain rather than a contract, this is the most approachable path** — and the app-chain model is a genuinely different architecture from deploying to a shared chain.

## Where Go actually fits

- **Chain clients** — geth, Prysm (consensus), Erigon
- **Cosmos chains** and IBC relayers
- **Backend services** that talk to chains — payment processors, custody systems, exchange infrastructure
- **Indexers and data pipelines**, where throughput matters
- **Bots and monitoring**

**Go's fit is the same as everywhere else:** concurrency, deployment simplicity, and long-lived network services. Nothing web3-specific about why it's used → [[languages/02-go/README|Go]].

## Practical notes

**Use `*big.Int` for all amounts.** Go has no arbitrary-precision integer literals, so this is verbose and non-negotiable:

```go
amount := new(big.Int)
amount.SetString("1500000000000000000", 10)     // 1.5 tokens at 18 decimals
```

**Never `int64` for token amounts** — it overflows well below `uint256`.

**Manage nonces explicitly** with a mutex-guarded counter for any service sending concurrent transactions. Querying `PendingNonceAt` per send is a race that will bite under load → [[web3/02-ethereum-and-the-evm/04-transactions-and-the-mempool|nonce bugs]].

**Handle reorgs** in anything indexing. Track block hashes; a mismatched parent means unwind → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## Related
- [[languages/02-go/README|Go]] — the language
- [[web3/01-foundations/06-networking-and-nodes|nodes and clients]]
- [[web3/05-beyond-ethereum/07-other-chains|other chains]] — Cosmos
- [[web3/frameworks/README|web3 frameworks]]
