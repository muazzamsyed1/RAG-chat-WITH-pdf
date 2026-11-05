from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.document_service import DocumentService
from app.schemas.document import DocumentResponse, DocumentListResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF. Validates, stores, and ingests into vector DB."""
    service = DocumentService(db)
    content = await file.read()
    return await service.upload_and_ingest(
        user_id=current_user.id,
        file_content=content,
        original_name=file.filename or "unnamed.pdf",
        content_type=file.content_type or "application/pdf",
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all documents belonging to the authenticated user only."""
    service = DocumentService(db)
    docs = await service.list_documents(current_user.id)
    return DocumentListResponse(documents=docs, total=len(docs))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document. Only the owner can delete their documents."""
    await DocumentService(db).delete_document(
        document_id=document_id,
        user_id=current_user.id,
    )
