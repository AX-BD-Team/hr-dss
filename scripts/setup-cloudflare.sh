#!/bin/bash
# Cloudflare 초기 설정 스크립트
# 사전 요구사항: wrangler 로그인 완료 (wrangler login)

set -e

echo "🔧 Cloudflare 초기 설정"
echo "========================"

# Cloudflare 로그인 확인
echo ""
echo "1. Cloudflare 로그인 확인..."
if ! wrangler whoami &> /dev/null; then
    echo "❌ Cloudflare에 로그인되어 있지 않습니다."
    echo "   실행: wrangler login"
    exit 1
fi
echo "✅ 로그인 확인됨"

# 계정 ID 확인
ACCOUNT_ID=$(wrangler whoami 2>&1 | grep -oP 'account_id = "\K[^"]+' || echo "")
if [[ -z "$ACCOUNT_ID" ]]; then
    echo ""
    echo "⚠️ Account ID를 자동으로 가져올 수 없습니다."
    echo "   Cloudflare 대시보드에서 Account ID를 확인하세요."
    read -p "Account ID 입력: " ACCOUNT_ID
fi
echo "📋 Account ID: $ACCOUNT_ID"

# Pages 프로젝트 생성
echo ""
echo "2. Cloudflare Pages 프로젝트 생성..."
echo "   (이미 존재하면 건너뜁니다)"
wrangler pages project create hr-dss-web --production-branch=main 2>/dev/null || echo "   Pages 프로젝트가 이미 존재합니다."

# KV Namespace 생성 (선택)
echo ""
echo "3. KV Namespace 생성 (캐싱용)..."
read -p "KV Namespace 생성? (y/N): " CREATE_KV
if [[ "$CREATE_KV" =~ ^[Yy]$ ]]; then
    wrangler kv:namespace create CACHE 2>/dev/null || echo "   KV Namespace가 이미 존재합니다."
    wrangler kv:namespace create CACHE --preview 2>/dev/null || echo "   Preview KV Namespace가 이미 존재합니다."
fi

# R2 Bucket 생성 (선택)
echo ""
echo "4. R2 Bucket 생성 (파일 저장용)..."
read -p "R2 Bucket 생성? (y/N): " CREATE_R2
if [[ "$CREATE_R2" =~ ^[Yy]$ ]]; then
    wrangler r2 bucket create hr-dss-assets 2>/dev/null || echo "   R2 Bucket이 이미 존재합니다."
fi

# 설정 파일 업데이트 안내
echo ""
echo "==========================================="
echo "✅ 초기 설정 완료!"
echo ""
echo "📝 다음 단계:"
echo ""
echo "1. GitHub Secrets 설정:"
echo "   - CLOUDFLARE_API_TOKEN: API 토큰 생성 필요"
echo "   - CLOUDFLARE_ACCOUNT_ID: $ACCOUNT_ID"
echo ""
echo "2. wrangler.toml 업데이트:"
echo "   account_id = \"$ACCOUNT_ID\""
echo ""
echo "3. 도메인 설정 (Cloudflare DNS):"
echo "   - hr-dss.example.com → Pages"
echo "   - api.hr-dss.example.com → Workers"
echo ""
echo "4. Zero Trust 설정 (Cloudflare 대시보드):"
echo "   - Access Application 생성"
echo "   - Identity Provider 연동"
