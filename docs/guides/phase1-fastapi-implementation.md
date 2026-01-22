# Phase 1: FastAPI 라우터 구현 가이드

> 마지막 업데이트: 2025-01-22
> 예상 소요: 4-6시간

---

## 1. 개요

### 1.1 현재 상태
- `backend/agent_runtime/` - 6개 에이전트 구현 완료
- `backend/database/` - 모델 정의 완료
- `backend/api/` - **미구현** ❌

### 1.2 목표
Backend API 서버를 구현하여 Railway 배포 가능 상태로 만들기

### 1.3 필요한 엔드포인트

| 엔드포인트 | 메서드 | 설명 | 우선순위 |
|------------|--------|------|----------|
| `/health` | GET | 헬스 체크 | 🔴 P0 |
| `/api` | GET | API 정보 | 🔴 P0 |
| `/api/v1/agents/query` | POST | 에이전트 쿼리 실행 | 🔴 P0 |
| `/api/v1/decisions` | GET/POST | 의사결정 목록/생성 | 🟡 P1 |
| `/api/v1/decisions/{id}` | GET | 의사결정 상세 | 🟡 P1 |
| `/api/v1/graph/query` | POST | KG 쿼리 | 🟡 P1 |
| `/api/v1/graph/nodes` | GET | 노드 목록 | 🟢 P2 |

---

## 2. 디렉토리 구조

```
backend/
├── __init__.py              # 기존
├── api/                     # 🆕 신규 생성
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 설정
│   ├── dependencies.py      # 공통 의존성
│   └── routers/
│       ├── __init__.py
│       ├── health.py        # 헬스 체크
│       ├── agents.py        # 에이전트 API
│       ├── decisions.py     # 의사결정 API
│       └── graph.py         # KG API
├── agent_runtime/           # 기존
└── database/                # 기존
```

---

## 3. 구현 코드

### 3.1 `backend/api/__init__.py`

```python
"""HR-DSS Backend API"""
```

### 3.2 `backend/api/config.py`

```python
"""API 설정"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 환경
    environment: str = "development"
    debug: bool = False

    # 서버
    host: str = "0.0.0.0"
    port: int = 8000

    # 데이터베이스
    database_url: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    # AI
    anthropic_api_key: str = ""

    # 보안
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

### 3.3 `backend/api/main.py`

```python
"""
HR-DSS Backend API

FastAPI 기반 REST API 서버
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.config import settings
from backend.api.routers import health, agents, decisions, graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    print(f"🚀 HR-DSS API 시작 (환경: {settings.environment})")
    yield
    # Shutdown
    print("👋 HR-DSS API 종료")


app = FastAPI(
    title="HR-DSS API",
    description="HR 의사결정 지원 시스템 API",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(decisions.router, prefix="/api/v1/decisions", tags=["Decisions"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["Graph"])


@app.get("/api")
async def api_info():
    """API 정보"""
    return {
        "name": "HR-DSS API",
        "version": "0.2.0",
        "environment": settings.environment,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "agents": "/api/v1/agents",
            "decisions": "/api/v1/decisions",
            "graph": "/api/v1/graph",
        },
    }


def main():
    """CLI 진입점"""
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
```

### 3.4 `backend/api/dependencies.py`

```python
"""공통 의존성"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> dict | None:
    """현재 사용자 조회 (선택적 인증)"""
    if credentials is None:
        return None
    # TODO: JWT 검증 구현
    return {"sub": "anonymous", "role": "user"}


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
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
```

### 3.5 `backend/api/routers/__init__.py`

```python
"""API 라우터"""
from backend.api.routers import health, agents, decisions, graph

__all__ = ["health", "agents", "decisions", "graph"]
```

### 3.6 `backend/api/routers/health.py`

```python
"""헬스 체크 라우터"""
from datetime import datetime

from fastapi import APIRouter

from backend.api.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "hr-dss-api",
        "version": "0.2.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """준비 상태 체크"""
    # TODO: DB 연결 상태 확인
    checks = {
        "database": "ok",  # TODO: 실제 확인
        "neo4j": "ok",  # TODO: 실제 확인
    }
    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": checks,
    }
```

### 3.7 `backend/api/routers/agents.py`

```python
"""에이전트 API 라우터"""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class QueryRequest(BaseModel):
    """쿼리 요청"""

    question: str = Field(..., description="자연어 질문")
    context: dict[str, Any] | None = Field(default=None, description="추가 컨텍스트")
    options: dict[str, Any] | None = Field(default=None, description="실행 옵션")


class QueryResponse(BaseModel):
    """쿼리 응답"""

    request_id: str
    status: str
    result: dict[str, Any] | None = None
    error: str | None = None


@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    에이전트 쿼리 실행

    자연어 질문을 받아 적절한 에이전트를 호출하고 결과를 반환합니다.
    """
    import uuid

    request_id = str(uuid.uuid4())

    try:
        # TODO: 실제 에이전트 호출 구현
        # from backend.agent_runtime.agents import query_decomposition
        # result = await query_decomposition.process(request.question)

        return QueryResponse(
            request_id=request_id,
            status="success",
            result={
                "question": request.question,
                "decomposed": {
                    "goal": "분석 목표",
                    "constraints": ["제약조건1", "제약조건2"],
                    "period": "12주",
                },
                "message": "쿼리 분해 완료 (Mock 응답)",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_agent_types():
    """사용 가능한 에이전트 타입 목록"""
    return {
        "agents": [
            {
                "id": "query-decomposition",
                "name": "쿼리 분해",
                "description": "자연어 질문을 목표/제약/기간으로 분해",
            },
            {
                "id": "option-generator",
                "name": "옵션 생성",
                "description": "의사결정을 위한 대안 3개 생성",
            },
            {
                "id": "impact-simulator",
                "name": "영향 시뮬레이터",
                "description": "As-Is vs To-Be 가동률 시뮬레이션",
            },
            {
                "id": "success-probability",
                "name": "성공 확률",
                "description": "휴리스틱+모델 기반 성공확률 산출",
            },
            {
                "id": "validator",
                "name": "검증기",
                "description": "근거 연결 검증 및 환각 탐지",
            },
            {
                "id": "workflow-builder",
                "name": "워크플로우 빌더",
                "description": "실행 계획 및 Workflow 생성",
            },
        ]
    }
```

### 3.8 `backend/api/routers/decisions.py`

```python
"""의사결정 API 라우터"""
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class Decision(BaseModel):
    """의사결정"""

    id: str
    title: str
    status: str
    question: str
    options: list[dict[str, Any]] | None = None
    selected_option: str | None = None
    created_at: datetime
    updated_at: datetime


class DecisionCreate(BaseModel):
    """의사결정 생성 요청"""

    title: str = Field(..., description="의사결정 제목")
    question: str = Field(..., description="의사결정 질문")


# Mock 데이터
_decisions: dict[str, Decision] = {}


@router.get("")
async def list_decisions(
    status: str | None = Query(None, description="상태 필터"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """의사결정 목록 조회"""
    decisions = list(_decisions.values())

    if status:
        decisions = [d for d in decisions if d.status == status]

    return {
        "total": len(decisions),
        "limit": limit,
        "offset": offset,
        "items": decisions[offset : offset + limit],
    }


@router.post("", response_model=Decision)
async def create_decision(request: DecisionCreate):
    """의사결정 생성"""
    import uuid

    decision_id = str(uuid.uuid4())
    now = datetime.utcnow()

    decision = Decision(
        id=decision_id,
        title=request.title,
        question=request.question,
        status="pending",
        options=None,
        selected_option=None,
        created_at=now,
        updated_at=now,
    )

    _decisions[decision_id] = decision
    return decision


@router.get("/{decision_id}", response_model=Decision)
async def get_decision(decision_id: str):
    """의사결정 상세 조회"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")
    return _decisions[decision_id]


@router.post("/{decision_id}/analyze")
async def analyze_decision(decision_id: str):
    """의사결정 분석 실행"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")

    decision = _decisions[decision_id]
    decision.status = "analyzing"
    decision.updated_at = datetime.utcnow()

    # TODO: 실제 분석 에이전트 호출
    return {"status": "analyzing", "message": "분석이 시작되었습니다"}


@router.post("/{decision_id}/approve")
async def approve_decision(decision_id: str, option_id: str):
    """의사결정 승인"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")

    decision = _decisions[decision_id]
    decision.status = "approved"
    decision.selected_option = option_id
    decision.updated_at = datetime.utcnow()

    return {"status": "approved", "selected_option": option_id}
```

### 3.9 `backend/api/routers/graph.py`

```python
"""Knowledge Graph API 라우터"""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class GraphQuery(BaseModel):
    """그래프 쿼리"""

    cypher: str = Field(..., description="Cypher 쿼리")
    params: dict[str, Any] | None = Field(default=None, description="쿼리 파라미터")


class GraphQueryResult(BaseModel):
    """그래프 쿼리 결과"""

    success: bool
    data: list[dict[str, Any]]
    meta: dict[str, Any] | None = None


@router.post("/query", response_model=GraphQueryResult)
async def execute_query(request: GraphQuery):
    """
    Cypher 쿼리 실행

    Neo4j Knowledge Graph에 Cypher 쿼리를 실행합니다.
    """
    try:
        # TODO: 실제 Neo4j 연결 구현
        # from backend.agent_runtime.ontology.kg_query import KGQueryEngine
        # engine = KGQueryEngine()
        # result = await engine.execute(request.cypher, request.params)

        return GraphQueryResult(
            success=True,
            data=[
                {"message": "Mock 응답 - Neo4j 연결 필요"},
                {"query": request.cypher},
            ],
            meta={"execution_time_ms": 0},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes")
async def list_node_types():
    """노드 타입 목록"""
    return {
        "node_types": [
            {"label": "Employee", "count": 0, "description": "직원"},
            {"label": "Team", "count": 0, "description": "팀"},
            {"label": "Project", "count": 0, "description": "프로젝트"},
            {"label": "Skill", "count": 0, "description": "스킬"},
            {"label": "Decision", "count": 0, "description": "의사결정"},
        ]
    }


@router.get("/schema")
async def get_schema():
    """그래프 스키마 조회"""
    return {
        "nodes": [
            "Employee",
            "Team",
            "Division",
            "Project",
            "Skill",
            "Decision",
            "Option",
            "Evidence",
        ],
        "relationships": [
            "BELONGS_TO",
            "MANAGES",
            "ASSIGNED_TO",
            "HAS_SKILL",
            "REQUIRES_SKILL",
            "SUPPORTS",
            "CONTRADICTS",
        ],
    }


@router.get("/stats")
async def get_stats():
    """그래프 통계"""
    # TODO: 실제 통계 조회
    return {
        "node_count": 0,
        "relationship_count": 0,
        "labels": {},
        "relationship_types": {},
    }
```

---

## 4. 테스트

### 4.1 테스트 파일 생성

`tests/test_api.py`:

```python
"""API 테스트"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_info():
    """API 정보 테스트"""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "HR-DSS API"


def test_agent_types():
    """에이전트 타입 목록 테스트"""
    response = client.get("/api/v1/agents/types")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) >= 6


def test_create_decision():
    """의사결정 생성 테스트"""
    response = client.post(
        "/api/v1/decisions",
        json={"title": "테스트 의사결정", "question": "테스트 질문"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "테스트 의사결정"
    assert data["status"] == "pending"
```

### 4.2 테스트 실행

```bash
# 테스트 실행
pytest tests/test_api.py -v

# 커버리지 포함
pytest tests/test_api.py -v --cov=backend.api
```

---

## 5. 로컬 실행

### 5.1 직접 실행

```bash
# 개발 모드
uvicorn backend.api.main:app --reload --port 8000

# 또는 CLI
python -m backend.api.main
```

### 5.2 Docker 실행

```bash
# 빌드
docker build -t hr-dss-api .

# 실행
docker run -p 8000:8000 hr-dss-api
```

### 5.3 docker-compose 실행

```bash
docker-compose up -d api
```

---

## 6. 검증 체크리스트

- [ ] `backend/api/` 디렉토리 생성
- [ ] `main.py` 구현
- [ ] `config.py` 구현
- [ ] `dependencies.py` 구현
- [ ] `routers/health.py` 구현
- [ ] `routers/agents.py` 구현
- [ ] `routers/decisions.py` 구현
- [ ] `routers/graph.py` 구현
- [ ] `/health` 엔드포인트 동작 확인
- [ ] `/api` 엔드포인트 동작 확인
- [ ] pytest 테스트 통과
- [ ] Docker 빌드 성공
- [ ] docker-compose 실행 성공

---

## 7. 다음 단계

코드 구현 완료 후:
1. Phase 2: 인프라 설정 진행
2. Phase 3: 배포 및 검증
