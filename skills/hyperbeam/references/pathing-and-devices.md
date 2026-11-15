# Paths and devices

Source docs: 34 (Pathing), 36 (Core Capabilities), 37 (AO-Core), 180 (Intro), 179 (Dev FAQ), 73 (cookbook welcome), 1/177 (glossary).

## Four principles

1. **Everything is a message.** Call any key of a message by name; its device decides how. Default device `message@1.0` returns literal values.
2. **Paths are pipelines.** Each `/segment` is a request applied to the previous result. `&key=value` sets keys inline.
3. **`~x@y` applies a request as if the base message had device `x@y`.**
4. **The last message is the HTTP response**, signed against the hashpath that produced it.

## Anatomy

```
https://forward.computer/<pid>~process@1.0/compute/cache/books
        └ node (signs)   └ load msg <pid>, interpret with process@1.0
                                         └ key "compute" (latest known state)
                                                 └ navigate into state map
```

| Key on `~process@1.0` | Meaning |
|---|---|
| `now` | compute real-time state including unprocessed messages |
| `compute` | serve latest computed state (faster) |
| `compute/<field>/...` | navigate state map |
| `compute/cache/<key>` | values published with `~patch@1.0` |

## Type casting in URLs

`key+type=value`:

| Example | Result |
|---|---|
| `count+integer=42` | `42` |
| `items+list="apple",1,"banana"` | `[<<"apple">>, 1, <<"banana">>]` |
| `config+map=key1="val1";key2=true` | nested map |
| `+float`, `+atom`, `+resolve` | float, atom, resolve another path |

`GET /~message@1.0&greeting="Hello"&count+integer=42/count` → `42`.

## Devices you will meet

| Device | Purpose |
|---|---|
| `~process@1.0` | persistent shared execution (scheduler + execution device, `push` to other processes) |
| `~patch@1.0` | process publishes selected state for direct GET (replaces dryrun) |
| `~lua@5.3a` | run Lua over a message/state (`&module=<tx id>`), pipeline transforms |
| `~wasm64@1.0` | run WASM (WAMR); Rust/C/C++ modules |
| `~json@1.0` | serialize output as JSON (`serialize~json@1.0`) |
| `~message@1.0` | default; literal key lookup, build transient messages |
| `~meta@1.0` | node info/config (`/~meta@1.0/info`) |
| `~relay@1.0` | relay messages to other nodes/HTTP |
| `~scheduler@1.0` | linear hashpath ordering |
| `~stack@1.0` | run several devices as one |
| `~compute-lite@1.0`, `~json-iface@1.0` | legacy AO process compatibility |
| `~snp@1.0` | AMD SEV-SNP TEE attestation (`/~snp@1.0/generate`, `/verify`) |
| `~p4@1.0` + `~simple-pay@1.0` / `~faff@1.0` | metering and payment for node operators |
| `~router@1.0`, `~greenzone@1.0`, `~node-process@1.0`, `~hyperbuddy@1.0` | routing, trusted node groups, node-local processes, UI |

Custom devices are Erlang modules; NIFs (C/Rust) for raw performance.

## Message formats

Codecs convert between wire formats (ANS-104, HTTP Signed Messages RFC 9421, JSON, flat) through TABM (Type Annotated Binary Messages). HTTP signatures authenticate node config changes and attest computation results.
