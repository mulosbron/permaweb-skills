# Gateway operations

Source docs: 20 (Filters), 29 (SSL), 30 (Moderation), 31 (Snapshots), 33 (Apex), 112 (Troubleshooting), 113 (Join), 141 (Upgrading), 111.

## Filters

Two filters: `ANS104_UNBUNDLE_FILTER` (which bundles to open) and `ANS104_INDEX_FILTER` (which items inside to index). Grammar:

| Form | Meaning |
|---|---|
| `{"always": true}` / `{"never": true}` | everything / nothing (empty = never) |
| `{"tags": [{"name": "App-Name", "value": "X"}]}` | exact; all listed tags must match |
| `{"tags": [{"name": "App-Name"}]}` | tag present |
| `{"tags": [{"name": "Protocol", "valueStartsWith": "AO"}]}` | prefix |
| `{"attributes": {"owner_address": "...", "data_size": 1000}}` | metadata; owner keys auto-converted to addresses |
| `{"isNestedBundle": true}` | item is a bundle inside a bundle (match it in **both** filters) |
| `{"and": [...]}`, `{"or": [...]}`, `{"not": {...}}` | nest to any depth |

Tag names/values are base64url-decoded before matching. Recipes:

- Own uploads only: unbundle `{"tags":[{"name":"App-Name","valueStartsWith":"MyApp"}]}`, index `{"attributes":{"owner_address":"<you>"}}`.
- Bundles from your own bundler sidecar: unbundle `{"attributes":{"owner_address":"$BUNDLER_ARWEAVE_ADDRESS"}}`, index `{"always":true}`.
- ArFS app: index `or` over `ArFS` = `0.10`/`0.11`/`0.12`.
- Excluding noisy bundlers: `not` + `or` over `Bundler-App-Name` (`Warp`, `Redstone`, `AO`).

After changes: restart; `FILTER_CHANGE_REPROCESS=true` to re-run old bundles. If processing stops: invalid JSON, missing env, or not restarted.

## TLS

```bash
apt install certbot python3-certbot-dns-cloudflare -y
# /etc/letsencrypt/cloudflare.ini: dns_cloudflare_api_token = ...   (chmod 600)
certbot certonly --dns-cloudflare --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini -d example.com -d '*.example.com'
certbot renew --dry-run && systemctl list-timers | grep certbot
```

Namecheap needs API eligibility (20 domains or $50 balance/spend) and `certbot-dns-namecheap`. Reload nginx after renewal.

## Content moderation

```bash
curl -X PUT http://localhost:3000/ar-io/admin/block-data -H "Authorization: Bearer $ADMIN_API_KEY" \
  -H 'Content-Type: application/json' -d '{"id":"<txid>","notes":"reason","source":"Public Block list"}'
curl -X PUT .../ar-io/admin/block-name   -d '{"name":"<arns>","notes":"...","source":"..."}'
curl -X PUT .../ar-io/admin/unblock-name -d '{"name":"<arns>"}'
```

Unblock data: `sqlite3 data/sqlite/moderation.db "DELETE FROM blocked_ids WHERE id=X'<hex of txid bytes>';"` or delete by `block_source_id` of a named source. A blocked name stays blocked even if its owner repoints it.

## Apex content

`APEX_ARNS_NAME=<name>` (preferred, updates without restart) or `APEX_TX_ID=<id>` (restart to change). Set only one. Check with `grep -E "APEX_(TX_ID|ARNS_NAME)" .env`.

## Bootstrapping the index

- **SQLite snapshot** (2025-04-23, block 1645229, ~42.8 GB, ArDrive/Turbo data items): download by BitTorrent magnet, `docker compose down`, move files into `data/sqlite/`, `up -d`, watch `docker compose logs -f core` import from 1645230.
- **L1 bands** (Release 85): subscribe `INDEX_SWARM_SUBSCRIBE` with `"name":["root-tx-index","parquet-l1"]`, `docker compose stop core`, `./tools/ar-io-node index-l1-import --bands-dir data/indexes/installed/parquet-l1 --core-db data/sqlite/core.db --cache-mib 8192`, then `up -d --no-deps core`. ~15 GB bands + ~120 GB core.db. No data items included.
- **Index sharing only** (~21 GB root-tx index, kept current) to resolve data items without a full DB.

## Upgrade

```bash
git pull               # on main
docker compose down -v # -v removes anonymous volumes; indexed data lives in ./data, not in them
# diff .env.example for new variables, add them
docker compose up -d   # no --build needed
```

Check `https://<gateway>/ar-io/info` release; `-pre` means `develop`.

## Joining via CLI

```bash
npm install -g @ar.io/sdk
# --wallet-file takes a 64-byte keypair JSON; use --private-key '<base58>' for a Phantom export instead
ar.io join-network -t solana --mainnet --rpc-url <rpc> \
  --core-program-id 73Yo... --gar-program-id 89fN... --arns-program-id 2yCU... --ant-program-id 2MWe... \
  --wallet-file ./solana-keypair.json \
  --operator-stake 20000 --allow-delegated-staking --min-delegated-stake 100000000 \
  --delegate-reward-share-ratio 10 --observer-address <pubkey> --fqdn gateway.example.com --auto-stake
ar.io get-gateway -t solana --mainnet --rpc-url <rpc> ...program ids... --address <operator pubkey>   # expect "status": "joined"
```

Portal: `gateways.ar.io/#/<operator pubkey>`. Observation starts next epoch (daily).

## Troubleshooting (observer report reasons)

| Symptom / reason | Fix |
|---|---|
| Timeout awaiting socket/connect (persistent) | gateway down, DNS, TLS, ISP blocking home networks |
| Cert has expired | renew and reload proxy |
| `dataHashDigest mismatch` (most names) | gateway not on mainnet, or stale cache |
| 502 | nginx up, core down or misrouted; `nginx -t`, reload, check containers |
| 503 (persistent) | core crashed or overloaded; restart |
| `EHOSTUNREACH`, `getaddrinfo ENOTFOUND` | DNS for apex or wildcard missing |
| Host not in cert altnames / `tlsv1 unrecognized name` | cert lacks the domain or the wildcard |
| Observing own gateway fails | `AR_IO_WALLET`, `ARNS_ROOT_HOST` |
| `.env` changes ignored | restart/recreate containers |
| Out of disk | check inode exhaustion |
| `/ar-io/observer/reports/current` "report pending" | normal |

A gateway failed by more than half of prescribed observers gets no reward that epoch. Run manual observations from the Network Portal ("Observe" → "Run Observation"). ArNS resolution > 10 s in Grafana means the gateway is misconfigured or outdated.
