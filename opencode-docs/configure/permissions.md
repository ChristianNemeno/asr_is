# Permissions - OpenCode Documentation

# Permissions

Control which actions require approval to run.

OpenCode uses the `permission` config to decide whether a given action should run automatically, prompt you, or be blocked.

## Actions

Each permission rule resolves to one of:
- `"allow"` — run without approval
- `"ask"` — prompt for approval
- `"deny"` — block the action

## Configuration

You can set permissions globally (with `*`), and override specific tools.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": "allow",
    "edit": "deny"
  }
}
```

You can also set all permissions at once:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow"
}
```

## Granular Rules (Object Syntax)

For most permissions, you can use an object to apply different actions based on the tool input.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "npm *": "allow",
      "rm *": "deny",
      "grep *": "allow"
    },
    "edit": {
      "*": "deny",
      "packages/web/src/content/docs/*.mdx": "allow"
    }
  }
}
```

Rules are evaluated by pattern match, with the last matching rule winning.

## Wildcards

Permission patterns use simple wildcard matching:
- `*` matches zero or more of any character
- `?` matches exactly one character
- All other characters match literally

## Home Directory Expansion

You can use `~` or `$HOME` at the start of a pattern to reference your home directory. This is particularly useful for `external_directory` rules.

- `~/projects/*` -> `/Users/username/projects/*`
- `$HOME/projects/*` -> `/Users/username/projects/*`
- `~` -> `/Users/username`

## External Directories

Use `external_directory` to allow tool calls that touch paths outside the working directory.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow"
    }
  }
}
```

Any directory allowed here inherits the same defaults as the current workspace.

## Available Permissions

- `read` — reading a file (matches the file path)
- `edit` — all file modifications (covers edit, write, patch)
- `glob` — file globbing (matches the glob pattern)
- `grep` — content search (matches the regex pattern)
- `bash` — running shell commands (matches parsed commands)
- `task` — launching subagents (matches the subagent type)
- `skill` — loading a skill (matches the skill name)
- `lsp` — running LSP queries
- `question` — asking the user questions during execution
- `webfetch` — fetching a URL (matches the URL)
- `websearch` — web search (matches the query)
- `external_directory` — triggered when a tool touches paths outside the project working directory
- `doom_loop` — triggered when the same tool call repeats 3 times with identical input

## Defaults

If you don't specify anything, OpenCode starts from permissive defaults:
- Most permissions default to `"allow"`.
- `doom_loop` and `external_directory` default to `"ask"`.
- `read` is `"allow"`, but `.env` files are denied by default.

## What "Ask" Does

When OpenCode prompts for approval, the UI offers three outcomes:
- **once** — approve just this request
- **always** — approve future requests matching the suggested patterns
- **reject** — deny the request

## Agents

You can override permissions per agent. Agent permissions are merged with the global config, and agent rules take precedence.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "grep *": "allow"
    }
  },
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git *": "allow",
          "git commit *": "ask",
          "git push *": "deny",
          "grep *": "allow"
        }
      }
    }
  }
}
```

You can also configure agent permissions in Markdown:

```markdown
---
description: Code review without edits
mode: subagent
permission:
  edit: deny
  bash: ask
  webfetch: deny
---
```
