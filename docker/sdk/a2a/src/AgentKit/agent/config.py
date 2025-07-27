from enum import Enum
from typing import Optional, Union

from a2a.types import AgentSkill
from pydantic import BaseModel

from .agent_id import make_agent_id


class ModelSpec(BaseModel):
    """
    Specification for a model used by an agent.
    If the provider is not specified, it defaults to 'docker'.
    """

    name: str
    provider: Optional[str] = None


class AgentType(str, Enum):
    LLM = "llm"
    SEQUENTIAL = "sequential"


class AgentConfig(BaseModel):
    """
    Configuration for an agent.
    """

    name: str
    id: Optional[str] = None
    type: Optional[AgentType] = AgentType.LLM
    description: Optional[str] = None
    instructions: Optional[str] = None
    model: Optional[Union[str, ModelSpec]] = (
        None  # Model can be a string or a ModelSpec object
    )
    skills: Optional[list[AgentSkill]] = None
    tools: Optional[list[str]] = None
    sub_agents: Optional[list[str]] = None  # URLs for sub-agents

    @property
    def agent_id(self) -> str:
        if self.id:
            return self.id
        return make_agent_id(self.name)
