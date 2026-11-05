import uuid
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.rag.vector_store import add_documents_for_user, search_for_user
from app.rag.llm import get_llm
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}


def validate_file(filename: str, content_type: str, file_size: int) -> None:
    """Validate file type and size. Raises ValueError on failure."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension '{ext}' is not allowed. Only PDF files accepted.")
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"MIME type '{content_type}' is not allowed.")
    max_bytes = settings.max_upload_size_bytes
    if file_size > max_bytes:
        raise ValueError(
            f"File size {file_size} bytes exceeds max {max_bytes} bytes "
            f"({settings.MAX_UPLOAD_SIZE_MB} MB)."
        )


def safe_stored_filename(original_filename: str) -> str:
    """Generate UUID-based filename to prevent path traversal."""
    ext = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4()}{ext}"


def ingest_document(
    file_path: str, user_id: str, document_id: str
) -> Tuple[int, str]:
    """
    Load, split, embed, and store a PDF document.
    Returns (chunk_count, error_message). error_message is empty on success.
    Preserves original RAG logic from app.py (PyPDFLoader + RecursiveCharacterTextSplitter).
    """
    try:
        loader = PyPDFLoader(file_path)
        raw_docs: List[Document] = loader.load()

        if not raw_docs:
            return 0, "PDF appears to be empty or unreadable."

        # Preserved from original app.py: chunk_size=1000, chunk_overlap=200
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks: List[Document] = splitter.split_documents(raw_docs)

        if not chunks:
            return 0, "No text could be extracted from the PDF."

        count = add_documents_for_user(
            user_id=user_id,
            document_id=document_id,
            chunks=chunks,
        )

        logger.info(
            "Ingested doc %s for user %s: %d chunks", document_id, user_id, count
        )
        return count, ""

    except Exception as e:
        logger.error("Failed to ingest doc %s: %s", document_id, str(e))
        return 0, str(e)


def answer_query(
    user_id: str,
    query: str,
    document_id: Optional[str] = None,
    conversation_history: Optional[List[dict]] = None,
) -> Tuple[str, List[str]]:
    """
    RAG query: retrieve context from user's documents, generate answer.
    SECURITY: search_for_user enforces user_id filtering.
    User A cannot retrieve context from User B's documents.
    Returns (answer_text, source_snippets).
    """
    relevant_docs = search_for_user(
        user_id=user_id,
        query=query,
        k=4,
        document_id=document_id,
    )

    if not relevant_docs:
        return (
            "I couldn't find relevant information in your documents to answer this "
            "question. Please make sure you have uploaded a document first.",
            [],
        )

    context = "\n\n---\n\n".join(doc.page_content for doc in relevant_docs)

    history_text = ""
    if conversation_history:
        for msg in conversation_history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"

    system_prompt = (
        "You are a helpful AI assistant that answers questions based ONLY on the "
        "provided document context. If the answer is not in the context, say so. "
        "Do not make up information. Be concise and accurate."
    )

    history_section = (
        f"Previous conversation:\n{history_text}\n" if history_text else ""
    )

    user_prompt = (
        f"{system_prompt}\n\n"
        f"Document Context:\n{context}\n\n"
        f"{history_section}"
        f"User Question: {query}\n\nAnswer:"
    )

    llm = get_llm()
    response = llm.invoke(user_prompt)

    if hasattr(response, "content"):
        if isinstance(response.content, str):
            answer = response.content
        elif isinstance(response.content, list):
            answer = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in response.content
            )
        else:
            answer = str(response.content)
    else:
        answer = str(response)

    sources = [doc.page_content[:200] + "..." for doc in relevant_docs]
    return answer, sources
