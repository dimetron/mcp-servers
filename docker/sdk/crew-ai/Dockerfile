ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-python:${DOCKER_REGISTRY_TAG}

# for numpy and other packages that require C extensions
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add libstdc++ libgcc build-base

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy \
    uv sync --frozen && \
    rm -fr build dist *.egg-info
COPY . .
COPY <<EOF /entrypoint.sh
#!/bin/sh

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
exec python -m marketing_posts.main
EOF
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
