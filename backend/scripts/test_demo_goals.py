import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from routers.path import generate_path, PathGenerationRequest

def test_goals():
    db = SessionLocal()
    
    goals = [
        "Backend Developer",
        "Full Stack Developer",
        "Frontend Developer",
        "AI Engineer",
        "Machine Learning Engineer",
        "Data Scientist",
        "Data Engineer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Cybersecurity Engineer",
        "Generative AI Engineer",
        "RAG Engineer"
    ]
    
    print("\n--- GOAL PATH GENERATION TEST ---")
    for g in goals:
        req = PathGenerationRequest(
            target_skill_name=g,
            current_skills=[],
            completed_skill_ids=[],
            learner_level="INTERMEDIATE"
        )
        try:
            res = generate_path(req, db, current_user=None)
            target = res["target"]["name"]
            nodes = len(res["nodes"])
            edges = len(res["edges"])
            print(f"Goal: {g:<30} -> Resolved Target: {target:<30} | Nodes: {nodes:<2} | Edges: {edges:<2} | Succeeded: Yes")
        except Exception as e:
            print(f"Goal: {g:<30} -> FAILED: {str(e)}")

if __name__ == "__main__":
    test_goals()
