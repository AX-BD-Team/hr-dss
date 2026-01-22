"""헬스 체크 라우터"""

from datetime import UTC, datetime

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
        "timestamp": datetime.now(UTC).isoformat(),
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
