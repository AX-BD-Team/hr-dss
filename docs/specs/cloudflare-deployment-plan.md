# HR-DSS Cloudflare 클라우드 배포 계획

> 마지막 업데이트: 2025-01-21
> 버전: 1.0

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
hr-dss.example.com           → Cloudflare Pages (Frontend)
api.hr-dss.example.com       → Cloudflare Workers → Railway (Backend)
auth.hr-dss.example.com      → Cloudflare Zero Trust
*.hr-dss.example.com         → Cloudflare CDN
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
| Production Access | `hr-dss.example.com/*` | 회사 이메일 + SSO | Allow |
| API Access | `api.hr-dss.example.com/*` | 유효한 JWT | Allow |
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
  domain: "hr-dss.example.com"
  type: "self_hosted"
  session_duration: "8h"

policies:
  - name: "Allow Company Users"
    decision: "allow"
    include:
      - email_domain: "example.com"
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
  - hostname: api.hr-dss.example.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true

  - hostname: ws.hr-dss.example.com
    service: http://localhost:8000
    originRequest:
      httpHostHeader: "ws.hr-dss.example.com"

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

## 부록 A: Cloudflare 설정 체크리스트

### A.1 초기 설정

- [ ] Cloudflare 계정 생성
- [ ] 도메인 추가 및 네임서버 변경
- [ ] SSL/TLS 인증서 설정
- [ ] Pages 프로젝트 생성
- [ ] Workers 프로젝트 생성

### A.2 Zero Trust 설정

- [ ] Access Application 생성
- [ ] Identity Provider 연동 (SSO)
- [ ] Access Policy 설정
- [ ] Tunnel 생성 및 연결

### A.3 보안 설정

- [ ] WAF 규칙 활성화
- [ ] Rate Limiting 설정
- [ ] Bot Management 설정
- [ ] Security Headers 설정

### A.4 모니터링 설정

- [ ] Analytics 대시보드 구성
- [ ] Logpush 설정
- [ ] Notification Policy 설정
- [ ] Health Check 설정
