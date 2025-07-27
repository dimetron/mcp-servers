##### Base image
ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-python:${DOCKER_REGISTRY_TAG} AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv sync --frozen && \
    rm -fr build dist *.egg-info
COPY main.py src ./
RUN uv run python -m compileall -q .

ENV AGENT_CONFIG=/app/agent.yaml

COPY <<EOF ./entrypoint.sh
#!/bin/sh
set -e

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${OPENAI_MODEL_NAME}"
    export LLM_AGENT_MODEL_PROVIDER=openai
    export LLM_AGENT_MODEL_NAME=\${OPENAI_MODEL_NAME}
else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export LLM_AGENT_MODEL_PROVIDER=docker
    export LLM_AGENT_MODEL_NAME=\${MODEL_RUNNER_MODEL}
fi
exec \$@
EOF
RUN chmod +x ./entrypoint.sh

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S app -G appgroup -h /home/app -s /bin/sh && \
    chown -R app:appgroup /app
USER app

##### Critic Agent
FROM base AS critic-agent

COPY --chown=app:app agents/critic.yaml /app/agent.yaml
CMD ["./entrypoint.sh", "python", "main.py", "--host", "0.0.0.0", "--port", "8001"]

##### Reviser Agent
FROM base AS reviser-agent

COPY --chown=app:app agents/reviser.yaml /app/agent.yaml
CMD ["./entrypoint.sh", "python", "main.py", "--host", "0.0.0.0", "--port", "8001"]

##### Auditor Agent
FROM base AS auditor-agent

COPY --chown=app:app agents/auditor.yaml /app/agent.yaml
EXPOSE 8080
CMD ["./entrypoint.sh", "adk", "web", ".", "--host", "0.0.0.0", "--port", "8080"]
# Use this to expose the agent as a web service instead of a UI
#CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8002"]
