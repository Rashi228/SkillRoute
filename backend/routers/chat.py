from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from schemas import ProfilerResponse, LearnerProfile
from agents.profiler import extract_profile_logic

router = APIRouter(prefix="/api/chat", tags=["Chat"])

from typing import List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    
@router.post("/profiler", response_model=ProfilerResponse)
def run_profiler(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = extract_profile_logic(user_message=request.message, chat_history=request.history)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from agents.coach import extract_coach_intent
from routers.progress import update_skill_progress
import models
from auth import get_current_user_optional
from typing import Optional

class CoachRequest(BaseModel):
    message: str
    target_goal: str
    budget: str
    time_commitment: str

@router.post("/coach")
def run_coach(request: CoachRequest, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user_optional)):
    try:
        intent_data = extract_coach_intent(request.message)
        intent = intent_data.get("intent")
        params = intent_data.get("parameters", {})
        reply = intent_data.get("reply", "Understood.")
        
        # We need to perform the action and possibly trigger regeneration on the frontend
        action_performed = False
        requires_regeneration = False
        
        if intent == "MARK_SKILL_COMPLETED":
            skill_name = params.get("skill_name")
            if skill_name:
                skill = db.query(models.Skill).filter(models.Skill.name.ilike(skill_name)).first()
                if skill and current_user:
                    update_skill_progress(db, current_user.id, skill.id, "COMPLETED")
                action_performed = True
                requires_regeneration = True
                    
        elif intent == "MARK_SKILL_INCOMPLETE":
            skill_name = params.get("skill_name")
            if skill_name:
                skill = db.query(models.Skill).filter(models.Skill.name.ilike(skill_name)).first()
                if skill and current_user:
                    update_skill_progress(db, current_user.id, skill.id, "INCOMPLETE")
                action_performed = True
                requires_regeneration = True
                    
        elif intent == "UPDATE_BUDGET":
            budget = params.get("budget", "FREE").upper()
            if current_user:
                profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
                if profile:
                    profile.budget = budget
                    db.commit()
            action_performed = True
            requires_regeneration = True
                
        elif intent == "UPDATE_TIME":
            time_comm = params.get("time_commitment")
            if current_user and time_comm:
                profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
                if profile:
                    profile.time_commitment = time_comm
                    db.commit()
            action_performed = True
            requires_regeneration = True
                
        elif intent in ["REQUEST_DEEP_ROUTE", "REQUEST_FAST_ROUTE", "REPLAN_PATH"]:
            requires_regeneration = True

        return {
            "intent": intent,
            "action_performed": action_performed,
            "requires_regeneration": requires_regeneration,
            "reply": reply,
            "parameters": params
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from agents.router_graph import router_graph

@router.post("/route")
def run_router(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        state = {"message": request.message, "history": request.history, "db": db,
                  "intent": None, "subject": None, "result": None}
        final_state = router_graph.invoke(state)
        return final_state["result"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
