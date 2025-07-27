ARG BASE_IMAGE_REGISTRY=cgr.dev
FROM $BASE_IMAGE_REGISTRY/chainguard/wolfi-base:latest

### Install Dependencies
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update && apk add  \
    curl openssl ca-certificates docker-cli

ARG TARGETARCH
RUN mkdir -p /usr/local/bin \
    && curl -L https://github.com/agentgateway/agentgateway/releases/download/v0.6.2/agentgateway-linux-${TARGETARCH} -o /usr/local/bin/agentgateway \
    && chmod +x /usr/local/bin/agentgateway \
    && agentgateway --version

ENV PATH="/usr/local/bin:${PATH}"
ENV OTLP_ENDPOINT="127.0.0.1:4317"
ENV ADMIN_ADDR="0.0.0.0:15000"
CMD ["agentgateway", "--file", "/etc/config.yaml"]
