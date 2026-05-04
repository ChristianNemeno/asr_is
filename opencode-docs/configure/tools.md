# Tools - OpenCode Documentation

# Tools

Manage the tools an LLM can use.

Tools allow the LLM to perform actions in your codebase. OpenCode comes with a set of built-in tools, but you can extend it with custom tools or MCP servers.

By default, all tools are enabled and don't need permission to run. You can control tool behavior through permissions.

## Configure

Use the `permission` field to control tool behavior. You can allow, deny, or require approval for each tool.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "deny",
    "bash": "ask",
    "webfetch": "allow"
  }
}
```

You can also use wildcards to control multiple tools at once. For example, to require approval for all tools from an MCP server:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "mymcp_*": "ask"
  }
}
```

## Built-in

### bash

Execute shell commands in your project environment.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": "allow"
  }
}
```

### edit

Modify existing files using exact string replacements.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "allow"
  }
}
```

### write

Create new files or overwrite existing ones. Controlled by the `edit` permission.

### read

Read file contents from your codebase.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "allow"
  }
}
```

### grep

Search file contents using regular expressions.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "grep": "allow"
  }
}
```

### glob

Find files by pattern matching.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "glob": "allow"
  }
}
```

### lsp (experimental)

Interact with your configured LSP servers to get code intelligence features. Only available when `OPENCODE_EXPERIMENTAL_LSP_TOOL=true`.

### apply_patch

Apply patches to files. Controlled by the `edit` permission.

### skill

Load a skill (a SKILL.md file) and return its content in the conversation.

### todowrite

Manage todo lists during coding sessions. Disabled for subagents by default.

### webfetch

Fetch web content.

### websearch

Search the web for information. Only available when using the OpenCode provider or when `OPENCODE_ENABLE_EXA` is set.

### question

Ask the user questions during execution. Useful for gathering preferences, clarifying instructions, or getting decisions on implementation choices.

## Custom tools

Custom tools let you define your own functions that the LLM can call. These are defined in your config file and can execute arbitrary code.

## MCP servers

MCP (Model Context Protocol) servers allow you to integrate external tools and services. This includes database access, API integrations, and third-party services.

## Internals

Internally, tools like `grep` and `glob` use ripgrep under the hood. By default, ripgrep respects `.gitignore` patterns.

## Ignore patterns

To include files that would normally be ignored, create a `.ignore` file in your project root.

```
!node_modules/
!dist/
!build/
```
