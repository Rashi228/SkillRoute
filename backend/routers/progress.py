from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
import models
from auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["Progress"])

def update_skill_progress(db: Session, user_id: int, skill_id: int, status: str):
    progress = db.query(models.UserSkillProgress).filter(
        models.UserSkillProgress.user_id == user_id,
        models.UserSkillProgress.skill_id == skill_id
    ).first()
    
    if not progress:
        progress = models.UserSkillProgress(
            user_id=user_id,
            skill_id=skill_id,
            status=status,
            completed_at=datetime.utcnow() if status == "COMPLETED" else None
        )
        db.add(progress)
    else:
        progress.status = status
        progress.completed_at = datetime.utcnow() if status == "COMPLETED" else None
        
    db.commit()
    db.refresh(progress)
    return progress

def get_user_completed_skill_ids(db: Session, user_id: int):
    completed = db.query(models.UserSkillProgress).filter(
        models.UserSkillProgress.user_id == user_id,
        models.UserSkillProgress.status == "COMPLETED"
    ).all()
    return [c.skill_id for c in completed]

@router.post("/{skill_id}/complete")
def mark_skill_complete(skill_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    update_skill_progress(db, current_user.id, skill_id, "COMPLETED")
    return {"status": "SUCCESS", "message": "Skill marked as complete"}

@router.post("/{skill_id}/incomplete")
def mark_skill_incomplete(skill_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    update_skill_progress(db, current_user.id, skill_id, "INCOMPLETE")
    return {"status": "SUCCESS", "message": "Skill marked as incomplete"}

@router.get("")
def get_progress(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    skill_ids = get_user_completed_skill_ids(db, current_user.id)
    return {"completed_skill_ids": skill_ids}
