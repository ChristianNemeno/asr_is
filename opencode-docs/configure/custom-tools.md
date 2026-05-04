# Custom Tools - OpenCode Documentation

# Custom Tools

Create tools the LLM can call in OpenCode.

Custom tools are functions you create that the LLM can call during conversations. They work alongside OpenCode's built-in tools like `read`, `write`, and `bash`.

## Creating a tool

Tools are defined as TypeScript or JavaScript files. However, the tool definition can invoke scripts written in any language — TypeScript or JavaScript is only used for the tool definition itself.

### Location

They can be defined:
- Locally by placing them in the `.opencode/tools/` directory of your project.
- Or globally, by placing them in `~/.config/opencode/tools/`.

### Structure

The easiest way to create tools is using the `tool()` helper which provides type-safety and validation.

```typescript
// .opencode/tools/database.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Query the project database",
  args: {
    query: tool.schema.string().describe("SQL query to execute"),
  },
  async execute(args) {
    // Your database logic here
    return `Executed query: ${args.query}`
  },
})
```

The filename becomes the tool name. The above creates a `database` tool.

### Multiple tools per file

You can also export multiple tools from a single file. Each export becomes a separate tool with the name `<filename>_<exportname>`:

```typescript
// .opencode/tools/math.ts
import { tool } from "@opencode-ai/plugin"

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a + args.b
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a * args.b
  },
})
```

This creates two tools: `math_add` and `math_multiply`.

### Name collisions with built-in tools

Custom tools are keyed by tool name. If a custom tool uses the same name as a built-in tool, the custom tool takes precedence.

### Arguments

You can use `tool.schema` (Zod) to define argument types:

```typescript
args: {
  query: tool.schema.string().describe("SQL query to execute")
}
```

You can also import Zod directly:

```typescript
import { z } from "zod"
// ...
args: {
  param: z.string().describe("Parameter description"),
}
```

### Context

Tools receive context about the current session:

```typescript
// .opencode/tools/project.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Get project information",
  args: {},
  async execute(args, context) {
    const { agent, sessionID, messageID, directory, worktree } = context
    return `Agent: ${agent}, Session: ${sessionID}, Directory: ${directory}`
  },
})
```

Use `context.directory` for the session working directory. Use `context.worktree` for the git worktree root.

## Examples

### Write a tool in Python

Create the Python script:

```python
# .opencode/tools/add.py
import sys
a = int(sys.argv[1])
b = int(sys.argv[2])
print(a + b)
```

Then create the tool definition that invokes it:

```typescript
// .opencode/tools/python-add.ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Add two numbers using Python",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/add.py")
    const result = await Bun.$`python3 ${script} ${args.a} ${args.b}`.text()
    return result.trim()
  },
})
```
