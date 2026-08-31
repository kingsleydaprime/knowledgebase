# JavaScript / TypeScript for Web3

**The client layer** — frontends, indexers, bots, scripts. Almost everything that isn't a contract.

**Use TypeScript.** viem's type inference from ABIs is a genuine safety feature in a domain where a wrong argument type costs money.

## viem — the default

```bash
npm i viem
```

```ts
import { createPublicClient, createWalletClient, http, custom, parseUnits, formatUnits } from 'viem'
import { mainnet, base } from 'viem/chains'

const publicClient = createPublicClient({ chain: base, transport: http(RPC_URL) })

// READ — free, instant
const balance = await publicClient.readContract({
  address: TOKEN, abi: erc20Abi, functionName: 'balanceOf', args: [user],
})

// SIMULATE then WRITE — catches most reverts before the user pays
const { request } = await publicClient.simulateContract({
  address: TOKEN, abi: erc20Abi, functionName: 'transfer',
  args: [to, parseUnits('1.5', 18)], account,
})
const hash = await walletClient.writeContract(request)
const receipt = await publicClient.waitForTransactionReceipt({ hash, confirmations: 2 })
if (receipt.status === 'reverted') { /* mined AND failed — the user still paid */ }
```

**Batch reads with multicall.** The biggest frontend performance win available:

```ts
const [balance, decimals, symbol] = await publicClient.multicall({
  contracts: [
    { address: TOKEN, abi: erc20Abi, functionName: 'balanceOf', args: [user] },
    { address: TOKEN, abi: erc20Abi, functionName: 'decimals' },
    { address: TOKEN, abi: erc20Abi, functionName: 'symbol' },
  ],
  allowFailure: false,
})
```

**Type the ABI with `as const`** — that's what gives you inferred argument and return types:

```ts
const abi = [...] as const     // without this you get `any` everywhere
```

## wagmi — React hooks

```bash
npm i wagmi viem @tanstack/react-query
```

```tsx
import { useAccount, useConnect, useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi'

function Transfer() {
  const { address, chain } = useAccount()
  const { data: balance } = useReadContract({
    address: TOKEN, abi, functionName: 'balanceOf', args: [address!],
    query: { enabled: !!address },
  })

  const { writeContract, data: hash, isPending } = useWriteContract()
  const { isLoading, isSuccess } = useWaitForTransactionReceipt({ hash })

  return <button
    disabled={isPending || isLoading}
    onClick={() => writeContract({ address: TOKEN, abi, functionName: 'transfer', args: [to, amount] })}
  >{isPending ? 'Confirm in wallet…' : isLoading ? 'Pending…' : 'Send'}</button>
}
```

**wagmi ships TanStack Query**, so caching, refetching and loading states are handled. Set staleness per data type — `decimals` never changes, balances change per block.

**RainbowKit or ConnectKit** on top gives you a wallet connection modal with EIP-6963 multi-wallet discovery handled → [[web3/06-building-dapps/02-wallets-and-connection|wallets and connection]].

## The non-negotiables

**1. `bigint`, never `number`.** JavaScript numbers lose precision above 2⁵³; token amounts routinely exceed it.

```ts
parseUnits('1.5', 18)      // '1.5' → 1500000000000000000n
formatUnits(raw, 18)       // back to a display string
```

**Never `Number(balance)`. Never floats for amounts.** Format only at the render boundary.

**2. Check the chain before every write.** A user on the wrong network silently interacts with a different contract at the same address.

**3. Model all the transaction states** — rejected, pending, mined-and-reverted, dropped, replaced, reorged. **"Mined and reverted" is the one everyone forgets** → [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading and writing]].

**4. Have an RPC fallback.** viem's `fallback()` transport rotates providers.

```ts
transport: fallback([http(ALCHEMY), http(QUICKNODE), http(PUBLIC)])
```

**5. Never put a private key in frontend code.** For backend signers, use a KMS or a keystore.

## Indexing

**Ponder** — TypeScript, Postgres, hot reload, handles reorgs. The best DX for custom indexing:

```ts
ponder.on('ERC20:Transfer', async ({ event, context }) => {
  await context.db.insert(transfers).values({ id: event.log.id, ...event.args })
})
```

**The Graph** for hosted subgraphs; **Alchemy/Moralis APIs** when a prebuilt endpoint fits — don't build an indexer for "NFTs owned by X" → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## The ecosystem

| | |
|---|---|
| **viem** | The default client. Type-safe, tree-shakeable, well-documented |
| **ethers.js v6** | Mature, widely used, larger. Fine — most tutorials use it |
| **web3.js** | **Deprecated.** Don't start here |
| **wagmi** | React hooks over viem |
| **RainbowKit / ConnectKit** | Connection UI |
| **Ponder** | TypeScript indexer |
| **Hardhat** | Contract development in TS |
| **Safe SDK** | Multisig integration |
| **permissionless.js** | ERC-4337 account abstraction → [[web3/06-building-dapps/07-account-abstraction|AA]] |

**viem + wagmi is the current default.** ethers is the mature alternative and the one most existing code uses; migrating isn't urgent.

## Related
- [[web3/06-building-dapps/README|building dapps]] — the architecture this implements
- [[frontend/README|frontend]] — the other 90% of a dapp
- [[web3/frameworks/README|web3 frameworks]]
