"""
Pydantic schemas for request and response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# ============================================================================
# Search & Discovery Schemas
# ============================================================================

class SearchCriteria(BaseModel):
    """Search criteria for discovering companies."""
    industry: Optional[str] = Field(None, description="Industry or sector")
    location: Optional[str] = Field(None, description="Geographic location")
    size: Optional[str] = Field(None, description="Company size range (e.g., '50-200')")
    keywords: Optional[str] = Field(None, description="Additional search keywords")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")


class DiscoveryRequest(BaseModel):
    """Request to discover companies."""
    criteria: SearchCriteria
    include_scoring: bool = Field(True, description="Calculate lead scores")


class CompanyBasic(BaseModel):
    """Basic company information."""
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    location: Optional[str] = None
    lead_score: Optional[float] = Field(None, ge=0, le=100)


class DiscoveryResponse(BaseModel):
    """Response from company discovery."""
    total_found: int
    companies: List[CompanyBasic]
    search_criteria: SearchCriteria
    search_id: Optional[str] = None


# ============================================================================
# Company Profile Schemas
# ============================================================================

class CompanyCreate(BaseModel):
    """Request to create a new company record."""
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    size: Optional[str] = Field(None, max_length=50)
    employee_count: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=255)


class CompanyUpdate(BaseModel):
    """Request to update company information."""
    name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    size: Optional[str] = Field(None, max_length=50)
    employee_count: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    lead_score: Optional[float] = Field(None, ge=0, le=100)


class ContactBasic(BaseModel):
    """Basic contact information."""
    id: int
    name: str
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    is_decision_maker: bool = False
    department: Optional[str] = None
    seniority_level: Optional[str] = None

    class Config:
        from_attributes = True


class CompanyDetail(BaseModel):
    """Detailed company information."""
    id: int
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    employee_count: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    lead_score: float = 0.0
    status: str = "discovered"
    tech_stack: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    contacts: List[ContactBasic] = []

    class Config:
        from_attributes = True


class CompanyList(BaseModel):
    """Paginated list of companies."""
    total: int
    page: int
    page_size: int
    companies: List[CompanyDetail]


# ============================================================================
# Profile Building Schemas
# ============================================================================

class ProfileBuildRequest(BaseModel):
    """Request to build company profile."""
    company_id: int = Field(..., description="Company ID")
    include_contacts: bool = Field(True, description="Include contact discovery")
    use_cache: bool = Field(True, description="Use cached data if available")


class ProfileBuildResponse(BaseModel):
    """Response from profile building."""
    company_id: int
    status: str
    task_id: Optional[str] = None
    message: str


# ============================================================================
# Intelligence Analysis Schemas
# ============================================================================

class AnalysisRequest(BaseModel):
    """Request to analyze a company."""
    company_id: int = Field(..., description="Company ID to analyze")
    force_refresh: bool = Field(False, description="Force new analysis")


class PainPoint(BaseModel):
    """Identified pain point."""
    pain_point: str
    reasoning: str
    impact: str


class Priority(BaseModel):
    """Business priority."""
    priority: str
    reasoning: str
    urgency_level: str


class IntelligenceSummary(BaseModel):
    """Intelligence analysis summary."""
    company_id: int
    pain_points: List[Dict[str, Any]] = []
    priorities: List[Dict[str, Any]] = []
    communication_approach: Optional[Dict[str, Any]] = None
    executive_summary: Optional[str] = None
    generated_at: datetime
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class AnalysisResponse(BaseModel):
    """Response from intelligence analysis."""
    company_id: int
    status: str
    task_id: Optional[str] = None
    intelligence: Optional[IntelligenceSummary] = None
    message: str


# ============================================================================
# Content Generation Schemas
# ============================================================================

class ContentGenerationRequest(BaseModel):
    """Request to generate outreach content."""
    company_id: int = Field(..., description="Company ID")
    contact_id: Optional[int] = Field(None, description="Specific contact ID")
    contact_name: Optional[str] = Field(None, description="Contact name if no ID")
    contact_title: Optional[str] = Field(None, description="Contact title")
    product_description: str = Field(..., description="Your product/service description")
    tone: Optional[str] = Field("professional", description="Email tone")
    include_variants: bool = Field(True, description="Generate A/B variants")


class EmailContent(BaseModel):
    """Generated email content."""
    subject: str
    body: str
    cta: Optional[str] = None


class ConversationStarters(BaseModel):
    """Conversation starters for multiple channels."""
    linkedin_message: Optional[str] = None
    email_subject: Optional[str] = None
    phone_opener: Optional[str] = None
    connection_request: Optional[str] = None
    followup_subject: Optional[str] = None


class ContentGenerationResponse(BaseModel):
    """Response from content generation."""
    company_id: int
    contact_id: Optional[int] = None
    email: EmailContent
    conversation_starters: Optional[ConversationStarters] = None
    variants: Optional[Dict[str, EmailContent]] = None
    generated_at: datetime


# ============================================================================
# Contact Schemas
# ============================================================================

class ContactCreate(BaseModel):
    """Request to create a contact."""
    company_id: int
    name: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    is_decision_maker: bool = False
    department: Optional[str] = Field(None, max_length=100)
    seniority_level: Optional[str] = Field(None, max_length=50)


class ContactDetail(BaseModel):
    """Detailed contact information."""
    id: int
    company_id: int
    name: str
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_decision_maker: bool = False
    department: Optional[str] = None
    seniority_level: Optional[str] = None
    source: Optional[str] = None
    verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Background Task Schemas
# ============================================================================

class TaskStatus(BaseModel):
    """Background task status."""
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
