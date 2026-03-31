# API Reference

## Worker Loader Binding

Configured as `env.LOADER` via `worker_loaders` in wrangler config.

### `load(code: WorkerCode): WorkerStub`

Creates a fresh Dynamic Worker from the provided `WorkerCode`. Each call creates a new Worker — no caching.

Use for one-time code execution (AI-generated tool calls, code mode).

### `get(id: string, callback: () => Promise<WorkerCode>): WorkerStub`

Loads a Worker with the given ID. The runtime caches isolates — if the same ID is requested again, the existing isolate may be reused.

The callback only runs when the system needs to create a new isolate and doesn't have the code cached. It's async, so code can be loaded from remote storage.

**ID rules:**
- Same ID + same code = potential isolate reuse (saves startup cost)
- Different code requires a new ID
- Suggested format: `<name>:<version>` or content hash
- Random ID = no caching (equivalent to `load()`)

Returns a `WorkerStub` synchronously. If the Worker isn't loaded yet, requests wait for loading. If loading fails, requests throw.

**No isolation guarantee between requests** — even with the same `WorkerStub`, requests may execute in different isolates. The callback may be called multiple times.

## WorkerCode

Object passed to `load()` or returned by `get()` callback.

### `compatibilityDate: string` (required)

Cloudflare compatibility date. Same as `compatibility_date` in wrangler config.

### `compatibilityFlags: string[]` (optional)

Additional compatibility flags. Same as `compatibility_flags` in wrangler config.

### `allowExperimental: boolean` (optional)

Permits experimental compatibility flags. The parent Worker must itself have the `"experimental"` flag set. Cannot be used in production.

### `mainModule: string` (required)

Entry module name. Must exist as a key in `modules`.

### `modules: Record<string, string | Module>` (required)

Module name to content mapping. String values use file extension for type (`.js` or `.py`).

Object values for explicit typing:
- `{js: string}` — ES module
- `{cjs: string}` — CommonJS module
- `{py: string}` — Python module (much slower startup than JS)
- `{text: string}` — Importable string value
- `{data: ArrayBuffer}` — Importable ArrayBuffer
- `{json: object}` — Importable JSON-serializable object (transferred as parsed object, not serialized)

### `globalOutbound: ServiceStub | null` (optional)

Controls network access for the Dynamic Worker.

- **Omitted**: inherits parent's network access (usually full Internet)
- **`null`**: completely blocks `fetch()` and `connect()` — they throw exceptions
- **ServiceStub**: routes all `fetch()` and `connect()` calls through the specified service binding

Use `ctx.exports` loopback bindings to customize per-sandbox with `ctx.props`.

### `env: object` (optional)

Custom environment/bindings for the Dynamic Worker. Serialized and transferred directly as the Worker's `env`.

May contain:
- Structured-clonable types
- Service Bindings (including `ctx.exports` loopback bindings)

Custom RPC bindings are created by defining `WorkerEntrypoint` classes and passing them via `ctx.exports`.

### `tails: ServiceStub[]` (optional)

Tail Workers that observe console logs, errors, and request metadata. Tail events are delivered after the Dynamic Worker completes a request. Reference tail workers via `ctx.exports`:

```javascript
tails: [ctx.exports.LogTailer({ props: { workerId } })]
```

## Supported Languages

- **JavaScript**: ES modules and CommonJS
- **Python**: Supported but significantly slower startup — prefer JS for one-off code

No build step — TypeScript must be compiled to JS before passing to `load()`/`get()`. Use `@cloudflare/worker-bundler` for TypeScript compilation and npm dependency resolution.
