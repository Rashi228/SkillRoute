import os
import sys
import json
import hashlib
from typing import List

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill
from sentence_transformers import SentenceTransformer

def get_content_hash(name: str, desc: str, aliases: str) -> str:
    content = f"{name} {desc or ''} {aliases or ''}"
    return hashlib.sha256(content.encode()).hexdigest()

def main():
    db = SessionLocal()
    
    model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    skills = db.query(Skill).all()
    print(f"Found {len(skills)} skills in DB.")
    
    updated_count = 0
    for skill in skills:
        content_hash = get_content_hash(skill.name, skill.description, skill.aliases)
        
        # Check if re-embedding is needed
        if (skill.embedding_model != model_name or
            skill.embedding_content_hash != content_hash or
            not skill.embedding):
            
            # Combine text
            text = skill.name
            if skill.description:
                text += f"\nDescription: {skill.description}"
            if skill.aliases:
                try:
                    aliases_list = json.loads(skill.aliases)
                    text += f"\nAliases: {', '.join(aliases_list)}"
                except:
                    pass
                    
            print(f"Generating embedding for skill: {skill.name}")
            embedding = model.encode(text).tolist()
            
            # Save
            skill.embedding = json.dumps(embedding)
            skill.embedding_model = model_name
            skill.embedding_version = "v1"
            skill.embedding_content_hash = content_hash
            updated_count += 1
            
    db.commit()
    print(f"Updated embeddings for {updated_count} skills.")

if __name__ == "__main__":
    main()
