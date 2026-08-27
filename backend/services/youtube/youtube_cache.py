import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Resource, ResourceSkill

class YouTubeCache:
    def __init__(self, db: Session):
        self.db = db
        self.min_cache_results = int(os.environ.get("YOUTUBE_MIN_CACHE_RESULTS", "5"))
        self.cache_ttl_hours = int(os.environ.get("YOUTUBE_CACHE_TTL_HOURS", "168"))
        
    def check_cache(self, skill_id: int) -> Tuple[bool, List[Resource]]:
        """
        Checks if we have enough fresh, verified YouTube resources for the given skill.
        Returns (is_cache_hit, list_of_resources).
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(hours=self.cache_ttl_hours)
        
        # Query for active, verified YouTube resources mapped to this skill
        cached = self.db.query(Resource).join(ResourceSkill).filter(
            Resource.provider == 'YOUTUBE',
            Resource.is_active == True,
            Resource.verification_status == 'VERIFIED',
            ResourceSkill.skill_id == skill_id,
            Resource.updated_at >= cutoff_date # Consider freshness of the cache record itself
        ).all()
        
        if len(cached) >= self.min_cache_results:
            return True, cached
        return False, cached
        
    def get_existing_urls(self) -> set:
        """
        Returns a set of all known canonical URLs to prevent duplicate inserts 
        and skip redundant processing during the deduplication phase.
        """
        urls = self.db.query(Resource.canonical_url).filter(Resource.canonical_url != None).all()
        return set([u[0] for u in urls if u[0]])
