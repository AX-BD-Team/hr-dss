# HR 의사결정 지원 시스템 Prototype

> Claude와의 개발 협업을 위한 프로젝트 핵심 문서

**현재 버전**: 0.2.1 | **상태**: ✅ Prototype Complete | **방법론**: SSDD
**기간**: 2025.01.22 ~ 2025.01.30 (평일 7일) | **목표**: PoC 준비를 위한 Prototype 구현

---

## 🎯 개발 방법론

**SSDD (Skillful Spec-Driven Development)** = SDD + Claude Skills Integration

| Skill           | 용도                 | 산출물             |
| --------------- | -------------------- | ------------------ |
| ontology-design | Ontology 스키마 설계 | schema.cypher      |
| data-loader     | KG 데이터 적재       | data-loader.ts     |
| agent-eval      | 에이전트 평가        | AgentEvalDashboard |

**문서 인덱스**: [docs/INDEX.md](docs/INDEX.md)

---

## 📜 프로젝트 헌법

핵심 가치:

- **팔란티어 수준 예측**: 목표/제약 기반 복수 데이터 연결을 통한 예측+시뮬레이션+처방
- **근거 기반 의사결정**: ModelRun + Finding + Evidence로 모든 추론 추적 가능
- **HITL (Human-in-the-Loop)**: DecisionGate/Approval을 통한 승인 후 Workflow 연결

기술 원칙:

- TDD (Test-Driven Development)
- 컴포넌트 단일 책임 원칙
- Evidence-first: 근거 없는 주장 금지

---

## 🤖 AI 협업 규칙

### 언어 원칙

- **모든 출력은 한글로 작성**: 코드 주석, 커밋 메시지, 문서, 대화 응답
- **예외**: 코드 변수명, 함수명, 기술 용어는 영문 유지

### 날짜/시간 원칙

- **기준 시간대**: KST (Korea Standard Time, UTC+9)
- **날짜 표기**: YYYY-MM-DD 형식
- **마이그레이션 파일명**: YYYYMMDDHHMMSS 형식 (UTC 기준)
- **현재 날짜 확인**: 시스템 프롬프트의 `Today's date` 참조
- **문서 업데이트 시**: 반드시 현재 날짜로 `마지막 업데이트` 갱신

### 컨텍스트 관리

- **태스크마다 새 대화 시작**: 이전 대화의 오염 방지
- **명세 참조로 컨텍스트 제공**: 대화 히스토리 대신 명세 파일 공유
- **관련 파일만 공유**: 전체 코드베이스가 아닌 필요한 파일만

### 작업 체크리스트

**작업 전**: 관련 명세 검토, 아키텍처 확인, 작업 분해
**작업 후**: CLAUDE.md 업데이트, project-todo.md 체크

### 작업 실행 원칙

- **병렬 작업 우선**: 독립적인 작업은 항상 병렬로 진행
- **효율성 극대화**: 의존성 없는 도구 호출은 동시에 실행

### 문서 효율화 원칙

- **중복 금지**: 정보는 한 곳에만 기록, 다른 곳에서는 링크 참조
- **링크 우선**: 상세 내용은 별도 문서로 분리 후 링크
- **헤더 통합**: 버전/상태/방법론 등 메타데이터는 문서 헤더에 통합
- **아카이브 활용**: 히스토리는 `docs/archive/`로 이동, 최신 요약만 유지
- **단일 책임**: 각 문서는 하나의 명확한 목적만 가짐

---

## 🔧 Sub Agent & Skills 시스템

### 사용 가능한 Sub Agent

| Agent               | 용도                               | 자동 호출 조건       |
| ------------------- | ---------------------------------- | -------------------- |
| orchestrator        | 워크플로 실행 및 서브에이전트 조율 | 모든 Command 실행 시 |
| query-decomposition | 질문 분해 (목표/제약/기간 추출)    | 자연어 질문 입력 시  |
| option-generator    | 대안 3개 생성 (내부/혼합/역량강화) | 의사결정 요청 시     |
| impact-simulator    | As-Is vs To-Be 가동률 시뮬레이션   | 옵션 비교 요청 시    |
| success-probability | 휴리스틱+모델 기반 성공확률 산출   | 옵션 평가 시         |
| validator           | 근거 연결 검증 (환각 탐지)         | 응답 생성 후         |
| workflow-builder    | 실행 계획 및 Workflow 생성         | 승인 완료 후         |

### 사용 가능한 Skills

| Skill              | 용도                     | 키워드   |
| ------------------ | ------------------------ | -------- |
| capacity-forecast  | 12주 가동률 병목 예측    | A-1 질문 |
| go-nogo            | Go/No-go + 성공확률 분석 | B-1 질문 |
| headcount-analysis | 증원 원인분해            | C-1 질문 |
| competency-gap     | 역량 갭 분석 및 ROI      | D-1 질문 |

---

## 🔢 버전 관리

**형식**: Major.Minor.Patch (Semantic Versioning)

| 버전          | 변경 기준         | 승인                |
| ------------- | ----------------- | ------------------- |
| Major (X.0.0) | Breaking Changes  | ⚠️ 사용자 승인 필수 |
| Minor (0.X.0) | 새로운 기능 추가  | 자동                |
| Patch (0.0.X) | 버그 수정, Hotfix | 자동                |

```bash
npm run release:patch  # 패치 버전
npm run release:minor  # 마이너 버전
npm run release:major  # 메이저 버전
```

### 버전 동기화 원칙

**package.json/pyproject.toml 버전과 GitHub Tag/Release는 반드시 일치해야 합니다.**

| 항목           | 위치                              | 동기화      |
| -------------- | --------------------------------- | ----------- |
| 시스템 버전    | `package.json` / `pyproject.toml` | 기준값      |
| GitHub Tag     | `git tag vX.X.X`                  | 자동 동기화 |
| GitHub Release | `gh release create`               | 자동 동기화 |

---

## 📋 프로젝트 개요

**HR 의사결정 지원 시스템 Prototype**은 PoC 준비를 위한 "팔란티어 수준 예측" 가능성 검증 시스템입니다.

**핵심 가치 제안**:

- 복수 데이터 연결: BizForce(수요) ↔ TMS(공급) ↔ R&R ↔ HR Master ↔ Cost/Risk/Outcome
- 예측+시뮬레이션+처방: ForecastPoint → Option/Scenario/Action → Evaluation/MetricValue
- 근거/감사 가능: ModelRun + Finding + Evidence로 추적

**4대 유스케이스**:
| ID | 유형 | 질문 예시 |
|----|------|----------|
| A-1 | 12주 Capacity 병목 | "향후 12주 본부/팀별 가동률 90% 초과 주차와 병목 원인 예측" |
| B-1 | Go/No-go + 성공확률 | "'100억 미디어 AX' 내부 수행 가능 여부와 성공확률" |
| C-1 | 증원 원인분해 | "OOO팀 1명 증원 요청의 원인분해" |
| D-1 | 역량 투자 ROI | "AI-driven 전환 관점 역량 갭 Top10 정량화" |

---

## 🛠️ 기술 스택

| 레이어            | 기술               | 버전     | 용도                        |
| ----------------- | ------------------ | -------- | --------------------------- |
| **Frontend**      | Next.js            | 14+      | React 기반 UI               |
| **Frontend**      | TypeScript         | 5.7+     | 타입 안전성                 |
| **Frontend**      | D3.js              | -        | Graph 시각화                |
| **Backend**       | Cloudflare Workers | -        | Edge Runtime                |
| **Backend**       | Hono               | -        | Web Framework               |
| **Runtime**       | Python             | 3.11+    | 백엔드/에이전트 런타임      |
| **Backend**       | FastAPI            | 0.115.0+ | REST API 서버               |
| **Agent SDK**     | Claude Agent SDK   | 0.1.19+  | 멀티에이전트 오케스트레이션 |
| **AI Model**      | Claude Sonnet 4    | 20250514 | LLM 추론 엔진               |
| **Database**      | Neo4j AuraDB       | -        | Ontology/Knowledge Graph    |
| **Database**      | Cloudflare D1      | -        | Metadata 저장소             |
| **Storage**       | Cloudflare R2      | -        | 파일 저장소                 |
| **Testing**       | pytest             | 8.3.0+   | 단위/통합 테스트            |
| **Linting**       | ruff               | 0.8.0+   | 코드 품질 검사              |
| **Type Checking** | mypy               | 1.13.0+  | 정적 타입 검사              |

---

## 📁 프로젝트 구조

```
hr-dss/
├── .claude/              # Claude Code 설정
│   ├── agents/          # 에이전트 정의 (7개)
│   ├── skills/          # Skills (4개 유스케이스)
│   ├── commands/        # Commands
│   ├── hooks/           # Tool use 훅
│   └── prompts/         # LLM 프롬프트 (Entity/Relation Extraction)
├── apps/
│   └── web/             # Next.js 14+ Frontend
│       ├── components/  # React 컴포넌트 (8개)
│       │   ├── ConversationUI.tsx
│       │   ├── OptionCompare.tsx
│       │   ├── ExplanationPanel.tsx
│       │   ├── GraphViewer.tsx
│       │   ├── EvalDashboard.tsx
│       │   ├── AgentEvalDashboard.tsx
│       │   ├── OntologyScoreCard.tsx
│       │   └── DataQualityReport.tsx
│       └── app/         # App Router (4개 페이지)
│           ├── page.tsx          # / 메인
│           ├── decisions/        # /decisions 의사결정
│           ├── dashboard/        # /dashboard 대시보드
│           └── graph/            # /graph KG 뷰어
├── backend/              # FastAPI 백엔드
│   ├── api/             # REST API 라우터
│   ├── agent_runtime/   # 에이전트 실행 환경
│   │   ├── agents/      # 6개 Agent 구현
│   │   ├── ontology/    # Ontology 스키마/검증
│   │   └── workflows/   # HITL Workflow
│   ├── database/        # Neo4j/D1 모델/리포지토리
│   ├── evals/           # Agent/Ontology 평가 시스템
│   └── core/            # 설정, 로깅
├── data/                 # 데이터
│   ├── mock/            # Mock 데이터 6종
│   ├── labeled/         # 라벨 데이터셋
│   └── schemas/         # Ontology Cypher 스키마
├── evals/                # 평가 정의 (YAML)
│   ├── schemas/         # JSON Schema
│   ├── suites/          # 평가 스위트
│   ├── tasks/           # 평가 과제
│   └── rubrics/         # LLM Judge 루브릭
├── tests/                # pytest 테스트
├── docs/                 # 문서
│   ├── INDEX.md         # 문서 인덱스
│   ├── specs/           # 명세 문서
│   └── reports/         # 결과 리포트
├── pyproject.toml        # Python 프로젝트 설정
├── package.json          # Node.js 프로젝트 설정
└── hr-prototype-plan-v2.md  # 개발 계획서
```

---

## 📝 참고사항

- **Import Alias**: `@/` → `src/` (Frontend), `backend/` (Python)
- **코드 컨벤션**: PascalCase (컴포넌트), camelCase (함수/훅), kebab-case (파일)
- **문서 인덱스**: [docs/INDEX.md](docs/INDEX.md)
- **개발 계획**: [hr-prototype-plan-v2.md](hr-prototype-plan-v2.md)
- **Ontology 스키마**: 28개 노드, 30+ 관계 타입 ([스키마 상세](hr-prototype-plan-v2.md#33-핵심-관계-edge))

---

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (\*.md) or README files.

# Context Engineering

당신은 최신 스택이 빠르게 변하는 프로젝트에서 작업하는 AI 개발자입니다.

1. **환경 파악**: package.json, 구성 파일을 읽고 프레임워크·라이브러리 버전 확인
2. **버전 차이 대응**: 릴리스 노트 참조, 최신 권장사항 확인
3. **설계 시 체크**: 네트워크 리소스, 인증/데이터 레이어 호환성 고려
4. **구현 중 검증**: 린트/타입/빌드 명령 실행, 예상 오류 미리 보고
5. **결과 전달**: 버전 차이 반영 사항, 추가 확인 항목 명시
