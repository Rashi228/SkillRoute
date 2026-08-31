import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from agents.router_graph import router_graph
from database import Base
from models import Skill, SkillPrerequisite
from schemas import LearnerProfile, ProfilerResponse


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
    python = Skill(name="Python", description="A programming language used for automation, data, and backend work.")
    fastapi = Skill(name="FastAPI", description="A Python web framework.")
    session.add_all([python, fastapi])
    session.commit()
    session.add(SkillPrerequisite(skill_id=fastapi.id, prerequisite_id=python.id))
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def run_router(message, db):
    state = {
        "message": message,
        "history": [],
        "db": db,
        "intent": None,
        "subject": None,
        "result": None,
        "warnings": [],
    }
    return router_graph.invoke(state)["result"]


@patch("agents.router_graph.get_llm", side_effect=ValueError("LLM unavailable"))
def test_chat_router_handles_broad_exploration(mock_llm, db):
    result = run_router("what topics are in FastAPI", db)

    assert result["type"] == "BROAD_EXPLORATION"
    assert result["subject"] == "FastAPI"
    assert result["topics"] == ["Python"]


@patch("agents.router_graph.get_llm", side_effect=ValueError("LLM unavailable"))
def test_chat_router_handles_specific_lookup(mock_llm, db):
    result = run_router("what is Python used for?", db)

    assert result["type"] == "SPECIFIC_LOOKUP"
    assert result["subject"] == "Python"
    assert "programming language" in result["answer"]


@patch("agents.router_graph.get_llm", side_effect=ValueError("LLM unavailable"))
@patch(
    "agents.router_graph.extract_profile_logic",
    return_value=ProfilerResponse(
        profile=LearnerProfile(target_goal="Backend Developer", current_skills=["Python"]),
        follow_up_question=None,
        is_complete=True,
    ),
)
def test_chat_router_preserves_goal_directed_profiler(mock_profiler, mock_llm, db):
    result = run_router("I want to become a backend developer", db)

    assert result["type"] == "GOAL_DIRECTED"
    assert result["data"]["is_complete"] is True
    assert result["data"]["profile"]["target_goal"] == "Backend Developer"
