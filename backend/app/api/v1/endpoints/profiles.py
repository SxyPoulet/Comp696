"""
API endpoints for profile building operations.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db, Company, Contact
from app.api.v1.schemas import ProfileBuildRequest, ProfileBuildResponse
from app.tasks.agent_tasks import build_profile_task
from app.agents.profiler import ProfileBuilderAgent
from app.services.data_collector import data_collector
import asyncio

router = APIRouter()


@router.post("/", response_model=ProfileBuildResponse)
def build_profile(
    request: ProfileBuildRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Build a comprehensive company profile.
    This is a long-running operation that runs in the background.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update status
    company.status = "profiling"
    db.commit()

    # Start background task
    task = build_profile_task.delay(
        company_id=request.company_id,
        include_contacts=request.include_contacts,
        use_cache=request.use_cache
    )

    return ProfileBuildResponse(
        company_id=request.company_id,
        status="started",
        task_id=task.id,
        message=f"Profile building started for {company.name}"
    )


@router.post("/sync", response_model=dict)
async def build_profile_sync(
    request: ProfileBuildRequest,
    db: Session = Depends(get_db)
):
    """
    Build a company profile synchronously (blocking).
    Use for testing or when immediate results are needed.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if not company.domain:
        raise HTTPException(
            status_code=400,
            detail="Company domain is required for profile building"
        )

    # Update status
    company.status = "profiling"
    db.commit()

    try:
        # Collect profile data
        profile = await data_collector.collect_full_profile(
            company_name=company.name,
            domain=company.domain,
            include_contacts=request.include_contacts,
            use_cache=request.use_cache
        )

        # Update company with collected data
        if profile.get("data"):
            data = profile["data"]
            company.employee_count = data.get("employee_count") or company.employee_count
            company.industry = data.get("industry") or company.industry
            company.description = data.get("description") or company.description
            company.lead_score = profile.get("lead_score", 0.0)
            company.tech_stack = {"technologies": data.get("tech_stack", [])}
            company.status = "analyzed"
            company.last_analyzed_at = datetime.utcnow()

        # Save or update contacts
        contacts_saved = 0
        if request.include_contacts and profile.get("contacts"):
            for contact_data in profile["contacts"]:
                # Check if contact already exists
                existing_contact = db.query(Contact).filter(
                    Contact.company_id == company.id,
                    Contact.email == contact_data.get("email")
                ).first()

                if not existing_contact and contact_data.get("email"):
                    contact = Contact(
                        company_id=company.id,
                        name=contact_data.get("name", "Unknown"),
                        title=contact_data.get("title"),
                        email=contact_data.get("email"),
                        is_decision_maker=contact_data.get("is_decision_maker", False),
                        department=contact_data.get("department"),
                        seniority_level=contact_data.get("seniority_level"),
                        source="automated_discovery"
                    )
                    db.add(contact)
                    contacts_saved += 1

        db.commit()
        db.refresh(company)

        return {
            "company_id": company.id,
            "status": "completed",
            "lead_score": company.lead_score,
            "contacts_found": len(profile.get("contacts", [])),
            "contacts_saved": contacts_saved,
            "sources_used": profile.get("data", {}).get("sources_used", []),
            "profile": {
                "name": company.name,
                "domain": company.domain,
                "industry": company.industry,
                "employee_count": company.employee_count,
                "description": company.description,
                "tech_stack": company.tech_stack
            }
        }

    except Exception as e:
        company.status = "error"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Error building profile: {str(e)}"
        )
