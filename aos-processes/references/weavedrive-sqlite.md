# WeaveDrive, SQLite and the dev-cli

Source docs: 64 (WeaveDrive), 65 (SQLite), 66 (AO Dev-Cli), 1 (glossary: WeaveDrive, Attestor, AO-SQLite).

## WeaveDrive (AOP-5)

Virtual file system that lets a process read Arweave data items deterministically (lazy loading, caching, attestation).

- Availability mode "Assignments": spawn the process with an **Attestor** wallet. The process can read data items for which that attestor has published an attestation data item.
- Steps: upload data (cookbook uses `arx`), upload an attestation signed by the attestor wallet referencing the data item id, wait for ~20 confirmations (data is "on Arweave" only after that), spawn the aos process with WeaveDrive enabled and the attestor set, then read.
- The attestor address at spawn must equal the wallet that signed the attestation.

The exact spawn flags and Lua read calls were in code blocks lost from this snapshot; fetch the live cookbook page before implementing.

## SQLite in a process

```bash
aos mydb --sqlite
```

```lua
.load-blueprint apm
apm.install('@rakis/dbAdmin')           -- helper over sqlite3
local sqlite3 = require('lsqlite3')
Db = Db or sqlite3.open_memory()
dbAdmin = require('@rakis/dbAdmin').new(Db)
dbAdmin:exec([[CREATE TABLE IF NOT EXISTS Comments (ID INTEGER PRIMARY KEY AUTOINCREMENT, Asset TEXT, User TEXT, Body TEXT);]])
dbAdmin:select('SELECT * FROM Comments')
```

The database lives in process memory and is rebuilt by replay; keep schema creation idempotent (`IF NOT EXISTS`, `Db = Db or ...`). Verify package and require names against the installed apm package.

## AO dev-cli (build WASM modules)

- Requires Docker and an Arweave keyfile (`npx -y @permaweb/wallet > wallet.json`).
- Builds Lua or C/C++ (since 0.1.x any pure C/C++) into ao WASM modules; then publish the module and spawn processes from it.
- `config.yml`: `preset` (default `md`), `stack_size` (32MB default, multiple of 64), `initial_memory` (48MB, > stack), `maximum_memory` (256MB), `extra_compile_args` (emcc), `keep_js` (false).
- Native libs: put emcc-compiled `.a/.so/.o` in `/libs`; C includes headers directly, Lua can `require` bound libs.
- Memory errors at runtime on a CU: raise `PROCESS_WASM_MEMORY_MAX_LIMIT` / tune `GC_INTERVAL_MS` on the CU, or choose a larger preset.
