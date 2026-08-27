from typing import List, Dict, Any
from datetime import datetime, timezone
import dateutil.parser

class YouTubeRanker:
    def __init__(self, semantic_matcher):
        self.semantic_matcher = semantic_matcher
        
        # Configurable weights
        self.weight_semantic = 0.70
        self.weight_quality = 0.20
        self.weight_freshness = 0.10
        
    def rank_and_filter(self, videos: List[Dict[str, Any]], target_skill: Any, learner_level: str) -> List[Dict[str, Any]]:
        """
        Filters and ranks raw YouTube Data API video responses based on semantics, engagement, and freshness.
        """
        if not videos:
            return []
            
        # Extract text for semantic embedding
        texts = []
        for v in videos:
            snippet = v.get("snippet", {})
            # Emphasize title more
            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            texts.append(f"{title}. {title}. {desc}")
            
        embeddings = self.semantic_matcher.embed_texts(texts)
        
        # We need the embedding for the skill itself
        import json
        aliases = []
        if target_skill.aliases:
            try:
                aliases = json.loads(target_skill.aliases)
            except:
                pass
        skill_text = f"{target_skill.name}. {target_skill.description}. " + " ".join(aliases)
        skill_emb = self.semantic_matcher.embed_texts([skill_text])[0]
        
        # Compute cosine similarities manually against the specific skill
        import torch
        skill_tensor = torch.tensor(skill_emb).unsqueeze(0)
        video_tensors = torch.tensor(embeddings)
        similarities = torch.nn.functional.cosine_similarity(skill_tensor, video_tensors).tolist()
        
        ranked_videos = []
        
        # Baseline engagement
        max_views = max([int(v.get("statistics", {}).get("viewCount", "0") or 0) for v in videos] + [1])
        
        now = datetime.now(timezone.utc)
        
        for i, v in enumerate(videos):
            semantic_score = similarities[i]
            
            # Semantic filter (reject completely irrelevant)
            if semantic_score < self.semantic_matcher.threshold:
                continue
                
            stats = v.get("statistics", {})
            views = int(stats.get("viewCount", "0") or 0)
            quality_score = min(views / (max_views if max_views > 0 else 1), 1.0)
            
            # Freshness score (decay over 5 years)
            published_at_str = v.get("snippet", {}).get("publishedAt")
            freshness_score = 0.5 # default
            if published_at_str:
                try:
                    pub_date = dateutil.parser.isoparse(published_at_str)
                    age_days = (now - pub_date).days
                    # Normalize: 0 days = 1.0, 5 years (1825 days) = 0.0
                    freshness_score = max(0.0, 1.0 - (age_days / 1825.0))
                except:
                    pass
                    
            # Basic level adjustment (heuristic)
            # If beginner, favor views and "tutorial/beginner" keywords.
            # If advanced, favor high semantic match and ignore views penalty.
            title_lower = v.get("snippet", {}).get("title", "").lower()
            if learner_level.upper() == "BEGINNER":
                if "beginner" in title_lower or "basics" in title_lower:
                    semantic_score = min(semantic_score + 0.1, 1.0)
            elif learner_level.upper() == "ADVANCED":
                if "advanced" in title_lower or "deep dive" in title_lower:
                    semantic_score = min(semantic_score + 0.1, 1.0)
                # Reduce view penalty for advanced
                quality_score = min(quality_score + 0.3, 1.0)
                
            final_score = (semantic_score * self.weight_semantic) + (quality_score * self.weight_quality) + (freshness_score * self.weight_freshness)
            
            ranked_videos.append({
                "video_id": v["id"] if isinstance(v["id"], str) else v["id"]["videoId"], # Depending on search vs video endpoint
                "raw_api_data": v,
                "semantic_score": semantic_score,
                "final_score": final_score,
                "metrics": {
                    "views": views,
                    "freshness": freshness_score
                }
            })
            
        # Sort descending by final score
        ranked_videos.sort(key=lambda x: x["final_score"], reverse=True)
        return ranked_videos
