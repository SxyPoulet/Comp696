from typing import Any, Dict, List
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from app.agents.base import BaseAgent
from app.core.config import settings


class ExampleAgent(BaseAgent):
    """
    Example agent demonstrating basic agent setup with tools.
    This agent can search the web and analyze text using Claude.
    """

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the example agent."""

        # Tool 1: Web search
        search = DuckDuckGoSearchRun()

        # Tool 2: Text analysis
        def analyze_text(text: str) -> str:
            """Analyze text and extract key insights."""
            try:
                response = self.llm.invoke(
                    f"Analyze the following text and extract key insights, "
                    f"pain points, and opportunities:\n\n{text}"
                )
                return response.content
            except Exception as e:
                return f"Error analyzing text: {str(e)}"

        tools = [
            Tool(
                name="search_web",
                func=search.run,
                description="Search the web for information about companies, people, or topics. "
                "Input should be a search query string.",
            ),
            Tool(
                name="analyze_text",
                func=analyze_text,
                description="Analyze text content to extract insights, pain points, and opportunities. "
                "Input should be the text to analyze.",
            ),
        ]

        return tools

    def _get_prompt_template(self) -> str:
        """Get the prompt template for the example agent."""
        return """You are a helpful sales intelligence agent that can search for information and analyze text.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


# Example usage function
def example_usage():
    """Demonstrate how to use the ExampleAgent."""

    agent = ExampleAgent()

    # Example 1: Search for a company
    result = agent.run({
        "input": "Search for information about Anthropic AI and analyze what you find."
    })

    print("Example 1 - Search and Analyze:")
    print(f"Success: {result['success']}")
    print(f"Output: {result['output']}")
    print("\n" + "=" * 80 + "\n")

    # Example 2: Analyze text
    sample_text = """
    TechCorp Inc. is a mid-sized software company struggling with outdated legacy systems.
    Their engineering team has grown from 20 to 100 people in the last year, but they're
    still using tools from 5 years ago. The VP of Engineering recently mentioned in an
    interview that scaling their infrastructure is their top priority for 2024.
    """

    result = agent.run({
        "input": f"Analyze this company information and identify the key pain points: {sample_text}"
    })

    print("Example 2 - Text Analysis:")
    print(f"Success: {result['success']}")
    print(f"Output: {result['output']}")


if __name__ == "__main__":
    example_usage()
