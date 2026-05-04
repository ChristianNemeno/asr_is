# SDK - OpenCode Documentation

# SDK

Type-safe JS client for OpenCode server.

The OpenCode JS/TS SDK provides a type-safe client for interacting with the server. Use it to build integrations and control OpenCode programmatically.

## Install

Install the SDK from npm:

```
npm install @opencode-ai/sdk
```

## Create client

Create an instance of OpenCode:

```typescript
import { createOpencode } from "@opencode-ai/sdk"

const { client } = await createOpencode()
```

This starts both a server and a client. Options include `hostname`, `port`, `signal` (AbortSignal), `timeout`, and `config`.

### Config

You can pass a configuration object to customize behavior:

```typescript
import { createOpencode } from "@opencode-ai/sdk"

const opencode = await createOpencode({
  hostname: "127.0.0.1",
  port: 4096,
  config: {
    model: "anthropic/claude-3-5-sonnet-20241022",
  },
})

console.log(`Server running at ${opencode.server.url}`)
opencode.server.close()
```

### Client only

If you already have a running instance of OpenCode, you can create a client instance to connect to it:

```typescript
import { createOpencodeClient } from "@opencode-ai/sdk"

const client = createOpencodeClient({
  baseUrl: "http://localhost:4096",
})
```

Options: `baseUrl`, `fetch` (custom fetch implementation), `parseAs`, `responseStyle` (`data` or `fields`), `throwOnError`.

## Types

The SDK includes TypeScript definitions for all API types:

```typescript
import type { Session, Message, Part } from "@opencode-ai/sdk"
```

## Errors

The SDK can throw errors that you can catch and handle:

```typescript
try {
  await client.session.get({ path: { id: "invalid-id" } })
} catch (error) {
  console.error("Failed to get session:", (error as Error).message)
}
```

## Structured Output

You can request structured JSON output from the model by specifying a `format` with a JSON schema:

```typescript
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [{ type: "text", text: "Research Anthropic and provide company info" }],
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          company: { type: "string", description: "Company name" },
          founded: { type: "number", description: "Year founded" },
          products: {
            type: "array",
            items: { type: "string" },
            description: "Main products",
          },
        },
        required: ["company", "founded"],
      },
    },
  },
})
```

Output format types: `text` (default), `json_schema` (returns validated JSON).

### Error Handling

If the model fails to produce valid structured output after all retries:

```typescript
if (result.data.info.error?.name === "StructuredOutputError") {
  console.error("Failed to produce structured output:", result.data.info.error.message)
}
```

## APIs

### Global

```typescript
const health = await client.global.health()
console.log(health.data.version)
```

### App

```typescript
await client.app.log({
  body: { service: "my-app", level: "info", message: "Operation completed" },
})
const agents = await client.app.agents()
```

### Project

```typescript
const projects = await client.project.list()
const currentProject = await client.project.current()
```

### Path

```typescript
const pathInfo = await client.path.get()
```

### Config

```typescript
const config = await client.config.get()
const { providers, default: defaults } = await client.config.providers()
```

### Sessions

```typescript
const session = await client.session.create({ body: { title: "My session" } })
const sessions = await client.session.list()

const result = await client.session.prompt({
  path: { id: session.id },
  body: {
    model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },
    parts: [{ type: "text", text: "Hello!" }],
  },
})
```

### Files

```typescript
const textResults = await client.find.text({ query: { pattern: "function.*opencode" } })
const files = await client.find.files({ query: { query: "*.ts", type: "file" } })
const content = await client.file.read({ query: { path: "src/index.ts" } })
```

### TUI

```typescript
await client.tui.appendPrompt({ body: { text: "Add this to prompt" } })
await client.tui.showToast({ body: { message: "Task completed", variant: "success" } })
```

### Auth

```typescript
await client.auth.set({
  path: { id: "anthropic" },
  body: { type: "api", key: "your-api-key" },
})
```

### Events

```typescript
const events = await client.event.subscribe()
for await (const event of events.stream) {
  console.log("Event:", event.type, event.properties)
}
```
