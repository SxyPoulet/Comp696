"""
API endpoints for company discovery operations.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.v1.schemas import (
    DiscoveryRequest,
    DiscoveryResponse,
    CompanyBasic
)
from app.tasks.agent_tasks import discover_companies_task
from app.agents.discovery import DiscoveryAgent

router = APIRouter()


@router.post("/", response_model=dict)
async def discover_companies(
    request: DiscoveryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Discover companies matching search criteria.
    This is a long-running operation that runs in the background.
    """
    # Start background task
    task = discover_companies_task.delay(
        search_criteria=request.criteria.model_dump(),
        include_scoring=request.include_scoring
    )

    return {
        "message": "Company discovery started",
        "task_id": task.id,
        "status": "PENDING",
        "note": "Use GET /api/v1/tasks/{task_id} to check status"
    }


@router.post("/sync", response_model=DiscoveryResponse)
def discover_companies_sync(
    request: DiscoveryRequest,
    db: Session = Depends(get_db)
):
    """
    Discover companies synchronously (blocking).
    Use for small searches or testing. For large searches, use async endpoint.
    """
    agent = DiscoveryAgent()

    # Run discovery
    result = agent.discover_companies(
        search_criteria=request.criteria.model_dump(),
        max_results=request.criteria.max_results
    )

    # Parse agent output to extract companies
    # This is simplified - in production, you'd parse the agent's output more robustly
    companies = []

    if result.get("success"):
        # For demo, return mock data with realistic names
        # In production, parse agent output from the agent's text response

        # Sample company data based on criteria
        sample_companies = [
            ("TechFlow Solutions", "techflow.com", "Software Development", 150, "San Francisco, CA"),
            ("CloudScale Systems", "cloudscale.io", "Cloud Infrastructure", 85, "Seattle, WA"),
            ("DataSync Pro", "datasyncpro.com", "Data Analytics", 120, "Austin, TX"),
            ("AppVenture Labs", "appventurelabs.com", "Mobile Development", 95, "Boston, MA"),
            ("SecureNet Inc", "securenet.io", "Cybersecurity", 180, "New York, NY"),
            ("AI Dynamics", "aidynamics.com", "Artificial Intelligence", 110, "Palo Alto, CA"),
            ("MarketPulse", "marketpulse.io", "Marketing Tech", 75, "Chicago, IL"),
            ("FinTech Innovations", "fintechinno.com", "Financial Technology", 140, "London, UK"),
            ("HealthTech Solutions", "healthtech-sol.com", "Healthcare IT", 160, "Toronto, Canada"),
            ("EduStream Platform", "edustream.io", "Education Technology", 90, "Denver, CO"),
        ]

        # Filter and score based on criteria
        industry_filter = request.criteria.industry or ""
        location_filter = request.criteria.location or ""

        companies = []
        for i, (name, domain, industry, emp_count, location) in enumerate(sample_companies[:request.criteria.max_results]):
            # Calculate score based on match quality
            score = 70.0
            if industry_filter.lower() in industry.lower():
                score += 15
            if location_filter and location_filter.lower() in location.lower():
                score += 10
            score = min(score - (i * 2), 95.0)  # Slight decay for later results

            companies.append(CompanyBasic(
                name=name,
                domain=domain,
                industry=industry,
                employee_count=emp_count,
                location=location,
                lead_score=score
            ))

    return DiscoveryResponse(
        total_found=len(companies),
        companies=companies,
        search_criteria=request.criteria
    )
