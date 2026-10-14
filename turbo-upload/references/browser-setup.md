# Turbo SDK in the browser

Source docs: 4 (Vite), 7 (vanilla HTML), 8 (Next.js), 101 (overview), 11 (SDK intro).

The SDK imports Node modules (`crypto`, `stream`, `buffer`, `process`, and `node:` protocol imports). Bundlers need polyfills; a CDN ES-module import does not.

## Vanilla HTML (no bundler)

```html
<script type="module">
  import { TurboFactory } from "https://esm.sh/@ardrive/turbo-sdk@<exact-version>";
</script>
```

Pin a version in production. `unpkg.com/@ardrive/turbo-sdk@<version>` works too; polyfills are inside the web bundle. Wallet integrations need HTTPS hosting, and CSP must allow the CDN.

## Vite

```bash
npm i @ardrive/turbo-sdk && npm i -D vite-plugin-node-polyfills
```

```js
// vite.config.js
import { nodePolyfills } from 'vite-plugin-node-polyfills';
export default defineConfig({
  plugins: [react(), nodePolyfills({ include: ['crypto','stream','buffer','process'],
                                     globals: { Buffer: true, global: true, process: true } })],
  define: { global: 'globalThis' },
});
```

tsconfig: `"moduleResolution": "Bundler"`, and `"paths": { "buffer/": ["./node_modules/vite-plugin-node-polyfills/shims/buffer"] }` if Buffer types fail. Import from `@ardrive/turbo-sdk/web`.

| Error | Fix |
|---|---|
| `global is not defined` | `define: { global: 'globalThis' }` |
| `process is not defined` | enable `process` in polyfill globals |
| Module resolution errors | `moduleResolution: "Bundler"`, import the `/web` subpath |

## Next.js (webpack)

```bash
npm i -D crypto-browserify stream-browserify process buffer
```

```ts
// next.config.ts, client bundle only
webpack: (config, { isServer, webpack }) => {
  if (!isServer) {
    config.resolve.fallback = { ...config.resolve.fallback,
      crypto: require.resolve('crypto-browserify'), stream: require.resolve('stream-browserify'),
      buffer: require.resolve('buffer'), process: require.resolve('process/browser'),
      fs: false, net: false, tls: false };
    config.plugins.push(new webpack.ProvidePlugin({ process: 'process/browser', Buffer: ['buffer', 'Buffer'] }));
    // Required: rewrite node: imports or the build fails with UnhandledSchemeError
    config.plugins.push(new webpack.NormalModuleReplacementPlugin(/^node:/, (r) => {
      const m = r.request.replace(/^node:/, '');
      r.request = { crypto: 'crypto-browserify', stream: 'stream-browserify', buffer: 'buffer', process: 'process/browser' }[m] || m;
    }));
  }
  return config;
}
```

- Mark every component that touches the SDK `'use client'`; for heavy cases `dynamic(() => import('./Uploader'), { ssr: false })`.
- Create the client inside the component with `useMemo`, never at module level (module level runs during SSR).
- tsconfig `"target": "ES2017"` or newer.
- Next.js 15 route files may export only HTTP method functions; un-export helpers.

| Error | Cause |
|---|---|
| `UnhandledSchemeError: Reading from 'node:stream'` | missing `NormalModuleReplacementPlugin` |
| `Can't resolve 'fs'` | `fs: false` missing in fallback |
| `crypto.getRandomValues is not a function` | crypto polyfill not applied |
| `e.startsWith is not a function` | `EthereumSigner` used with a wallet; use `InjectedEthereumSigner` |
| 400 Invalid Data Item with server signing | public key lost its `04` prefix, string/binary message confusion, or token mismatch |

## Server-side signing for a browser app

When the app pays, keep the key on the server and give the browser a signer whose `signMessage` POSTs to an API route:

- The SDK calls `signMessage` with UTF-8 strings (setup) **and** `Uint8Array` (data). Send `{ signatureData, isHex }` and let the server decode accordingly.
- Return the uncompressed EVM public key with the `04` byte: `publicKey.slice(2)` (drop only `0x`), never `slice(4)`.
- Sign with ethers `Wallet` (EIP-191). `TypedEthereumSigner` from arbundles produces an incompatible signature format.
- Client `token` must equal the server key's chain and the funded account.

## Wallet typing

Declare `window.ethereum` and `window.arweaveWallet` in a `types/wallet.d.ts`; both guides ship the same interface. Always check the wallet object exists before connecting.
