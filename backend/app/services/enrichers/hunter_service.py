"""
Hunter.io API integration for email discovery and verification.
Free tier: 25 requests/month
API Docs: https://hunter.io/api-documentation
"""

import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.services.cache_service import cache_service


class HunterService:
    """Service for discovering email patterns and contacts using Hunter.io API."""

    def __init__(self):
        """Initialize Hunter.io service."""
        self.api_key = settings.hunter_api_key
        self.base_url = "https://api.hunter.io/v2"
        self.timeout = 10.0

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Make authenticated request to Hunter.io API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response data or None on error
        """
        if not self.api_key:
            print("Warning: Hunter.io API key not configured")
            return None

        try:
            url = f"{self.base_url}/{endpoint}"
            params = params or {}
            params["api_key"] = self.api_key

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print(f"Hunter.io: Not found for {params}")
                    return None
                elif response.status_code == 429:
                    print("Hunter.io: Rate limit exceeded")
                    return None
                else:
                    print(f"Hunter.io API error: {response.status_code} - {response.text}")
                    return None

        except httpx.TimeoutException:
            print("Hunter.io API request timed out")
            return None
        except Exception as e:
            print(f"Hunter.io API error: {str(e)}")
            return None

    def domain_search(self, domain: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Search for email addresses associated with a domain.

        Args:
            domain: Company domain (e.g., 'anthropic.com')
            use_cache: Whether to use cached data (default: True)

        Returns:
            Email search results including pattern and contacts
        """
        cache_key = f"hunter_domain:{domain}"

        # Check cache first
        if use_cache:
            cached = cache_service.get("hunter", cache_key)
            if cached:
                print(f"Cache hit for Hunter domain: {domain}")
                return cached

        # Make API request
        response = self._make_request("domain-search", params={"domain": domain})

        if response and "data" in response:
            data = response["data"]

            # Cache the result
            if use_cache:
                cache_service.set("hunter", cache_key, data, ttl=settings.cache_ttl)

            return data

        return None

    def email_finder(
        self,
        domain: str,
        first_name: str,
        last_name: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Find email address for a specific person.

        Args:
            domain: Company domain
            first_name: Person's first name
            last_name: Person's last name
            use_cache: Whether to use cached data

        Returns:
            Email finding results with confidence score
        """
        cache_key = f"hunter_email:{domain}:{first_name}:{last_name}"

        # Check cache first
        if use_cache:
            cached = cache_service.get("hunter", cache_key)
            if cached:
                print(f"Cache hit for Hunter email: {first_name} {last_name}")
                return cached

        # Make API request
        response = self._make_request(
            "email-finder",
            params={
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        if response and "data" in response:
            data = response["data"]

            # Cache the result
            if use_cache:
                cache_service.set("hunter", cache_key, data, ttl=settings.cache_ttl)

            return data

        return None

    def email_verifier(self, email: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Verify if an email address is valid and deliverable.

        Args:
            email: Email address to verify
            use_cache: Whether to use cached data

        Returns:
            Verification results with status and score
        """
        cache_key = f"hunter_verify:{email}"

        # Check cache first
        if use_cache:
            cached = cache_service.get("hunter", cache_key)
            if cached:
                print(f"Cache hit for Hunter verify: {email}")
                return cached

        # Make API request
        response = self._make_request("email-verifier", params={"email": email})

        if response and "data" in response:
            data = response["data"]

            # Cache the result
            if use_cache:
                cache_service.set("hunter", cache_key, data, ttl=settings.cache_ttl)

            return data

        return None

    def get_email_pattern(self, domain: str) -> Optional[str]:
        """
        Get the email pattern for a domain.

        Args:
            domain: Company domain

        Returns:
            Email pattern string (e.g., '{first}.{last}@domain.com')
        """
        data = self.domain_search(domain)
        if data:
            return data.get("pattern")
        return None

    def get_contacts(self, domain: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of contacts for a domain.

        Args:
            domain: Company domain
            limit: Maximum number of contacts to return

        Returns:
            List of contact dictionaries
        """
        data = self.domain_search(domain)
        if data and "emails" in data:
            emails = data["emails"][:limit]
            return [
                {
                    "email": email.get("value"),
                    "first_name": email.get("first_name"),
                    "last_name": email.get("last_name"),
                    "position": email.get("position"),
                    "department": email.get("department"),
                    "seniority": email.get("seniority"),
                    "confidence": email.get("confidence"),
                    "linkedin": email.get("linkedin"),
                    "twitter": email.get("twitter"),
                    "phone_number": email.get("phone_number"),
                }
                for email in emails
            ]
        return []

    def extract_email_info(self, hunter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize email information.

        Args:
            hunter_data: Raw Hunter.io API response

        Returns:
            Normalized email data
        """
        if not hunter_data:
            return {}

        return {
            "pattern": hunter_data.get("pattern"),
            "organization": hunter_data.get("organization"),
            "total_emails": hunter_data.get("total", 0),
            "contacts": self.get_contacts(hunter_data.get("domain", "")),
        }

    def generate_email(self, first_name: str, last_name: str, domain: str) -> Optional[str]:
        """
        Generate likely email address based on company pattern.

        Args:
            first_name: Person's first name
            last_name: Person's last name
            domain: Company domain

        Returns:
            Generated email address or None
        """
        pattern = self.get_email_pattern(domain)
        if not pattern:
            return None

        # Parse pattern and generate email
        email = pattern.lower()
        email = email.replace("{first}", first_name.lower())
        email = email.replace("{last}", last_name.lower())
        email = email.replace("{f}", first_name[0].lower() if first_name else "")
        email = email.replace("{l}", last_name[0].lower() if last_name else "")

        return email

    def is_available(self) -> bool:
        """
        Check if Hunter.io service is available (API key configured).

        Returns:
            True if API key is set, False otherwise
        """
        return bool(self.api_key)


# Singleton instance
hunter_service = HunterService()


# Example usage
if __name__ == "__main__":
    service = HunterService()

    # Test domain search
    domain = "anthropic.com"
    print(f"Searching emails for domain: {domain}")

    data = service.domain_search(domain)
    if data:
        print("\n=== Email Pattern ===")
        print(service.get_email_pattern(domain))

        print("\n=== Contacts ===")
        contacts = service.get_contacts(domain, limit=5)
        for contact in contacts:
            print(f"{contact['first_name']} {contact['last_name']}: {contact['email']}")
            print(f"  Position: {contact['position']}")
            print(f"  Confidence: {contact['confidence']}")
            print()

        print("\n=== Email Generation ===")
        generated = service.generate_email("John", "Doe", domain)
        print(f"Generated email: {generated}")
    else:
        print("No data found or API error")
