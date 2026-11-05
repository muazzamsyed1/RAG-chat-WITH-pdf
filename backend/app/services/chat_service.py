from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.document_repo import DocumentRepository
from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation, MessageRole
from app.rag.pipeline import answer_query
from app.schemas.chat import ChatRequest, ChatResponse


class ChatService:
    def __init__(self, db: AsyncSession):
        self.convo_repo = ConversationRepository(db)
        self.doc_repo = DocumentRepository(db)

    async def chat(self, user_id: str, request: ChatRequest) -> ChatResponse:
        # Validate document ownership if a specific document is requested
        if request.document_id:
            doc = await self.doc_repo.get_by_id_and_user(
                request.document_id, user_id
            )
            if not doc:
                raise NotFoundError("Document")

        # Get or create conversation
        if request.conversation_id:
            convo = await self.convo_repo.get_by_id_and_user(
                request.conversation_id, user_id, load_messages=True
            )
            if not convo:
                raise NotFoundError("Conversation")
        else:
            title = request.query[:80] + ("..." if len(request.query) > 80 else "")
            convo = await self.convo_repo.create(user_id=user_id, title=title)
            convo.messages = []

        # Build history for context
        history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in (convo.messages or [])
        ]

        # Store user message
        await self.convo_repo.add_message(
            conversation_id=convo.id,
            role=MessageRole.USER,
            content=request.query,
        )

        # Run user-scoped RAG pipeline
        answer, sources = answer_query(
            user_id=user_id,
            query=request.query,
            document_id=request.document_id,
            conversation_history=history,
        )

        # Store assistant response
        await self.convo_repo.add_message(
            conversation_id=convo.id,
            role=MessageRole.ASSISTANT,
            content=answer,
        )

        return ChatResponse(
            conversation_id=convo.id,
            answer=answer,
            sources=sources,
        )

    async def list_conversations(self, user_id: str) -> List[Conversation]:
        return await self.convo_repo.list_by_user(user_id)

    async def get_conversation(
        self, conversation_id: str, user_id: str
    ) -> Conversation:
        convo = await self.convo_repo.get_by_id_and_user(
            conversation_id, user_id, load_messages=True
        )
        if not convo:
            raise NotFoundError("Conversation")
        return convo

    async def delete_conversation(
        self, conversation_id: str, user_id: str
    ) -> None:
        convo = await self.convo_repo.get_by_id_and_user(
            conversation_id, user_id
        )
        if not convo:
            raise NotFoundError("Conversation")
        await self.convo_repo.delete(convo)
