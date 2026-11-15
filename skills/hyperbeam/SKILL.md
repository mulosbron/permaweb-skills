---
name: hyperbeam
description: "Use when working with HyperBEAM, the Erlang AO-Core node that is AO's production network: reading AO process state over HTTP (/now, /compute), exposing state with ~patch@1.0 instead of dryrun, path syntax with ~device@version and key+type=value casting, device pipelines (~lua@5.3a, ~json@1.0, ~message@1.0), signed responses and TEE (~snp@1.0) attestation, or running a node (rebar3, config.flat, routers, p4 payments)."
metadata:
  category: permaweb
  triggers: hyperbeam, ao-core, ~process@1.0, ~patch@1.0, dryrun replacement, forward.computer, hyperbeam node, config.flat, ao mainnet
---

# HyperBEAM

HyperBEAM is the production implementation of **AO-Core** (Erlang/OTP). Everything is a **message**; a **device** (`~name@version`) says how to interpret it; a **path** is a pipeline of messages applied left to right. The URL bar is the command line. Each response is signed by the node and carries a hashpath, so it is verifiable and portable to other nodes.

## Reading AO process state (the main reason you are here)

```
GET https://<node>/<pid>~process@1.0/now                  full state, recomputed now (slower, freshest)
GET https://<node>/<pid>~process@1.0/compute              latest known state (fast)
GET https://<node>/<pid>~process@1.0/compute/cache/<key>  data the process published with ~patch@1.0
GET https://<node>/<pid>~process@1.0/now/~lua@5.3a&module=<id>/sum/serialize~json@1.0   pipeline: compute in Lua, return JSON
```

Publishing from the process (aos/Lua), after every write that changes public data:

```lua
-- shape per HyperBEAM "Exposing Process State"; confirm against the live doc for your aos version
Send({ device = "patch@1.0", cache = { books = Books, stats = Stats } })
-- readers: GET /<pid>~process@1.0/compute/cache/books
```

The cookbook welcome example reads a top-level field (`/compute/counter`), so the exact key layout depends on how you patch; test the URL once after deploy.

Paths, devices and type casting: `references/pathing-and-devices.md`. Running a node, config, routers, TEE: `references/node-operation.md`.

## Rules

1. **Reads are HTTP GETs; writes are signed messages.** Never send a message just to read, and do not use `dryrun` for HyperBEAM processes (deprecated: unsigned, unverifiable, and it bottlenecked CUs).
2. **Patch only what clients need**, from the handlers that change it. Don't patch secrets: everything patched is world-readable.
3. **Getters must not mutate.** State changes inside a read path are never persisted (they were silently dropped under dryrun too). Make counters/views an explicit write.
4. **`/compute` for UI polling, `/now` when you must include the latest messages.**
5. **Trust**: responses are signed by the node key; for trust-minimized reads use a TEE node and check `~snp@1.0` attestation, or compare across nodes.
6. **Message vs process ids**: `<pid>` is the AO process id (43 chars). Hashpaths reference computation, not Arweave tx ids.

## Things that bite

- Query params are strings unless cast: `count+integer=42`, `items+list="a",1`, `cfg+map=k1="v";k2=true`, plus `+float`, `+atom`, `+resolve`. List values follow HTTP Structured Fields (RFC 8941).
- `&key=value` inside the path sets keys on that step's message; parameters after `?` apply to every message in the pipeline.
- Public node hostnames in the docs (`forward.computer`, `push.forward.computer`) change; take the node URL from config, not hard-coded.
- The `Compute Unit` is still a separate NodeJS component behind HyperBEAM for WASM processes (`curl http://localhost:6363`); memory errors there are tuned with `PROCESS_WASM_MEMORY_MAX_LIMIT` and `GC_INTERVAL_MS`.
- Build guides moved to the AO Cookbook ("Using aos with HyperBEAM", "Using aoconnect with HyperBEAM", "Migration Guide"); the HyperBEAM site keeps protocol and node-operator docs.

## Fetch the docs

```bash
python tools/docslice.py 34 36 37 180 179
```

Live: `https://hyperbeam.arweave.net` (`llms.txt`, `llms-full.txt` on its "Fuel Your LLM" page).
