"""
API endpoints for content generation operations.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.db import get_db, Company, Contact, Intelligence
from app.api.v1.schemas import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    EmailContent,
    ConversationStarters
)
from app.tasks.agent_tasks import generate_outreach_task
from app.agents.generator import ContentGeneratorAgent

router = APIRouter()


@router.post("/", response_model=dict)
def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate personalized outreach content.
    This is a long-running operation that runs in the background.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get contact if specified
    contact = None
    if request.contact_id:
        contact = db.query(Contact).filter(Contact.id == request.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

    # Start background task
    task = generate_outreach_task.delay(
        company_id=request.company_id,
        contact_id=request.contact_id
    )

    return {
        "message": "Content generation started",
        "company_id": request.company_id,
        "contact_id": request.contact_id,
        "task_id": task.id,
        "status": "PENDING",
        "note": "Use GET /api/v1/tasks/{task_id} to check status"
    }


@router.post("/sync", response_model=ContentGenerationResponse)
def generate_content_sync(
    request: ContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate personalized outreach content synchronously (blocking).
    Use for testing or when immediate results are needed.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get contact info
    contact = None
    if request.contact_id:
        contact = db.query(Contact).filter(Contact.id == request.contact_id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

    contact_name = request.contact_name or (contact.name if contact else "there")
    contact_title = request.contact_title or (contact.title if contact else "Decision Maker")

    # Get intelligence for pain points
    intelligence = db.query(Intelligence).filter(
        Intelligence.company_id == request.company_id
    ).order_by(Intelligence.generated_at.desc()).first()

    pain_points = []
    if intelligence and intelligence.pain_points:
        pain_points = [p.get("pain_point", "") for p in intelligence.pain_points[:3]]
    else:
        pain_points = ["operational efficiency", "growth challenges"]

    try:
        # Generate content
        agent = ContentGeneratorAgent()
        result = agent.generate_outreach_campaign(
            company_name=company.name,
            contact_name=contact_name,
            contact_title=contact_title,
            industry=company.industry or "Business",
            pain_points=pain_points,
            product_description=request.product_description
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {result.get('error', 'Unknown error')}"
            )

        # Parse agent output (simplified)
        agent_output = result.get("output", "")

        # Create response (in production, parse agent output to extract structured data)
        email = EmailContent(
            subject=f"Helping {company.name} with {pain_points[0] if pain_points else 'growth'}",
            body=agent_output[:500] if len(agent_output) > 500 else agent_output,
            cta="Would you be open to a 15-minute call to discuss?"
        )

        conversation_starters = ConversationStarters(
            linkedin_message=f"Hi {contact_name}, I noticed {company.name} is working on {pain_points[0] if pain_points else 'interesting challenges'}...",
            email_subject=email.subject,
            phone_opener=f"Hi {contact_name}, I'm reaching out because I work with {company.industry or 'companies like yours'}...",
            connection_request=f"Hi {contact_name}, I'd love to connect and share insights about {pain_points[0] if pain_points else 'the industry'}.",
            followup_subject=f"Following up: {company.name} + {pain_points[0] if pain_points else 'our solution'}"
        )

        # Generate variants if requested
        variants = None
        if request.include_variants:
            variants = {
                "version_a": EmailContent(
                    subject=f"Quick question about {company.name}'s {pain_points[0] if pain_points else 'strategy'}",
                    body="Version A - More direct approach...",
                    cta="Can we schedule a brief call?"
                ),
                "version_b": EmailContent(
                    subject=f"Thought this might interest {company.name}",
                    body="Version B - More story-driven approach...",
                    cta="Would love to hear your thoughts on this."
                )
            }

        return ContentGenerationResponse(
            company_id=company.id,
            contact_id=request.contact_id,
            email=email,
            conversation_starters=conversation_starters,
            variants=variants,
            generated_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content: {str(e)}"
        )


@router.post("/email-only", response_model=EmailContent)
def generate_email_only(
    request: ContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate just an email (no conversation starters or variants).
    Faster endpoint for simple email generation.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get contact info
    contact = None
    if request.contact_id:
        contact = db.query(Contact).filter(Contact.id == request.contact_id).first()

    contact_name = request.contact_name or (contact.name if contact else "there")
    contact_title = request.contact_title or (contact.title if contact else "Decision Maker")

    # Get pain points from intelligence
    intelligence = db.query(Intelligence).filter(
        Intelligence.company_id == request.company_id
    ).order_by(Intelligence.generated_at.desc()).first()

    pain_points = []
    if intelligence and intelligence.pain_points:
        pain_points = [p.get("pain_point", "") for p in intelligence.pain_points[:3]]

    # Generate simple email content
    context = {
        "company_name": company.name,
        "contact_name": contact_name,
        "contact_title": contact_title,
        "industry": company.industry or "Business",
        "pain_points": pain_points or ["business growth"],
        "product_description": request.product_description
    }

    try:
        agent = ContentGeneratorAgent()
        result = agent.run({
            "input": f"Generate a personalized email for: {json.dumps(context)}"
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail="Email generation failed"
            )

        agent_output = result.get("output", "")

        return EmailContent(
            subject=f"Helping {company.name} with {pain_points[0] if pain_points else 'growth'}",
            body=agent_output[:500] if len(agent_output) > 500 else agent_output,
            cta="Would you be open to a quick call?"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating email: {str(e)}"
        )
