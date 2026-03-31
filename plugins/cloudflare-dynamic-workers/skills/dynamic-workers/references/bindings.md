# Bindings

Dynamic Worker bindings don't typically point at platform resources (KV, R2). Instead, they point to anything you define via Workers RPC interfaces.

## Capability-Based Security

Workers RPC (Cap'n Web) implements capability-based security. Objects are passed "by reference" across RPC boundaries — receiving a stub grants the ability to call its methods. Objects have no global identifier, so you can only call them if you received a stub.

This is the foundation for strong sandboxing: block the network, then constructively offer specific capabilities via bindings.

## Custom Bindings

Define a `WorkerEntrypoint` class in the parent Worker and export it. Use `ctx.props` to specialize per-tenant.

```typescript
import { WorkerEntrypoint } from "cloudflare:workers";

export class ChatRoom extends WorkerEntrypoint<Cloudflare.Env, ChatRoomProps> {
  async post(text: string): Promise<void> {
    const { apiKey, botName, roomName } = this.ctx.props;
    text = `[${botName}]: ${text}`;
    await postToChat(apiKey, roomName, text);
  }
}

type ChatRoomProps = {
  apiKey: string;
  roomName: string;
  botName: string;
};
```

Pass the binding to the Dynamic Worker via `ctx.exports` and `env`:

```typescript
const props: ChatRoomProps = { apiKey, roomName: "#bot-chat", botName: "Robo" };
const chatRoom = ctx.exports.ChatRoom({ props });

const worker = env.LOADER.load({
  env: { CHAT_ROOM: chatRoom },
  compatibilityDate: "2026-01-01",
  mainModule: "index.js",
  modules: { "index.js": codeFromAgent },
  globalOutbound: null,
});

return worker.getEntrypoint("Agent").run();
```

**Sandbox properties achieved:**
- Agent can only post to the designated room
- API key is never visible to the agent
- Messages are rewritten to include the agent's identity
- No cooperation from the agent required

## Tip: Tell your agent TypeScript types

Describe binding interfaces to AI agents using TypeScript types with JSDoc comments. LLMs understand TypeScript well — it's the most concise way to describe a JavaScript API. Even if the agent writes plain JavaScript, explain the interface in TypeScript.

## Passing Standard Workers Bindings

Direct pass-through of KV, R2, D1, etc. is not yet supported. Create a wrapper RPC interface that forwards to the real binding. This is often preferable anyway — it lets you narrow scope, filter requests, and rewrite data.
