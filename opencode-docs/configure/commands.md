# Commands - OpenCode Documentation

# Commands

Create custom commands for repetitive tasks.

Custom commands let you specify a prompt you want to run when that command is executed in the TUI.

```
/my-command
```

Custom commands are in addition to the built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`.

## Create command files

Create markdown files in the `commands/` directory to define custom commands.

`.opencode/commands/test.md`:
```markdown
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

The frontmatter defines command properties. The content becomes the template. Use the command by typing `/` followed by the command name.

## Configure

### JSON

Use the `command` option in your OpenCode config:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

Now you can run this command in the TUI: `/test`

### Markdown

You can also define commands using markdown files. Place them in:
- Global: `~/.config/opencode/commands/`
- Per-project: `.opencode/commands/`

The markdown file name becomes the command name. For example, `test.md` lets you run `/test`.

## Prompt config

### Arguments

Pass arguments to commands using the `$ARGUMENTS` placeholder:

```markdown
---
description: Create a new component
---

Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.
```

Run the command with arguments: `/component Button`

You can also access individual arguments using positional parameters: `$1`, `$2`, `$3`, etc.

### Shell output

Use `!command` to inject bash command output into your prompt:

```markdown
---
description: Analyze test coverage
---

Here are the current test results:
!`npm test`

Based on these results, suggest improvements to increase coverage.
```

### File references

Include files in your command using `@` followed by the filename:

```markdown
---
description: Review component
---

Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

## Options

- **Template** - The prompt that will be sent to the LLM when the command is executed. Required.
- **Description** - Brief description shown in the TUI. Optional.
- **Agent** - Optionally specify which agent should execute this command. Defaults to current agent.
- **Subtask** - Force the command to trigger a subagent invocation. Optional.
- **Model** - Override the default model for this command. Optional.

## Built-in

OpenCode includes several built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`. Custom commands can override built-in commands if you define a custom command with the same name.
