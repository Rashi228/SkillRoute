from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from llm import get_llm
from agents.profiler import extract_profile_logic
import models

class IntentClassification(BaseModel):
    intent: Literal["GOAL_DIRECTED", "BROAD_EXPLORATION", "SPECIFIC_LOOKUP"] = Field(
        description=(
            "GOAL_DIRECTED: user wants a full personalized path toward a career/role goal "
            "(mentions becoming something, a timeline, or asks to be guided end-to-end). "
            "BROAD_EXPLORATION: user just wants to see what topics/subtopics exist under a "
            "subject — no personalization needed, e.g. 'what's in Python', 'show me web dev topics'. "
            "SPECIFIC_LOOKUP: user is asking a direct factual question about one specific "
            "skill/topic, e.g. 'what is Docker used for'."
        )
    )
    subject: Optional[str] = Field(description="The core subject/skill name mentioned, if any")

class RouterState(TypedDict):
    message: str
    history: list
    db: object
    intent: Optional[str]
    subject: Optional[str]
    result: Optional[dict]

def classify_intent_node(state: RouterState) -> RouterState:
    llm = get_llm()
    structured_llm = llm.with_structured_output(IntentClassification)
    result = structured_llm.invoke([
        SystemMessage(content="Classify the user's learning-related request."),
        HumanMessage(content=state["message"]),
    ])
    state["intent"] = result.intent
    state["subject"] = result.subject
    return state

def route_by_intent(state: RouterState) -> str:
    return state["intent"]

def full_profiler_node(state: RouterState) -> RouterState:
    response = extract_profile_logic(user_message=state["message"], chat_history=state["history"])
    state["result"] = {"type": "GOAL_DIRECTED", "data": response.model_dump()}
    return state

def topic_overview_node(state: RouterState) -> RouterState:
    db: Session = state["db"]
    subject = state["subject"] or state["message"]
    skill = db.query(models.Skill).filter(models.Skill.name.ilike(f"%{subject}%")).first()
    topics = []
    if skill:
        related = db.query(models.SkillPrerequisite).filter(
            (models.SkillPrerequisite.skill_id == skill.id) |
            (models.SkillPrerequisite.prerequisite_id == skill.id)
        ).all()
        related_ids = {r.skill_id for r in related} | {r.prerequisite_id for r in related}
        related_ids.discard(skill.id)
        topics = [s.name for s in db.query(models.Skill).filter(models.Skill.id.in_(related_ids)).all()]
    state["result"] = {"type": "BROAD_EXPLORATION", "subject": subject, "topics": topics}
    return state

def direct_answer_node(state: RouterState) -> RouterState:
    db: Session = state["db"]
    subject = state["subject"] or state["message"]
    skill = db.query(models.Skill).filter(models.Skill.name.ilike(f"%{subject}%")).first()
    context = skill.description if (skill and skill.description) else "No specific record found in the database."
    llm = get_llm()
    answer = llm.invoke([
        SystemMessage(content=f"Answer the user's question using ONLY this context, concisely: {context}"),
        HumanMessage(content=state["message"]),
    ])
    state["result"] = {"type": "SPECIFIC_LOOKUP", "subject": subject, "answer": answer.content}
    return state

def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify", classify_intent_node)
    graph.add_node("full_profiler", full_profiler_node)
    graph.add_node("topic_overview", topic_overview_node)
    graph.add_node("direct_answer", direct_answer_node)
    graph.set_entry_point("classify")
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
