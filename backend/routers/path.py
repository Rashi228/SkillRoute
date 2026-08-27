from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database import get_db
import models

router = APIRouter(prefix="/api/path", tags=["Learning Path"])

class PathGenerationRequest(BaseModel):
    user_id: Optional[int] = None
    target_skill_name: str
    preferred_cost_type: Optional[str] = None
    max_duration_hours: Optional[float] = None
    # Support temporary chat context profile if no user_id
    current_skills: Optional[List[str]] = []
    learner_level: Optional[str] = "BEGINNER"

class PathResponse(BaseModel):
    target: Dict[str, Any]
    routes: Dict[str, Any]
    skills: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@router.post("/generate", response_model=PathResponse)
def generate_path(request: PathGenerationRequest, db: Session = Depends(get_db)):
    # 1. Target Skill
    target_skill = db.query(models.Skill).filter(models.Skill.name.ilike(request.target_skill_name)).first()
    if not target_skill:
        # Fallback to a default if not found to prevent breaking demo
        target_skill = db.query(models.Skill).filter(models.Skill.name == "Generative AI").first()
        if not target_skill:
            raise HTTPException(status_code=404, detail=f"Target skill not found.")

    # 2. Get User Profile or Context
    user_skills_dict = {}
    if request.user_id:
        profile = db.query(models.Profile).filter(models.Profile.user_id == request.user_id).first()
        if profile:
            user_skills_dict = {ls.skill_id: ls.confidence_score for ls in profile.passports if ls.confidence_score > 70}
    else:
        # Use temporary context
        if request.current_skills:
            for s_name in request.current_skills:
                s = db.query(models.Skill).filter(models.Skill.name.ilike(s_name)).first()
                if s:
                    user_skills_dict[s.id] = 100.0

    # 3. Build the DAG (Recursive Prerequisite Tree)
    # Using a recursive CTE to get all prerequisites and relationships
    query = text("""
        WITH RECURSIVE SkillTree AS (
            -- Base case: the target skill itself
            SELECT id, name, CAST(NULL AS INTEGER) as parent_id, 0 AS depth
            FROM skills
            WHERE id = :target_id
            
            UNION ALL
            
            -- Recursive case: find prerequisites
            SELECT s.id, s.name, st.id as parent_id, st.depth + 1
            FROM skills s
            JOIN skill_prerequisites sp ON s.id = sp.prerequisite_id
            JOIN SkillTree st ON sp.skill_id = st.id
        )
        SELECT id, name, parent_id, depth FROM SkillTree
        ORDER BY depth DESC;
    """)
    
    result = db.execute(query, {"target_id": target_skill.id}).fetchall()
    
    # Track unique skills and edges
    skills_map = {}
    edges = []
    
    for row in result:
        sid = row.id
        sname = row.name
        pid = row.parent_id
        depth = row.depth
        
        if sid not in skills_map:
            skills_map[sid] = {
                "id": sid,
                "name": sname,
                "depth": depth,
                "is_target": sid == target_skill.id
            }
        
        # Keep the maximum depth for layout
        if depth > skills_map[sid]["depth"]:
            skills_map[sid]["depth"] = depth
            
        if pid:
            edges.append({"source": f"n{sid}", "target": f"n{pid}", "type": "prerequisite"})

    # 4. Determine Node States
    # COMPLETED: in user_skills_dict
    # NEXT: Not completed, but all prerequisites are completed
    # LOCKED: Not completed, has uncompleted prerequisites
    # CURRENT: The user's current focal point (usually the first 'NEXT')
    
    # Build prerequisite map (skill -> list of prerequisites)
    prereqs = {sid: [] for sid in skills_map.keys()}
    for edge in edges:
        s_id = int(edge["source"][1:])
        t_id = int(edge["target"][1:])
        prereqs[t_id].append(s_id)
        
    skills_list = []
    nodes = []
    
    current_assigned = False
    
    sorted_skills = sorted(skills_map.values(), key=lambda x: x["depth"], reverse=True)
    
    # Layout positioning - Centered tree
    max_depth = max(s["depth"] for s in sorted_skills) if sorted_skills else 0
    depth_counts = {}
    for s in sorted_skills:
        depth_counts[s["depth"]] = depth_counts.get(s["depth"], 0) + 1
        
    depth_x_map = {d: 400 - (count - 1) * 150 for d, count in depth_counts.items()}
    
    for s in sorted_skills:
        sid = s["id"]
        
        is_completed = sid in user_skills_dict
        
        state = "locked"
        if is_completed:
            state = "completed"
        elif s["is_target"]:
            state = "goal"
        else:
            # Check if all prereqs are completed
            all_prereqs_completed = True
            for p in prereqs[sid]:
                if p not in user_skills_dict:
                    all_prereqs_completed = False
                    break
                    
            if all_prereqs_completed:
                if not current_assigned:
                    state = "current"
                    current_assigned = True
                else:
                    state = "next"
            else:
                state = "locked"
                
        # Layout positioning
        d = s["depth"]
        x = depth_x_map[d]
        depth_x_map[d] += 300  # Spread out nodes at the same depth
        
        y = 150 * (max_depth - d)
        
        # Add Node
        node = {
            "id": f"n{sid}",
            "type": "resource",
            "position": {"x": x, "y": y},
            "data": {
                "status": state,
                "skill_name": s["name"],
                "skill_id": sid,
                "resources": [] # Fetched dynamically via YouTube API later!
            }
        }
        nodes.append(node)
        
        skills_list.append({
            "id": sid,
            "name": s["name"],
            "status": state.upper(),
            "readiness": 1.0 if is_completed else 0.0
        })

    # Format edges for React Flow
    rf_edges = []
    for e in edges:
        source_id = e["source"]
        target_id = e["target"]
        rf_edges.append({
            "id": f"e-{source_id}-{target_id}",
            "source": source_id,
            "target": target_id,
            "label": "Prerequisite",
            "animated": True, # You can make this conditional based on state
            "style": {"stroke": "#0284c7", "strokeWidth": 2}
        })
        
    # Temporary Routes (Mocked for now since discovery is lazy)
    routes = {
        "fast": {"title": "FAST TRACK", "time": "12 hrs", "desc": "Minimum requirements."},
        "balanced": {"title": "BALANCED", "time": "24 hrs", "desc": "Recommended. Mix of theory and practice."},
        "deep": {"title": "DEEP DIVE", "time": "40 hrs", "desc": "Comprehensive. Master every concept."}
    }
    
    return {
        "target": {"name": target_skill.name, "id": target_skill.id},
        "routes": routes,
        "skills": skills_list,
        "nodes": nodes,
        "edges": rf_edges
    }
