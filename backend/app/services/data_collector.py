"""
Data collection orchestrator that combines multiple data sources.
Coordinates scraping, enrichment, and caching.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.scrapers.linkedin_scraper import mock_linkedin_scraper
from app.services.enrichers.clearbit_service import clearbit_service
from app.services.enrichers.hunter_service import hunter_service
from app.services.cache_service import cache_service


class DataCollector:
    """
    Orchestrates data collection from multiple sources.
    Combines LinkedIn scraping, Clearbit enrichment, and Hunter.io email discovery.
    """

    def __init__(self):
        """Initialize data collector with all services."""
        self.linkedin = mock_linkedin_scraper
        self.clearbit = clearbit_service
        self.hunter = hunter_service
        self.cache = cache_service

    async def collect_company_data(
        self,
        company_name: Optional[str] = None,
        domain: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Collect comprehensive company data from all available sources.

        Args:
            company_name: Name of the company
            domain: Company domain (e.g., 'anthropic.com')
            use_cache: Whether to use cached data

        Returns:
            Aggregated company data from all sources
        """
        if not company_name and not domain:
            raise ValueError("Either company_name or domain must be provided")

        result = {
            "collected_at": datetime.utcnow().isoformat(),
            "company_name": company_name,
            "domain": domain,
            "linkedin_data": None,
            "clearbit_data": None,
            "hunter_data": None,
            "aggregated_data": {},
        }

        # Collect from LinkedIn (if company name provided)
        if company_name:
            try:
                linkedin_data = await self.linkedin.search_company(company_name, use_cache)
                result["linkedin_data"] = linkedin_data
            except Exception as e:
                print(f"LinkedIn collection error: {str(e)}")

        # Collect from Clearbit (if domain provided)
        if domain and self.clearbit.is_available():
            try:
                clearbit_data = self.clearbit.enrich_company(domain, use_cache)
                result["clearbit_data"] = clearbit_data
                if clearbit_data:
                    result["aggregated_data"].update(
                        self.clearbit.extract_company_info(clearbit_data)
                    )
            except Exception as e:
                print(f"Clearbit collection error: {str(e)}")

        # Collect from Hunter.io (if domain provided)
        if domain and self.hunter.is_available():
            try:
                hunter_data = self.hunter.domain_search(domain, use_cache)
                result["hunter_data"] = hunter_data
                if hunter_data:
                    result["aggregated_data"]["email_pattern"] = hunter_data.get("pattern")
                    result["aggregated_data"]["total_emails_found"] = hunter_data.get("total", 0)
            except Exception as e:
                print(f"Hunter collection error: {str(e)}")

        # Merge data intelligently
        result["aggregated_data"] = self._merge_company_data(result)

        return result

    async def collect_contacts(
        self,
        company_name: str,
        domain: str,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Collect contact information from multiple sources.

        Args:
            company_name: Name of the company
            domain: Company domain
            limit: Maximum number of contacts to collect
            use_cache: Whether to use cached data

        Returns:
            List of contacts with enriched data
        """
        contacts = []

        # Get contacts from LinkedIn
        try:
            linkedin_contacts = await self.linkedin.scrape_company_employees(
                company_name,
                limit=limit,
                use_cache=use_cache
            )
            contacts.extend(linkedin_contacts)
        except Exception as e:
            print(f"LinkedIn contacts error: {str(e)}")

        # Get contacts from Hunter.io
        if self.hunter.is_available():
            try:
                hunter_contacts = self.hunter.get_contacts(domain, limit=limit)
                contacts.extend(hunter_contacts)
            except Exception as e:
                print(f"Hunter contacts error: {str(e)}")

        # Deduplicate and enrich
        contacts = self._deduplicate_contacts(contacts)

        return contacts[:limit]

    def _merge_company_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently merge company data from multiple sources.

        Args:
            result: Raw result from all sources

        Returns:
            Merged and normalized company data
        """
        merged = result.get("aggregated_data", {})

        # Merge LinkedIn data
        if result.get("linkedin_data"):
            linkedin = result["linkedin_data"]
            merged.update({
                "name": merged.get("name") or linkedin.get("name"),
                "description": merged.get("description") or linkedin.get("description"),
                "industry": merged.get("industry") or linkedin.get("industry"),
                "employee_count": merged.get("employee_count") or linkedin.get("employee_count"),
                "website": merged.get("website") or linkedin.get("website"),
                "linkedin_url": linkedin.get("linkedin_url"),
            })

        # Clearbit data already in aggregated_data via extract_company_info

        # Add metadata
        merged["sources_used"] = []
        if result.get("linkedin_data"):
            merged["sources_used"].append("linkedin")
        if result.get("clearbit_data"):
            merged["sources_used"].append("clearbit")
        if result.get("hunter_data"):
            merged["sources_used"].append("hunter")

        return merged

    def _deduplicate_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate contacts based on email or name.

        Args:
            contacts: List of contact dictionaries

        Returns:
            Deduplicated list of contacts
        """
        seen_emails = set()
        seen_names = set()
        unique_contacts = []

        for contact in contacts:
            email = contact.get("email", "").lower()
            name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".lower().strip()

            # Use email as primary deduplication key
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_contacts.append(contact)
            elif not email and name and name not in seen_names:
                seen_names.add(name)
                unique_contacts.append(contact)

        return unique_contacts

    def calculate_lead_score(self, company_data: Dict[str, Any]) -> float:
        """
        Calculate a lead score (0-100) based on collected data.

        Args:
            company_data: Aggregated company data

        Returns:
            Lead score between 0 and 100
        """
        score = 0.0

        # Score based on data completeness (max 30 points)
        required_fields = ["name", "domain", "industry", "employee_count", "description"]
        complete_fields = sum(1 for field in required_fields if company_data.get(field))
        score += (complete_fields / len(required_fields)) * 30

        # Score based on company size (max 20 points)
        employee_count = company_data.get("employee_count")
        if employee_count:
            if 50 <= employee_count <= 500:
                score += 20  # Sweet spot for B2B
            elif 500 <= employee_count <= 1000:
                score += 15
            elif employee_count < 50:
                score += 10
            else:
                score += 5

        # Score based on funding/revenue (max 20 points)
        funding = company_data.get("funding", {})
        if funding.get("total"):
            score += 20
        elif funding.get("annual_revenue"):
            score += 15

        # Score based on tech stack (max 15 points)
        tech_stack = company_data.get("tech_stack", [])
        if len(tech_stack) > 0:
            score += min(len(tech_stack) * 3, 15)

        # Score based on contact availability (max 15 points)
        if company_data.get("email_pattern"):
            score += 10
        if company_data.get("total_emails_found", 0) > 0:
            score += 5

        return min(score, 100.0)

    async def collect_full_profile(
        self,
        company_name: str,
        domain: str,
        include_contacts: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Collect complete company profile with all available data.

        Args:
            company_name: Name of the company
            domain: Company domain
            include_contacts: Whether to collect contact data
            use_cache: Whether to use cached data

        Returns:
            Complete company profile
        """
        # Collect company data
        company_data = await self.collect_company_data(
            company_name=company_name,
            domain=domain,
            use_cache=use_cache
        )

        # Collect contacts if requested
        contacts = []
        if include_contacts:
            contacts = await self.collect_contacts(
                company_name=company_name,
                domain=domain,
                limit=20,
                use_cache=use_cache
            )

        # Calculate lead score
        lead_score = self.calculate_lead_score(company_data.get("aggregated_data", {}))

        # Assemble full profile
        profile = {
            "company_name": company_name,
            "domain": domain,
            "lead_score": lead_score,
            "data": company_data.get("aggregated_data", {}),
            "contacts": contacts,
            "raw_data": {
                "linkedin": company_data.get("linkedin_data"),
                "clearbit": company_data.get("clearbit_data"),
                "hunter": company_data.get("hunter_data"),
            },
            "collected_at": company_data.get("collected_at"),
            "sources_available": {
                "linkedin": True,  # Using mock scraper
                "clearbit": self.clearbit.is_available(),
                "hunter": self.hunter.is_available(),
            }
        }

        return profile


# Singleton instance
data_collector = DataCollector()


# Example usage
async def example_usage():
    """Demonstrate data collection."""
    collector = DataCollector()

    print("=== Collecting Company Data ===")
    company_data = await collector.collect_company_data(
        company_name="Anthropic",
        domain="anthropic.com"
    )
    print(f"\nAggregated Data:")
    for key, value in company_data["aggregated_data"].items():
        print(f"  {key}: {value}")

    print("\n=== Collecting Contacts ===")
    contacts = await collector.collect_contacts(
        company_name="Anthropic",
        domain="anthropic.com",
        limit=5
    )
    print(f"Found {len(contacts)} contacts:")
    for contact in contacts:
        print(f"  - {contact.get('name', 'N/A')}: {contact.get('title', 'N/A')}")

    print("\n=== Full Profile ===")
    profile = await collector.collect_full_profile(
        company_name="Anthropic",
        domain="anthropic.com"
    )
    print(f"Lead Score: {profile['lead_score']}")
    print(f"Total Contacts: {len(profile['contacts'])}")
    print(f"Sources Used: {profile['data'].get('sources_used', [])}")


if __name__ == "__main__":
    asyncio.run(example_usage())
