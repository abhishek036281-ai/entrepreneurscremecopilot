from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class SchemeBase(BaseModel):
    name: str
    description: str
    ministry: str
    category: str
    target_beneficiaries: list[str] = []
    states: list[str] = ["All"]
    business_types: list[str] = []
    industries: list[str] = []
    business_stages: list[str] = []
    minimum_age: int = 18
    maximum_age: int = 65
    gender_requirements: str = "All"
    social_category_requirements: list[str] = ["All"]
    rural_urban_requirements: str = "All"
    funding_min: float = 0.0
    funding_max: float = 0.0
    support_types: list[str] = []
    benefits: str
    eligibility_rules: dict[str, Any] = {}
    required_documents: list[str] = []
    application_process: list[Any] = []
    official_url: str
    status: str = "Active"
    last_verified: Optional[str] = None

class SchemeCreate(SchemeBase):
    pass

class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ministry: Optional[str] = None
    category: Optional[str] = None
    target_beneficiaries: Optional[list[str]] = None
    states: Optional[list[str]] = None
    business_types: Optional[list[str]] = None
    industries: Optional[list[str]] = None
    business_stages: Optional[list[str]] = None
    minimum_age: Optional[int] = None
    maximum_age: Optional[int] = None
    gender_requirements: Optional[str] = None
    social_category_requirements: Optional[list[str]] = None
    rural_urban_requirements: Optional[str] = None
    funding_min: Optional[float] = None
    funding_max: Optional[float] = None
    support_types: Optional[list[str]] = None
    benefits: Optional[str] = None
    eligibility_rules: Optional[dict[str, Any]] = None
    required_documents: Optional[list[str]] = None
    application_process: Optional[list[Any]] = None
    official_url: Optional[str] = None
    status: Optional[str] = None
    last_verified: Optional[str] = None

class SchemeResponse(SchemeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MatchScoreBreakdown(BaseModel):
    overall_score: float
    eligibility_score: float # 30% weight
    relevance_score: float   # 30% weight
    funding_score: float     # 20% weight
    location_score: float    # 10% weight
    need_score: float        # 10% weight
    is_eligible: bool
    reasons: list[str]
    missing_requirements: list[str]
    required_documents: list[str]
    next_steps: list[str]

class SchemeRecommendationResponse(BaseModel):
    scheme: SchemeResponse
    match_breakdown: MatchScoreBreakdown

class SavedSchemeResponse(BaseModel):
    id: int
    user_id: int
    scheme_id: int
    saved_at: datetime
    scheme: SchemeResponse

    class Config:
        from_attributes = True

class ApplicationRoadmapStep(BaseModel):
    step_number: int
    title: str
    description: str
    completed: bool = False

class ApplicationRoadmapResponse(BaseModel):
    scheme_id: int
    scheme_name: str
    official_url: str
    required_documents: list[str]
    roadmap_steps: list[ApplicationRoadmapStep]
    completed_step_count: int
    total_step_count: int
