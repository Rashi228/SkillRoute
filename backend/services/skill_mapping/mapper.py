from typing import List, Tuple, Dict
from sqlalchemy.orm import Session
from models import Resource
from services.ingestion.base import NormalizedResource
from .embedding_store import SkillEmbeddingStore
from .aliases import AliasManager
from .exact_matcher import ExactMatcher
from .semantic_matcher import SemanticMatcher
from .llm_resolver import LLMResolver
import torch

class SkillMapperOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_store = SkillEmbeddingStore(db)
        self.alias_manager = AliasManager(db)
        self.exact_matcher = ExactMatcher(self.alias_manager)
        
        # Load semantic matcher only if there are skills to match against
        self.semantic_matcher = SemanticMatcher(self.embedding_store)
        self.llm_resolver = LLMResolver()

    def process_batch(self, resources: List[NormalizedResource]) -> List[List[Tuple[int, float, str]]]:
        """
        Processes a batch of resources through the cascade:
        Exact -> Alias -> Semantic -> Groq
        Returns a list of mapped skills (skill_id, conf, source) for each resource.
        """
        final_mappings = []
        
        # 1. Prepare Semantic Embeddings for the entire batch
        semantic_texts = []
        for res in resources:
            # Combine title, description, and outcomes into one semantic string
            text = f"{res.title}. {res.description or ''}. Skills: {', '.join(res.raw_skills)}"
            semantic_texts.append(text)
            
        resource_embeddings = self.semantic_matcher.embed_texts(semantic_texts)
        semantic_candidates = self.semantic_matcher.match_batch(resource_embeddings)
        
        # 2. Process each resource
        for i, res in enumerate(resources):
            res_mappings = []
            mapped_skill_ids = set()
            
            # Step A: Explicit Provider Skills (Exact & Alias)
            explicit_matches = self.exact_matcher.match_provider_skills(res.raw_skills)
            for skill_id, conf, source in explicit_matches:
                if skill_id not in mapped_skill_ids:
                    res_mappings.append((skill_id, conf, source))
                    mapped_skill_ids.add(skill_id)
                    
            # Step B: Semantic Matches & Ambiguity Resolution
            candidates = semantic_candidates[i]
            high, ambiguous, low = self.semantic_matcher.resolve_candidates(candidates)
            
            # Add high confidence semantic matches
            for c in high:
                if c["skill_id"] not in mapped_skill_ids:
                    res_mappings.append((c["skill_id"], c["score"], "SEMANTIC"))
                    mapped_skill_ids.add(c["skill_id"])
                    
            # Resolve ambiguous
            if ambiguous:
                decision = self.llm_resolver.resolve_ambiguity(res.title, res.description or "", ambiguous)
                if decision and decision.decision == "MAP":
                    for skill_id in decision.skill_ids:
                        if skill_id not in mapped_skill_ids:
                            # Verify Groq didn't hallucinate an ID
                            if any(c["skill_id"] == skill_id for c in ambiguous):
                                res_mappings.append((skill_id, decision.confidence, "LLM_REVIEW"))
                                mapped_skill_ids.add(skill_id)
                                
            final_mappings.append(res_mappings)
            
        return final_mappings
