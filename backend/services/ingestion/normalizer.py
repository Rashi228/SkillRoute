from typing import List, Tuple
from sqlalchemy.orm import Session
from models import Skill
from .base import NormalizedResource

class CostClassifier:
    @staticmethod
    def classify(resource: NormalizedResource, raw_row: dict) -> NormalizedResource:
        # Default strategy for Coursera
        # In a real implementation this would check `raw_row` for explicit 'price' or 'is_paid'
        
        provider = resource.provider.lower()
        if provider == "coursera":
            # Most coursera courses have free audit
            resource.cost_type = "FREE_AUDIT"
        else:
            resource.cost_type = "UNKNOWN"
            
        # Hardcode price test
        if raw_row.get('price'):
            try:
                price = float(raw_row.get('price'))
                resource.price_amount = price
                resource.currency = "USD"
                if price > 0:
                    resource.cost_type = "PAID"
                else:
                    resource.cost_type = "FREE"
            except:
                pass
                
        return resource

class SkillMapper:
    def __init__(self, db: Session):
        self.db = db
        # Load controlled vocabulary into memory for fast matching
        self.vocabulary = {s.name.lower(): s.id for s in db.query(Skill).all()}

    def map_skills(self, resource: NormalizedResource) -> List[Tuple[int, float]]:
        """
        Maps raw skills to DB Skill IDs with a confidence score.
        Phase 1: Basic string matching against controlled vocabulary.
        Returns: List of tuples (skill_id, confidence)
        """
        mapped = []
        for raw_skill in resource.raw_skills:
            normalized_raw = raw_skill.lower().strip()
            
            # Exact match
            if normalized_raw in self.vocabulary:
                mapped.append((self.vocabulary[normalized_raw], 1.0))
            else:
                # Basic substring match
                for vocab_skill, skill_id in self.vocabulary.items():
                    if vocab_skill in normalized_raw or normalized_raw in vocab_skill:
                        mapped.append((skill_id, 0.8))
                        
        # Deduplicate mapped skills keeping highest confidence
        unique_mapped = {}
        for s_id, conf in mapped:
            if s_id not in unique_mapped or unique_mapped[s_id] < conf:
                unique_mapped[s_id] = conf
                
        return list(unique_mapped.items())
