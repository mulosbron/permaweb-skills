---
name: ario-sdk
description: "Use when writing code against the ar.io protocol with @ar.io/sdk on Solana: ARIO.init with @solana/kit, reading the gateway registry, balances, token supply, epochs and observations, ARIO transfers, vaults, delegated staking and withdrawals, redelegation, cranking epochs, program IDs, devnet/testnet config, mARIO conversion, pagination and filters. ANT/record work is in the arns skill."
metadata:
  category: permaweb
  triggers: "@ar.io/sdk, ARIO.init, ario token, mARIO, delegate stake, gateway registry, getGateways, ario epoch, solana ario"
---

# ar.io SDK (`@ar.io/sdk`)

TypeScript client for the ar.io protocol programs on **Solana** (default backend since v3.23). Two classes: `ARIO` (network: gateways, staking, tokens, epochs, ArNS registry, primary names) and `ANT` (one name token; see `../arns/SKILL.md`).

## Init

```ts
import { ARIO } from '@ar.io/sdk';                     // '@ar.io/sdk/node' or '/web' subpaths also exist
import { createSolanaRpc, createSolanaRpcSubscriptions, createKeyPairSignerFromBytes } from '@solana/kit';

const rpc = createSolanaRpc('https://api.mainnet-beta.solana.com');
const ario = ARIO.init({ rpc });                                                   // read-only
const signer = await createKeyPairSignerFromBytes(secretKey64);                     // Solana keypair
const arioW = ARIO.init({ rpc, rpcSubscriptions: createSolanaRpcSubscriptions('wss://api.mainnet-beta.solana.com'), signer });
```

Devnet / localnet: point `rpc` at the cluster and pass `coreProgramId`, `garProgramId`, `arnsProgramId`, `antProgramId` (`address('<id>')`). Mainnet program ids and the token mint are in `references/token.md`.

Browsers need the usual polyfills (`vite-plugin-node-polyfills`); a CDN build exists (`https://unpkg.com/@ar.io/sdk`).

## What is where

| Area | Methods (see `references/api-surface.md`) |
|---|---|
| Info and tokens | `getInfo`, `getTokenSupply`, `getBalance`, `getBalances`, `transfer` |
| Vaults | `getVault(s)`, `createVault`, `extendVault`, `increaseVault`, `vaultedTransfer`, `revokeVault` |
| Gateways | `getGateway(s)`, `getGatewayDelegates`, `joinNetwork`, `leaveNetwork`, `updateGatewaySettings`, `updateGatewayMetadata`, `updateOperationsAddress` |
| Staking | `increase/decreaseOperatorStake`, `increase/decreaseDelegateStake`, `redelegateStake`, `getDelegations`, `getWithdrawals`, `instantWithdrawal`, `cancelWithdrawal`, `getRedelegationFee` |
| Epochs / OIP | `getCurrentEpoch`, `getEpoch`, `getPrescribedObservers`, `getObservations`, `getDistributions`, `getEligibleEpochRewards`, `saveObservations`, `crankEpochStep` |
| ArNS registry | `getArNSRecord(s)`, `buyRecord`, `upgradeRecord`, primary names |

## Rules

1. **All quantities are mARIO integers** (1 ARIO = 1,000,000 mARIO). Convert with `new ARIOToken(n).toMARIO()` and `new mARIOToken(n).toARIO()`. A bare number is treated as mARIO.
2. **Writes need `signer` and `rpcSubscriptions`.** Signers are `@solana/kit` signers; addresses are base58 Solana pubkeys (some doc examples still show 43-char Arweave-style ids).
3. **Paginate with cursors**: `{ items, nextCursor, hasMore, totalItems, sortBy, sortOrder }`; loop while `hasMore`, passing `cursor: nextCursor`. `limit` defaults to 100. `filters: { key: value | [values] }` = AND across keys, OR within an array.
4. **Solana-only operations live on `SolanaARIOWriteable`** (`updateOperationsAddress`, `updateGatewayMetadata`, `migrateGateways`, `transferEpochSettingsAuthority`).
5. **Logging is global**: `Logger.default.setLogLevel('debug')` or assign a custom `ILogger` to `Logger.default`. `ARIO.init` takes no logger.

## Things that bite

- Old examples use `ARIO.mainnet()` / `ARIO.testnet()` and AO process ids. They target the retired AO backend. Port to `ARIO.init({ rpc })`.
- `getInfo()` keeps AO-era fields (`Handlers`, `LastCreatedEpochIndex`) as placeholders; only `totalSupply`, `protocolBalance`, `epochSettings` are live.
- Minimum operator stake: the `joinNetwork` example comments 10,000 ARIO while the token page says 20,000 ARIO. Read the live value before staking.
- Delegated stake decreases go to a withdrawal vault; claim when `Date.now() >= endTimestamp`, or pay the fee with `instant: true`.
- One free redelegation every 7 epochs; each extra adds 10% fee, capped at 60%.
- `crankEpochStep()` is permissionless and does one step per call; loop it (e.g. every 60 s). It also compounds delegate rewards, rolls the Demand Factor and prunes returned names when idle.

## Fetch the docs

```bash
python tools/docslice.py 105 27 153 129 89 151
```

Live: `https://docs.ar.io/sdks/ar-io-sdk` (has a per-SDK `llm.txt`).
