from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.scheme import Scheme
from app.schemas.scheme import SchemeCreate, SchemeUpdate, SchemeResponse
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])

@router.get("/schemes", response_model=List[SchemeResponse])
def admin_get_all_schemes(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return db.query(Scheme).all()

@router.post("/schemes", response_model=SchemeResponse)
def admin_create_scheme(
    scheme_data: SchemeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    new_scheme = Scheme(**scheme_data.model_dump())
    db.add(new_scheme)
    db.commit()
    db.refresh(new_scheme)
    return new_scheme

@router.put("/schemes/{id}", response_model=SchemeResponse)
def admin_update_scheme(
    id: int,
    scheme_data: SchemeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    scheme = db.query(Scheme).filter(Scheme.id == id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    update_dict = scheme_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(scheme, key, value)
    
    db.commit()
    db.refresh(scheme)
    return scheme

@router.delete("/schemes/{id}")
def admin_delete_scheme(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    scheme = db.query(Scheme).filter(Scheme.id == id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    
    db.delete(scheme)
    db.commit()
    return {"message": "Scheme deleted successfully"}
