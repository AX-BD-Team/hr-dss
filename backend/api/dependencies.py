"""공통 의존성"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict | None:
    """현재 사용자 조회 (선택적 인증)"""
    if credentials is None:
        return None
    # TODO: JWT 검증 구현
    return {"sub": "anonymous", "role": "user"}


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict:
    """인증 필수"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # TODO: JWT 검증 구현
    return {"sub": "authenticated", "role": "user"}
