ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-bun:${DOCKER_REGISTRY_TAG} AS builder

COPY . /app
COPY tsconfig.json /tsconfig.json

WORKDIR /app

RUN --mount=type=cache,target=/root/.bun bun update --latest
RUN --mount=type=cache,target=/root/.bun bun audit --fix
RUN --mount=type=cache,target=/root/.bun bun install
RUN --mount=type=cache,target=/root/.bun-production bun ci --ignore-scripts --omit-dev

ARG MCP_IMAGE_REGISTRY
ARG DOCKER_REGISTRY_TAG
FROM ${MCP_IMAGE_REGISTRY}/base-bun:${DOCKER_REGISTRY_TAG} AS release

COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/package.json /app/package.json

ENV NODE_ENV=production

WORKDIR /app

RUN bun ci --ignore-scripts --omit-dev

ENTRYPOINT ["bun", "dist/index.js"]