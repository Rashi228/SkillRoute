import json
import os
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

class GroqDecision(BaseModel):
    decision: str = Field(description="Must be 'MAP' or 'REJECT'")
    skill_ids: List[int] = Field(description="List of skill IDs to map if decision is MAP")
    confidence: float = Field(description="Confidence of the mapping from 0.0 to 1.0")
    reason: str = Field(description="Short explanation for the decision")

class LLMResolver:
    def __init__(self):
        # Only initialize if the key is present, otherwise we can't use it.
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            self.llm = None
        else:
            self.llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0.0).with_structured_output(GroqDecision)
            
        self.calls_made = 0

    def resolve_ambiguity(self, resource_title: str, resource_description: str, candidates: List[Dict[str, Any]]) -> Optional[GroqDecision]:
        """
        Calls Groq to resolve ambiguous skill mappings.
        """
        if not self.llm:
            print("Warning: GROQ_API_KEY not set. Cannot resolve ambiguity. Defaulting to REJECT.")
            return None
            
        self.calls_made += 1
        
        # Prepare Candidates text
        candidates_text = ""
        for c in candidates:
            skill = c["skill"]
            candidates_text += f"- ID: {skill.id} | Name: {skill.name} | Description: {skill.description or 'None'}\n"
            
        sys_msg = SystemMessage(content=(
            "You are an expert AI Curriculum architect. Your job is to resolve ambiguous skill mappings for an educational resource. "
            "You will be given the resource title and description, and a list of candidate skills. "
            "Determine if the resource legitimately teaches or targets ANY of these skills. "
            "If YES, return decision='MAP' and the list of applicable skill IDs. "
            "If NO (false positive), return decision='REJECT' and an empty list of IDs. "
            "Only map if the skill is a core topic, not just a briefly mentioned concept."
        ))
        
        human_msg = HumanMessage(content=(
            f"Resource Title: {resource_title}\n"
            f"Resource Description: {resource_description[:1000]}...\n\n"
            f"Candidate Skills:\n{candidates_text}"
        ))
        
        try:
            decision = self.llm.invoke([sys_msg, human_msg])
            return decision
        except Exception as e:
            print(f"Error calling Groq: {e}")
            return None
