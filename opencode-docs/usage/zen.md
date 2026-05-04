# Zen - OpenCode Documentation

# Zen

Curated list of models provided by OpenCode.

OpenCode Zen is a list of tested and verified models provided by the OpenCode team. Zen works like any other provider in OpenCode. You login to OpenCode Zen and get your API key. It's completely optional and you don't need to use it to use OpenCode.

## Background

There are a large number of models out there but only a few work well as coding agents. Additionally, most providers are configured very differently, so you get very different performance and quality.

To fix this:
- We tested a select group of models and talked to their teams about how to best run them.
- We then worked with a few providers to make sure these were being served correctly.
- Finally, we benchmarked the combination of the model/provider and came up with a list that we feel good recommending.

## How it works

OpenCode Zen works like any other provider in OpenCode:
1. You sign in to OpenCode Zen, add your billing details, and copy your API key.
2. You run `/connect` in the TUI, select OpenCode Zen, and paste your API key.
3. Run `/models` in the TUI to see the list of models we recommend.

You are charged per request and you can add credits to your account.

## Endpoints

| Model | Model ID | Endpoint | AI SDK Package |
|---|---|---|---|
| GPT 5.5 | gpt-5.5 | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.5 Pro | gpt-5.5-pro | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.4 | gpt-5.4 | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.4 Pro | gpt-5.4-pro | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.4 Mini | gpt-5.4-mini | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.4 Nano | gpt-5.4-nano | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.3 Codex | gpt-5.3-codex | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.3 Codex Spark | gpt-5.3-codex-spark | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.2 | gpt-5.2 | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.2 Codex | gpt-5.2-codex | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.1 | gpt-5.1 | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.1 Codex | gpt-5.1-codex | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.1 Codex Max | gpt-5.1-codex-max | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5.1 Codex Mini | gpt-5.1-codex-mini | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5 | gpt-5 | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5 Codex | gpt-5-codex | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| GPT 5 Nano | gpt-5-nano | https://opencode.ai/zen/v1/responses | @ai-sdk/openai |
| Claude Opus 4.7 | claude-opus-4-7 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Opus 4.6 | claude-opus-4-6 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Opus 4.5 | claude-opus-4-5 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Opus 4.1 | claude-opus-4-1 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Sonnet 4.6 | claude-sonnet-4-6 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Sonnet 4.5 | claude-sonnet-4-5 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Sonnet 4 | claude-sonnet-4 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Haiku 4.5 | claude-haiku-4-5 | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Claude Haiku 3.5 | claude-3-5-haiku | https://opencode.ai/zen/v1/messages | @ai-sdk/anthropic |
| Gemini 3.1 Pro | gemini-3.1-pro | https://opencode.ai/zen/v1/models/gemini-3.1-pro | @ai-sdk/google |
| Gemini 3 Flash | gemini-3-flash | https://opencode.ai/zen/v1/models/gemini-3-flash | @ai-sdk/google |
| Qwen3.6 Plus | qwen3.6-plus | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Qwen3.5 Plus | qwen3.5-plus | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| MiniMax M2.7 | minimax-m2.7 | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| MiniMax M2.5 | minimax-m2.5 | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| MiniMax M2.5 Free | minimax-m2.5-free | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| GLM 5.1 | glm-5.1 | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| GLM 5 | glm-5 | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Kimi K2.5 | kimi-k2.5 | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Kimi K2.6 | kimi-k2.6 | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Big Pickle | big-pickle | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Ling 2.6 Flash | ling-2.6-flash | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Hy3 Preview Free | hy3-preview-free | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |
| Nemotron 3 Super Free | nemotron-3-super-free | https://opencode.ai/zen/v1/chat/completions | @ai-sdk/openai-compatible |

The model id in your OpenCode config uses the format `opencode/<model-id>`. For example, for GPT 5.5, you would use `opencode/gpt-5.5`.

## Models

You can fetch the full list of available models and their metadata from: https://opencode.ai/zen/v1/models

## Pricing

We support a pay-as-you-go model. Below are the prices per 1M tokens.

Free models: Big Pickle (Free), MiniMax M2.5 Free (Free), Ling 2.6 Flash Free (Free), Hy3 Preview Free (Free), Nemotron 3 Super Free (Free), GPT 5 Nano (Free).

Credit card fees are passed along at cost (4.4% + $0.30 per transaction); we don't charge anything beyond that.

## Auto-reload

If your balance goes below $5, Zen will automatically reload $20. You can change the auto-reload amount. You can also disable auto-reload entirely.

## Monthly limits

You can also set a monthly usage limit for the entire workspace and for each member of your team.

## Deprecated models

Models may be deprecated over time. Check the Zen page for the latest list of deprecated models and their deprecation dates.

## Privacy

All our models are hosted in the US. Our providers follow a zero-retention policy and do not use your data for model training, with exceptions for free models and certain providers as documented on the Zen page.

## For Teams

Zen also works great for teams. You can invite teammates, assign roles, curate the models your team uses, and more.

### Roles

- **Admin:** Manage models, members, API keys, and billing
- **Member:** Manage only their own API keys

### Model access

Admins can enable or disable specific models for the workspace. Requests made to a disabled model will return an error.

### Bring your own key

You can use your own OpenAI or Anthropic API keys while still accessing other models in Zen. When you use your own keys, tokens are billed directly by the provider, not by Zen.

## Goals

We created OpenCode Zen to:
- Benchmark the best models/providers for coding agents.
- Have access to the highest quality options.
- Pass along any price drops by selling at cost.
- Have no lock-in by allowing you to use it with any other coding agent.
