# Keybinds - OpenCode Documentation

# Keybinds

Customize your keybinds.

OpenCode has a list of keybinds that you can customize through `tui.json`.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "keybinds": {
    "leader": "ctrl+x",
    "app_exit": "ctrl+c,ctrl+d,<leader>q",
    "editor_open": "<leader>e",
    "theme_list": "<leader>t",
    "sidebar_toggle": "<leader>b",
    "scrollbar_toggle": "none",
    "username_toggle": "none",
    "status_view": "<leader>s",
    "tool_details": "none",
    "session_export": "<leader>x",
    "session_new": "<leader>n",
    "session_list": "<leader>l",
    "session_timeline": "<leader>g",
    "session_fork": "none",
    "session_rename": "ctrl+r",
    "session_share": "none",
    "session_unshare": "none",
    "session_interrupt": "escape",
    "session_compact": "<leader>c",
    "session_child_first": "<leader>down",
    "session_child_cycle": "right",
    "session_child_cycle_reverse": "left",
    "session_parent": "up",
    "messages_page_up": "pageup,ctrl+alt+b",
    "messages_page_down": "pagedown,ctrl+alt+f",
    "messages_line_up": "ctrl+alt+y",
    "messages_line_down": "ctrl+alt+e",
    "messages_half_page_up": "ctrl+alt+u",
    "messages_half_page_down": "ctrl+alt+d",
    "messages_first": "ctrl+g,home",
    "messages_last": "ctrl+alt+g,end",
    "messages_copy": "<leader>y",
    "messages_undo": "<leader>u",
    "messages_redo": "<leader>r",
    "model_list": "<leader>m",
    "model_cycle_recent": "f2",
    "model_cycle_recent_reverse": "shift+f2",
    "variant_cycle": "ctrl+t",
    "command_list": "ctrl+p",
    "agent_list": "<leader>a",
    "agent_cycle": "tab",
    "agent_cycle_reverse": "shift+tab",
    "input_clear": "ctrl+c",
    "input_paste": "ctrl+v",
    "input_submit": "return",
    "input_newline": "shift+return,ctrl+return,alt+return,ctrl+j",
    "input_move_left": "left,ctrl+b",
    "input_move_right": "right,ctrl+f",
    "input_move_up": "up",
    "input_move_down": "down",
    "input_backspace": "backspace,shift+backspace",
    "input_delete": "ctrl+d,delete,shift+delete",
    "input_undo": "ctrl+-,super+z",
    "input_redo": "ctrl+.,super+shift+z",
    "history_previous": "up",
    "history_next": "down",
    "terminal_suspend": "ctrl+z"
  }
}
```

## Leader key

OpenCode uses a leader key for most keybinds. By default, `ctrl+x` is the leader key and most actions require you to first press the leader key and then the shortcut. For example, to start a new session you first press `ctrl+x` and then press `n`.

## Disable keybind

You can disable a keybind by adding the key to `tui.json` with a value of `"none"`.

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "keybinds": {
    "session_compact": "none"
  }
}
```

## Desktop prompt shortcuts

The OpenCode desktop app prompt input supports common Readline/Emacs-style shortcuts:

| Shortcut | Action |
|---|---|
| ctrl+a | Move to start of current line |
| ctrl+e | Move to end of current line |
| ctrl+b | Move cursor back one character |
| ctrl+f | Move cursor forward one character |
| alt+b | Move cursor back one word |
| alt+f | Move cursor forward one word |
| ctrl+d | Delete character under cursor |
| ctrl+k | Kill to end of line |
| ctrl+u | Kill to start of line |
| ctrl+w | Kill previous word |
| alt+d | Kill next word |
| ctrl+t | Transpose characters |
| ctrl+g | Cancel popovers / abort running response |

## Shift+Enter

Some terminals don't send modifier keys with Enter by default. You may need to configure your terminal to send Shift+Enter as an escape sequence.

### Windows Terminal

Open your settings.json at `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`:

```json
"actions": [
  {
    "command": {
      "action": "sendInput",
      "input": "\u001b[13;2u"
    },
    "id": "User.sendInput.ShiftEnterCustom"
  }
],
"keybindings": [
  {
    "keys": "shift+enter",
    "id": "User.sendInput.ShiftEnterCustom"
  }
]
```
