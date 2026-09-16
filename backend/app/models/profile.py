from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class EntrepreneurProfile(Base):
    __tablename__ = "entrepreneur_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False) # Male, Female, Other
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    social_category = Column(String, nullable=False) # General, OBC, SC, ST, EWS
    rural_urban = Column(String, nullable=False) # Rural, Urban
    disability_status = Column(Boolean, default=False)
    entrepreneur_type = Column(String, default="New") # New, Existing
    business_stage = Column(String, default="Idea") # Idea, Early, Growth

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="entrepreneur_profile")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    business_name = Column(String, nullable=False)
    raw_description = Column(Text, nullable=True) # Natural language business description
    industry = Column(String, nullable=False) # Food Processing, Agriculture, Textile, IT, Service, Manufacturing, Retail, etc.
    business_type = Column(String, nullable=False) # Manufacturing, Service, Trading, Agri, etc.
    business_stage = Column(String, default="Idea") # Idea, Early, Growth
    is_new_business = Column(Boolean, default=True)
    
    estimated_investment = Column(Float, default=0.0) # Total capital needed
    funding_required = Column(Float, default=0.0) # Loan / Grant sought
    purpose_of_funding = Column(String, nullable=True) # Machinery, Working Capital, Expansion, Marketing
    machinery_cost = Column(Float, default=0.0)
    working_capital_cost = Column(Float, default=0.0)
    
    employee_count = Column(Integer, default=1)
    expected_turnover = Column(Float, default=0.0)
    business_location_state = Column(String, nullable=False)
    business_location_district = Column(String, nullable=False)
    is_rural = Column(Boolean, default=True)

    support_needed = Column(JSON, default=list) # ["Loan", "Subsidy", "Grant", "Machinery / Equipment", ...]
    support_notes = Column(Text, nullable=True) # Free-text specific requirement notes

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="business_profile")
