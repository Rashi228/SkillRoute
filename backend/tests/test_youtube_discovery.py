import pytest
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import Skill, Resource, ResourceSkill
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator

# Setup in-memory SQLite DB for fast testing
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Seed a skill
    skill = Skill(name="RAG", description="Retrieval Augmented Generation", aliases='["Retrieval-Augmented Generation"]')
    session.add(skill)
    session.commit()
    session.refresh(skill)
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

def mock_youtube_client(*args, **kwargs):
    client = MagicMock()
    client.calls_made = 0
    client.search_videos.return_value = [
        {
            "id": "vid123",
            "snippet": {
                "title": "RAG Tutorial 2026",
                "description": "Learn RAG in Python",
                "channelTitle": "AI Channel",
                "publishedAt": "2026-01-01T00:00:00Z"
            },
            "statistics": {"viewCount": "1000"},
            "contentDetails": {"duration": "PT42M"}
        }
    ]
    return client

def mock_youtube_search(*args, **kwargs):
    search = MagicMock()
    search.calls_made = 1
    search.generate_queries.return_value = [{"query": "RAG python tutorial", "language": "en"}]
    return search
    
def mock_semantic_matcher(*args, **kwargs):
    matcher = MagicMock()
    matcher.threshold = 0.35
    # Embed texts mock (just return fake embeddings)
    # The ranker needs to compute cosine similarity, so we return real vectors
    # Actually, the ranker imports torch and computes it. Let's return valid dummy lists.
    def fake_embed(texts):
        return [[1.0] * 384 for _ in texts]
    matcher.embed_texts = fake_embed
    return matcher

class AsyncMockValidator:
    def __init__(self, *args, **kwargs):
        pass
    async def validate_urls(self, urls):
        return {url: True for url in urls}

@pytest.mark.asyncio
@patch('services.youtube.youtube_orchestrator.YouTubeClient', new=mock_youtube_client)
@patch('services.youtube.youtube_orchestrator.YouTubeSearchIntent', new=mock_youtube_search)
@patch('services.youtube.youtube_orchestrator.SemanticMatcher', new=mock_semantic_matcher)
@patch.object(YouTubeDiscoveryOrchestrator, '_validate_urls', new_callable=AsyncMock, return_value={"https://www.youtube.com/watch?v=vid123": True})
async def test_discovery_pipeline_cache_miss(mock_validate, db):
    """
    Test a full discovery pipeline on cache miss.
    """
    orchestrator = YouTubeDiscoveryOrchestrator(db)
    
    # Needs to be async
    res = await orchestrator.discover(skill_id=1, learner_level="INTERMEDIATE", goal="Test", constraints={})
    
    assert res["status"] == "DISCOVERED"
    assert res["metrics"]["cache_misses"] == 1
    assert res["metrics"]["cache_hits"] == 0
    assert len(res["resources"]) == 1
    assert res["resources"][0]["title"] == "RAG Tutorial 2026"
    assert res["resources"][0]["verified"] == True

@pytest.mark.asyncio
@patch('services.youtube.youtube_orchestrator.YouTubeClient', new=mock_youtube_client)
@patch('services.youtube.youtube_orchestrator.YouTubeSearchIntent', new=mock_youtube_search)
@patch('services.youtube.youtube_orchestrator.SemanticMatcher', new=mock_semantic_matcher)
@patch.object(YouTubeDiscoveryOrchestrator, '_validate_urls', new_callable=AsyncMock, return_value={})
async def test_discovery_pipeline_cache_hit(mock_validate, db):
    """
    Test cache hit bypasses Groq and YouTube API.
    """
    import datetime
    
    # Inject 5 fake resources into the cache to simulate a cache hit (YOUTUBE_MIN_CACHE_RESULTS=5)
    for i in range(5):
        r = Resource(
            title=f"Cached {i}", 
            provider="YOUTUBE", 
            external_id=f"cached_{i}",
            verification_status="VERIFIED",
            is_active=True,
            updated_at=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(r)
        db.flush()
        db.add(ResourceSkill(resource_id=r.id, skill_id=1, mapping_source="YOUTUBE_DISCOVERY"))
    db.commit()
    
    os.environ["YOUTUBE_MIN_CACHE_RESULTS"] = "5"
    orchestrator = YouTubeDiscoveryOrchestrator(db)
    
    res = await orchestrator.discover(skill_id=1, learner_level="INTERMEDIATE", goal="Test", constraints={})
    
    assert res["status"] == "CACHE_HIT"
    assert res["metrics"]["cache_hits"] == 1
    assert res["metrics"]["cache_misses"] == 0
    assert len(res["resources"]) == 5
    assert res["metrics"]["youtube_api_calls"] == 0
