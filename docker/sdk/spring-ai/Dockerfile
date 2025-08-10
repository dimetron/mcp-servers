# ---- Stage 1: Build the app ----
ARG MCP_IMAGE_REGISTRY=ghcr.io/dimetron/mcp-servers
ARG DOCKER_REGISTRY_TAG=local
FROM ${MCP_IMAGE_REGISTRY}/base-java:${DOCKER_REGISTRY_TAG} AS builder

WORKDIR /build

#install maven
RUN bash -c "source /root/.sdkman/bin/sdkman-init.sh; sdk install maven" && \
    ls /root/.sdkman/candidates/maven/current/bin && \
    which mvn

# Only copy metadata first to cache dependencies
COPY pom.xml ./
RUN mvn dependency:go-offline -B

# Now copy the rest of the app
COPY src ./src
RUN mvn package -DskipTests -B

# ---- Stage 2: Runtime image ----
FROM ${MCP_IMAGE_REGISTRY}/base-java:${DOCKER_REGISTRY_TAG} AS app

WORKDIR /app

# Copy only the built jar from the builder stage
COPY --from=builder /build/target/*.jar app.jar

ENV SPRING_PROFILES_ACTIVE=prod
COPY <<EOF entrypoint.sh
#!/bin/sh

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${MODEL_NAME}"
    export OPENAI_BASE_URL=https://api.openai.com/v1
else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export OPENAI_BASE_URL=\${MODEL_RUNNER_URL}
    export OPENAI_MODEL_NAME=\${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=cannot_be_empty
fi

# spring.ai expects the base URL to omit the /v1/? suffix
export OPENAI_BASE_URL=\${OPENAI_BASE_URL%/}
export OPENAI_BASE_URL=\${OPENAI_BASE_URL%/v1}
exec java -jar app.jar
EOF
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
