# Themes - OpenCode Documentation

# Themes

Select a built-in theme or define your own.

With OpenCode you can select from one of several built-in themes, use a theme that adapts to your terminal theme, or define your own custom theme.

By default, OpenCode uses our own `opencode` theme.

## Terminal requirements

For themes to display correctly with their full color palette, your terminal must support truecolor (24-bit color). Most modern terminals support this by default, but you may need to enable it:

- Check support: Run `echo $COLORTERM` - it should output `truecolor` or `24bit`
- Enable truecolor: Set `COLORTERM=truecolor` in your shell profile
- Terminal compatibility: Ensure your terminal emulator supports 24-bit color

## Built-in themes

| Name | Description |
|---|---|
| system | Adapts to your terminal's background color |
| tokyonight | Based on the Tokyonight theme |
| everforest | Based on the Everforest theme |
| ayu | Based on the Ayu dark theme |
| catppuccin | Based on the Catppuccin theme |
| catppuccin-macchiato | Based on the Catppuccin theme |
| gruvbox | Based on the Gruvbox theme |
| kanagawa | Based on the Kanagawa theme |
| nord | Based on the Nord theme |
| matrix | Hacker-style green on black theme |
| one-dark | Based on the Atom One Dark theme |

And more, we are constantly adding new themes.

## System theme

The system theme is designed to automatically adapt to your terminal's color scheme. It:
- Generates a custom gray scale based on your terminal's background color
- Uses ANSI colors (0-15) for syntax highlighting and UI elements
- Preserves terminal defaults for text and background colors

## Using a theme

You can select a theme with the `/theme` command, or specify it in `tui.json`:

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight"
}
```

## Custom themes

### Hierarchy

Themes are loaded from multiple directories in the following order (later directories override earlier ones):
1. Built-in themes
2. User config directory: `~/.config/opencode/themes/*.json`
3. Project root directory: `<project-root>/.opencode/themes/*.json`
4. Current working directory: `./.opencode/themes/*.json`

### Creating a theme

Create a JSON file in one of the theme directories.

For user-wide themes:
```
mkdir -p ~/.config/opencode/themes
```

For project-specific themes:
```
mkdir -p .opencode/themes
```

### JSON format

Themes use a flexible JSON format with support for:
- Hex colors: `"#ffffff"`
- ANSI colors: `3` (0-255)
- Color references: `"primary"` or custom definitions
- Dark/light variants: `{"dark": "#000", "light": "#fff"}`
- No color: `"none"` - Uses the terminal's default color or transparent

### Color definitions

The `defs` section is optional and allows you to define reusable colors that can be referenced in the theme.

### Terminal defaults

The special value `"none"` can be used for any color to inherit the terminal's default color.

### Example

```json
{
  "$schema": "https://opencode.ai/theme.json",
  "defs": {
    "nord0": "#2E3440",
    "nord1": "#3B4252",
    "nord2": "#434C5E",
    "nord3": "#4C566A",
    "nord4": "#D8DEE9",
    "nord5": "#E5E9F0",
    "nord6": "#ECEFF4",
    "nord7": "#8FBCBB",
    "nord8": "#88C0D0",
    "nord9": "#81A1C1",
    "nord10": "#5E81AC",
    "nord11": "#BF616A",
    "nord12": "#D08770",
    "nord13": "#EBCB8B",
    "nord14": "#A3BE8C",
    "nord15": "#B48EAD"
  },
  "theme": {
    "primary": { "dark": "nord8", "light": "nord10" },
    "secondary": { "dark": "nord9", "light": "nord9" },
    "accent": { "dark": "nord7", "light": "nord7" },
    "error": { "dark": "nord11", "light": "nord11" },
    "warning": { "dark": "nord12", "light": "nord12" },
    "success": { "dark": "nord14", "light": "nord14" },
    "info": { "dark": "nord8", "light": "nord10" },
    "text": { "dark": "nord4", "light": "nord0" },
    "background": { "dark": "nord0", "light": "nord6" },
    "border": { "dark": "nord2", "light": "nord3" },
    "diffAdded": { "dark": "nord14", "light": "nord14" },
    "diffRemoved": { "dark": "nord11", "light": "nord11" }
  }
}
```
