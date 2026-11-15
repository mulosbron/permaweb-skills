# ANTs and records (ar.io SDK)

Source docs: 102 (Initialize), 130 (Spawn), 131 (Records), 132 (Metadata), 133 (Controllers), 143 (Transfer), 144 (Upgrade), 13 (Versions), 154 (State), 175 (Balances), 14 (Undername Ownership), 120 (ANTs), 128 (Primary Names), 148, 226.

## Init

```ts
import { ANT } from '@ar.io/sdk';
import { createSolanaRpc, createSolanaRpcSubscriptions } from '@solana/kit';
const rpc = createSolanaRpc('https://api.mainnet-beta.solana.com');
const ant = await ANT.init({ processId: '<MPL Core asset pubkey>', rpc });                    // read-only
const antW = await ANT.init({ processId, rpc,
  rpcSubscriptions: createSolanaRpcSubscriptions('wss://api.mainnet-beta.solana.com'), signer }); // read + write
```

Every write method takes an optional second arg `{ tags: [{ name, value }] }` and returns `{ id }`.

## Create

```ts
const { processId, mint, signature } = await ANT.spawn({ rpc, rpcSubscriptions, signer, state: {
  name: 'My ANT', ticker: 'MYANT', description, keywords, logo /* tx id */,
  uri: 'ar://<metadata tx id>',           // Metaplex JSON; build with buildAntMetadata, upload via Turbo
  transactionId,                          // initial @ target
}});
```

CLI: `ar.io spawn-ant --wallet-file wallet.json --name ... --ticker ... --metadata-uri ar://...`.

## Read

| Method | Returns |
|---|---|
| `getInfo()`, `getState()` | name, ticker, owner, controllers, records, balances, logo |
| `getOwner()`, `getName()`, `getTicker()`, `getLogo()`, `getControllers()` | single fields (ANT name ≠ ArNS name) |
| `getRecords()` | `{ '@': { transactionId, ttlSeconds, targetProtocol, index }, sub: {...} }` |
| `getRecord({ undername })` | one record incl. `owner`, `displayName`, `logo`, `description`, `keywords` |
| `getBalances()`, `getBalance({ address })` | 1 for the owner |
| `getModuleId()`, `getVersion()`, `isLatestVersion()` | version info |

## Write

| Method | Who |
|---|---|
| `setBaseNameRecord({ transactionId, ttlSeconds, owner?, displayName?, logo?, description?, keywords? })` | owner, controller |
| `setUndernameRecord({ undername, transactionId, ttlSeconds, owner?, ...meta })` | owner, controller, that record's owner |
| `setRecord({ undername: '@' \| name, transactionId, ttlSeconds })` | owner, controller |
| `removeUndernameRecord({ undername })`, `removeRecord({ undername })` | owner, controller |
| `transferRecord({ undername, recipient })` | record owner, ANT owner, controller |
| `setName`, `setTicker`, `setDescription`, `setKeywords`, `setLogo({ txId })` | owner, controller |
| `addController({ controller })`, `removeController({ controller })` | owner only |
| `transfer({ target: <Solana address> })` | owner only (standard Metaplex Core transfer) |
| `upgrade()` → `{ id, needsMigration }` | migrate on-chain schema |

CLI equivalents exist (`ar.io transfer-record --process-id ... --undername ... --recipient ... --wallet-file ...`).

## Permission matrix

| Action | ANT owner | Controller | Undername owner | Any ARIO holder |
|---|---|---|---|---|
| Transfer ANT | ✔ | | | |
| Add/remove controllers | ✔ | | | |
| Approve/remove primary name | ✔ | | ✔ | |
| Reassign name to new ANT | ✔ | | | |
| Return a permanent name | ✔ | | | |
| Set records (pointer + metadata) | ✔ | ✔ | ✔ (own record) | |
| Update records, name, ticker, description, keywords | ✔ | ✔ | | |
| Create/assign undernames | ✔ | ✔ | | |
| Extend lease, increase undernames, convert to permabuy | ✔ | ✔ | ✔ | ✔ |

Undername owners control their record's tx id, TTL, owner, description, display name, keywords, logo; not its priority.

## Primary names (on the ARIO client)

```ts
const ario = ARIO.init({ rpc, rpcSubscriptions, signer });
await ario.setPrimaryName({ name: 'my-arns-name' });       // signer must own the ANT behind the name
await ario.requestPrimaryName({ name: 'arns' });            // request; approved by the name's owner
await ario.getPrimaryName({ address }) / ({ name });        // { name, owner, processId, startTimestamp }
await ario.getPrimaryNames({ cursor, limit, sortBy, sortOrder });
await ario.getPrimaryNameRequest({ initiator });
```

## Marketplace

ANTs trade on Tensor and Magic Eden or by direct Solana transfer. Lazy reconciliation clears previous controllers on the next write after an outside sale. Records may point to Arweave tx ids (or IPFS CIDs per the marketplace page).
