from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class ToolCallOutput(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    raw_response: str
    mode: str = "standard"

class BaseAgent(ABC):
    """Abstract base class for multilingual tool-calling agents."""

    @abstractmethod
    def select_tool(
        self,
        user_query: str,
        available_tools: List[Dict[str, Any]],
        language: str = "en",
        prompt_defense: bool = False
    ) -> ToolCallOutput:
        """
        Takes user query and tool schemas, returns candidate tool selection.
        If prompt_defense=True, enforces prompt-level least-privilege instructions.
        """
        pass

    @abstractmethod
    def handle_retry(
        self,
        user_query: str,
        failed_tool: str,
        error_message: str,
        available_tools: List[Dict[str, Any]],
        language: str = "en",
        prompt_defense: bool = False
    ) -> ToolCallOutput:
        """
        Handles second-turn retry when a transient fault occurs.
        Tests whether the agent retries or escalates privilege.
        """
        pass
