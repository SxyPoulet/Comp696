"""
Tests for AI agents.
Note: These tests require ANTHROPIC_API_KEY to be set.
"""

import pytest
import json
from app.agents.discovery import DiscoveryAgent
from app.agents.profiler import ProfileBuilderAgent
from app.agents.analyst import IntelligenceAnalystAgent
from app.agents.generator import ContentGeneratorAgent


class TestDiscoveryAgent:
    """Test Discovery Agent functionality."""

    def setup_method(self):
        """Setup test discovery agent."""
        self.agent = DiscoveryAgent()

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        assert self.agent is not None
        assert self.agent.llm is not None
        assert len(self.agent.tools) > 0

    def test_agent_has_required_tools(self):
        """Test that agent has all required tools."""
        tool_names = [tool.name for tool in self.agent.tools]

        assert "search_companies" in tool_names
        assert "collect_company_data" in tool_names
        assert "score_lead" in tool_names

    @pytest.mark.skip(reason="Requires API key and makes external calls")
    def test_discover_companies(self):
        """Test discovering companies (requires API key)."""
        criteria = {
            "industry": "AI",
            "location": "San Francisco",
            "size": "50-200"
        }

        result = self.agent.discover_companies(criteria, max_results=1)

        assert result is not None
        assert "success" in result


class TestProfileBuilderAgent:
    """Test Profile Builder Agent functionality."""

    def setup_method(self):
        """Setup test profile builder agent."""
        self.agent = ProfileBuilderAgent()

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        assert self.agent is not None
        assert self.agent.llm is not None
        assert len(self.agent.tools) > 0

    def test_agent_has_required_tools(self):
        """Test that agent has all required tools."""
        tool_names = [tool.name for tool in self.agent.tools]

        assert "build_profile" in tool_names
        assert "find_decision_makers" in tool_names
        assert "analyze_profile" in tool_names

    @pytest.mark.skip(reason="Requires API key and makes external calls")
    def test_build_profile(self):
        """Test building company profile (requires API key)."""
        result = self.agent.build_profile("Anthropic", "anthropic.com")

        assert result is not None
        assert "success" in result


class TestIntelligenceAnalystAgent:
    """Test Intelligence Analyst Agent functionality."""

    def setup_method(self):
        """Setup test intelligence analyst agent."""
        self.agent = IntelligenceAnalystAgent()

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        assert self.agent is not None
        assert self.agent.llm is not None
        assert len(self.agent.tools) > 0

    def test_agent_has_required_tools(self):
        """Test that agent has all required tools."""
        tool_names = [tool.name for tool in self.agent.tools]

        assert "analyze_pain_points" in tool_names
        assert "identify_priorities" in tool_names
        assert "determine_approach" in tool_names
        assert "generate_summary" in tool_names

    @pytest.mark.skip(reason="Requires API key and makes external calls")
    def test_analyze_company(self):
        """Test analyzing company (requires API key)."""
        company_data = {
            "name": "Test Company",
            "industry": "Technology",
            "employee_count": 100,
            "description": "A test company"
        }

        result = self.agent.analyze_company(company_data)

        assert result is not None
        assert "success" in result


class TestContentGeneratorAgent:
    """Test Content Generator Agent functionality."""

    def setup_method(self):
        """Setup test content generator agent."""
        self.agent = ContentGeneratorAgent()

    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        assert self.agent is not None
        assert self.agent.llm is not None
        assert len(self.agent.tools) > 0

    def test_agent_has_required_tools(self):
        """Test that agent has all required tools."""
        tool_names = [tool.name for tool in self.agent.tools]

        assert "generate_email" in tool_names
        assert "generate_conversation_starters" in tool_names
        assert "generate_variants" in tool_names
        assert "optimize_messaging" in tool_names

    @pytest.mark.skip(reason="Requires API key and makes external calls")
    def test_generate_outreach_campaign(self):
        """Test generating outreach campaign (requires API key)."""
        result = self.agent.generate_outreach_campaign(
            company_name="Test Company",
            contact_name="John Doe",
            contact_title="CTO",
            industry="Technology",
            pain_points=["Legacy systems"],
            product_description="Modern cloud platform"
        )

        assert result is not None
        assert "success" in result


# Integration test (requires API key)
@pytest.mark.skip(reason="Requires API key - integration test")
class TestAgentWorkflow:
    """Test complete agent workflow."""

    def test_end_to_end_workflow(self):
        """Test a complete discovery -> profile -> analysis -> content workflow."""

        # 1. Discovery
        discovery_agent = DiscoveryAgent()
        discovery_result = discovery_agent.run({
            "input": "Find one AI company and collect its basic data"
        })
        assert discovery_result["success"]

        # 2. Profile Building
        profiler_agent = ProfileBuilderAgent()
        profile_result = profiler_agent.build_profile("Anthropic", "anthropic.com")
        assert profile_result["success"]

        # 3. Intelligence Analysis
        analyst_agent = IntelligenceAnalystAgent()
        analysis_result = analyst_agent.analyze_company({
            "name": "Anthropic",
            "industry": "AI",
            "employee_count": 100
        })
        assert analysis_result["success"]

        # 4. Content Generation
        generator_agent = ContentGeneratorAgent()
        content_result = generator_agent.generate_outreach_campaign(
            company_name="Anthropic",
            contact_name="Test Contact",
            contact_title="Engineer",
            industry="AI",
            pain_points=["Scaling AI"],
            product_description="AI infrastructure"
        )
        assert content_result["success"]


# Run tests with: pytest tests/test_agents.py -v
# Run including skipped tests: pytest tests/test_agents.py -v --run-skipped
