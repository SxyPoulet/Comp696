from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class Company(Base):
    """Company model for storing target company information."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, index=True)
    industry = Column(String(255), index=True)
    size = Column(String(50))  # e.g., "50-200", "1000+"
    employee_count = Column(Integer)
    location = Column(String(255))
    description = Column(Text)
    website = Column(String(255))
    linkedin_url = Column(String(255))

    # Lead scoring
    lead_score = Column(Float, default=0.0)  # 0-100

    # Technology stack (JSON array)
    tech_stack = Column(JSON)

    # Enrichment data
    funding_info = Column(JSON)
    company_metrics = Column(JSON)

    # Status tracking
    status = Column(String(50), default="discovered")  # discovered, profiling, analyzed, contacted

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed_at = Column(DateTime)

    # Relationships
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    intelligence = relationship("Intelligence", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', domain='{self.domain}')>"


class Contact(Base):
    """Contact model for storing key personnel information."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Personal information
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    email = Column(String(255), index=True)
    linkedin_url = Column(String(255))
    phone = Column(String(50))

    # Role classification
    is_decision_maker = Column(Boolean, default=False)
    department = Column(String(100))  # Engineering, Sales, Marketing, etc.
    seniority_level = Column(String(50))  # C-Level, VP, Director, Manager, IC

    # Contact data
    email_pattern = Column(String(100))  # For Hunter.io patterns
    verified = Column(Boolean, default=False)

    # Metadata
    source = Column(String(100))  # linkedin, hunter, clearbit, manual

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="contacts")

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', title='{self.title}')>"


class Intelligence(Base):
    """Intelligence model for storing AI-generated insights."""

    __tablename__ = "intelligence"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # AI-generated content
    summary = Column(Text)  # Executive summary
    pain_points = Column(JSON)  # List of identified pain points
    priorities = Column(JSON)  # Business priorities
    decision_makers = Column(JSON)  # Key people analysis
    communication_style = Column(Text)  # Recommended approach

    # Strategic insights
    approach_strategy = Column(Text)
    recommended_messaging = Column(Text)
    competitive_insights = Column(JSON)

    # Outreach content
    email_templates = Column(JSON)  # Generated email variants
    conversation_starters = Column(JSON)  # Opening lines

    # Metadata
    agent_version = Column(String(50))
    confidence_score = Column(Float)  # 0-1

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="intelligence")

    def __repr__(self):
        return f"<Intelligence(id={self.id}, company_id={self.company_id})>"


class SearchHistory(Base):
    """Track search queries and results for analytics."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)

    # Search parameters
    query = Column(Text)
    industry = Column(String(255))
    company_size = Column(String(50))
    location = Column(String(255))
    keywords = Column(JSON)

    # Results
    total_results = Column(Integer)
    companies_discovered = Column(JSON)  # List of company IDs

    # Performance metrics
    execution_time = Column(Float)  # seconds

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, total_results={self.total_results})>"
