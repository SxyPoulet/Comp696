"""
API endpoints for intelligence analysis operations.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.db import get_db, Company, Intelligence
from app.api.v1.schemas import AnalysisRequest, AnalysisResponse, IntelligenceSummary
from app.tasks.agent_tasks import analyze_company_task
from app.agents.analyst import IntelligenceAnalystAgent

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
def analyze_company(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze a company and generate intelligence insights.
    This is a long-running operation that runs in the background.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if recent analysis exists and force_refresh is False
    if not request.force_refresh:
        recent_intelligence = db.query(Intelligence).filter(
            Intelligence.company_id == request.company_id
        ).order_by(Intelligence.generated_at.desc()).first()

        if recent_intelligence:
            # Return existing intelligence
            return AnalysisResponse(
                company_id=request.company_id,
                status="completed",
                intelligence=IntelligenceSummary(
                    company_id=recent_intelligence.company_id,
                    pain_points=recent_intelligence.pain_points or [],
                    priorities=recent_intelligence.priorities or [],
                    communication_approach=json.loads(recent_intelligence.communication_style) if recent_intelligence.communication_style else None,
                    executive_summary=recent_intelligence.summary,
                    generated_at=recent_intelligence.generated_at,
                    confidence_score=recent_intelligence.confidence_score
                ),
                message="Returning existing analysis. Use force_refresh=true for new analysis."
            )

    # Start background task
    task = analyze_company_task.delay(company_id=request.company_id)

    return AnalysisResponse(
        company_id=request.company_id,
        status="started",
        task_id=task.id,
        intelligence=None,
        message=f"Intelligence analysis started for {company.name}"
    )


@router.post("/sync", response_model=dict)
def analyze_company_sync(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a company synchronously (blocking).
    Use for testing or when immediate results are needed.
    """
    # Check if company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Prepare company data for analysis
    company_data = {
        "name": company.name,
        "domain": company.domain,
        "industry": company.industry,
        "employee_count": company.employee_count,
        "description": company.description,
        "founded_year": None,  # Could extract if available
        "tech_stack": company.tech_stack.get("technologies", []) if company.tech_stack else [],
        "lead_score": company.lead_score
    }

    try:
        # Run intelligence analysis
        agent = IntelligenceAnalystAgent()
        result = agent.analyze_company(company_data)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}"
            )

        # Parse agent output (simplified - in production, parse more robustly)
        agent_output = result.get("output", "")

        # Create or update intelligence record
        intelligence = Intelligence(
            company_id=company.id,
            summary=agent_output[:1000] if len(agent_output) > 1000 else agent_output,  # Store first 1000 chars as summary
            pain_points=[
                {"pain_point": "Legacy systems", "reasoning": "Common for established companies", "impact": "Slows innovation"},
                {"pain_point": "Scaling challenges", "reasoning": "Growing employee base", "impact": "Operational efficiency"}
            ],  # Placeholder - would parse from agent output
            priorities=[
                {"priority": "Digital transformation", "reasoning": "Industry trend", "urgency_level": "high"},
                {"priority": "Team growth", "reasoning": "Expanding operations", "urgency_level": "medium"}
            ],  # Placeholder - would parse from agent output
            decision_makers=[],
            communication_style="Professional and data-driven",
            approach_strategy=agent_output,
            recommended_messaging="Focus on efficiency and scalability benefits",
            confidence_score=0.85,
            agent_version="v1.0"
        )

        db.add(intelligence)
        db.commit()
        db.refresh(intelligence)

        return {
            "company_id": company.id,
            "status": "completed",
            "intelligence": {
                "id": intelligence.id,
                "summary": intelligence.summary,
                "pain_points": intelligence.pain_points,
                "priorities": intelligence.priorities,
                "approach_strategy": intelligence.approach_strategy,
                "recommended_messaging": intelligence.recommended_messaging,
                "confidence_score": intelligence.confidence_score,
                "generated_at": intelligence.generated_at
            },
            "agent_output": agent_output
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing company: {str(e)}"
        )
