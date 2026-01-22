"""공통 의존성"""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from backend.api.config import settings

# Neo4j 드라이버
try:
    from neo4j import AsyncDriver, AsyncGraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    AsyncDriver = Any  # type: ignore[misc,assignment]

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


# =============================================================================
# Neo4j 연결 서비스
# =============================================================================


class Neo4jService:
    """Neo4j 데이터베이스 서비스"""

    _driver: AsyncDriver | None = None

    @classmethod
    async def get_driver(cls) -> AsyncDriver | None:
        """Neo4j 드라이버 반환 (싱글톤)"""
        if not NEO4J_AVAILABLE:
            return None

        if cls._driver is None and settings.neo4j_uri:
            cls._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return cls._driver

    @classmethod
    async def close(cls) -> None:
        """드라이버 연결 종료"""
        if cls._driver:
            await cls._driver.close()
            cls._driver = None

    @classmethod
    async def execute_query(
        cls,
        query: str,
        params: dict | None = None,
        database: str = "neo4j",
    ) -> list[dict]:
        """Cypher 쿼리 실행"""
        driver = await cls.get_driver()
        if not driver:
            raise HTTPException(
                status_code=503,
                detail="Neo4j 서비스를 사용할 수 없습니다",
            )

        async with driver.session(database=database) as session:
            result = await session.run(query, params or {})
            records = await result.data()
            return records

    @classmethod
    async def get_stats(cls) -> dict:
        """그래프 통계 조회"""
        driver = await cls.get_driver()
        if not driver:
            return {
                "node_count": 0,
                "relationship_count": 0,
                "labels": {},
                "relationship_types": {},
            }

        try:
            # 노드 수
            node_count_query = "MATCH (n) RETURN count(n) as count"
            node_result = await cls.execute_query(node_count_query)
            node_count = node_result[0]["count"] if node_result else 0

            # 관계 수
            rel_count_query = "MATCH ()-[r]->() RETURN count(r) as count"
            rel_result = await cls.execute_query(rel_count_query)
            rel_count = rel_result[0]["count"] if rel_result else 0

            # 라벨별 노드 수
            labels_query = "CALL db.labels() YIELD label RETURN label"
            labels_result = await cls.execute_query(labels_query)
            labels = {}
            for record in labels_result:
                label = record["label"]
                count_query = f"MATCH (n:`{label}`) RETURN count(n) as count"
                count_result = await cls.execute_query(count_query)
                labels[label] = count_result[0]["count"] if count_result else 0

            # 관계 타입별 수
            rel_types_query = (
                "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
            )
            rel_types_result = await cls.execute_query(rel_types_query)
            rel_types = {}
            for record in rel_types_result:
                rel_type = record["relationshipType"]
                count_query = f"MATCH ()-[r:`{rel_type}`]->() RETURN count(r) as count"
                count_result = await cls.execute_query(count_query)
                rel_types[rel_type] = count_result[0]["count"] if count_result else 0

            return {
                "node_count": node_count,
                "relationship_count": rel_count,
                "labels": labels,
                "relationship_types": rel_types,
            }
        except Exception:
            return {
                "node_count": 0,
                "relationship_count": 0,
                "labels": {},
                "relationship_types": {},
            }

    @classmethod
    async def search(
        cls,
        query: str,
        labels: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """그래프 검색"""
        driver = await cls.get_driver()
        if not driver:
            return []

        # 라벨 필터 구성
        if labels:
            label_filter = " OR ".join([f"n:`{label}`" for label in labels])
            cypher = f"""
            MATCH (n)
            WHERE ({label_filter})
              AND (
                any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $query)
              )
            RETURN labels(n) as labels, properties(n) as properties
            LIMIT $limit
            """
        else:
            cypher = """
            MATCH (n)
            WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $query)
            RETURN labels(n) as labels, properties(n) as properties
            LIMIT $limit
            """

        try:
            results = await cls.execute_query(cypher, {"query": query, "limit": limit})
            return results
        except Exception:
            return []


async def get_neo4j_service() -> Neo4jService:
    """Neo4j 서비스 의존성"""
    return Neo4jService()
