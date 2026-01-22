# HR-DSS Backend Dockerfile
# Python 3.11 기반 FastAPI 애플리케이션

FROM python:3.11-slim AS base

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Builder 단계
# ----------------------------
FROM base AS builder

# 의존성 파일 복사 및 설치 (README.md는 hatchling 빌드에 필요)
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && \
    pip install hatchling && \
    pip install .

# ----------------------------
# Development 단계
# ----------------------------
FROM base AS development

# 개발 의존성 포함 설치 (README.md는 hatchling 빌드에 필요)
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

COPY . .

# 개발 서버 실행
EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ----------------------------
# Production 단계
# ----------------------------
FROM base AS production

# 런타임 전용 의존성 설치 (README.md는 hatchling 빌드에 필요)
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && \
    pip install .

# 애플리케이션 코드 복사
COPY backend/ ./backend/
COPY data/ ./data/

# 비루트 사용자 생성
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 프로덕션 서버 실행
EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
