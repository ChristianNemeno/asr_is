# Agents - OpenCode Documentation

# Agents

Configure and use specialized agents.

Agents are specialized AI assistants that can be configured for specific tasks and workflows. They allow you to create focused tools with custom prompts, models, and tool access.

You can switch between agents during a session or invoke them with the `@` mention.

## Types

### Primary agents

Primary agents are the main assistants you interact with directly. You can cycle through them using the Tab key, or your configured `switch_agent` keybind. These agents handle your main conversation. Tool access is configured via permissions.

### Subagents

Subagents are specialized assistants that primary agents can invoke for specific tasks. You can also manually invoke them by `@` mentioning them in your messages.

## Built-in

### build
- Mode: primary
- The default primary agent with all tools enabled. Standard agent for development work.

### plan
- Mode: primary
- A restricted agent designed for planning and analysis. File edits and bash commands require approval by default.

### general
- Mode: subagent
- A general-purpose agent for researching complex questions and executing multi-step tasks. Has full tool access (except todo).

### explore
- Mode: subagent
- A fast, read-only agent for exploring codebases. Cannot modify files.

### compaction
- Mode: primary (hidden)
- System agent that compacts long context into a smaller summary. Runs automatically.

### title
- Mode: primary (hidden)
- System agent that generates short session titles. Runs automatically.

### summary
- Mode: primary (hidden)
- System agent that creates session summaries. Runs automatically.

## Usage

- For primary agents, use the Tab key to cycle through them during a session.
- Subagents can be invoked automatically by primary agents, or manually by `@` mentioning a subagent (e.g., `@general help me search for this function`).

## Configure

### JSON

Configure agents in your `opencode.json` config file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "permission": {
        "edit": "allow",
        "bash": "allow"
      }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    },
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "permission": {
        "edit": "deny"
      }
    }
  }
}
```

### Markdown

You can also define agents using markdown files. Place them in:
- Global: `~/.config/opencode/agents/`
- Per-project: `.opencode/agents/`

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  edit: deny
  bash: deny
---

You are in code review mode. Focus on:
- Code quality and best practices
- Potential bugs and edge cases
- Performance implications
- Security considerations
```

The markdown file name becomes the agent name. For example, `review.md` creates a `review` agent.

## Options

- **Description** - Brief description of what the agent does. Required.
- **Temperature** - Control randomness (0.0-1.0). Lower values are more focused.
- **Max steps** - Maximum number of agentic iterations before forced text response.
- **Disable** - Set to `true` to disable the agent.
- **Prompt** - Custom system prompt file for this agent.
- **Model** - Override the model for this agent.
- **Permissions** - Manage what actions an agent can take. Keys: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `webfetch`, `websearch`, `lsp`, `skill`, `question`, `doom_loop`.
- **Mode** - `primary`, `subagent`, or `all`.
- **Hidden** - Hide a subagent from the `@` autocomplete menu.
- **Task permissions** - Control which subagents an agent can invoke via the Task tool.
- **Color** - Customize agent's visual appearance in the UI (hex color or theme color).
- **Top P** - Control response diversity (0.0-1.0).
- **Additional** - Any other options are passed through directly to the provider as model options.

## Create agents

You can create new agents using the following command:
```
opencode agent create
```

This interactive command will ask where to save the agent, what it should do, generate an appropriate system prompt and identifier, and let you select which permissions the agent should be allowed.

## Use cases

- **Build agent:** Full development work with all tools enabled.
- **Plan agent:** Analysis and planning without making changes.
- **Review agent:** Code review with read-only access.
- **Debug agent:** Focused on investigation with bash and read tools enabled.
- **Docs agent:** Documentation writing with file operations but no system commands.

## Examples

### Documentation agent

```markdown
---
description: Writes and maintains project documentation
mode: subagent
permission:
  bash: deny
---

You are a technical writer. Create clear, comprehensive documentation.
Focus on:
- Clear explanations
- Proper structure
- Code examples
- User-friendly language
```

### Security auditor

```markdown
---
description: Performs security audits and identifies vulnerabilities
mode: subagent
permission:
  edit: deny
---

You are a security expert. Focus on identifying potential security issues.
Look for:
- Input validation vulnerabilities
- Authentication and authorization flaws
- Data exposure risks
- Dependency vulnerabilities
- Configuration security issues
```
