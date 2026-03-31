# Egress Control

Control outbound network access for Dynamic Workers via the `globalOutbound` option.

## Block All Outbound Access

Set `globalOutbound: null` to fully isolate the Dynamic Worker:

```javascript
return {
  mainModule: "index.js",
  modules: { "index.js": code },
  globalOutbound: null,
};
```

Any `fetch()` or `connect()` throws an exception. Use bindings to grant access to specific resources.

## Intercept Outbound Requests

Define a `WorkerEntrypoint` gateway class. Every `fetch()` and `connect()` from the Dynamic Worker routes through this gateway.

```javascript
import { WorkerEntrypoint } from "cloudflare:workers";

export class HttpGateway extends WorkerEntrypoint {
  async fetch(request) {
    // Inspect, modify, block, or forward
    return fetch(request);
  }
}

export default {
  async fetch(request, env, ctx) {
    const worker = env.LOADER.get("my-worker", async () => ({
      compatibilityDate: "2026-01-01",
      mainModule: "index.js",
      modules: { "index.js": code },
      globalOutbound: ctx.exports.HttpGateway(),
    }));
    return worker.getEntrypoint().fetch(request);
  },
};
```

## Inject Credentials

Attach secrets to outbound requests without exposing them to the Dynamic Worker. Use `ctx.props` for per-tenant context.

```javascript
export class HttpGateway extends WorkerEntrypoint {
  async fetch(request) {
    const url = new URL(request.url);
    const headers = new Headers(request.headers);

    if (url.hostname === "api.example.com") {
      headers.set("Authorization", `Bearer ${this.env.API_TOKEN}`);
      headers.set("X-Tenant-Id", this.ctx.props.tenantId);
    }

    return fetch(request, { headers });
  }
}
```

Pass per-tenant props:

```javascript
globalOutbound: ctx.exports.HttpGateway({ props: { tenantId } })
```

## Common Patterns

| Pattern | `globalOutbound` value |
|---|---|
| Full isolation | `null` |
| Full Internet access | omit (inherits parent) |
| Allowlist domains | Gateway that checks `url.hostname` |
| Inject API credentials | Gateway that adds `Authorization` header |
| Audit/log all requests | Gateway that logs before forwarding |
| Per-tenant routing | Gateway with `ctx.props` for tenant context |
