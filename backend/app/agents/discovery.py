"""
Discovery Agent - Searches for and qualifies target companies.

This agent uses available tools to find companies matching search criteria,
extract basic data, and score leads based on fit criteria.
"""

from typing import Any, Dict, List
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from app.agents.base import BaseAgent
from app.services.data_collector import data_collector
import asyncio
import json


class DiscoveryAgent(BaseAgent):
    """
    Agent for discovering and qualifying target companies.

    Capabilities:
    - Search for companies by industry, size, location
    - Extract basic company data
    - Score leads based on fit criteria
    - Return list of qualified targets
    """

    def __init__(self):
        """Initialize the discovery agent."""
        super().__init__()
        self.data_collector = data_collector

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the discovery agent."""

        # Tool 1: Web search for companies
        search = DuckDuckGoSearchRun()

        # Tool 2: Collect company data
        def collect_company_info(company_info: str) -> str:
            """
            Collect detailed information about a company.
            Input should be in format: "company_name|domain"
            Example: "Anthropic|anthropic.com"
            """
            try:
                parts = company_info.split("|")
                if len(parts) != 2:
                    return "Error: Input must be in format 'company_name|domain'"

                company_name, domain = parts[0].strip(), parts[1].strip()

                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    profile = loop.run_until_complete(
                        self.data_collector.collect_company_data(
                            company_name=company_name,
                            domain=domain,
                            use_cache=True
                        )
                    )
                finally:
                    loop.close()

                if profile and profile.get("aggregated_data"):
                    data = profile["aggregated_data"]
                    result = {
                        "name": data.get("name", company_name),
                        "domain": domain,
                        "industry": data.get("industry"),
                        "employee_count": data.get("employee_count"),
                        "location": data.get("location"),
                        "description": data.get("description"),
                        "tech_stack": data.get("tech_stack", []),
                        "sources_used": data.get("sources_used", [])
                    }
                    return json.dumps(result, indent=2)
                else:
                    return f"No detailed data found for {company_name}"

            except Exception as e:
                return f"Error collecting company info: {str(e)}"

        # Tool 3: Calculate lead score
        def calculate_lead_score(company_data_json: str) -> str:
            """
            Calculate a lead score (0-100) for a company.
            Input should be a JSON string with company data.
            """
            try:
                company_data = json.loads(company_data_json)
                score = self.data_collector.calculate_lead_score(company_data)

                return json.dumps({
                    "lead_score": round(score, 2),
                    "rating": self._get_score_rating(score),
                    "company": company_data.get("name", "Unknown")
                }, indent=2)

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error calculating score: {str(e)}"

        tools = [
            Tool(
                name="search_companies",
                func=search.run,
                description="Search the web for companies matching criteria. "
                "Input should be a search query with keywords like industry, location, size. "
                "Example: 'AI companies in San Francisco with 50-200 employees'"
            ),
            Tool(
                name="collect_company_data",
                func=collect_company_info,
                description="Collect detailed data about a specific company. "
                "Input format: 'company_name|domain' (e.g., 'Anthropic|anthropic.com'). "
                "Returns company profile with industry, size, tech stack, etc."
            ),
            Tool(
                name="score_lead",
                func=calculate_lead_score,
                description="Calculate a lead score (0-100) for a company based on fit criteria. "
                "Input should be a JSON string with company data fields. "
                "Returns score, rating, and company name."
            ),
        ]

        return tools

    def _get_prompt_template(self) -> str:
        """Get the prompt template for the discovery agent."""
        return """You are a Discovery Agent specialized in finding and qualifying target companies for sales outreach.

Your goal is to help users find companies that match their ideal customer profile.

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

When searching for companies:
1. Start with a web search to find potential companies
2. For each promising company, collect detailed data using their domain
3. Calculate a lead score for qualified companies
4. Provide a summary with top prospects ranked by score

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    def _get_score_rating(self, score: float) -> str:
        """Convert numeric score to rating."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"

    def discover_companies(
        self,
        search_criteria: Dict[str, Any],
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Discover companies matching search criteria.

        Args:
            search_criteria: Dictionary with keys like industry, size, location, keywords
            max_results: Maximum number of companies to return

        Returns:
            Dictionary with discovered companies and scores
        """
        # Build search query from criteria
        query_parts = []
        if search_criteria.get("industry"):
            query_parts.append(search_criteria["industry"])
        if search_criteria.get("keywords"):
            query_parts.append(search_criteria["keywords"])
        if search_criteria.get("location"):
            query_parts.append(f"in {search_criteria['location']}")
        if search_criteria.get("size"):
            query_parts.append(f"with {search_criteria['size']} employees")

        query = " ".join(query_parts)

        # Use the agent to discover companies
        input_text = f"""Find and qualify up to {max_results} companies matching these criteria:

Search Query: {query}

For each company you find:
1. Collect detailed company data
2. Calculate a lead score
3. Note why they match the criteria

Provide a ranked list of the top prospects."""

        result = self.run({"input": input_text})

        return result


# Example usage
if __name__ == "__main__":
    agent = DiscoveryAgent()

    print("=== Discovery Agent Demo ===\n")

    # Example 1: Simple search
    print("Example 1: Find AI companies")
    result = agent.run({
        "input": "Find 3 AI companies in San Francisco and score them as leads"
    })
    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}\n")

    # Example 2: Using search criteria
    print("\n=== Example 2: Structured search ===")
    criteria = {
        "industry": "AI/ML",
        "location": "San Francisco",
        "size": "50-200",
        "keywords": "machine learning"
    }
    result = agent.discover_companies(criteria, max_results=5)
    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}")
