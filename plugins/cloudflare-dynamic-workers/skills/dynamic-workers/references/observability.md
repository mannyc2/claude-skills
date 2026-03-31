# Observability

Capture logs, exceptions, and request metadata from Dynamic Workers using Tail Workers.

## Setup Overview

1. Enable Workers Logs on the loader Worker
2. Define a Tail Worker class that receives and forwards logs
3. Attach the Tail Worker when creating the Dynamic Worker

Tail Workers run asynchronously after the Dynamic Worker responds — no added latency.

## Enable Workers Logs

Add to the loader Worker's wrangler config:

```jsonc
{
  "observability": {
    "enabled": true,
    "head_sampling_rate": 1
  }
}
```

Workers Logs only captures the loader Worker's own output. Dynamic Worker `console.log()` calls require a Tail Worker to bridge them.

## Define a Tail Worker

```javascript
import { WorkerEntrypoint } from "cloudflare:workers";

export class DynamicWorkerTail extends WorkerEntrypoint {
  async tail(events) {
    for (const event of events) {
      for (const log of event.logs) {
        console.log({
          source: "dynamic-worker-tail",
          workerId: this.ctx.props.workerId,
          level: log.level,
          message: log.message,
        });
      }
    }
  }
}
```

Include `workerId` in each entry for filtering/searching later.

## Attach to Dynamic Worker

```javascript
const worker = env.LOADER.get(workerId, () => ({
  mainModule: "index.js",
  modules: { "index.js": workerSource },
  tails: [
    ctx.exports.DynamicWorkerTail({
      props: { workerId },
    }),
  ],
}));
```

## Real-Time Logs

For development, use a Durable Object as a shared log buffer:

1. Create a log session in a Durable Object before running the Dynamic Worker
2. Dynamic Worker runs and produces logs
3. Tail Worker writes collected logs to the Durable Object
4. Fetch handler reads logs from the Durable Object and returns them

```javascript
import { exports } from "cloudflare:workers";

const logSession = exports.LogSession.getByName(workerName);
const logWaiter = await logSession.waitForLogs();

const response = await worker.getEntrypoint().fetch(request);

// Wait up to 1 second for tail delivery
const logs = await logWaiter.getLogs(1000);
```

Full implementation: [Dynamic Workers Playground](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers-playground)

## Example Repos

- [Dynamic Workers Starter](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers) — Hello world
- [Dynamic Workers Playground](https://github.com/cloudflare/agents/tree/main/examples/dynamic-workers-playground) — Write/import code, bundle at runtime, real-time logs
- [Codemode](https://github.com/cloudflare/agents/tree/main/examples/codemode) — AI agent code execution
