#!/usr/bin/env python3
"""
Sales Intelligence Agent - Interactive Demo Script

This script demonstrates all key features of the Sales Intelligence Agent
with a user-friendly interactive interface.

Usage:
    python demo_script.py
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SalesIntelligenceDemo:
    """Interactive demo for Sales Intelligence Agent."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.company_id: Optional[int] = None
        self.contact_id: Optional[int] = None

    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

    def print_success(self, text: str):
        """Print success message."""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")

    def print_error(self, text: str):
        """Print error message."""
        print(f"{Colors.RED}✗ {text}{Colors.END}")

    def print_info(self, text: str):
        """Print info message."""
        print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

    def print_warning(self, text: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

    def wait_for_enter(self, message: str = "Press Enter to continue..."):
        """Wait for user input."""
        input(f"\n{Colors.YELLOW}{message}{Colors.END}")

    def check_health(self) -> bool:
        """Check if the API is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_success("API is healthy and responding")
                return True
            else:
                self.print_error(f"API returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to API. Is the server running?")
            self.print_info("Start services with: docker-compose up -d")
            return False
        except Exception as e:
            self.print_error(f"Error checking API health: {str(e)}")
            return False

    def demo_create_company(self) -> Optional[int]:
        """Demo: Create a company."""
        self.print_header("STEP 1: Create Company")

        print("Creating a sample company record...")
        print(f"{Colors.CYAN}Company: TechCorp Inc{Colors.END}")
        print(f"{Colors.CYAN}Industry: Software Development{Colors.END}")
        print(f"{Colors.CYAN}Domain: techcorp.com{Colors.END}\n")

        company_data = {
            "name": "TechCorp Inc",
            "domain": "techcorp.com",
            "industry": "Software Development",
            "size": "100-200",
            "employee_count": 150,
            "location": "San Francisco, CA",
            "description": "Fast-growing B2B SaaS company providing project management tools",
            "website": "https://techcorp.com",
            "linkedin_url": "https://linkedin.com/company/techcorp"
        }

        try:
            response = requests.post(
                f"{self.api_url}/companies",
                json=company_data,
                timeout=10
            )

            if response.status_code == 201:
                company = response.json()
                self.company_id = company["id"]
                self.print_success(f"Company created with ID: {self.company_id}")
                print(f"\n{Colors.BOLD}Company Details:{Colors.END}")
                print(f"  Name: {company['name']}")
                print(f"  Domain: {company['domain']}")
                print(f"  Industry: {company['industry']}")
                print(f"  Status: {company['status']}")
                return self.company_id
            elif response.status_code == 400:
                self.print_warning("Company may already exist")
                # Try to get existing company
                response = requests.get(f"{self.api_url}/companies?page=1&page_size=1")
                if response.status_code == 200:
                    companies = response.json()["companies"]
                    if companies:
                        self.company_id = companies[0]["id"]
                        self.print_info(f"Using existing company ID: {self.company_id}")
                        return self.company_id
            else:
                self.print_error(f"Failed to create company: {response.status_code}")
                print(response.text)
                return None

        except Exception as e:
            self.print_error(f"Error creating company: {str(e)}")
            return None

    def demo_build_profile(self, company_id: int):
        """Demo: Build company profile."""
        self.print_header("STEP 2: Build Company Profile")

        print("Building comprehensive company profile...")
        print("This will:")
        print("  • Collect data from multiple sources")
        print("  • Find key decision makers")
        print("  • Identify technology stack")
        print("  • Calculate lead score\n")

        try:
            response = requests.post(
                f"{self.api_url}/profiles/sync",
                json={
                    "company_id": company_id,
                    "include_contacts": True,
                    "use_cache": True
                },
                timeout=60
            )

            if response.status_code == 200:
                profile = response.json()
                self.print_success("Profile built successfully!")

                print(f"\n{Colors.BOLD}Profile Results:{Colors.END}")
                print(f"  Lead Score: {Colors.GREEN}{profile.get('lead_score', 0):.1f}/100{Colors.END}")
                print(f"  Contacts Found: {profile.get('contacts_found', 0)}")
                print(f"  Contacts Saved: {profile.get('contacts_saved', 0)}")
                print(f"  Sources Used: {', '.join(profile.get('sources_used', []))}")

                if profile.get('profile'):
                    prof = profile['profile']
                    print(f"\n{Colors.BOLD}Company Data:{Colors.END}")
                    print(f"  Industry: {prof.get('industry', 'N/A')}")
                    print(f"  Employees: {prof.get('employee_count', 'N/A')}")
                    if prof.get('tech_stack') and prof['tech_stack'].get('technologies'):
                        print(f"  Tech Stack: {', '.join(prof['tech_stack']['technologies'][:5])}")

                return True
            else:
                self.print_error(f"Failed to build profile: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            self.print_error(f"Error building profile: {str(e)}")
            return False

    def demo_analyze_intelligence(self, company_id: int):
        """Demo: Analyze company intelligence."""
        self.print_header("STEP 3: Analyze Intelligence (AI-Powered)")

        print("Analyzing company with Claude AI...")
        print("This will:")
        print("  • Identify pain points and challenges")
        print("  • Determine business priorities")
        print("  • Recommend communication approach")
        print("  • Generate executive summary\n")

        try:
            response = requests.post(
                f"{self.api_url}/intelligence/sync",
                json={
                    "company_id": company_id,
                    "force_refresh": False
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                self.print_success("Intelligence analysis complete!")

                if result.get('intelligence'):
                    intel = result['intelligence']

                    print(f"\n{Colors.BOLD}Pain Points Identified:{Colors.END}")
                    for i, pp in enumerate(intel.get('pain_points', [])[:3], 1):
                        print(f"  {i}. {pp.get('pain_point', 'N/A')}")
                        print(f"     Reasoning: {pp.get('reasoning', 'N/A')}")

                    print(f"\n{Colors.BOLD}Business Priorities:{Colors.END}")
                    for i, priority in enumerate(intel.get('priorities', [])[:3], 1):
                        urgency = priority.get('urgency_level', 'medium')
                        color = Colors.RED if urgency == 'high' else Colors.YELLOW if urgency == 'medium' else Colors.GREEN
                        print(f"  {i}. {priority.get('priority', 'N/A')} [{color}{urgency.upper()}{Colors.END}]")

                    if intel.get('approach_strategy'):
                        print(f"\n{Colors.BOLD}Recommended Approach:{Colors.END}")
                        strategy = intel['approach_strategy']
                        # Print first 200 chars
                        print(f"  {strategy[:200]}..." if len(strategy) > 200 else f"  {strategy}")

                    print(f"\n{Colors.BOLD}Confidence Score:{Colors.END} {intel.get('confidence_score', 0):.0%}")

                return True
            else:
                self.print_error(f"Failed to analyze intelligence: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            self.print_error(f"Error analyzing intelligence: {str(e)}")
            return False

    def demo_generate_content(self, company_id: int):
        """Demo: Generate outreach content."""
        self.print_header("STEP 4: Generate Outreach Content (AI-Powered)")

        print("Generating personalized outreach content...")
        print("This will:")
        print("  • Create personalized cold email")
        print("  • Generate conversation starters")
        print("  • Produce A/B testing variants\n")

        try:
            response = requests.post(
                f"{self.api_url}/content/sync",
                json={
                    "company_id": company_id,
                    "contact_name": "Sarah Johnson",
                    "contact_title": "VP of Engineering",
                    "product_description": "Cloud infrastructure platform that reduces deployment time by 70% and costs by 40%",
                    "tone": "professional",
                    "include_variants": True
                },
                timeout=90
            )

            if response.status_code == 200:
                content = response.json()
                self.print_success("Content generated successfully!")

                if content.get('email'):
                    email = content['email']
                    print(f"\n{Colors.BOLD}Generated Email:{Colors.END}")
                    print(f"\n{Colors.UNDERLINE}Subject:{Colors.END}")
                    print(f"{email.get('subject', 'N/A')}")
                    print(f"\n{Colors.UNDERLINE}Body:{Colors.END}")
                    body = email.get('body', 'N/A')
                    # Print first 300 chars
                    print(body[:300] + "..." if len(body) > 300 else body)
                    print(f"\n{Colors.UNDERLINE}CTA:{Colors.END}")
                    print(f"{email.get('cta', 'N/A')}")

                if content.get('conversation_starters'):
                    starters = content['conversation_starters']
                    print(f"\n{Colors.BOLD}Conversation Starters:{Colors.END}")
                    if starters.get('linkedin_message'):
                        print(f"\n{Colors.CYAN}LinkedIn:{Colors.END}")
                        print(f"{starters['linkedin_message'][:150]}...")
                    if starters.get('phone_opener'):
                        print(f"\n{Colors.CYAN}Phone:{Colors.END}")
                        print(f"{starters['phone_opener'][:150]}...")

                if content.get('variants'):
                    print(f"\n{Colors.BOLD}A/B Variants Generated:{Colors.END}")
                    print(f"  ✓ Version A (Direct approach)")
                    print(f"  ✓ Version B (Story-driven)")

                return True
            else:
                self.print_error(f"Failed to generate content: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            self.print_error(f"Error generating content: {str(e)}")
            return False

    def demo_list_companies(self):
        """Demo: List all companies."""
        self.print_header("BONUS: List All Companies")

        print("Retrieving all companies from database...\n")

        try:
            response = requests.get(
                f"{self.api_url}/companies?page=1&page_size=10",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                companies = data.get('companies', [])
                total = data.get('total', 0)

                self.print_success(f"Found {total} companies in database")

                if companies:
                    print(f"\n{Colors.BOLD}Companies:{Colors.END}")
                    for i, company in enumerate(companies, 1):
                        score = company.get('lead_score', 0)
                        score_color = Colors.GREEN if score >= 70 else Colors.YELLOW if score >= 50 else Colors.RED
                        print(f"  {i}. {company['name']} ({company.get('domain', 'N/A')})")
                        print(f"     Lead Score: {score_color}{score:.1f}/100{Colors.END} | Status: {company.get('status', 'N/A')}")

                return True
            else:
                self.print_error(f"Failed to list companies: {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Error listing companies: {str(e)}")
            return False

    def run_full_demo(self):
        """Run the complete demo workflow."""
        self.print_header("🚀 SALES INTELLIGENCE AGENT - LIVE DEMO 🚀")

        print(f"{Colors.BOLD}This demo will showcase:{Colors.END}")
        print("  1. Company creation and data management")
        print("  2. Profile building from multiple sources")
        print("  3. AI-powered intelligence analysis")
        print("  4. Personalized content generation")
        print("  5. Complete workflow integration\n")

        self.wait_for_enter("Press Enter to start the demo...")

        # Check API health
        self.print_header("System Health Check")
        if not self.check_health():
            self.print_error("\nDemo cannot continue. Please ensure services are running.")
            self.print_info("Run: docker-compose up -d")
            return False

        self.wait_for_enter()

        # Step 1: Create company
        company_id = self.demo_create_company()
        if not company_id:
            self.print_error("Failed to create company. Demo stopped.")
            return False

        self.wait_for_enter()

        # Step 2: Build profile
        if not self.demo_build_profile(company_id):
            self.print_warning("Profile building failed, but continuing demo...")

        self.wait_for_enter()

        # Step 3: Analyze intelligence
        if not self.demo_analyze_intelligence(company_id):
            self.print_warning("Intelligence analysis failed, but continuing demo...")

        self.wait_for_enter()

        # Step 4: Generate content
        if not self.demo_generate_content(company_id):
            self.print_warning("Content generation failed, but continuing demo...")

        self.wait_for_enter()

        # Bonus: List companies
        self.demo_list_companies()

        # Summary
        self.print_header("✅ DEMO COMPLETE!")

        print(f"{Colors.BOLD}What we just demonstrated:{Colors.END}")
        print(f"  {Colors.GREEN}✓{Colors.END} Complete sales intelligence workflow")
        print(f"  {Colors.GREEN}✓{Colors.END} Multi-agent AI system in action")
        print(f"  {Colors.GREEN}✓{Colors.END} Data collection from multiple sources")
        print(f"  {Colors.GREEN}✓{Colors.END} Claude AI-powered analysis")
        print(f"  {Colors.GREEN}✓{Colors.END} Personalized content generation")
        print(f"  {Colors.GREEN}✓{Colors.END} RESTful API with full CRUD operations")

        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print(f"  • Explore API docs: {Colors.CYAN}http://localhost:8000/docs{Colors.END}")
        print(f"  • Monitor Celery: {Colors.CYAN}http://localhost:5555{Colors.END}")
        print(f"  • Read API guide: {Colors.CYAN}API_USAGE_GUIDE.md{Colors.END}")
        print(f"  • Build frontend: {Colors.CYAN}NEXT_STEPS.md{Colors.END}")

        print(f"\n{Colors.GREEN}{Colors.BOLD}Thank you for watching the demo!{Colors.END} 🎉\n")

        return True


def main():
    """Main entry point."""
    demo = SalesIntelligenceDemo()

    try:
        demo.run_full_demo()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {str(e)}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
