import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from agents.coach import extract_coach_intent
from api.recommendations import RecommendationRequest, build_skill_recommendations
from llm import get_llm
from routers.progress import update_skill_progress
from routers.path import PathGenerationRequest, generate_path
from services.recommendations.project_generator import ProjectGenerator
from services.youtube.youtube_orchestrator import YouTubeDiscoveryOrchestrator


class RecommendationIntent(str, Enum):
    LEARNING_PATH = "LEARNING_PATH"
    SKILL_RECOMMENDATION = "SKILL_RECOMMENDATION"
    COURSE_RECOMMENDATION = "COURSE_RECOMMENDATION"
    PROJECT_RECOMMENDATION = "PROJECT_RECOMMENDATION"
    RESOURCE_RECOMMENDATION = "RESOURCE_RECOMMENDATION"
    YOUTUBE_RECOMMENDATION = "YOUTUBE_RECOMMENDATION"
    PROFILE_UPDATE = "PROFILE_UPDATE"
    GENERAL_EXPLORATION = "GENERAL_EXPLORATION"


class StructuredRecommendationRequest(BaseModel):
    intents: List[RecommendationIntent] = Field(default_factory=list)
    target_goal: Optional[str] = None
    current_skills: List[str] = Field(default_factory=list)
    target_skills: List[str] = Field(default_factory=list)
    learner_level: str = "INTERMEDIATE"
    budget: str = "FREE"
    time_commitment: Optional[str] = None
    preferences: List[str] = Field(default_factory=list)


class UnifiedRecommendationState(TypedDict, total=False):
    original_query: str
    user_id: Optional[int]
    existing_profile: Dict[str, Any]
    extracted_profile: Dict[str, Any]
    intents: List[str]
    requested_engines: List[str]
    current_skills: List[str]
    target_goal: str
    target_skills: List[str]
    constraints: Dict[str, Any]
    recommendation_results: Dict[str, Any]
    path_result: Optional[Dict[str, Any]]
    course_result: Optional[Dict[str, Any]]
    resource_result: Optional[Dict[str, Any]]
    youtube_result: Optional[Dict[str, Any]]
    project_result: Optional[Dict[str, Any]]
    final_response: str
    errors: List[str]
    warnings: List[str]
    db: Session
    current_user: Optional[models.User]


ANALYZER_PROMPT = """You analyze SkillRoute learning requests.
Return structured data only. Use only these intents:
LEARNING_PATH, SKILL_RECOMMENDATION, COURSE_RECOMMENDATION,
PROJECT_RECOMMENDATION, RESOURCE_RECOMMENDATION, YOUTUBE_RECOMMENDATION,
PROFILE_UPDATE, GENERAL_EXPLORATION.

Choose multiple intents when useful. Extract goal, current skills, budget,
time commitment, learner level, and preferences. Do not recommend resources.
"""


FORMATTER_PROMPT = """You are formatting grounded SkillRoute recommendation results.
Use only the supplied engine outputs. Do not invent courses, videos, projects,
skills, scores, or URLs. If an engine returned nothing, say that plainly.
Keep the answer concise and useful."""


def _model_dump(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return dict(model)


def _safe_jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {k: _safe_jsonable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_safe_jsonable(v) for v in value]
        return str(value)


def _fallback_analyze(query: str, existing_profile: Dict[str, Any]) -> StructuredRecommendationRequest:
    text = query.lower()
    intents: List[RecommendationIntent] = []

    if any(word in text for word in ["roadmap", "path", "route", "learn", "become"]):
        intents.append(RecommendationIntent.LEARNING_PATH)
    if any(word in text for word in ["course", "coursera", "udemy"]):
        intents.append(RecommendationIntent.COURSE_RECOMMENDATION)
    if any(word in text for word in ["project", "build", "portfolio"]):
        intents.append(RecommendationIntent.PROJECT_RECOMMENDATION)
    if any(word in text for word in ["youtube", "video", "tutorial"]):
        intents.append(RecommendationIntent.YOUTUBE_RECOMMENDATION)
    if any(word in text for word in ["resource", "documentation", "docs", "practice"]):
        intents.append(RecommendationIntent.RESOURCE_RECOMMENDATION)
    if any(word in text for word in ["i know", "completed", "budget", "hours", "week"]):
        intents.append(RecommendationIntent.PROFILE_UPDATE)
    if not intents:
        intents.append(RecommendationIntent.GENERAL_EXPLORATION)

    goal = existing_profile.get("target_goal")
    match = re.search(r"(?:become|learn|roadmap for|path for|route for)\s+(.+?)(?:\s+in\s+\d|\s+with\s+|$)", query, re.I)
    if match:
        goal = match.group(1).strip(" .")

    skills = list(existing_profile.get("current_skills") or [])
    know_match = re.search(r"i know\s+(.+?)(?:\.|,?\s+and\s+i want|$)", query, re.I)
    if know_match:
        raw = re.split(r",| and ", know_match.group(1))
        skills = [s.strip() for s in raw if s.strip()]

    budget = existing_profile.get("budget") or "FREE"
    if "paid" in text:
        budget = "PAID"
    elif any(word in text for word in ["free", "no budget"]):
        budget = "FREE"

    return StructuredRecommendationRequest(
        intents=intents,
        target_goal=goal,
        current_skills=skills,
        learner_level=existing_profile.get("learner_level") or "INTERMEDIATE",
        budget=budget,
        time_commitment=existing_profile.get("time_commitment"),
    )


class UnifiedRecommendationGraph:
    def __init__(self, db: Session, current_user: Optional[models.User] = None):
        self.db = db
        self.current_user = current_user
        self.graph = self._build_graph()

    async def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        initial_state: UnifiedRecommendationState = {
            "original_query": query,
            "user_id": self.current_user.id if self.current_user else None,
            "existing_profile": context or {},
            "extracted_profile": {},
            "intents": [],
            "requested_engines": [],
            "constraints": {},
            "recommendation_results": {},
            "path_result": None,
            "course_result": None,
            "resource_result": None,
            "youtube_result": None,
            "project_result": None,
            "final_response": "",
            "errors": [],
            "warnings": [],
            "db": self.db,
            "current_user": self.current_user,
        }
        final_state = await self.graph.ainvoke(initial_state)
        return self._public_response(final_state)

    def _build_graph(self):
        builder = StateGraph(UnifiedRecommendationState)
        builder.add_node("load_user_context", self._load_user_context)
        builder.add_node("query_analyzer", self._query_analyzer)
        builder.add_node("deterministic_router", self._deterministic_router)
        builder.add_node("profile_update_node", self._profile_update_node)
        builder.add_node("path_recommender_node", self._path_recommender_node)
        builder.add_node("resource_recommender_node", self._resource_recommender_node)
        builder.add_node("project_recommender_node", self._project_recommender_node)
        builder.add_node("youtube_recommender_node", self._youtube_recommender_node)
        builder.add_node("result_aggregator", self._result_aggregator)
        builder.add_node("response_formatter", self._response_formatter)

        builder.add_edge(START, "load_user_context")
        builder.add_edge("load_user_context", "query_analyzer")
        builder.add_edge("query_analyzer", "deterministic_router")
        builder.add_conditional_edges(
            "deterministic_router",
            self._route_after_router,
            {
                "profile_update": "profile_update_node",
                "path": "path_recommender_node",
                "resources": "resource_recommender_node",
                "project": "project_recommender_node",
                "youtube": "youtube_recommender_node",
                "aggregate": "result_aggregator",
            },
        )
        builder.add_edge("profile_update_node", "path_recommender_node")
        builder.add_edge("path_recommender_node", "resource_recommender_node")
        builder.add_edge("resource_recommender_node", "project_recommender_node")
        builder.add_edge("project_recommender_node", "youtube_recommender_node")
        builder.add_edge("youtube_recommender_node", "result_aggregator")
        builder.add_edge("result_aggregator", "response_formatter")
        builder.add_edge("response_formatter", END)
        return builder.compile()

    def _load_user_context(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        profile_data = dict(state.get("existing_profile") or {})
        current_user = state.get("current_user")
        if current_user:
            profile = self.db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
            if profile:
                profile_data = {
                    **profile_data,
                    "target_goal": profile_data.get("target_goal") or profile.target_goal,
                    "budget": profile_data.get("budget") or profile.budget,
                    "time_commitment": profile_data.get("time_commitment") or profile.time_commitment,
                    "deadline": profile_data.get("deadline") or profile.deadline,
                    "current_skills": profile_data.get("current_skills") or [
                        learner_skill.skill.name
                        for learner_skill in profile.passports
                        if learner_skill.skill and learner_skill.confidence_score > 70
                    ],
                }
        return {"existing_profile": profile_data}

    def _query_analyzer(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        query = state["original_query"]
        existing_profile = state.get("existing_profile") or {}
        try:
            llm = get_llm()
            structured_llm = llm.with_structured_output(StructuredRecommendationRequest)
            result = structured_llm.invoke([
                SystemMessage(content=ANALYZER_PROMPT),
                HumanMessage(content=f"Existing profile/context: {json.dumps(existing_profile)}\n\nUser query: {query}"),
            ])
        except Exception as exc:
            result = _fallback_analyze(query, existing_profile)
            return {
                **self._analyzer_update(result),
                "warnings": state.get("warnings", []) + [f"LLM analyzer fallback used: {exc}"],
            }
        return self._analyzer_update(result)

    def _analyzer_update(self, result: StructuredRecommendationRequest) -> Dict[str, Any]:
        extracted = _model_dump(result)
        intents = [intent.value if isinstance(intent, RecommendationIntent) else str(intent) for intent in result.intents]
        return {
            "extracted_profile": extracted,
            "intents": intents,
            "target_goal": result.target_goal or "Generative AI",
            "target_skills": result.target_skills,
            "current_skills": result.current_skills,
            "constraints": {
                "budget": result.budget or "FREE",
                "time_commitment": result.time_commitment,
                "learner_level": result.learner_level or "INTERMEDIATE",
                "preferences": result.preferences,
            },
        }

    def _deterministic_router(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        intents = set(state.get("intents") or [])
        engines: List[str] = []
        if RecommendationIntent.PROFILE_UPDATE.value in intents:
            engines.append("profile_update")
        if intents & {
            RecommendationIntent.LEARNING_PATH.value,
            RecommendationIntent.SKILL_RECOMMENDATION.value,
            RecommendationIntent.GENERAL_EXPLORATION.value,
        }:
            engines.append("path")
        if intents & {
            RecommendationIntent.COURSE_RECOMMENDATION.value,
            RecommendationIntent.RESOURCE_RECOMMENDATION.value,
            RecommendationIntent.SKILL_RECOMMENDATION.value,
        }:
            engines.append("resources")
        if RecommendationIntent.PROJECT_RECOMMENDATION.value in intents:
            engines.append("project")
        if RecommendationIntent.YOUTUBE_RECOMMENDATION.value in intents:
            engines.append("youtube")

        if not engines:
            engines = ["path"]
        return {"requested_engines": engines}

    def _route_after_router(self, state: UnifiedRecommendationState) -> str:
        engines = state.get("requested_engines") or []
        if "profile_update" in engines:
            return "profile_update"
        if "path" in engines:
            return "path"
        if "resources" in engines:
            return "resources"
        if "project" in engines:
            return "project"
        if "youtube" in engines:
            return "youtube"
        return "aggregate"

    def _profile_update_node(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        if "profile_update" not in state.get("requested_engines", []):
            return {}
        try:
            intent_data = extract_coach_intent(state["original_query"])
            self._apply_profile_update(intent_data, state.get("current_user"))
            return {"recommendation_results": {**state.get("recommendation_results", {}), "profile_update": intent_data}}
        except Exception as exc:
            return {"warnings": state.get("warnings", []) + [f"Profile update intent failed: {exc}"]}

    def _path_recommender_node(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        if "path" not in state.get("requested_engines", []):
            return {}
        try:
            request = PathGenerationRequest(
                target_skill_name=state.get("target_goal") or "Generative AI",
                current_skills=state.get("current_skills") or [],
                completed_skill_ids=[],
                learner_level=state.get("constraints", {}).get("learner_level") or "INTERMEDIATE",
            )
            result = generate_path(request, self.db, state.get("current_user"))
            return {"path_result": _safe_jsonable(result)}
        except Exception as exc:
            return {"errors": state.get("errors", []) + [f"Path engine failed: {exc}"]}

    async def _resource_recommender_node(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        if "resources" not in state.get("requested_engines", []):
            return {}
        skill_id = self._select_skill_id(state)
        if not skill_id:
            return {"warnings": state.get("warnings", []) + ["Resource engine skipped: no skill_id available."]}
        try:
            req = RecommendationRequest(
                skill_id=skill_id,
                learner_level=state.get("constraints", {}).get("learner_level") or "INTERMEDIATE",
                goal=state.get("target_goal") or "General learning",
                budget=state.get("constraints", {}).get("budget") or "FREE",
            )
            result = await build_skill_recommendations(req, self.db, include_project=False)
            return {
                "course_result": {"courses": result.get("courses", [])},
                "resource_result": {
                    "practice": result.get("practice", []),
                    "read": result.get("read", []),
                },
            }
        except Exception as exc:
            return {"errors": state.get("errors", []) + [f"Resource engine failed: {exc}"]}

    def _project_recommender_node(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        if "project" not in state.get("requested_engines", []):
            return {}
        skill_id = self._select_skill_id(state)
        if not skill_id:
            return {"warnings": state.get("warnings", []) + ["Project engine skipped: no skill_id available."]}
        try:
            skill = self.db.query(models.Skill).filter(models.Skill.id == skill_id).first()
            if not skill:
                return {"warnings": state.get("warnings", []) + ["Project engine skipped: skill not found."]}
            project = ProjectGenerator().generate_project(
                skill.name,
                state.get("constraints", {}).get("learner_level") or "INTERMEDIATE",
                state.get("target_goal") or "General learning",
            )
            return {"project_result": _safe_jsonable(project)}
        except Exception as exc:
            return {"errors": state.get("errors", []) + [f"Project engine failed: {exc}"]}

    async def _youtube_recommender_node(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        if "youtube" not in state.get("requested_engines", []):
            return {}
        skill_id = self._select_skill_id(state)
        if not skill_id:
            return {"warnings": state.get("warnings", []) + ["YouTube engine skipped: no skill_id available."]}
        try:
            orchestrator = YouTubeDiscoveryOrchestrator(self.db)
            result = await orchestrator.discover(
                skill_id=skill_id,
                learner_level=state.get("constraints", {}).get("learner_level") or "INTERMEDIATE",
                goal=state.get("target_goal") or "General learning",
                constraints={"budget": state.get("constraints", {}).get("budget") or "FREE"},
                is_struggling=False,
            )
            return {"youtube_result": _safe_jsonable(result)}
        except Exception as exc:
            return {"errors": state.get("errors", []) + [f"YouTube engine failed: {exc}"]}

    def _result_aggregator(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        results = dict(state.get("recommendation_results") or {})
        if state.get("path_result"):
            results["path"] = state["path_result"]
        if state.get("course_result"):
            results["courses"] = state["course_result"]
        if state.get("resource_result"):
            results["resources"] = state["resource_result"]
        if state.get("project_result"):
            results["project"] = state["project_result"]
        if state.get("youtube_result"):
            results["youtube"] = state["youtube_result"]
        return {"recommendation_results": _safe_jsonable(results)}

    def _response_formatter(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        payload = {
            "query": state["original_query"],
            "profile": state.get("extracted_profile", {}),
            "engines_used": state.get("requested_engines", []),
            "results": state.get("recommendation_results", {}),
            "warnings": state.get("warnings", []),
            "errors": state.get("errors", []),
        }
        try:
            llm = get_llm(temperature=0.2)
            response = llm.invoke([
                SystemMessage(content=FORMATTER_PROMPT),
                HumanMessage(content=json.dumps(payload, default=str)),
            ])
            final = response.content.strip()
        except Exception:
            final = self._fallback_format(state)
        return {"final_response": final}

    def _fallback_format(self, state: UnifiedRecommendationState) -> str:
        results = state.get("recommendation_results") or {}
        parts = [f"I found recommendations for {state.get('target_goal', 'your goal')} using: {', '.join(state.get('requested_engines', []))}."]
        if "path" in results:
            skills = results["path"].get("skills", [])
            next_skills = [s["name"] for s in skills if s.get("status") == "NEXT"][:3]
            if next_skills:
                parts.append("Next skills: " + ", ".join(next_skills) + ".")
        if "courses" in results:
            courses = results["courses"].get("courses", [])
            parts.append(f"Courses found: {len(courses)}.")
        if "project" in results and results["project"]:
            parts.append(f"Project: {results['project'].get('title')}.")
        if "youtube" in results:
            videos = results["youtube"].get("resources", [])
            parts.append(f"YouTube tutorials found: {len(videos)}.")
        if state.get("errors"):
            parts.append("Some engines could not complete: " + "; ".join(state["errors"]))
        return " ".join(parts)

    def _select_skill_id(self, state: UnifiedRecommendationState) -> Optional[int]:
        path = state.get("path_result") or {}
        for skill in path.get("skills", []):
            if skill.get("status") == "NEXT":
                return skill.get("id")
        target = path.get("target") or {}
        if target.get("id"):
            return target["id"]
        target_goal = state.get("target_goal")
        if target_goal:
            skill = self.db.query(models.Skill).filter(models.Skill.name.ilike(target_goal)).first()
            if skill:
                return skill.id
        return None

    def _apply_profile_update(self, intent_data: Dict[str, Any], current_user: Optional[models.User]) -> None:
        if not current_user:
            return
        intent = intent_data.get("intent")
        params = intent_data.get("parameters", {}) or {}
        if intent in {"MARK_SKILL_COMPLETED", "MARK_SKILL_INCOMPLETE"}:
            skill_name = params.get("skill_name")
            if not skill_name:
                return
            skill = self.db.query(models.Skill).filter(models.Skill.name.ilike(skill_name)).first()
            if not skill:
                return
            status = "COMPLETED" if intent == "MARK_SKILL_COMPLETED" else "INCOMPLETE"
            update_skill_progress(self.db, current_user.id, skill.id, status)
            return
        if intent in {"UPDATE_BUDGET", "UPDATE_TIME"}:
            profile = self.db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
            if not profile:
                return
            if intent == "UPDATE_BUDGET":
                profile.budget = params.get("budget", "FREE").upper()
            else:
                profile.time_commitment = params.get("time_commitment")
            self.db.commit()

    def _public_response(self, state: UnifiedRecommendationState) -> Dict[str, Any]:
        return {
            "detected_intents": state.get("intents", []),
            "engines_used": state.get("requested_engines", []),
            "structured_request": {
                "target_goal": state.get("target_goal"),
                "current_skills": state.get("current_skills", []),
                "target_skills": state.get("target_skills", []),
                "constraints": state.get("constraints", {}),
            },
            "recommendation_results": state.get("recommendation_results", {}),
            "final_response": state.get("final_response", ""),
            "warnings": state.get("warnings", []),
            "errors": state.get("errors", []),
        }
