from typing import TypedDict, Sequence, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
from llm import get_llm
from schemas import LearnerProfile, ProfilerResponse

# System Prompt
PROFILER_SYSTEM_PROMPT = """
You are an AI Learning Coach for the Adaptive Learning Navigator.
Your goal is to extract the user's learning profile from the conversation.
You need to identify:
1. target_goal: What do they want to achieve? (e.g. Become a GenAI Engineer)
2. current_skills: What do they already know? (e.g. Python, basic ML)
3. budget: What is their budget? (Free, Paid, specific amount)
4. time_commitment: How much time can they study? (e.g. 8 hours per week)
5. deadline: When do they want to achieve this?

IMPORTANT RULES:
- ONLY ask about MISSING data. Do NOT ask for information the user has already provided! For example, if they provided a timeline or duration, DO NOT ask about their available time.
- If essential information like 'target_goal' or 'current_skills' is missing, set is_complete to false and provide a natural, conversational 'follow_up_question' to ask the user exclusively about what is missing.
- If everything seems clear enough to build a basic path, set is_complete to true.
"""

def extract_profile_logic(user_message: str, chat_history: list = None) -> ProfilerResponse:
    llm = get_llm()
    structured_llm = llm.with_structured_output(ProfilerResponse)
    
    messages = [SystemMessage(content=PROFILER_SYSTEM_PROMPT)]
    if chat_history:
        for msg in chat_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "ai":
                messages.append(AIMessage(content=msg.get("content", "")))
        
    messages.append(HumanMessage(content=user_message))
    
    response: ProfilerResponse = structured_llm.invoke(messages)
    return response
