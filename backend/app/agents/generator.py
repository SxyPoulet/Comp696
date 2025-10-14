"""
Content Generator Agent - Creates personalized outreach content.

This agent generates personalized email templates, conversation starters,
and suggests optimal messaging based on company intelligence.
"""

from typing import Any, Dict, List
from langchain.tools import Tool
from app.agents.base import BaseAgent
import json


class ContentGeneratorAgent(BaseAgent):
    """
    Agent for generating personalized sales outreach content.

    Capabilities:
    - Generate personalized email templates
    - Create conversation starters
    - Suggest optimal messaging
    - Create multiple variants for A/B testing
    """

    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the content generator agent."""

        # Tool 1: Generate personalized email
        def generate_email(context_json: str) -> str:
            """
            Generate a personalized cold email.
            Input should be a JSON string with context including:
            - company_name, industry, pain_points, contact_name, contact_title
            """
            try:
                context = json.loads(context_json)

                email_prompt = f"""Write a personalized cold email for B2B sales outreach.

Target Company: {context.get('company_name', 'Unknown')}
Industry: {context.get('industry', 'Unknown')}
Recipient: {context.get('contact_name', 'there')}
Title: {context.get('contact_title', 'Decision Maker')}
Pain Points: {', '.join(context.get('pain_points', ['business growth']))}
Your Product/Service: {context.get('product_description', 'Business solutions')}

Write a compelling cold email that:
1. Has a personalized, attention-grabbing subject line
2. Opens with a relevant observation about their company or industry
3. Briefly mentions one specific pain point they likely have
4. Introduces your value proposition clearly (1 sentence)
5. Includes a specific, low-friction call-to-action
6. Is under 150 words
7. Has a professional but friendly tone

Format as a JSON object with keys: subject, body, cta"""

                response = self.llm.invoke(email_prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error generating email: {str(e)}"

        # Tool 2: Generate conversation starters
        def generate_conversation_starters(context_json: str) -> str:
            """
            Generate conversation starters for different channels.
            Input should be a JSON string with company and contact context.
            """
            try:
                context = json.loads(context_json)

                prompt = f"""Generate 5 different conversation starters for reaching out to:

Contact: {context.get('contact_name', 'the prospect')}
Title: {context.get('contact_title', 'Decision Maker')}
Company: {context.get('company_name', 'Unknown')}
Industry: {context.get('industry', 'Unknown')}
Context: {context.get('context', 'General outreach')}

Create openers for:
1. LinkedIn message (2-3 sentences)
2. Email subject line (under 60 characters)
3. Phone call opening (1-2 sentences)
4. LinkedIn connection request note
5. Follow-up email subject

Each should be:
- Personalized with specific company/role details
- Value-focused (what's in it for them)
- Natural and conversational
- Avoid generic sales language

Format as a JSON object with keys: linkedin_message, email_subject, phone_opener, connection_request, followup_subject"""

                response = self.llm.invoke(prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error generating conversation starters: {str(e)}"

        # Tool 3: Generate email variants
        def generate_email_variants(base_email_json: str) -> str:
            """
            Generate A/B testing variants of an email.
            Input should be a JSON string with the base email.
            """
            try:
                base_email = json.loads(base_email_json)

                prompt = f"""Create 2 alternative versions of this cold email for A/B testing:

Original Email:
Subject: {base_email.get('subject')}
Body: {base_email.get('body')}

Create Version A and Version B that test different approaches:
- Version A: More direct and business-focused
- Version B: More story-driven and relatable

Keep the core value proposition but vary:
- Opening hook
- Tone and style
- Call-to-action phrasing

Each version should be the same length or shorter than the original.

Format as a JSON object with keys: version_a, version_b (each with subject and body)"""

                response = self.llm.invoke(prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error generating variants: {str(e)}"

        # Tool 4: Optimize messaging
        def optimize_messaging(email_json: str) -> str:
            """
            Analyze and optimize an email for better response rates.
            Input should be a JSON string with email content.
            """
            try:
                email = json.loads(email_json)

                prompt = f"""Analyze this cold email and provide optimization suggestions:

Subject: {email.get('subject')}
Body: {email.get('body')}

Evaluate and provide specific feedback on:
1. Subject line effectiveness (clarity, curiosity, length)
2. Opening hook strength
3. Value proposition clarity
4. Personalization level
5. Call-to-action effectiveness
6. Overall length and readability
7. Tone appropriateness

For each area, provide:
- Score out of 10
- What works well
- Specific improvement suggestions

Format as a JSON object with keys for each evaluation area, each containing: score, strengths, improvements"""

                response = self.llm.invoke(prompt)

                return response.content

            except json.JSONDecodeError:
                return "Error: Invalid JSON input"
            except Exception as e:
                return f"Error optimizing messaging: {str(e)}"

        tools = [
            Tool(
                name="generate_email",
                func=generate_email,
                description="Generate a personalized cold email based on company and contact context. "
                "Input should be a JSON string with company_name, industry, pain_points, "
                "contact_name, contact_title, and product_description. "
                "Returns email with subject, body, and CTA."
            ),
            Tool(
                name="generate_conversation_starters",
                func=generate_conversation_starters,
                description="Generate conversation starters for multiple channels (LinkedIn, email, phone). "
                "Input should be a JSON string with contact and company context. "
                "Returns personalized openers for different channels."
            ),
            Tool(
                name="generate_variants",
                func=generate_email_variants,
                description="Generate A/B testing variants of an email. "
                "Input should be a JSON string with the base email (subject and body). "
                "Returns two alternative versions for testing."
            ),
            Tool(
                name="optimize_messaging",
                func=optimize_messaging,
                description="Analyze and optimize email messaging for better response rates. "
                "Input should be a JSON string with email content. "
                "Returns detailed feedback and improvement suggestions."
            ),
        ]

        return tools

    def _get_prompt_template(self) -> str:
        """Get the prompt template for the content generator agent."""
        return """You are a Content Generator Agent specialized in creating personalized sales outreach content.

Your goal is to help sales teams create compelling, personalized messages that get responses.

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

When generating content:
1. Always personalize based on company and contact information
2. Focus on value, not features
3. Keep messages concise and scannable
4. Include specific, low-friction CTAs
5. Avoid generic sales language

Best practices:
- Use recipient's name and company details
- Reference specific pain points or challenges
- Lead with value, not your company
- Make the ask clear and easy
- Proofread for grammar and tone

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    def generate_outreach_campaign(
        self,
        company_name: str,
        contact_name: str,
        contact_title: str,
        industry: str,
        pain_points: List[str],
        product_description: str
    ) -> Dict[str, Any]:
        """
        Generate a complete outreach campaign.

        Args:
            company_name: Target company name
            contact_name: Contact person's name
            contact_title: Contact's job title
            industry: Company industry
            pain_points: List of identified pain points
            product_description: Brief description of product/service

        Returns:
            Agent result with complete outreach campaign
        """
        context = {
            "company_name": company_name,
            "contact_name": contact_name,
            "contact_title": contact_title,
            "industry": industry,
            "pain_points": pain_points,
            "product_description": product_description
        }

        context_json = json.dumps(context)

        input_text = f"""Create a complete outreach campaign for this prospect:

Context: {context_json}

Generate:
1. A personalized cold email with subject line
2. Conversation starters for LinkedIn and phone
3. Two A/B testing variants of the email
4. Analysis and optimization suggestions

Provide all content ready to use."""

        result = self.run({"input": input_text})
        return result


# Example usage
if __name__ == "__main__":
    agent = ContentGeneratorAgent()

    print("=== Content Generator Agent Demo ===\n")

    # Example: Generate outreach campaign
    result = agent.generate_outreach_campaign(
        company_name="TechCorp Inc",
        contact_name="Sarah Johnson",
        contact_title="VP of Engineering",
        industry="Software Development",
        pain_points=["Legacy infrastructure", "Slow deployment cycles", "Technical debt"],
        product_description="Cloud infrastructure platform that reduces deployment time by 70%"
    )

    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}\n")

    # Example 2: Just generate an email
    print("\n=== Example 2: Generate email only ===")
    context = {
        "company_name": "DataCo",
        "contact_name": "John Smith",
        "contact_title": "CTO",
        "industry": "Data Analytics",
        "pain_points": ["Data silos", "Manual reporting"],
        "product_description": "Automated data pipeline solution"
    }
    result = agent.run({
        "input": f"Generate a personalized email for: {json.dumps(context)}"
    })
    print(f"Output:\n{result['output']}")
