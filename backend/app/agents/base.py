from abc import ABC, abstractmethod
from typing import Any, Dict, List
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from app.core.config import settings


class BaseAgent(ABC):
    """Base class for all AI agents in the system."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        """Initialize the agent with Claude LLM."""
        self.llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=0.7,
            max_tokens=4096,
        )
        self.tools = self._setup_tools()
        self.agent_executor = self._create_agent()

    @abstractmethod
    def _setup_tools(self) -> List[Tool]:
        """Setup tools specific to this agent. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _get_prompt_template(self) -> str:
        """Get the prompt template for this agent. Must be implemented by subclasses."""
        pass

    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor with tools and prompt."""
        prompt_template = self._get_prompt_template()

        # Create the ReAct agent prompt
        prompt = PromptTemplate.from_template(
            template=prompt_template
        )

        # Create the agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
        )

        return agent_executor

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with given input.

        Args:
            input_data: Dictionary containing input for the agent

        Returns:
            Dictionary containing the agent's output
        """
        try:
            result = self.agent_executor.invoke(input_data)
            return {
                "success": True,
                "output": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": None,
            }

    async def arun(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent asynchronously with given input.

        Args:
            input_data: Dictionary containing input for the agent

        Returns:
            Dictionary containing the agent's output
        """
        try:
            result = await self.agent_executor.ainvoke(input_data)
            return {
                "success": True,
                "output": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": None,
            }
