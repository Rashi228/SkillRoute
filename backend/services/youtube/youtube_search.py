import os
import json
import re
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings

class YouTubeSearchIntent:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = os.environ.get("GROQ_SEARCH_MODEL", "openai/gpt-oss-20b")
        self.max_queries = int(os.environ.get("YOUTUBE_MAX_SEARCH_QUERIES", "3"))
        
        if self.api_key:
            self.llm = ChatGroq(model=self.model_name, temperature=0.7, api_key=self.api_key)
        else:
            self.llm = None
            
        self.calls_made = 0
        
    def generate_queries(self, skill_name: str, aliases: List[str], learner_level: str, goal: str, constraints: Dict[str, Any], is_struggling: bool = False) -> List[Dict[str, str]]:
        """
        Generates optimized YouTube search queries using Groq.
        Forces exactly 1 English and 1 Hindi query unless a custom intent is provided.
        """
        custom_intent = constraints.get("search_intent")
        if custom_intent:
            return [
                {"query": f"{custom_intent} english", "language": "en"},
                {"query": f"{custom_intent} hindi", "language": "hi"}
            ]

        if not self.llm:
            return self._fallback_queries(skill_name, aliases, learner_level, is_struggling)
            
        self.calls_made += 1
        
        # Force strict deterministic structure rather than relying entirely on LLM JSON schema for the exact languages
        if is_struggling:
            queries = [
                {"query": f"{skill_name} beginner-friendly step-by-step intuitive explanation tutorial in english", "language": "en"},
                {"query": f"{skill_name} beginner-friendly step-by-step intuitive explanation tutorial in hindi", "language": "hi"}
            ]
        else:
            queries = [
                {"query": f"{skill_name} tutorial {learner_level} in english", "language": "en"},
                {"query": f"{skill_name} tutorial {learner_level} in hindi", "language": "hi"}
            ]
        return queries
            
    def _fallback_queries(self, skill_name: str, aliases: List[str], learner_level: str, is_struggling: bool = False) -> List[Dict[str, str]]:
        """
        Deterministic fallback queries if LLM fails.
        """
        if is_struggling:
            return [
                {"query": f"{skill_name} beginner-friendly fundamentals tutorial in english", "language": "en"},
                {"query": f"{skill_name} beginner-friendly fundamentals tutorial in hindi", "language": "hi"}
            ]
        return [
            {"query": f"{skill_name} tutorial {learner_level} in english", "language": "en"},
            {"query": f"{skill_name} tutorial {learner_level} in hindi", "language": "hi"}
        ]
