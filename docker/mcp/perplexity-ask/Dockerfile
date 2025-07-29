ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-bun:${DOCKER_REGISTRY_TAG} AS builder

COPY . /app
WORKDIR /app

RUN --mount=type=cache,target=/root/.bun bun update --latest
RUN --mount=type=cache,target=/root/.bun bun audit --fix
RUN --mount=type=cache,target=/root/.bun bun install
RUN --mount=type=cache,target=/root/.bun bun install

ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-bun:${DOCKER_REGISTRY_TAG} AS release

WORKDIR /app

COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package.json /app/package.json

ENV NODE_ENV=production
RUN bun ci --ignore-scripts --omit-dev

ENTRYPOINT ["bun", "dist/index.js"]
