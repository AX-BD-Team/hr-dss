"""
HR-DSS Backend API

FastAPI 기반 REST API 서버
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.config import settings
from backend.api.routers import agents, decisions, graph, health


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
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
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
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    main()
