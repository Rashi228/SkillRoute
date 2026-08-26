from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
import models
from agents.discovery import generate_search_queries
from services.youtube import search_youtube

router = APIRouter(prefix="/api/path", tags=["Learning Path"])

class PathGenerationRequest(BaseModel):
    user_id: int
    target_skill_name: str
    preferred_cost_type: Optional[str] = None
    max_duration_hours: Optional[float] = None

class PathNodeResponse(BaseModel):
    skill_name: str
    resource_title: str
    resource_type: str
    url: str
    duration_hours: float
    cost_type: str

class LearningPathResponse(BaseModel):
    route_name: str
    total_duration: float
    nodes: List[PathNodeResponse]

@router.post("/generate", response_model=List[LearningPathResponse])
def generate_path(request: PathGenerationRequest, db: Session = Depends(get_db)):
    # 1. Check if user profile exists
    profile = db.query(models.Profile).filter(models.Profile.user_id == request.user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete the AI profiler first.")

    # 2. Find Target Skill
    target_skill = db.query(models.Skill).filter(models.Skill.name.ilike(request.target_skill_name)).first()
    if not target_skill:
        raise HTTPException(status_code=404, detail=f"Target skill '{request.target_skill_name}' not found in the Skill Graph.")

    # 3. Recursive CTE to find all prerequisite skills for the target skill
    query = text("""
        WITH RECURSIVE SkillTree AS (
            -- Base case: the target skill itself
            SELECT id, name, 0 AS depth
            FROM skills
            WHERE id = :target_id
            
            UNION ALL
            
            -- Recursive case: find prerequisites
            SELECT s.id, s.name, st.depth + 1
            FROM skills s
            JOIN skill_prerequisites sp ON s.id = sp.prerequisite_id
            JOIN SkillTree st ON sp.skill_id = st.id
        )
        SELECT id, name, depth FROM SkillTree
        ORDER BY depth DESC;
    """)
    
    result = db.execute(query, {"target_id": target_skill.id}).fetchall()
    
    # Required skills sorted from most basic prerequisite to target
    required_skills = []
    seen = set()
    for row in result:
        if row.id not in seen:
            required_skills.append({"id": row.id, "name": row.name})
            seen.add(row.id)
            
    # 4. Check user's current passports
    user_skills = {ls.skill_id: ls.confidence_score for ls in profile.passports if ls.confidence_score > 70}
    
    # 5. Identify skill gaps
    missing_skills = [s for s in required_skills if s["id"] not in user_skills]
    
    if not missing_skills:
        return [] # User already has all skills!

    # 6. Generate Alternate Routes (Simulated based on missing skills)
    # Fast Route: Pick resources with shortest duration
    # Deep Route: Pick resources with Advanced difficulty if available
    
    routes = []
    
    def build_route(route_name, sort_order):
        nodes = []
        total_duration = 0
        for ms in missing_skills:
            # Query resources for this missing skill that match constraints
            res_query = db.query(models.Resource).join(models.ResourceSkill).filter(
                models.ResourceSkill.skill_id == ms["id"],
                models.Resource.is_active == True
            )
            
            if request.preferred_cost_type and request.preferred_cost_type != "PAID":
                res_query = res_query.filter(models.Resource.cost_type.in_(["FREE", "FREE_AUDIT"]))
                
            available_resources = res_query.all()
            
            # TRIGGER VERIFIED DISCOVERY if fewer than 2 suitable resources
            if len(available_resources) < 2:
                # 1. LLM generates queries
                constraints = f"Cost: {request.preferred_cost_type or 'Any'}, Max Duration: {request.max_duration_hours or 'Any'} hours"
                search_queries = generate_search_queries(ms["name"], constraints)
                
                # 2. Hit YouTube API for verified URLs
                discovered_videos = []
                for q in search_queries:
                    vids = search_youtube(q, max_results=2)
                    discovered_videos.extend(vids)
                
                # Deduplicate based on video_id
                seen_vids = set()
                unique_vids = []
                for v in discovered_videos:
                    if v["video_id"] not in seen_vids:
                        seen_vids.add(v["video_id"])
                        unique_vids.append(v)
                
                # 3. Cache validated resources in DB
                for v in unique_vids:
                    # Check if exists (by url which is unique)
                    existing = db.query(models.Resource).filter(models.Resource.url == v["url"]).first()
                    if not existing:
                        new_res = models.Resource(
                            title=v["title"],
                            resource_type="Video",
                            url=v["url"],
                            difficulty="Beginner", # AI-inferred in future, default for now
                            duration_hours=v["duration_hours"],
                            cost_type="FREE", # YouTube is free
                            quality_score=v["quality_score"],
                            video_id=v["video_id"],
                            channel_id=v["channel_id"],
                            duration_seconds=v["duration_seconds"],
                            view_count=v["view_count"],
                            source="YouTube API"
                        )
                        db.add(new_res)
                        db.commit()
                        db.refresh(new_res)
                        db.add(models.ResourceSkill(resource_id=new_res.id, skill_id=ms["id"]))
                        db.commit()
                
                # Re-query resources after caching
                available_resources = res_query.all()

            if sort_order == "Fast":
                best_resource = min(available_resources, key=lambda r: r.duration_hours, default=None) if available_resources else None
            else:
                best_resource = max(available_resources, key=lambda r: r.duration_hours, default=None) if available_resources else None
                
            if best_resource:
                nodes.append(PathNodeResponse(
                    skill_name=ms["name"],
                    resource_title=best_resource.title,
                    resource_type=best_resource.resource_type,
                    url=best_resource.url,
                    duration_hours=best_resource.duration_hours,
                    cost_type=best_resource.cost_type.value
                ))
                total_duration += best_resource.duration_hours
                
        return LearningPathResponse(route_name=route_name, total_duration=total_duration, nodes=nodes)

    fast_route = build_route("Fast & Practical Route", "Fast")
    deep_route = build_route("Deep Theory Route", "Deep")
    
    if fast_route.nodes:
        routes.append(fast_route)
    if deep_route.nodes:
        routes.append(deep_route)
        
    return routes
