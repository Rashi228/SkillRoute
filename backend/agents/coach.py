import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

logger = logging.getLogger(__name__)

# Initialize Groq LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

try:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama3-8b-8192",
        temperature=0.1
    )
except Exception as e:
    logger.error(f"Failed to init ChatGroq: {e}")
    llm = None

coach_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI Learning Coach helping a user modify their learning path.
You must output ONLY valid JSON.

Determine the user's intent from their message.
Possible intents:
UPDATE_BUDGET (params: budget = 'FREE' or 'PAID')
UPDATE_TIME (params: time_commitment = string)
MARK_SKILL_COMPLETED (params: skill_name = string)
MARK_SKILL_INCOMPLETE (params: skill_name = string)
SKIP_SKILL (params: skill_name = string)
REQUEST_DEEP_ROUTE (no params)
REQUEST_FAST_ROUTE (no params)
REPLAN_PATH (no params)
CONVERSATIONAL (for normal chat, params: None)

If the user says "I know Docker" -> MARK_SKILL_COMPLETED, skill_name="Docker"
If the user says "I don't know Docker anymore" -> MARK_SKILL_INCOMPLETE, skill_name="Docker"
If the user says "I want paid courses" -> UPDATE_BUDGET, budget="PAID"
If the user says "I only have 5 hours a week" -> UPDATE_TIME, time_commitment="5 hours per week"

Output format:
{{
    "intent": "INTENT_NAME",
    "parameters": {{
        // appropriate parameters based on intent
    }},
    "reply": "A brief conversational reply acknowledging the change or answering the question."
}}
"""),
    ("user", "{message}")
])

def extract_coach_intent(user_message: str):
    if not llm:
        return {"intent": "CONVERSATIONAL", "parameters": {}, "reply": "LLM not configured."}
        
    chain = coach_prompt | llm
    response = chain.invoke({"message": user_message})
    
    content = response.content.strip()
    # Strip markdown code blocks if present
    if content.startswith("```json"):
        content = content.replace("```json", "", 1).strip()
    if content.endswith("```"):
        content = content[:-3].strip()
        
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON from Coach LLM: {content}")
        return {"intent": "CONVERSATIONAL", "parameters": {}, "reply": "I'm having trouble understanding that right now."}
