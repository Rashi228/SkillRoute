import json
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from models import Skill
import datetime

class SkillEmbeddingStore:
    """
    Abstracts embedding storage to decouple from PostgreSQL JSON/ARRAY fallback.
    When pgvector is available, this can be updated to use actual Vector columns
    without changing the mapping logic.
    """
    def __init__(self, db: Session):
        self.db = db
        
    def get_all_embeddings(self) -> List[Tuple[Skill, List[float]]]:
        """
        Returns a list of (Skill, embedding) for all skills that have an embedding.
        """
        skills = self.db.query(Skill).filter(Skill.embedding.isnot(None)).all()
        results = []
        for s in skills:
            try:
                emb = json.loads(s.embedding)
                results.append((s, emb))
            except Exception:
                pass
        return results

    def save_embedding(self, skill_id: int, embedding: List[float], model: str, version: str, content_hash: str):
        """
        Saves a newly generated embedding for a skill.
        """
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            skill.embedding = json.dumps(embedding)
            skill.embedding_model = model
            skill.embedding_version = version
            skill.embedding_content_hash = content_hash
            skill.embedding_updated_at = datetime.datetime.utcnow()
            self.db.commit()
