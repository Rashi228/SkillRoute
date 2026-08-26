from pydantic import BaseModel
from typing import List
from llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class SearchQueries(BaseModel):
    queries: List[str]

DISCOVERY_SYSTEM_PROMPT = """
You are an AI Resource Discovery orchestrator.
Your job is to take a Target Skill and a set of Constraints and generate highly optimized YouTube search queries to find the best educational content.
Generate exactly 2 unique search queries.
Example for Skill "RAG" and Constraint "Advanced": 
["Advanced Retrieval Augmented Generation Python tutorial", "Build complex RAG application guide"]
"""

def generate_search_queries(skill_name: str, constraints: str) -> List[str]:
    llm = get_llm()
    structured_llm = llm.with_structured_output(SearchQueries)
    
    messages = [
        SystemMessage(content=DISCOVERY_SYSTEM_PROMPT),
        HumanMessage(content=f"Skill: {skill_name}\nConstraints: {constraints}")
    ]
    
    response: SearchQueries = structured_llm.invoke(messages)
    return response.queries
