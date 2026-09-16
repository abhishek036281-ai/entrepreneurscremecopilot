from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.profile import EntrepreneurProfile, BusinessProfile
from app.models.scheme import Scheme, SavedScheme, ApplicationProgress
from app.schemas.scheme import (
    SchemeResponse, SchemeRecommendationResponse,
    SavedSchemeResponse, ApplicationRoadmapResponse, ApplicationRoadmapStep
)
from app.utils.auth import get_current_user
from app.matching.engine import evaluate_scheme_match
from app.ai.service import analyze_business_description

router = APIRouter(prefix="/api", tags=["Schemes & Recommendations"])

class AIExplainRequest(BaseModel):
    scheme_id: int

class AIExplainResponse(BaseModel):
    scheme_name: str
    explanation: str
    key_highlights: List[str]
    disclaimer: str

@router.get("/schemes", response_model=List[SchemeResponse])
def get_all_schemes(db: Session = Depends(get_db)):
    return db.query(Scheme).filter(Scheme.status == "Active").all()

@router.get("/schemes/{id}", response_model=SchemeResponse)
def get_scheme_by_id(id: int, db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.post("/recommendations", response_model=List[SchemeRecommendationResponse])
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entrepreneur = db.query(EntrepreneurProfile).filter(EntrepreneurProfile.user_id == current_user.id).first()
    business = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    
    if not entrepreneur:
        raise HTTPException(status_code=400, detail="Please complete your Entrepreneur Profile first.")
    if not business:
        raise HTTPException(status_code=400, detail="Please complete your Business Profile & Requirements first.")
    
    active_schemes = db.query(Scheme).filter(Scheme.status == "Active").all()
    results = []

    for scheme in active_schemes:
        match_data = evaluate_scheme_match(entrepreneur, business, scheme)
        results.append({
            "scheme": scheme,
            "match_breakdown": match_data
        })
    
    # Sort descending by overall match score
    results.sort(key=lambda x: x["match_breakdown"]["overall_score"], reverse=True)
    return results

@router.post("/explain-match", response_model=AIExplainResponse)
def explain_match(
    req: AIExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scheme = db.query(Scheme).filter(Scheme.id == req.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    entrepreneur = db.query(EntrepreneurProfile).filter(EntrepreneurProfile.user_id == current_user.id).first()
    business = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()

    if not entrepreneur or not business:
        raise HTTPException(status_code=400, detail="Profile and business data required for AI explanation.")

    match_data = evaluate_scheme_match(entrepreneur, business, scheme)
    score = match_data["overall_score"]

    highlights = match_data["reasons"]
    missing = match_data["missing_requirements"]

    if match_data["is_eligible"]:
        explanation = (
            f"Based on your profile, {scheme.name} is a strong match ({score}% match score). "
            f"As a {entrepreneur.social_category} {entrepreneur.gender} entrepreneur in {entrepreneur.state} running a {business.industry} unit, "
            f"your funding requirement of ₹{business.funding_required:,.0f} falls within the scheme's provisions. "
            f"Primary benefits include: {scheme.benefits}"
        )
    else:
        explanation = (
            f"This scheme is currently listed with a low match score ({score}%) due to specific eligibility boundaries. "
            f"Main attention items: {', '.join(missing)}. Please verify latest guidelines on the official portal."
        )

    return AIExplainResponse(
        scheme_name=scheme.name,
        explanation=explanation,
        key_highlights=highlights,
        disclaimer="AI explanation generated strictly from database rules and your verified profile data. Verify official portal before applying."
    )

@router.post("/schemes/{id}/save")
def save_scheme(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    existing = db.query(SavedScheme).filter(
        SavedScheme.user_id == current_user.id,
        SavedScheme.scheme_id == id
    ).first()
    
    if existing:
        return {"message": "Scheme already saved", "saved": True}
    
    new_saved = SavedScheme(user_id=current_user.id, scheme_id=id)
    db.add(new_saved)
    db.commit()
    return {"message": "Scheme saved successfully", "saved": True}

@router.delete("/schemes/{id}/save")
def remove_saved_scheme(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = db.query(SavedScheme).filter(
        SavedScheme.user_id == current_user.id,
        SavedScheme.scheme_id == id
    ).first()
    
    if saved:
        db.delete(saved)
        db.commit()
    return {"message": "Scheme removed from saved", "saved": False}

@router.get("/saved-schemes", response_model=List[SavedSchemeResponse])
def get_saved_schemes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(SavedScheme).filter(SavedScheme.user_id == current_user.id).all()

@router.get("/roadmap/{scheme_id}", response_model=ApplicationRoadmapResponse)
def get_roadmap(scheme_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    progress = db.query(ApplicationProgress).filter(
        ApplicationProgress.user_id == current_user.id,
        ApplicationProgress.scheme_id == scheme_id
    ).first()

    completed_indices = progress.completed_steps if progress and progress.completed_steps else [0, 1]

    # Generate 6-step Roadmap Steps dynamically from Scheme data
    process_list = scheme.application_process or []
    process_str = ", ".join(process_list) if process_list else ""
    
    docs_list = scheme.required_documents or []
    docs_str = ", ".join(docs_list) if docs_list else ""

    default_msg = "Information not available — verify on the official scheme source."

    steps_data = [
        {
            "title": "Step 1: Eligibility & Readiness",
            "desc": f"Ensure you meet the criteria for {scheme.name}. Minimum age: {scheme.minimum_age or 'N/A'}. Target: {', '.join(scheme.target_beneficiaries or ['All'])}."
        },
        {
            "title": "Step 2: Required Documents",
            "desc": f"Gather mandatory documents: {docs_str}" if docs_str else default_msg
        },
        {
            "title": "Step 3: Preparation",
            "desc": "Prepare business plan and project report as required by the scheme guidelines." if docs_str else default_msg
        },
        {
            "title": "Step 4: Application Process",
            "desc": f"Follow official procedures: {process_str}" if process_str else default_msg
        },
        {
            "title": "Step 5: Submission",
            "desc": f"Apply online at official portal: {scheme.official_url}" if scheme.official_url else default_msg
        },
        {
            "title": "Step 6: Follow-up & Verification",
            "desc": "Track application status and participate in field verification if required by the department."
        }
    ]

    steps = []
    for idx, item in enumerate(steps_data):
        steps.append(ApplicationRoadmapStep(
            step_number=idx + 1,
            title=item["title"],
            description=item["desc"],
            completed=(idx in completed_indices)
        ))

    return ApplicationRoadmapResponse(
        scheme_id=scheme.id,
        scheme_name=scheme.name,
        official_url=scheme.official_url,
        required_documents=scheme.required_documents or [],
        roadmap_steps=steps,
        completed_step_count=len(completed_indices),
        total_step_count=len(steps)
    )

@router.post("/roadmap/{scheme_id}/toggle-step")
def toggle_roadmap_step(
    scheme_id: int,
    step_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    progress = db.query(ApplicationProgress).filter(
        ApplicationProgress.user_id == current_user.id,
        ApplicationProgress.scheme_id == scheme_id
    ).first()

    if not progress:
        progress = ApplicationProgress(
            user_id=current_user.id,
            scheme_id=scheme_id,
            completed_steps=[0, 1]
        )
        db.add(progress)

    current_completed = list(progress.completed_steps or [0, 1])
    if step_index in current_completed:
        current_completed.remove(step_index)
    else:
        current_completed.append(step_index)

    progress.completed_steps = current_completed
    db.commit()
    return {"message": "Step updated", "completed_steps": current_completed}
