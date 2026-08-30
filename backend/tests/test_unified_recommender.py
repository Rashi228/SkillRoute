import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch

from database import Base
from models import Skill
from services.orchestration.langgraph_recommender import UnifiedRecommendationGraph


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add(Skill(name="Python", description="Programming language"))
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
@patch("services.orchestration.langgraph_recommender.get_llm", side_effect=ValueError("LLM unavailable"))
@patch(
    "services.orchestration.langgraph_recommender.ProjectGenerator.generate_project",
    return_value={"title": "Build a Python Application"},
)
@patch(
    "services.orchestration.langgraph_recommender.build_skill_recommendations",
    new_callable=AsyncMock,
)
async def test_unified_graph_routes_to_path_resources_and_project(mock_recommendations, mock_project, mock_llm, db):
    mock_recommendations.return_value = {
        "status": "SUCCESS",
        "skill_name": "Python",
        "practice": [{"platform": "Exercism", "match_percentage": 100}],
        "read": [{"title": "Python Official Documentation", "match_percentage": 97}],
        "project": None,
        "courses": [{"title": "Python Basics", "match_percentage": 92}],
    }

    graph = UnifiedRecommendationGraph(db=db)
    result = await graph.run(
        query="Give me a roadmap for Python with courses and projects",
        context={"budget": "FREE", "current_skills": []},
    )

    assert result["structured_request"]["target_goal"] == "Python"
    assert "LEARNING_PATH" in result["detected_intents"]
    assert "COURSE_RECOMMENDATION" in result["detected_intents"]
    assert "PROJECT_RECOMMENDATION" in result["detected_intents"]
    assert result["engines_used"] == ["path", "resources", "project"]
    assert result["recommendation_results"]["path"]["target"]["name"] == "Python"
    assert result["recommendation_results"]["courses"]["courses"][0]["title"] == "Python Basics"
    assert result["recommendation_results"]["project"]["title"] == "Build a Python Application"
    assert "using: path, resources, project" in result["final_response"]
