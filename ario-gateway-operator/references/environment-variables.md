# Gateway environment variables (curated)

Source doc: 32 (~4,000 words, every variable). This is the subset that decides behavior; print the full table with `python tools/docslice.py 32`.

Set in `.env` next to `docker-compose.yaml`. Defaults below are under the shipped compose file. Restart after changes.

## Identity and keys

| Variable | Default | Notes |
|---|---|---|
| `AR_IO_WALLET` | – | operator Solana pubkey (base58); shown on `/ar-io/info` |
| `SOLANA_RPC_URL` | `https://api.mainnet-beta.solana.com` | use a dedicated provider in production |
| `SOLANA_KEYPAIR_PATH` / `SOLANA_PRIVATE_KEY` | – | operator key (64-byte JSON, path under `/app/wallets/`) or base58 secret; mutually exclusive |
| `OBSERVER_WALLET` | – | observer address; must match `observerWallet` at join |
| `OBSERVER_KEYPAIR_PATH` / `OBSERVER_PRIVATE_KEY` | – | observer Ed25519 key; also signs HTTP responses |
| `ARWEAVE_UPLOAD_KEY_FILE`, `ARWEAVE_UPLOAD_JWK`, `ETHEREUM_UPLOAD_PRIVATE_KEY(_FILE)`, `SOLANA_UPLOAD_KEYPAIR_PATH`, `SOLANA_UPLOAD_PRIVATE_KEY` | – | report upload signer, in that precedence; mixing groups is rejected; falls back to observer then operator key |
| `ADMIN_API_KEY` / `ADMIN_API_KEY_FILE` | generated | bearer for `/ar-io/admin/*` |
| `ARIO_CORE_PROGRAM_ID`, `ARIO_GAR_PROGRAM_ID`, `ARIO_ARNS_PROGRAM_ID`, `ARIO_ANT_PROGRAM_ID` | mainnet ids | override for devnet/staging |
| `ENABLE_EPOCH_CRANKING` | false | observer runs permissionless epoch instructions |

## Ports and logging

`CORE_PORT` 4000, `ENVOY_PORT` 3000 (what nginx proxies to), `OBSERVER_PORT` 5050, `CORE_LOG_LEVEL` info, `CORE_LOG_FORMAT` simple|json, `OBSERVER_LOG_LEVEL` verbose.

## ArNS and serving

| Variable | Default | Notes |
|---|---|---|
| `ARNS_ROOT_HOST` | – | your domain; required for `name.domain` resolution and observation |
| `SANDBOX_PROTOCOL` | – | `https` in production |
| `APEX_TX_ID` / `APEX_ARNS_NAME` | – | serve content at `/` (set only one; ArNS form updates without restart) |
| `ARNS_CACHE_TTL_SECONDS` | 86400 | |
| `ARNS_RESOLVER_PRIORITY_ORDER` | `on-demand,gateway` | |
| `ARNS_NOT_FOUND_TX_ID` / `ARNS_NOT_FOUND_ARNS_NAME` | `unregistered_arns` | 404 page |

## Data sources and trust

| Variable | Default |
|---|---|
| `TRUSTED_NODE_URL` | `http://envoy:3000` (→ `TRUSTED_NODE_HOST` arweave.net) |
| `TRUSTED_GATEWAYS_URLS` | `{"https://turbo-gateway.com": 1, "https://arweave.net": {"priority": 2, "trusted": false}}` |
| `TRUSTED_GATEWAY_URL` | single trusted gateway alternative |
| `ON_DEMAND_RETRIEVAL_ORDER` | `trusted-gateways,ar-io-network,chunks-offset-aware,tx-data` |
| `BACKGROUND_RETRIEVAL_ORDER` | `chunks` |
| `ROOT_TX_LOOKUP_ORDER` | `db,gateways,graphql,hyperbeam,cdb` (put `cdb` right after `db` when using index sharing) |
| `CDB64_ROOT_TX_INDEX_SOURCES` | three shipped indexes (~3.8B records); list them too when adding your own |
| `GRAPHQL_HOST` / `GRAPHQL_PORT` | `core`/4000; set `turbo-gateway.com`/443 to proxy GraphQL for a complete index |

## Indexing

| Variable | Default | Notes |
|---|---|---|
| `ANS104_UNBUNDLE_FILTER` | `{"never": true}` | which bundles to unbundle |
| `ANS104_INDEX_FILTER` | `{"always": true}` with background verification on, else never | which items to index |
| `ANS104_UNBUNDLE_WORKERS` / `ANS104_DOWNLOAD_WORKERS` | 1 / 5 (0 when nothing to do) | |
| `FILTER_CHANGE_REPROCESS` | false | reprocess old bundles with new filters |
| `BACKFILL_BUNDLE_RECORDS` | false | |
| `DATA_ITEM_FLUSH_COUNT_THRESHOLD` / `MAX_FLUSH_INTERVAL_SECONDS` | 1000 / 600 | |
| `MAX_DATA_ITEM_QUEUE_SIZE` | 100000 | |
| `ENABLE_BACKGROUND_DATA_VERIFICATION` | true | |
| `WEBHOOK_TARGET_SERVERS`, `WEBHOOK_INDEX_FILTER`, `WEBHOOK_BLOCK_FILTER` | –, never, never | push indexed tx / blocks to URLs |
| `NODE_MAX_OLD_SPACE_SIZE` | 2048 (8192 with >1 unbundle worker) | MB |
| `TAG_SELECTIVITY` | JSON weights | query planner hints |

## Index sharing (Release 84+)

`INDEX_SWARM_SUBSCRIBE='[{"publisher":"<wallet>","name":["root-tx-index"]}]'`, `INDEX_SWARM_PUBLISH`, `INDEX_SWARM_MAX_DISK_BYTES`, `INDEX_SWARM_TRUSTED_PUBLISHERS`, torrent engine via `INDEX_SWARM_ENGINE_AUTH` (profile `index-swarm-torrent`), band building via `INDEX_EXPORT_*` (Release 85, profile `index-export`). `parquet-l1` bands are opt-in and must be named.

## HTTP signatures, rate limit, x402

| Variable | Default |
|---|---|
| `HTTPSIG_ENABLED` | true (RFC 9421; observer key if set, else `data/keys/httpsig.pem`) |
| `HTTPSIG_BIND_REQUEST` | true |
| `ENABLE_RATE_LIMITER` | false; `RATE_LIMITER_IP_*`, `RATE_LIMITER_RESOURCE_*`, `RATE_LIMITER_IPS_AND_CIDRS_ALLOWLIST`, `RATE_LIMITER_ARNS_ALLOWLIST` |
| `TRUSTED_PROXIES` | private ranges; add CDN/LB ranges when one is in front |

## Observer

`RUN_OBSERVER` true, `SUBMIT_CONTRACT_INTERACTIONS` true (no-op unless prescribed), `NUM_ARNS_NAMES_TO_OBSERVE_PER_GROUP` 8, `REPORT_GENERATION_INTERVAL_MS` 3600000, `REPORT_DATA_SINK` turbo.

## Storage and extras

ClickHouse: `CLICKHOUSE_URL`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`. Redis: `REDIS_MAX_MEMORY` 256mb. S3 contiguous data: `AWS_*`. Litestream backups: `AR_IO_SQLITE_BACKUP_S3_*`. Image pins: `CORE_IMAGE_TAG`, `ENVOY_IMAGE_TAG`, `OBSERVER_IMAGE_TAG`, ... `RUN_AUTOHEAL` restarts unhealthy containers.
