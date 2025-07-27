from abc import abstractmethod
import os
from typing import Any, AsyncIterable, Callable, Sequence, Type, TypeVar

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
)
from google.adk.agents.base_agent import BaseAgent as ADKBaseAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from starlette.applications import Starlette
import yaml

from ..executor import ADKAgentExecutor
from .base_agent import BaseAgent
from .config import AgentConfig, AgentType
from .proxy import A2AProxyAgent

SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

T = TypeVar("T", bound="Agent")

_agent_classes: dict[AgentType, Type["Agent"]] = {}


class Agent(BaseAgent, ADKBaseAgent):
    """
    Base class for all agents.
    """

    def __init__(self, config: AgentConfig):
        self._config = config
        self._agent = self.build_agent()
        self._user_id = config.agent_id
        self._runner = Runner(
            app_name=self._config.agent_id,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def app(self, port: int) -> Starlette:
        request_handler = DefaultRequestHandler(
            agent_executor=ADKAgentExecutor(self),
            task_store=InMemoryTaskStore(),
        )

        capabilities = AgentCapabilities(streaming=True)

        agent_card = AgentCard(
            name=self._config.name,
            capabilities=capabilities,
            description=self._config.description or "",
            skills=self._config.skills or [],
            url=f"http://0.0.0.0:{port}/",
            version="1.0.0",
            defaultInputModes=SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=SUPPORTED_CONTENT_TYPES,
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        return server.build()

    def get_processing_message(self) -> str:
        return "Processing..."

    def build_agent(self) -> ADKBaseAgent:
        sub_agents: Sequence[ADKBaseAgent] = (
            [A2AProxyAgent(a2a_url=url) for url in self._config.sub_agents]
            if self._config.sub_agents
            else []
        )
        return self._build_agent(list(sub_agents))

    @abstractmethod
    def _build_agent(self, sub_agents: list[ADKBaseAgent]) -> ADKBaseAgent:
        pass

    async def stream(
        self, query: str, session_id: str
    ) -> AsyncIterable[dict[str, Any]]:
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        accumulated_response = ""
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response: str | dict[str, Any] = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = "\n".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif (
                    event.content
                    and event.content.parts
                    and any(p.function_response for p in event.content.parts)
                ):
                    # Find the first part with function_response
                    for p in event.content.parts:
                        if p.function_response:
                            response = p.function_response.model_dump()
                            break

                # Use accumulated response if available, otherwise use final response
                final_content = (
                    accumulated_response if accumulated_response else response
                )
                yield {
                    "is_task_complete": True,
                    "content": final_content,
                }
            else:
                # Handle streaming content - accumulate partial responses
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            accumulated_response += part.text
                yield {
                    "is_task_complete": False,
                    "updates": self.get_processing_message(),
                }

    def __str__(self):
        return f"Agent(name={self._config.name})"

    @staticmethod
    def from_yaml_filename(filename: str) -> "Agent":
        """
        Create an agent instance from a YAML configuration file.
        This method should be overridden by subclasses if they have specific configuration needs.
        """
        with open(filename, "r") as f:
            expanded = os.path.expandvars(f.read())
            config_data = yaml.safe_load(expanded)
        config = AgentConfig(**config_data)
        agent_type = config.type
        if not agent_type:
            agent_type = AgentType.LLM
        agent_cls = _agent_classes.get(agent_type)
        if not agent_cls:
            raise ValueError(f"Unknown agent type: {config.type}")
        return agent_cls(config)

    @staticmethod
    def register(t: AgentType) -> Callable[[Type[T]], Type[T]]:
        """
        Register the agent type with the base agent class.
        This method should be called in the subclass to register the agent type.

        :param t: The agent type to associate with the class.
        :return: A decorator that registers the class.
        """

        def decorator(cls: Type[T]) -> Type[T]:
            if t in _agent_classes:
                raise ValueError(
                    f"class {_agent_classes[t]} is already registered for {cls}"
                )
            _agent_classes[t] = cls
            return cls

        return decorator
