from typing import Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db_config import db_manager, Token, async_session_scope


security = HTTPBearer()


async def verify_token(token: str, role: str) -> Union[Token, None]:
    """Verify user token from database
    Args:
        token (str): 검증할 토큰 문자열
    returns:
        Token: 데이터베이스의 토큰 객체 또는 None
    """
    session_factory = db_manager.get_session_factory()
    async with async_session_scope(session_factory) as session:
        query = select(Token).where(Token.token == token, Token.is_active == True, Token.role == role)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def verify_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user token and verify from database
    Args:
        credentials (HTTPAuthorizationCredentials): FastAPI의 사용자 인증 정보
    returns:
        Token: 데이터베이스의 토큰 객체
    """
    token = credentials.credentials
    if await verify_token(token, "user") or await verify_token(token, "admin"):
        return token
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


def verify_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token
    Args:
        credentials (HTTPAuthorizationCredentials): FastAPI의 사용자 인증 정보
    returns:
        str: 어드민 토큰
    """
    token = credentials.credentials
    if not verify_token(token, "admin"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token")
    return token


class TokenManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_token(self, user_id: str) -> Token:
        new_token = Token(token=self.generate_token(), user_id=user_id, is_active=True)  # user_id 저장
        self.session.add(new_token)
        await self.session.commit()
        await self.session.refresh(new_token)
        return new_token

    async def deactivate_token(self, token: str) -> bool:
        query = select(Token).where(Token.token == token)
        result = await self.session.execute(query)
        db_token = result.scalar_one_or_none()

        if db_token:
            db_token.is_active = False
            await self.session.commit()
            return True
        return False

    @staticmethod
    def generate_token() -> str:
        import secrets

        return secrets.token_urlsafe(32)
