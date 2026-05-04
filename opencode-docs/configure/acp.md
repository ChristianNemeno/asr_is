# ACP Support - OpenCode Documentation

# ACP Support

Use OpenCode in any ACP-compatible editor.

OpenCode supports the Agent Client Protocol (ACP), allowing you to use it directly in compatible editors and IDEs.

ACP is an open protocol that standardizes communication between code editors and AI coding agents.

## Configure

To use OpenCode via ACP, configure your editor to run the `opencode acp` command. The command starts OpenCode as an ACP-compatible subprocess that communicates with your editor over JSON-RPC via stdio.

### Zed

Add to your Zed configuration (`~/.config/zed/settings.json`):

```json
{
  "agent_servers": {
    "OpenCode": {
      "command": "opencode",
      "args": ["acp"]
    }
  }
}
```

To open it, use the `agent: new thread` action in the Command Palette.

You can also bind a keyboard shortcut:

```json
[
  {
    "bindings": {
      "cmd-alt-o": [
        "agent::NewExternalAgentThread",
        {
          "agent": {
            "custom": {
              "name": "OpenCode",
              "command": {
                "command": "opencode",
                "args": ["acp"]
              }
            }
          }
        }
      ]
    }
  }
]
```

### JetBrains IDEs

Add to your JetBrains IDE `acp.json` according to the documentation:

```json
{
  "agent_servers": {
    "OpenCode": {
      "command": "/absolute/path/bin/opencode",
      "args": ["acp"]
    }
  }
}
```

To open it, use the new 'OpenCode' agent in the AI Chat agent selector.

### Avante.nvim

Add to your Avante.nvim configuration:

```lua
{
  acp_providers = {
    ["opencode"] = {
      command = "opencode",
      args = { "acp" }
    }
  }
}
```

### CodeCompanion.nvim

Add to your Neovim config:

```lua
require("codecompanion").setup({
  interactions = {
    chat = {
      adapter = {
        name = "opencode",
        model = "claude-sonnet-4",
      },
    },
  },
})
```

## Support

OpenCode works the same via ACP as it does in the terminal. All features are supported:
- Built-in tools (file operations, terminal commands, etc.)
- Custom tools and slash commands
- MCP servers configured in your OpenCode config
- Project-specific rules from AGENTS.md
- Custom formatters and linters
- Agents and permissions system

Some built-in slash commands like `/undo` and `/redo` are currently unsupported via ACP.
