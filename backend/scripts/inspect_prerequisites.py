import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill, SkillPrerequisite

def inspect():
    db = SessionLocal()
    
    skills = db.query(Skill).all()
    prereqs = db.query(SkillPrerequisite).all()
    
    print(f"Current Skill count: {len(skills)}")
    print(f"Current SkillPrerequisite count: {len(prereqs)}")
    
    skill_dict = {s.id: s.name for s in skills}
    
    print("\nExisting Prerequisite Relationships:")
    for p in prereqs:
        target = skill_dict.get(p.skill_id, f"Unknown({p.skill_id})")
        req = skill_dict.get(p.prerequisite_id, f"Unknown({p.prerequisite_id})")
        print(f"  {req} -> {target}")
        
    has_prereqs = set(p.skill_id for p in prereqs)
    no_prereqs = [s.name for s in skills if s.id not in has_prereqs]
    
    print(f"\nSkills currently having NO prerequisites ({len(no_prereqs)}):")
    for name in no_prereqs:
        print(f"  - {name}")

if __name__ == "__main__":
    inspect()
