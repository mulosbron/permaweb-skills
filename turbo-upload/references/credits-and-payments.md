# Turbo Credits and payments

Source docs: 25 (Paying for Uploads), 88 (Credit Sharing), 2 (top-up, on-demand, x402), 24, 80.

## Units

- AR divides into **Winston** (10^12 per AR).
- Turbo Credits are counted in **winc** (Winston Credits). A credit is a 1:1 claim on Arweave upload power; it cannot be traded, only spent or shared.
- No account and no subscription: any wallet buys credits up front and spends them per upload.

## What it costs

Three charges only:

1. **Storage rate** per byte (quoted per GiB), pegged to Arweave storage price.
2. **Per-item fee**, pegged at USD 0.00002 per data item (one per file). Read live from `perDataItemFeeWinc` in `/v1/rates`.
3. **Infrastructure fee** taken out of each top-up (a 35% fee means a USD 100 top-up buys USD 65 of credits). Read it live from the `fees` array of `GET /v1/price/:currency/:amount`.

Free tier: items up to 105 KiB, against a 10 MiB lifetime allowance per wallet and per subnet. It never resets.

## Buying credits

| Path | How |
|---|---|
| Web | `console.ar.io/topup` (fiat or crypto); `app.ardrive.io` (fiat, Arweave wallets) |
| SDK | `topUpWithTokens({ tokenAmount, turboCreditDestinationAddress? })`, or `createCheckoutSession` for Stripe |
| CLI | `turbo top-up --token base-usdc --amount 1`, `turbo balance`, `turbo free-status`, `turbo payment-history --limit 25` |
| HTTP | `payment.ardrive.io/api-docs` |

Supported tokens: AR, ETH (L1 and Base), SOL, POL, ARIO (SPL on Solana, pay with a Solana key), USDC (Ethereum, Base, Polygon, Solana). Credits can be sent to any supported wallet type via the destination address.

`$ARIO` top-up without a destination credits the base58 public key of the paying Solana key, the same account `getBalance()` reads.

## Just-in-time funding

Pay at upload time instead of pre-funding. Supported: ARIO, SOL, USDC (Solana), ETH (Base), USDC (Base), POL. Not AR, ETH L1, or fiat.

```ts
await turbo.upload({ ...params, fundingMode: new OnDemandFunding({
  maxTokenAmount: ARIOToTokenAmount(500), topUpBufferMultiplier: 1.1 }) });
```

## x402

HTTP 402 based JIT payment in USDC on Base. Install `x402-fetch`.

```ts
const turbo = TurboFactory.authenticated({ signer, token: 'base-usdc' });
await turbo.uploadFile({ ...params, fundingMode: new X402Funding({ maxMUSDCAmount: 1_000_000 }) }); // max 1 USDC
```

- Large items are chunked and paid when the upload is created; small items are buffered so `Content-Length` can be priced.
- Price without sending: `getX402PriceForDataItem({ byteCount })` for signed items, `getX402PriceForRawData({ byteCount, tagCount, contentType })` for raw data.
- `network` defaults to `base`; use `base-sepolia` against a testnet service.

## Credit sharing

- The owner creates an approval (signed data item) for a recipient address, a winc amount, and an optional expiry in seconds: `shareCredits`, `revokeCredits({ revokedAddress })`, `getCreditShareApprovals()`.
- Shared credits cannot be re-shared. The owner cannot spend them while the approval lives. Revoked or expired remainder returns to the owner.
- Recipient pays with them by sending `x-paid-by` (SDK: `dataItemOpts.paidBy: [ownerAddress]`). The SDK never uses approvals without `paidBy`.
- CLI: `share-credits`, `revoke-credits`, `list-shares`, `--paid-by`, `--ignore-approvals`, `--use-signer-balance-first`. The CLI uses approvals automatically.
- Typical uses: org treasury funding employees, trial upload budgets, giving an agent a capped budget without its key.

## Buying ArNS names with credits

Credits also buy, extend and upgrade ArNS names (SDK >= 2.1.0). Buying mints the ANT (a Solana asset) and registers the name in one step; the owner signs once and needs no SOL.

```ts
const owner = solanaOwnerSigner(bs58SolanaSecretKey);
const price = await turbo.getArNSPriceForName({ intent: 'Buy-Name', name: 'my-name', type: 'lease', years: 1 });
const { antId, messageId } = await turbo.buyArNSName({ name: 'my-name', owner, type: 'lease', years: 1 });
```

Use `wincTotal` from the price quote. Extending, upgrading and adding undernames need no owner signature. See `../../arns/SKILL.md`.
