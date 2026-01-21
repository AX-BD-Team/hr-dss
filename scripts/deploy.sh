#!/bin/bash
# HR-DSS 배포 스크립트
# 사용법: ./scripts/deploy.sh [environment]
# 환경: development, staging, production

set -e

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 HR-DSS 배포 시작 (환경: $ENVIRONMENT)"
echo "==========================================="

# 환경 검증
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "❌ 잘못된 환경: $ENVIRONMENT"
    echo "사용 가능: development, staging, production"
    exit 1
fi

# 필수 도구 확인
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 이(가) 설치되어 있지 않습니다."
        exit 1
    fi
}

check_tool "wrangler"
check_tool "railway"
check_tool "pnpm"

# 1. Frontend 빌드 및 배포 (Cloudflare Pages)
echo ""
echo "📦 1/3: Frontend 빌드 및 배포"
echo "---------------------------------------------"
cd "$PROJECT_DIR/apps/web"
pnpm install
pnpm build
echo "✅ Frontend 빌드 완료"

if [[ "$ENVIRONMENT" != "development" ]]; then
    echo "🚀 Cloudflare Pages 배포 중..."
    # wrangler pages deploy out --project-name=hr-dss-web
    echo "✅ Pages 배포 완료 (수동 배포 필요: wrangler pages deploy)"
fi

# 2. API Gateway 배포 (Cloudflare Workers)
echo ""
echo "⚡ 2/3: API Gateway 배포"
echo "---------------------------------------------"
cd "$PROJECT_DIR/workers/api-gateway"
npm install

if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "🚀 Workers (Production) 배포 중..."
    wrangler deploy --env production
elif [[ "$ENVIRONMENT" == "staging" ]]; then
    echo "🚀 Workers (Staging) 배포 중..."
    wrangler deploy --env staging
else
    echo "ℹ️ Development 환경 - Workers 로컬 실행"
    echo "  실행: cd workers/api-gateway && wrangler dev"
fi

# 3. Backend 배포 (Railway)
echo ""
echo "🔧 3/3: Backend 배포"
echo "---------------------------------------------"
cd "$PROJECT_DIR"

if [[ "$ENVIRONMENT" == "production" ]] || [[ "$ENVIRONMENT" == "staging" ]]; then
    echo "🚀 Railway 배포 중..."
    railway up --detach
    echo "✅ Railway 배포 완료"
else
    echo "ℹ️ Development 환경 - 로컬 실행"
    echo "  실행: docker-compose up -d"
fi

# 완료
echo ""
echo "==========================================="
echo "✅ HR-DSS 배포 완료 (환경: $ENVIRONMENT)"
echo ""
echo "📝 배포 URL:"
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "  - Frontend: https://hr.minu.best"
    echo "  - API: https://api.hr.minu.best"
elif [[ "$ENVIRONMENT" == "staging" ]]; then
    echo "  - Frontend: https://staging.hr.minu.best"
    echo "  - API: https://staging-api.hr.minu.best"
else
    echo "  - Frontend: http://localhost:3000"
    echo "  - API: http://localhost:8000"
fi
