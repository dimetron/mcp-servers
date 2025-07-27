ARG BASE_IMAGE_REGISTRY=cgr.dev
FROM $BASE_IMAGE_REGISTRY/chainguard/wolfi-base:latest

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Common dependencies for all
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add curl openssl ca-certificates

# Install Bun (https://bun.sh/) nodejs runtime
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add bun

### Docker Entrypoint
ENTRYPOINT [ "bun" ]
CMD [ "--version" ]