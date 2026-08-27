import os
import json
import re
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings

class ProjectGenerator:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = os.environ.get("GROQ_SEARCH_MODEL", "openai/gpt-oss-20b")
        if self.api_key:
            self.llm = ChatGroq(model=self.model_name, temperature=0.7, api_key=self.api_key)
        else:
            self.llm = None
            
    def generate_project(self, skill_name: str, learner_level: str, goal: str) -> Optional[Dict[str, Any]]:
        """
        Generates a project recommendation using Groq, avoiding external URLs.
        Returns a structured dictionary.
        """
        if not self.llm:
            return self._fallback_project(skill_name)
            
        sys_msg = SystemMessage(content=(
            "You are a Project Recommendation AI. Given a tech skill, learner level, and target career goal, "
            "generate ONE practical, highly relevant project idea. "
            "Do NOT include any external URLs, links, or hallucinated websites. "
            "Output ONLY a valid JSON object matching exactly this schema:\n"
            '{\n'
            '  "title": "Build a Semantic Search Engine",\n'
            '  "difficulty": "Intermediate",\n'
            '  "estimated_hours": 6,\n'
            '  "skills": ["Python", "Embeddings", "Vector Search"],\n'
            '  "description": "A short 2 sentence description.",\n'
            '  "tutorial_search_intent": "semantic search engine build tutorial"\n'
            '}\n'
            "The tutorial_search_intent should be an optimal YouTube search query to find a build tutorial for this exact project."
        ))
        
        human_msg = HumanMessage(content=(
            f"Skill: {skill_name}\n"
            f"Learner Level: {learner_level}\n"
            f"Target Goal: {goal}\n"
        ))
        
        try:
            response = self.llm.invoke([sys_msg, human_msg])
            text = response.content
            
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
            return self._fallback_project(skill_name)
            
        except Exception as e:
            print(f"Error calling Groq for project generation: {e}")
            return self._fallback_project(skill_name)
            
    def _fallback_project(self, skill_name: str) -> Dict[str, Any]:
        return {
            "title": f"Build a {skill_name} Application",
            "difficulty": "Beginner",
            "estimated_hours": 4,
            "skills": [skill_name],
            "description": f"A practical starter project to solidify your understanding of {skill_name}.",
            "tutorial_search_intent": f"{skill_name} project build tutorial"
        }
