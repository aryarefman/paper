from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class ToolCallOutput(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    raw_response: str

class BaseAgent(ABC):
    """Abstract base class for multilingual tool-calling agents."""

    @abstractmethod
    def select_tool(
        self,
        user_query: str,
        available_tools: List[Dict[str, Any]],
        language: str = "en"
    ) -> ToolCallOutput:
        """
        Takes user query and tool schemas, returns candidate tool selection.
        """
        pass
