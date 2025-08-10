ARG BASE_IMAGE_REGISTRY=cgr.dev
FROM $BASE_IMAGE_REGISTRY/chainguard/wolfi-base:latest

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Common dependencies for all
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add curl openssl ca-certificates

# docker run --rm -it cgr.dev/chainguard/wolfi-base:latest sh
# Install SDKMAN (https://sdkman.io/)
RUN --mount=type=cache,target=/var/cache/apk,rw \
    apk update \
    && apk add bash unzip zip

ENV TERM=xterm-256color
ENV SDKMAN_DIR="/root/.sdkman"
ENV JAVA_HOME="/root/.sdkman/candidates/java/current"
ENV PATH="/root/.sdkman/candidates/java/current/bin:/root/.sdkman/candidates/maven/current/bin:$PATH"

RUN curl -s "https://get.sdkman.io" | bash && \
    bash -c "source /root/.sdkman/bin/sdkman-init.sh; sdk update;sdk list java" && \
    bash -c "source /root/.sdkman/bin/sdkman-init.sh; sdk install java 24.0.2-amzn"

WORKDIR /app

CMD ["java", "-version"]