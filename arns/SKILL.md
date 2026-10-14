---
name: arns
description: "Use when giving Arweave content a human-readable name with ArNS: buying or leasing a name, pointing it (or an undername like blog_name) at a manifest or tx id, managing ANT records/controllers/ownership, primary names, delegated undername ownership, deploy-time record updates, name pricing, returned-name auctions, or trading ANTs on Solana NFT marketplaces."
metadata:
  category: permaweb
  triggers: arns, ar.io name, undername, ANT, setRecord, primary name, buy arns name, arns deploy, name.ar.io
---

# ArNS (Ar.io Name System)

A name in the ArNS registry (Solana program `ario-arns`) points to an **ANT** (Ar.io Name Token, a Metaplex Core NFT managed by `ario-ant`). The ANT holds **records**: `@` (the base name) and undernames, each mapping to an Arweave tx id with a TTL. Every ar.io gateway resolves `https://<name>.<gateway>/` and `ar://<name>`.

```
myapp            -> ANT record "@"    -> manifest tx id   https://myapp.ar.io
docs_myapp       -> ANT record "docs" -> other tx id      https://docs_myapp.ar.io
```

## Common jobs

| Job | How |
|---|---|
| Get a name | arns.ar.io (fiat, Turbo credits, ARIO), Turbo SDK `buyArNSName`, or ar.io SDK `ario.buyRecord` |
| Point name at a deploy | `ant.setBaseNameRecord({ transactionId, ttlSeconds })` or `ant.setRecord({ undername: '@', ... })` |
| Versioned/preview deploys | `ant.setUndernameRecord({ undername: 'v2', transactionId, ttlSeconds })` → `v2_myapp` |
| Let a teammate or CI update records | `ant.addController({ controller })` (max 10) |
| Give someone one undername | `setUndernameRecord({ ..., owner })` or `ant.transferRecord({ undername, recipient })` |
| Wallet display name | `ario.setPrimaryName({ name })` |
| Read where a name points | `ario.getArNSRecord({ name })` → ANT id; `ant.getRecords()` |

Client setup, every method and the permission matrix: `references/ants-and-records.md`. Registration rules, pricing, leases, returns: `references/registration-and-pricing.md`.

## Minimal record update

```ts
import { ARIO, ANT } from '@ar.io/sdk';
import { createSolanaRpc, createSolanaRpcSubscriptions } from '@solana/kit';

const rpc = createSolanaRpc('https://api.mainnet-beta.solana.com');
const rpcSubscriptions = createSolanaRpcSubscriptions('wss://api.mainnet-beta.solana.com');
const record = await ARIO.init({ rpc }).getArNSRecord({ name: 'myapp' });
const ant = await ANT.init({ processId: record.processId, rpc, rpcSubscriptions, signer }); // @solana/kit signer of owner or controller
await ant.setBaseNameRecord({ transactionId: manifestId, ttlSeconds: 3600 });
```

## Rules

1. **Writes need `signer` + `rpcSubscriptions`** on `ARIO.init` / `ANT.init`. Without them the client is read-only and write calls fail.
2. **`processId` now means the ANT's Metaplex Core asset pubkey** (a Solana address), not an AO process id. Get it from `getArNSRecord`.
3. **Undernames use `_`, not `.`**: `docs_myapp.ar.io`. `@` is the base record.
4. **A record owner updating their own undername must pass `owner: <their address>`.** Omitting `owner` renounces it back to the ANT owner; a different address transfers it.
5. **TTL is client cache time.** Use short TTLs (300–900 s) on records you redeploy often; gateways and clients cache resolutions that long.
6. **Validate names before buying**: `a-z`, `0-9`, `-`; 1–51 chars; no leading/trailing dash; no dash in 1-char names; never exactly 43 chars; lowercase; reserved names (e.g. `www`) rejected.
7. **Price from the live source.** Use the SDK, Turbo `getArNSPriceForName` (`wincTotal`), or arns.ar.io. Do not hard-code formulas; the Demand Factor moves.
8. **Losing the owner key of a permabought name loses the name.** Keep the owner key cold and give CI a controller key.

## Things that bite

- Doc snippets do `const arnsRecord = await ario.getArNSRecord(...)` then `ANT.init({ processId: arnsName.processId })`; the variable is `arnsRecord`, and on Solana `ANT.init` also needs `rpc`.
- AO-era helpers (`releaseName`, `reassignName`, `approvePrimaryNameRequest`, `removePrimaryNames`, `ANT.fork`, static `ANT.upgrade`) are removed. Use `ARIO` write methods (`upgradeRecord`, `setPrimaryName`, ...), `ant.upgrade()` for schema migration, `ANT.spawn()` for new ANTs.
- After a marketplace sale (Tensor, Magic Eden) old controllers are cleared lazily on the next write; until then `getControllers()` may still list them.
- Some docs still show `ARIO.mainnet()`; the current SDK (Solana default since v3.23) is initialized with `ARIO.init({ rpc })`.
- `ant.getState()` / `getHandlers()` examples still list AO handler names; treat them as legacy shape.

## Typical deploy flow

1. Build with relative paths → `turbo.uploadFolder` → manifest id (`../turbo-upload/SKILL.md`).
2. `ant.setUndernameRecord({ undername: 'preview', ... })`, check `https://preview_myapp.<gateway>`.
3. Promote: `ant.setBaseNameRecord({ transactionId: sameManifestId })`.
4. Old manifest ids stay live forever; rollback means pointing `@` back.

## Fetch the docs

```bash
python tools/docslice.py 131 14 119 120 217
```

Live: `https://docs.ar.io/learn/arns`; SDK reference `https://docs.ar.io/sdks/ar-io-sdk`.
