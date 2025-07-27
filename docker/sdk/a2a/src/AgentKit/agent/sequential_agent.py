from google.adk.agents import SequentialAgent as ADKSequentialAgent

from .agent import ADKBaseAgent, Agent
from .config import AgentType


@Agent.register(AgentType.SEQUENTIAL)
class SequentialAgent(Agent):
    def _build_agent(self, sub_agents: list[ADKBaseAgent]) -> ADKBaseAgent:
        return ADKSequentialAgent(
            name=self._config.agent_id,
            description=self._config.description or "",
            sub_agents=sub_agents,
        )
