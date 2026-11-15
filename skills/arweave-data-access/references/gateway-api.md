# ar.io gateway HTTP API

Source docs: 95 (Data), 96 (Chunks), 97 (Gateway), 98 (GraphQL), 99 (Pricing), 100 (Admin), 147 (Wallets), 149 (Blocks), 94 (Farcaster), 206.

Examples use `https://turbo-gateway.com`; every ar.io gateway exposes the same routes. ids match `^[0-9a-zA-Z_-]{43}$`.

## Data

| Route | Notes |
|---|---|
| `GET/HEAD /:txId` | content, manifest resolution, `Range` support, verification and cache headers |
| `GET/HEAD /raw/:txId` | raw bytes, no manifest resolution |
| `GET /:manifestId/:path` | manifest path |

Request hint headers for data items (optional; the URL id is authoritative):

| Header | Meaning |
|---|---|
| `X-AR-IO-Root-Transaction-Id` | L1 transaction containing the item |
| `X-AR-IO-Root-Path` | comma list: root tx → each parent bundle (nested bundles) |
| `X-AR-IO-Root-Item-Offset` + `X-AR-IO-Root-Item-Size` | full item location in root data; only without `Range`, used only if the item signature verifies |

Response headers to save for later requests: `X-AR-IO-Root-Transaction-Id`, `X-AR-IO-Data-Item-Offset`, `X-AR-IO-Data-Item-Size`, plus root offsets (`X-AR-IO-Root-Data-Item-Offset`, `X-AR-IO-Root-Data-Offset`). Relationship: `rootDataItemOffset = rootParentOffset + offset`.

## Chunks

| Route | Notes |
|---|---|
| `GET/HEAD /chunk/:offset` | JSON `{ tx_path, packing, data_path, chunk }` (base64url) |
| `GET/HEAD /chunk/:offset/data` | raw binary chunk (~40% less bandwidth); headers `X-Arweave-Chunk-Start-Offset`, `-Tx-Start-Offset`, `-Relative-Start-Offset`, `-Read-Offset`, `-Data-Path`, `-Data-Root`; `If-None-Match` → 304 |

`offset` is a weave byte position. The whole 256 KiB chunk containing it comes back; start reading at `X-Arweave-Chunk-Read-Offset`.

## Gateway info

| Route | Returns |
|---|---|
| `GET /` | gateway info, or apex content if `APEX_TX_ID` / `APEX_ARNS_NAME` is configured |
| `GET /ar-io/info` | wallet, unbundle/index filters, manifest versions, release, `services.bundlers`, `rateLimiter`, `x402`, `httpsig` (ed25519 response signing, attestation), `indexes` |
| `GET /ar-io/healthcheck` | `{ status, uptime, date, reasons }` |
| `GET /ar-io/offsets/:id` | `{ rootTxId, path, rootOffset, rootDataOffset, contentType, size, dataSize }` from one index lookup |
| `GET /ar-io/peers` | ar.io peers with `dataWeight`/`chunkWeight`, Arweave nodes |
| `GET /ar-io/__gateway_metrics` | Prometheus metrics |
| `POST /graphql` | GraphQL (see `graphql.md`) |
| `GET /ar-io/indexes` | signed index publication (index sharing) |

## Arweave-node compatible

| Route | Returns |
|---|---|
| `GET /price/:bytes` | Winston to store bytes on L1 |
| `GET /price/:bytes/:target` | Winston including wallet creation for target |
| `GET /wallet/:address/balance` | AR balance in Winston |
| `GET /wallet/:address/last_tx` | last tx id |
| `GET /current_block`, `/block/current`, `/block/height/:h`, `/block/hash/:hash` | block JSON |

## Admin (bearer `ADMIN_API_KEY`, own gateway only)

| Route | Purpose |
|---|---|
| `GET /ar-io/admin/debug` | debug info |
| `POST /ar-io/admin/queue-tx` `{ id }` | prioritize indexing a tx or bundle |
| `POST /ar-io/admin/queue-bundle` `{ id }` | index a bundle, bypassing filters |
| queue data items | prioritize data item headers |
| `POST /ar-io/admin/queue-optimistic-tx` | index signed, unmined L1 headers (needs `OPTIMISTIC_TX_INDEXING_ENABLED=true`) |
| `GET /ar-io/admin/bundle-status/:id` | unbundling progress |
| `PUT /ar-io/admin/block-data` `{ id, notes, source }` | stop serving a tx/data item/hash (testing with a real id blocks it) |
| `PUT /ar-io/admin/block-name`, `/unblock-name` | ArNS name moderation |
| `POST /ar-io/admin/export-parquet` + `/status[/:jobId]` | Parquet export by height range |
| `POST /ar-io/admin/prune-stable-data-items` `{ indexedAtThreshold }` | DB size management |

## Farcaster Frames

`GET/POST /local/farcaster/frame/:txId` serves a tx as a Frame initial/response.
