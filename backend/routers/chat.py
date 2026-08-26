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
