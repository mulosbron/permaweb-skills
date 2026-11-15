# Sidecars: ClickHouse, bundler, Grafana

Source docs: 17 (Grafana), 18 (ClickHouse & Parquet), 19 (Bundler), 207.

Sidecars are separate containers on the gateway's Docker network. Community extensions are listed at `gateways.ar.io/#/extensions`.

## ClickHouse + Parquet

Speed/batch split: SQLite keeps real-time writes and recent blocks; ClickHouse serves GraphQL for blocks up to `max_imported_height - 10`. Results are merged and deduplicated; a circuit breaker degrades to ClickHouse-only with a partial-result warning.

Enable when GraphQL traffic on history is heavy or millions of items are indexed. Skip for small or retrieval-only gateways.

```bash
# .env
CLICKHOUSE_URL=http://clickhouse:8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=...
CLICKHOUSE_SQLITE_MIN_HEIGHT_ENABLED=true
ADMIN_API_KEY=...
docker compose --profile clickhouse up -d       # server + auto-import daemon
./scripts/clickhouse-import                     # after placing Parquet files in data/parquet
```

- ArDrive Parquet snapshot (~3.5 GB, to 2025-04-23, 32,712,311 distinct ids) needs matching unbundle/index filters.
- Auto-import every `CLICKHOUSE_AUTO_IMPORT_SLEEP_INTERVAL` (3600 s; 600–900 for busy gateways), `CLICKHOUSE_AUTO_IMPORT_HEIGHT_INTERVAL` 1000 blocks per partition.
- TTL rules in `config/clickhouse-ttl-rules.yaml` (`default_ttl_seconds`, `l1_never_expires`, rules by tag `exact|prefix` or `owner_address`; first matching branch wins: L1 keep → `never_expire` → shortest TTL → default → keep).
- Tuning: `CLICKHOUSE_GQL_DEDUPE_HEADROOM` (short pages → 8), `CLICKHOUSE_QUERY_TIMEOUT_SECONDS` (3 → 10), `CLICKHOUSE_GQL_MAX_ROWS_TO_READ` (10M guardrail).
- Topologies: single local; shared cluster with exactly one writer running auto-import; independent per gateway from a shared snapshot.
- Parquet files are the source of truth: rollback = drop table, re-import. Failed imports leave files in `data/etl/staging/`.

## Bundler (accept uploads through your gateway)

```bash
cp .env.bundler.example .env.bundler
# BUNDLER_ARWEAVE_WALLET='<stringified JWK>'   pays AR for every bundle
# BUNDLER_ARWEAVE_ADDRESS=<normalized address of that wallet>
# APP_NAME=...   AR_IO_ADMIN_KEY=<same as gateway admin key, in both env files>
docker compose --env-file ./.env.bundler --file docker-compose.bundler.yaml up -d
```

- Sync the gateway index to tip first; the bundler relies on GraphQL for its pipeline.
- In the **gateway** `.env`: `ANS104_UNBUNDLE_FILTER={"attributes":{"owner_address":"<BUNDLER_ARWEAVE_ADDRESS>"}}`, `ANS104_INDEX_FILTER={"always":true}`.
- Access control:

| Scheme | `ALLOW_LISTED_ADDRESSES` | `SKIP_BALANCE_CHECKS` | `ALLOW_LISTED_SIGNATURE_TYPES` | `PAYMENT_SERVICE_BASE_URL` |
|---|---|---|---|---|
| Specific wallets (default) | normalized addresses | false | empty/any | empty |
| Specific chains | any | false | arbundles sig type ints | empty |
| Allow all | n/a | true | n/a | n/a |
| Allow none | empty | false | empty | empty |
| Paying users | any | false | any | your payment service URL |

## Grafana

```bash
docker compose -f docker-compose.grafana.yaml up -d    # http://localhost:1024, admin/admin
```

Change the password after every start. To expose, add an nginx `location /grafana/ { proxy_pass http://localhost:1024/grafana/; ... }` behind TLS and restrict access.
