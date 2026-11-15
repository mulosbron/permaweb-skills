# Gateway registry and OIP

Source docs: 84 (OIP), 118 (Gateway Registry), 121 (Distributions), 122 (Reporting), 123 (Observer Selection), 124 (Performance), 125 (Architecture), 113.

## Gateway Address Registry (GAR)

- Solana state in `ario-gar`. Max 3,000 gateways; 20,000 ARIO minimum join stake; up to 10,000 delegated stakers per gateway; operators need SOL for fees.
- States: **joined → leaving → gone**. Leaving: no new rewards, ≥ 90-day window for delegates to withdraw. Gone: entry closed permissionlessly, slot freed, must re-register.
- Sustained deficiency → pruning; minimum join stake slashed to protocol balance, excess and delegated stake follow normal withdrawal.
- Operations address (gateway schema ≥ 1.2.0): updates metadata, claims ArNS operator discount; cannot touch stake, delegation, observer or itself. Keeps the operator key offline.

## Epoch cycle (daily)

1. Start: observers chosen by weighted random selection; prescribed ArNS names chosen (25 per epoch, up to 50 observers per `epochSettings`).
2. Observation: observers test gateways (wallet ownership, ArNS resolution to expected tx id, content hash, response time; chunk/offset validation if selected).
3. Reporting: observers upload a JSON report to Arweave **and** submit on-chain failed-gateway lists (`saveObservations({ reportTxId, failedGateways })`).
4. Tally: majority of submitted observers PASS → **functional**; else **deficient**.
5. Distribute: protocol balance (fed mainly by ArNS purchases) pays Base Gateway Reward to functional gateways and Base Observer Reward to observers that submitted.

Solana pipeline, permissionless and idempotent: `create_epoch → tally_weights → prescribe_epoch → save_observations → distribute_epoch → close_epoch`. Drive it with `ario.crankEpochStep()` or `ENABLE_EPOCH_CRANKING=true` on the observer.

## Weights

Composite weight = Stake Weight × Tenure Weight × Gateway Performance Ratio Weight × Observer Performance Ratio Weight, normalized across eligible gateways = selection probability. Functional epochs raise GPRW; submitted observations raise OPRW. Live view: `gateways.ar.io/#/observers`.

ArNS operator discount (20%) needs GPRW 0.9 and TW 1.0.

## Rewards

- Operator rewards auto-compound into operator stake; withdraw with `decreaseOperatorStake`.
- Delegates: reward-per-share accumulator, settled when the delegate interacts; split by `delegateRewardShareRatio`.
- Deficient observers lose observer reward and may have gateway reward reduced.
- Undistributed rewards roll forward (discourages observers from failing peers to grab a bigger share).
- Leaving gateways and fully withdrawn delegates earn nothing for that epoch.

## Gateway internals (for debugging)

- Node.js/TypeScript, event-driven workers: block sync, bundle processing, verification, maintenance.
- SQLite DBs: `core` (blocks/tx), `data` (hashes, cache meta), `bundles` (data items), `moderation`, `chunks`; Redis for chain + ArNS cache; optional ClickHouse; filesystem for chunks, headers, contiguous data; CDB64 root-tx indexes under `data/indexes`.
- Trust hierarchy for serving: cached verified → trusted cached → network streams; verification state in response headers.
