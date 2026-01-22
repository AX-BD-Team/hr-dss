# HR-DSS Cloudflare 클라우드 배포 계획

> 마지막 업데이트: 2025-01-22
> 버전: 1.1

---

## 0. 프로젝트 현황 및 배포 준비 상태

### 0.1 구현 현황

| 레이어 | 컴포넌트 | 상태 | 비고 |
|--------|----------|------|------|
| **Frontend** | Next.js App | ✅ 완료 | 8개 컴포넌트, 4개 페이지 |
| **Frontend** | Cloudflare Pages 설정 | ✅ 완료 | `output: 'export'` 설정 |
| **API Gateway** | Cloudflare Workers | ✅ 완료 | CORS, Rate Limiting, 프록시 |
| **API Gateway** | wrangler.toml | ✅ 완료 | hr.minu.best 도메인 설정 |
| **Backend** | Agent Runtime | ✅ 완료 | 6개 에이전트 구현 |
| **Backend** | Ontology/KG | ✅ 완료 | 검증기, 데이터 로더, 쿼리 |
| **Backend** | HITL Workflow | ✅ 완료 | 승인 워크플로우 |
| **Backend** | FastAPI 라우터 | ❌ **미구현** | `backend/api/` 필요 |
| **인프라** | Dockerfile | ✅ 완료 | Multi-stage 빌드 |
| **인프라** | docker-compose | ✅ 완료 | 로컬 개발 환경 |
| **인프라** | Railway 설정 | ✅ 완료 | railway.json, railway.toml |
| **인프라** | GitHub Actions | ✅ 완료 | deploy-cloudflare.yml |
| **테스트** | pytest | ✅ 완료 | Day 2-7 테스트 |

### 0.2 파일 구조 현황

```
hr-dss/
├── apps/web/                    # ✅ Frontend (Next.js 14)
│   ├── components/              # 8개 컴포넌트
│   │   ├── ConversationUI.tsx
│   │   ├── OptionCompare.tsx
│   │   ├── ExplanationPanel.tsx
│   │   ├── GraphViewer.tsx
│   │   ├── EvalDashboard.tsx
│   │   ├── AgentEvalDashboard.tsx
│   │   ├── OntologyScoreCard.tsx
│   │   └── DataQualityReport.tsx
│   ├── app/                     # 4개 페이지
│   │   ├── page.tsx             # /
│   │   ├── decisions/page.tsx   # /decisions
│   │   ├── dashboard/page.tsx   # /dashboard
│   │   └── graph/page.tsx       # /graph
│   ├── next.config.js           # Cloudflare Pages 설정
│   └── package.json
├── backend/                      # ✅ Backend (FastAPI)
│   ├── agent_runtime/
│   │   ├── agents/              # 6개 에이전트
│   │   ├── ontology/            # KG 검증/쿼리
│   │   ├── workflows/           # HITL
│   │   └── data_quality/        # 품질 검사
│   ├── database/                # 모델 정의
│   └── api/                     # ❌ 미구현 (필요!)
│       └── main.py              # ❌ 미구현
├── workers/api-gateway/          # ✅ Cloudflare Workers
│   ├── src/index.ts
│   ├── wrangler.toml
│   └── package.json
├── Dockerfile                    # ✅ 완료
├── docker-compose.yml            # ✅ 완료
├── railway.json                  # ✅ 완료
├── railway.toml                  # ✅ 완료
└── .github/workflows/
    └── deploy-cloudflare.yml     # ✅ 완료
```

### 0.3 배포 차단 요소 (Blockers)

| 순위 | 항목 | 영향 | 해결 방안 |
|------|------|------|----------|
| 🔴 1 | **FastAPI 라우터 미구현** | Backend 배포 불가 | `backend/api/main.py` 구현 |
| 🟡 2 | GitHub Secrets 미설정 | CI/CD 실패 | 대시보드에서 설정 |
| 🟡 3 | Cloudflare 계정 미설정 | 배포 불가 | 계정 생성 및 도메인 설정 |
| 🟡 4 | Railway 프로젝트 미생성 | Backend 배포 불가 | 프로젝트 생성 |
| 🟢 5 | Neo4j Aura 미연결 | KG 기능 제한 | 인스턴스 생성 |

### 0.4 도메인 설정 현황

| 항목 | 설정값 | 상태 |
|------|--------|------|
| Production Frontend | `https://hr.minu.best` | 📝 코드 설정 완료 |
| Production API | `https://api.hr.minu.best` | 📝 코드 설정 완료 |
| Staging Frontend | `https://staging.hr.minu.best` | 📝 코드 설정 완료 |
| Staging API | `https://staging-api.hr.minu.best` | 📝 코드 설정 완료 |
| Cloudflare DNS | minu.best | ⚠️ DNS 레코드 추가 필요 |

---

## 1. 아키텍처 개요

### 1.1 Cloudflare 기반 하이브리드 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              사용자 (브라우저)                                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Cloudflare Edge Network                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   CDN       │  │ Zero Trust  │  │   WAF       │  │  DDoS Protection    │ │
│  │  (캐싱)     │  │  (인증)     │  │  (보안)     │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────────────┐
│  Cloudflare       │    │  Cloudflare       │    │  Cloudflare Tunnel        │
│  Pages            │    │  Workers          │    │  (Argo Tunnel)            │
│  ─────────────    │    │  ─────────────    │    │  ────────────────────     │
│  • Next.js SSG    │    │  • API Gateway    │    │  • Backend 연결           │
│  • React SPA      │    │  • Edge 캐싱      │    │  • Private Network 연결   │
│  • 정적 자산      │    │  • Rate Limiting  │    │                           │
└───────────────────┘    └─────────┬─────────┘    └─────────────┬─────────────┘
                                   │                            │
                                   └──────────────┬─────────────┘
                                                  │
                                                  ▼
                    ┌─────────────────────────────────────────────────────┐
                    │                  Backend Services                    │
                    │  ┌───────────────┐  ┌───────────────────────────┐   │
                    │  │  FastAPI      │  │  Agent Runtime             │   │
                    │  │  (Railway)    │  │  • Query Decomposition     │   │
                    │  │  ───────────  │  │  • Option Generator        │   │
                    │  │  • REST API   │  │  • Impact Simulator        │   │
                    │  │  • WebSocket  │  │  • Success Probability     │   │
                    │  │  • SSE        │  │  • Validator               │   │
                    │  └───────┬───────┘  └───────────────────────────┘   │
                    │          │                                          │
                    └──────────┼──────────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
┌───────────────────┐  ┌───────────────┐  ┌───────────────────┐
│  Neon PostgreSQL  │  │  Neo4j Aura   │  │  Cloudflare R2    │
│  ────────────────  │  │  ──────────   │  │  ────────────     │
│  • 관계형 DB      │  │  • Knowledge  │  │  • 파일 저장소    │
│  • 트랜잭션       │  │    Graph      │  │  • 로그 아카이브  │
│  • Serverless     │  │  • Cypher     │  │  • 백업           │
└───────────────────┘  └───────────────┘  └───────────────────┘
```

### 1.2 서비스 선정 이유

| 서비스 | 역할 | 선정 이유 |
|--------|------|----------|
| **Cloudflare Pages** | Frontend 호스팅 | 무료 SSL, 글로벌 CDN, 자동 배포 |
| **Cloudflare Workers** | API Gateway | Edge 실행, 낮은 레이턴시, Rate Limiting |
| **Cloudflare Zero Trust** | 인증/권한 | SSO 연동, 조건부 접근, 감사 로그 |
| **Cloudflare Tunnel** | Backend 연결 | 공인 IP 없이 연결, 보안 강화 |
| **Cloudflare R2** | 객체 저장소 | S3 호환, egress 비용 없음 |
| **Railway** | Backend 호스팅 | Python 지원, 자동 스케일링, 간편 배포 |
| **Neon** | PostgreSQL | Serverless, 자동 스케일링, 분기 기능 |
| **Neo4j Aura** | Knowledge Graph | 관리형 Neo4j, 고가용성 |

---

## 2. 환경 구성

### 2.1 환경별 구성

| 환경 | 용도 | Cloudflare 설정 | Backend |
|------|------|-----------------|---------|
| **Development** | 로컬 개발 | - | docker-compose |
| **Preview** | PR 미리보기 | Pages Preview | Railway (Preview) |
| **Staging** | 통합 테스트 | staging.hr-dss.* | Railway (Staging) |
| **Production** | 운영 | hr-dss.* | Railway (Production) |

### 2.2 도메인 구성

```
hr.minu.best           → Cloudflare Pages (Frontend)
api.hr.minu.best       → Cloudflare Workers → Railway (Backend)
auth.hr.minu.best      → Cloudflare Zero Trust
*.hr.minu.best         → Cloudflare CDN
```

---

## 3. Cloudflare 서비스별 구성

### 3.1 Cloudflare Pages (Frontend)

**설정:**
```toml
# wrangler.toml (Pages)
name = "hr-dss-web"
compatibility_date = "2024-01-01"

[env.production]
vars = { ENVIRONMENT = "production" }

[env.staging]
vars = { ENVIRONMENT = "staging" }
```

**빌드 설정:**
| 항목 | 값 |
|------|-----|
| Framework | Next.js |
| Build command | `pnpm build` |
| Build output | `.next` |
| Root directory | `apps/web` |
| Node version | 20 |

**배포 트리거:**
- `main` 브랜치 push → Production
- PR 생성 → Preview 환경

### 3.2 Cloudflare Workers (API Gateway)

**기능:**
1. API 라우팅 및 프록시
2. Rate Limiting
3. 요청/응답 캐싱
4. CORS 처리
5. 인증 토큰 검증

**코드 예시:**
```typescript
// workers/api-gateway/src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Rate Limiting
    const rateLimitResult = await env.RATE_LIMITER.limit({ key: getClientIP(request) });
    if (!rateLimitResult.success) {
      return new Response('Too Many Requests', { status: 429 });
    }

    // 인증 검증
    const authResult = await validateAuth(request, env);
    if (!authResult.valid) {
      return new Response('Unauthorized', { status: 401 });
    }

    // Backend로 프록시
    const backendUrl = `${env.BACKEND_URL}${url.pathname}${url.search}`;
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
    });

    // 응답 캐싱 (GET 요청)
    if (request.method === 'GET') {
      const cachedResponse = new Response(response.body, response);
      cachedResponse.headers.set('Cache-Control', 'public, max-age=60');
      return cachedResponse;
    }

    return response;
  },
};
```

**Rate Limiting 설정:**
```toml
# wrangler.toml
[[unsafe.bindings]]
name = "RATE_LIMITER"
type = "ratelimit"
namespace_id = "hr-dss-api"
simple = { limit = 100, period = 60 }  # 분당 100 요청
```

### 3.3 Cloudflare Zero Trust (인증/보안)

**접근 정책:**

| 정책 이름 | 대상 | 조건 | 액션 |
|----------|------|------|------|
| Production Access | `hr.minu.best/*` | 회사 이메일 + SSO | Allow |
| API Access | `api.hr.minu.best/*` | 유효한 JWT | Allow |
| Admin Access | `*/admin/*` | 관리자 그룹 + MFA | Allow |
| Staging Access | `staging.*` | 개발팀 그룹 | Allow |

**SSO 연동:**
- SAML 2.0 / OIDC 지원
- Azure AD / Okta / Google Workspace 연동
- 기존 HR 시스템 SSO 연동

**설정:**
```yaml
# Zero Trust Application 설정
application:
  name: "HR-DSS Production"
  domain: "hr.minu.best"
  type: "self_hosted"
  session_duration: "8h"

policies:
  - name: "Allow Company Users"
    decision: "allow"
    include:
      - email_domain: "minu.best"
    require:
      - login_method: ["saml"]

  - name: "Admin Access"
    decision: "allow"
    include:
      - group: "hr-dss-admins"
    require:
      - mfa: true
```

### 3.4 Cloudflare Tunnel (Backend 연결)

**아키텍처:**
```
Railway (FastAPI)
      │
      ▼
┌─────────────────┐
│  cloudflared    │  ← Tunnel Connector
│  (Docker)       │
└────────┬────────┘
         │
         ▼ (암호화된 연결)
┌─────────────────┐
│  Cloudflare     │
│  Edge Network   │
└─────────────────┘
```

**설정:**
```yaml
# cloudflared/config.yml
tunnel: hr-dss-backend
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: api.hr.minu.best
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true

  - hostname: ws.hr.minu.best
    service: http://localhost:8000
    originRequest:
      httpHostHeader: "ws.hr.minu.best"

  - service: http_status:404
```

### 3.5 Cloudflare R2 (객체 저장소)

**버킷 구성:**

| 버킷 | 용도 | 보존 정책 |
|------|------|----------|
| `hr-dss-assets` | 정적 자산 (이미지, 문서) | 영구 |
| `hr-dss-logs` | 애플리케이션 로그 | 90일 |
| `hr-dss-backups` | DB 백업 | 30일 |
| `hr-dss-exports` | 사용자 내보내기 파일 | 7일 |

**접근 설정:**
```typescript
// R2 바인딩 설정
export interface Env {
  ASSETS_BUCKET: R2Bucket;
  LOGS_BUCKET: R2Bucket;
}

// 파일 업로드
await env.ASSETS_BUCKET.put(key, file, {
  httpMetadata: { contentType: 'application/pdf' },
  customMetadata: { uploadedBy: userId },
});
```

---

## 4. Backend 배포 (Railway)

### 4.1 Railway 프로젝트 구성

```
hr-dss (Project)
├── api (Service)           # FastAPI Backend
├── worker (Service)        # Background Jobs
├── postgres (Database)     # PostgreSQL (또는 Neon 연결)
└── redis (Database)        # 캐싱/세션
```

### 4.2 환경 변수

```bash
# Railway 환경 변수
ENVIRONMENT=production
DATABASE_URL=postgresql://...@neon.tech/hr_dss
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=${NEO4J_PASSWORD}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# Cloudflare 연동
CLOUDFLARE_TUNNEL_TOKEN=${CF_TUNNEL_TOKEN}
R2_ACCESS_KEY_ID=${R2_ACCESS_KEY}
R2_SECRET_ACCESS_KEY=${R2_SECRET_KEY}
R2_BUCKET_NAME=hr-dss-assets
```

### 4.3 railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

---

## 5. 데이터베이스 구성

### 5.1 Neon PostgreSQL

**연결 설정:**
```
postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/hr_dss?sslmode=require
```

**기능 활용:**
- **Branching**: PR별 DB 브랜치 생성
- **Autoscaling**: 사용량 기반 자동 스케일링
- **Point-in-time Recovery**: 특정 시점 복구

**설정:**
```python
# backend/core/config.py
DATABASE_URL = os.getenv("DATABASE_URL")
# Neon 권장 설정
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
```

### 5.2 Neo4j Aura

**연결 설정:**
```python
NEO4J_URI = "neo4j+s://xxx.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
```

**인스턴스 크기:**
| 환경 | 인스턴스 | 노드/관계 | 월 비용 (예상) |
|------|---------|----------|--------------|
| Staging | AuraDB Free | 50K/175K | $0 |
| Production | AuraDB Professional | 400K/1.6M | ~$65 |

---

## 6. CI/CD 파이프라인 업데이트

### 6.1 GitHub Actions 수정

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
  CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}

jobs:
  deploy-frontend:
    name: Deploy Frontend to Cloudflare Pages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Install dependencies
        run: pnpm install

      - name: Build
        run: pnpm build
        working-directory: apps/web

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ env.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ env.CLOUDFLARE_ACCOUNT_ID }}
          projectName: hr-dss-web
          directory: apps/web/.next
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}

  deploy-workers:
    name: Deploy Workers
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy API Gateway Worker
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ env.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ env.CLOUDFLARE_ACCOUNT_ID }}
          workingDirectory: workers/api-gateway

  deploy-backend:
    name: Deploy Backend to Railway
    runs-on: ubuntu-latest
    needs: [deploy-frontend, deploy-workers]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: api
```

---

## 7. 모니터링 및 관측성

### 7.1 Cloudflare Analytics

| 메트릭 | 임계값 | 알림 |
|--------|--------|------|
| 요청 수 | - | 대시보드 |
| 에러율 | > 1% | Slack/Email |
| 레이턴시 P99 | > 3s | Slack |
| 캐시 히트율 | < 80% | Email |

### 7.2 로그 스택

```
Application Logs → Cloudflare Logpush → R2 → (선택) DataDog/Grafana
```

**Logpush 설정:**
```json
{
  "destination": "r2://hr-dss-logs/cloudflare-logs",
  "dataset": "http_requests",
  "frequency": "high",
  "logpull_options": "fields=EdgeStartTimestamp,ClientIP,ClientRequestPath,EdgeResponseStatus"
}
```

### 7.3 알림 설정

```yaml
# Cloudflare Notification Policy
notifications:
  - name: "High Error Rate"
    type: "workers_analytics"
    conditions:
      - metric: "errors_rate"
        operator: "greater_than"
        value: 0.01  # 1%
    alert_type: "slack"

  - name: "DDoS Attack"
    type: "ddos_attack_l7"
    alert_type: ["slack", "email"]
```

---

## 8. 보안 설정

### 8.1 WAF Rules

| 규칙 | 액션 | 설명 |
|------|------|------|
| OWASP Core Ruleset | Block | SQL Injection, XSS 등 |
| Rate Limiting | Challenge | 분당 100+ 요청 |
| Bot Management | Challenge | 의심스러운 봇 |
| Custom Rule | Block | 특정 국가 차단 (선택) |

### 8.2 SSL/TLS 설정

| 설정 | 값 |
|------|-----|
| SSL Mode | Full (Strict) |
| Minimum TLS Version | TLS 1.2 |
| TLS 1.3 | Enabled |
| HSTS | Enabled (max-age=31536000) |
| Always Use HTTPS | Enabled |

### 8.3 보안 헤더

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

---

## 9. 비용 예측

### 9.1 월간 예상 비용 (Production)

| 서비스 | 티어 | 예상 비용 |
|--------|------|----------|
| Cloudflare Pro | Pro Plan | $20 |
| Cloudflare Workers | Paid (Bundled) | ~$5 |
| Cloudflare R2 | 10GB 저장 | ~$2 |
| Cloudflare Zero Trust | 50 사용자 | $0 (Free Tier) |
| Railway | Hobby → Pro | $5 ~ $20 |
| Neon PostgreSQL | Launch | $19 |
| Neo4j Aura | Professional | $65 |
| **합계** | | **~$116 ~ $131/월** |

### 9.2 비용 최적화 옵션

- Cloudflare Free 티어 활용 (소규모 시)
- Railway Hobby 플랜 ($5/월)
- Neo4j Aura Free (개발/스테이징)
- R2 egress 비용 없음 활용

---

## 10. 마이그레이션 계획

### 10.1 단계별 마이그레이션

| 단계 | 기간 | 작업 | 검증 |
|------|------|------|------|
| **1단계** | Week 1 | Cloudflare 계정 설정, 도메인 연결 | DNS 전파 확인 |
| **2단계** | Week 1-2 | Pages 배포, Workers 구성 | Frontend 접속 확인 |
| **3단계** | Week 2 | Railway 배포, Tunnel 설정 | API 호출 확인 |
| **4단계** | Week 2-3 | Neon/Neo4j Aura 마이그레이션 | 데이터 무결성 확인 |
| **5단계** | Week 3 | Zero Trust 설정, 보안 강화 | 인증 플로우 확인 |
| **6단계** | Week 4 | 모니터링 설정, 부하 테스트 | 성능 기준 충족 |

### 10.2 롤백 계획

1. **DNS 롤백**: Cloudflare DNS에서 origin 직접 연결
2. **서비스 롤백**: Railway 이전 버전 배포
3. **데이터 롤백**: Neon Point-in-time Recovery

---

## 11. 관련 문서

- [Phase 1 계획](./phase1-plan.md)
- [API 문서](../api-docs.md)
- [인프라 설정 (Docker)](../../docker-compose.yml)
- [CI/CD 파이프라인](../../.github/workflows/)

---

## 부록 A: 배포 작업 계획

### A.1 Phase 1: 코드 완성 (필수)

| 우선순위 | 작업 | 담당 | 예상 소요 |
|----------|------|------|----------|
| 🔴 P0 | **FastAPI 라우터 구현** (`backend/api/main.py`) | 개발 | 2-4시간 |
| 🔴 P0 | Health check 엔드포인트 (`/health`) | 개발 | 30분 |
| 🔴 P0 | Agent API 엔드포인트 (`/api/v1/agents/*`) | 개발 | 2시간 |
| 🟡 P1 | Decision API 엔드포인트 (`/api/v1/decisions/*`) | 개발 | 2시간 |
| 🟡 P1 | Graph API 엔드포인트 (`/api/v1/graph/*`) | 개발 | 1시간 |

**FastAPI 라우터 구조 (필요):**
```
backend/api/
├── __init__.py
├── main.py              # FastAPI app, 라우터 등록
├── routers/
│   ├── __init__.py
│   ├── health.py        # /health
│   ├── agents.py        # /api/v1/agents/*
│   ├── decisions.py     # /api/v1/decisions/*
│   └── graph.py         # /api/v1/graph/*
└── dependencies.py      # 공통 의존성
```

### A.2 Phase 2: 인프라 설정 (수동)

| 순서 | 작업 | 플랫폼 | 체크 |
|------|------|--------|------|
| 1 | Cloudflare 계정 확인/생성 | cloudflare.com | [ ] |
| 2 | minu.best 도메인 Cloudflare 등록 확인 | Cloudflare DNS | [ ] |
| 3 | GitHub Secrets 설정 | GitHub | [ ] |
| 4 | Cloudflare Pages 프로젝트 생성 | Cloudflare | [ ] |
| 5 | Railway 프로젝트 생성 | railway.app | [ ] |
| 6 | Neo4j Aura 인스턴스 생성 | neo4j.com | [ ] |
| 7 | Railway 환경 변수 설정 | Railway | [ ] |

### A.3 Phase 3: 배포 및 검증

| 순서 | 작업 | 검증 방법 |
|------|------|----------|
| 1 | Frontend 배포 (Pages) | `https://hr.minu.best` 접속 |
| 2 | Workers 배포 | `https://api.hr.minu.best/health` |
| 3 | Backend 배포 (Railway) | Workers → Railway 프록시 확인 |
| 4 | DNS 레코드 추가 | dig 명령으로 확인 |
| 5 | E2E 테스트 | 전체 플로우 확인 |

### A.4 GitHub Secrets 설정

```
Repository → Settings → Secrets and variables → Actions
```

| Secret Name | 값 | 상태 |
|-------------|-----|------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API 토큰 | [ ] 미설정 |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 계정 ID | [ ] 미설정 |
| `RAILWAY_TOKEN` | Railway 배포 토큰 | [ ] 미설정 |

### A.5 DNS 레코드 설정 (Cloudflare)

```
Type    Name              Content                              Proxy
─────────────────────────────────────────────────────────────────────
CNAME   hr                hr-dss-web.pages.dev                 ✓
CNAME   api.hr            hr-dss-api-gateway.workers.dev       ✓
CNAME   staging.hr        hr-dss-web.pages.dev                 ✓
CNAME   staging-api.hr    hr-dss-api-gateway-staging.workers.dev  ✓
```

---

## 부록 B: Cloudflare 설정 체크리스트

### B.1 초기 설정

- [ ] Cloudflare 계정 생성
- [ ] 도메인 추가 및 네임서버 변경
- [ ] SSL/TLS 인증서 설정
- [ ] Pages 프로젝트 생성
- [ ] Workers 프로젝트 생성

### B.2 Zero Trust 설정 (선택, PoC 이후)

- [ ] Access Application 생성
- [ ] Identity Provider 연동 (SSO)
- [ ] Access Policy 설정
- [ ] Tunnel 생성 및 연결

### B.3 보안 설정

- [ ] WAF 규칙 활성화
- [ ] Rate Limiting 설정
- [ ] Bot Management 설정
- [ ] Security Headers 설정

### B.4 모니터링 설정

- [ ] Analytics 대시보드 구성
- [ ] Logpush 설정
- [ ] Notification Policy 설정
- [ ] Health Check 설정
