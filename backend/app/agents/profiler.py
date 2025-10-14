"""
Profile Builder Agent - Builds detailed target company profiles.

This agent orchestrates data collection tools to find key personnel,
map organizational structure, identify technology stack, and track company news.
"""

from typing import Any, Dict, List
from langchain.tools import Tool
from app.agents.base import BaseAgent
from app.services.data_collector import data_collector
import asyncio
import json


class ProfileBuilderAgent(BaseAgent):
    """
    Agent for building comprehensive company profiles.

    Capabilities:
    - Find key personnel (decision-makers)
    - Map organizational structure
    - Extract contact information
    - Identify technology stack
    - Track recent company news/events
    """

    def __init__(self):
        """Initialize the profile builder agent."""
        super().__init__()
        self.data_collector = data_collector

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the profile builder agent."""

        # Tool 1: Build full company profile
        def build_company_profile(company_info: str) -> str:
            """
            Build a comprehensive company profile.
            Input format: "company_name|domain"
            Example: "Anthropic|anthropic.com"
            """
            try:
                parts = company_info.split("|")
                if len(parts) != 2:
                    return "Error: Input must be in format 'company_name|domain'"

                company_name, domain = parts[0].strip(), parts[1].strip()

                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    profile = loop.run_until_complete(
                        self.data_collector.collect_full_profile(
                            company_name=company_name,
                            domain=domain,
                            include_contacts=True,
                            use_cache=True
                        )
                    )
                finally:
                    loop.close()

                if profile:
                    result = {
                        "company": profile["company_name"],
                        "domain": profile["domain"],
                        "lead_score": profile["lead_score"],
                        "data": profile["data"],
                        "contacts_count": len(profile["contacts"]),
                        "sources": profile["sources_available"]
                    }
                    return json.dumps(result, indent=2, default=str)
                else:
                    return f"Could not build profile for {company_name}"

            except Exception as e:
                return f"Error building profile: {str(e)}"

        # Tool 2: Get key decision makers
        def find_decision_makers(company_info: str) -> str:
            """
            Find key decision makers at a company.
            Input format: "company_name|domain"
            """
            try:
                parts = company_info.split("|")
                if len(parts) != 2:
                    return "Error: Input must be in format 'company_name|domain'"

                company_name, domain = parts[0].strip(), parts[1].strip()

                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    contacts = loop.run_until_complete(
                        self.data_collector.collect_contacts(
                            company_name=company_name,
                            domain=domain,
                            limit=20,
                            use_cache=True
                        )
                    )
                finally:
                    loop.close()

                # Filter for decision makers (C-level, VP, Director)
                decision_makers = [
                    c for c in contacts
                    if c.get("is_decision_maker") or
                    any(title in str(c.get("title", "")).lower()
                        for title in ["ceo", "cto", "cfo", "vp", "vice president", "director", "head"])
                ]

                result = {
                    "company": company_name,
                    "total_contacts": len(contacts),
                    "decision_makers_count": len(decision_makers),
                    "decision_makers": [
                        {
                            "name": c.get("name"),
                            "title": c.get("title"),
                            "email": c.get("email"),
                            "seniority": c.get("seniority_level")
                        }
                        for c in decision_makers[:10]  # Top 10
                    ]
                }

                return json.dumps(result, indent=2)

            except Exception as e:
                return f"Error finding decision makers: {str(e)}"

        # Tool 3: Analyze company data
        def analyze_company_data(profile_json: str) -> str:
            """
            Analyze company profile data and extract insights.
            Input should be a JSON string with company profile data.
            """
            try:
                profile = json.loads(profile_json)

                insights = {
                    "company": profile.get("company", "Unknown"),
                    "analysis": {}
                }

                data = profile.get("data", {})

                # Company size analysis
                employee_count = data.get("employee_count")
                if employee_count:
                    if employee_count < 50:
                        insights["analysis"]["size_category"] = "Small (startup)"
                    elif employee_count < 200:
                        insights["analysis"]["size_category"] = "Mid-size (growth stage)"
                    elif employee_count < 1000:
                        insights["analysis"]["size_category"] = "Large (established)"
                    else:
                        insights["analysis"]["size_category"] = "Enterprise"

                # Tech stack analysis
                tech_stack = data.get("tech_stack", [])
                if tech_stack:
                    insights["analysis"]["tech_stack_count"] = len(tech_stack)
                    insights["analysis"]["technologies"] = tech_stack[:5]

                # Contact availability
                contacts_count = profile.get("contacts_count", 0)
                insights["analysis"]["contact_availability"] = "Good" if contacts_count > 5 else "Limited"

                # Lead quality
                lead_score = profile.get("lead_score", 0)
                insights["analysis"]["lead_quality"] = (
                    "Excellent" if lead_score >= 80 else
                    "Good" if lead_score >= 60 else
                    "Fair" if lead_score >= 40 else
                    "Poor"
                )

                return json.dumps(insights, indent=2)

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error analyzing data: {str(e)}"

        tools = [
            Tool(
                name="build_profile",
                func=build_company_profile,
                description="Build a comprehensive company profile including all available data "
                "and contacts. Input format: 'company_name|domain' (e.g., 'Anthropic|anthropic.com'). "
                "Returns full profile with company data, contacts, and lead score."
            ),
            Tool(
                name="find_decision_makers",
                func=find_decision_makers,
                description="Find key decision makers (C-level, VPs, Directors) at a company. "
                "Input format: 'company_name|domain'. Returns list of decision makers with titles and emails."
            ),
            Tool(
                name="analyze_profile",
                func=analyze_company_data,
                description="Analyze company profile data to extract insights about size, tech stack, "
                "contact availability, and lead quality. Input should be a JSON string with profile data."
            ),
        ]

        return tools

    def _get_prompt_template(self) -> str:
        """Get the prompt template for the profile builder agent."""
        return """You are a Profile Builder Agent specialized in creating comprehensive company profiles for sales outreach.

Your goal is to gather all relevant information about target companies and identify key decision makers.

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

When building a profile:
1. Start by building the full company profile
2. Find and identify key decision makers
3. Analyze the profile data to extract insights
4. Summarize the findings with actionable information

Focus on:
- Company size and stage
- Key technologies they use
- Decision makers and their roles
- Contact availability
- Overall lead quality

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    def build_profile(
        self,
        company_name: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        Build a complete company profile.

        Args:
            company_name: Name of the company
            domain: Company domain

        Returns:
            Agent result with comprehensive profile
        """
        input_text = f"""Build a comprehensive profile for the company:

Company: {company_name}
Domain: {domain}

Include:
1. Complete company data (size, industry, tech stack, etc.)
2. Key decision makers and their contact information
3. Analysis of the company's fit as a sales prospect
4. Recommendations for outreach approach

Provide a detailed summary."""

        result = self.run({"input": input_text})
        return result


# Example usage
if __name__ == "__main__":
    agent = ProfileBuilderAgent()

    print("=== Profile Builder Agent Demo ===\n")

    # Example 1: Build a profile
    print("Example 1: Build profile for Anthropic")
    result = agent.build_profile("Anthropic", "anthropic.com")
    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}\n")

    # Example 2: Find decision makers
    print("\n=== Example 2: Find decision makers ===")
    result = agent.run({
        "input": "Find the key decision makers at Anthropic (anthropic.com)"
    })
    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}")
