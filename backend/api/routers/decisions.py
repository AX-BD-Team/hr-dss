"""의사결정 API 라우터"""

import uuid
from datetime import UTC, datetime
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


class DecisionAnalyzeRequest(BaseModel):
    """의사결정 분석 요청"""

    agent_type: str | None = Field(default=None, description="사용할 에이전트 타입")


class DecisionApproveRequest(BaseModel):
    """의사결정 승인 요청"""

    option_id: str = Field(..., description="선택된 옵션 ID")
    comment: str | None = Field(default=None, description="승인 코멘트")


# In-memory 저장소 (프로토타입용)
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

    # 최신순 정렬
    decisions.sort(key=lambda x: x.updated_at, reverse=True)

    return {
        "total": len(decisions),
        "limit": limit,
        "offset": offset,
        "items": decisions[offset : offset + limit],
    }


@router.post("", response_model=Decision)
async def create_decision(request: DecisionCreate):
    """의사결정 생성"""
    decision_id = str(uuid.uuid4())
    now = datetime.now(UTC)

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


@router.delete("/{decision_id}")
async def delete_decision(decision_id: str):
    """의사결정 삭제"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")

    del _decisions[decision_id]
    return {"status": "deleted", "id": decision_id}


@router.post("/{decision_id}/analyze")
async def analyze_decision(decision_id: str, request: DecisionAnalyzeRequest | None = None):
    """의사결정 분석 실행"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")

    decision = _decisions[decision_id]
    decision.status = "analyzing"
    decision.updated_at = datetime.now(UTC)

    # TODO: 실제 분석 에이전트 호출
    # Mock 옵션 생성
    decision.options = [
        {
            "id": "opt-1",
            "type": "internal",
            "name": "내부 역량 활용",
            "description": "기존 인력으로 프로젝트 수행",
            "success_probability": 0.75,
            "cost": 50000000,
            "risk": "medium",
        },
        {
            "id": "opt-2",
            "type": "hybrid",
            "name": "혼합 수행",
            "description": "내부 + 외부 협력사 혼합",
            "success_probability": 0.85,
            "cost": 80000000,
            "risk": "low",
        },
        {
            "id": "opt-3",
            "type": "external",
            "name": "외부 위탁",
            "description": "전문 협력사에 위탁",
            "success_probability": 0.90,
            "cost": 120000000,
            "risk": "low",
        },
    ]
    decision.status = "analyzed"
    decision.updated_at = datetime.now(UTC)

    return {
        "status": "analyzed",
        "message": "분석이 완료되었습니다",
        "options_count": len(decision.options),
    }


@router.post("/{decision_id}/approve")
async def approve_decision(decision_id: str, request: DecisionApproveRequest):
    """의사결정 승인"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")

    decision = _decisions[decision_id]

    if decision.status != "analyzed":
        raise HTTPException(status_code=400, detail="분석이 완료된 의사결정만 승인할 수 있습니다")

    decision.status = "approved"
    decision.selected_option = request.option_id
    decision.updated_at = datetime.now(UTC)

    return {
        "status": "approved",
        "selected_option": request.option_id,
        "comment": request.comment,
    }


@router.post("/{decision_id}/reject")
async def reject_decision(decision_id: str, reason: str | None = None):
    """의사결정 반려"""
    if decision_id not in _decisions:
        raise HTTPException(status_code=404, detail="의사결정을 찾을 수 없습니다")

    decision = _decisions[decision_id]
    decision.status = "rejected"
    decision.updated_at = datetime.now(UTC)

    return {"status": "rejected", "reason": reason}
