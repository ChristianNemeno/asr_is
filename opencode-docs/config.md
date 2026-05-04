# Config - OpenCode Documentation

# Config

Using the OpenCode JSON config.

You can configure OpenCode using a JSON config file.

## Format

OpenCode supports both JSON and JSONC (JSON with Comments) formats.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "server": {
    "port": 4096,
  },
}
```

## Locations

You can place your config in a couple of different locations and they have a different order of precedence.

Configuration files are merged together, not replaced. Settings from the following config locations are combined. Later configs override earlier ones only for conflicting keys. Non-conflicting settings from all configs are preserved.

For example, if your global config sets `autoupdate: true` and your project config sets `model: "anthropic/claude-sonnet-4-5"`, the final configuration will include both settings.

### Precedence order

Config sources are loaded in this order (later sources override earlier ones):

1. Remote config (from `.well-known/opencode`) - organizational defaults
2. Global config (`~/.config/opencode/opencode.json`) - user preferences
3. Custom config (`OPENCODE_CONFIG` env var) - custom overrides
4. Project config (`opencode.json` in project) - project-specific settings
5. `.opencode` directories - agents, commands, plugins
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var) - runtime overrides
7. Managed config files (`/Library/Application Support/opencode/` on macOS) - admin-controlled
8. macOS managed preferences (`.mobileconfig` via MDM) - highest priority, not user-overridable

The `.opencode` and `~/.config/opencode` directories use plural names for subdirectories: `agents/`, `commands/`, `modes/`, `plugins/`, `skills/`, `tools/`, and `themes/`. Singular names (e.g., `agent/`) are also supported for backwards compatibility.

### Remote

Organizations can provide default configuration via the `.well-known/opencode` endpoint. This is fetched automatically when you authenticate with a provider that supports it.

Remote config is loaded first, serving as the base layer. All other config sources (global, project) can override these defaults.

```json
{
  "mcp": {
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": false
    }
  }
}
```

### Global

Place your global OpenCode config in `~/.config/opencode/opencode.json`. Use global config for user-wide server/runtime preferences like providers, models, and permissions. For TUI-specific settings, use `~/.config/opencode/tui.json`.

### Per project

Add `opencode.json` in your project root. Project config has the highest precedence among standard config files - it overrides both global and remote configs. For project-specific TUI settings, add `tui.json` alongside it.

When OpenCode starts up, it looks for a config file in the current directory or traverses up to the nearest Git directory.

### Custom path

Specify a custom config file path using the `OPENCODE_CONFIG` environment variable.

```
export OPENCODE_CONFIG=/path/to/my/custom-config.json
opencode run "Hello world"
```

Custom config is loaded between global and project configs in the precedence order.

### Custom directory

Specify a custom config directory using the `OPENCODE_CONFIG_DIR` environment variable.

```
export OPENCODE_CONFIG_DIR=/path/to/my/config-directory
opencode run "Hello world"
```

### Managed settings

Organizations can enforce configuration that users cannot override.

**File-based:** Drop an `opencode.json` or `opencode.jsonc` file in the system managed config directory:

| Platform | Path |
|---|---|
| macOS | `/Library/Application Support/opencode/` |
| Linux | `/etc/opencode/` |
| Windows | `%ProgramData%\opencode` |

**macOS managed preferences:** On macOS, OpenCode reads managed preferences from the `ai.opencode.managed` preference domain. Deploy a `.mobileconfig` via MDM (Jamf, Kandji, FleetDM) and the settings are enforced automatically.

OpenCode checks these paths:
- `/Library/Managed Preferences/<user>/ai.opencode.managed.plist`
- `/Library/Managed Preferences/ai.opencode.managed.plist`

## Schema

The server/runtime config schema is defined at `opencode.ai/config.json`. TUI config uses `opencode.ai/tui.json`.

## TUI

Use a dedicated `tui.json` (or `tui.jsonc`) file for TUI-specific settings.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "scroll_speed": 3,
  "scroll_acceleration": {
    "enabled": true
  },
  "diff_style": "auto",
  "mouse": true
}
```

Use `OPENCODE_TUI_CONFIG` to point to a custom TUI config file.

## Server

Configure server settings for the `opencode serve` and `opencode web` commands through the `server` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true,
    "mdnsDomain": "myproject.local",
    "cors": ["http://localhost:5173"]
  }
}
```

Available options:
- `port` - Port to listen on.
- `hostname` - Hostname to listen on.
- `mdns` - Enable mDNS service discovery.
- `mdnsDomain` - Custom domain name for mDNS service. Defaults to `opencode.local`.
- `cors` - Additional origins to allow for CORS.

## Shell

Configure the shell used for the interactive terminal using the `shell` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "shell": "pwsh"
}
```

If not specified, OpenCode will automatically discover and use a sensible default.

## Tools

Manage the tools an LLM can use.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "write": false,
    "bash": false
  }
}
```

## Models

Configure providers and models.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {},
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5"
}
```

The `small_model` option configures a separate model for lightweight tasks like title generation.

Provider options can include `timeout`, `chunkTimeout`, and `setCacheKey`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "chunkTimeout": 30000,
        "setCacheKey": true
      }
    }
  }
}
```

- `timeout` - Request timeout in milliseconds (default: 300000). Set to `false` to disable.
- `chunkTimeout` - Timeout in milliseconds between streamed response chunks.
- `setCacheKey` - Ensure a cache key is always set for designated provider.

### Provider-Specific Options

**Amazon Bedrock:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile",
        "endpoint": "https://bedrock-runtime.us-east-1.vpce-xxxxx.amazonaws.com"
      }
    }
  }
}
```

- `region` - AWS region for Bedrock (defaults to `AWS_REGION` env var or `us-east-1`)
- `profile` - AWS named profile from `~/.aws/credentials`
- `endpoint` - Custom endpoint URL for VPC endpoints.

## Themes

Set your UI theme in `tui.json`.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight"
}
```

## Agents

Configure specialized agents for specific tasks through the `agent` option.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": {
        "write": false,
        "edit": false,
      },
    },
  },
}
```

## Default agent

Set the default agent using the `default_agent` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "plan"
}
```

The default agent must be a primary agent (not a subagent). This can be a built-in agent like "build" or "plan", or a custom agent you've defined.

## Sharing

Configure the share feature through the `share` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "share": "manual"
}
```

- `"manual"` - Allow manual sharing via commands (default)
- `"auto"` - Automatically share new conversations
- `"disabled"` - Disable sharing entirely

## Commands

Configure custom commands for repetitive tasks through the `command` option.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-haiku-4-5",
    },
  },
}
```

## Keybinds

Customize keybinds in `tui.json`.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "keybinds": {}
}
```

## Snapshot

OpenCode uses snapshots to track file changes during agent operations. Snapshots are enabled by default.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "snapshot": false
}
```

Disabling snapshots means changes made by the agent cannot be rolled back through the UI.

## Autoupdate

OpenCode will automatically download any new updates when it starts up.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "autoupdate": false
```

If you don't want updates but want to be notified when a new version is available, set `autoupdate` to `"notify"`.

## Formatters

Enable and configure code formatters through the `formatter` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": true
}
```

Use an object to keep built-ins enabled while configuring overrides or custom formatters.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {
    "prettier": {
      "disabled": true
    },
    "custom-prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": {
        "NODE_ENV": "development"
      },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    }
  }
}
```

## LSP Servers

Enable and configure LSP servers through the `lsp` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": true
}
```

Use an object to keep built-ins enabled while configuring overrides or custom LSP servers.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "lsp": {
    "typescript": {
      "disabled": true
    }
  }
}
```

## Permissions

Control whether actions require approval.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

## Compaction

Control context compaction behavior through the `compaction` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

- `auto` - Automatically compact the session when context is full (default: `true`).
- `prune` - Remove old tool outputs to save tokens (default: `true`).
- `reserved` - Token buffer for compaction.

## Watcher

Configure file watcher ignore patterns through the `watcher` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "watcher": {
    "ignore": ["node_modules/**", "dist/**", ".git/**"]
  }
}
```

## MCP servers

Configure MCP servers you want to use through the `mcp` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {}
}
```

## Plugins

Plugins extend OpenCode with custom tools, hooks, and integrations.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"]
}
```

## Instructions

Configure instructions for the model through the `instructions` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"]
}
```

## Disabled providers

Disable providers that are loaded automatically through the `disabled_providers` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "disabled_providers": ["openai", "gemini"]
}
```

The `disabled_providers` takes priority over `enabled_providers`.

## Enabled providers

Specify an allowlist of providers through the `enabled_providers` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "enabled_providers": ["anthropic", "openai"]
}
```

## Experimental

The `experimental` key contains options that are under active development.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "experimental": {}
}
```

Experimental options are not stable. They may change or be removed without notice.

## Variables

### Env vars

Use `{env:VARIABLE_NAME}` to substitute environment variables:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### Files

Use `{file:path/to/file}` to substitute the contents of a file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

File paths can be relative to the config file directory, or absolute paths starting with `/` or `~`.
