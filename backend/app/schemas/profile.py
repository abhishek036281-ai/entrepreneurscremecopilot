from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class EntrepreneurProfileCreate(BaseModel):
    full_name: str
    age: int
    gender: str
    state: str
    district: str
    social_category: str # General, OBC, SC, ST, EWS
    rural_urban: str # Rural, Urban
    disability_status: bool = False
    entrepreneur_type: str = "New" # New, Existing
    business_stage: str = "Idea" # Idea, Early, Growth

class EntrepreneurProfileResponse(EntrepreneurProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BusinessProfileCreate(BaseModel):
    business_name: str
    raw_description: Optional[str] = None
    industry: str
    business_type: str
    business_stage: str = "Idea"
    is_new_business: bool = True
    estimated_investment: float = 0.0
    funding_required: float = 0.0
    purpose_of_funding: Optional[str] = None
    machinery_cost: float = 0.0
    working_capital_cost: float = 0.0
    employee_count: int = 1
    expected_turnover: float = 0.0
    business_location_state: str
    business_location_district: str
    is_rural: bool = True
    support_needed: List[str] = []
    support_notes: Optional[str] = None

class BusinessProfileResponse(BusinessProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AIAnalyzeRequest(BaseModel):
    text: str

class AIAnalyzeResponse(BaseModel):
    extracted_industry: str
    extracted_business_type: str
    extracted_funding_needed: float
    extracted_purpose: str
    suggested_tags: List[str]
    ai_summary: str
    confidence_note: str
