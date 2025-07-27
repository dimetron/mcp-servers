# Use Python 3.11 slim image as base
ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-python:${DOCKER_REGISTRY_TAG}
ENV PYTHONUNBUFFERED=1

WORKDIR /app
# Install system dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv sync --frozen && \
    rm -fr build dist *.egg-info
# Copy application code
COPY agents ./agents/
RUN uv run python -m compileall -q .

COPY <<EOF /entrypoint.sh
#!/bin/sh
set -e

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${OPENAI_MODEL_NAME}"
else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export OPENAI_BASE_URL=\${MODEL_RUNNER_URL}
    export OPENAI_MODEL_NAME=openai/\${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=cannot_be_empty
fi
exec adk web --host 0.0.0.0 --port 8080 --log_level DEBUG
EOF
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S app -G appgroup -h /home/app -s /bin/sh && \
    chown -R app:appgroup /app
USER app

ENTRYPOINT [ "/entrypoint.sh" ]
