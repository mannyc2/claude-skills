---
name: dynamic-workers
description: "Cloudflare Dynamic Workers — spin up isolated Workers at runtime to execute code on demand. Use when building sandboxed code execution, AI agent code mode, dynamic worker loaders, or working with env.LOADER, worker_loaders bindings, globalOutbound, WorkerEntrypoint RPC bindings, egress control, or tail workers for dynamic workers. Triggers on: Dynamic Workers, worker loader, env.LOADER.load, env.LOADER.get, WorkerCode, WorkerStub, globalOutbound, sandbox workers, capability-based security, Cap'n Web."
---

# Cloudflare Dynamic Workers

Spin up Workers at runtime to execute arbitrary code in secure, sandboxed environments. Dynamic Workers are the lowest-level primitive for creating on-demand Workers with full control over bindings, network access, and observability.

## Quick Start

Configure the Worker Loader binding in `wrangler.jsonc`:

```jsonc
{
  "worker_loaders": [{ "binding": "LOADER" }]
}
```

Load and run a Dynamic Worker:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const worker = env.LOADER.load({
      compatibilityDate: "2026-01-01",
      mainModule: "index.js",
      modules: {
        "index.js": `
          export default {
            fetch(request) {
              return new Response("Hello from a dynamic Worker");
            },
          };
        `,
      },
      globalOutbound: null, // Block all network access
    });

    return worker.getEntrypoint().fetch(request);
  },
};
```

## Two Loading Modes

### `load(code)` — One-time execution

Creates a fresh Dynamic Worker each time. Best for one-off code execution (AI-generated tool calls, code mode).

```typescript
const worker = env.LOADER.load({ compatibilityDate, mainModule, modules, globalOutbound: null });
```

### `get(id, callback)` — Cached by ID

Reuses warm Workers across requests. The callback only runs if the Worker isn't already loaded. Use a stable ID to avoid extra billing.

```typescript
const worker = env.LOADER.get("my-worker-v1", async () => {
  const code = await env.STORAGE.get("my-worker-v1");
  return { compatibilityDate: "2026-01-01", mainModule: "index.js", modules: { "index.js": code }, globalOutbound: null };
});
```

**ID strategy**: Use `<name>:<version>` or a content hash. Same ID + same code = reused isolate. Different code requires a new ID.

## WorkerCode Object

The object passed to `load()` or returned by the `get()` callback:

| Field | Type | Required | Description |
|---|---|---|---|
| `compatibilityDate` | `string` | Yes | Cloudflare compatibility date |
| `compatibilityFlags` | `string[]` | No | Additional compatibility flags |
| `mainModule` | `string` | Yes | Entry module name (must exist in `modules`) |
| `modules` | `Record<string, string \| Module>` | Yes | Module name to content mapping |
| `globalOutbound` | `ServiceStub \| null` | No | Network access control. `null` = blocked. Omit = inherited. |
| `env` | `object` | No | Custom bindings for the Dynamic Worker |
| `tails` | `ServiceStub[]` | No | Tail Workers for log capture |

### Module Types

String values use file extension for type (`.js` or `.py`). Object values for explicit typing:

- `{js: string}` — ES module
- `{cjs: string}` — CommonJS
- `{py: string}` — Python (slow startup, prefer JS)
- `{text: string}` — Importable string
- `{data: ArrayBuffer}` — Importable binary
- `{json: object}` — Importable object

## Custom Bindings via RPC

Define `WorkerEntrypoint` classes in the parent Worker and pass them to the Dynamic Worker as bindings. This is capability-based security — the Dynamic Worker can only access what you explicitly give it.

```typescript
import { WorkerEntrypoint } from "cloudflare:workers";

export class DatabaseBinding extends WorkerEntrypoint {
  async query(sql: string) {
    // Dynamic Worker calls env.DB.query("SELECT ...") — never sees credentials
    return this.env.D1.prepare(sql).all();
  }
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const worker = env.LOADER.load({
      compatibilityDate: "2026-01-01",
      mainModule: "index.js",
      modules: { "index.js": agentCode },
      env: {
        DB: ctx.exports.DatabaseBinding(), // RPC binding
      },
      globalOutbound: null,
    });
    return worker.getEntrypoint().fetch(request);
  },
};
```

Use `ctx.props` to specialize bindings per-tenant:

```typescript
ctx.exports.ChatRoom({ props: { roomName: "#general", apiKey } })
```

The Dynamic Worker accesses `this.ctx.props` inside the entrypoint.

## Egress Control

Control outbound network access with `globalOutbound`:

- **Block all**: `globalOutbound: null` — `fetch()` and `connect()` throw
- **Inherit parent**: omit `globalOutbound` — full Internet access
- **Intercept**: route through a gateway entrypoint for filtering, credential injection, or auditing

```typescript
export class HttpGateway extends WorkerEntrypoint {
  async fetch(request: Request) {
    const url = new URL(request.url);
    if (!ALLOWED_HOSTS.has(url.hostname)) {
      return new Response("Blocked", { status: 403 });
    }
    // Inject credentials the Dynamic Worker can't see
    const headers = new Headers(request.headers);
    headers.set("Authorization", `Bearer ${this.env.API_TOKEN}`);
    return fetch(request, { headers });
  }
}
```

Pass it: `globalOutbound: ctx.exports.HttpGateway({ props: { tenantId } })`

## Observability

Capture logs with Tail Workers. Logs are collected during execution and delivered asynchronously after the Dynamic Worker finishes (no added latency).

```typescript
export class LogTailer extends WorkerEntrypoint {
  async tail(events: TailEvent[]) {
    for (const event of events) {
      for (const log of event.logs) {
        console.log({ source: "dynamic-worker", workerId: this.ctx.props.workerId, level: log.level, message: log.message });
      }
    }
  }
}
```

Attach: `tails: [ctx.exports.LogTailer({ props: { workerId } })]`

Enable Workers Logs on the loader Worker for persistence:

```jsonc
{ "observability": { "enabled": true, "head_sampling_rate": 1 } }
```

For real-time logs during development, use a Durable Object as a shared log buffer between the Tail Worker and the fetch handler. See the [Dynamic Workers Playground](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers-playground) for a full implementation.

## TypeScript & npm Dependencies

Dynamic Workers execute raw JS/Python — no build step. For TypeScript or npm dependencies, bundle first with `@cloudflare/worker-bundler`:

```typescript
import { createWorker } from "@cloudflare/worker-bundler";

const worker = env.LOADER.get("my-app", async () => {
  const { mainModule, modules } = await createWorker({
    files: {
      "src/index.ts": tsCode,
      "package.json": JSON.stringify({ dependencies: { hono: "^4.0.0" } }),
    },
  });
  return { mainModule, modules, compatibilityDate: "2026-01-01" };
});
```

## References

- [API Reference](./references/api-reference.md) — Full WorkerCode, WorkerStub, load/get API details
- [Bindings](./references/bindings.md) — Custom RPC bindings, capability-based security, Cap'n Web
- [Egress Control](./references/egress-control.md) — Network blocking, interception, credential injection
- [Observability](./references/observability.md) — Tail Workers, Workers Logs, real-time log streaming
