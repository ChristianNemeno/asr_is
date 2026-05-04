# TUI - OpenCode Documentation

# TUI

Using the OpenCode terminal user interface.

OpenCode provides an interactive terminal interface or TUI for working on your projects with an LLM.

Running OpenCode starts the TUI for the current directory.
```
opencode
```

Or you can start it for a specific working directory.
```
opencode /path/to/project
```

## File references

You can reference files in your messages using `@`. This does a fuzzy file search in the current working directory.

```
How is auth handled in @packages/functions/src/api/index.ts?
```

The content of the file is added to the conversation automatically.

## Bash commands

Start a message with `!` to run a shell command.
```
!ls -la
```

The output of the command is added to the conversation as a tool result.

## Commands

When using the OpenCode TUI, you can type `/` followed by a command name to quickly execute actions.

**connect** - Add a provider to OpenCode. Allows you to select from available providers and add their API keys.
```
/connect
```

**compact** - Compact the current session. Alias: `/summarize`
```
/compact
```
Keybind: `ctrl+x c`

**details** - Toggle tool execution details.
```
/details
```

**editor** - Open external editor for composing messages. Uses the editor set in your `EDITOR` environment variable.
```
/editor
```
Keybind: `ctrl+x e`

**exit** - Exit OpenCode. Aliases: `/quit`, `/q`
```
/exit
```
Keybind: `ctrl+x q`

**export** - Export current conversation to Markdown and open in your default editor.
```
/export
```
Keybind: `ctrl+x x`

**help** - Show the help dialog.
```
/help
```

**init** - Guided setup for creating or updating AGENTS.md.
```
/init
```

**models** - List available models.
```
/models
```
Keybind: `ctrl+x m`

**new** - Start a new session. Alias: `/clear`
```
/new
```
Keybind: `ctrl+x n`

**redo** - Redo a previously undone message. Only available after using `/undo`.
```
/redo
```
Keybind: `ctrl+x r`

**sessions** - List and switch between sessions. Aliases: `/resume`, `/continue`
```
/sessions
```
Keybind: `ctrl+x l`

**share** - Share current session.
```
/share
```

**themes** - List available themes.
```
/themes
```
Keybind: `ctrl+x t`

**thinking** - Toggle the visibility of thinking/reasoning blocks in the conversation.
```
/thinking
```

**undo** - Undo last message in the conversation.
```
/undo
```
Keybind: `ctrl+x u`

**unshare** - Unshare current session.
```
/unshare
```

## Editor setup

Both the `/editor` and `/export` commands use the editor specified in your `EDITOR` environment variable.

```
# Linux/macOS
export EDITOR=nano
export EDITOR=vim
export EDITOR="code --wait"

# Windows (CMD)
set EDITOR=notepad
set EDITOR=code --wait

# Windows (PowerShell)
$env:EDITOR = "notepad"
$env:EDITOR = "code --wait"
```

Popular editor options include: `code` (VS Code), `cursor` (Cursor), `windsurf` (Windsurf), `nvim` (Neovim), `vim`, `nano`, `notepad`, `subl` (Sublime Text).

## Configure

You can customize TUI behavior through `tui.json` (or `tui.jsonc`).

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "opencode",
  "keybinds": {
    "leader": "ctrl+x"
  },
  "scroll_speed": 3,
  "scroll_acceleration": {
    "enabled": false
  },
  "diff_style": "auto",
  "mouse": true
}
```

**Options:**
- `theme` - Sets your UI theme.
- `keybinds` - Customizes keyboard shortcuts.
- `scroll_acceleration.enabled` - Enable macOS-style scroll acceleration.
- `scroll_speed` - Controls how fast the TUI scrolls (minimum: 0.001, supports decimal values). Defaults to 3.
- `diff_style` - Controls diff rendering. `"auto"` adapts to terminal width, `"stacked"` always shows a single-column layout.
- `mouse` - Enable or disable mouse capture in the TUI (default: `true`).

Use `OPENCODE_TUI_CONFIG` to load a custom TUI config path.

## Customization

You can customize various aspects of the TUI view using the command palette (`ctrl+p`). These settings persist across restarts.

**Username display:** Toggle whether your username appears in chat messages. Access this through the command palette by searching for "username" or "hide username".
