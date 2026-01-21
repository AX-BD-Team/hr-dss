# HR 의사결정 지원 시스템 (HR-DSS)

> 팔란티어 수준 예측을 목표로 하는 HR 의사결정 지원 시스템 Prototype

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/AX-BD-Team/hr-dss)
[![Status](https://img.shields.io/badge/status-Development-yellow.svg)]()
[![License](https://img.shields.io/badge/license-Private-red.svg)]()

## 개요

**HR-DSS**는 복수 데이터 연결을 통한 예측, 시뮬레이션, 처방 기능을 제공하는 HR 의사결정 지원 시스템입니다.

### 핵심 가치

- **복수 데이터 연결**: BizForce(수요) ↔ TMS(공급) ↔ R&R ↔ HR Master ↔ Cost/Risk/Outcome
- **예측+시뮬레이션+처방**: ForecastPoint → Option/Scenario/Action → Evaluation/MetricValue
- **근거/감사 가능**: ModelRun + Finding + Evidence로 모든 추론 추적

## 4대 유스케이스

| ID | 유형 | 질문 예시 |
|----|------|----------|
| **A-1** | 12주 Capacity 병목 | "향후 12주 본부/팀별 가동률 90% 초과 주차와 병목 원인 예측" |
| **B-1** | Go/No-go + 성공확률 | "'100억 미디어 AX' 내부 수행 가능 여부와 성공확률" |
| **C-1** | 증원 원인분해 | "OOO팀 1명 증원 요청의 원인분해" |
| **D-1** | 역량 투자 ROI | "AI-driven 전환 관점 역량 갭 Top10 정량화" |

## 기술 스택

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 백엔드/에이전트 런타임 |
| FastAPI | 0.115.0+ | REST API 서버 |
| Claude Agent SDK | 0.1.19+ | 멀티에이전트 오케스트레이션 |
| Neo4j AuraDB | - | Ontology/Knowledge Graph |

### Frontend
| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 14+ | React 기반 UI |
| TypeScript | 5.7+ | 타입 안전성 |
| D3.js | - | Graph 시각화 |

### Infrastructure
| 기술 | 용도 |
|------|------|
| Cloudflare Workers | Edge Runtime |
| Cloudflare D1 | Metadata 저장소 |
| Cloudflare R2 | 파일 저장소 |

## 프로젝트 구조

```
hr-dss/
├── .claude/              # Claude Code 설정
│   ├── agents/          # 에이전트 정의 (7개)
│   ├── skills/          # Skills (6개)
│   └── prompts/         # LLM 프롬프트
├── backend/              # FastAPI 백엔드
│   ├── api/             # REST API 라우터
│   ├── agent_runtime/   # 에이전트 실행 환경
│   └── database/        # Neo4j/D1 모델
├── data/                 # 데이터
│   ├── mock/            # Mock 데이터
│   └── schemas/         # Ontology 스키마
├── evals/                # 평가 정의 (YAML)
├── tests/                # pytest 테스트
└── docs/                 # 문서
```

## 시작하기

### 사전 요구사항

- Python 3.11+
- Node.js 20+
- pnpm 9+

### 설치

```bash
# 저장소 클론
git clone https://github.com/AX-BD-Team/hr-dss.git
cd hr-dss

# Python 의존성 설치
pip install -e ".[dev]"

# Node.js 의존성 설치
pnpm install
```

### 환경 설정

```bash
# 환경 변수 설정
cp .env.example .env

# 필요한 값 설정
# - ANTHROPIC_API_KEY
# - NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD
```

### 실행

```bash
# Backend 실행
uvicorn backend.main:app --reload

# Frontend 실행 (별도 터미널)
pnpm dev
```

## 에이전트 시스템

### Sub Agents

| Agent | 용도 |
|-------|------|
| orchestrator | 워크플로 실행 및 서브에이전트 조율 |
| query-decomposition | 질문 분해 (목표/제약/기간 추출) |
| option-generator | 대안 3개 생성 (내부/혼합/역량강화) |
| impact-simulator | As-Is vs To-Be 가동률 시뮬레이션 |
| success-probability | 휴리스틱+모델 기반 성공확률 산출 |
| validator | 근거 연결 검증 (환각 탐지) |
| workflow-builder | 실행 계획 및 Workflow 생성 |

### Skills

| Skill | 용도 | 유스케이스 |
|-------|------|-----------|
| capacity-forecast | 12주 가동률 병목 예측 | A-1 |
| go-nogo | Go/No-go + 성공확률 분석 | B-1 |
| headcount-analysis | 증원 원인분해 | C-1 |
| competency-gap | 역량 갭 분석 및 ROI | D-1 |
| project-plan | 프로젝트 계획 수립 | - |
| project-cleanup | 프로젝트 정리 (테스트/커밋) | - |

## 테스트

```bash
# 전체 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest --cov=backend --cov-report=term-missing

# 타입 검사
mypy backend/

# 린트
ruff check .
```

## 문서

- [CLAUDE.md](CLAUDE.md) - Claude 협업 가이드
- [docs/INDEX.md](docs/INDEX.md) - 문서 인덱스
- [hr-prototype-plan-v2.md](hr-prototype-plan-v2.md) - 개발 계획서

## 라이선스

Private - AX BD Team 내부 사용

---

**개발 기간**: 2025.01.22 ~ 2025.01.30 (평일 7일)
**방법론**: SSDD (Skillful Spec-Driven Development)
