import sys
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()
sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator
from models import Skill

async def main():
    db = SessionLocal()
    
    skill = db.query(Skill).filter(Skill.name == "Generative AI").first()
    if not skill:
        skill = db.query(Skill).filter(Skill.name == "Machine Learning").first()
    if not skill:
        print("No skills found. Run seed_skills_extended.py first.")
        sys.exit(1)
        
    orchestrator = YouTubeDiscoveryOrchestrator(db)
    
    print(f"\n--- RUN 1 (Cache Miss Expected) ---")
    print(f"Discovering resources for Skill: {skill.name} (ID: {skill.id})")
    
    res1 = await orchestrator.discover(
        skill_id=skill.id,
        learner_level="INTERMEDIATE",
        goal="Build real apps",
        constraints={"language": "English"}
    )
    
    print(f"\nStatus: {res1['status']}")
    print("Metrics:")
    for k, v in res1["metrics"].items():
        print(f"  {k}: {v}")
        
    print("\nSample Recommended Resource:")
    if res1["resources"]:
        print(json.dumps(res1["resources"][0], indent=2))
        
    print(f"\n--- RUN 2 (Cache Hit Expected) ---")
    res2 = await orchestrator.discover(
        skill_id=skill.id,
        learner_level="INTERMEDIATE",
        goal="Build real apps",
        constraints={"language": "English"}
    )
    
    print(f"\nStatus: {res2['status']}")
    print("Metrics:")
    for k, v in res2["metrics"].items():
        print(f"  {k}: {v}")
        
if __name__ == "__main__":
    asyncio.run(main())
