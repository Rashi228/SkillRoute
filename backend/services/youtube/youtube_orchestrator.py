import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from services.youtube.youtube_client import YouTubeClient
from services.youtube.youtube_search import YouTubeSearchIntent
from services.youtube.youtube_ranker import YouTubeRanker
from services.youtube.youtube_cache import YouTubeCache
from services.skill_mapping.semantic_matcher import SemanticMatcher
from services.skill_mapping.embedding_store import SkillEmbeddingStore
from models import Skill, Resource, ResourceSkill
import aiohttp

class YouTubeDiscoveryOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.client = YouTubeClient()
        self.search_intent = YouTubeSearchIntent()
        self.cache = YouTubeCache(db)
        
        # Share semantic matcher
        self.semantic_matcher = SemanticMatcher(SkillEmbeddingStore(db))
        self.ranker = YouTubeRanker(self.semantic_matcher)
        
        self.metrics = {
            "groq_calls": 0,
            "youtube_api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "videos_received": 0,
            "videos_deduplicated": 0,
            "videos_rejected": 0,
            "videos_verified": 0,
            "videos_cached": 0,
            "final_recommendations": 0
        }

    async def discover(self, skill_id: int, learner_level: str, goal: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            raise ValueError(f"Skill ID {skill_id} not found")
            
        # 1. Check Cache
        is_hit, cached_resources = self.cache.check_cache(skill_id)
        if is_hit:
            self.metrics["cache_hits"] += 1
            self.metrics["final_recommendations"] = len(cached_resources)
            return {
                "status": "CACHE_HIT",
                "resources": [self._format_resource(r, True) for r in cached_resources],
                "metrics": self.metrics
            }
            
        self.metrics["cache_misses"] += 1
        
        # 2. Generate Search Intent
        aliases = []
        if skill.aliases:
            try:
                aliases = json.loads(skill.aliases)
            except:
                pass
                
        queries = self.search_intent.generate_queries(skill.name, aliases, learner_level, goal, constraints)
        self.metrics["groq_calls"] = self.search_intent.calls_made
        
        # 3. Search YouTube & Deduplicate across queries
        discovered_urls = self.cache.get_existing_urls() # Used for deduplication
        raw_videos = []
        
        for q in queries:
            vids = self.client.search_videos(q)
            self.metrics["youtube_api_calls"] += 1 # 1 for search, 1 for enrich (tracked in client, but we approximate here, client has calls_made)
            self.metrics["videos_received"] += len(vids)
            
            for v in vids:
                vid_id = v["id"] if isinstance(v["id"], str) else v["id"]["videoId"]
                url = f"https://www.youtube.com/watch?v={vid_id}"
                
                # Check for duplicate in THIS BATCH to prevent processing the same API result twice
                if url not in [f"https://www.youtube.com/watch?v={rv['id'] if isinstance(rv['id'], str) else rv['id']['videoId']}" for rv in raw_videos]:
                    raw_videos.append(v)
                else:
                    self.metrics["videos_deduplicated"] += 1
                    
        self.metrics["youtube_api_calls"] = self.client.calls_made
        
        if not raw_videos:
            return {
                "status": "DISCOVERY_UNAVAILABLE",
                "message": "No new videos found from YouTube API",
                "resources": [self._format_resource(r, True) for r in cached_resources], # Return whatever was in cache
                "metrics": self.metrics
            }
            
        # 4. Rank and Filter (Semantic)
        ranked = self.ranker.rank_and_filter(raw_videos, skill, learner_level)
        self.metrics["videos_rejected"] = len(raw_videos) - len(ranked)
        
        # 5. URL Verification
        # We only verify the top candidates to save time. Let's take top 10 max.
        top_ranked = ranked[:10]
        urls_to_verify = [f"https://www.youtube.com/watch?v={v['video_id']}" for v in top_ranked]
        validation_results = await self._validate_urls(urls_to_verify)
        
        # 6. Cache into DB
        final_resources = []
        processed_urls = set()
        for v in top_ranked:
            url = f"https://www.youtube.com/watch?v={v['video_id']}"
            if url in processed_urls:
                continue
            processed_urls.add(url)
            is_valid = validation_results.get(url, False)
            
            if not is_valid:
                continue # Skip invalid
                
            self.metrics["videos_verified"] += 1
            
            new_res = self._insert_resource(v, skill, learner_level)
            final_resources.append(new_res)
            
        self.db.commit()
        self.metrics["videos_cached"] = len(final_resources)
        
        # Combine new and existing cache
        all_resources = cached_resources + final_resources
        
        # Sort combined results by relevance if they have it, else put new ones first
        self.metrics["final_recommendations"] = len(all_resources)
        
        return {
            "status": "DISCOVERED",
            "resources": [self._format_resource(r, False) if r in final_resources else self._format_resource(r, True) for r in all_resources],
            "metrics": self.metrics
        }
        
    async def _validate_urls(self, urls: List[str]) -> Dict[str, bool]:
        results = {}
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, timeout=5) as response:
                        results[url] = response.status == 200
                except:
                    results[url] = False
        return results
        
    def _insert_resource(self, ranked_vid: Dict[str, Any], skill: Skill, learner_level: str) -> Resource:
        raw = ranked_vid["raw_api_data"]
        snippet = raw.get("snippet", {})
        stats = raw.get("statistics", {})
        content_details = raw.get("contentDetails", {})
        
        vid_id = ranked_vid["video_id"]
        url = f"https://www.youtube.com/watch?v={vid_id}"
        
        # Check if already exists in DB
        existing = self.db.query(Resource).filter(Resource.canonical_url == url).first()
        if existing:
            # Map skill if not mapped
            rs = self.db.query(ResourceSkill).filter_by(resource_id=existing.id, skill_id=skill.id).first()
            if not rs:
                rs = ResourceSkill(resource_id=existing.id, skill_id=skill.id, mapping_source="SEMANTIC", confidence=ranked_vid["semantic_score"])
                self.db.add(rs)
            return existing
        
        # Extract duration
        duration_iso = content_details.get("duration", "PT0M")
        
        meta = {
            "search_query_intent": True,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "channel_id": snippet.get("channelId"),
            "category_id": snippet.get("categoryId"),
            "ranking": {
                "semantic_score": ranked_vid["semantic_score"],
                "final_score": ranked_vid["final_score"],
                "views": ranked_vid["metrics"]["views"]
            },
            "why_recommended": {
                "skill_match": skill.name,
                "semantic_score": round(ranked_vid["semantic_score"], 2),
                "difficulty_match": learner_level,
                "source": "YouTube API",
                "verified": True
            }
        }
        
        r = Resource(
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            provider="YOUTUBE",
            source="YOUTUBE_API",
            external_id=vid_id,
            canonical_url=url,
            final_url=url,
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
            channel_id=snippet.get("channelTitle"),
            published_at=dateutil.parser.isoparse(snippet.get("publishedAt")) if snippet.get("publishedAt") else None,
            duration_seconds=0,
            view_count=int(stats.get("viewCount", "0") or 0),
            cost_type="FREE",
            verification_status="VERIFIED",
            last_verified=datetime.now(timezone.utc),
            is_active=True,
            metadata_json=json.dumps(meta)
        )
        self.db.add(r)
        self.db.flush() # Get ID
        
        # Map skill
        rs = ResourceSkill(resource_id=r.id, skill_id=skill.id, mapping_source="SEMANTIC", confidence=ranked_vid["semantic_score"])
        self.db.add(rs)
        
        return r
        
    def _format_resource(self, r: Resource, from_cache: bool) -> Dict[str, Any]:
        meta = {}
        if r.metadata_json:
            try:
                meta = json.loads(r.metadata_json)
            except:
                pass
        return {
            "id": r.id,
            "title": r.title,
            "description": r.description[:200] + "..." if r.description else "",
            "thumbnail": r.thumbnail_url,
            "channel": r.channel_id,
            "duration": r.duration_seconds,
            "views": r.view_count,
            "url": r.canonical_url,
            "cost_type": r.cost_type.value if hasattr(r.cost_type, "value") else str(r.cost_type),
            "verified": r.verification_status.value == "VERIFIED" if hasattr(r.verification_status, "value") else str(r.verification_status) == "VERIFIED",
            "cached": from_cache,
            "why_recommended": meta.get("why_recommended", {})
        }

import dateutil.parser
