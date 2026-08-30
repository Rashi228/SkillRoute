from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from auth import get_current_user_optional
from database import get_db
from services.orchestration.langgraph_recommender import UnifiedRecommendationGraph

router = APIRouter(prefix="/api/recommend", tags=["unified-recommendations"])


class UnifiedRecommendationRequest(BaseModel):
    query: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None


@router.post("/ask")
async def ask_unified_recommender(
    request: UnifiedRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
):
    try:
        graph = UnifiedRecommendationGraph(db=db, current_user=current_user)
        return await graph.run(query=request.query, context=request.context)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unified recommendation failed: {exc}")
