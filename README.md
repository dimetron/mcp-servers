# MCP Playground

A comprehensive collection of **Model Context Protocol (MCP)** implementations, agent frameworks, and AI toolkit examples. 
This playground demonstrates how to build intelligent agents using different programming languages and frameworks, 
all orchestrated with Docker for seamless setup and experimentation.

## 🏗️ Project Structure

### 🤖 AI Agent SDK Examples

#### Python-Based Frameworks
- **a2a:** Multi-agent fact-checking system using the Agent2Agent SDK. Features an Auditor that coordinates Critic (web search via DuckDuckGo) and Reviser (reasoning-only) agents for collaborative fact verification
- **adk:** Multi-agent fact-checker built with Google's Agent Development Kit (ADK). Similar architecture to A2A but using ADK's orchestration patterns
- **crew-ai:** Autonomous virtual marketing team using CrewAI. Demonstrates task delegation across specialized agents (Market Analyst, Marketing Strategist, Content Creator, Creative Director) to produce complete marketing strategies
- **langgraph:** SQL query agent using LangGraph that converts natural language questions into SQL queries against a PostgreSQL database populated with the Chinook sample dataset

#### Go-Based Frameworks  
- **langchaingo:** Natural language search application using LangchainGO with DuckDuckGo integration via MCP, demonstrating zero-config web search capabilities

#### Java-Based Frameworks
- **spring-ai:** Spring Boot application showcasing Spring AI framework integration with MCP for web search via DuckDuckGo, featuring auto-configuration and enterprise-ready patterns

### 🔧 MCP Server Implementations

The project includes several purpose-built MCP servers that provide specialized capabilities:

- **memory:** Knowledge graph-based persistent memory server that enables Claude to remember information across conversations using entities, relations, and observations
- **time:** Timezone-aware time server providing current time lookup and timezone conversion capabilities using IANA timezone names
- **sequentialthinking:** Structured problem-solving server that facilitates step-by-step thinking processes with revision and branching capabilities

### 🏛️ Infrastructure Components

- **Agent Gateway:** Central orchestration service (port 15000 UI, 10000 MCP) that manages MCP server connections and provides a unified interface

- **Telemetry Stack:** Comprehensive observability with Jaeger tracing (port 16686)
- **Containerization:** Full Docker setup with multi-language base images (Python, Go, Java, Bun) and orchestrated deployments

## 🚀 Getting Started

### Prerequisites

- **Docker Desktop 4.43.0+** or **Docker Engine**
- **GPU-enabled system** (MacBook, Linux with GPU, etc.) for local model inference
- **Docker Compose 2.38.1+** (for Linux Docker Engine users)

### Quick Start

Each SDK example is self-contained and can be run independently:

```bash
# Navigate to any SDK example
cd docker/sdk/crew-ai  # or any other SDK directory

# Run with single command
make start
```

### 🧠 Inference Options

All examples support multiple inference backends:

1. **Local Models** (default): Uses ollama
2. **OpenAI Integration**: Create `secret.openai-api-key` file with your API key
3. **Docker Offload**: For high-performance remote GPU instances

## 🎯 Use Cases & Examples

### Multi-Agent Collaboration
- **Fact Checking**: A2A and ADK demonstrate how multiple agents with different tools can collaborate on verification tasks
- **Marketing Strategy**: CrewAI shows autonomous team coordination for end-to-end marketing campaign creation

### Natural Language Interfaces  
- **Database Queries**: LangGraph converts conversational questions into SQL against real datasets
- **Web Search**: LangchainGO and Spring AI demonstrate intelligent web search integration

### Memory & Context
- **Persistent Memory**: Knowledge graph storage for maintaining context across conversations
- **Structured Thinking**: Step-by-step problem decomposition with revision capabilities

## 🛠️ Development

### Building Components

```bash
# Build all services
docker compose up --build

# Build specific MCP server
cd docker/mcp/memory
docker build -t mcp/memory .

# Build SDK example
cd docker/sdk/langgraph  
docker build -t mcp-servers/langgraph .
```

### Adding New Examples

1. Create directory under `docker/sdk/your-framework/`
2. Add Dockerfile and compose.yaml
3. Implement MCP integration patterns
4. Update this README with description

## 📚 Learning Resources

Each subdirectory contains detailed READMEs with:
- Architecture diagrams
- Step-by-step setup instructions  
- Example interactions and use cases
- Customization options

## 🧹 Cleanup

```bash
# Stop and remove containers/volumes
docker compose down -v

# Remove all MCP playground images
docker images | grep mcp-servers | awk '{print $3}' | xargs docker rmi
```

## 🤝 Contributing

Contributions welcome! Whether you want to:
- Add support for new AI frameworks
- Implement additional MCP servers
- Improve documentation
- Add new agent architectures

See individual component READMEs for specific contribution guidelines.

## 📄 License

Licensed under the MIT License - see [LICENSE](LICENSE) file for details.