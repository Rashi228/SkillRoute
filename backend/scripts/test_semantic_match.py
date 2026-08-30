import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from routers.path import resolve_target_skill
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from services.skill_mapping.semantic_matcher import SemanticMatcher
from models import Skill
import json

def test_semantic_match():
    db = SessionLocal()
    store = SkillEmbeddingStore(db)
    matcher = SemanticMatcher(store)
    
    queries = [
        "Backend Developer",
        "AI Engineer",
        "Machine Learning Engineer",
        "Data Scientist",
        "Data Engineer",
        "Frontend Developer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Cybersecurity Engineer",
        "Generative AI Engineer",
        "RAG Engineer",
        "Full Stack Developer"
    ]
    
    print("\n--- PHASE C.1: SEMANTIC MATCH VERIFICATION ---", flush=True)
    
    # We will simulate the exact logic from resolve_target_skill to see the fallback trace
    for target_name in queries:
        resolution_type = "None"
        target_skill = None
        score = None
        
        # 1. Exact Match
        s = db.query(Skill).filter(Skill.name.ilike(target_name)).first()
        if s:
            target_skill = s
            resolution_type = "Exact"
        else:
            # 2. Alias Match
            all_skills = db.query(Skill).all()
            for s in all_skills:
                if s.aliases:
                    try:
                        aliases_list = json.loads(s.aliases)
                        if any(target_name.lower() == a.lower() for a in aliases_list):
                            target_skill = s
                            resolution_type = "Alias"
                            break
                    except Exception:
                        pass
        
        # 3. Semantic Match
        if not target_skill:
            try:
                # We need to get the score, so let's call matcher.match directly
                # matcher.find_best_match returns a Skill object but no score
                # Let's peek into SemanticMatcher's internals
                query_emb = matcher.model.encode([target_name])[0]
                import torch
                from sentence_transformers import util
                query_tensor = torch.tensor(query_emb).float()
                similarities = util.cos_sim(query_tensor, matcher.skill_tensor)[0]
                best_idx = torch.argmax(similarities).item()
                best_score = similarities[best_idx].item()
                
                if best_score >= matcher.threshold:
                    skill_id = matcher.skill_ids[best_idx]
                    target_skill = db.query(Skill).filter(Skill.id == skill_id).first()
                    resolution_type = "Semantic"
                    score = best_score
            except Exception as e:
                print(f"Error during semantic matching for {target_name}: {e}", flush=True)
                
        if target_skill:
            score_str = f"{score:.4f}" if score is not None else "N/A"
            print(f"Query: {target_name:<25} -> Match: {target_skill.name:<25} (ID: {target_skill.id}) | Type: {resolution_type:<8} | Score: {score_str}", flush=True)
        else:
            print(f"Query: {target_name:<25} -> NO MATCH FOUND (Groq Fallback Required)", flush=True)

if __name__ == "__main__":
    test_semantic_match()
