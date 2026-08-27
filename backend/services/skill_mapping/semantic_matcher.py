import os
from typing import List, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer, util
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from models import Skill
import torch

class SemanticMatcher:
    def __init__(self, embedding_store: SkillEmbeddingStore, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_store = embedding_store
        self.model_name = os.environ.get("EMBEDDING_MODEL", model_name)
        
        # Load the local model
        self.model = SentenceTransformer(self.model_name)
        
        # Load Skill Embeddings into memory
        self.skill_embeddings_data = self.embedding_store.get_all_embeddings()
        
        # Prepare tensors for fast cosine similarity
        self.skill_ids = [s[0].id for s in self.skill_embeddings_data]
        self.skill_objects = {s[0].id: s[0] for s in self.skill_embeddings_data}
        
        if self.skill_embeddings_data:
            self.skill_tensor = torch.tensor([s[1] for s in self.skill_embeddings_data])
        else:
            self.skill_tensor = torch.empty((0, self.model.get_sentence_embedding_dimension()))
            
        self.threshold = float(os.environ.get("SKILL_SIMILARITY_THRESHOLD", "0.33"))
        self.top_k = int(os.environ.get("SKILL_SIMILARITY_TOP_K", "5"))
        self.ambiguity_margin = float(os.environ.get("AMBIGUITY_MARGIN", "0.03"))

    def embed_texts(self, texts: List[str]) -> torch.Tensor:
        """Batch generates embeddings for a list of texts."""
        if not texts:
            return torch.empty(0)
        return self.model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    def match_batch(self, resource_embeddings: torch.Tensor) -> List[List[Dict[str, Any]]]:
        """
        Calculates cosine similarity between resource embeddings and skill embeddings.
        Returns a list of candidates for each resource.
        """
        if self.skill_tensor.size(0) == 0:
            return [[] for _ in range(resource_embeddings.size(0))]
            
        # Cosine similarity matrix: (num_resources, num_skills)
        cos_scores = util.cos_sim(resource_embeddings, self.skill_tensor)
        
        results = []
        for scores in cos_scores:
            # Sort scores in descending order
            top_results = torch.topk(scores, k=min(self.top_k, len(scores)))
            
            candidates = []
            for score, idx in zip(top_results[0], top_results[1]):
                candidates.append({
                    "skill_id": self.skill_ids[idx],
                    "skill": self.skill_objects[self.skill_ids[idx]],
                    "score": score.item()
                })
            results.append(candidates)
            
        return results

    def resolve_candidates(self, candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Applies thresholds and ambiguity margin to candidates.
        Returns: (high_confidence, ambiguous, low_confidence)
        """
        high = []
        ambiguous = []
        low = []
        
        if not candidates:
            return high, ambiguous, low
            
        # Filter by absolute threshold first
        valid = [c for c in candidates if c["score"] >= self.threshold]
        invalid = [c for c in candidates if c["score"] < self.threshold]
        low.extend(invalid)
        
        if not valid:
            return high, ambiguous, low
            
        # Sort by score
        valid.sort(key=lambda x: x["score"], reverse=True)
        
        # Ambiguity check (top-1 vs top-2 margin)
        if len(valid) >= 2:
            top1 = valid[0]["score"]
            top2 = valid[1]["score"]
            if (top1 - top2) <= self.ambiguity_margin:
                # Ambiguous! Send the top candidates that are close to each other
                for c in valid:
                    if (top1 - c["score"]) <= self.ambiguity_margin:
                        ambiguous.append(c)
                    else:
                        high.append(c) # Or maybe lower confidence should be dropped? We'll just separate them.
            else:
                # Top 1 is clear winner, but maybe multiple skills are highly relevant?
                # For this implementation, if top1 is clear, we map top1 (and others if they clear the threshold but aren't ambiguous? 
                # Wait, the user said "Allow multiple valid skills per resource. Do not force a single skill."
                # So if they clear the threshold, they are valid. Ambiguity is just to decide if we need Groq.
                # If they are clustered, Groq helps pick the BEST or ALL.
                high.extend(valid)
        else:
            high.extend(valid)
            
        return high, ambiguous, low
