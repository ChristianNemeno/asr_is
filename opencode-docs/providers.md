# Providers - OpenCode Documentation

# Providers

Using any LLM provider in OpenCode.

OpenCode uses the AI SDK and Models.dev to support 75+ LLM providers and it supports running local models.

To add a provider you need to:

1. Add the API keys for the provider using the `/connect` command.
2. Configure the provider in your OpenCode config.

## Credentials

When you add a provider's API keys with the `/connect` command, they are stored in `~/.local/share/opencode/auth.json`.

## Config

You can customize the providers through the `provider` section in your OpenCode config.

### Base URL

You can customize the base URL for any provider by setting the `baseURL` option.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com/v1"
      }
    }
  }
}
```

## OpenCode Zen

OpenCode Zen is a list of models provided by the OpenCode team that have been tested and verified to work well with OpenCode.

1. Run `/connect` in the TUI, select OpenCode Zen, and head to opencode.ai/auth.
2. Sign in, add your billing details, and copy your API key.
3. Paste your API key.
4. Run `/models` to see the list of recommended models.

It works like any other provider and is completely optional.

## OpenCode Go

OpenCode Go is a low cost subscription plan that provides reliable access to popular open coding models.

1. Run `/connect` in the TUI, select OpenCode Go, and head to opencode.ai/auth.
2. Sign in, add your billing details, and copy your API key.
3. Paste your API key.
4. Run `/models` to see the list of recommended models.

It works like any other provider and is completely optional.

## Directory

### 302.AI

1. Head over to the 302.AI console, create an account, and generate an API key.
2. Run `/connect` and search for 302.AI.
3. Enter your 302.AI API key.
4. Run `/models` to select a model.

### Amazon Bedrock

1. Head over to the Model catalog in the Amazon Bedrock console and request access to the models you want.
2. Configure authentication using one of the following methods:

**Environment Variables (Quick Start):**
```
AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=YYY opencode
AWS_PROFILE=my-profile opencode
AWS_BEARER_TOKEN_BEDROCK=XXX opencode
```

**Configuration File (Recommended):**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile"
      }
    }
  }
}
```

Available options: `region`, `profile`, `endpoint` (for VPC endpoints).

**Authentication Methods:** AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY, AWS_PROFILE, AWS_BEARER_TOKEN_BEDROCK, AWS_WEB_IDENTITY_TOKEN_FILE / AWS_ROLE_ARN (for EKS IRSA).

**Authentication Precedence:** Bearer Token > AWS Credential Chain (Profile, access keys, shared credentials, IAM roles, Web Identity Tokens, instance metadata).

For custom inference profiles:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "amazon-bedrock": {
      "models": {
        "anthropic-claude-sonnet-4.5": {
          "id": "arn:aws:bedrock:us-east-1:xxx:application-inference-profile/yyy"
        }
      }
    }
  }
}
```

3. Run `/models` to select a model.

### Anthropic

1. Once you've signed up, run `/connect` and select Anthropic.
2. Select the Claude Pro/Max option to authenticate via browser.
3. Run `/models` to see available models.

### Atomic Chat

Configure opencode to use local models through Atomic Chat:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "atomic-chat": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Atomic Chat (local)",
      "options": {
        "baseURL": "http://127.0.0.1:1337/v1"
      },
      "models": {
        "<your-model-id>": {
          "name": "<your-model-name>"
        }
      }
    }
  }
}
```

### Azure OpenAI

1. Create an Azure OpenAI resource in the Azure portal. You'll need the resource name and API key.
2. Go to Azure AI Foundry and deploy a model (deployment name must match model name).
3. Run `/connect` and search for Azure.
4. Enter your API key.
5. Set your resource name: `AZURE_RESOURCE_NAME=XXX opencode`
6. Run `/models` to select a model.

### Azure Cognitive Services

1. Create an Azure Cognitive Services resource. You'll need the resource name and API key.
2. Go to Azure AI Foundry and deploy a model (deployment name must match model name).
3. Run `/connect` and search for Azure Cognitive Services.
4. Enter your API key.
5. Set your resource name: `AZURE_COGNITIVE_SERVICES_RESOURCE_NAME=XXX opencode`
6. Run `/models` to select a model.

### Baseten

1. Head over to Baseten, create an account, and generate an API key.
2. Run `/connect` and search for Baseten.
3. Enter your Baseten API key.
4. Run `/models` to select a model.

### Cerebras

1. Head over to the Cerebras console, create an account, and generate an API key.
2. Run `/connect` and search for Cerebras.
3. Enter your Cerebras API key.
4. Run `/models` to select a model like Qwen 3 Coder 480B.

### Cloudflare AI Gateway

1. Create a gateway in Cloudflare dashboard (AI > AI Gateway). Note your Account ID and Gateway ID.
2. Run `/connect` and search for Cloudflare AI Gateway.
3. Enter your Account ID, Gateway ID, and Cloudflare API token.
4. Run `/models` to select a model.

You can also add models through your config:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "cloudflare-ai-gateway": {
      "models": {
        "openai/gpt-4o": {},
        "anthropic/claude-sonnet-4": {}
      }
    }
  }
}
```

### Cloudflare Workers AI

1. Navigate to Workers AI in Cloudflare dashboard and note your Account ID and create an API token.
2. Run `/connect` and search for Cloudflare Workers AI.
3. Enter your Account ID and API key.
4. Run `/models` to select a model.

### Cortecs

1. Head over to the Cortecs console, create an account, and generate an API key.
2. Run `/connect` and search for Cortecs.
3. Enter your Cortecs API key.
4. Run `/models` to select a model like Kimi K2 Instruct.

### DeepSeek

1. Head over to the DeepSeek console, create an account, and click Create new API key.
2. Run `/connect` and search for DeepSeek.
3. Enter your DeepSeek API key.
4. Run `/models` to select a DeepSeek model like DeepSeek V4 Pro.

### Deep Infra

1. Head over to the Deep Infra dashboard, create an account, and generate an API key.
2. Run `/connect` and search for Deep Infra.
3. Enter your Deep Infra API key.
4. Run `/models` to select a model.

### Firmware

1. Head over to the Firmware dashboard, create an account, and generate an API key.
2. Run `/connect` and search for Firmware.
3. Enter your Firmware API key.
4. Run `/models` to select a model.

### Fireworks AI

1. Head over to the Fireworks AI console, create an account, and click Create API Key.
2. Run `/connect` and search for Fireworks AI.
3. Enter your Fireworks AI API key.
4. Run `/models` to select a model like Kimi K2 Instruct.

### GitLab Duo

OpenCode integrates with the GitLab Duo Agent Platform. Requires a Premium or Ultimate GitLab subscription.

1. Run `/connect` and select GitLab.
2. Choose authentication method (OAuth recommended or Personal Access Token).
3. Run `/models` to see available models.

Available models: `duo-chat-haiku-4-5` (Default), `duo-chat-sonnet-4-5`, `duo-chat-opus-4-5`.

For self-hosted GitLab instances:
```
GITLAB_INSTANCE_URL=https://gitlab.company.com
GITLAB_AI_GATEWAY_URL=https://ai-gateway.company.com
GITLAB_TOKEN=glpat-...
```

Configuration via `opencode.json`:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "gitlab": {
      "options": {
        "instanceUrl": "https://gitlab.com"
      }
    }
  }
}
```

### GitHub Copilot

1. Run `/connect` and search for GitHub Copilot.
2. Navigate to github.com/login/device and enter the code.
3. Run `/models` to select a model.

### Google Vertex AI

1. Check available models in Model Garden (Google Cloud Console). You need a Google Cloud project with Vertex AI API enabled.
2. Set environment variables:
   - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
   - `VERTEX_LOCATION` (optional): Region for Vertex AI (defaults to `global`)
   - Authentication: `GOOGLE_APPLICATION_CREDENTIALS` or `gcloud auth application-default login`
3. Run `/models` to select a model.

### Groq

1. Head over to the Groq console, click Create API Key, and copy the key.
2. Run `/connect` and search for Groq.
3. Enter your API key.
4. Run `/models` to select a model.

### Hugging Face

1. Create a token in Hugging Face settings with permission for Inference Providers.
2. Run `/connect` and search for Hugging Face.
3. Enter your Hugging Face token.
4. Run `/models` to select a model like Kimi-K2-Instruct or GLM-4.6.

### Helicone

Helicone is an LLM observability platform with an AI Gateway that routes requests to the appropriate provider automatically.

1. Head over to Helicone, create an account, and generate an API key.
2. Run `/connect` and search for Helicone.
3. Enter your Helicone API key.
4. Run `/models` to select a model.

Optional custom configuration:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "helicone": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Helicone",
      "options": {
        "baseURL": "https://ai-gateway.helicone.ai",
        "headers": {
          "Helicone-Cache-Enabled": "true",
          "Helicone-User-Id": "opencode"
        }
      },
      "models": {
        "gpt-4o": { "name": "GPT-4o" },
        "claude-sonnet-4-20250514": { "name": "Claude Sonnet 4" }
      }
    }
  }
}
```

### llama.cpp

Configure opencode to use local models through llama.cpp's llama-server:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "llama.cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-server (local)",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "qwen3-coder:a3b": {
          "name": "Qwen3-Coder: a3b-30b (local)",
          "limit": {
            "context": 128000,
            "output": 65536
          }
        }
      }
    }
  }
}
```

### IO.NET

1. Head over to the IO.NET console, create an account, and generate an API key.
2. Run `/connect` and search for IO.NET.
3. Enter your IO.NET API key.
4. Run `/models` to select a model.

### LM Studio

Configure opencode to use local models through LM Studio:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1"
      },
      "models": {
        "google/gemma-3n-e4b": {
          "name": "Gemma 3n-e4b (local)"
        }
      }
    }
  }
}
```

### Moonshot AI

1. Head over to the Moonshot AI console, create an account, and click Create API key.
2. Run `/connect` and search for Moonshot AI.
3. Enter your Moonshot API key.
4. Run `/models` to select Kimi K2.

### MiniMax

1. Head over to the MiniMax API Console, create an account, and generate an API key.
2. Run `/connect` and search for MiniMax.
3. Enter your MiniMax API key.
4. Run `/models` to select a model like M2.1.

### NVIDIA

1. Head over to build.nvidia.com, create an account, and generate an API key.
2. Run `/connect` and search for NVIDIA.
3. Enter your NVIDIA API key.
4. Run `/models` to select a model like nemotron-3-super-120b-a12b.

For on-prem / NIM:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "nvidia": {
      "options": {
        "baseURL": "http://localhost:8000/v1"
      }
    }
  }
}
```

### Nebius Token Factory

1. Head over to the Nebius Token Factory console, create an account, and click Add Key.
2. Run `/connect` and search for Nebius Token Factory.
3. Enter your Nebius Token Factory API key.
4. Run `/models` to select a model like Kimi K2 Instruct.

### Ollama

Configure opencode to use local models through Ollama:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "llama2": {
          "name": "Llama 2"
        }
      }
    }
  }
}
```

### Ollama Cloud

1. Sign in at ollama.com, navigate to Settings > Keys, and generate an API key.
2. Run `/connect` and search for Ollama Cloud.
3. Enter your Ollama Cloud API key.
4. Pull model information locally: `ollama pull gpt-oss:20b-cloud`
5. Run `/models` to select a model.

### OpenAI

1. Once you've signed up for ChatGPT Plus or Pro, run `/connect` and select OpenAI.
2. Select ChatGPT Plus/Pro to authenticate via browser, or manually enter an API key.
3. Run `/models` to see available models.

### OpenCode Zen

1. Sign in to OpenCode Zen and click Create API Key.
2. Run `/connect` and search for OpenCode Zen.
3. Enter your OpenCode API key.
4. Run `/models` to select a model like Qwen 3 Coder 480B.

### OpenRouter

1. Head over to the OpenRouter dashboard, click Create API Key, and copy the key.
2. Run `/connect` and search for OpenRouter.
3. Enter your API key.
4. Run `/models` to select a model.

Add additional models:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openrouter": {
      "models": {
        "somecoolnewmodel": {}
      }
    }
  }
}
```

Customize provider routing:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openrouter": {
      "models": {
        "moonshotai/kimi-k2": {
          "options": {
            "provider": {
              "order": ["baseten"],
              "allow_fallbacks": false
            }
          }
        }
      }
    }
  }
}
```

### LLM Gateway

1. Head over to the LLM Gateway dashboard, click Create API Key, and copy the key.
2. Run `/connect` and search for LLM Gateway.
3. Enter your API key.
4. Run `/models` to select a model.

Add additional models:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "llmgateway": {
      "models": {
        "glm-4.7": { "name": "GLM 4.7" },
        "gpt-5.2": { "name": "GPT-5.2" },
        "gemini-2.5-pro": { "name": "Gemini 2.5 Pro" },
        "claude-3-5-sonnet-20241022": { "name": "Claude 3.5 Sonnet" }
      }
    }
  }
}
```

### SAP AI Core

1. Go to your SAP BTP Cockpit, navigate to your SAP AI Core service instance, and create a service key.
2. Run `/connect` and search for SAP AI Core.
3. Enter your service key JSON, or set the `AICORE_SERVICE_KEY` environment variable.
4. Optionally set `AICORE_DEPLOYMENT_ID` and `AICORE_RESOURCE_GROUP`.
5. Run `/models` to select from 40+ available models.

### STACKIT

1. Head over to STACKIT Portal, navigate to AI Model Serving, and create an auth token.
2. Run `/connect` and search for STACKIT.
3. Enter your STACKIT auth token.
4. Run `/models` to select from available models.

### OVHcloud AI Endpoints

1. Navigate to OVHcloud Public Cloud > AI & Machine Learning > AI Endpoints > API Keys, create a new API key.
2. Run `/connect` and search for OVHcloud AI Endpoints.
3. Enter your API key.
4. Run `/models` to select a model like gpt-oss-120b.

### Scaleway

1. Head over to the Scaleway Console IAM settings to generate a new API key.
2. Run `/connect` and search for Scaleway.
3. Enter your Scaleway API key.
4. Run `/models` to select a model like devstral-2-123b-instruct-2512 or gpt-oss-120b.

### Together AI

1. Head over to the Together AI console, create an account, and click Add Key.
2. Run `/connect` and search for Together AI.
3. Enter your Together AI API key.
4. Run `/models` to select a model like Kimi K2 Instruct.

### Venice AI

1. Head over to the Venice AI console, create an account, and generate an API key.
2. Run `/connect` and search for Venice AI.
3. Enter your Venice AI API key.
4. Run `/models` to select a model like Llama 3.3 70B.

### Vercel AI Gateway

1. Navigate to Vercel dashboard > AI Gateway > API keys, create a new API key.
2. Run `/connect` and search for Vercel AI Gateway.
3. Enter your API key.
4. Run `/models` to select a model.

Customize provider routing:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "vercel": {
      "models": {
        "anthropic/claude-sonnet-4": {
          "options": {
            "order": ["anthropic", "vertex"]
          }
        }
      }
    }
  }
}
```

Useful routing options: `order` (provider sequence to try), `only` (restrict to specific providers), `zeroDataRetention` (only use providers with zero data retention policies).

### xAI

1. Head over to the xAI console, create an account, and generate an API key.
2. Run `/connect` and search for xAI.
3. Enter your xAI API key.
4. Run `/models` to select a model like Grok Beta.

### Z.AI

1. Head over to the Z.AI API console, create an account, and click Create a new API key.
2. Run `/connect` and search for Z.AI.
3. If subscribed to the GLM Coding Plan, select Z.AI Coding Plan.
4. Enter your Z.AI API key.
5. Run `/models` to select a model like GLM-4.7.

### ZenMux

1. Head over to the ZenMux dashboard, click Create API Key, and copy the key.
2. Run `/connect` and search for ZenMux.
3. Enter your API key.
4. Run `/models` to select a model.

Add additional models:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "zenmux": {
      "models": {
        "somecoolnewmodel": {}
      }
    }
  }
}
```

## Custom provider

To add any OpenAI-compatible provider not listed in `/connect`:

1. Run `/connect` and scroll down to Other.
2. Enter a unique ID for the provider.
3. Enter your API key.
4. Create or update `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My AI Provider Display Name",
      "options": {
        "baseURL": "https://api.myprovider.com/v1"
      },
      "models": {
        "my-model-name": {
          "name": "My Model Display Name"
        }
      }
    }
  }
}
```

Configuration options:
- `npm`: AI SDK package to use (`@ai-sdk/openai-compatible` for `/v1/chat/completions`, `@ai-sdk/openai` for `/v1/responses`)
- `name`: Display name in UI
- `models`: Available models
- `options.baseURL`: API endpoint URL
- `options.apiKey`: Optionally set the API key
- `options.headers`: Optionally set custom headers

Advanced example:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My AI Provider",
      "options": {
        "baseURL": "https://api.myprovider.com/v1",
        "apiKey": "{env:ANTHROPIC_API_KEY}",
        "headers": {
          "Authorization": "Bearer custom-token"
        }
      },
      "models": {
        "my-model-name": {
          "name": "My Model Display Name",
          "limit": {
            "context": 200000,
            "output": 65536
          }
        }
      }
    }
  }
}
```

## Troubleshooting

If you are having trouble configuring a provider:

1. Check the auth setup: Run `opencode auth list` to see if the credentials are added.
2. For custom providers, make sure the provider ID used in `/connect` matches the ID in your opencode config.
3. The right npm package is used for the provider (`@ai-sdk/openai-compatible` for OpenAI-compatible, `@ai-sdk/openai` for `/v1/responses`, etc.).
4. Check the correct API endpoint is used in `options.baseURL`.
