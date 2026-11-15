---
name: arweave-data-access
description: "Use when reading, querying, or verifying Arweave data via gateways: GraphQL queries by tags, owners, recipients, or bundledIn with cursor pagination; ar.io gateway HTTP routes (/raw/:txId, /chunk/:offset, /ar-io/info, /ar-io/offsets/:id, admin endpoints); sandboxed subdomain origins (base32 txId); or gateway retrieval and Merkle verification."
metadata:
  category: permaweb
  triggers: arweave graphql, gateway api, turbo-gateway, goldsky, sandbox subdomain, txId, data retrieval, chunk
---

# Arweave Data Access

Read bytes and query transaction metadata through ar.io gateways (`https://turbo-gateway.com`) and Arweave GraphQL endpoints.

## Endpoints & routes

| Purpose | Endpoint / Route |
|---|---|
| Full-network GraphQL | `POST https://turbo-gateway.com/graphql` or `https://arweave-search.goldsky.com/graphql` |
| Gateway-indexed GraphQL | `POST https://<ar-io-gateway>/graphql` (scoped to what that gateway unbundled/indexed) |
| Fetch data / manifest path | `GET /:txId`, `GET /raw/:txId`, `GET /:manifestId/:path` |
| Gateway info & offsets | `GET /ar-io/info`, `GET /ar-io/healthcheck`, `GET /ar-io/offsets/:id` |

## References

- GraphQL arguments, node fields, cursor pagination, and query design: `references/graphql.md`
- Gateway HTTP API (data, hint headers, chunks, info, Arweave-node compatible, admin): `references/gateway-api.md`
- Sandbox subdomains (`base32`), retrieval order, Merkle verification, trust boundaries: `references/verification-and-sandboxing.md`

## Rules

1. **Filter GraphQL `owners:` with normalized addresses**, not raw `0x...` or base58 strings (`../arweave-core/references/addresses-and-signers.md`).
2. **Never trust tags alone for authenticity.** Anyone can write `App-Name: YourApp`; include `owners` or verify signatures.
3. **Unmined items have `block: null`** in GraphQL, so `HEIGHT_DESC` does not order items before confirmation.
4. **Each tx/manifest resolves on a sandboxed subdomain** (`base32(base64urlDecode(txId))`), isolating cookies, `localStorage`, and IndexedDB per deploy. Persist cross-deploy state under a stable ArNS subdomain or on-chain.
5. **A single gateway's response is only as trustworthy as its operator.** For untrusted contexts, verify client-side with Wayfinder (`../wayfinder/SKILL.md`).

## Fetch the docs

```bash
python tools/docslice.py 5 21 95 96 97 98 109 114 126
```
