# Turbo HTTP API

Source docs: 75, 90, 92, 93, 142, 152, 215.

One host serves both halves: `https://turbo.ardrive.io`. Upload routes are at the root, payment routes under `/v1`. Legacy hosts `upload.ardrive.io` and `payment.ardrive.io` map to the same services. Full OpenAPI: `https://payment.ardrive.io/api-docs`.

## Authentication

Signed routes take `x-signature` (signature over the request data concatenated with the nonce) and `x-nonce`, or a previously obtained JWT. The address is read from the signature, never from a query parameter, so self-scoped routes cannot be used for other wallets.

## Upload service pricing

| Route | Returns |
|---|---|
| `GET /price/:token/:byteCount` | winc to upload a data item of that size |
| `GET /price/x402/data-item/:token/:byteCount` | exact USDC for a complete signed ANS-104 item |
| `GET /price/x402/data/:token/:byteCount?tags=3&contentType=image%2Fpng` | USDC for raw data, including ANS-104 overhead |

x402 token format `{currency}-{network}` or `{network}-{currency}`: `usdc-base` / `base-usdc` on by default; Base Sepolia, Ethereum and Polygon USDC only when the operator enables them. Fee markup defaults to 15%.

Raw-data overhead estimate: signature 512 B + owner 512 B + headers ~80 B + ~64 B per tag. x402 raw uploads add system tags `Bundler`, `Upload-Type: raw-data-x402`, `Payer-Address`, `X402-TX-Hash`, `X402-Payment-ID`, `X402-Network`, `Upload-Timestamp`.

## Payment service (`/v1`)

| Route | Purpose |
|---|---|
| `GET /v1/price/bytes/:byteCount` | winc for a byte count |
| `GET /v1/price/:type/:amount` | winc quote for fiat or token amount (smallest unit: USD 10 = 1000, 1 AR = 10^12); `fees` array shows infra fee |
| legacy Arweave-compatible price route | plain-string winc, no adjustments (for ArConnect-era tools) |
| `GET /v1/rates` | includes `perDataItemFeeWinc` |
| balance (signed or `?address=`) | current winc; Ethereum addresses normalized to EIP-55 |
| free-tier route (`?address=`) | remaining free bytes; never 404s for new wallets |
| top-up quote `/:method/:address/:currency/:amount` | `payment-intent` or `checkout-session`; `promoCode`, `uiMode`, `returnUrl`, `successUrl`, `cancelUrl` |
| `POST /v1/account/balance/:token` `{ tx_id }` | credit a transfer already sent to the Turbo wallet; re-posting an already credited tx returns the existing record |
| `GET /v1/redeem?destinationAddress=&id=&email=` | redeem emailed gift credits |
| `GET /v1/account/approvals?payingAddress=&approvedAddress=` | approvals between two wallets |
| `GET /v1/account/approvals/get?userAddress=` | `{ givenApprovals, receivedApprovals }` |

`POST /v1/account/balance/:token` tokens: `arweave`, `ethereum`, `solana` (alias `ed25519`), `matic` (alias `pol`), `kyve`, `base-eth`, `ario`, `usdc`, `base-usdc`, `solana-usdc`. A deployment may accept fewer (`ACCEPTED_FUNDING_TOKENS`); others return 400 "Token not supported".

SPL payments (`ario`, `solana-usdc`) must contain exactly one transfer of the configured mint into the associated token account derived from the recipient wallet in `GET /info`. An `spl-memo` of `turboCreditDestinationAddress=<address>` credits another account.

Responses for a posted payment: `creditedTransaction`, `pendingTransaction`, or `failedTransaction` with `failureReason`.
