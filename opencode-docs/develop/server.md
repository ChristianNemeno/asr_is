# Server - OpenCode Documentation

# Server

Interact with OpenCode server over HTTP.

The `opencode serve` command runs a headless HTTP server that exposes an OpenAPI endpoint that an OpenCode client can use.

## Usage

```
opencode serve [--port <number>] [--hostname <string>] [--cors <origin>]
```

**Options:**
- `--port` - Port to listen on (default: 4096)
- `--hostname` - Hostname to listen on (default: 127.0.0.1)
- `--mdns` - Enable mDNS discovery (default: false)
- `--mdns-domain` - Custom domain name for mDNS service (default: opencode.local)
- `--cors` - Additional browser origins to allow (can be passed multiple times)

## Authentication

Set `OPENCODE_SERVER_PASSWORD` to protect the server with HTTP basic auth. The username defaults to `opencode`, or set `OPENCODE_SERVER_USERNAME` to override it.

```
OPENCODE_SERVER_PASSWORD=your-password opencode serve
```

## How it works

When you run OpenCode it starts a TUI and a server. The TUI is the client that talks to the server. The server exposes an OpenAPI 3.1 spec endpoint.

You can run `opencode serve` to start a standalone server.

### Connect to an existing server

When you start the TUI it randomly assigns a port and hostname. You can instead pass in the `--hostname` and `--port` flags. The `/tui` endpoint can be used to drive the TUI through the server.

## Spec

The server publishes an OpenAPI 3.1 spec that can be viewed at:
`http://<hostname>:<port>/doc`

For example, `http://localhost:4096/doc`. Use the spec to generate clients or inspect request and response types.

## APIs

### Global
- `GET /global/health` - Get server health and version
- `GET /global/event` - Get global events (SSE stream)

### Project
- `GET /project` - List all projects
- `GET /project/current` - Get the current project

### Path & VCS
- `GET /path` - Get the current path
- `GET /vcs` - Get VCS info for the current project

### Instance
- `POST /instance/dispose` - Dispose the current instance

### Config
- `GET /config` - Get config info
- `PATCH /config` - Update config
- `GET /config/providers` - List providers and default models

### Provider
- `GET /provider` - List all providers
- `GET /provider/auth` - Get provider authentication methods
- `POST /provider/{id}/oauth/authorize` - Authorize a provider using OAuth
- `POST /provider/{id}/oauth/callback` - Handle OAuth callback

### Sessions
- `GET /session` - List all sessions
- `POST /session` - Create a new session
- `GET /session/status` - Get session status for all sessions
- `GET /session/:id` - Get session details
- `DELETE /session/:id` - Delete a session
- `PATCH /session/:id` - Update session properties
- `GET /session/:id/children` - Get child sessions
- `GET /session/:id/todo` - Get the todo list
- `POST /session/:id/init` - Analyze app and create AGENTS.md
- `POST /session/:id/fork` - Fork an existing session
- `POST /session/:id/abort` - Abort a running session
- `POST /session/:id/share` - Share a session
- `DELETE /session/:id/share` - Unshare a session
- `GET /session/:id/diff` - Get the diff for this session
- `POST /session/:id/summarize` - Summarize the session
- `POST /session/:id/revert` - Revert a message
- `POST /session/:id/unrevert` - Restore all reverted messages
- `POST /session/:id/permissions/:permissionID` - Respond to a permission request

### Messages
- `GET /session/:id/message` - List messages in a session
- `POST /session/:id/message` - Send a message and wait for response
- `GET /session/:id/message/:messageID` - Get message details
- `POST /session/:id/prompt_async` - Send a message asynchronously
- `POST /session/:id/command` - Execute a slash command
- `POST /session/:id/shell` - Run a shell command

### Commands
- `GET /command` - List all commands

### Files
- `GET /find?pattern=<pat>` - Search for text in files
- `GET /find/file?query=<q>` - Find files and directories by name
- `GET /find/symbol?query=<q>` - Find workspace symbols
- `GET /file?path=<path>` - List files and directories
- `GET /file/content?path=<p>` - Read a file
- `GET /file/status` - Get status for tracked files

### Tools (Experimental)
- `GET /experimental/tool/ids` - List all tool IDs
- `GET /experimental/tool?provider=<p>&model=<m>` - List tools with JSON schemas

### LSP, Formatters & MCP
- `GET /lsp` - Get LSP server status
- `GET /formatter` - Get formatter status
- `GET /mcp` - Get MCP server status
- `POST /mcp` - Add MCP server dynamically

### Agents
- `GET /agent` - List all available agents

### Logging
- `POST /log` - Write log entry

### TUI
- `POST /tui/append-prompt` - Append text to the prompt
- `POST /tui/open-help` - Open the help dialog
- `POST /tui/open-sessions` - Open the session selector
- `POST /tui/open-themes` - Open the theme selector
- `POST /tui/open-models` - Open the model selector
- `POST /tui/submit-prompt` - Submit the current prompt
- `POST /tui/clear-prompt` - Clear the prompt
- `POST /tui/execute-command` - Execute a command
- `POST /tui/show-toast` - Show toast notification
- `GET /tui/control/next` - Wait for the next control request
- `POST /tui/control/response` - Respond to a control request

### Auth
- `PUT /auth/:id` - Set authentication credentials

### Events
- `GET /event` - Server-sent events stream

### Docs
- `GET /doc` - OpenAPI 3.1 specification
