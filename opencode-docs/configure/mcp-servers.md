# MCP Servers - OpenCode Documentation

# MCP servers

Add local and remote MCP tools.

You can add external tools to OpenCode using the Model Context Protocol (MCP). OpenCode supports both local and remote servers.

Once added, MCP tools are automatically available to the LLM alongside built-in tools.

MCP servers add to your context, so you want to be careful with which ones you enable. Certain MCP servers can easily exceed the context limit.

## Enable

Define MCP servers in your OpenCode Config under `mcp`. Add each MCP with a unique name.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "name-of-mcp-server": {
      "enabled": true,
    },
    "name-of-other-mcp-server": {},
  },
}
```

You can also disable a server by setting `enabled` to `false`.

## Overriding remote defaults

Organizations can provide default MCP servers via their `.well-known/opencode` endpoint. To enable a specific server from your organization's remote config, add it to your local config with `enabled: true`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": true
    }
  }
}
```

## Local

Add local MCP servers using `type` set to `"local"`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-local-mcp-server": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": {
        "MY_ENV_VAR": "my_env_var_value",
      },
    },
  },
}
```

**Options:**
- `type` (required) - Must be `"local"`
- `command` (required) - Command and arguments to run the MCP server
- `environment` - Environment variables for the server
- `enabled` - Enable or disable on startup
- `timeout` - Timeout in ms for fetching tools (default: 5000)

## Remote

Add remote MCP servers by setting `type` to `"remote"`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-remote-mcp": {
      "type": "remote",
      "url": "https://my-mcp-server.com",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer MY_API_KEY"
      }
    }
  }
}
```

**Options:**
- `type` (required) - Must be `"remote"`
- `url` (required) - URL of the remote MCP server
- `enabled` - Enable or disable on startup
- `headers` - Headers to send with requests
- `oauth` - OAuth authentication configuration
- `timeout` - Timeout in ms for fetching tools (default: 5000)

## OAuth

OpenCode automatically handles OAuth authentication for remote MCP servers.

### Automatic

For most OAuth-enabled MCP servers, no special configuration is needed:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-oauth-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

### Pre-registered

If you have client credentials from the MCP server provider:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-oauth-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "clientId": "{env:MY_MCP_CLIENT_ID}",
        "clientSecret": "{env:MY_MCP_CLIENT_SECRET}",
        "scope": "tools:read tools:execute"
      }
    }
  }
}
```

### Authenticating

- `opencode mcp auth my-oauth-server` - Trigger authentication
- `opencode mcp list` - List all MCP servers and their auth status
- `opencode mcp logout my-oauth-server` - Remove stored credentials
- `opencode mcp debug my-oauth-server` - Debug connection and OAuth flow

### Disabling OAuth

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-api-key-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

## Manage

### Global

Your MCPs are available as tools in OpenCode. You can enable or disable them globally using the `tools` config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-mcp-foo": {
      "type": "local",
      "command": ["bun", "x", "my-mcp-command-foo"]
    },
    "my-mcp-bar": {
      "type": "local",
      "command": ["bun", "x", "my-mcp-command-bar"]
    }
  },
  "tools": {
    "my-mcp-foo": false
  }
}
```

You can also use a glob pattern to disable all matching MCPs:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "tools": {
    "my-mcp*": false
  }
}
```

### Per agent

If you have a large number of MCP servers you may want to only enable them per agent:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-mcp": {
      "type": "local",
      "command": ["bun", "x", "my-mcp-command"],
      "enabled": true
    }
  },
  "tools": {
    "my-mcp*": false
  },
  "agent": {
    "my-agent": {
      "tools": {
        "my-mcp*": true
      }
    }
  }
}
```

## Examples

### Sentry

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "oauth": {}
    }
  }
}
```

After adding the configuration, authenticate with: `opencode mcp auth sentry`

### Context7

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

### Grep by Vercel

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "gh_grep": {
      "type": "remote",
      "url": "https://mcp.grep.app"
    }
  }
}
```
