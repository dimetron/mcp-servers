from abc import ABC, abstractmethod
from typing import Any, AsyncIterable


class BaseAgent(ABC):
    @abstractmethod
    def stream(self, query: str, session_id: str) -> AsyncIterable[dict[str, Any]]:
        """
        Stream results asynchronously based on the query and session ID.
        Must be implemented by all subclasses.
        """
        pass
