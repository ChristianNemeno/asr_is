# Rules - OpenCode Documentation

# Rules

Set custom instructions for OpenCode.

You can provide custom instructions to OpenCode by creating an AGENTS.md file. This is similar to Cursor's rules. It contains instructions that will be included in the LLM's context to customize its behavior for your specific project.

## Initialize

To create a new AGENTS.md file, run the `/init` command in OpenCode.

`/init` scans the important files in your repo, may ask a couple of targeted questions when the codebase cannot answer them, and then creates or updates AGENTS.md with concise project-specific guidance.

It focuses on:
- Build, lint, and test commands
- Command order and focused verification steps
- Architecture and repo structure that are not obvious from filenames alone
- Project-specific conventions, setup quirks, and operational gotchas
- References to existing instruction sources like Cursor or Copilot rules

## Example

```markdown
# SST v3 Monorepo Project

This is an SST v3 monorepo with TypeScript. The project uses bun workspaces for package management.

## Project Structure
- `packages/` - Contains all workspace packages (functions, core, web, etc.)
- `infra/` - Infrastructure definitions split by service (storage.ts, api.ts, web.ts)
- `sst.config.ts` - Main SST configuration with dynamic imports

## Code Standards
- Use TypeScript with strict mode enabled
- Shared code goes in `packages/core/` with proper exports configuration
- Functions go in `packages/functions/`
- Infrastructure should be split into logical files in `infra/`

## Monorepo Conventions
- Import shared modules using workspace names: `@my-app/core/example`
```

## Types

OpenCode supports reading the AGENTS.md file from multiple locations.

### Project

Place an AGENTS.md in your project root for project-specific rules. These only apply when you are working in this directory or its sub-directories.

### Global

You can also have global rules in a `~/.config/opencode/AGENTS.md` file. This gets applied across all OpenCode sessions.

### Claude Code Compatibility

For users migrating from Claude Code, OpenCode supports Claude Code's file conventions as fallbacks:
- Project rules: `CLAUDE.md` in your project directory (used if no AGENTS.md exists)
- Global rules: `~/.claude/CLAUDE.md` (used if no `~/.config/opencode/AGENTS.md` exists)
- Skills: `~/.claude/skills/`

To disable Claude Code compatibility:
```
export OPENCODE_DISABLE_CLAUDE_CODE=1        # Disable all .claude support
export OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1 # Disable only ~/.claude/CLAUDE.md
export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1 # Disable only .claude/skills
```

## Precedence

When OpenCode starts, it looks for rule files in this order:
1. Local files by traversing up from the current directory (AGENTS.md, CLAUDE.md)
2. Global file at `~/.config/opencode/AGENTS.md`
3. Claude Code file at `~/.claude/CLAUDE.md` (unless disabled)

The first matching file wins in each category.

## Custom Instructions

You can specify custom instruction files in your `opencode.json` or the global config.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"]
}
```

You can also use remote URLs to load instructions from the web.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"]
}
```

Remote instructions are fetched with a 5 second timeout. All instruction files are combined with your AGENTS.md files.

## Referencing External Files

### Using opencode.json

The recommended approach is to use the `instructions` field in `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["docs/development-standards.md", "test/testing-guidelines.md", "packages/*/AGENTS.md"]
}
```

### Manual Instructions in AGENTS.md

You can teach OpenCode to read external files by providing explicit instructions in your AGENTS.md.

```markdown
## External File Loading
CRITICAL: When you encounter a file reference (e.g., @rules/general.md), use your Read tool to load it on a need-to-know basis.

Instructions:
- Do NOT preemptively load all references - use lazy loading based on actual need
- When loaded, treat content as mandatory instructions that override defaults
- Follow references recursively when needed

## Development Guidelines
For TypeScript code style and best practices: @docs/typescript-guidelines.md
For React component architecture and hooks patterns: @docs/react-patterns.md
```

For monorepos or projects with shared standards, using `opencode.json` with glob patterns is more maintainable than manual instructions.
