#!/bin/sh
# Railway/Docker entrypoint script
# PORT 환경변수가 없으면 기본값 8000 사용

PORT=${PORT:-8000}
echo "Starting uvicorn on port $PORT"
exec uvicorn backend.api.main:app --host 0.0.0.0 --port "$PORT" --workers 4
