from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import get_db
from app.core.security import decode_token
from app.repositories.user_repo import UserRepository
from app.models.user import User

bearerScheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearerScheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT, load and return the authenticated user."""
    payload = decode_token(credentials.credentials, expected_type="access")
    user_id: str = payload.get("sub")
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
