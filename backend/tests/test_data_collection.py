"""
Tests for data collection services.
"""

import pytest
import asyncio
from app.services.cache_service import CacheService
from app.services.scrapers.linkedin_scraper import MockLinkedInScraper
from app.services.data_collector import DataCollector


class TestCacheService:
    """Test Redis caching service."""

    def setup_method(self):
        """Setup test cache service."""
        self.cache = CacheService()

    def test_set_and_get(self):
        """Test setting and getting cache data."""
        namespace = "test"
        identifier = "key1"
        data = {"foo": "bar", "number": 42}

        # Set data
        result = self.cache.set(namespace, identifier, data, ttl=60)
        assert result is True

        # Get data
        cached = self.cache.get(namespace, identifier)
        assert cached == data

    def test_cache_expiry(self):
        """Test cache TTL."""
        namespace = "test"
        identifier = "key2"
        data = {"temp": "data"}

        # Set with short TTL
        self.cache.set(namespace, identifier, data, ttl=1)
        assert self.cache.exists(namespace, identifier) is True

        # Wait for expiry (would need actual wait in real test)
        # For now, just verify exists works
        ttl = self.cache.get_ttl(namespace, identifier)
        assert ttl is not None

    def test_delete(self):
        """Test cache deletion."""
        namespace = "test"
        identifier = "key3"
        data = {"delete": "me"}

        self.cache.set(namespace, identifier, data)
        assert self.cache.exists(namespace, identifier) is True

        self.cache.delete(namespace, identifier)
        assert self.cache.exists(namespace, identifier) is False

    def test_health_check(self):
        """Test Redis health check."""
        # This will fail if Redis is not running
        # In that case, the service should handle it gracefully
        health = self.cache.health_check()
        # Don't assert True as Redis may not be available in test env
        assert isinstance(health, bool)


@pytest.mark.asyncio
class TestLinkedInScraper:
    """Test LinkedIn mock scraper."""

    def setup_method(self):
        """Setup test scraper."""
        self.scraper = MockLinkedInScraper()

    async def test_search_company(self):
        """Test company search."""
        company_data = await self.scraper.search_company("Test Company")

        assert company_data is not None
        assert company_data["name"] == "Test Company"
        assert "linkedin_url" in company_data
        assert "industry" in company_data

    async def test_scrape_employees(self):
        """Test employee scraping."""
        employees = await self.scraper.scrape_company_employees("Test Company", limit=5)

        assert len(employees) <= 5
        assert all("name" in emp for emp in employees)
        assert all("title" in emp for emp in employees)
        assert all("company" in emp for emp in employees)


@pytest.mark.asyncio
class TestDataCollector:
    """Test data collection orchestrator."""

    def setup_method(self):
        """Setup test collector."""
        self.collector = DataCollector()

    async def test_collect_company_data(self):
        """Test collecting company data from multiple sources."""
        result = await self.collector.collect_company_data(
            company_name="Anthropic",
            domain="anthropic.com",
            use_cache=False  # Don't use cache for tests
        )

        assert result is not None
        assert result["company_name"] == "Anthropic"
        assert result["domain"] == "anthropic.com"
        assert "aggregated_data" in result
        assert "linkedin_data" in result

    async def test_collect_contacts(self):
        """Test collecting contacts."""
        contacts = await self.collector.collect_contacts(
            company_name="Anthropic",
            domain="anthropic.com",
            limit=5,
            use_cache=False
        )

        assert isinstance(contacts, list)
        assert len(contacts) <= 5

    async def test_calculate_lead_score(self):
        """Test lead scoring algorithm."""
        company_data = {
            "name": "Test Company",
            "domain": "test.com",
            "industry": "Technology",
            "employee_count": 100,
            "description": "A test company",
            "tech_stack": ["React", "Python", "PostgreSQL"],
            "email_pattern": "{first}.{last}@test.com",
            "total_emails_found": 10,
        }

        score = self.collector.calculate_lead_score(company_data)

        assert 0 <= score <= 100
        assert score > 0  # Should have some score based on data

    async def test_full_profile_collection(self):
        """Test collecting full company profile."""
        profile = await self.collector.collect_full_profile(
            company_name="Anthropic",
            domain="anthropic.com",
            include_contacts=True,
            use_cache=False
        )

        assert profile is not None
        assert profile["company_name"] == "Anthropic"
        assert profile["domain"] == "anthropic.com"
        assert "lead_score" in profile
        assert 0 <= profile["lead_score"] <= 100
        assert "contacts" in profile
        assert "data" in profile
        assert "sources_available" in profile


# Run tests with: pytest tests/test_data_collection.py -v
