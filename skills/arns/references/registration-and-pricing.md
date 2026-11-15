# Registration and pricing

Source docs: 119 (Name Registration), 217 (Pricing Model), 22 (Access via ArNS), 83, 25 (buying with Turbo credits), 76 (Marketplace).

## Ways to buy

| Path | Payment |
|---|---|
| arns.ar.io | card, Turbo credits, ARIO |
| ar.io Console name checkout | ARIO directly |
| Turbo SDK `buyArNSName({ name, owner: solanaOwnerSigner(key), type: 'lease' \| 'permabuy', years })` | Turbo credits; mints ANT + registers in one purchase; owner signs once, needs no SOL (SDK >= 2.1.0) |
| ar.io SDK `ario.buyRecord({ name, years, ... })` | ARIO or Turbo credits |

Quote first: `turbo.getArNSPriceForName({ intent: 'Buy-Name', name, type, years })` and use `wincTotal`.

## Registration types

- **Lease**: yearly. Anyone with ARIO can extend any active lease or convert it to permabuy (priced as a new permanent purchase).
- **Permabuy**: no expiry. Owner may **return** it to the protocol.
- **Undername capacity**: purchasable for active names. Undernames and capacity expire with the base lease.
- **Reassignment**: a name can be pointed at a different ANT.

Lease end → grace period (renew or convert) → expired → **Returned Name Premium** Dutch auction starting high and decaying to normal price. Returned-name proceeds split between the protocol and the previous owner (for voluntary permabuy returns, between returning owner and protocol balance).

## Validation

| Rule | Detail |
|---|---|
| Characters | `a-z`, `0-9`, `-`, lowercase at submission |
| Dashes | not leading/trailing; not in 1-char names |
| Length | 1 to 51 |
| Forbidden length | exactly 43 (collides with tx ids) |
| Reserved | e.g. `www` |

## Price drivers

- Name length (shorter costs more), lease vs permabuy, lease years, undername count.
- **Demand Factor**: protocol multiplier tracking recent registrations; low demand for long enough steps base fees down.
- **Gateway operator discount**: 20% on registrations, extensions, upgrades and undername purchases for gateways with Gateway Performance Ratio Weight 0.9 and Tenure Weight 1.0. The gateway's operations address can claim it.
- Primary name fee: one undername on a 51-char name of the same type × Demand Factor.

All ArNS revenue goes to the protocol balance, which funds gateway rewards. Exact numbers: arns.ar.io live chart, ar.io Console price table, or SDK simulation. Never copy formulas into app code.
