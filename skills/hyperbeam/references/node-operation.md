# Running a HyperBEAM node

Source docs: 15 (Running), 39 (Configuring), 16 (Routers), 9 (TEE), 38/40 (operator FAQ, troubleshooting), 176, 181.

## Requirements

Ubuntu 22.04 or macOS (tested), Erlang/OTP 27, rebar3, cmake/git/pkg-config/openssl/ncurses, Node 22+, Rust (for WASM/NIF devices like `~snp@1.0`), an Arweave wallet keyfile. Containers are not recommended yet. One node per IP in production.

## Run

```bash
git clone <HyperBEAM repo> && cd HyperBEAM && rebar3 compile
rebar3 shell                         # dev; HTTP on 8734
rebar3 as rocksdb, genesis_wasm shell   # profiles: rocksdb, genesis_wasm, http3 (compile-time)
curl http://localhost:8734/~meta@1.0/info

rebar3 release                       # production
cd _build/default/rel/hb && ./bin/hb start|console|ping|status|stop
```

Stop the shell with Ctrl-C twice or `q().`.

## config.flat

`Key = Value.` lines (note the period), in the working dir or `HB_CONFIG_LOCATION`. Only scalars; lists/maps (e.g. `store`) need env vars or `hb:start_mainnet/1`.

| Key | Default |
|---|---|
| `port` | 8734 |
| `priv_key_location` | `hyperbeam-key.json` |
| `mode` | debug (`prod`) |
| `gateway` | `https://arweave.net` |
| `bundler_ans104` | `https://up.arweave.net:443` |
| `protocol` | http2 |
| `scheduling_mode` | local_confirmation |
| `compute_mode` | lazy |
| `store_all_signed` | true |
| `load_remote_devices` | false |
| `wasm_allow_aot` | false |

Env overrides: `HB_PORT`, `HB_KEY`, `HB_STORE`, `HB_PRINT` (true or module list, e.g. `hb_http,dev_router`), `HB_CONFIG_LOCATION`. The docs give the precedence list inconsistently (one place: CLI erl_opts > config.flat > env > defaults; another says env overrides config.flat). Verify on your build before relying on it.

Full option list: `default_message/0` in `hb_opts.erl`.

## Routers

- **Joining** a router (worker): config with `operator: trustless`, `initialized: permanent`, `on.request/response` → `p4@1.0` with `lua@5.3a` ledger and `simple-pay@1.0` pricing, `p4_non_chargable_routes`, `node_processes.ledger`, `router_opts.offered` (template, price). Then call in order: `POST ~meta@1.0/info`, `GET ~greenzone@1.0/join`, `GET ~greenzone@1.0/become`, `GET ~router@1.0/register`.
- **Running** a router: `on.request` → `router@1.0` `preprocess`, `router_opts.provider/registrar` paths on `router~node-process@1.0`, weights (`pricing-weight`, `performance-weight`, `score-preference`), `is-admissible` policy. Advanced; most operators should join instead. See `dev_router.erl`, `scripts/dynamic-router.lua`.
- `initialized: permanent` locks configuration; double-check before booting.

## TEE nodes

AMD EPYC Milan+ with SEV-SNP enabled. HB-OS (`permaweb/hb-os`: `./run init && ./run setup_host && ./run build_base_image && ./run build_guest_image && ./run start`) gives dm-verity, measured boot and automatic attestation. Clients call `/~snp@1.0/generate` and verify nonce, signature, ephemeral address, debug disabled, trusted firmware/kernel/initramfs hashes (`snp_trusted`), measurement, AMD signature. Custom policy: `is-trusted-device` header on `/~snp@1.0/verify`.

## Troubleshooting

| Problem | Check |
|---|---|
| Erlang build fails | deps (`libssl-dev ncurses-dev make cmake gcc g++`), `./configure --without-wx --without-debugger --without-observer --without-et`, disk space |
| Node won't start | port conflict, key file path, crash dump |
| Crashes | memory/disk, network to external services |
| CU won't start / unreachable | `node -v`, `npm i`, `.env`, wallet file, `curl http://localhost:6363`, firewall |
| Debug logging | `HB_PRINT=...` or `DEBUG=HB_PRINT rebar3 shell` |
