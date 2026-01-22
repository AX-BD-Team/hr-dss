"""공통 의존성"""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.api.config import settings

security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """JWT 토큰 페이로드"""

    sub: str  # 사용자 ID
    role: str = "user"
    exp: datetime | None = None


class TokenPayload(BaseModel):
    """토큰 생성용 페이로드"""

    sub: str
    role: str = "user"


def create_access_token(data: TokenPayload, expires_delta: timedelta | None = None) -> str:
    """액세스 토큰 생성"""
    to_encode = data.model_dump()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> TokenData:
    """JWT 토큰 검증 및 디코딩"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        sub: str | None = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(
            sub=sub,
            role=payload.get("role", "user"),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=UTC),
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 검증 실패: {e!s}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenData | None:
    """현재 사용자 조회 (선택적 인증)"""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> TokenData:
    """인증 필수"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(credentials.credentials)
