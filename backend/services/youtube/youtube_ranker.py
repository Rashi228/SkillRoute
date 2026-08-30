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
            if not isinstance(v, dict):
                texts.append("")
                continue
            snippet = v.get("snippet", {})
            if not isinstance(snippet, dict):
                snippet = {}
            # Emphasize title more
            title = snippet.get("title", "")
            desc = snippet.get("description", "")
            texts.append(f"{title}. {title}. {desc}")
            
        import json
        aliases = []
        if target_skill.aliases:
            try:
                aliases = json.loads(target_skill.aliases)
            except:
                pass
                
        # Attempt semantic ranking
        similarities = None
        use_fallback = False
        try:
            embeddings = self.semantic_matcher.embed_texts(texts)
            skill_text = f"{target_skill.name}. {target_skill.description}. " + " ".join(aliases)
            skill_emb = self.semantic_matcher.embed_texts([skill_text])[0]
            
            import torch
            # Safe detach/clone for tensors as per warnings
            skill_tensor = torch.tensor(skill_emb).clone().detach().unsqueeze(0)
            video_tensors = torch.tensor(embeddings).clone().detach()
            similarities = torch.nn.functional.cosine_similarity(skill_tensor, video_tensors).tolist()
        except Exception as e:
            print(f"Semantic ranking failed: {e}. Falling back to deterministic keyword scoring.")
            use_fallback = True
        
        ranked_videos = []
        
        # Baseline engagement
        max_views = max([int(v.get("statistics", {}).get("viewCount", "0") or 0) for v in videos] + [1])
        
        now = datetime.now(timezone.utc)
        
        for i, v in enumerate(videos):
            if not use_fallback and similarities:
                semantic_score = similarities[i]
            else:
                # Deterministic keyword fallback
                text_to_search = texts[i].lower()
                target_terms = [target_skill.name.lower()] + [a.lower() for a in aliases]
                matches = sum(1 for term in target_terms if term in text_to_search)
                # Maximize at 1.0, minimum base score
                semantic_score = min(0.3 + (matches * 0.2), 1.0)
                if matches == 0:
                    semantic_score = 0.0 # completely irrelevant
            
            # Semantic filter (reject completely irrelevant)
            if semantic_score < self.semantic_matcher.threshold and not use_fallback:
                continue
            elif use_fallback and semantic_score < 0.3:
                continue
                
            if not isinstance(v, dict):
                continue
            stats = v.get("statistics", {})
            if not isinstance(stats, dict):
                stats = {}
            views = int(stats.get("viewCount", "0") or 0)
            quality_score = min(views / (max_views if max_views > 0 else 1), 1.0)
            
            # Freshness score (decay over 5 years)
            snippet = v.get("snippet", {})
            if not isinstance(snippet, dict):
                snippet = {}
            published_at_str = snippet.get("publishedAt")
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
            title_lower = snippet.get("title", "").lower()
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
