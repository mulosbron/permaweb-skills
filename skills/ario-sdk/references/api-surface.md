# ARIO client API surface

Source docs: 105 (General), 27 (Gateways), 129 (Vaults), 153 (Epochs), 89 (Pagination), 3 (Logging), 104 (Token Conversion), 151 (Networks), 173, 22.

`W` = needs `signer` + `rpcSubscriptions`. Writes accept optional `{ tags }` and return `{ id }`.

## Protocol info and tokens

| Method | Notes |
|---|---|
| `getInfo()` | `{ Name, Ticker, Denomination: 6, totalSupply, protocolBalance, epochSettings: { durationMs: 86400000, prescribedNameCount: 25, maxObservers: 50 } }` |
| `getTokenSupply()` | `{ total, circulating, locked, withdrawn, delegated, staked, protocolBalance }` in mARIO |
| `getBalance({ address })` | mARIO number |
| `getBalances({ cursor, limit, sortBy: 'balance', sortOrder })` | paginated |
| `transfer({ target, qty })` W | `target` is a base58 Solana pubkey |

## Vaults (time-locked ARIO)

| Method | Notes |
|---|---|
| `getVault({ address, vaultId })`, `getVaults({ cursor, limit, sortBy, sortOrder })` | `{ balance, startTimestamp, endTimestamp }` |
| `createVault({ lockLengthMs, quantity })` W | lock own balance |
| `extendVault({ vaultId, extendLengthMs })` W | |
| `increaseVault({ vaultId, quantity })` W | |
| `vaultedTransfer({ recipient, quantity, lockLengthMs, revokable })` W | send locked |
| `revokeVault({ recipient, vaultId })` W | sender only, if revokable |

## Gateways

| Method | Notes |
|---|---|
| `getGateway({ address })` | one gateway |
| `getGateways({ limit, sortBy, sortOrder, cursor })` | sort by any key: `operatorStake`, `start`, `status`, `settings.fqdn`, `stats.failedConsecutiveEpochs`, ... Items include `settings`, `stats`, `weights`, `status: 'joined'` |
| `getGatewayDelegates({ address, ... })`, `getAllDelegates(...)`, `getAllowedDelegates({ address })` | |
| `joinNetwork({ qty, allowDelegatedStaking, minDelegatedStake, delegateRewardShareRatio, label (1-64), note (≤256), properties, observerWallet, fqdn, port: 443, protocol: 'https' })` W | `observerWallet` must equal the gateway's `OBSERVER_WALLET` |
| `leaveNetwork()` W | stakes vaulted, returned after leave period |
| `updateGatewaySettings({ ... })` W | e.g. `minDelegatedStake` |
| `SolanaARIOWriteable.updateOperationsAddress({ operationsAddress })` | operator only; pass own address to revoke |
| `SolanaARIOWriteable.updateGatewayMetadata({ gatewayAddress, fqdn, port, label, protocol, properties, note })` | operator or operations address; gateway schema >= 1.2.0 |
| `getUnmigratedGatewayAddresses()`, `migrateGateways({ gatewayAddresses?, batchSize? })` | permissionless schema migration; signer pays small rent |

## Staking

| Method | Notes |
|---|---|
| `increaseOperatorStake({ qty })` / `decreaseOperatorStake({ qty })` W | operator wallet |
| `increaseDelegateStake({ target, qty })` W | |
| `decreaseDelegateStake({ target, qty, instant? })` W | `instant: true` pays early-withdrawal fee |
| `getDelegations({ address, cursor, limit, sortBy, sortOrder })` | items typed `stake` or `vault` |
| `getWithdrawals({ address })` | pending; claimable when `Date.now() >= endTimestamp`; `claimWithdrawal({ withdrawalId: item.vaultId })` |
| `instantWithdrawal({ gatewayAddress?, vaultId })` W | |
| `cancelWithdrawal({ gatewayAddress?, vaultId })` W | back into stake |
| `redelegateStake({ target, source, stakeQty, vaultId? })` W | fee 0–60% |
| `getRedelegationFee({ address })` | `{ redelegationFeeRate, feeResetTimestamp }` |
| `getGatewayVaults({ address })`, `getAllGatewayVaults(...)` | |

## Epochs and observation

| Method | Notes |
|---|---|
| `getCurrentEpoch()`, `getEpoch({ epochIndex })` | observations, `prescribedNames`, `prescribedObservers` with weights, distributions, `arnsStats` |
| `getPrescribedObservers({ epochIndex })` | |
| `getObservations({ epochIndex? })` | `{ failureSummaries, reports }` |
| `getDistributions({ epochIndex? })`, `getEligibleEpochRewards({ epochIndex })` | |
| `saveObservations({ reportTxId, failedGateways })` W | observer only |
| `crankEpochStep(opts?)` W | returns `{ action, epochIndex?, txId?, progress? }`; actions `create, tally, prescribe, distribute, close, close_observation, compound, update_demand_factor, prune_returned_names, idle` |
| `SolanaARIOWriteable.transferEpochSettingsAuthority({ newAuthority })` | admin |

## ArNS registry (see arns skill for ANT side)

`getArNSRecord({ name })` → `{ processId (ANT asset), type, ... }`; `getArNSRecords({ filters, cursor, limit })`; `buyRecord({ name, years, ... })` W; `upgradeRecord` W; primary-name methods.
