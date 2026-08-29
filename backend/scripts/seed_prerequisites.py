"""
Seeds SkillPrerequisite edges for the extended skill catalogue.
Run AFTER seed_skills_extended.py has populated the skills table.

Usage:
    cd backend
    python scripts/seed_prerequisites.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill, SkillPrerequisite

db = SessionLocal()

# (child_skill_name, [prerequisite_skill_names])
# Names must match Skill.name exactly as seeded in seed_skills_extended.py / seed.py
EDGES = [
    # --- Programming foundations ---
    ("Data Structures", ["Python"]),
    ("Algorithms", ["Data Structures"]),
    ("Object-Oriented Programming", ["Python"]),
    ("Functional Programming", ["Python"]),
    ("Test-Driven Development", ["Object-Oriented Programming"]),

    # --- Backend ---
    ("Backend Development", ["Python"]),
    ("API Design", ["Backend Development"]),
    ("Node.js", ["JavaScript"]),
    ("Java", ["Object-Oriented Programming"]),
    ("Go", ["Data Structures"]),
    ("C++", ["Data Structures"]),
    ("Ruby on Rails", ["Backend Development"]),

    # --- Frontend ---
    ("JavaScript", ["HTML/CSS"]),
    ("TypeScript", ["JavaScript"]),
    ("React", ["JavaScript"]),
    ("Angular", ["TypeScript"]),
    ("Vue.js", ["JavaScript"]),
    ("Frontend Development", ["HTML/CSS"]),

    # --- Data & Database ---
    ("Database Management", ["SQL"]),
    ("NoSQL", ["Database Management"]),
    ("Data Engineering", ["SQL", "Python"]),
    ("Big Data", ["Data Engineering"]),
    ("Data Science", ["Python", "SQL"]),

    # --- AI / ML ---
    ("Machine Learning", ["Data Science"]),
    ("Deep Learning", ["Machine Learning"]),
    ("Generative AI", ["Deep Learning"]),
    ("Large Language Models", ["Generative AI"]),
    ("Retrieval-Augmented Generation", ["Large Language Models"]),
    ("Natural Language Processing", ["Machine Learning"]),
    ("Computer Vision", ["Deep Learning"]),
    ("Reinforcement Learning", ["Machine Learning"]),
    ("Prompt Engineering", ["Large Language Models"]),

    # --- Cloud / DevOps ---
    ("Cloud Computing", ["Backend Development"]),
    ("Amazon Web Services", ["Cloud Computing"]),
    ("Microsoft Azure", ["Cloud Computing"]),
    ("Google Cloud Platform", ["Cloud Computing"]),
    ("DevOps", ["Backend Development"]),
    ("Continuous Integration and Delivery", ["DevOps"]),
    ("Docker", ["DevOps"]),
    ("Kubernetes", ["Docker"]),
    ("Infrastructure as Code", ["Cloud Computing"]),
    ("MLOps", ["Machine Learning", "DevOps"]),

    # --- Architecture ---
    ("System Design", ["Data Structures", "Algorithms"]),
    ("Microservices", ["System Design", "API Design"]),

    # --- Security ---
    ("Cybersecurity", ["Backend Development"]),
    ("Network Security", ["Cybersecurity"]),
    ("Cryptography", ["Cybersecurity"]),
    ("Blockchain", ["Cryptography"]),

    # --- Other ---
    ("Mobile Development", ["React"]),
]

inserted = 0
skipped_missing_skill = []

for child_name, prereq_names in EDGES:
    child = db.query(Skill).filter(Skill.name.ilike(child_name)).first()
    if not child:
        skipped_missing_skill.append(child_name)
        continue

    for prereq_name in prereq_names:
        prereq = db.query(Skill).filter(Skill.name.ilike(prereq_name)).first()
        if not prereq:
            skipped_missing_skill.append(prereq_name)
            continue

        exists = db.query(SkillPrerequisite).filter_by(
            skill_id=child.id, prerequisite_id=prereq.id
        ).first()
        if not exists:
            db.add(SkillPrerequisite(skill_id=child.id, prerequisite_id=prereq.id))
            inserted += 1

db.commit()
print(f"Inserted {inserted} new prerequisite edges.")
if skipped_missing_skill:
    print(f"Skipped (skill name not found in DB): {sorted(set(skipped_missing_skill))}")
