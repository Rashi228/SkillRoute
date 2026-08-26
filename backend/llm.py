import os
from groq import Groq
from langchain_groq import ChatGroq
from config import settings

# Direct Groq Client (for simple API calls)
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

# LangChain Groq Chat Model (for LangGraph)
def get_llm(model_name="llama3-8b-8192", temperature=0):
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY, 
        model_name=model_name,
        temperature=temperature
    )
