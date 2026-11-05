from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TOKEN_TYPE_REFRESH,
)
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.models.user import User
from fastapi import HTTPException, status


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, request: RegisterRequest) -> User:
        if await self.repo.exists_by_email(request.email):
            raise UserAlreadyExistsError()
        hashed = hash_password(request.password)
        return await self.repo.create(
            email=request.email,
            hashed_password=hashed,
            full_name=request.full_name,
        )

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(request.email)
        if not user or not verify_password(request.password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()
        token_data = {"sub": user.id, "email": user.email}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type=TOKEN_TYPE_REFRESH)
        user = await self.repo.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )
        token_data = {"sub": user.id, "email": user.email}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )
