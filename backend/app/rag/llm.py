import os
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import get_settings


def get_llm() -> ChatGoogleGenerativeAI:
    """Return a configured Gemini LLM instance."""
    settings = get_settings()
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_LLM_MODEL,
        temperature=0.3,
        max_retries=2,
    )
