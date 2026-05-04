# Models - OpenCode Documentation

# Models

Configuring an LLM provider and model.

OpenCode uses the AI SDK and Models.dev to support 75+ LLM providers and it supports running local models.

## Providers

Most popular providers are preloaded by default. If you've added the credentials for a provider through the `/connect` command, they'll be available when you start OpenCode.

## Select a model

Once you've configured your provider you can select the model you want by typing:
```
/models
```

## Recommended models

Several models that work well with OpenCode include:
- GPT 5.2
- GPT 5.1 Codex
- Claude Opus 4.5
- Claude Sonnet 4.5
- Minimax M2.1
- Gemini 3 Pro

## Set a default

To set a default model, set the `model` key in your OpenCode config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "lmstudio/google/gemma-3n-e4b"
}
```

The format is `provider_id/model_id`. For example, `opencode/gpt-5.1-codex` for GPT 5.1 Codex using OpenCode Zen.

## Configure models

You can globally configure a model's options through the config:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "options": {
            "reasoningEffort": "high",
            "textVerbosity": "low",
            "reasoningSummary": "auto",
            "include": ["reasoning.encrypted_content"],
          },
        },
      },
    },
    "anthropic": {
      "models": {
        "claude-sonnet-4-5-20250929": {
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 16000,
            },
          },
        },
      },
    },
  },
}
```

You can also define custom variants that extend built-in ones:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "opencode": {
      "models": {
        "gpt-5": {
          "variants": {
            "high": {
              "reasoningEffort": "high",
              "textVerbosity": "low",
            },
            "low": {
              "reasoningEffort": "low",
              "textVerbosity": "low",
            },
          },
        },
      },
    },
  },
}
```

## Variants

### Built-in variants

**Anthropic:** `high` (high thinking budget, default), `max` (maximum thinking budget)

**OpenAI:** Varies by model: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`

**Google:** `low` (lower effort/token budget), `high` (higher effort/token budget)

### Custom variants

You can override existing variants or add your own:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "variants": {
            "thinking": {
              "reasoningEffort": "high",
              "textVerbosity": "low",
            },
            "fast": {
              "disabled": true,
            },
          },
        },
      },
    },
  },
}
```

### Cycle variants

Use the keybind `variant_cycle` to quickly switch between variants.

## Loading models

When OpenCode starts up, it checks for models in the following priority order:
1. The `--model` or `-m` command line flag
2. The model list in the OpenCode config
3. The last used model
4. The first model using an internal priority
