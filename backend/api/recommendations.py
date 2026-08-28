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
    for p in valid_practice:
        # Curated practice platforms have high baseline relevance (80%) + difficulty match (20%)
        diff_match = 1.0 if p.get("difficulty", "").upper() == req.learner_level.upper() else 0.8
        p["match_percentage"] = int((0.8 * 100) + (0.2 * diff_match * 100))
    
    # 2. Documentation / Reading
    raw_docs = get_documentation(skill_name)
    valid_docs = await filter_valid_resources(raw_docs)
    for d in valid_docs:
        diff_match = 1.0 if d.get("difficulty", "").upper() == req.learner_level.upper() else 0.8
        d["match_percentage"] = int((0.85 * 100) + (0.15 * diff_match * 100))
    
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
        # Priority: Skill relevance (50%) > user/profile fit (20%) > budget compatibility (10%) > verification (10%) > quality (10%)
        rs = db.query(models.ResourceSkill).filter_by(resource_id=c.id, skill_id=skill.id).first()
        skill_relevance = rs.confidence if rs and rs.confidence else 0.8
        
        difficulty_score = 1.0 if c.difficulty and c.difficulty.upper() == req.learner_level.upper() else 0.8
        budget_score = 1.0 # filtered in DB
        verification_score = 1.0 # filtered in DB
        quality_score = min(c.quality_score or 0.8, 1.0)
        
        final_score = (skill_relevance * 0.5) + (difficulty_score * 0.2) + (budget_score * 0.1) + (verification_score * 0.1) + (quality_score * 0.1)
        match_percentage = int(min(max(final_score * 100, 0), 100))
        
        courses.append({
            "title": c.title,
            "provider": c.provider,
            "difficulty": c.difficulty,
            "rating": c.rating,
            "review_count": c.review_count,
            "duration_hours": c.duration_hours,
            "cost_type": c.cost_type.value if hasattr(c.cost_type, "value") else str(c.cost_type),
            "price": c.price_amount,
            "currency": c.currency,
            "url": c.final_url or c.url,
            "match_percentage": match_percentage
        })
    
    return {
        "status": "SUCCESS",
        "skill_name": skill_name,
        "practice": valid_practice,
        "read": valid_docs,
        "project": project,
        "courses": courses
    }
