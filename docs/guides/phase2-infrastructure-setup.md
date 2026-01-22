# Phase 2: 인프라 설정 가이드

> 마지막 업데이트: 2026-01-22
> 예상 소요: 1-2시간

---

## 현재 상태 (2026-01-22)

| 항목                       | 상태      | URL                          |
| -------------------------- | --------- | ---------------------------- |
| Cloudflare Pages           | ✅ 완료   | https://hr.minu.best         |
| Cloudflare Pages (Staging) | ✅ 완료   | https://staging.hr.minu.best |
| Cloudflare Workers         | ✅ 완료   | https://api-hr.minu.best     |
| Railway Backend            | 🔄 대기   | -                            |
| Neo4j Aura                 | ❌ 미설정 | -                            |

---

## 1. 개요

### 1.1 목표

클라우드 인프라를 설정하여 HR-DSS를 `hr.minu.best` 도메인으로 배포

### 1.2 설정 순서

```
1. Cloudflare 계정 확인        ✅ 완료
       ↓
2. GitHub Secrets 설정         🔄 진행중
       ↓
3. Cloudflare Pages 프로젝트   ✅ 완료
       ↓
4. Railway 프로젝트 생성       🔄 대기
       ↓
5. Neo4j Aura 인스턴스 생성    ❌ 미시작
       ↓
6. DNS 레코드 설정             ✅ 완료
```

### 1.3 필요한 계정

| 서비스     | URL                 | 용도                |
| ---------- | ------------------- | ------------------- |
| Cloudflare | dash.cloudflare.com | Pages, Workers, DNS |
| GitHub     | github.com          | CI/CD, Secrets      |
| Railway    | railway.app         | Backend 호스팅      |
| Neo4j Aura | console.neo4j.io    | Knowledge Graph     |

---

## 2. Cloudflare 설정

### 2.1 계정 확인

1. [Cloudflare Dashboard](https://dash.cloudflare.com) 로그인
2. `minu.best` 도메인이 등록되어 있는지 확인
3. 없으면 **Add a Site** 클릭하여 도메인 추가

### 2.2 API Token 생성

1. **My Profile** → **API Tokens** → **Create Token**
2. **Custom token** 선택
3. 권한 설정:

| Permission                 | Zone         | Access |
| -------------------------- | ------------ | ------ |
| Account - Cloudflare Pages | All accounts | Edit   |
| Account - Workers Scripts  | All accounts | Edit   |
| Zone - DNS                 | All zones    | Edit   |

4. **Continue to summary** → **Create Token**
5. 토큰 복사 (⚠️ 한 번만 표시됨)

```
토큰 예시: Cv1234567890abcdefghijklmnopqrstuv
```

### 2.3 Account ID 확인

1. Cloudflare Dashboard → 도메인 선택 (`minu.best`)
2. 우측 하단 **API** 섹션에서 **Account ID** 복사

```
Account ID 예시: abcd1234567890efghij1234567890kl
```

### 2.4 Pages 프로젝트 생성

1. Cloudflare Dashboard → **Pages** → **Create a project**
2. **Connect to Git** → GitHub 연결
3. Repository: `AX-BD-Team/hr-dss` 선택
4. 설정:

| 항목                   | 값                                          |
| ---------------------- | ------------------------------------------- |
| Project name           | `hr-dss-web`                                |
| Production branch      | `master`                                    |
| Framework preset       | Next.js (Static HTML Export)                |
| Build command          | `cd apps/web && pnpm install && pnpm build` |
| Build output directory | `apps/web/out`                              |
| Root directory         | `/`                                         |
| Node version           | `20`                                        |

5. Environment variables (Production):

```
NEXT_PUBLIC_API_URL = https://api-hr.minu.best
NEXT_PUBLIC_ENVIRONMENT = production
```

6. **Save and Deploy**

> ✅ **완료**: Pages 프로젝트 `hr-dss-web` 생성 및 배포됨
>
> - Production: https://hr.minu.best
> - Staging: https://staging.hr.minu.best

### 2.5 Workers 배포 (첫 배포) ✅ 완료

```bash
# 로컬에서 Workers 배포
cd workers/api-gateway
npm install
wrangler login
wrangler deploy --env production
```

**배포 결과:**

- Workers.dev: `https://hr-dss-api-gateway.sinclair-account.workers.dev`
- 커스텀 도메인: `https://api-hr.minu.best`

> ⚠️ Workers 서브도메인은 계정마다 다릅니다. `wrangler whoami`로 확인 후
> `wrangler subdomain`으로 서브도메인을 조회하세요.

---

## 3. GitHub Secrets 설정

### 3.1 설정 위치

```
GitHub Repository → Settings → Secrets and variables → Actions → New repository secret
```

### 3.2 필요한 Secrets

| Secret Name             | 값                       | 설명                 |
| ----------------------- | ------------------------ | -------------------- |
| `CLOUDFLARE_API_TOKEN`  | Step 2.2에서 생성한 토큰 | Cloudflare API 인증  |
| `CLOUDFLARE_ACCOUNT_ID` | Step 2.3에서 확인한 ID   | Cloudflare 계정 식별 |
| `RAILWAY_TOKEN`         | Step 4에서 생성          | Railway 배포 인증    |

### 3.3 설정 방법

1. GitHub Repository 페이지 이동
2. **Settings** 탭 클릭
3. 좌측 메뉴에서 **Secrets and variables** → **Actions**
4. **New repository secret** 클릭
5. Name과 Secret 입력 후 **Add secret**

---

## 4. Railway 설정

### 4.1 프로젝트 생성

1. [Railway](https://railway.app) 로그인
2. **New Project** → **Deploy from GitHub repo**
3. Repository: `AX-BD-Team/hr-dss` 선택
4. **Deploy Now**

### 4.2 서비스 설정

1. 생성된 서비스 클릭
2. **Settings** 탭:

| 항목           | 값                                                         |
| -------------- | ---------------------------------------------------------- |
| Root Directory | `/`                                                        |
| Build Command  | (자동 - Dockerfile 사용)                                   |
| Start Command  | `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT` |

### 4.3 환경 변수 설정

**Variables** 탭에서 추가:

```bash
# 필수
ENVIRONMENT=production
DATABASE_URL=postgresql://...  # Step 5에서 설정
NEO4J_URI=neo4j+s://...        # Step 5에서 설정
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
ANTHROPIC_API_KEY=sk-ant-...

# 보안
JWT_SECRET_KEY=your-secure-random-key-here

# CORS
ALLOWED_ORIGINS=https://hr.minu.best,https://staging.hr.minu.best
```

### 4.4 Railway Token 생성

1. Railway Dashboard → **Account Settings** (우측 상단 아바타)
2. **Tokens** 탭
3. **Create Token** → 이름 입력 → **Create**
4. 토큰 복사 → GitHub Secret `RAILWAY_TOKEN`에 저장

### 4.5 Public Domain 설정 (선택)

Railway에서 직접 도메인 노출 시:

1. 서비스 → **Settings** → **Networking**
2. **Generate Domain** 클릭
3. 생성된 URL: `hr-dss-production.up.railway.app`

---

## 5. 데이터베이스 설정

### 5.1 Neo4j Aura 설정

#### 인스턴스 생성

1. [Neo4j Aura Console](https://console.neo4j.io) 로그인
2. **Create Instance** 클릭
3. 설정:

| 항목          | 값                                            |
| ------------- | --------------------------------------------- |
| Instance name | `hr-dss-production`                           |
| Region        | `asia-southeast1` (Singapore)                 |
| Instance type | **AuraDB Free** (PoC용) 또는 **Professional** |

4. **Create** 클릭
5. 생성 완료 후 연결 정보 복사:

```
Connection URI: neo4j+s://xxxxxxxx.databases.neo4j.io
Username: neo4j
Password: (생성 시 표시, 저장 필수!)
```

#### Railway 환경 변수 업데이트

```bash
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-generated-password
```

### 5.2 PostgreSQL (선택 - Neon)

Railway에 내장 PostgreSQL 사용 시 생략 가능.

#### Neon 사용 시

1. [Neon Console](https://console.neon.tech) 로그인
2. **Create Project** → `hr-dss`
3. 연결 문자열 복사:

```
postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/hr_dss?sslmode=require
```

4. Railway `DATABASE_URL`에 설정

---

## 6. DNS 설정

### 6.1 Cloudflare DNS 레코드 추가

Cloudflare Dashboard → `minu.best` → **DNS** → **Add record**

> ⚠️ **중요**: Cloudflare Universal SSL은 1단계 서브도메인(`*.minu.best`)만 커버합니다.
> 따라서 `api.hr.minu.best` 대신 `api-hr.minu.best`를 사용합니다.

| Type  | Name          | Content                                           | Proxy     | 상태 |
| ----- | ------------- | ------------------------------------------------- | --------- | ---- |
| CNAME | `hr`          | `hr-dss-web.pages.dev`                            | ✓ Proxied | ✅   |
| CNAME | `staging`     | `hr-dss-web.pages.dev`                            | ✓ Proxied | ✅   |
| CNAME | `api-hr`      | `hr-dss-api-gateway.sinclair-account.workers.dev` | ✓ Proxied | ✅   |
| CNAME | `api-staging` | `hr-dss-api-gateway.sinclair-account.workers.dev` | ✓ Proxied | 🔄   |

**실제 배포 URL:**

- Pages: `hr-dss-web.pages.dev`
- Workers: `hr-dss-api-gateway.sinclair-account.workers.dev`

### 6.2 SSL/TLS 설정

1. Cloudflare → `minu.best` → **SSL/TLS**
2. **Overview** → **Full (strict)** 선택
3. **Edge Certificates** → 설정 확인:

| 항목                | 값              |
| ------------------- | --------------- |
| Always Use HTTPS    | ✓ On            |
| Minimum TLS Version | TLS 1.2         |
| TLS 1.3             | ✓ On            |
| HSTS                | ✓ Enable (권장) |

---

## 7. 검증

### 7.1 배포 확인

```bash
# Frontend 확인
curl -I https://hr.minu.best

# API Gateway 확인 (1단계 서브도메인 사용)
curl https://api-hr.minu.best/health

# API 정보 확인
curl https://api-hr.minu.best/api

# Backend 확인 (Workers 경유 - Railway 배포 후)
curl https://api-hr.minu.best/api/v1/health
```

### 7.2 예상 응답

**Frontend** (`https://hr.minu.best`): ✅ 확인됨

```
HTTP/1.1 200 OK
content-type: text/html; charset=utf-8
```

**API Gateway** (`https://api-hr.minu.best/health`): ✅ 확인됨

```json
{
  "status": "healthy",
  "service": "hr-dss-api-gateway",
  "timestamp": "2026-01-22T04:16:46.770Z"
}
```

**API Info** (`https://api-hr.minu.best/api`): ✅ 확인됨

```json
{
  "name": "HR-DSS API Gateway",
  "version": "0.1.0",
  "environment": "production",
  "endpoints": {
    "health": "/health",
    "api": "/api/v1/*",
    "agents": "/api/v1/agents/*",
    "decisions": "/api/v1/decisions/*",
    "graph": "/api/v1/graph/*"
  }
}
```

**Backend API** (`https://api-hr.minu.best/api/v1/health`): 🔄 Railway 배포 필요

```json
{
  "status": "healthy",
  "service": "hr-dss-api",
  "version": "0.2.0",
  "environment": "production"
}
```

---

## 8. 체크리스트

### 8.1 Cloudflare

- [x] 계정 로그인 확인
- [x] `minu.best` 도메인 등록 확인
- [ ] API Token 생성 (CI/CD용)
- [x] Account ID 확인: `02ae9a2bead25d99caa8f3258b81f568`
- [x] Pages 프로젝트 생성 (`hr-dss-web`)
- [x] Workers 첫 배포 (`hr-dss-api-gateway`)

### 8.2 GitHub

- [ ] `CLOUDFLARE_API_TOKEN` 설정
- [ ] `CLOUDFLARE_ACCOUNT_ID` 설정
- [ ] `RAILWAY_TOKEN` 설정

### 8.3 Railway

- [ ] 프로젝트 생성
- [ ] GitHub 연결
- [ ] 환경 변수 설정
- [ ] Token 생성

### 8.4 데이터베이스

- [ ] Neo4j Aura 인스턴스 생성
- [ ] 연결 정보 Railway에 등록
- [ ] (선택) Neon PostgreSQL 설정

### 8.5 DNS

- [x] `hr` CNAME 레코드 추가 → https://hr.minu.best ✅
- [x] `staging` CNAME 레코드 추가 → https://staging.hr.minu.best ✅
- [x] `api-hr` CNAME 레코드 추가 → https://api-hr.minu.best ✅
- [ ] `api-staging` CNAME 레코드 추가
- [x] SSL/TLS 설정 확인
- [x] DNS 전파 확인

---

## 9. 트러블슈팅

### 9.1 Pages 배포 실패

**증상**: Build failed
**해결**:

1. Build command 확인: `cd apps/web && pnpm install && pnpm build`
2. Node version 20 설정 확인
3. `next.config.js`의 `output: 'export'` 확인

### 9.2 Workers 배포 실패

**증상**: wrangler deploy 에러
**해결**:

```bash
wrangler login  # 재로그인
wrangler deploy --env production
```

### 9.3 Railway 배포 실패

**증상**: Build/Start failed
**해결**:

1. Dockerfile 경로 확인
2. Start command 확인: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
3. `backend/api/main.py` 파일 존재 확인 (Phase 1 완료 필요)

### 9.4 DNS 연결 안됨

**증상**: ERR_NAME_NOT_RESOLVED
**해결**:

1. DNS 전파 대기 (최대 24-48시간)
2. `dig hr.minu.best` 로 확인
3. Cloudflare Proxy 상태 확인 (주황색 구름)

### 9.5 SSL 인증서 오류 (2단계 서브도메인)

**증상**: `api.hr.minu.best` 접속 시 SSL handshake 실패
**원인**: Cloudflare Universal SSL은 `*.minu.best` (1단계)만 커버

**해결**:

1. **권장**: 1단계 서브도메인 사용 (`api-hr.minu.best`)
2. **대안**: Advanced Certificate Manager 구매 (유료)

```bash
# 변경 전 (SSL 미지원)
api.hr.minu.best     # 2단계 서브도메인

# 변경 후 (SSL 지원)
api-hr.minu.best     # 1단계 서브도메인
```

### 9.6 Workers itty-router 오류

**증상**: Error 1101 - Worker threw exception
**원인**: itty-router v5 API 변경

**해결**:

```typescript
// 변경 전 (v4)
import { Router } from "itty-router";
const router = Router();
router.handle(request, env, ctx);

// 변경 후 (v5)
import { AutoRouter } from "itty-router";
const router = AutoRouter();
router.fetch(request, env, ctx);
```

---

## 10. 다음 단계

인프라 설정 완료 후:

1. Phase 1 코드 완성 확인
2. Phase 3: 배포 및 검증 진행
3. E2E 테스트 실행
