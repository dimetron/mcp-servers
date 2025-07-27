ARG BASE_IMAGE_REGISTRY=cgr.dev
FROM $BASE_IMAGE_REGISTRY/chainguard/wolfi-base:latest

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Common dependencies for all
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add curl openssl ca-certificates

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR=/app/python/.cache
ENV PATH=$PATH:/app/python/.venv/bin

# for numpy and other packages that require C extensions
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add uv

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv --python=python3.13 --system