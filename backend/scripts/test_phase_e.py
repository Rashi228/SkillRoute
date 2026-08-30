import os
import sys
import asyncio
from unittest.mock import patch
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator
from services.youtube.youtube_ranker import YouTubeRanker
from services.youtube.youtube_client import YouTubeClient
from models import Resource

async def test_phase_e():
    db = SessionLocal()
    orchestrator = YouTubeDiscoveryOrchestrator(db)
    
    print("\n--- TEST A: Normal successful YouTube discovery ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', return_value=(False, [])):
        res = await orchestrator.discover(102, "INTERMEDIATE", "Goal", {})
        print(f"Status: {res.get('status')} | Resources: {len(res.get('resources', []))}")
        assert res.get('status') == 'SUCCESS' or len(res.get('resources', [])) > 0
    
    # ---------------------------------------------------------
    print("\n--- TEST E: Normal cache hit ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', return_value=(True, [Resource(id=1, title="Cached 1", provider="YOUTUBE", url="http")])):
        res_cache = await orchestrator.discover(102, "INTERMEDIATE", "Goal", {})
        print(f"Status: {res_cache.get('status')} | Cache hits metric: {res_cache.get('metrics', {}).get('cache_hits')}")
        assert res_cache.get('status') == 'CACHE_HIT'
    
    # ---------------------------------------------------------
    print("\n--- TEST F: Struggling cache hit ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', side_effect=[(False, []), (True, [Resource(id=2, title="Cached 2", provider="YOUTUBE", url="http")])]):
        res_struggle_miss = await orchestrator.discover(102, "INTERMEDIATE", "Goal", {}, is_struggling=True)
        res_struggle_hit = await orchestrator.discover(102, "INTERMEDIATE", "Goal", {}, is_struggling=True)
        print(f"Status: {res_struggle_hit.get('status')}")
        assert res_struggle_hit.get('status') == 'CACHE_HIT'
    
    # ---------------------------------------------------------
    print("\n--- TEST B: YouTube API failure ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', return_value=(False, [])):
        with patch.object(YouTubeClient, 'search_videos', side_effect=RuntimeError("Simulated Quota Error")):
            res_fail = await orchestrator.discover(101, "INTERMEDIATE", "Goal", {})
            print(f"Status: {res_fail.get('status')} | Message: {res_fail.get('message')}")
            assert res_fail.get('status') == 'API_FAILED'
            
    # ---------------------------------------------------------
    print("\n--- TEST C: YouTube API returns zero videos ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', return_value=(False, [])):
        with patch.object(YouTubeClient, 'search_videos', return_value=[]):
            res_zero = await orchestrator.discover(100, "INTERMEDIATE", "Goal", {})
            print(f"Status: {res_zero.get('status')} | Message: {res_zero.get('message')}")
            assert res_zero.get('status') == 'DISCOVERY_UNAVAILABLE'
            
    # ---------------------------------------------------------
    print("\n--- TEST D: SemanticMatcher throws exception ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', return_value=(False, [])):
        with patch('services.skill_mapping.semantic_matcher.SemanticMatcher.embed_texts', side_effect=Exception("OOM Model crash")):
            res_fallback = await orchestrator.discover(99, "INTERMEDIATE", "Goal", {})
            print(f"Status: {res_fallback.get('status')} | Resources: {len(res_fallback.get('resources', []))}")
            
    # ---------------------------------------------------------
    print("\n--- TEST H: Invalid/malformed YouTube response ---")
    with patch('services.youtube.youtube_cache.YouTubeCache.check_cache', return_value=(False, [])):
        with patch.object(YouTubeClient, 'search_videos', return_value=[{"id": "invalid", "snippet": "missing things"}]):
            res_malformed = await orchestrator.discover(98, "INTERMEDIATE", "Goal", {})
            print(f"Status: {res_malformed.get('status')} | Resources: {len(res_malformed.get('resources', []))}")
        
    db.close()
    print("\n--- All Tests Passed ---")

if __name__ == "__main__":
    asyncio.run(test_phase_e())
