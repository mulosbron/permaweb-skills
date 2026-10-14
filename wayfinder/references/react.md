# @ar.io/wayfinder-react

Source docs: 106, 28 (useWayfinderRequest), 26 (React example), 23.

```bash
npm install @ar.io/wayfinder-react @ar.io/wayfinder-core @ar.io/sdk
npm install -D vite-plugin-node-polyfills   # Buffer, global, process polyfills
```

## Provider

`WayfinderProvider` takes the same options as `createWayfinderClient` as props.

```tsx
<WayfinderProvider
  gatewaysProvider={new NetworkGatewaysProvider({ ario })}
  routingSettings={{ strategy: new FastestPingRoutingStrategy({ timeoutMs: 1000 }) }}
  verificationSettings={{ enabled: true, strict: true }}
>
  <App />
</WayfinderProvider>
```

Create `ario` and strategy instances outside render (module scope or `useMemo`) so the provider is not rebuilt each render.

## Hooks

| Hook | Returns | Use |
|---|---|---|
| `useWayfinderUrl({ txId })` (also ArNS forms) | `{ resolvedUrl, isLoading, error }` | `src`/`href` for media; no byte verification |
| `useWayfinderRequest()` | `request(url, overrides?)` → `Response` | fetch and optionally verify bytes |
| `useWayfinder()` | client context | direct access |

```tsx
function Data({ txId }: { txId: string }) {
  const request = useWayfinderRequest();
  const [data, setData] = useState<ArrayBuffer | null>(null);
  useEffect(() => {
    let cancelled = false;
    request(`ar://${txId}`, { verificationSettings: { enabled: true, strict: true } })
      .then(r => r.arrayBuffer()).then(b => { if (!cancelled) setData(b); });
    return () => { cancelled = true; };
  }, [request, txId]);
  ...
}
```

Render binary as a Blob URL or decode text first; dropping an `ArrayBuffer` into `<pre>` (as some doc snippets do) prints nothing useful.
