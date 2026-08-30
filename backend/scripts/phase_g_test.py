import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill
from services.skill_mapping.semantic_matcher import SemanticMatcher
from services.skill_mapping.embedding_store import SkillEmbeddingStore

def test_goals():
    db = SessionLocal()
    store = SkillEmbeddingStore(db)
    matcher = SemanticMatcher(store)
    skills = db.query(Skill).all()
    
    queries = [
        "Backend Developer",
        "Backend Engineer",
        "Frontend Developer",
        "Frontend Engineer",
        "Full Stack Developer",
        "Full Stack Engineer",
        "AI Engineer",
        "Machine Learning Engineer",
        "ML Engineer",
        "Data Scientist",
        "Data Engineer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Cybersecurity Engineer",
        "Generative AI Engineer",
        "LLM Engineer",
        "RAG Engineer",
        "RAG Developer"
    ]
    
    print(f"{'Query':<25} -> {'Matched Skill':<30} | {'Method':<10} | {'Score':<10}")
    print("-" * 80)
    
    for q in queries:
        matched_skill = None
        method = ""
        score = None
        
        # 1. Exact Match
        skill = db.query(Skill).filter(Skill.name.ilike(q)).first()
        if skill:
            matched_skill = skill.name
            method = "Exact"
        else:
            # 2. Alias Match
            for s in skills:
                if s.aliases:
                    try:
                        aliases = json.loads(s.aliases)
                        if any(q.lower() in a.lower() for a in aliases):
                            matched_skill = s.name
                            method = "Alias"
                            break
                    except:
                        pass
                        
            # 3. Semantic Match
            if not matched_skill:
                try:
                    emb = matcher.embed_texts([q])
                    candidates = matcher.match_batch(emb)[0]
                    if candidates and candidates[0]["score"] >= 0.5:
                        matched_skill = candidates[0]["skill"].name
                        method = "Semantic"
                        score = candidates[0]["score"]
                except:
                    pass
                    
        score_str = f"{score:.4f}" if score is not None else "N/A"
        print(f"{q:<25} -> {str(matched_skill):<30} | {method:<10} | {score_str:<10}")

    db.close()

if __name__ == "__main__":
    test_goals()
