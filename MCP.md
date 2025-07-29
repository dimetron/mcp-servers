### Using MCP Servers

```json

{
  "servers": {
    "kagent-tools": {
      "command": "kagent-tools",
      "args": [
        "--stdio",
        "--kubeconfig",
        "~/.kube/config"
      ]
    },
    "perplexity-ask": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "PERPLEXITY_API_KEY=your_perplexity_api_key_here",
        "ghcr.io/dimetron/mcp-servers/perplexity-ask:local"
      ]
    },
    "github": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    },
    "sequentialthinking": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "ghcr.io/dimetron/mcp-servers/sequentialthinking:local"
      ]
    },
    "memory": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e",
        "MEMORY_FILE_PATH=/app/memory.json",
        "-v",
        "./memory.json:/app/memory.json",
        "ghcr.io/dimetron/mcp-servers/memory:local"
      ]
    }
  }
}

```