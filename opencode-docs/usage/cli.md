# CLI - OpenCode Documentation

# CLI

OpenCode CLI options and commands.

The OpenCode CLI by default starts the TUI when run without any arguments.
```
opencode
```

But it also accepts commands as documented on this page. This allows you to interact with OpenCode programmatically.
```
opencode run "Explain how closures work in JavaScript"
```

## tui

Start the OpenCode terminal user interface.
```
opencode [project]
```

**Flags:**
- `--continue`, `-c` - Continue the last session
- `--session`, `-s` - Session ID to continue
- `--fork` - Fork the session when continuing
- `--prompt` - Prompt to use
- `--model`, `-m` - Model to use in the form of `provider/model`
- `--agent` - Agent to use
- `--port` - Port to listen on
- `--hostname` - Hostname to listen on
- `--mdns` - Enable mDNS discovery
- `--mdns-domain` - Custom mDNS domain name
- `--cors` - Additional browser origin(s) to allow CORS

## Commands

### agent

Manage agents for OpenCode.
```
opencode agent [command]
```

**create** - Create a new agent with custom configuration.
```
opencode agent create
```
Flags: `--path`, `--description`, `--mode`, `--permissions`/`--tools`, `--model`, `-m`

**list** - List all available agents.
```
opencode agent list
```

### attach

Attach a terminal to an already running OpenCode backend server.
```
opencode attach [url]
```
Flags: `--dir`, `--continue`/`-c`, `--session`/`-s`, `--fork`, `--password`/`-p`, `--username`/`-u`

### auth

Manage credentials and login for providers.
```
opencode auth [command]
```

**login** - Configure API keys for any provider.
**list** - Lists all authenticated providers. Alias: `ls`
**logout** - Logs you out of a provider.

### github

Manage the GitHub agent for repository automation.
```
opencode github [command]
```

**install** - Install the GitHub agent in your repository.
**run** - Run the GitHub agent. Flags: `--event`, `--token`

### mcp

Manage Model Context Protocol servers.
```
opencode mcp [command]
```

**add** - Add an MCP server.
**list** - List all configured MCP servers. Alias: `ls`
**auth** - Authenticate with an OAuth-enabled MCP server.
**logout** - Remove OAuth credentials.
**debug** - Debug OAuth connection issues.

### models

List all available models from configured providers.
```
opencode models [provider]
```
Flags: `--refresh`, `--verbose`

### run

Run OpenCode in non-interactive mode by passing a prompt directly.
```
opencode run [message..]
```
Flags: `--command`, `--continue`/`-c`, `--session`/`-s`, `--fork`, `--share`, `--model`/`-m`, `--agent`, `--file`/`-f`, `--format`, `--title`, `--attach`, `--password`/`-p`, `--username`/`-u`, `--dir`, `--port`, `--variant`, `--thinking`, `--dangerously-skip-permissions`

### serve

Start a headless OpenCode server for API access.
```
opencode serve
```
Flags: `--port`, `--hostname`, `--mdns`, `--mdns-domain`, `--cors`

### session

Manage OpenCode sessions.
```
opencode session [command]
```

**list** - List all OpenCode sessions. Flags: `--max-count`/`-n`, `--format`
**delete** - Delete an OpenCode session.

### stats

Show token usage and cost statistics for your OpenCode sessions.
```
opencode stats
```
Flags: `--days`, `--tools`, `--models`, `--project`

### export

Export session data as JSON.
```
opencode export [sessionID]
```
Flags: `--sanitize`

### import

Import session data from a JSON file or OpenCode share URL.
```
opencode import <file>
```

### web

Start a headless OpenCode server with a web interface.
```
opencode web
```
Flags: `--port`, `--hostname`, `--mdns`, `--mdns-domain`, `--cors`

### acp

Start an ACP (Agent Client Protocol) server.
```
opencode acp
```
Flags: `--cwd`, `--port`, `--hostname`, `--mdns`, `--mdns-domain`, `--cors`

### plugin

Install a plugin and update your config.
```
opencode plugin <module>
```
Alias: `opencode plug <module>`
Flags: `--global`/`-g`, `--force`/`-f`

### pr

Fetch and checkout a GitHub PR branch, then run OpenCode.
```
opencode pr <number>
```

### db

Database tools.
```
opencode db [query]
```
Flags: `--format`

**path** - Print the database path.

### debug

Debugging and troubleshooting tools.
```
opencode debug [command]
```

### uninstall

Uninstall OpenCode and remove all related files.
```
opencode uninstall
```
Flags: `--keep-config`/`-c`, `--keep-data`/`-d`, `--dry-run`, `--force`/`-f`

### upgrade

Updates OpenCode to the latest version or a specific version.
```
opencode upgrade [target]
```
Flags: `--method`/`-m`

## Global Flags

- `--help`, `-h` - Display help
- `--version`, `-v` - Print version number
- `--print-logs` - Print logs to stderr
- `--log-level` - Log level (DEBUG, INFO, WARN, ERROR)
- `--pure` - Run without external plugins

## Environment variables

| Variable | Type | Description |
|---|---|---|
| OPENCODE_AUTO_SHARE | boolean | Automatically share sessions |
| OPENCODE_GIT_BASH_PATH | string | Path to Git Bash executable on Windows |
| OPENCODE_CONFIG | string | Path to config file |
| OPENCODE_TUI_CONFIG | string | Path to TUI config file |
| OPENCODE_CONFIG_DIR | string | Path to config directory |
| OPENCODE_CONFIG_CONTENT | string | Inline json config content |
| OPENCODE_DISABLE_AUTOUPDATE | boolean | Disable automatic update checks |
| OPENCODE_DISABLE_PRUNE | boolean | Disable pruning of old data |
| OPENCODE_DISABLE_TERMINAL_TITLE | boolean | Disable automatic terminal title updates |
| OPENCODE_PERMISSION | string | Inlined json permissions config |
| OPENCODE_DISABLE_DEFAULT_PLUGINS | boolean | Disable default plugins |
| OPENCODE_DISABLE_LSP_DOWNLOAD | boolean | Disable automatic LSP server downloads |
| OPENCODE_ENABLE_EXPERIMENTAL_MODELS | boolean | Enable experimental models |
| OPENCODE_DISABLE_AUTOCOMPACT | boolean | Disable automatic context compaction |
| OPENCODE_DISABLE_CLAUDE_CODE | boolean | Disable reading from .claude (prompt + skills) |
| OPENCODE_DISABLE_CLAUDE_CODE_PROMPT | boolean | Disable reading ~/.claude/CLAUDE.md |
| OPENCODE_DISABLE_CLAUDE_CODE_SKILLS | boolean | Disable loading .claude/skills |
| OPENCODE_DISABLE_MODELS_FETCH | boolean | Disable fetching models from remote sources |
| OPENCODE_DISABLE_MOUSE | boolean | Disable mouse capture in the TUI |
| OPENCODE_FAKE_VCS | string | Fake VCS provider for testing purposes |
| OPENCODE_CLIENT | string | Client identifier (defaults to cli) |
| OPENCODE_ENABLE_EXA | boolean | Enable Exa web search tools |
| OPENCODE_SERVER_PASSWORD | string | Enable basic auth for serve/web |
| OPENCODE_SERVER_USERNAME | string | Override basic auth username (default opencode) |
| OPENCODE_MODELS_URL | string | Custom URL for fetching models configuration |

## Experimental

| Variable | Type | Description |
|---|---|---|
| OPENCODE_EXPERIMENTAL | boolean | Enable all experimental features |
| OPENCODE_EXPERIMENTAL_ICON_DISCOVERY | boolean | Enable icon discovery |
| OPENCODE_EXPERIMENTAL_DISABLE_COPY_ON_SELECT | boolean | Disable copy on select in TUI |
| OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS | number | Default timeout for bash commands in ms |
| OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX | number | Max output tokens for LLM responses |
| OPENCODE_EXPERIMENTAL_FILEWATCHER | boolean | Enable file watcher for entire dir |
| OPENCODE_EXPERIMENTAL_OXFMT | boolean | Enable oxfmt formatter |
| OPENCODE_EXPERIMENTAL_LSP_TOOL | boolean | Enable experimental LSP tool |
| OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER | boolean | Disable file watcher |
| OPENCODE_EXPERIMENTAL_EXA | boolean | Enable experimental Exa features |
| OPENCODE_EXPERIMENTAL_LSP_TY | boolean | Enable TY LSP for python files |
| OPENCODE_EXPERIMENTAL_MARKDOWN | boolean | Enable experimental markdown features |
| OPENCODE_EXPERIMENTAL_PLAN_MODE | boolean | Enable plan mode |
