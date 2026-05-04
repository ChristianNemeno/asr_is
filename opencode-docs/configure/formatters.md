# Formatters - OpenCode Documentation

# Formatters

OpenCode uses language specific formatters.

OpenCode can format files after they are written or edited using language-specific formatters. Formatters are disabled by default; enable them in your config before OpenCode will run them.

## Built-in

| Formatter | Extensions | Requirements |
|---|---|---|
| air | .r | `air` command available |
| biome | .js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml, and more | biome.json(c) config file |
| cargofmt | .rs | `cargo fmt` command available |
| clang-format | .c, .cpp, .h, .hpp, .ino, and more | .clang-format config file |
| cljfmt | .clj, .cljs, .cljc, .edn | `cljfmt` command available |
| dart | .dart | `dart` command available |
| dfmt | .d | `dfmt` command available |
| gleam | .gleam | `gleam` command available |
| gofmt | .go | `gofmt` command available |
| htmlbeautifier | .erb, .html.erb | `htmlbeautifier` command available |
| ktlint | .kt, .kts | `ktlint` command available |
| mix | .ex, .exs, .eex, .heex, .leex, .neex, .sface | `mix` command available |
| nixfmt | .nix | `nixfmt` command available |
| ocamlformat | .ml, .mli | `ocamlformat` command available and .ocamlformat config file |
| ormolu | .hs | `ormolu` command available |
| oxfmt (Experimental) | .js, .jsx, .ts, .tsx | oxfmt dependency in package.json and experimental env flag |
| pint | .php | `laravel/pint` dependency in composer.json |
| prettier | .js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml, and more | prettier dependency in package.json |
| rubocop | .rb, .rake, .gemspec, .ru | `rubocop` command available |
| ruff | .py, .pyi | `ruff` command available with config |
| rustfmt | .rs | `rustfmt` command available |
| shfmt | .sh, .bash | `shfmt` command available |
| standardrb | .rb, .rake, .gemspec, .ru | `standardrb` command available |
| terraform | .tf, .tfvars | `terraform` command available |
| uv | .py, .pyi | `uv` command available |
| zig | .zig, .zon | `zig` command available |

## How it works

When OpenCode writes or edits a file and formatters are enabled, it:
1. Checks the file extension against all enabled formatters.
2. Runs the appropriate formatter command on the file.
3. Applies the formatting changes.

## Configure

To enable all built-in formatters, set `formatter` to `true`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": true
}
```

Use an object to keep built-ins enabled while configuring overrides or custom formatters:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {}
}
```

## Disabling formatters

To disable all formatters, set `formatter` to `false`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": false
}
```

To disable a specific formatter:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {
    "prettier": {
      "disabled": true
    }
  }
}
```

## Custom formatters

You can configure built-in formatters with options, or add custom formatters:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": {
    "prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": {
        "NODE_ENV": "development"
      },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    },
    "custom-markdown-formatter": {
      "command": ["deno", "fmt", "$FILE"],
      "extensions": [".md"]
    }
  }
}
```

The `$FILE` placeholder will be replaced with the path to the file being formatted.
