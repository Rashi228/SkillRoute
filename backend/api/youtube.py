from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio

from database import get_db
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator

router = APIRouter(prefix="/api/resources/youtube", tags=["youtube"])

class DiscoveryRequest(BaseModel):
    skill_id: int = Field(..., description="ID of the target skill")
    learner_level: str = Field("INTERMEDIATE", description="BEGINNER, INTERMEDIATE, or ADVANCED")
    goal: str = Field("General learning", description="Learner's objective")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints like max_hours, language")
    is_struggling: bool = Field(False, description="Whether the user is currently struggling with this skill")

@router.post("/discover")
async def discover_youtube_resources(req: DiscoveryRequest, db: Session = Depends(get_db)):
    """
    Triggers the YouTube discovery pipeline for a given skill.
    """
    orchestrator = YouTubeDiscoveryOrchestrator(db)
    try:
        result = await orchestrator.discover(
            skill_id=req.skill_id,
            learner_level=req.learner_level,
            goal=req.goal,
            constraints=req.constraints,
            is_struggling=req.is_struggling
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Discovery Error: {e}")
        # Always gracefully fail back to cache if possible, but orchestrator handles that.
        # If it throws, it's a fatal error.
        raise HTTPException(status_code=500, detail="Internal discovery failure")
