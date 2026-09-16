from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.profile import EntrepreneurProfile, BusinessProfile
from app.schemas.profile import (
    EntrepreneurProfileCreate, EntrepreneurProfileResponse,
    BusinessProfileCreate, BusinessProfileResponse,
    AIAnalyzeRequest, AIAnalyzeResponse
)
from app.utils.auth import get_current_user
from app.ai.service import analyze_business_description

router = APIRouter(prefix="/api", tags=["Profile & Business"])

# Entrepreneur Profile
@router.get("/profile", response_model=EntrepreneurProfileResponse)
def get_entrepreneur_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(EntrepreneurProfile).filter(EntrepreneurProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Entrepreneur profile not found. Please complete profile.")
    return profile

@router.put("/profile", response_model=EntrepreneurProfileResponse)
def upsert_entrepreneur_profile(
    profile_data: EntrepreneurProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(EntrepreneurProfile).filter(EntrepreneurProfile.user_id == current_user.id).first()
    if profile:
        for key, value in profile_data.model_dump().items():
            setattr(profile, key, value)
    else:
        profile = EntrepreneurProfile(user_id=current_user.id, **profile_data.model_dump())
        db.add(profile)
    
    # Also sync full_name on User model if provided
    if profile_data.full_name:
        current_user.full_name = profile_data.full_name
        db.add(current_user)

    db.commit()
    db.refresh(profile)
    return profile

# Business Profile
@router.get("/business", response_model=BusinessProfileResponse)
def get_business_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found. Please add business requirements.")
    return profile

@router.put("/business", response_model=BusinessProfileResponse)
def upsert_business_profile(
    business_data: BusinessProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if profile:
        for key, value in business_data.model_dump().items():
            setattr(profile, key, value)
    else:
        profile = BusinessProfile(user_id=current_user.id, **business_data.model_dump())
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile

# AI Natural Language Business Analysis
@router.post("/analyze-business", response_model=AIAnalyzeResponse)
def analyze_business(req: AIAnalyzeRequest):
    if not req.text or len(req.text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please enter a detailed description of your business idea.")
    
    result = analyze_business_description(req.text)
    return result
