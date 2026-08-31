# Reading and Writing Chain State

**[Intermediate]** — the JSON-RPC surface, the transaction states a UI must model, and the mistakes that make dapps feel broken.

## The RPC methods that matter

Everything a client does reduces to a handful of JSON-RPC calls:

```
eth_call                  simulate a call. FREE. All reads go through this
eth_estimateGas           simulate and report gas used
eth_sendRawTransaction    submit a signed transaction
eth_getTransactionReceipt poll for the outcome
eth_getLogs               query historical events (heavily rate-limited)
eth_getBalance            native token balance
eth_blockNumber           current head
eth_getStorageAt          read ANY storage slot — including `private` ones
```

**`eth_call` is the workhorse.** Every `balanceOf`, every `view` function, every price check is a simulation against current state that never touches the network's consensus. Free, instant, and unlimited.

**`eth_getStorageAt` is the reminder that `private` isn't private** → [[web3/03-smart-contracts-with-solidity/04-functions-modifiers-visibility|visibility]].

## Reading, in practice

```ts
import { createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'

const client = createPublicClient({ chain: mainnet, transport: http(RPC_URL) })

const balance = await client.readContract({
  address: TOKEN, abi: erc20Abi, functionName: 'balanceOf', args: [user],
})
```

**Batch reads with multicall.** Twenty separate `eth_call`s is twenty round trips; **Multicall3 is deployed at the same address on every major chain** and batches them into one:

```ts
const results = await client.multicall({
  contracts: [
    { address: TOKEN, abi, functionName: 'balanceOf', args: [user] },
    { address: TOKEN, abi, functionName: 'decimals' },
    { address: TOKEN, abi, functionName: 'symbol' },
  ],
})
```

**This is the single biggest performance win available to a dapp frontend.** A dashboard doing 50 individual reads feels broken; the same 50 in one multicall feels instant.

**Cache aggressively.** `decimals`, `symbol` and `name` never change — fetch once. Balances change per block. Use TanStack Query (wagmi ships with it) and set staleness per data type rather than refetching everything on an interval.

## Writing, and the states you must model

```ts
const { writeContractAsync } = useWriteContract()

const hash = await writeContractAsync({ address, abi, functionName: 'transfer', args: [to, amount] })
const receipt = await publicClient.waitForTransactionReceipt({ hash, confirmations: 2 })

if (receipt.status === 'reverted') {
  // MINED AND FAILED. The user paid gas. This is not an error you can retry blindly
}
```

**The full state machine — a UI that models fewer than these is wrong:**

```
idle
  → awaiting signature       (wallet open; user may reject — normal, not an error)
  → rejected                 (terminal, no cost)
  → pending                  (broadcast; may take seconds or MINUTES)
  → mined + success          (still reorg-able for a short window)
  → mined + REVERTED         (failed, and the user paid)
  → dropped                  (fell out of the mempool; underpriced)
  → replaced                 (user sped it up or cancelled in their wallet)
```

**"Mined and reverted" is the one people forget.** The transaction succeeded at the network level and failed at the application level, and the user was charged. Showing "success" on receipt without checking `status` is a common and confusing bug.

## Simulate before you send

```ts
const { request } = await publicClient.simulateContract({
  address, abi, functionName: 'transfer', args: [to, amount], account,
})
await walletClient.writeContract(request)     // only reached if the simulation passed
```

**Simulation catches most reverts before the user pays.** It runs `eth_call` against current state with the user's address as sender, and surfaces the revert reason as a readable error. wagmi's `useSimulateContract` does this and it should be your default — **letting a user pay gas to discover their transaction was always going to fail is poor and avoidable.**

The caveat: state can change between simulation and inclusion, so a passing simulation isn't a guarantee. It catches the deterministic failures, which is most of them.

## Decoding errors

Reverts come back as ABI-encoded error data, not strings:

```ts
try {
  await publicClient.simulateContract({ ... })
} catch (err) {
  if (err instanceof BaseError) {
    const revert = err.walk(e => e instanceof ContractFunctionRevertedError)
    // revert.data.errorName === 'InsufficientBalance'
    // revert.data.args     === [requested, available]
  }
}
```

**Custom errors give you typed, structured failures** — you can map `InsufficientBalance(1000, 500)` to a real message showing both numbers. This is a concrete argument for custom errors over string reverts → [[web3/03-smart-contracts-with-solidity/02-solidity-fundamentals|errors]].

## Watching for changes

```ts
const unwatch = client.watchContractEvent({
  address, abi, eventName: 'Transfer',
  onLogs: logs => { /* ... */ },
})
```

Over a WebSocket transport this is a real push subscription; over HTTP viem polls. **Neither is a substitute for an indexer** — subscriptions give you *new* events, not history → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

**And handle `log.removed === true`**, which means that log was reorged away.

## Common mistakes

- **Polling `eth_getLogs` over a wide range.** Providers cap it and it's slow. Use an indexer
- **Not handling reverts on mined transactions**
- **Assuming one confirmation is final** → [[web3/02-ethereum-and-the-evm/04-transactions-and-the-mempool|finality]]
- **Ignoring the chain ID** — silently interacting with the wrong network
- **Using floats for token amounts.** Use `bigint` and viem's `parseUnits`/`formatUnits`. **JavaScript numbers lose precision above 2⁵³**, and token amounts are routinely larger
- **One RPC provider, no fallback.** Providers go down and take your app with them

## Key insight

**Reads are free simulations against current state; writes are money-costing, minutes-long operations that can fail after you've already paid.** Almost every dapp that feels broken is one that modelled the write path as a normal async request — with a spinner and a success toast — instead of as a state machine with seven outcomes, two of which cost the user money.

## Related
- [[web3/06-building-dapps/04-indexing-and-events|indexing and events]] — for anything historical
- [[web3/06-building-dapps/01-the-dapp-architecture|the dapp architecture]]
- [[web3/frameworks/javascript/README|JS/TS for web3]] — viem and wagmi in full
- [[web3/01-foundations/06-networking-and-nodes|nodes and RPC]]
