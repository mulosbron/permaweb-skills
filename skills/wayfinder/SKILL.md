---
name: wayfinder
description: "Use when fetching or resolving Arweave/ArNS content across multiple ar.io gateways with client-side verification using @ar.io/wayfinder-core or @ar.io/wayfinder-react: replacing single-gateway arweave.net links, resolving ar:// URLs, routing strategies (FastestPing, PreferredWithFallback, random), HashVerificationStrategy, NetworkGatewaysProvider with Solana ARIO, or React WayfinderProvider and hooks."
metadata:
  category: permaweb
  triggers: wayfinder, "@ar.io/wayfinder-core", "@ar.io/wayfinder-react", ar://, WayfinderProvider, useWayfinderRequest, useWayfinderUrl, HashVerificationStrategy
---

# Wayfinder (`@ar.io/wayfinder-core` & `@ar.io/wayfinder-react`)

Routes `ar://` requests and Arweave/ArNS lookups across decentralized ar.io gateways instead of hard-coding a single gateway (`arweave.net`), with optional client-side verification.

```ts
import { createWayfinderClient } from '@ar.io/wayfinder-core';

const wayfinder = createWayfinderClient();
const res = await wayfinder.request('ar://<txId-or-arns>');
const url = await wayfinder.resolveUrl({ arnsName: 'ardrive' });
```

## References

- Core client, routing strategies, `HashVerificationStrategy`, `resolveUrl`, Solana `ARIO` integration: `references/core.md`
- React `WayfinderProvider`, `useWayfinderUrl`, `useWayfinderRequest`, `useWayfinder`, Vite polyfills: `references/react.md`

## Rules

1. **Verification is off by default.** Enable `verificationSettings: { enabled: true, strict: true }` (e.g. with `HashVerificationStrategy`) when reading untrusted data.
2. **`useWayfinderUrl` does not verify bytes**—it only resolves a URL for `src`/`href`. Use `useWayfinderRequest()` when byte verification is required.
3. **Pass Solana-initialized `ARIO`** (`ARIO.init({ rpc })` from `@ar.io/sdk`) to `NetworkGatewaysProvider({ ario })`. Older examples showing `ARIO.mainnet()` are legacy (`../ario-sdk/SKILL.md`).
4. **Instantiate `ario`, providers, and strategies outside React render** (module scope or `useMemo`) so `WayfinderProvider` does not recreate the client on every render.
5. **Decode binary responses** (`arrayBuffer` → Blob URL or `TextDecoder`) before rendering; passing an `ArrayBuffer` directly into JSX prints nothing useful.
6. **Check installed package exports** before using strategies/providers beyond `FastestPingRoutingStrategy`, `PreferredWithFallbackRoutingStrategy`, `random`, and `HashVerificationStrategy` (several Wayfinder strategy docs returned 404 in the snapshot).

## Fetch the docs

```bash
python tools/docslice.py 23 26 28 79 82 106 134 150
```
