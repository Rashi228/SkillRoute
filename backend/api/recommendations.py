from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from database import get_db
import models
from services.recommendations.catalogue import get_practice_platforms, get_documentation
from services.recommendations.project_generator import ProjectGenerator
from services.recommendations.validator import filter_valid_resources

router = APIRouter(prefix="/api/resources/recommendations", tags=["recommendations"])

class RecommendationRequest(BaseModel):
    skill_id: int
    learner_level: str = "INTERMEDIATE"
    goal: str = "General learning"
    budget: str = "FREE"

@router.post("")
async def get_skill_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == req.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    skill_name = skill.name
    
    # 1. Practice
    raw_practice = get_practice_platforms(skill_name)
    if req.budget.upper() == "FREE":
        raw_practice = [p for p in raw_practice if p.get("cost") in ["FREE", "FREE_AUDIT"]]
    valid_practice = await filter_valid_resources(raw_practice)
    
    # 2. Documentation / Reading
    raw_docs = get_documentation(skill_name)
    valid_docs = await filter_valid_resources(raw_docs)
    
    # 3. Build (Project)
    # Project generation does not include external URLs so no validation needed here
    project_gen = ProjectGenerator()
    project = project_gen.generate_project(skill_name, req.learner_level, req.goal)
    
    # 4. Courses (Coursera / Udemy)
    courses = []
    allowed_providers = ["COURSERA", "UDEMY"]
    allowed_costs = [models.CostType.FREE, models.CostType.FREE_AUDIT]
    if req.budget.upper() == "PAID":
        allowed_costs.extend([models.CostType.PAID, models.CostType.FREEMIUM])
        
    db_courses = db.query(models.Resource).join(
        models.ResourceSkill, models.Resource.id == models.ResourceSkill.resource_id
    ).filter(
        models.ResourceSkill.skill_id == skill.id,
        models.Resource.provider.in_(allowed_providers),
        models.Resource.verification_status == models.VerificationStatus.VERIFIED,
        models.Resource.is_active == True,
        models.Resource.cost_type.in_(allowed_costs)
    ).order_by(
        models.ResourceSkill.confidence.desc(),
        models.Resource.quality_score.desc()
    ).limit(5).all()
    
    for c in db_courses:
        courses.append({
            "title": c.title,
            "provider": c.provider,
            "difficulty": c.difficulty,
            "rating": c.rating,
            "review_count": c.review_count,
            "duration_hours": c.duration_hours,
            "cost_type": c.cost_type.value,
            "price": c.price_amount,
            "currency": c.currency,
            "url": c.final_url or c.url
        })
    
    return {
        "status": "SUCCESS",
        "skill_name": skill_name,
        "practice": valid_practice,
        "read": valid_docs,
        "project": project,
        "courses": courses
    }
