"""
Intelligence Analyst Agent - Analyzes company profiles using Claude AI.

This agent synthesizes insights from company data, identifies pain points,
determines communication styles, and recommends outreach strategies.
"""

from typing import Any, Dict, List
from langchain.tools import Tool
from app.agents.base import BaseAgent
import json


class IntelligenceAnalystAgent(BaseAgent):
    """
    Agent for analyzing company profiles and generating strategic insights.

    Capabilities:
    - Analyze profiles for pain points and priorities
    - Determine communication styles
    - Generate intelligence summaries
    - Recommend approach strategies
    """

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the intelligence analyst agent."""

        # Tool 1: Analyze company pain points
        def analyze_pain_points(company_data_json: str) -> str:
            """
            Analyze company data to identify potential pain points.
            Input should be a JSON string with company profile data.
            """
            try:
                company_data = json.loads(company_data_json)

                # Use Claude to analyze pain points
                analysis_prompt = f"""Analyze this company profile and identify potential pain points or challenges they might be facing:

Company: {company_data.get('name', 'Unknown')}
Industry: {company_data.get('industry', 'Unknown')}
Size: {company_data.get('employee_count', 'Unknown')} employees
Description: {company_data.get('description', 'No description available')}
Tech Stack: {', '.join(company_data.get('tech_stack', [])[:5])}

Based on this information, identify 3-5 potential pain points or business challenges they might have.
For each pain point, explain:
1. What the challenge likely is
2. Why it matters to them
3. How it might impact their business

Format your response as a JSON array of objects with keys: pain_point, reasoning, impact"""

                response = self.llm.invoke(analysis_prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error analyzing pain points: {str(e)}"

        # Tool 2: Identify business priorities
        def identify_priorities(company_data_json: str) -> str:
            """
            Identify likely business priorities based on company data.
            Input should be a JSON string with company profile data.
            """
            try:
                company_data = json.loads(company_data_json)

                analysis_prompt = f"""Analyze this company and identify their likely business priorities:

Company: {company_data.get('name', 'Unknown')}
Industry: {company_data.get('industry', 'Unknown')}
Size: {company_data.get('employee_count', 'Unknown')} employees
Founded: {company_data.get('founded_year', 'Unknown')}
Description: {company_data.get('description', 'No description available')}

Based on their stage, size, and industry, what are their top 3-5 business priorities?
Consider factors like:
- Growth stage (startup vs established)
- Market conditions in their industry
- Common challenges for companies of their size
- Technology adoption patterns

Format as a JSON array of objects with keys: priority, reasoning, urgency_level (high/medium/low)"""

                response = self.llm.invoke(analysis_prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error identifying priorities: {str(e)}"

        # Tool 3: Determine communication approach
        def determine_approach(profile_json: str) -> str:
            """
            Determine the best communication approach and messaging strategy.
            Input should be a JSON string with company profile and decision makers.
            """
            try:
                profile = json.loads(profile_json)

                analysis_prompt = f"""Based on this company profile, recommend a communication and outreach strategy:

Company: {profile.get('company', 'Unknown')}
Industry: {profile.get('industry', 'Unknown')}
Size: {profile.get('size_category', 'Unknown')}
Lead Quality: {profile.get('lead_quality', 'Unknown')}
Decision Makers Available: {profile.get('has_decision_makers', False)}

Recommend:
1. Communication style (formal vs casual, technical vs business-focused)
2. Key messaging themes to emphasize
3. Objections they might raise and how to address them
4. Best channels for outreach (email, LinkedIn, phone)
5. Optimal timing and frequency

Format as a JSON object with keys: communication_style, messaging_themes, potential_objections, recommended_channels, timing_strategy"""

                response = self.llm.invoke(analysis_prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error determining approach: {str(e)}"

        # Tool 4: Generate executive summary
        def generate_summary(all_insights_json: str) -> str:
            """
            Generate an executive summary of all insights.
            Input should be a JSON string with company data, pain points, priorities, and approach.
            """
            try:
                insights = json.loads(all_insights_json)

                summary_prompt = f"""Create a concise executive summary for a sales team about this prospect:

Company: {insights.get('company', 'Unknown')}
Lead Score: {insights.get('lead_score', 'Unknown')}/100

Pain Points: {insights.get('pain_points', 'Not analyzed')}
Business Priorities: {insights.get('priorities', 'Not analyzed')}
Recommended Approach: {insights.get('approach', 'Not analyzed')}

Create a 2-3 paragraph executive summary that:
1. Describes why this is a good (or not good) prospect
2. Highlights the most important pain points and priorities
3. Provides clear next steps for the sales team

Write in a professional but concise style."""

                response = self.llm.invoke(summary_prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error generating summary: {str(e)}"

        tools = [
            Tool(
                name="analyze_pain_points",
                func=analyze_pain_points,
                description="Analyze company data to identify potential pain points and business challenges. "
                "Input should be a JSON string with company profile data. "
                "Returns analysis of 3-5 pain points with reasoning and impact."
            ),
            Tool(
                name="identify_priorities",
                func=identify_priorities,
                description="Identify likely business priorities based on company stage, size, and industry. "
                "Input should be a JSON string with company data. "
                "Returns top 3-5 business priorities with urgency levels."
            ),
            Tool(
                name="determine_approach",
                func=determine_approach,
                description="Determine the best communication and outreach strategy based on company profile. "
                "Input should be a JSON string with profile data. "
                "Returns recommended communication style, messaging themes, and channels."
            ),
            Tool(
                name="generate_summary",
                func=generate_summary,
                description="Generate an executive summary of all insights for the sales team. "
                "Input should be a JSON string with all gathered insights. "
                "Returns a concise 2-3 paragraph summary with next steps."
            ),
        ]

        return tools

    def _get_prompt_template(self) -> str:
        """Get the prompt template for the intelligence analyst agent."""
        return """You are an Intelligence Analyst Agent specialized in analyzing company profiles and generating strategic insights for sales teams.

Your goal is to synthesize data about target companies and provide actionable intelligence.

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

When analyzing a company:
1. Start by analyzing their pain points
2. Identify their business priorities
3. Determine the best communication approach
4. Generate an executive summary with all insights

Provide clear, actionable insights that a sales team can immediately use.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    def analyze_company(
        self,
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform complete intelligence analysis on a company.

        Args:
            company_data: Dictionary with company profile data

        Returns:
            Agent result with comprehensive intelligence report
        """
        company_json = json.dumps(company_data, default=str)

        input_text = f"""Analyze this company profile and generate a complete intelligence report:

Company Data: {company_json}

Provide:
1. Identified pain points and business challenges
2. Current business priorities
3. Recommended communication approach and messaging
4. Executive summary for the sales team

Make your analysis specific and actionable."""

        result = self.run({"input": input_text})
        return result


# Example usage
if __name__ == "__main__":
    agent = IntelligenceAnalystAgent()

    print("=== Intelligence Analyst Agent Demo ===\n")

    # Example company data
    company_data = {
        "name": "TechCorp Inc",
        "industry": "Software Development",
        "employee_count": 150,
        "founded_year": 2018,
        "description": "Fast-growing B2B SaaS company providing project management tools",
        "tech_stack": ["React", "Python", "PostgreSQL", "AWS"],
        "lead_score": 75
    }

    print("Example: Analyze TechCorp Inc")
    result = agent.analyze_company(company_data)
    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}\n")

    # Example 2: Just analyze pain points
    print("\n=== Example 2: Analyze pain points only ===")
    result = agent.run({
        "input": f"Analyze the pain points for this company: {json.dumps(company_data)}"
    })
    print(f"Output:\n{result['output']}")
