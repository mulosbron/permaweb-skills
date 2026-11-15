# @ar.io/wayfinder-core

Source docs: 23, 26 (Integration), 79, 82 (Protocol), 134 (Dynamic Routing), 146 (Telemetry), 150 (Core), 10 (DePIN example).

```bash
npm install @ar.io/wayfinder-core @ar.io/sdk
```

## Client

```ts
const wayfinder = createWayfinderClient(options?);
await wayfinder.request(url, perRequestOverrides?);   // Response
await wayfinder.resolveUrl({ txId } | { arnsName } | { originalUrl });  // string URL
```

`createWayfinderClient()` with no options works and uses defaults (network gateways, verification off).

### Options seen in the docs

| Option | Shape |
|---|---|
| `routingSettings.strategy` | a routing strategy instance |
| `gatewaysProvider` | where candidate gateways come from (`NetworkGatewaysProvider({ ario })`) |
| `verificationSettings` | `{ enabled: boolean, strategy?, strict?: boolean }` |
| `telemetrySettings` | `{ enabled, sampleRate, exporterUrl?, apiKey?, clientName, clientVersion }` |
| legacy: `ario`, `routingStrategy`, `verificationStrategy` | older top-level form |

Per-request overrides: `request('ar://id', { verificationSettings: { enabled: true, strict: true } })`.

## Routing strategies (documented here)

| Strategy | Behavior |
|---|---|
| `FastestPingRoutingStrategy({ timeoutMs?, gatewaysProvider? })` | ping candidates, use the fastest |
| `PreferredWithFallbackRoutingStrategy({ preferredGateway, fallbackStrategy })` | your gateway first, fallback strategy on failure |
| `createRoutingStrategy({ strategy: 'random' })` | random gateway (factory form) |

The docs also mention round-robin distribution, static gateways and other providers on pages not in this snapshot (several returned 404 at crawl time). Read the installed package's exports or the live docs before using them.

## Verification strategies

| Strategy | Behavior |
|---|---|
| `HashVerificationStrategy({ trustedGateways: [URL] })` | compare the served data's hash with the hash reported by trusted gateways |
| `createVerificationStrategy({ strategy: 'hash', trustedGateways: [...] })` | factory form |

Protocol-level verification covers: content matches tx id, transmission integrity, manifest components, ArNS name to tx id resolution.

## resolveUrl results

| Input | Output |
|---|---|
| `{ arnsName: 'ardrive' }` | `https://ardrive.<gateway>` |
| `{ txId }` | `https://<gateway>/<txId>` |
| `{ originalUrl: 'https://arweave.net/<id>' }` | `https://<gateway>/<id>` |
| `{ originalUrl: 'ar://name/sub?x=1' }` | `https://<gateway>/name/sub?x=1` |

## With the ar.io SDK on Solana

```ts
import { ARIO } from '@ar.io/sdk';
import { createSolanaRpc } from '@solana/kit';
const ario = ARIO.init({ rpc: createSolanaRpc('https://api.mainnet-beta.solana.com') });
new NetworkGatewaysProvider({ ario });
```

Older examples use `ARIO.mainnet()`; see `../../ario-sdk/SKILL.md` for the current init.
