import sys, os, random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from models import Skill, PathTransition

db = SessionLocal()
skills = db.query(Skill).all()
skill_ids = [s.id for s in skills]

random.seed(42)
for _ in range(40):
    from_id = random.choice(skill_ids + [None])
    to_id = random.choice(skill_ids)
    existing = db.query(PathTransition).filter_by(from_skill_id=from_id, to_skill_id=to_id).first()
    if existing:
        existing.count += 1
    else:
        db.add(PathTransition(from_skill_id=from_id, to_skill_id=to_id, count=random.randint(1, 8)))
db.commit()
print("Seeded synthetic path transitions.")
