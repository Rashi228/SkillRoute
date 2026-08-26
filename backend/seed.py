import os
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
from models import Skill, SkillPrerequisite, Resource, ResourceSkill, CostType

def seed_db():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(Skill).first():
        print("Database already seeded.")
        return
        
    print("Seeding Skills...")
    python = Skill(name="Python", description="Basic Python Programming")
    ml = Skill(name="Machine Learning", description="ML Fundamentals")
    transformers = Skill(name="Transformers", description="Attention mechanisms")
    rag = Skill(name="RAG", description="Retrieval-Augmented Generation")
    
    db.add_all([python, ml, transformers, rag])
    db.commit()
    
    print("Seeding Prerequisites...")
    db.add(SkillPrerequisite(skill_id=ml.id, prerequisite_id=python.id))
    db.add(SkillPrerequisite(skill_id=transformers.id, prerequisite_id=ml.id))
    db.add(SkillPrerequisite(skill_id=rag.id, prerequisite_id=transformers.id))
    db.commit()
    
    print("Seeding Resources...")
    res1 = Resource(title="Python for Beginners", resource_type="Video", url="https://youtube.com/python", difficulty="Beginner", duration_hours=2.0, cost_type=CostType.FREE)
    res2 = Resource(title="ML Crash Course", resource_type="Course", url="https://google.com/ml", difficulty="Intermediate", duration_hours=5.0, cost_type=CostType.FREE)
    res3 = Resource(title="Transformer Models Explained", resource_type="Article", url="https://blog.com/transformers", difficulty="Advanced", duration_hours=1.5, cost_type=CostType.FREEMIUM)
    res4 = Resource(title="Build a RAG app", resource_type="Project", url="https://github.com/rag-app", difficulty="Advanced", duration_hours=10.0, cost_type=CostType.FREE)
    
    db.add_all([res1, res2, res3, res4])
    db.commit()
    
    print("Mapping Resources to Skills...")
    db.add(ResourceSkill(resource_id=res1.id, skill_id=python.id))
    db.add(ResourceSkill(resource_id=res2.id, skill_id=ml.id))
    db.add(ResourceSkill(resource_id=res3.id, skill_id=transformers.id))
    db.add(ResourceSkill(resource_id=res4.id, skill_id=rag.id))
    db.commit()
    
    print("Seeding complete!")

if __name__ == "__main__":
    seed_db()
