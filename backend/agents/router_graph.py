import re
from typing import Literal, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

import models
from agents.profiler import extract_profile_logic
from llm import get_llm
from schemas import LearnerProfile, ProfilerResponse


class IntentClassification(BaseModel):
    intent: Literal["GOAL_DIRECTED", "BROAD_EXPLORATION", "SPECIFIC_LOOKUP"] = Field(
        description=(
            "GOAL_DIRECTED: user wants a personalized path toward a career, role, "
            "goal, or end-to-end plan. BROAD_EXPLORATION: user asks what topics, "
            "subtopics, or prerequisites exist under a subject. SPECIFIC_LOOKUP: "
            "user asks a direct factual question about one skill/topic."
        )
    )
    subject: Optional[str] = Field(default=None, description="Core subject or skill name, if present.")


class RouterState(TypedDict):
    message: str
    history: list
    db: Session
    intent: Optional[str]
    subject: Optional[str]
    result: Optional[dict]
    warnings: list[str]


def _dump_model(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return dict(model)


def _fallback_classify(message: str) -> IntentClassification:
    text = message.lower()
    subject = _extract_subject(message)
    if any(phrase in text for phrase in ["what topics", "topics in", "topics are", "subtopics", "what's in", "what is in", "show me"]):
        return IntentClassification(intent="BROAD_EXPLORATION", subject=subject)
    if any(phrase in text for phrase in ["what is", "what are", "used for", "explain", "define"]):
        return IntentClassification(intent="SPECIFIC_LOOKUP", subject=subject)
    return IntentClassification(intent="GOAL_DIRECTED", subject=subject)


def _extract_subject(message: str) -> Optional[str]:
    patterns = [
        r"(?:topics|subtopics)\s+(?:are\s+)?(?:in|under|for)\s+(.+)",
        r"what(?:'s| is)\s+in\s+(.+)",
        r"what\s+(?:is|are)\s+(.+?)(?:\s+used\s+for|\?|$)",
        r"explain\s+(.+)",
        r"(?:become|learn|roadmap for|path for|route for)\s+(.+?)(?:\s+in\s+\d|\s+with\s+|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.I)
        if match:
            return match.group(1).strip(" ?.!")
    return None


def classify_intent_node(state: RouterState) -> RouterState:
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(IntentClassification)
        result = structured_llm.invoke([
            SystemMessage(content="Classify the user's learning-related request."),
            HumanMessage(content=state["message"]),
        ])
    except Exception as exc:
        result = _fallback_classify(state["message"])
        state["warnings"].append(f"Intent classifier fallback used: {exc}")

    state["intent"] = result.intent
    state["subject"] = result.subject
    return state


def route_by_intent(state: RouterState) -> str:
    return state["intent"] or "GOAL_DIRECTED"


def full_profiler_node(state: RouterState) -> RouterState:
    try:
        response = extract_profile_logic(user_message=state["message"], chat_history=state["history"])
    except Exception as exc:
        state["warnings"].append(f"Profiler fallback used: {exc}")
        response = ProfilerResponse(
            profile=LearnerProfile(target_goal=state["subject"], current_skills=[]),
            follow_up_question="What skills do you already have for this goal?",
            is_complete=False,
        )

    state["result"] = {
        "type": "GOAL_DIRECTED",
        "data": _dump_model(response),
        "warnings": state["warnings"],
    }
    return state


def topic_overview_node(state: RouterState) -> RouterState:
    db = state["db"]
    subject = state["subject"] or state["message"]
    skill = _find_skill(db, subject)

    topics = []
    if skill:
        relationships = db.query(models.SkillPrerequisite).filter(
            or_(
                models.SkillPrerequisite.skill_id == skill.id,
                models.SkillPrerequisite.prerequisite_id == skill.id,
            )
        ).all()
        related_ids = {rel.skill_id for rel in relationships} | {rel.prerequisite_id for rel in relationships}
        related_ids.discard(skill.id)
        if related_ids:
            topics = [s.name for s in db.query(models.Skill).filter(models.Skill.id.in_(related_ids)).all()]

    state["result"] = {
        "type": "BROAD_EXPLORATION",
        "subject": skill.name if skill else subject,
        "topics": topics,
        "warnings": state["warnings"],
    }
    return state


def direct_answer_node(state: RouterState) -> RouterState:
    db = state["db"]
    subject = state["subject"] or state["message"]
    skill = _find_skill(db, subject)
    context = skill.description if skill and skill.description else "No specific record found in the SkillRoute database."

    try:
        llm = get_llm()
        answer = llm.invoke([
            SystemMessage(content=f"Answer using only this SkillRoute database context: {context}"),
            HumanMessage(content=state["message"]),
        ]).content
    except Exception as exc:
        state["warnings"].append(f"Direct answer fallback used: {exc}")
        answer = context

    state["result"] = {
        "type": "SPECIFIC_LOOKUP",
        "subject": skill.name if skill else subject,
        "answer": answer,
        "warnings": state["warnings"],
    }
    return state


def _find_skill(db: Session, subject: str):
    cleaned = subject.strip()
    skill = db.query(models.Skill).filter(models.Skill.name.ilike(cleaned)).first()
    if skill:
        return skill
    return db.query(models.Skill).filter(models.Skill.name.ilike(f"%{cleaned}%")).first()


def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify", classify_intent_node)
    graph.add_node("full_profiler", full_profiler_node)
    graph.add_node("topic_overview", topic_overview_node)
    graph.add_node("direct_answer", direct_answer_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route_by_intent, {
        "GOAL_DIRECTED": "full_profiler",
        "BROAD_EXPLORATION": "topic_overview",
        "SPECIFIC_LOOKUP": "direct_answer",
    })
    graph.add_edge("full_profiler", END)
    graph.add_edge("topic_overview", END)
    graph.add_edge("direct_answer", END)
    return graph.compile()


router_graph = build_router_graph()
