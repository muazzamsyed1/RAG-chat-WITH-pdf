import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config.settings import get_settings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a configured Gemini Embeddings instance."""
    settings = get_settings()
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    return GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL)
