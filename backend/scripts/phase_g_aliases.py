import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill

# Target roles and the skills they should map to.
# We will append these roles to the skill's aliases.
ROLE_ALIASES = {
    "Backend Development": ["Backend Engineer", "Backend Developer"],
    "Frontend Development": ["Frontend Engineer", "Frontend Developer"],
    "Full Stack Developer": ["Full Stack Engineer", "Full Stack Development"],
    "Artificial Intelligence": ["AI Engineer"],
    "Machine Learning": ["ML Engineer", "Machine Learning Engineer"],
    "Data Engineering": ["Data Engineer"],
    "Data Science": ["Data Scientist"],
    "DevOps": ["DevOps Engineer"],
    "Cloud Computing": ["Cloud Engineer"],
    "Amazon Web Services": ["AWS", "AWS Engineer"],
    "Cybersecurity": ["Cybersecurity Engineer"],
    "Generative AI": ["Generative AI Engineer"],
    "Large Language Models": ["LLM Engineer"],
    "RAG": ["RAG Engineer", "RAG Developer", "Retrieval Augmented Generation", "Retrieval-Augmented Generation"]
}

def update_aliases():
    db = SessionLocal()
    total_added = 0
    
    for skill_name, new_aliases in ROLE_ALIASES.items():
        # Case insensitive search
        skill = db.query(Skill).filter(Skill.name.ilike(skill_name)).first()
        if not skill:
            print(f"[WARNING] Skill not found: {skill_name}")
            continue
            
        current_aliases = []
        if skill.aliases:
            try:
                current_aliases = json.loads(skill.aliases)
                if not isinstance(current_aliases, list):
                    current_aliases = []
            except:
                current_aliases = []
                
        added_for_skill = 0
        for alias in new_aliases:
            # Case insensitive check
            if not any(a.lower() == alias.lower() for a in current_aliases):
                current_aliases.append(alias)
                added_for_skill += 1
                total_added += 1
                
        if added_for_skill > 0:
            skill.aliases = json.dumps(current_aliases)
            print(f"[UPDATED] {skill.name} -> {current_aliases}")
            
    db.commit()
    db.close()
    
    print(f"\nTotal new aliases added: {total_added}")

if __name__ == "__main__":
    update_aliases()
