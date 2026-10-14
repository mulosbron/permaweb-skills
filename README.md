# Permaweb Skills

Skill files that turn an AI coding agent into a permaweb developer: upload to Arweave with Turbo, read and verify data through ar.io gateways and Wayfinder, name it with ArNS, model files with ArFS, build AO processes in Lua, talk to them from JavaScript, read their state over HyperBEAM, and run an ar.io gateway.

Built from a 232-document snapshot of docs.ar.io, the AO Cookbook, HyperBEAM docs and the Permaweb Glossary (`_source/permaweb-docs-2026-10-13.llms.txt`, generated 2026-10-13). Each file holds what a model gets wrong or cannot know on its own: current API shapes, units, traps, contradictions between doc pages, and where to look things up.

## Install

Copy the folder where your agent looks for `AGENTS.md` (project or global agents directory):

```bash
cp -r permaweb-skills/ my-project/.agents/
```

Agents that read `AGENTS.md` (Claude Code, Codex, Cursor, Windsurf and others) get the skill table and load individual `SKILL.md` files on demand. References under `*/references/` load only when a skill points to them.

## Skills

| Skill | Use it for |
|---|---|
| `arweave-core/` | Stack overview, units, tags, manifests, normalized addresses, glossary |
| `turbo-upload/` | Turbo SDK/CLI/API uploads, credits, x402, browser setup |
| `arweave-data-access/` | Gateway HTTP API, GraphQL, verification, sandboxing |
| `wayfinder/` | `ar://` routing and verification (core + React) |
| `arns/` | Names, ANTs, records, undernames, pricing |
| `ario-sdk/` | `@ar.io/sdk` on Solana: gateways, staking, vaults, epochs, token |
| `ario-gateway-operator/` | Running ar-io-node: env, filters, OIP, sidecars, troubleshooting |
| `arfs/` | ArFS entities, drive state, private drives, v0.15 upgrade |
| `aos-processes/` | Lua processes with aos: handlers, messaging, modules |
| `aoconnect/` | JS client for AO messages, spawns, assignments |
| `ao-blueprints/` | Token spec and blueprints, games and bots |
| `hyperbeam/` | AO-Core paths, devices, `~patch@1.0` reads, node operation |

## Example prompts

**Ship a site**

> Build this Vite app with relative paths, upload `dist/` with Turbo using an incremental folder index, then point the `preview` undername of my ArNS name at the new manifest. Show me the cost before uploading.

**Find my data**

> Write a function that lists every JSON document my app uploaded (App-Name `LitBook-v1`, owner is a Solana wallet), newest first, with cursor pagination, and fetches each one through Wayfinder with hash verification.

**AO process with HTTP reads**

> Review `LitBook.lua`. Writes must stay messages; move every read (`GetBook`, `ListBooks`) to `~patch@1.0`-published state and give me the HyperBEAM URLs the frontend should GET. Flag any getter that mutates state.

**Token**

> Create a standard ao token with bint math, owner-only mint, and Credit-Notice handling in a shop process that marks orders paid by `X-Order-Id`.

**Gateway operator**

> My gateway failed the last two epochs with `dataHashDigest mismatch`. Read my `.env` and the observer report and tell me what to change. Do not restart anything.

## Layout

```text
permaweb-skills/
├── AGENTS.md                 # skill table, how to work, cross-cutting rules, boundaries
├── README.md
├── _source/
│   ├── permaweb-docs-2026-10-13.llms.txt   # full snapshot (1.2 MB)
│   └── doc-index.md          # doc no → title → lines → source URL, grouped by skill
├── tools/
│   └── docslice.py           # print docs by number, --find term, --list
├── arweave-core/             # SKILL.md + references/{glossary,bundles-and-tags,manifests,addresses-and-signers}.md
├── turbo-upload/             # references/{sdk-clients,browser-setup,credits-and-payments,rest-api,advanced-uploading}.md
├── arweave-data-access/      # references/{graphql,gateway-api,verification-and-sandboxing}.md
├── wayfinder/                # references/{core,react}.md
├── arns/                     # references/{ants-and-records,registration-and-pricing}.md
├── ario-sdk/                 # references/{api-surface,token}.md
├── ario-gateway-operator/    # references/{environment-variables,operations,extensions,network-and-oip}.md
├── arfs/                     # references/{entity-types,privacy-and-upgrades}.md
├── aos-processes/            # references/{handlers-and-messaging,modules,lua-and-cli,concepts,weavedrive-sqlite}.md
├── aoconnect/                # references/api.md
├── ao-blueprints/            # references/{token-spec,blueprints,bots-and-games}.md
└── hyperbeam/                # references/{pathing-and-devices,node-operation}.md
```

## Known gaps in the snapshot

- 18 pages returned 404 at crawl time (hosting guides, ArNS primary-name/undername guides, some Wayfinder strategy pages, ARIO staking/architecture). They are listed at the end of `_source/doc-index.md`.
- AO Cookbook pages lost most code blocks during extraction; the AO skills say where exact syntax must be confirmed against the live cookbook.
- Some gateway features in the docs need Release 85, marked unreleased at snapshot time.

## Updating

Regenerate the snapshot, replace `_source/permaweb-docs-*.llms.txt`, rebuild `doc-index.md`, then diff the docs each skill cites. Before adding a line, ask whether a capable model would get it wrong without it; if not, leave it out. Keep each `SKILL.md` well under 150 lines and its `description` specific enough to trigger only for its job.
