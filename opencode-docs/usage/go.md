# Go - OpenCode Documentation

# Go

Low cost subscription for open coding models.

OpenCode Go is a low cost subscription — $5 for your first month, then $10/month — that gives you reliable access to popular open coding models.

OpenCode Go is currently in beta. Go works like any other provider in OpenCode. You subscribe to OpenCode Go and get your API key. It's completely optional and you don't need to use it to use OpenCode.

It is designed primarily for international users, with models hosted in the US, EU, and Singapore for stable global access.

## Background

Open models have gotten really good. They now reach performance close to proprietary models for coding tasks. And because many providers can serve them competitively, they are usually far cheaper. However, getting reliable, low latency access to them can be difficult.

To fix this:
- We tested a select group of open models and talked to their teams about how to best run them.
- We then worked with a few providers to make sure these were being served correctly.
- Finally, we benchmarked the combination of the model/provider and came up with a list that we feel good recommending.

## How it works

1. You sign in to OpenCode Zen, subscribe to Go, and copy your API key.
2. You run `/connect` in the TUI, select OpenCode Go, and paste your API key.
3. Run `/models` in the TUI to see the list of models available through Go.

Current models include: GLM-5, GLM-5.1, Kimi K2.5, Kimi K2.6, MiMo-V2-Pro, MiMo-V2-Omni, MiMo-V2.5-Pro, MiMo-V2.5, MiniMax M2.5, MiniMax M2.7, Qwen3.5 Plus, Qwen3.6 Plus, DeepSeek V4 Pro, DeepSeek V4 Flash.

## Usage limits

OpenCode Go includes the following limits:
- 5 hour limit — $12 of usage
- Weekly limit — $30 of usage
- Monthly limit — $60 of usage

Limits are defined in dollar value. Cheaper models allow for more requests, while higher-cost models allow for fewer. You can track your current usage in the console.

If you reach the usage limit, you can continue using the free models.

If you also have credits on your Zen balance, you can enable the "Use balance" option in the console. When enabled, Go will fall back to your Zen balance after you've reached your usage limits.

## Endpoints

| Model | Model ID | Endpoint | AI SDK Package |
|---|---|---|---|
| GLM-5.1 | glm-5.1 | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| GLM-5 | glm-5 | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| Kimi K2.5 | kimi-k2.5 | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| Kimi K2.6 | kimi-k2.6 | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| DeepSeek V4 Pro | deepseek-v4-pro | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| DeepSeek V4 Flash | deepseek-v4-flash | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| MiMo-V2-Pro | mimo-v2-pro | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| MiMo-V2-Omni | mimo-v2-omni | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| MiMo-V2.5-Pro | mimo-v2.5-pro | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| MiMo-V2.5 | mimo-v2.5 | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/openai-compatible |
| MiniMax M2.7 | minimax-m2.7 | https://opencode.ai/zen/go/v1/messages | @ai-sdk/anthropic |
| MiniMax M2.5 | minimax-m2.5 | https://opencode.ai/zen/go/v1/messages | @ai-sdk/anthropic |
| Qwen3.6 Plus | qwen3.6-plus | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/alibaba |
| Qwen3.5 Plus | qwen3.5-plus | https://opencode.ai/zen/go/v1/chat/completions | @ai-sdk/alibaba |

The model id in your OpenCode config uses the format `opencode-go/<model-id>`. For example, for Kimi K2.6, you would use `opencode-go/kimi-k2.6`.

## Models

You can fetch the full list of available models and their metadata from: https://opencode.ai/zen/go/v1/models

## Privacy

The plan is designed primarily for international users, with models hosted in the US, EU, and Singapore for stable global access. Our providers follow a zero-retention policy and do not use your data for model training.

## Goals

We created OpenCode Go to:
- Make AI coding accessible to more people with a low cost subscription.
- Provide reliable access to the best open coding models.
- Curate models that are tested and benchmarked for coding agent use.
- Have no lock-in by allowing you to use any other provider with OpenCode as well.
