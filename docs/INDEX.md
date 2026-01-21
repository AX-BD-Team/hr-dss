# HR 의사결정 지원 시스템 - 문서 인덱스

> 마지막 업데이트: 2025-01-22

---

## 핵심 문서

| 문서 | 설명 | 상태 |
|------|------|------|
| [CLAUDE.md](../CLAUDE.md) | 프로젝트 개발 문서 (AI 협업 규칙) | ✅ 완료 |
| [개발 계획서](../hr-prototype-plan-v2.md) | Prototype 개발 계획 (WBS 포함) | ✅ 완료 |
| [project-todo.md](./project-todo.md) | 일별 작업 체크리스트 | 🚧 진행중 |

---

## Phase별 산출물

### P0-P1: Kick-off + Key Questions (1/22)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| PoC Charter v1 | [docs/specs/poc-charter.md](./specs/poc-charter.md) | ✅ 완료 |
| Question Set v1 | [docs/specs/question-set.md](./specs/question-set.md) | ✅ 완료 |
| Decision Criteria Spec | [docs/specs/decision-criteria.md](./specs/decision-criteria.md) | ✅ 완료 |
| KPI & Acceptance Criteria | [docs/specs/kpi-acceptance.md](./specs/kpi-acceptance.md) | ✅ 완료 |

### P2: Data Readiness (1/23)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| Data Catalog v1 | `docs/specs/data-catalog.md` | ⏳ 예정 |
| Join Key Standard | `docs/specs/join-key-standard.md` | ⏳ 예정 |
| Mock Dataset 6종 | `data/mock/*.json` | ⏳ 예정 |

### P3-P4: Predictive Enablement + KG (1/24)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| Outcome Definition v1 | `docs/specs/outcome-definition.md` | ⏳ 예정 |
| Demand Data Spec v1 | `docs/specs/demand-data-spec.md` | ⏳ 예정 |
| Ontology Schema v0.1.1 | `data/schemas/schema.cypher` | ⏳ 예정 |
| Labeled Dataset v1 | `data/labeled/*.json` | ⏳ 예정 |

### P5: LLM/Agent 의사결정 엔진 (1/27)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| Query Decomposition Agent | `backend/agent_runtime/agents/query_decomposition.py` | ⏳ 예정 |
| Option Generator Agent | `backend/agent_runtime/agents/option_generator.py` | ⏳ 예정 |
| Impact Simulator | `backend/agent_runtime/agents/impact_simulator.py` | ⏳ 예정 |
| Validator | `backend/agent_runtime/agents/validator.py` | ⏳ 예정 |

### P6: Workflow + 평가 시스템 (1/28)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| Workflow Builder Agent | `backend/agent_runtime/agents/workflow_builder.py` | ⏳ 예정 |
| HITL 승인 시스템 | `backend/agent_runtime/workflows/hitl_approval.py` | ⏳ 예정 |
| Agent Eval Dashboard | `apps/web/components/AgentEvalDashboard.tsx` | ⏳ 예정 |
| Ontology Scorecard | `apps/web/components/OntologyScoreCard.tsx` | ⏳ 예정 |

### P7: 웹/앱 Prototype UI (1/29)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| Conversational UI | `apps/web/components/ConversationUI.tsx` | ⏳ 예정 |
| Option Compare Dashboard | `apps/web/components/OptionCompare.tsx` | ⏳ 예정 |
| Explanation Panel | `apps/web/components/ExplanationPanel.tsx` | ⏳ 예정 |
| Graph Viewer | `apps/web/components/GraphViewer.tsx` | ⏳ 예정 |

### P8: 검증 + 결과 리포트 (1/30)

| 산출물 | 경로 | 상태 |
|--------|------|------|
| 정량 비교 리포트 | `docs/reports/comparison-report.md` | ⏳ 예정 |
| PoC Final Report | `docs/reports/poc-final-report.md` | ⏳ 예정 |
| API 문서 | `docs/api-docs.md` | ⏳ 예정 |

---

## 참조 문서

| 문서 | 설명 |
|------|------|
| [Ontology 스키마 상세](../hr-prototype-plan-v2.md#3-ontology-스키마-v011) | 28개 노드, 30+ 관계 타입 |
| [4대 유스케이스](../hr-prototype-plan-v2.md#42-4대-유스케이스) | A-1, B-1, C-1, D-1 질문 |
| [Agent 평가 지표](../hr-prototype-plan-v2.md#day-5-128-화---p6-workflow--평가-시스템) | 완결성, 근거 연결률, 환각률 등 |
