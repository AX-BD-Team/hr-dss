"""에이전트 API 라우터"""
import uuid
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
        raise HTTPException(status_code=500, detail=str(e)) from e


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


@router.get("/{agent_id}")
async def get_agent_info(agent_id: str):
    """에이전트 상세 정보"""
    agents = {
        "query-decomposition": {
            "id": "query-decomposition",
            "name": "쿼리 분해",
            "description": "자연어 질문을 목표/제약/기간으로 분해",
            "input_schema": {"question": "string", "context": "object"},
            "output_schema": {"goal": "string", "constraints": "array", "period": "string"},
        },
        "option-generator": {
            "id": "option-generator",
            "name": "옵션 생성",
            "description": "의사결정을 위한 대안 3개 생성",
            "input_schema": {"goal": "string", "constraints": "array"},
            "output_schema": {"options": "array"},
        },
    }

    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")

    return agents[agent_id]
