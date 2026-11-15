# Verification, retrieval and sandboxing

Source docs: 109 (Browser Sandboxing), 114 (Data Verification), 126 (Data Retrieval), 210 (ar.io Gateways).

## Sandbox subdomains

A gateway answers `https://gw.com/<txId>` with a 301 to `https://<sandbox>.gw.com/<txId>`, where `sandbox = base32(base64urlDecode(txId))` (lowercase, deterministic):

```ts
const expectedTxSandbox = (id: string) => toB32(fromB64Url(id));
// gnWKBqFXMJrrksEWrXLQRUQQQeFhv4uVxesHBcT8i6o -> qj2yubvbk4yjv24syelk24wqivcbaqpbmg7yxfof5mdqlrh4rova
```

Why it matters:

- Each tx/manifest is its own origin. Cookies, `localStorage`, IndexedDB and service workers are isolated per deploy. Persist user settings with a stable origin (ArNS subdomain) or on-chain, not per manifest id.
- Requires HTTPS and a wildcard TLS cert on the gateway. Without TLS, browsers disable WebCrypto and the app is open to MITM (e.g. a tampered `/price`).
- You can precompute the sandbox host to link directly and skip the redirect.

Custom domains (legacy DNS pattern): `CNAME www → gateway` plus `TXT arweavetx → <txId>`; the gateway reads the TXT record for non-default hostnames.

## How a gateway retrieves data

On-demand order (fast fallback, parallel attempts, streaming): **trusted gateways → untrusted ar.io peers → chunk assembly → Arweave nodes**.

Locating a data item: own database for what it indexed, CDB64 indexes kept current via index sharing for the rest, otherwise peers and GraphQL.

Background retrieval (unbundling, verification) prefers authoritative sources with relaxed timeouts.

## How a gateway verifies data

1. Queue unverified items by priority.
2. Stream the data, recompute the Merkle data root with Arweave's algorithm.
3. Compare with the indexed root; validate chunks against Merkle proofs.
4. Success: mark verified with a timestamp. Failure: re-import from Arweave or re-unbundle from the parent bundle. Error: retry later.

Bundles get container checks, per-item checks and recursive unbundling for nested bundles. Unmined optimistic data is never marked verified.

## What this means for clients

- A single gateway's response is only as trustworthy as that operator. For untrusted contexts, verify client-side: Wayfinder hash/data-root/signature verification (`../../wayfinder/SKILL.md`), or compare a hash you recorded at upload.
- Verification and cache status come back as response headers on data routes; read them with `HEAD`.
- Gateways may sign responses (`httpsig` in `/ar-io/info`, ed25519) and publish signed indexes keyed to their registered observer key.
