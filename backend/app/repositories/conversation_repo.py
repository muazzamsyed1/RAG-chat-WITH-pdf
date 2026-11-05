from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.conversation import Conversation, Message, MessageRole


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id_and_user(
        self,
        conversation_id: str,
        user_id: str,
        load_messages: bool = False,
    ) -> Optional[Conversation]:
        q = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        if load_messages:
            q = q.options(selectinload(Conversation.messages))
        result = await self.db.execute(q)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> List[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self, user_id: str, title: Optional[str] = None
    ) -> Conversation:
        convo = Conversation(user_id=user_id, title=title)
        self.db.add(convo)
        await self.db.flush()
        await self.db.refresh(convo)
        return convo

    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id, role=role, content=content
        )
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def delete(self, conversation: Conversation) -> None:
        await self.db.delete(conversation)
        await self.db.flush()
