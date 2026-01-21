# HR 의사결정 지원 시스템 Prototype 개발 계획

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | HR 의사결정 지원 시스템 Prototype |
| 기간 | 2025.01.22 (수) ~ 2025.01.30 (목) / 평일 7일 |
| 목표 | PoC 준비를 위한 Prototype 구현 - **"팔란티어 수준 예측"** 가능성 검증 |
| 기술 스택 | Neo4j (Ontology/KG), LLM (Claude), Next.js, Cloudflare |

### 1.1 "팔란티어 수준 예측" 정의

| 요건 | 설명 |
|------|------|
| 목표/제약 기반 | DecisionCase에 Objective/Constraint를 구조적으로 저장 |
| 복수 데이터 연결 | BizForce(수요) ↔ TMS(공급) ↔ R&R ↔ HR Master ↔ Cost/Risk/Outcome |
| 예측+시뮬레이션+처방 | ForecastPoint → Option/Scenario/Action → Evaluation/MetricValue |
| 근거/감사 가능 | ModelRun + Finding + Evidence로 추적 |
| HITL+Workflow | DecisionGate/Approval 후 WorkflowTask로 실행 연결 |

---

## 2. 일정 요약

| 날짜 | 요일 | Phase | 핵심 작업 | 마일스톤 |
|------|------|-------|----------|----------|
| 1/22 | 수 | P0-P1 | Kick-off + Ontology 스키마 + Key Questions | M1: 기반 완성 |
| 1/23 | 목 | P2 | Data Readiness + Mock 데이터 생성 | M2: 데이터 준비 |
| 1/24 | 금 | P3-P4 | KG 구축 + Predictive Enablement | M3: KG 구축 완료 |
| 1/27 | 월 | P5 | LLM/Agent 의사결정 엔진 | M4: 질문 응답 가능 |
| 1/28 | 화 | P6 | Workflow + 평가 시스템 | M5: 에이전트 동작 |
| 1/29 | 수 | P7 | 웹/앱 Prototype UI | M6: UI 완성 |
| 1/30 | 목 | P8 | 검증 + 결과 리포트 | M7: Prototype 완성 |

---

## 3. Ontology 스키마 v0.1.1

### 3.1 핵심 모듈 구성

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HR 의사결정 지원 Ontology v0.1.1                   │
├─────────────────────────────────────────────────────────────────────┤
│  [Workforce & Org]     [Work & Portfolio]     [Demand & Supply]     │
│  Organization          Client/Industry        DemandSignal          │
│  OrgUnit               Opportunity            ResourceDemand        │
│  Employee              Project                Availability          │
│  JobRole               WorkPackage            Assignment            │
│  Position              WorkType               TimeBucket            │
├─────────────────────────────────────────────────────────────────────┤
│  [R&R / Coverage]      [Competency]           [Decision/Eval]       │
│  DeliveryRole          Competency             DecisionCase          │
│  Responsibility        CompetencyEvidence     Objective/Constraint  │
│  PRIMARY_FOR           CompetencyRequirement  Option/Scenario       │
│  BACKUP_FOR            LearningProgram        Action/Evaluation     │
├─────────────────────────────────────────────────────────────────────┤
│  [Forecast & Audit]                [HITL & Workflow]                │
│  Model/ModelRun                    DecisionGate                     │
│  ForecastPoint                     Approval                         │
│  Finding/Evidence                  WorkflowInstance                 │
│  DataSnapshot                      WorkflowTask                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 MVP 필수 노드 (28개)

| 모듈 | 노드 | Key | 필수 Props |
|------|------|-----|-----------|
| **Workforce** | OrgUnit | orgUnitId | name, type(본부/실/팀) |
| | Employee | employeeId | name, grade, status |
| | JobRole | jobRoleId | name, jobFamily, levelBand |
| **Work** | Opportunity | opportunityId | name, stage, expectedStartDate, dealValue |
| | Project | projectId | name, startDate, endDate, priority |
| | WorkPackage | workPackageId | name, startDate, endDate, criticality |
| **Demand** | DemandSignal | signalId | sourceSystem, closeProbability, expectedStartDate |
| | ResourceDemand | demandId | quantityFTE, startDate, endDate, **probability** |
| | Availability | availabilityId | availableFTE, reason, startDate, endDate |
| | Assignment | assignmentId | allocationFTE, startDate, endDate |
| | TimeBucket | bucketId | granularity=WEEK, startDate, endDate, year, week |
| **R&R** | DeliveryRole | deliveryRoleId | name (PM/아키텍트/데이터엔지니어 등) |
| | Responsibility | responsibilityId | name, criticality |
| **Competency** | Competency | competencyId | name, domain |
| | CompetencyEvidence | evidenceId | level, assessedAt, sourceType |
| **Decision** | DecisionCase | decisionCaseId | type, status, createdAt |
| | Objective | objectiveId | metricType, operator, targetValue |
| | Constraint | constraintId | type, severity, expression |
| | Option | optionId | name, optionType(Internal/Mixed/Upskill) |
| | Scenario | scenarioId | baselineSnapshotId, assumptions |
| | Action | actionId | type, owner, startDate, status |
| | Evaluation | evaluationId | totalScore, successProbability, rationale |
| | MetricValue | metricValueId | metricType, asIsValue, toBeValue, delta |
| **Forecast** | Model | modelId | name, type(heuristic/ml/rules), version |
| | ModelRun | runId | runAt, parameters, status, scenarioId |
| | ForecastPoint | forecastPointId | metricType, value, confidence |
| | Finding | findingId | type, severity, narrative, rootCause |
| | Evidence | evidenceId | sourceSystem, sourceType, sourceRef |
| **Workflow** | DecisionGate | gateId | process(VRB/Pre-PRB/PRB), status |
| | Approval | approvalId | decision, approvedBy, approvedAt |
| | WorkflowTask | taskId | type, owner, dueDate, status |

### 3.3 핵심 관계 (Edge)

```cypher
// 조직/인력
(OrgUnit)-[:HAS_SUB_UNIT]->(OrgUnit)
(Employee)-[:BELONGS_TO {startDate, endDate}]->(OrgUnit)
(Employee)-[:HAS_JOBROLE {startDate, endDate}]->(JobRole)

// 파이프라인/프로젝트
(Opportunity)-[:HAS_SIGNAL]->(DemandSignal)
(DemandSignal)-[:IMPLIES_DEMAND]->(ResourceDemand)
(Project)-[:HAS_WORKPACKAGE]->(WorkPackage)

// 수요/공급
(ResourceDemand)-[:FOR_BUCKET]->(TimeBucket)
(ResourceDemand)-[:REQUIRES_ROLE]->(DeliveryRole)
(Employee)-[:ASSIGNED_TO {allocationFTE, startDate, endDate}]->(WorkPackage|Project)
(Employee)-[:HAS_AVAILABILITY]->(Availability)

// R&R/대무 (핵심!)
(Employee)-[:PRIMARY_FOR {startDate, endDate}]->(Responsibility)
(Employee)-[:BACKUP_FOR {startDate, endDate}]->(Responsibility)
(Responsibility)-[:REQUIRES_ROLE]->(DeliveryRole)

// 역량
(Employee)-[:HAS_EVIDENCE]->(CompetencyEvidence)
(CompetencyEvidence)-[:FOR_COMPETENCY]->(Competency)

// 의사결정
(DecisionCase)-[:ABOUT]->(OrgUnit|Opportunity|Project)
(DecisionCase)-[:HAS_OBJECTIVE]->(Objective)
(DecisionCase)-[:HAS_CONSTRAINT]->(Constraint)
(DecisionCase)-[:HAS_OPTION]->(Option)
(Option)-[:HAS_SCENARIO]->(Scenario)
(Scenario)-[:INCLUDES_ACTION]->(Action)
(Option)-[:HAS_EVALUATION]->(Evaluation)
(Evaluation)-[:HAS_METRIC]->(MetricValue)

// 예측/근거
(ModelRun)-[:RUNS_MODEL]->(Model)
(ModelRun)-[:FOR_SCENARIO]->(Scenario)
(ModelRun)-[:OUTPUTS]->(ForecastPoint)
(ModelRun)-[:HAS_FINDING]->(Finding)
(Finding)-[:EVIDENCED_BY]->(Evidence)
(ForecastPoint)-[:FOR_BUCKET]->(TimeBucket)
(ForecastPoint)-[:FOR_SUBJECT]->(OrgUnit|Project)

// HITL/Workflow
(DecisionCase)-[:HAS_GATE]->(DecisionGate)
(DecisionGate)-[:HAS_APPROVAL]->(Approval)
(Approval)-[:TRIGGERS_WORKFLOW]->(WorkflowInstance)
(WorkflowTask)-[:RELATED_TO]->(Action)
```

---

## 4. 핵심 질문 (Key Questions)

### 4.1 공통 3단계 템플릿

| 단계 | 내용 | Output |
|------|------|--------|
| 1. 문제 정의 | Scope + Horizon + Objective + Constraint + KPI | 구조화된 요청서 |
| 2. 대안 탐색 | 3안(내부/혼합/역량강화) + As-Is vs To-Be 시뮬레이션 | Option 비교표 |
| 3. 보고/기획 | 1페이지 요약 + 실행계획 + HITL 승인 + Workflow | 실행 패키지 |

### 4.2 4대 유스케이스

| ID | 유형 | 질문 예시 | 핵심 Output |
|----|------|----------|-------------|
| A-1 | 12주 Capacity 병목 | "향후 12주 본부/팀별 가동률 90% 초과 주차와 병목 원인 예측" | ForecastPoint(UTILIZATION) + Finding(병목) |
| B-1 | Go/No-go + 성공확률 | "'100억 미디어 AX' 내부 수행 가능 여부와 성공확률" | ForecastPoint(SUCCESS_PROB, MARGIN) + Risk |
| C-1 | 증원 원인분해 | "OOO팀 1명 증원 요청의 원인분해" | Finding(rootCause) + Evidence |
| D-1 | 역량 투자 ROI | "AI-driven 전환 관점 역량 갭 Top10 정량화" | CompetencyGap + ImpactAssessment |

---

## 5. 상세 WBS (평일 7일)

### Day 1: 1/22 (수) - P0. Kick-off + P1. Key Questions

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 0.1 | PoC Charter 확정 | PoC Charter v1 |
| P0 | 0.2 | Steering/Working Group 구성 | 운영체계/R&R 문서 |
| P0 | 0.3 | 예산 항목표 + SoW 초안 | 예산 항목표, SoW 초안 |
| P0 | 1.1 | Key Question 5개 확정 (3단계 대화 흐름) | Question Set v1 |
| P0 | 1.2 | 의사결정 기준/스코어링 정의 | Decision Criteria Spec |
| P0 | 1.3 | Acceptance Criteria/KPI 확정 | KPI & Acceptance v1 |

**Day 1 Checklist:**
- [ ] PoC Charter v1
- [ ] Question Set v1 (5개 질문 + 입력/출력 형식)
- [ ] Decision Criteria Spec (영향도/성공확률 산정 기준)

---

### Day 2: 1/23 (목) - P2. Data Readiness & 거버넌스

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 2.1 | 데이터 인벤토리/스키마 정리 | Data Catalog v1 |
| P0 | 2.2 | Join Key 표준 확정 | Join Key Standard + 매핑 테이블 |
| P0 | 2.3 | 개인정보/민감정보 범위 확정 | Data Classification & Access Matrix |
| P0 | 2.4 | **Data Readiness Scorecard 구현** | Data Readiness Dashboard |
| P0 | 2.5 | Mock 데이터 6종 생성 | persons/projects/skills/orgs/opportunities/assignments.json |

**Data Readiness Scorecard 지표:**

| 지표 | 설명 | 목표 |
|------|------|------|
| 결측률 | 필수 필드 결측 비율 | < 10% |
| 중복률 | 키 중복 비율 | < 1% |
| 키 매칭률 | 사번/조직코드/프로젝트키 연결 성공률 | > 95% |
| 필수필드 충족률 | 질문별 Required Fields 충족 | > 80% |

**Day 2 Checklist:**
- [ ] Data Catalog v1
- [ ] Join Key Standard + 매핑 테이블
- [ ] Data Readiness Dashboard (UI)
- [ ] Mock Dataset 6종

---

### Day 3: 1/24 (금) - P3. Predictive Enablement + P4. Ontology/KG

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 3.1 | **Outcome(성공/실패) 정의** | Outcome Definition v1 |
| P0 | 3.2 | **라벨 데이터 샘플 구축** | Labeled Dataset v1 |
| P0 | 3.3 | **Demand Data Spec 정의** | Demand Data Spec v1 |
| P1 | 3.4 | VRB Decision Capture Spec | VRB Capture Spec |
| P0 | 4.1 | Ontology v0.1.1 Neo4j 스키마 생성 | schema.cypher |
| P0 | 4.2 | 데이터 적재 파이프라인 | data-loader.ts |
| P0 | 4.3 | KG 생성 + Evidence 연결 | Neo4j KG 완성 |
| P0 | 4.4 | KG 시각화 뷰 | GraphViewer.tsx |

**Outcome Definition 예시:**

| 프로젝트 성공 기준 | 측정 방법 | 데이터 소스 |
|-------------------|----------|-------------|
| 납기 준수 | 계획 종료일 vs 실제 종료일 | ERP/SAP |
| 마진 목표 달성 | 실제 마진 >= 목표 마진 | 정산 데이터 |
| 클레임 없음 | 계약 변동/클레임 건수 = 0 | 계약 관리 |

**Day 3 Checklist:**
- [ ] Outcome Definition v1
- [ ] Labeled Dataset v1 (최소 N건)
- [ ] Demand Data Spec v1
- [ ] Neo4j KG 적재 완료
- [ ] Graph Viewer UI

---

### Day 4: 1/27 (월) - P5. LLM/Agent 의사결정 엔진

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 5.1 | Query Decomposition Agent | question-parser.ts |
| P0 | 5.2 | Option Generator Agent (대안 3개) | option-generator.ts |
| P0 | 5.3 | Impact Simulator (As-Is vs To-Be) | impact-simulator.ts |
| P1 | 5.4 | Success Probability (휴리스틱+모델) | success-prob.ts |
| P0 | 5.5 | Validator (근거 없는 주장 탐지) | validator.ts |

**Agent 구조:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator                             │
├─────────────────────────────────────────────────────────────┤
│  [Query Decomposition]  →  [Option Generator]               │
│         ↓                         ↓                         │
│  목표/제약/기간 추출         3안 생성 (내부/혼합/역량강화)      │
│         ↓                         ↓                         │
│  [Impact Simulator]      →  [Success Probability]           │
│         ↓                         ↓                         │
│  As-Is vs To-Be 가동률      휴리스틱 + 모델 스코어            │
│         ↓                         ↓                         │
│  [Validator]             →  Evidence Coverage 검증           │
└─────────────────────────────────────────────────────────────┘
```

**Day 4 Checklist:**
- [ ] Query Decomposition Agent
- [ ] Option Generator Agent
- [ ] Impact Simulator (가동률 비교)
- [ ] Validator (근거 연결 검증)

---

### Day 5: 1/28 (화) - P6. Workflow + 평가 시스템

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 6.1 | Workflow Builder Agent | workflow-builder.ts |
| P0 | 6.2 | HITL 승인/Decision Log | hitl-approval.ts |
| P0 | 7.1 | **Agent Eval 시스템** | AgentEvalDashboard.tsx |
| P0 | 7.2 | **Ontology/KG Eval 시스템** | OntologyScoreCard.tsx |
| P0 | 7.3 | Data Quality Eval 연동 | DataQualityReport.tsx |

**Agent 평가 지표:**

| 지표 | 설명 | 목표 |
|------|------|------|
| 완결성 | 질문에 대한 답변 완성도 | > 90% |
| 근거 연결률 | 주장에 Evidence 연결 비율 | > 95% |
| 환각률 | 근거 없는 주장 비율 | < 5% |
| 재현성 | 동일 입력 시 동일 결과 | > 95% |
| 응답 시간 | 답변 생성 시간 | < 30s |

**Ontology/KG 평가 지표:**

| 지표 | 설명 | 목표 |
|------|------|------|
| 엔터티 커버리지 | 필수 노드 존재 비율 | 100% |
| 링크율 | 고아 노드 없는 비율 | > 95% |
| 중복/충돌 | 키 충돌 비율 | 0% |
| 최신성 | 데이터 갱신 주기 준수 | > 90% |

**Day 5 Checklist:**
- [ ] Workflow Builder Agent
- [ ] HITL 승인 UI + Decision Log
- [ ] Agent Eval Dashboard
- [ ] Ontology Scorecard
- [ ] Data Quality ↔ 성능 영향 분석

---

### Day 6: 1/29 (수) - P7. 웹/앱 Prototype UI

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 8.1 | Conversational UI + Scenario Builder | ConversationUI.tsx |
| P0 | 8.2 | Option Compare Dashboard | OptionCompare.tsx |
| P0 | 8.3 | Explanation Panel (근거/추론/가정) | ExplanationPanel.tsx |
| P1 | 8.4 | Eval Dashboard (운영자용) | EvalDashboard.tsx |

**UI 구성:**

```
┌─────────────────────────────────────────────────────────────────┐
│  HR 의사결정 지원 시스템                              [설정] [평가] │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐  ┌────────────────────────────────────┐ │
│ │  💬 Conversation    │  │  📊 Option Compare Dashboard       │ │
│ │                     │  │  ┌──────┬──────┬──────┐            │ │
│ │  Q: 12주 병목 예측   │  │  │ 1안  │ 2안  │ 3안  │            │ │
│ │                     │  │  │내부  │혼합  │역량↑ │            │ │
│ │  [제약 설정]        │  │  ├──────┼──────┼──────┤            │ │
│ │  [HITL 승인]        │  │  │가동률│      │      │            │ │
│ │                     │  │  │성공률│      │      │            │ │
│ │                     │  │  │리스크│      │      │            │ │
│ └─────────────────────┘  └────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │  🔍 Explanation Panel (근거/추론/가정)                      │   │
│ │  [Graph View] [Evidence List] [Reasoning Path]            │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Day 6 Checklist:**
- [ ] Conversational UI (질문 입력 + 제약 설정)
- [ ] Option Compare Dashboard (3안 비교)
- [ ] Explanation Panel (KG 뷰 + Evidence + 추론 경로)
- [ ] Eval Dashboard (운영자용)

---

### Day 7: 1/30 (목) - P8. 검증 + 결과 리포트

| 우선순위 | Task ID | Task | 산출물 |
|----------|---------|------|--------|
| P0 | 9.1 | 기존 방식 vs PoC 비교 (베이스라인) | 정량 비교 리포트 |
| P0 | 9.2 | 사용자 리뷰 + 개선 반영 | 피드백 로그 + 개선 백로그 |
| P0 | 9.3 | 최종 결과서 + 로드맵 | PoC Final Report |
| P0 | 9.4 | API 문서 + 사용자 가이드 | api-docs.md, user-guide.md |

**PoC 결과 리포트 구성:**

| 섹션 | 내용 |
|------|------|
| Executive Summary | 1페이지 요약 |
| 데이터 수준 진단 | Data Readiness Scorecard 결과 |
| 예측 가능성 검증 | 4대 유스케이스 테스트 결과 |
| Agent/Ontology 평가 | 평가 지표 달성률 |
| 발견된 문제점 | 데이터 갭, 프로세스 이슈 |
| 개선 로드맵 | 운영 전환/데이터·프로세스 개선 계획 |

**Day 7 Checklist:**
- [ ] 정량 비교 리포트 (시간/단계/품질)
- [ ] 피드백 로그 + 개선 백로그
- [ ] **PoC Final Report**
- [ ] Documentation Set

---

## 6. 마일스톤 체크포인트

| 마일스톤 | 날짜 | 검증 기준 |
|----------|------|-----------|
| M1: 기반 완성 | 1/22 저녁 | PoC Charter + Question Set + Decision Criteria 확정 |
| M2: 데이터 준비 | 1/23 저녁 | Data Readiness Dashboard 동작, Mock 데이터 6종 |
| M3: KG 구축 완료 | 1/24 저녁 | Neo4j에서 Cypher 쿼리 가능, Graph Viewer 동작 |
| M4: 질문 응답 가능 | 1/27 저녁 | A-1(12주 병목) 질문에 3안 생성 + 비교 가능 |
| M5: 에이전트 동작 | 1/28 저녁 | Agent Eval + Ontology Eval 대시보드 동작 |
| M6: UI 완성 | 1/29 저녁 | 전체 플로우 데모 가능 |
| M7: Prototype 완성 | 1/30 저녁 | PoC Final Report 완성 |

---

## 7. 산출물 목록

### 문서 산출물

| Phase | 산출물 | 완료일 |
|-------|--------|--------|
| P0 | PoC Charter v1 | 1/22 |
| P1 | Question Set v1 + Decision Criteria Spec | 1/22 |
| P2 | Data Catalog v1 + Join Key Standard | 1/23 |
| P3 | Outcome Definition v1 + Demand Data Spec | 1/24 |
| P4 | Ontology Spec v0.1.1 | 1/24 |
| P8 | PoC Final Report + 로드맵 | 1/30 |

### 시스템 산출물

| Phase | 산출물 | 완료일 |
|-------|--------|--------|
| P2 | Data Readiness Dashboard | 1/23 |
| P2 | Mock Dataset 6종 | 1/23 |
| P3 | Labeled Dataset v1 | 1/24 |
| P4 | Neo4j Knowledge Graph | 1/24 |
| P4 | Graph Viewer UI | 1/24 |
| P5 | Agent Framework (5개 Agent) | 1/27 |
| P6 | Workflow Engine + HITL 승인 | 1/28 |
| P6 | Agent Eval Dashboard | 1/28 |
| P6 | Ontology Scorecard | 1/28 |
| P7 | Decision Support Dashboard | 1/29 |

---

## 8. 기술 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                │
│  Next.js 14+ / React / TypeScript / Tailwind                   │
│  D3.js (Graph Viz) / Recharts (Charts)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                          Backend                                │
│  Cloudflare Workers / Hono                                     │
│  tRPC (Type-safe API)                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       AI/Agent Layer                            │
│  Claude API (LLM)                                              │
│  Custom Agent Framework (5 Agents + Orchestrator)              │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │  Query   │  Option  │  Impact  │ Success  │Validator │      │
│  │Decompose │Generator │Simulator │  Prob    │          │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                               │
│  Neo4j AuraDB (Ontology/KG)                                    │
│  - 28 Node Types / 30+ Relationship Types                      │
│  Cloudflare D1 (Metadata) / R2 (Storage)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. 리스크 및 대응 계획

| 리스크 | 영향도 | 발생 시 대응 |
|--------|--------|-------------|
| Day 2-3 지연 (데이터) | 높음 | Mock 데이터 규모 축소 (100명 → 50명) |
| Day 4 지연 (Agent) | 중간 | 5개 Agent → 3개 필수 (Query/Option/Simulator) |
| 라벨 데이터 확보 어려움 | 중간 | 휴리스틱 기반 스코어링으로 대체 |
| Ontology 스키마 변경 | 낮음 | Migration Script 준비 |
| 전체 지연 시 | - | 1/31(금)로 1일 연장 |

---

## 10. 관련 문서

| 문서명 | 링크 |
|--------|------|
| HR 의사결정 지원 PoC 기획안 | (링크) |
| Ontology 스키마 v0.1.1 | (링크) |
| VRB 프로세스 개선안 | (링크) |
| GitHub Repository | (링크) |

---

*작성일: 2025-01-21*
*작성자: Sinclair*
*버전: v2.0*
