# aos built-in modules

Source docs: 219 (ao), 221 (json), 194 (base64), 195 (crypto), 197 (utils), 229 (pretty), 186, 70, 59 (bint).

Load with `require`: `local json = require('json')`. Globals already present in aos: `ao`, `Handlers`, `Utils`, `Dump`, `Send`, `Spawn`, `Inbox`, `Name`, `Owner`, `Colors`.

## ao

| Member | Use |
|---|---|
| `ao.id` | this process id |
| `ao.send(msg)` | send; returns the message (supports `.receive()`) |
| `ao.spawn(module, msg)` | create a process from a module id |
| `ao.assign({ Processes = {...}, Message = id })` | assign an existing message to processes |
| `ao.log(str\|table)` | output readable by callers |
| `ao.env` | `Process` (Id, Owner, Tags) and `Module` reference objects |
| `ao.authorities` | trusted senders (MU authorities) |

## json

`json.encode(value) -> string`, `json.decode(string) -> table` (throws on invalid JSON; wrap with `pcall` for untrusted input).

## bint (big integers)

```lua
local bint = require('.bint')(256)
local a = bint(Balances[from]); local q = bint(msg.Quantity)
assert(bint.__lt(0, q), 'Quantity must be > 0')
if q <= a then Balances[from] = tostring(a - q) end
```

Store balances as strings; convert with `tostring(bint(x))`; `bint.tonumber(x)` only for small display values.

## utils (also global `Utils`)

Curry-friendly: `map(fn, t)`, `filter(fn, t)`, `reduce(fn, initial, t)`, `find(fn, t)`, `includes(val, t)`, `concat(a, b)`, `reverse(t)`, `keys(t)`, `values(t)`, `prop(name, obj)`, `propEq(name, val, obj)`, `compose(...)`. Validate input types yourself.

## base64

`encode(str, encoder?, usecache?)`, `decode(str, decoder?, usecache?)`, `makeencoder(s62?, s63?, spad?)`, `makedecoder(...)` for URL-safe or custom alphabets. Enable cache for large strings.

## crypto (pure Lua; slow, use sparingly)

| Area | API |
|---|---|
| Digests | `crypto.digest.md2/md4/md5/sha1/sha2_256(stream)`, `sha2_512(str)`, `sha3_256/sha3_512/keccak256/keccak512(str)`, `blake2b(data, outlen?, key?)` → `.asHex()/.asBytes()/.asString()` |
| Ciphers | `crypto.cipher.aes.encrypt(data, key, iv?, mode='CBC', keyLength=128)` (`CBC, ECB, CFB, OFB, CTR`), `decrypt(hexCipher, ...)`; ISSAC, Morus, NORX |
| RNG | ISAAC `random(min?, max?, seed?)` |
| MAC / KDF | `createHmac(stream, keyArray, 'sha1'\|'sha256')`, `pbkdf2(password, salt, iterations, keyLen, digest)` |
| Utils | `crypto.utils.array/stream/hex/queue` converters (`stream.fromString`, `hex.stringToHex`, ...) |

Determinism: seeds must come from message data, or every CU computes a different state. Anything on-chain is public, so don't "encrypt" secrets with keys stored in process state.

## pretty

`require('.pretty').tprint(tbl, indent?)` → formatted string. `Dump(tbl)` is the global shortcut.
