DOCKER_COMPOSE_CMD=docker compose
DOCKER_COMPOSE_ENV=--env-file .env --env-file .env.override

DOCKER_BUILDER_NAME=mcp-builder
DOCKER_REGISTRY_NAME=ghcr.io/$(shell whoami)/mcp-servers
DOCKER_REGISTRY_TAG=$(shell git describe --tags --abbrev=0 2>/dev/null || echo "local")
DOCKER_LOCAL_PLATFORM=$(shell uname -m | sed 's/x86_64/amd64/' | sed 's/aarch64/arm64/')
DOCKER_BUILD_ARGS=--build-arg DOCKER_REGISTRY_TAG=$(DOCKER_REGISTRY_TAG) --build-arg MCP_IMAGE_REGISTRY=$(DOCKER_REGISTRY_NAME)

AGENT_PROXY_WEB_PORT=15000
AGENT_PROXY_MCP_PORT=10000
JAEGER_PORT=16686

# MCP services to build
AGENT_SDK = $(shell ls docker/sdk)
MCP_BASE = $(shell ls docker/base)
MCP_SERVICES = $(shell ls docker/mcp)

.PHONY: clean
clean:
	docker buildx rm $(DOCKER_BUILDER_NAME) || true
	docker buildx prune -f --filter "until=24h" || true
	docker system prune -f --volumes
	rm -rf ./logs/* ./reports/*.cve

.PHONY: buildx-default
buildx-default:
	docker buildx create --name $(DOCKER_BUILDER_NAME) --platform linux/$(DOCKER_LOCAL_PLATFORM) --driver docker-container --use || true
	#docker buildx use $(DOCKER_BUILDER_NAME)
	docker buildx use default || true

.PHONY: build/agentgateway
build/agentgateway: buildx-default
	docker build -t $(DOCKER_REGISTRY_NAME)/agentgateway:$(DOCKER_REGISTRY_TAG) -f docker/gateways/agentgateway/Dockerfile .

.PHONY: build/base
build/base: buildx-default
	@echo "Building MCP images..."
	@set -e; mkdir -p logs; \
	for base in $(MCP_BASE); do \
		echo "Building base image: $$base"; \
		docker build \
			--build-arg DOCKER_REGISTRY_TAG=$(DOCKER_REGISTRY_TAG) \
			--build-arg MCP_IMAGE_REGISTRY=$(DOCKER_REGISTRY_NAME) \
			-t $(DOCKER_REGISTRY_NAME)/base-$$base:$(DOCKER_REGISTRY_TAG) \
			-f docker/base/$$base/Dockerfile docker/base/$$base \
			2>&1 | tee logs/build-base-$$base.log; \
	done

.PHONY: build/mcp
build/mcp: build/base
	@set -e; mkdir -p logs; \
	for service in $(MCP_SERVICES); do \
		echo "Building MCP service: $$service -> docker build"; \
		docker build \
			--build-arg DOCKER_REGISTRY_TAG=$(DOCKER_REGISTRY_TAG) \
			--build-arg MCP_IMAGE_REGISTRY=$(DOCKER_REGISTRY_NAME) \
			-t $(DOCKER_REGISTRY_NAME)/$$service:$(DOCKER_REGISTRY_TAG) \
			-f docker/mcp/$$service/Dockerfile docker/mcp/$$service \
			2>&1 | tee logs/build-mcp-$$service.log; \
	done

.PHONY: upgrade/python
upgrade/python:
	cd docker/sdk/a2a 		&& rm -rf .venv uv.lock && uv python pin 3.13 && uv sync --upgrade
	cd docker/sdk/adk 		&& rm -rf .venv uv.lock && uv python pin 3.13 && uv sync --upgrade
	cd docker/sdk/langgraph && rm -rf .venv uv.lock && uv python pin 3.13 && uv  sync --upgrade
	cd docker/sdk/crew-ai 	&& rm -rf .venv uv.lock && uv python pin 3.13 && uv  sync --upgrade

.PHONY: build/sdk
build/sdk: build/base
	@set -e; mkdir -p logs; \
	for sdk in $(AGENT_SDK); do \
		echo "Building Agent SDK: $$sdk -> docker build"; \
		docker build \
			--build-arg DOCKER_REGISTRY_TAG=$(DOCKER_REGISTRY_TAG) \
			--build-arg MCP_IMAGE_REGISTRY=$(DOCKER_REGISTRY_NAME) \
			-t $(DOCKER_REGISTRY_NAME)/$$sdk:$(DOCKER_REGISTRY_TAG) \
			-f docker/sdk/$$sdk/Dockerfile docker/sdk/$$sdk \
			2>&1 | tee logs/build-sdk-$$sdk.log; \
	done

.PHONY: scan/docker
scan/docker: #scan docker images for vulnerabilities and report
	@set -e; \
	mkdir -p logs reports ; \
	for service in $(MCP_SERVICES) $(AGENT_SDK); do \
		echo "=== Scan MCP service: $$service"; \
		grype docker:$(DOCKER_REGISTRY_NAME)/$$service:$(DOCKER_REGISTRY_TAG) -o template -t reports/cve-report.tmpl --file reports/$$service-cve.csv --fail-on high | tee logs/scan-mcp-$$service-cve.txt; \
		echo "=== Scan Completed: $$service"; \
	done

.PHONY: scan/secrets
scan/secrets: #scan for secrets in the codebase
	@echo "Scanning for secrets in the codebase..."
	ggshield secret scan path -r . || :

.PHONY: grype-all
scan/all: upgrade/python
scan/all: scan/secrets #scan for secrets in the codebase
scan/all: scan/docker  #scan all docker images for vulnerabilities
	@set -e; \
	grype .

.PHONY: build
build: build/agentgateway build/base build/mcp build/sdk
	docker images | grep "$(DOCKER_REGISTRY_NAME)"

.PHONY: start
start: build
	docker rm -f agw_sequentialthinking
	docker rm -f agw_memory
	docker rm -f agw_time
	$(DOCKER_COMPOSE_CMD) $(DOCKER_COMPOSE_ENV) up --force-recreate --remove-orphans --detach
	@echo "Go to http://localhost:$(AGENT_PROXY_WEB_PORT) for Agent Gateway UI."
	@echo "Go to http://localhost:$(JAEGER_PORT)/jaeger/ui for the Jaeger UI."
	@echo "Go to http://localhost:$(AGENT_PROXY_MCP_PORT) for MCP Proxy."
	#agentgateway --file config.yaml

.PHONY: stop
stop:
	$(DOCKER_COMPOSE_CMD) $(DOCKER_COMPOSE_ENV) down --remove-orphans --volumes

.PHONY: logs
logs:
	docker compose logs -f

