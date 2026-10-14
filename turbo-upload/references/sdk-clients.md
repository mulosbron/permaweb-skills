# Turbo SDK clients

Source docs: 2 (TurboAuthenticatedClient), 127 (TurboUnauthenticatedClient), 91 (TurboFactory), 228 (Logging), 6 (signers).

## Factory

```ts
import { TurboFactory } from '@ardrive/turbo-sdk';       // Node
import { TurboFactory } from '@ardrive/turbo-sdk/web';   // browser bundle

TurboFactory.unauthenticated({ token?, gatewayUrl? });   // prices, rates, upload pre-signed items
TurboFactory.authenticated({ signer } | { privateKey, token } | { walletAdapter, token });
TurboFactory.setLogLevel('debug');                       // winston logger
```

### Signers by wallet

| Wallet | Construction |
|---|---|
| Arweave JWK (Node) | `{ privateKey: jwk }` or `{ signer: new ArweaveSigner(jwk) }` |
| Wander / ArConnect (browser) | `{ signer: new ArconnectSigner(window.arweaveWallet) }` after `arweaveWallet.connect(['ACCESS_ADDRESS','ACCESS_PUBLIC_KEY','SIGN_TRANSACTION','SIGNATURE'])` |
| EVM private key (Node) | `{ signer: new EthereumSigner('0x...'), token: 'ethereum' \| 'base-eth' \| 'pol' \| 'base-usdc' ... }` |
| MetaMask / injected (browser) | `{ signer: new InjectedEthereumSigner({ getSigner: () => ({ signMessage }) }), token }` (`@dha-team/arbundles`, peer dep of the SDK) |
| ethers BrowserProvider | `new InjectedEthereumSigner({ getSigner: () => ethersSigner })` |
| wagmi | wrap `signMessage(config, { message: { raw } })`; set `signer.publicKey` by recovering it from a signed message with viem `recoverPublicKey` |
| Solana secret key | `{ privateKey: bs58.encode(secretKey), token: 'solana' \| 'ario' \| 'solana-usdc' }` |
| Phantom (browser) | `{ walletAdapter: { publicKey, signMessage: async m => (await provider.signMessage(m)).signature }, token: 'solana' }` |

`signer.getNativeAddress()` returns the address for the signer's chain; `signer.getPublicKey()` works for every signer type.

## Unauthenticated client (also available on authenticated)

| Method | Returns / notes |
|---|---|
| `getSupportedCurrencies()`, `getSupportedCountries()` | fiat top-up options |
| `getFiatToAR({ currency })` | raw oracle rate |
| `getFiatRates()` | `{ winc, fiat: { usd, eur, ... per GiB }, adjustments }` |
| `getWincForFiat({ amount: USD(100) })` | `{ winc, actualPaymentAmount, quotedPaymentAmount, adjustments }` |
| `getWincForToken({ tokenAmount })` | `{ winc, actualTokenAmount, equivalentWincTokenAmount }` |
| `getFiatEstimateForBytes({ byteCount, currency: 'usd' })` | `{ byteCount, amount, currency, winc }` |
| `getTokenPriceForBytes({ byteCount })` | `{ tokenPrice }` in the client's token |
| `getUploadCosts({ bytes: [n, ...] })` | `[{ winc, adjustments }]`, `winc` is a string |
| `getFreeStatus(address?)` | `{ bytesRemaining }`; `null` = unlimited, `0` = free tier disabled |
| `uploadSignedDataItem({ dataItemStreamFactory, dataItemSizeFactory, signal?, events? })` | upload an item you signed yourself |
| `createCheckoutSession({ amount: USD(10), owner })` | Stripe `{ url, winc, paymentAmount, ... }`; promo codes need authenticated client |
| `submitFundTransaction({ txId })` | credit a transfer you already sent to the Turbo wallet |
| `getX402PriceForDataItem({ byteCount, network? })` | price of a SIGNED item (`usdcAmount`) |
| `getX402PriceForRawData({ byteCount, tagCount, contentType })` | price plus `overhead`, `estimatedDataItemSize` |

## Authenticated client only

| Method | Notes |
|---|---|
| `getBalance()` | `{ winc, controlledWinc, ... }` for the signer |
| `getPaymentHistory({ limit (1-100, default 50), cursor? })` | `{ payments, hasMore, cursor }`; items typed `crypto` or `fiat` |
| `upload({ data, dataItemOpts?, signal?, events?, fundingMode?, chunking opts })` | any data type |
| `uploadFile({ file } \| { fileStreamFactory, fileSizeFactory }, ...)` | `file` may be a browser File or a Node path |
| `uploadFolder({ folderPath } \| { files }, dataItemOpts?, manifestOptions?, manifestDataItemOpts?, folderIndex?, maxConcurrentUploads?, throwOnFailure?, events? })` | returns `{ manifest, fileResponses, manifestResponse, folderIndexSummary? }` |
| `uploadRawX402Data({ data, maxMUSDCAmount? })` | raw bytes, Turbo's EVM signer signs; under 105 KiB works unauthenticated |
| `topUpWithTokens({ tokenAmount, feeMultiplier?, turboCreditDestinationAddress? })` | sends the token transfer and submits it |
| `shareCredits(...)`, `revokeCredits({ revokedAddress })`, `getCreditShareApprovals()` | see `credits-and-payments.md` |
| `getArNSPriceForName({ intent, name, type, years })`, `buyArNSName({ name, owner, type, years })` | SDK >= 2.1.0; quote `wincTotal`, not `winc` |

### `dataItemOpts`

`{ tags?: {name,value}[], target?, anchor?, paidBy?: string[] }`.

### Events

Single upload: `onProgress({ totalBytes, processedBytes, step: 'signing' | 'upload' })`, `onError({ error, step })`, `onSigningProgress`, `onSigningError`, `onUploadProgress`, `onUploadError`, `onUploadSuccess`.

Folder: per file `onFileStart`, `onFileProgress`, `onFileComplete({ id })`, `onFileError`; aggregate `onFolderProgress({ processedFiles, totalFiles, processedBytes, totalBytes, currentPhase })`, `onFolderError`, `onFolderSuccess`.

### Token amount helpers

`WinstonToTokenAmount`, `ARIOToTokenAmount`, `USDCToTokenAmount`, `ETHToTokenAmount`, `POLToTokenAmount`, `SOLToTokenAmount`, and `USD(n)` for fiat. Amounts are in the token's smallest unit.
