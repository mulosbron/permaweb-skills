# ao Standard Token

Source docs: 59 (Token Blueprint, full code), 44 (Building a Token), 57 (Crafting a Token tutorial).

## State

```lua
local bint = require('.bint')(256)
local json = require('json')
Variant = "0.0.3"
Denomination = Denomination or 12
Balances = Balances or { [ao.id] = tostring(bint(10000 * 10 ^ Denomination)) }
TotalSupply = TotalSupply or tostring(bint(10000 * 10 ^ Denomination))
Name = Name or 'Points Coin'; Ticker = Ticker or 'PNTS'; Logo = Logo or '<tx id>'
```

## Transfer (blueprint logic, cleaned up)

```lua
Handlers.add('transfer', 'Transfer', function(msg)
  assert(type(msg.Recipient) == 'string', 'Recipient is required!')
  assert(type(msg.Quantity) == 'string', 'Quantity is required!')
  local qty = bint(msg.Quantity)
  assert(bint.__lt(0, qty), 'Quantity must be greater than 0')
  Balances[msg.From] = Balances[msg.From] or '0'
  Balances[msg.Recipient] = Balances[msg.Recipient] or '0'
  if qty <= bint(Balances[msg.From]) then
    Balances[msg.From] = tostring(bint(Balances[msg.From]) - qty)
    Balances[msg.Recipient] = tostring(bint(Balances[msg.Recipient]) + qty)
    if not msg.Cast then
      local debit  = { Action = 'Debit-Notice',  Recipient = msg.Recipient, Quantity = msg.Quantity }
      local credit = { Target = msg.Recipient, Action = 'Credit-Notice', Sender = msg.From, Quantity = msg.Quantity }
      for k, v in pairs(msg) do if string.sub(k, 1, 2) == 'X-' then debit[k] = v; credit[k] = v end end
      msg.reply(debit); Send(credit)
    end
  else
    msg.reply({ Action = 'Transfer-Error', ['Message-Id'] = msg.Id, Error = 'Insufficient Balance!' })
  end
end)
```

Other handlers (from the blueprint): `info` (`msg.reply` with Name/Ticker/Logo/Denomination), `balance`, `balances` (`json.encode(Balances)`), `mint` (`msg.From == ao.id` only, updates `TotalSupply`), `totalSupply` (`Total-Supply`), `burn`.

## Calling a token

From aos:

```lua
Send({ Target = TOKEN, Action = "Transfer", Recipient = to, Quantity = "1000000000000" })
Send({ Target = TOKEN, Action = "Balance", Recipient = who })
```

From another process accepting payment:

```lua
Handlers.add("Paid", function(msg)
  return msg.Action == "Credit-Notice" and msg.From == PaymentToken
     and bint(msg.Quantity) >= bint(Price) and "continue"  -- or true
end, function(msg)
  Paid[msg.Sender] = true
end)
```

Use `X-` tags on the Transfer (`X-Order-Id`) to correlate a payment with an order; they arrive on the Credit-Notice.

## Review checklist

- [ ] All quantities `bint`, stored as strings.
- [ ] Every mutating handler asserts inputs before changing state.
- [ ] Mint/admin gated on `msg.From`.
- [ ] No negative or zero transfers; no self-transfer side effects.
- [ ] Error replies use `msg.reply` (go to the actual sender).
- [ ] `Denomination` matches what wallets and UIs assume.
- [ ] Balances published for readers via `~patch@1.0`, not dryrun.
