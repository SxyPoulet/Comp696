"""
API endpoints for company operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db, Company, Contact, Intelligence
from app.api.v1.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyDetail,
    CompanyList,
    ErrorResponse
)

router = APIRouter()


@router.post("/", response_model=CompanyDetail, status_code=201)
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new company record.
    """
    # Check if company already exists
    existing = db.query(Company).filter(Company.domain == company.domain).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Company with domain '{company.domain}' already exists"
        )

    # Create new company
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return db_company


@router.get("/", response_model=CompanyList)
def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None, description="Filter by status"),
    industry: str = Query(None, description="Filter by industry"),
    min_score: float = Query(None, ge=0, le=100, description="Minimum lead score"),
    db: Session = Depends(get_db)
):
    """
    List companies with pagination and filtering.
    """
    query = db.query(Company)

    # Apply filters
    if status:
        query = query.filter(Company.status == status)
    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    if min_score is not None:
        query = query.filter(Company.lead_score >= min_score)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    companies = query.order_by(Company.lead_score.desc()).offset(offset).limit(page_size).all()

    return CompanyList(
        total=total,
        page=page,
        page_size=page_size,
        companies=companies
    )


@router.get("/{company_id}", response_model=CompanyDetail)
def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific company.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.put("/{company_id}", response_model=CompanyDetail)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update company information.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update fields
    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a company and all associated data.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()

    return None


@router.get("/{company_id}/contacts", response_model=List[dict])
def get_company_contacts(
    company_id: int,
    decision_makers_only: bool = Query(False, description="Return only decision makers"),
    db: Session = Depends(get_db)
):
    """
    Get all contacts for a company.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    query = db.query(Contact).filter(Contact.company_id == company_id)

    if decision_makers_only:
        query = query.filter(Contact.is_decision_maker == True)

    contacts = query.all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "title": c.title,
            "email": c.email,
            "phone": c.phone,
            "is_decision_maker": c.is_decision_maker,
            "department": c.department,
            "seniority_level": c.seniority_level
        }
        for c in contacts
    ]


@router.get("/{company_id}/intelligence", response_model=dict)
def get_company_intelligence(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Get intelligence analysis for a company.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get latest intelligence
    intelligence = db.query(Intelligence).filter(
        Intelligence.company_id == company_id
    ).order_by(Intelligence.generated_at.desc()).first()

    if not intelligence:
        raise HTTPException(
            status_code=404,
            detail="No intelligence available. Run analysis first."
        )

    return {
        "id": intelligence.id,
        "company_id": intelligence.company_id,
        "summary": intelligence.summary,
        "pain_points": intelligence.pain_points,
        "priorities": intelligence.priorities,
        "decision_makers": intelligence.decision_makers,
        "communication_style": intelligence.communication_style,
        "approach_strategy": intelligence.approach_strategy,
        "recommended_messaging": intelligence.recommended_messaging,
        "confidence_score": intelligence.confidence_score,
        "generated_at": intelligence.generated_at
    }
