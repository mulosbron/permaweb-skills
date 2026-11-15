---
name: ario-gateway-operator
description: "Use when running or debugging an ar.io gateway (ar-io-node in Docker): .env configuration, ANS-104 unbundle/index filters, joining the network with ARIO stake on Solana, observer and epoch cranking, OIP failures in observer reports, TLS/wildcard certs, ArNS resolution, apex domain content, content moderation, SQLite snapshots, index sharing, ClickHouse, Grafana and bundler sidecars, upgrades."
metadata:
  category: permaweb
  triggers: ar.io gateway, ar-io-node, run a gateway, ANS104_UNBUNDLE_FILTER, gateway observer, join network, gateway env, failed epoch, ar.io operator
---

# ar.io Gateway Operator

An ar.io gateway is the `ar-io-node` Docker Compose stack: **core** (Node/TS, SQLite DBs `core`, `data`, `bundles`, `moderation`, `chunks`), **envoy** (front proxy, port 3000), **observer**, **redis**, plus optional sidecars (ClickHouse, index-swarm, bundler, Grafana, Litestream, autoheal). Protocol state (registry, stake, epochs, ArNS) lives on Solana.

Do not edit an operator's `.env`, run `docker compose down -v`, block content, or touch stake without explicit confirmation. Blocking with a real id blocks it for real.

## Before proposing anything

1. Read `.env` and the compose files in the repo root. Note `AR_IO_WALLET`, `ARNS_ROOT_HOST`, `OBSERVER_*`, `SOLANA_*`, filters, `TRUSTED_GATEWAYS_URLS`.
2. `curl https://<gateway>/ar-io/info | jq '{release, wallet, programIds}'` and `/ar-io/healthcheck`.
3. `docker compose logs -f --tail=100 core` (and `observer`).
4. The repo ships an operator skill at `.claude/skills/ar-io-gateway-operator/` with `scripts/health-check`; run it when present.

## Production checklist

| Item | Requirement |
|---|---|
| Domain + DNS | apex `A` record and wildcard `*.domain` (ArNS names and sandbox subdomains are subdomains) |
| TLS | wildcard cert (`-d example.com -d *.example.com`), DNS-01 via certbot plugin; auto-renew timer active |
| Reverse proxy | nginx 80→443 redirect, `proxy_pass http://localhost:3000`, forward `X-AR-IO-Origin`, `X-AR-IO-Origin-Node-Release`, `X-AR-IO-Hops` |
| `.env` | `ARNS_ROOT_HOST=<domain>`, `AR_IO_WALLET=<operator Solana pubkey>`, `ADMIN_API_KEY`, `SOLANA_RPC_URL` (dedicated provider, not public RPC) |
| Keys | operator `SOLANA_KEYPAIR_PATH` (inside container under `/app/wallets/`) or `SOLANA_PRIVATE_KEY`; observer `OBSERVER_KEYPAIR_PATH` or `OBSERVER_PRIVATE_KEY`; set upload signer `SOLANA_UPLOAD_PRIVATE_KEY` so report uploads do not fall back silently |
| Join | ≥ 20,000 ARIO operator stake + SOL for fees; portal `gateways.ar.io` or `ar.io join-network -t solana --mainnet ...` |
| Network | gateway must run on **mainnet** to pass observation |

Full variable reference: `references/environment-variables.md`. Day-2 tasks (filters, moderation, apex, snapshots, index sharing, upgrades, troubleshooting): `references/operations.md`. Sidecars: `references/extensions.md`. Registry, OIP, rewards: `references/network-and-oip.md`.

## Rules

1. **Filters default to nothing.** `ANS104_UNBUNDLE_FILTER` defaults to `{"never": true}`; a fresh gateway serves data but indexes no bundled data items. Set unbundle **and** index filters for what you need; restart after editing `.env`; use `FILTER_CHANGE_REPROCESS=true` to apply to old bundles.
2. **`--observer-address` must be unique** across gateways; it may equal the operator address. `observerWallet` at join must match `OBSERVER_WALLET` on the node.
3. **Program ids must match the network you joined.** `/ar-io/info.programIds` vs the cluster the stake is on; mismatch is the usual reason a new gateway never observes.
4. **CLI stake units differ**: `--operator-stake 20000` is whole ARIO; `--min-delegated-stake` is mARIO.
5. **Operator rewards auto-compound** into stake; realize them with `decrease_operator_stake`.
6. **Leaving takes ≥ 90 days** (joined → leaving → gone). Sustained deficiency gets the gateway pruned and its minimum join stake slashed.

## Things that bite

- The public Solana RPC rate-limits and may block `getProgramAccounts`; registry enumeration then fails silently. Use Helius, Triton, QuickNode or similar.
- `.env` names differ from in-container names (`CORE_LOG_LEVEL` → `LOG_LEVEL`). Outside Docker some defaults differ.
- Docs example `{"and": [{"equals": {"App-Name": ...}}]}` is not the documented filter grammar; use `tags`/`attributes`/`and`/`or`/`not`/`always`/`never`/`isNestedBundle`.
- Unblocking data means deleting rows from `data/sqlite/moderation.db` (ids are BLOBs: `X'<hex>'`). There is no unblock endpoint for data.
- `ADMIN_API_KEY` unset → random key generated at startup; admin calls start failing after restarts. Set it.
- Grafana sidecar starts with `admin/admin` on port 1024 and may reset after restart. Change it every time and don't expose it publicly without auth.
- Release numbers ending in `-pre` mean the `develop` branch; switch to `main`.
- Several features in current docs (L1 bands, `GATEWAYS_THROTTLE_BACKOFF_*`) need Release 85, which the docs mark as not yet released. Check `/ar-io/info.release`.

## Fetch the docs

```bash
python tools/docslice.py 32       # every environment variable
python tools/docslice.py 112 113  # troubleshooting, join the network
python tools/docslice.py --find INDEX_SWARM
```
