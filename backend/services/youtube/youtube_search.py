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
        
    def generate_queries(self, skill_name: str, aliases: List[str], learner_level: str, goal: str, constraints: Dict[str, Any]) -> List[str]:
        """
        Generates optimized YouTube search queries using Groq, with deterministic fallback.
        """
        if not self.llm:
            return self._fallback_queries(skill_name, aliases, learner_level)
            
        self.calls_made += 1
        
        sys_msg = SystemMessage(content=(
            "You are a YouTube search query generator. "
            "Given a target tech skill, learner level, and goal, generate highly optimized YouTube search queries to find the best tutorials. "
            "IMPORTANT: Do NOT generate URLs, video IDs, or metadata. Output ONLY a valid JSON object matching this schema:\n"
            '{"queries": ["query1", "query2", "query3"]}\n'
            f"Generate maximum {self.max_queries} queries."
        ))
        
        human_msg = HumanMessage(content=(
            f"Skill: {skill_name}\n"
            f"Aliases: {', '.join(aliases)}\n"
            f"Learner Level: {learner_level}\n"
            f"Goal: {goal}\n"
            f"Constraints: {json.dumps(constraints)}\n"
        ))
        
        try:
            response = self.llm.invoke([sys_msg, human_msg])
            text = response.content
            
            # Extract JSON if the model added markdown blocks
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                queries = data.get("queries", [])
                
                # Sanitize: Reject queries containing URLs
                clean_queries = []
                for q in queries:
                    if "http" not in q and "youtube.com" not in q:
                        clean_queries.append(q)
                
                if clean_queries:
                    # Deduplicate safely, preserve order
                    seen = set()
                    final_queries = []
                    for q in clean_queries[:self.max_queries]:
                        q_lower = q.lower().strip()
                        if q_lower not in seen:
                            seen.add(q_lower)
                            final_queries.append(q)
                            
                    return final_queries
                    
            print("Groq generated malformed JSON. Using fallback.")
            return self._fallback_queries(skill_name, aliases, learner_level)
            
        except Exception as e:
            print(f"Error calling Groq for search intent: {e}")
            return self._fallback_queries(skill_name, aliases, learner_level)
            
    def _fallback_queries(self, skill_name: str, aliases: List[str], learner_level: str) -> List[str]:
        """
        Deterministic fallback queries if LLM fails.
        """
        queries = [
            f"{skill_name} tutorial {learner_level}",
            f"{skill_name} course"
        ]
        
        if aliases:
            queries.append(f"{aliases[0]} implementation")
            
        return queries[:self.max_queries]
