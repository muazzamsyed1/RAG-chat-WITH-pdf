import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Optional
from app.config.settings import get_settings
from app.rag.embeddings import get_embeddings

COLLECTION_NAME = "rag_documents"


def get_chroma_client() -> chromadb.PersistentClient:
    settings = get_settings()
    return chromadb.PersistentClient(
        path=str(settings.chroma_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_vector_store() -> Chroma:
    """Return the shared persistent Chroma vector store."""
    client = get_chroma_client()
    embeddings = get_embeddings()
    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )


def add_documents_for_user(
    user_id: str, document_id: str, chunks: List[Document]
) -> int:
    """
    Add document chunks to ChromaDB with user_id and document_id metadata.
    Every chunk is tagged with ownership so queries can be user-scoped.
    """
    store = get_vector_store()
    for chunk in chunks:
        chunk.metadata["user_id"] = user_id
        chunk.metadata["document_id"] = document_id
    store.add_documents(documents=chunks)
    return len(chunks)


def search_for_user(
    user_id: str,
    query: str,
    k: int = 4,
    document_id: Optional[str] = None,
) -> List[Document]:
    """
    Similarity search STRICTLY filtered by user_id.
    User A's query can NEVER return User B's documents.
    """
    store = get_vector_store()

    if document_id:
        where_filter = {
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"document_id": {"$eq": document_id}},
            ]
        }
    else:
        where_filter = {"user_id": {"$eq": user_id}}

    return store.similarity_search(
        query=query,
        k=k,
        filter=where_filter,
    )


def delete_documents_for_user(user_id: str, document_id: str) -> None:
    """Delete all chunks belonging to a specific document and user."""
    client = get_chroma_client()
    collection = client.get_or_create_collection(COLLECTION_NAME)
    collection.delete(
        where={
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"document_id": {"$eq": document_id}},
            ]
        }
    )
