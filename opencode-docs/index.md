# Intro - OpenCode Documentation

# Intro

Get started with OpenCode.

**OpenCode** is an open source AI coding agent. It's available as a terminal-based interface, desktop app, or IDE extension.

## Prerequisites

To use OpenCode in your terminal, you'll need:

1. A modern terminal emulator like:
   - WezTerm, cross-platform
   - Alacritty, cross-platform
   - Ghostty, Linux and macOS
   - Kitty, Linux and macOS
2. API keys for the LLM providers you want to use.

## Install

The easiest way to install OpenCode is through the install script.

```
curl -fsSL https://opencode.ai/install | bash
```

You can also install it with:

**Using Node.js**
```
npm install -g opencode-ai
```
```
bun install -g opencode-ai
```
```
pnpm install -g opencode-ai
```
```
yarn global add opencode-ai
```

**Using Homebrew on macOS and Linux**
```
brew install anomalyco/tap/opencode
```

**Installing on Arch Linux**
```
sudo pacman -S opencode
paru -S opencode-bin
```

### Windows
Recommended: Use WSL

**Using Chocolatey**: `choco install opencode`
**Using Scoop**: `scoop install opencode`
**Using NPM**: `npm install -g opencode-ai`
**Using Mise**: `mise use -g github:anomalyco/opencode`
**Using Docker**: `docker run -it --rm ghcr.io/anomalyco/opencode`

## Configure

With OpenCode you can use any LLM provider by configuring their API keys.

1. Run `/connect` in the TUI, select opencode, and head to opencode.ai/auth.
2. Sign in, add your billing details, and copy your API key.
3. Paste your API key.

## Initialize

```
cd /path/to/project
opencode
```

Run `/init` to create an AGENTS.md file.

## Usage

### Ask questions
Use `@` to fuzzy search for files.
```
How is authentication handled in @packages/functions/src/api/index.ts
```

### Add features
1. Switch to Plan mode with Tab key
2. Describe what you want
3. Iterate on the plan
4. Switch back to Build mode with Tab key

### Make changes
```
We need to add authentication to the /settings route...
```

### Undo changes
```
/undo
```
```
/redo
```

## Share
```
/share
```

## Customize
Pick a theme, customize keybinds, configure formatters, create custom commands, or play with the config.
