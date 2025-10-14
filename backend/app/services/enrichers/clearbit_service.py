"""
Clearbit API integration for company enrichment.
Free tier: 50 requests/month
API Docs: https://clearbit.com/docs
"""

import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
from app.services.cache_service import cache_service


class ClearbitService:
    """Service for enriching company data using Clearbit API."""

    def __init__(self):
        """Initialize Clearbit service."""
        self.api_key = settings.clearbit_api_key
        self.base_url = "https://company.clearbit.com/v2"
        self.timeout = 10.0

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Make authenticated request to Clearbit API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response data or None on error
        """
        if not self.api_key:
            print("Warning: Clearbit API key not configured")
            return None

        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print(f"Clearbit: Company not found for {params}")
                    return None
                elif response.status_code == 402:
                    print("Clearbit: Rate limit exceeded or payment required")
                    return None
                else:
                    print(f"Clearbit API error: {response.status_code} - {response.text}")
                    return None

        except httpx.TimeoutException:
            print("Clearbit API request timed out")
            return None
        except Exception as e:
            print(f"Clearbit API error: {str(e)}")
            return None

    def enrich_company(self, domain: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Enrich company data by domain.

        Args:
            domain: Company domain (e.g., 'anthropic.com')
            use_cache: Whether to use cached data (default: True)

        Returns:
            Enriched company data or None if not found
        """
        cache_key = f"clearbit:{domain}"

        # Check cache first
        if use_cache:
            cached = cache_service.get("clearbit", domain)
            if cached:
                print(f"Cache hit for Clearbit: {domain}")
                return cached

        # Make API request
        data = self._make_request("companies/find", params={"domain": domain})

        # Cache the result
        if data and use_cache:
            cache_service.set("clearbit", domain, data, ttl=settings.cache_ttl)

        return data

    def extract_company_info(self, clearbit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize relevant company information from Clearbit response.

        Args:
            clearbit_data: Raw Clearbit API response

        Returns:
            Normalized company data
        """
        if not clearbit_data:
            return {}

        return {
            "name": clearbit_data.get("name"),
            "domain": clearbit_data.get("domain"),
            "description": clearbit_data.get("description"),
            "industry": clearbit_data.get("category", {}).get("industry"),
            "sector": clearbit_data.get("category", {}).get("sector"),
            "employee_count": clearbit_data.get("metrics", {}).get("employees"),
            "employee_range": clearbit_data.get("metrics", {}).get("employeesRange"),
            "founded_year": clearbit_data.get("foundedYear"),
            "location": clearbit_data.get("location"),
            "city": clearbit_data.get("geo", {}).get("city"),
            "state": clearbit_data.get("geo", {}).get("state"),
            "country": clearbit_data.get("geo", {}).get("country"),
            "logo_url": clearbit_data.get("logo"),
            "website": clearbit_data.get("url"),
            "linkedin_url": clearbit_data.get("linkedin", {}).get("handle"),
            "twitter_handle": clearbit_data.get("twitter", {}).get("handle"),
            "facebook_handle": clearbit_data.get("facebook", {}).get("handle"),
            "tech_stack": clearbit_data.get("tech", []),
            "tags": clearbit_data.get("tags", []),
            "type": clearbit_data.get("type"),
            "phone": clearbit_data.get("phone"),
            "email_provider": clearbit_data.get("emailProvider"),
            "funding": {
                "total": clearbit_data.get("metrics", {}).get("raised"),
                "annual_revenue": clearbit_data.get("metrics", {}).get("annualRevenue"),
            },
        }

    def get_tech_stack(self, domain: str) -> list:
        """
        Get technology stack for a company.

        Args:
            domain: Company domain

        Returns:
            List of technologies used by the company
        """
        data = self.enrich_company(domain)
        if data:
            return data.get("tech", [])
        return []

    def is_available(self) -> bool:
        """
        Check if Clearbit service is available (API key configured).

        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.api_key)


# Singleton instance
clearbit_service = ClearbitService()


# Example usage
if __name__ == "__main__":
    service = ClearbitService()

    # Test enrichment
    domain = "anthropic.com"
    print(f"Enriching company: {domain}")

    data = service.enrich_company(domain)
    if data:
        print("\nRaw Clearbit data:")
        print(data)

        print("\n\nNormalized data:")
        normalized = service.extract_company_info(data)
        for key, value in normalized.items():
            print(f"{key}: {value}")

        print("\n\nTech stack:")
        tech = service.get_tech_stack(domain)
        print(tech)
    else:
        print("No data found or API error")
