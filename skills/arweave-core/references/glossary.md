# Curated permaweb glossary

Source docs: 1 (Permaweb Glossary, ~10k words), 74 (ar.io glossary), 177/181 (HyperBEAM glossaries). Only terms an agent is likely to misread. Full text: `python tools/docslice.py 1 74`.

## Storage (Arweave)

| Term | Meaning |
|---|---|
| Blockweave | Each block links the previous block and a random older one; miners must store old data to mine |
| SPoRA | Succinct Proofs of Random Access, Arweave's mining: proof of storage plus a VDF clock |
| Endowment | Upfront fee pool (sized for ~200 years, 20 replicas) that pays miners over time, assuming ~38%/yr storage cost decline |
| Winston | 10^-12 AR |
| Mempool | Broadcast but unmined transactions |
| Seeding | Propagating new transactions and chunks to miners |
| ANS-### | Arweave Network Standards (ANS-104 = bundles) |
| UDL | Universal Data License, on-chain licensing via `License` tags |

## Access (ar.io)

| Term | Meaning |
|---|---|
| Gateway | ar.io node serving Arweave data over HTTP: retrieve, cache, index, resolve ArNS, verify |
| GAR | Gateway Address Registry: protocol list of joined gateways, input to observer selection and rewards |
| Observer | Gateway selected in an epoch to test peers' ArNS resolution and report |
| OIP | Observation and Incentive Protocol: observation, weights, reward distribution |
| Epoch | Protocol time window (daily). Pipeline: `create_epoch → tally_weights → prescribe_epoch → save_observations → distribute_epoch → close_epoch` |
| Cranker | Anyone submitting Solana transactions that advance lazy protocol steps |
| Operations address | Second Solana key allowed to update gateway metadata, not stake or keys |
| Protocol balance | Protocol-controlled ARIO pool funding rewards |
| Vault | Time-locked ARIO balance (start, optional end); some revocable |
| Index sharing | Gateways publish signed index bands (`/ar-io/indexes`) over HTTP or BitTorrent so others can locate data items in bundles |
| Root transaction | L1 transaction containing a data item |
| winc | Turbo credit unit; not Winston |
| PDA / Program ID / CPI | Solana concepts used by the ar.io programs (`ario-core`, `ario-gar`, `ario-arns`) |

## Names

| Term | Meaning |
|---|---|
| ArNS | Ar.io Name System: `name` → tx id, served as `name.<gateway>` and `ar://name` |
| ANT | Ar.io Name Token: owns the name's records. Now a Metaplex Core NFT on Solana (older docs: an AO process) |
| Undername | Sub-record written with underscore: `blog_name.ar.io`; `@` is the root record |
| Primary name | Name set as a wallet's display identity |
| Lease / permabuy | Rent yearly (extendable by anyone), or own permanently |

## Compute (AO)

| Term | Meaning |
|---|---|
| Process | Actor with its own state = log of messages on Arweave plus an init data item |
| Message | ANS-104 data item addressed to a process |
| MU / SU / CU | Messenger Unit (relays), Scheduler Unit (assigns ordered slots), Compute Unit (evaluates state) |
| Holographic state | State implied by the message log, not stored |
| Handler | `Handlers.add(name, pattern, fn)` entry reacting to matching messages |
| Assignment | Making an existing message or Arweave tx part of a process's schedule |
| Cron | Scheduled ticks delivered to a process |
| Authority | Address a process trusts to deliver messages |
| Bootloader / On-Boot | Code evaluated at spawn from Data or a tx id |
| WeaveDrive | AOP-5 virtual file system to read Arweave data from a process; needs attestors |
| dryrun | Read-only evaluation without committing; deprecated for HyperBEAM in favor of `~patch@1.0` |
| Armstrong | 10^-12 AO |
| Legacynet | Original AO testnet (2024-02-27) |

## Compute (HyperBEAM / AO-Core)

| Term | Meaning |
|---|---|
| AO-Core | Protocol where everything is a message; devices interpret messages; hashpaths memoize computation |
| Device | Named interpreter of a message, written `~name@version` (`~process@1.0`, `~meta@1.0`, `~wasm64@1.0`, `~lua@5.3a`, `~patch@1.0`, `~relay@1.0`, `~snp@1.0`, `~p4@1.0`, `~simple-pay@1.0`, `~faff@1.0`, `~json-iface@1.0`, `~scheduler@1.0`, `~stack@1.0`, `~compute-lite@1.0`) |
| Hashpath | 32-byte verifiable reference to a computation tree |
| Path | URL-style chain of messages applied to a base message |
| TABM | Type Annotated Binary Message, the internal format codecs convert to and from |
| Codec | Converter between TABM and a wire format (ANS-104, HTTP signatures, JSON, flat) |
| `~flat@1.0` | `key: value` per line format used for node config |
| TEE | Trusted Execution Environment; `~snp@1.0` proves a node runs inside one |
| Checkpoint | Saved process state to resume from |
