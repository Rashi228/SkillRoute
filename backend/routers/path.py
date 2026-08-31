from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database import get_db
import models
from auth import get_current_user_optional
from models import PathTransition

router = APIRouter(prefix="/api/path", tags=["Learning Path"])


def log_transition(db: Session, from_skill_id: Optional[int], to_skill_id: int):
    existing = db.query(PathTransition).filter_by(
        from_skill_id=from_skill_id, to_skill_id=to_skill_id
    ).first()
    if existing:
        existing.count += 1
    else:
        db.add(PathTransition(from_skill_id=from_skill_id, to_skill_id=to_skill_id, count=1))
    db.commit()

import json
from services.skill_mapping.semantic_matcher import SemanticMatcher
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from agents.coach import llm

# Cache for resolved targets to prevent redundant LLM calls
resolved_target_cache = {}

def resolve_target_skill(db: Session, target_name: str) -> Optional[models.Skill]:
    if target_name in resolved_target_cache:
        cached_id = resolved_target_cache[target_name]
        skill = db.query(models.Skill).filter(models.Skill.id == cached_id).first()
        if skill: return skill
        
    # 1. Exact Match
    skill = db.query(models.Skill).filter(models.Skill.name.ilike(target_name)).first()
    if skill: return skill
    
    # 2. Alias Match
    skills = db.query(models.Skill).all()
    for s in skills:
        if s.aliases:
            try:
                aliases = json.loads(s.aliases)
                if any(target_name.lower() in a.lower() for a in aliases):
                    return s
            except:
                pass

    # 3. Semantic Match
    try:
        store = SkillEmbeddingStore(db)
        matcher = SemanticMatcher(store)
        emb = matcher.embed_texts([target_name])
        candidates = matcher.match_batch(emb)[0]
        if candidates and candidates[0]["score"] >= 0.5:
            return candidates[0]["skill"]
    except Exception as e:
        pass
        
    # 4. Groq Goal Decomposition (Fallback)
    if llm:
        from langchain_core.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI curriculum designer. The user wants to learn '{goal}'. Map this goal to the most relevant foundational concept from this list of known skills: {skills}. Return ONLY the exact name of the closest skill from the list, nothing else. If nothing matches, return 'Generative AI'."),
            ("user", "{goal}")
        ])
        skill_names = [s.name for s in skills]
        chain = prompt | llm
        res = chain.invoke({"goal": target_name, "skills": ", ".join(skill_names)})
        mapped_name = res.content.strip()
        skill = db.query(models.Skill).filter(models.Skill.name.ilike(mapped_name)).first()
        if skill:
            resolved_target_cache[target_name] = skill.id
            return skill

    return None

class PathGenerationRequest(BaseModel):
    user_id: Optional[int] = None
    target_skill_name: str
    preferred_cost_type: Optional[str] = None
    max_duration_hours: Optional[float] = None
    # Support temporary chat context profile if no user_id
    current_skills: Optional[List[str]] = []
    completed_skill_ids: Optional[List[int]] = []
    learner_level: Optional[str] = "BEGINNER"

class PathResponse(BaseModel):
    target: Dict[str, Any]
    routes: Dict[str, Any]
    skills: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@router.post("/generate", response_model=PathResponse)
def generate_path(request: PathGenerationRequest, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user_optional)):
    # 1. Target Skill (Dynamic Fallback)
    target_skill = resolve_target_skill(db, request.target_skill_name)
    if not target_skill:
        # Final fallback to a default if completely unresolved to prevent breaking demo
        target_skill = db.query(models.Skill).filter(models.Skill.name == "Generative AI").first()
        if not target_skill:
            raise HTTPException(status_code=404, detail=f"Target skill not found.")

    log_transition(db, from_skill_id=None, to_skill_id=target_skill.id)

    # 2. Get User Profile or Context
    user_skills_dict = {}
    if current_user:
        profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
        if profile:
            user_skills_dict = {ls.skill_id: ls.confidence_score for ls in profile.passports if ls.confidence_score > 70}
        
        # Override with any DB progress
        progress_rows = db.query(models.UserSkillProgress).filter(
            models.UserSkillProgress.user_id == current_user.id,
            models.UserSkillProgress.status == "COMPLETED"
        ).all()
        for p in progress_rows:
            user_skills_dict[p.skill_id] = 100.0
    else:
        # Use temporary context
        if request.current_skills:
            for s_name in request.current_skills:
                s = db.query(models.Skill).filter(models.Skill.name.ilike(s_name)).first()
                if s:
                    user_skills_dict[s.id] = 100.0

    # Add explicitly completed skills from frontend
    if request.completed_skill_ids:
        for sid in request.completed_skill_ids:
            user_skills_dict[sid] = 100.0

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
    
    # Track node statuses
    node_states = {}
    
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
    seen_edges = set()
    for e in edges:
        source_id = e["source"]
        target_id = e["target"]
        edge_key = f"{source_id}-{target_id}"
        
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            rf_edges.append({
                "id": f"e-{edge_key}",
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

class ExplainNodeRequest(BaseModel):
    skill_id: int
    target_goal: str

@router.post("/explain_node")
def explain_node(request: ExplainNodeRequest, db: Session = Depends(get_db)):
    # 1. Check ExplanationCache
    cached = db.query(models.ExplanationCache).filter(
        models.ExplanationCache.skill_id == request.skill_id,
        models.ExplanationCache.target_goal == request.target_goal
    ).first()
    
    if cached:
        return {"explanation": cached.explanation_text}
        
    # 2. Fetch Skill + prerequisite relationships
    skill = db.query(models.Skill).filter(models.Skill.id == request.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    target = resolve_target_skill(db, request.target_goal)
    if not target:
        raise HTTPException(status_code=404, detail="Target goal not found")
        
    # If the skill IS the target goal
    if skill.id == target.id:
        return {"explanation": f"Mastering {skill.name} is your ultimate learning destination."}

    # Gather prerequisite facts (what does this skill unlock?)
    unlocks = db.query(models.Skill.name).join(
        models.SkillPrerequisite, models.SkillPrerequisite.skill_id == models.Skill.id
    ).filter(models.SkillPrerequisite.prerequisite_id == skill.id).all()
    
    unlock_names = [u[0] for u in unlocks]
    unlock_fact = f"It is a prerequisite for: {', '.join(unlock_names)}." if unlock_names else "It is a foundational concept."
    
    # 3. Construct strictly grounded prompt
    if not llm:
        return {"explanation": "This skill is part of your learning path toward the selected goal."}
        
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an educational assistant.
Explain in 1-2 concise lines why the user needs to learn {skill_name} to reach their goal of {target_goal}.

Facts you MUST rely on:
- {skill_name} covers: {skill_description}.
- {unlock_fact}

Rules:
1. ONLY use the facts supplied above.
2. DO NOT invent prerequisites.
3. DO NOT invent skills.
4. DO NOT explain internal reasoning.
5. Provide a direct, concise user-facing explanation.""")
    ])
    
    try:
        chain = prompt | llm
        res = chain.invoke({
            "skill_name": skill.name,
            "target_goal": target.name,
            "skill_description": skill.description or "core concepts",
            "unlock_fact": unlock_fact
        })
        explanation = res.content.strip()
    except Exception as e:
        explanation = "This skill is part of your learning path toward the selected goal."
        
    # 4. Store in ExplanationCache
    new_cache = models.ExplanationCache(
        skill_id=request.skill_id,
        target_goal=request.target_goal,
        explanation_text=explanation
    )
    db.add(new_cache)
    db.commit()
    
    return {"explanation": explanation}

