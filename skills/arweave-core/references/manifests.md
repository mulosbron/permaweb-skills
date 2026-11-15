# Path manifests

Source doc: 103 (Manifests).

A manifest is a JSON data item that maps friendly paths to transaction ids so a whole site or app resolves under one id:

```
https://<gateway>/<manifestId>             -> index
https://<gateway>/<manifestId>/js/app.js   -> paths["js/app.js"].id
https://<name>.<gateway>/js/app.js         -> same, via ArNS
```

## Schema

```json
{
  "manifest": "arweave/paths",
  "version": "0.2.0",
  "index":    { "path": "index.html" },
  "fallback": { "id": "<404 page tx id>" },
  "paths": {
    "index.html":          { "id": "<tx id>" },
    "assets/img/logo.png": { "id": "<tx id>" }
  }
}
```

| Field | Rule |
|---|---|
| `manifest` | must be exactly `arweave/paths` |
| `version` | `0.2.0` (adds `fallback`) |
| `index` | `{ path }` (a key in `paths`) or `{ id }`; `id` wins if both are set |
| `fallback` | served when a path is missing; this is how SPAs get client-side routing and how 404 pages work |
| `paths` | keys are relative paths without leading `/` |

Upload it with tag `Content-Type: application/x.arweave-manifest+json`, otherwise gateways serve it as plain JSON.

## Creating one

- `turbo.uploadFolder({ folderPath, manifestOptions: { indexFile: 'index.html', fallbackFile: '404.html' } })` builds and uploads it; the result includes the manifest and its id.
- CLI: `turbo upload-folder --folder-path ./dist --index-file index.html`.
- Manual: build the JSON above and `turbo.upload({ data: JSON.stringify(manifest), dataItemOpts: { tags: [{ name: 'Content-Type', value: 'application/x.arweave-manifest+json' }] } })`.

## Hosting a site

1. Build with **relative asset paths** (`./logo.png`, Vite `base: './'` or `'/'` depending on whether it is served at the root of an ArNS subdomain). Absolute `/assets/...` breaks under `https://<gateway>/<manifestId>/`.
2. SPA routing: use hash routing, or set `fallback` to `index.html`.
3. Upload the folder; point an ArNS name (or undername) at the manifest id (`../../arns/SKILL.md`).
4. Every deploy produces a new manifest id. The ArNS record is the mutable pointer; old versions stay reachable by id forever.

Gateways serve manifest content on a sandboxed subdomain (see `../../arweave-data-access/references/verification-and-sandboxing.md`), so relative URLs and same-origin storage behave per manifest.
