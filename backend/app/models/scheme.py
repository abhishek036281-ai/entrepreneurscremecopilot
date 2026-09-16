from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    ministry = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False) # Financial Support, Subsidy, Loan, Skill Development, Infrastructure
    
    # Targeting Criteria
    target_beneficiaries = Column(JSON, default=list) # ["SC", "ST", "Women", "OBC", "General", "Disabled"]
    states = Column(JSON, default=list) # ["All"] or ["Uttar Pradesh", "Bihar"]
    business_types = Column(JSON, default=list) # ["Manufacturing", "Service", "Trading", "Agri"]
    industries = Column(JSON, default=list) # ["Food Processing", "Textiles", "IT", "Agriculture", "All"]
    business_stages = Column(JSON, default=list) # ["Idea", "Early", "Growth"]
    
    # Demographics Rules
    minimum_age = Column(Integer, default=18)
    maximum_age = Column(Integer, default=65)
    gender_requirements = Column(String, default="All") # All, Women Only, Male Only
    social_category_requirements = Column(JSON, default=list) # ["SC", "ST", "OBC", "General", "All"]
    rural_urban_requirements = Column(String, default="All") # All, Rural, Urban
    
    # Financial Limits
    funding_min = Column(Float, default=0.0)
    funding_max = Column(Float, default=0.0) # 0 means no limit or variable
    support_types = Column(JSON, default=list) # ["Credit Guarantee", "Capital Subsidy", "Interest Subsidy", "Grant"]
    benefits = Column(Text, nullable=False)
    
    # Requirements & Process
    eligibility_rules = Column(JSON, default=dict) # Structured conditions for matching engine
    required_documents = Column(JSON, default=list) # List of doc names
    application_process = Column(JSON, default=list) # List of step dicts or strings
    official_url = Column(String, nullable=False)
    
    status = Column(String, default="Active") # Draft, Active, Inactive, Needs Verification
    last_verified = Column(String, nullable=True) # e.g. "2026-03-01"
    verification_status = Column(String, default="Verified") # Verified, Information requires verification
    verification_notes = Column(Text, nullable=True)
    source_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SavedScheme(Base):
    __tablename__ = "saved_schemes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="saved_schemes")
    scheme = relationship("Scheme")

class ApplicationProgress(Base):
    __tablename__ = "application_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    current_step = Column(Integer, default=0)
    completed_steps = Column(JSON, default=list) # List of step indices completed
    status = Column(String, default="In Progress") # Not Started, In Progress, Submitted
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User")
    scheme = relationship("Scheme")
