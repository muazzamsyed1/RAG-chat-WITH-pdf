from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, document_id: str) -> Optional[Document]:
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self, document_id: str, user_id: str
    ) -> Optional[Document]:
        """Ownership-enforced lookup. Never returns another user's document."""
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> List[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: str,
        original_name: str,
        stored_filename: str,
        file_size: int,
        mime_type: str,
    ) -> Document:
        doc = Document(
            user_id=user_id,
            original_name=original_name,
            stored_filename=stored_filename,
            file_size=file_size,
            mime_type=mime_type,
            status=DocumentStatus.PENDING,
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        chunk_count: int = 0,
        error_message: Optional[str] = None,
    ) -> None:
        doc = await self.get_by_id(document_id)
        if doc:
            doc.status = status
            doc.chunk_count = chunk_count
            if error_message:
                doc.error_message = error_message
            await self.db.flush()

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.flush()
