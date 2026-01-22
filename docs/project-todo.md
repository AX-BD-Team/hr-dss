# HR 의사결정 지원 시스템 - 작업 체크리스트

> 마지막 업데이트: 2026-01-21

---

## 마일스톤 현황

| 마일스톤           | 날짜 | 검증 기준                                           | 상태    |
| ------------------ | ---- | --------------------------------------------------- | ------- |
| M1: 기반 완성      | 1/22 | PoC Charter + Question Set + Decision Criteria 확정 | ✅ 완료 |
| M2: 데이터 준비    | 1/23 | Data Readiness Dashboard 동작, Mock 데이터 6종      | ✅ 완료 |
| M3: KG 구축 완료   | 1/24 | Neo4j에서 Cypher 쿼리 가능, Graph Viewer 동작       | ✅ 완료 |
| M4: 질문 응답 가능 | 1/27 | A-1(12주 병목) 질문에 3안 생성 + 비교 가능          | ✅ 완료 |
| M5: 에이전트 동작  | 1/28 | Agent Eval + Ontology Eval 대시보드 동작            | ✅ 완료 |
| M6: UI 완성        | 1/29 | 전체 플로우 데모 가능                               | ✅ 완료 |
| M7: Prototype 완성 | 1/30 | PoC Final Report 완성                               | ✅ 완료 |

---

## Day 1: 1/22 (수) - P0. Kick-off + P1. Key Questions ✅

### P0: Kick-off

- [x] **0.1** PoC Charter 확정 → `docs/specs/poc-charter.md`
- [x] **0.2** Steering/Working Group 구성 → 운영체계/R&R 문서 (poc-charter.md 내 포함)
- [ ] **0.3** 예산 항목표 + SoW 초안 (별도 진행)

### P1: Key Questions

- [x] **1.1** Key Question 5개 확정 (3단계 대화 흐름) → `docs/specs/question-set.md`
- [x] **1.2** 의사결정 기준/스코어링 정의 → `docs/specs/decision-criteria.md`
- [x] **1.3** Acceptance Criteria/KPI 확정 → `docs/specs/kpi-acceptance.md`

### Day 1 체크포인트

- [x] PoC Charter v1 완성
- [x] Question Set v1 (4개 핵심 질문 + 입력/출력 형식)
- [x] Decision Criteria Spec (영향도/성공확률 산정 기준)
- [x] KPI & Acceptance Criteria v1

---

## Day 2: 1/23 (목) - P2. Data Readiness & 거버넌스 ✅

### P2: Data Readiness

- [x] **2.1** 데이터 인벤토리/스키마 정리 → `docs/specs/data-catalog.md`
- [x] **2.2** Join Key 표준 확정 → `docs/specs/join-key-standard.md`
- [x] **2.3** 개인정보/민감정보 범위 확정 → `docs/specs/data-classification.md`
- [x] **2.4** Data Readiness Scorecard 구현 → `backend/agent_runtime/data_quality/`
- [x] **2.5** Mock 데이터 6종 생성:
  - [x] `data/mock/persons.json` (65명)
  - [x] `data/mock/projects.json` (12개 프로젝트, 30개 WP)
  - [x] `data/mock/skills.json` (40개 역량, 50개 증거)
  - [x] `data/mock/orgs.json` (20개 조직)
  - [x] `data/mock/opportunities.json` (15개 기회)
  - [x] `data/mock/assignments.json` (42개 배치, 30개 가용성)

### Day 2 체크포인트

- [x] Data Catalog v1 완성 (29개 엔터티 스키마)
- [x] Join Key Standard + 매핑 테이블
- [x] Data Readiness Scorecard (100% READY)
- [x] Mock Dataset 6종 생성 완료 (총 356개 레코드)

---

## Day 3: 1/24 (금) - P3. Predictive Enablement + P4. Ontology/KG ✅

### P3: Predictive Enablement

- [x] **3.1** Outcome(성공/실패) 정의 → `docs/specs/outcome-definition.md`
- [x] **3.2** 라벨 데이터 샘플 구축 → `data/labeled/`
  - [x] `data/labeled/project_outcomes.json` (20건)
  - [x] `data/labeled/capacity_outcomes.json` (24건)
- [x] **3.3** Demand Data Spec 정의 → `docs/specs/demand-data-spec.md`
- [ ] **3.4** VRB Decision Capture Spec (추후 진행)

### P4: Ontology/KG

- [x] **4.1** Ontology v0.1.1 Neo4j 스키마 생성 → `data/schemas/schema.cypher`
- [x] **4.2** 데이터 적재 파이프라인 → `backend/agent_runtime/ontology/data_loader.py`
- [x] **4.3** KG 생성 + Evidence 연결 → `backend/agent_runtime/ontology/kg_query.py`
- [x] **4.4** KG 시각화 뷰 → `apps/web/components/GraphViewer.tsx`

### Day 3 체크포인트

- [x] Outcome Definition v1 완성
- [x] Labeled Dataset v1 (44건: 프로젝트 20건 + 가동률 24건)
- [x] Demand Data Spec v1
- [x] Neo4j KG 스키마 및 데이터 로더 완료
- [x] Graph Viewer UI 컴포넌트 완료

---

## Day 4: 1/27 (월) - P5. LLM/Agent 의사결정 엔진 ✅

### P5: Agent Framework

- [x] **5.1** Query Decomposition Agent → `backend/agent_runtime/agents/query_decomposition.py`
- [x] **5.2** Option Generator Agent (대안 3개) → `backend/agent_runtime/agents/option_generator.py`
- [x] **5.3** Impact Simulator (As-Is vs To-Be) → `backend/agent_runtime/agents/impact_simulator.py`
- [x] **5.4** Success Probability (휴리스틱+모델) → `backend/agent_runtime/agents/success_probability.py`
- [x] **5.5** Validator (근거 없는 주장 탐지) → `backend/agent_runtime/agents/validator.py`

### Day 4 체크포인트

- [x] Query Decomposition Agent 동작 (4개 질문 유형 지원)
- [x] Option Generator Agent (3안 생성: 보수적/균형/적극적)
- [x] Impact Simulator (As-Is vs To-Be 비교, 시계열 예측)
- [x] Success Probability Agent (휴리스틱 기반 성공 확률)
- [x] Validator (근거 연결 검증, 환각 위험도 탐지)

---

## Day 5: 1/28 (화) - P6. Workflow + 평가 시스템 ✅

### P6: Workflow

- [x] **6.1** Workflow Builder Agent → `backend/agent_runtime/agents/workflow_builder.py`
- [x] **6.2** HITL 승인/Decision Log → `backend/agent_runtime/workflows/hitl_approval.py`

### P7: 평가 시스템

- [x] **7.1** Agent Eval 시스템 → `apps/web/components/AgentEvalDashboard.tsx`
- [x] **7.2** Ontology/KG Eval 시스템 → `apps/web/components/OntologyScoreCard.tsx`
- [x] **7.3** Data Quality Eval 연동 → `apps/web/components/DataQualityReport.tsx`

### Day 5 체크포인트

- [x] Workflow Builder Agent 동작 (8단계 워크플로, HITL 중단/재개 지원)
- [x] HITL 승인 시스템 + Decision Log (4단계 승인 레벨, 에스컬레이션)
- [x] Agent Eval Dashboard 동작 (5대 지표: 완결성/근거연결률/환각률/재현성/응답시간)
- [x] Ontology Scorecard 동작 (4대 지표: 커버리지/링크율/중복충돌/최신성)
- [x] Data Quality ↔ 성능 영향 분석 (상관관계 분석 포함)

---

## Day 6: 1/29 (수) - P7. 웹/앱 Prototype UI ✅

### P8: UI 구현

- [x] **8.1** Conversational UI + Scenario Builder → `apps/web/components/ConversationUI.tsx`
- [x] **8.2** Option Compare Dashboard → `apps/web/components/OptionCompare.tsx`
- [x] **8.3** Explanation Panel (근거/추론/가정) → `apps/web/components/ExplanationPanel.tsx`
- [x] **8.4** Eval Dashboard (운영자용) → `apps/web/components/EvalDashboard.tsx`

### Day 6 체크포인트

- [x] Conversational UI (질문 입력 + 시나리오 프리셋 + 제약조건 설정)
- [x] Option Compare Dashboard (3안 비교, 레이더 차트, ROI 분석)
- [x] Explanation Panel (추론 경로 + Evidence + 가정 + 검증 + KG 뷰)
- [x] Eval Dashboard (시스템 헬스, 알림, 활동 피드, 빠른 이동)

---

## Day 7: 1/30 (목) - P8. 검증 + 결과 리포트 ✅

### P9: 검증 및 리포트

- [x] **9.1** 기존 방식 vs PoC 비교 (베이스라인) → `docs/reports/comparison-report.md`
- [x] **9.2** 사용자 리뷰 + 개선 반영 → 피드백 로그 + 개선 백로그 (poc-final-report.md 내 포함)
- [x] **9.3** 최종 결과서 + 로드맵 → `docs/reports/poc-final-report.md`
- [x] **9.4** API 문서 + 사용자 가이드 → `docs/api-docs.md`, `docs/user-guide.md`

### Day 7 체크포인트

- [x] 정량 비교 리포트 (시간/단계/품질)
- [x] 피드백 로그 + 개선 백로그
- [x] **PoC Final Report** 완성
- [x] Documentation Set 완성

---

## 평가 지표 목표

### Agent 평가 지표

| 지표        | 설명                      | 목표  |
| ----------- | ------------------------- | ----- |
| 완결성      | 질문에 대한 답변 완성도   | > 90% |
| 근거 연결률 | 주장에 Evidence 연결 비율 | > 95% |
| 환각률      | 근거 없는 주장 비율       | < 5%  |
| 재현성      | 동일 입력 시 동일 결과    | > 95% |
| 응답 시간   | 답변 생성 시간            | < 30s |

### Ontology/KG 평가 지표

| 지표            | 설명                  | 목표  |
| --------------- | --------------------- | ----- |
| 엔터티 커버리지 | 필수 노드 존재 비율   | 100%  |
| 링크율          | 고아 노드 없는 비율   | > 95% |
| 중복/충돌       | 키 충돌 비율          | 0%    |
| 최신성          | 데이터 갱신 주기 준수 | > 90% |

### Data Readiness 지표

| 지표            | 설명                                 | 목표  |
| --------------- | ------------------------------------ | ----- |
| 결측률          | 필수 필드 결측 비율                  | < 10% |
| 중복률          | 키 중복 비율                         | < 1%  |
| 키 매칭률       | 사번/조직코드/프로젝트키 연결 성공률 | > 95% |
| 필수필드 충족률 | 질문별 Required Fields 충족          | > 80% |
