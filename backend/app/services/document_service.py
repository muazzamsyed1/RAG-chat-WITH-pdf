import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.document_repo import DocumentRepository
from app.core.exceptions import (
    NotFoundError,
    ForbiddenError,
    FileTooLargeError,
    InvalidFileTypeError,
    DocumentProcessingError,
)
from app.models.document import Document, DocumentStatus
from app.rag.pipeline import validate_file, safe_stored_filename, ingest_document
from app.rag.vector_store import delete_documents_for_user
from app.config.settings import get_settings
from typing import List

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    async def upload_and_ingest(
        self,
        user_id: str,
        file_content: bytes,
        original_name: str,
        content_type: str,
    ) -> Document:
        # Validate file
        try:
            validate_file(original_name, content_type, len(file_content))
        except ValueError as e:
            if "size" in str(e).lower():
                raise FileTooLargeError(max_mb=settings.MAX_UPLOAD_SIZE_MB)
            raise InvalidFileTypeError()

        # Store file with UUID filename (prevents path traversal)
        stored_name = safe_stored_filename(original_name)
        user_upload_dir = settings.upload_path / user_id
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_upload_dir / stored_name

        with open(file_path, "wb") as f:
            f.write(file_content)

        # Create DB record
        doc = await self.repo.create(
            user_id=user_id,
            original_name=original_name,
            stored_filename=stored_name,
            file_size=len(file_content),
            mime_type=content_type,
        )

        await self.repo.update_status(doc.id, DocumentStatus.PROCESSING)

        # Ingest into ChromaDB (user-scoped)
        chunk_count, error = ingest_document(
            file_path=str(file_path),
            user_id=user_id,
            document_id=doc.id,
        )

        if error:
            await self.repo.update_status(
                doc.id, DocumentStatus.FAILED, error_message=error
            )
            raise DocumentProcessingError(detail=error)

        await self.repo.update_status(
            doc.id, DocumentStatus.READY, chunk_count=chunk_count
        )
        await self.repo.db.refresh(doc)
        return doc

    async def list_documents(self, user_id: str) -> List[Document]:
        return await self.repo.list_by_user(user_id)

    async def delete_document(self, document_id: str, user_id: str) -> None:
        doc = await self.repo.get_by_id_and_user(document_id, user_id)
        if not doc:
            generic = await self.repo.get_by_id(document_id)
            if generic:
                raise ForbiddenError()
            raise NotFoundError("Document")

        file_path = settings.upload_path / user_id / doc.stored_filename
        if file_path.exists():
            file_path.unlink()

        try:
            delete_documents_for_user(user_id=user_id, document_id=document_id)
        except Exception as e:
            logger.warning(
                "Failed to delete vectors for doc %s: %s", document_id, e
            )

        await self.repo.delete(doc)
