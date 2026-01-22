# HR 의사결정 지원 시스템 - API 문서

> 마지막 업데이트: 2025-01-30
> 버전: 1.0

---

## 1. 개요

### 1.1 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Next.js)                 │
├─────────────────────────────────────────────────────────────────┤
│  ConversationUI │ OptionCompare │ ExplanationPanel │ Dashboard  │
└────────────────────────────────┬────────────────────────────────┘
                                 │ REST API
┌────────────────────────────────▼────────────────────────────────┐
│                      Agent Runtime (Python)                     │
├─────────────────────────────────────────────────────────────────┤
│  QueryDecomposition │ OptionGenerator │ ImpactSimulator │ ...   │
├─────────────────────────────────────────────────────────────────┤
│  WorkflowBuilder  │  HITL Approval System  │  Decision Log      │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Cypher Query
┌────────────────────────────────▼────────────────────────────────┐
│                     Knowledge Graph (Neo4j)                     │
│                   28개 노드 타입, 30+ 관계 타입                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Agent 개요

| Agent              | 역할            | 입력               | 출력               |
| ------------------ | --------------- | ------------------ | ------------------ |
| QueryDecomposition | 질문 분해       | 자연어 질문        | 하위 질의 목록     |
| OptionGenerator    | 대안 생성       | 분석 컨텍스트      | 3가지 대안         |
| ImpactSimulator    | 영향 시뮬레이션 | 대안 + 베이스라인  | As-Is vs To-Be     |
| SuccessProbability | 성공 확률 계산  | 기회/프로젝트 정보 | 성공 확률 + 리스크 |
| Validator          | 근거 검증       | 응답 텍스트        | 검증 결과          |
| WorkflowBuilder    | 워크플로 조율   | 질문 유형          | 실행 결과          |

---

## 2. Agent APIs

> 모든 Agent는 REST API endpoint를 통해 호출할 수 있습니다.

### 2.1 QueryDecompositionAgent

사용자 질문을 분석하여 실행 가능한 하위 질의로 분해합니다.

#### 클래스 정의

```python
from backend.agent_runtime.agents import QueryDecompositionAgent

agent = QueryDecompositionAgent(llm_client=None)
```

#### 메서드

**`decompose(query: str, context: dict | None = None) -> DecomposedQuery`**

| 파라미터  | 타입 | 필수 | 설명                                       |
| --------- | ---- | ---- | ------------------------------------------ |
| `query`   | str  | ✅   | 사용자 질문 (자연어)                       |
| `context` | dict | ❌   | 추가 컨텍스트 (org_unit_id, start_date 등) |

**반환값: `DecomposedQuery`**

```python
@dataclass
class DecomposedQuery:
    original_query: str       # 원본 질문
    query_type: QueryType     # CAPACITY, GO_NOGO, HEADCOUNT, COMPETENCY_GAP
    intent: str               # 질문 의도
    constraints: dict         # 추출된 제약조건
    sub_queries: list[SubQuery]  # 하위 질의 목록
    execution_order: list[str]   # 실행 순서
    confidence: float         # 분류 신뢰도 (0-1)
```

#### 지원 질문 유형

| 유형           | 키워드                    | 예시                                   |
| -------------- | ------------------------- | -------------------------------------- |
| CAPACITY       | 가동률, 병목, 12주        | "향후 12주간 AI팀의 가동률 병목은?"    |
| GO_NOGO        | go/no-go, 수주, 성공 확률 | "이 프로젝트를 수주해도 될까요?"       |
| HEADCOUNT      | 증원, 채용, 인원 부족     | "개발자 2명 증원이 타당한가요?"        |
| COMPETENCY_GAP | 역량 갭, 스킬 부족        | "데이터 엔지니어링 역량 갭을 분석해줘" |

#### 사용 예시

```python
agent = QueryDecompositionAgent()

result = agent.decompose(
    query="향후 12주간 AI팀의 가동률 병목 구간을 분석해줘",
    context={"org_unit_id": "ORG-AI-001"}
)

print(result.query_type)  # QueryType.CAPACITY
print(result.intent)      # "향후 12주간 조직별 인력 가동률 및 병목 구간 분석"
print(len(result.sub_queries))  # 4 (supply, demand, gap, bottleneck)
```

---

### 2.2 OptionGeneratorAgent

질문 유형에 맞는 3가지 대안(보수적/균형/적극적)을 생성합니다.

#### 클래스 정의

```python
from backend.agent_runtime.agents import OptionGeneratorAgent

agent = OptionGeneratorAgent(llm_client=None, kg_client=None)
```

#### 메서드

**`generate_options(query_type: str, context: dict, constraints: dict | None = None) -> OptionSet`**

| 파라미터      | 타입 | 필수 | 설명                             |
| ------------- | ---- | ---- | -------------------------------- |
| `query_type`  | str  | ✅   | 질문 유형 (CAPACITY, GO_NOGO 등) |
| `context`     | dict | ✅   | 분석 컨텍스트 (KG 쿼리 결과 등)  |
| `constraints` | dict | ❌   | 추가 제약조건                    |

**반환값: `OptionSet`**

```python
@dataclass
class OptionSet:
    query_type: str                # 질문 유형
    context: dict                  # 입력 컨텍스트
    options: list[DecisionOption]  # 3가지 대안
    recommendation: str            # 추천 대안 ID
    recommendation_reason: str     # 추천 사유

@dataclass
class DecisionOption:
    option_id: str                 # 대안 ID
    option_type: OptionType        # CONSERVATIVE, BALANCED, AGGRESSIVE
    name: str                      # 대안 이름
    description: str               # 설명
    actions: list[str]             # 실행 항목
    estimated_cost: float          # 예상 비용 (원)
    estimated_benefit: float       # 예상 효과 (원)
    risk_level: str                # LOW, MEDIUM, HIGH
    implementation_time: str       # 소요 기간
    prerequisites: list[str]       # 전제조건
    trade_offs: list[str]          # 트레이드오프
    scores: dict[str, float]       # 평가 점수 (impact, feasibility, risk, cost, time)
```

#### 대안 유형별 특성

| 유형         | 설명           | 리스크 | 비용 | 효과   |
| ------------ | -------------- | ------ | ---- | ------ |
| CONSERVATIVE | 보수적 접근    | 낮음   | 낮음 | 제한적 |
| BALANCED     | 균형 잡힌 접근 | 중간   | 중간 | 적정   |
| AGGRESSIVE   | 적극적 접근    | 높음   | 높음 | 최대   |

#### 사용 예시

```python
agent = OptionGeneratorAgent()

result = agent.generate_options(
    query_type="CAPACITY",
    context={
        "bottleneck_weeks": ["W05", "W06"],
        "gap_fte": 3,
        "org_unit": "AI팀"
    }
)

for opt in result.options:
    print(f"[{opt.option_type.value}] {opt.name}")
    print(f"  - 비용: {opt.estimated_cost:,.0f}원")
    print(f"  - 리스크: {opt.risk_level}")

print(f"\n추천: {result.recommendation}")
```

---

### 2.3 ImpactSimulatorAgent

각 대안의 영향도를 As-Is vs To-Be로 시뮬레이션합니다.

#### 클래스 정의

```python
from backend.agent_runtime.agents import ImpactSimulatorAgent

agent = ImpactSimulatorAgent(kg_client=None)
```

#### 메서드

**`simulate(query_type: str, options: list[dict], baseline: dict, horizon_weeks: int = 12) -> ScenarioComparison`**

| 파라미터        | 타입       | 필수 | 설명                        |
| --------------- | ---------- | ---- | --------------------------- |
| `query_type`    | str        | ✅   | 질문 유형                   |
| `options`       | list[dict] | ✅   | 대안 목록                   |
| `baseline`      | dict       | ✅   | 현재 상태 (As-Is)           |
| `horizon_weeks` | int        | ❌   | 시뮬레이션 기간 (기본 12주) |

**반환값: `ScenarioComparison`**

```python
@dataclass
class ScenarioComparison:
    query_type: str                # 질문 유형
    baseline: dict                 # 베이스라인 (As-Is)
    analyses: list[ImpactAnalysis] # 대안별 분석 결과
    comparison_summary: dict       # 비교 요약
    best_option_id: str            # 최적 대안 ID
    best_option_reason: str        # 선정 이유

@dataclass
class ImpactAnalysis:
    option_id: str                 # 대안 ID
    option_name: str               # 대안 이름
    metrics: list[MetricValue]     # 지표별 As-Is vs To-Be
    time_series: dict              # 시계열 예측 데이터
    overall_impact_score: float    # 종합 영향도 점수 (0-100)
    confidence_interval: tuple     # 신뢰구간 (lower, upper)
    assumptions: list[str]         # 가정 사항
    risks: list[str]               # 리스크 목록

@dataclass
class MetricValue:
    metric_type: MetricType        # UTILIZATION, COST, REVENUE 등
    name: str                      # 지표 이름
    as_is_value: float             # 현재 값
    to_be_value: float             # 예상 값
    unit: str                      # 단위
    change_percent: float          # 변화율 (%)
    change_direction: str          # POSITIVE, NEGATIVE, NEUTRAL
```

#### 지원 지표 (MetricType)

| 지표        | 설명      | 긍정 방향 | 가중치 |
| ----------- | --------- | --------- | ------ |
| UTILIZATION | 가동률    | -         | 0.20   |
| COST        | 비용      | 감소      | 0.15   |
| REVENUE     | 매출      | 증가      | 0.20   |
| MARGIN      | 마진율    | 증가      | 0.15   |
| RISK        | 리스크    | 감소      | 0.15   |
| TIME        | 소요 기간 | 감소      | 0.10   |
| QUALITY     | 품질      | 증가      | 0.05   |

#### 사용 예시

```python
agent = ImpactSimulatorAgent()

options = [
    {"option_id": "OPT-01", "name": "내부 재배치", "option_type": "CONSERVATIVE"},
    {"option_id": "OPT-02", "name": "외주 활용", "option_type": "BALANCED"},
    {"option_id": "OPT-03", "name": "정규직 채용", "option_type": "AGGRESSIVE"},
]

baseline = {
    "utilization": 0.92,
    "headcount": 10,
    "gap_fte": 3,
    "cost": 100000000,
}

result = agent.simulate(
    query_type="CAPACITY",
    options=options,
    baseline=baseline,
    horizon_weeks=12
)

for analysis in result.analyses:
    print(f"\n[{analysis.option_id}] {analysis.option_name}")
    print(f"  종합 점수: {analysis.overall_impact_score:.1f}")
    for m in analysis.metrics:
        print(f"  - {m.name}: {m.as_is_value:.1f} → {m.to_be_value:.1f} ({m.change_percent:+.1f}%)")
```

---

### 2.4 SuccessProbabilityAgent

프로젝트/기회의 성공 확률을 계산합니다.

#### 클래스 정의

```python
from backend.agent_runtime.agents import SuccessProbabilityAgent

agent = SuccessProbabilityAgent(kg_client=None)
```

#### 메서드

**`calculate(opportunity: dict, resources: dict, historical_data: list | None = None) -> ProbabilityResult`**

| 파라미터          | 타입 | 필수 | 설명                      |
| ----------------- | ---- | ---- | ------------------------- |
| `opportunity`     | dict | ✅   | 기회 정보                 |
| `resources`       | dict | ✅   | 가용 리소스 정보          |
| `historical_data` | list | ❌   | 과거 유사 프로젝트 데이터 |

**반환값: `ProbabilityResult`**

```python
@dataclass
class ProbabilityResult:
    overall_probability: float     # 종합 성공 확률 (0-1)
    confidence_level: str          # HIGH, MEDIUM, LOW
    factors: dict[str, float]      # 요인별 점수
    risk_factors: list[RiskFactor] # 리스크 요인
    recommendations: list[str]     # 성공률 향상 권고사항

@dataclass
class RiskFactor:
    factor_id: str                 # 리스크 ID
    name: str                      # 리스크 이름
    severity: str                  # HIGH, MEDIUM, LOW
    impact: float                  # 영향도 (0-1)
    mitigation: str                # 완화 방안
```

#### 성공 확률 계산 요인

| 요인                 | 가중치 | 설명             |
| -------------------- | ------ | ---------------- |
| resource_fit         | 0.30   | 리소스 적합도    |
| competency_match     | 0.25   | 역량 매칭률      |
| historical_success   | 0.20   | 과거 성공률      |
| timeline_feasibility | 0.15   | 일정 실현 가능성 |
| risk_level           | 0.10   | 리스크 수준      |

---

### 2.5 ValidatorAgent

응답의 주장을 검증하고 환각(Hallucination)을 탐지합니다.

#### 클래스 정의

```python
from backend.agent_runtime.agents import ValidatorAgent

agent = ValidatorAgent(kg_client=None)
```

#### 메서드

**`validate(response_text: str, available_evidence: list | None = None, context: dict | None = None) -> ValidationResult`**

| 파라미터             | 타입 | 필수 | 설명                  |
| -------------------- | ---- | ---- | --------------------- |
| `response_text`      | str  | ✅   | 검증할 응답 텍스트    |
| `available_evidence` | list | ❌   | 사용 가능한 근거 목록 |
| `context`            | dict | ❌   | 추가 컨텍스트         |

**반환값: `ValidationResult`**

```python
@dataclass
class ValidationResult:
    total_claims: int              # 총 주장 수
    verified_claims: int           # 검증된 주장 수
    partial_claims: int            # 부분 검증된 주장 수
    unverified_claims: int         # 미검증 주장 수 (환각 위험)
    assumption_claims: int         # 가정으로 표시된 주장 수
    evidence_link_rate: float      # 근거 연결률 (0-1)
    hallucination_risk: float      # 환각 위험도 (0-1)
    validations: list[ClaimValidation]  # 주장별 검증 결과
    overall_issues: list[str]      # 전체 이슈
```

#### 검증 상태

| 상태       | 설명                 | 환각 위험 |
| ---------- | -------------------- | --------- |
| VERIFIED   | 근거 있음 (2개 이상) | 낮음      |
| PARTIAL    | 부분적 근거 (1개)    | 중간      |
| UNVERIFIED | 근거 없음            | 높음      |
| ASSUMPTION | 가정으로 명시됨      | -         |

#### 사용 예시

```python
agent = ValidatorAgent()

response = """
향후 12주간 AI팀의 가동률은 약 92%로 예상됩니다.
현재 가용 인력은 8명이며, 필요 인력은 10명입니다.
"""

evidence = [
    {"evidence_id": "EV-001", "type": "DATA_POINT", "source": "HR System",
     "description": "AI팀 가용 인력 8명", "value": 8},
    {"evidence_id": "EV-002", "type": "CALCULATION", "source": "Capacity Model",
     "description": "예상 가동률 92%", "value": 92},
]

result = agent.validate(response, evidence)

print(f"근거 연결률: {result.evidence_link_rate * 100:.1f}%")
print(f"환각 위험도: {result.hallucination_risk * 100:.1f}%")
print(f"미검증 주장: {result.unverified_claims}개")
```

---

### 2.6 WorkflowBuilderAgent

질문 유형에 따른 전체 워크플로를 조율합니다.

#### 클래스 정의

```python
from backend.agent_runtime.agents import WorkflowBuilderAgent

agent = WorkflowBuilderAgent(
    query_agent=query_decomposition_agent,
    option_agent=option_generator_agent,
    impact_agent=impact_simulator_agent,
    probability_agent=success_probability_agent,
    validator_agent=validator_agent,
    kg_client=kg_client
)
```

#### 메서드

**`build_workflow(query_type: str, custom_steps: list | None = None, skip_hitl: bool = False) -> WorkflowDefinition`**

워크플로 정의를 생성합니다.

**`run_workflow(workflow: WorkflowDefinition, context: WorkflowContext, stop_on_hitl: bool = True) -> WorkflowExecution`**

워크플로를 실행합니다. `stop_on_hitl=True`이면 HITL 단계에서 일시 정지합니다.

**`resume_workflow(execution_id: str, workflow: WorkflowDefinition, context: WorkflowContext, hitl_result: dict) -> WorkflowExecution`**

HITL 승인 후 워크플로를 재개합니다.

**반환값**

```python
@dataclass
class WorkflowDefinition:
    workflow_id: str               # 워크플로 ID
    name: str                      # 워크플로 이름
    steps: list[WorkflowStep]      # 단계 목록
    total_steps: int               # 총 단계 수

@dataclass
class WorkflowExecution:
    execution_id: str              # 실행 ID
    workflow_id: str               # 워크플로 ID
    status: WorkflowStatus         # RUNNING, PAUSED_FOR_HITL, COMPLETED, FAILED
    current_step: int              # 현재 단계
    results: dict                  # 단계별 결과
    started_at: datetime           # 시작 시간
    completed_at: datetime | None  # 완료 시간
```

#### 기본 워크플로 단계

| 단계                       | 설명                 | Agent              |
| -------------------------- | -------------------- | ------------------ |
| 1. QUERY_DECOMPOSITION     | 질문 분해            | QueryDecomposition |
| 2. KG_QUERY                | Knowledge Graph 조회 | KG Client          |
| 3. OPTION_GENERATION       | 대안 생성            | OptionGenerator    |
| 4. IMPACT_SIMULATION       | 영향 시뮬레이션      | ImpactSimulator    |
| 5. PROBABILITY_CALCULATION | 성공 확률 계산       | SuccessProbability |
| 6. VALIDATION              | 근거 검증            | Validator          |
| 7. HITL_APPROVAL           | 인간 검토/승인       | HITL System        |
| 8. FINALIZATION            | 최종 결과 생성       | -                  |

---

## 3. HITL Approval System

### 3.1 HITLApprovalSystem

Human-in-the-Loop 승인 및 의사결정 로그 관리 시스템입니다.

#### 클래스 정의

```python
from backend.agent_runtime.workflows import HITLApprovalSystem

system = HITLApprovalSystem(
    notification_handler=None,     # 알림 핸들러
    approval_timeout_hours=24      # 타임아웃 (시간)
)
```

#### 메서드

**`create_approval_request(execution_id: str, decision_type: DecisionType, workflow_context: dict, requester_id: str) -> ApprovalRequest`**

승인 요청을 생성합니다.

**`submit_response(request_id: str, status: ApprovalStatus, approver_id: str, ...) -> ApprovalResponse`**

승인/거절 응답을 제출합니다.

**`escalate_request(request_id: str, escalation_reason: str, escalated_by: str) -> ApprovalRequest`**

상위 결재자로 에스컬레이션합니다.

**`create_decision_log(execution_id: str, decision_type: DecisionType, workflow_context: dict, approval_responses: list) -> DecisionLog`**

의사결정 로그를 생성합니다.

#### 승인 레벨

| 레벨       | 설명     | 기본 적용                |
| ---------- | -------- | ------------------------ |
| TEAM_LEAD  | 팀장급   | Capacity, Competency Gap |
| DEPARTMENT | 부서장급 | Go/No-go, Headcount      |
| DIVISION   | 본부장급 | 고가치/대규모 건         |
| EXECUTIVE  | 임원급   | 최종 에스컬레이션        |

#### 승인 상태

| 상태      | 설명           |
| --------- | -------------- |
| PENDING   | 대기 중        |
| APPROVED  | 승인됨         |
| REJECTED  | 거절됨         |
| MODIFIED  | 수정 후 승인   |
| ESCALATED | 에스컬레이션됨 |
| EXPIRED   | 타임아웃       |

#### 사용 예시

```python
system = HITLApprovalSystem()

# 1. 승인 요청 생성
request = system.create_approval_request(
    execution_id="EXEC-001",
    decision_type=DecisionType.CAPACITY,
    workflow_context=workflow_context,
    requester_id="user@example.com"
)

# 2. 승인 응답 제출
response = system.submit_response(
    request_id=request.request_id,
    status=ApprovalStatus.APPROVED,
    approver_id="manager@example.com",
    approver_name="김팀장",
    approval_level=ApprovalLevel.TEAM_LEAD,
    selected_option_id="OPT-02",
    rationale="균형 잡힌 접근 방식이 적합함",
    conditions=["외주 인력 품질 관리 필수"]
)

# 3. 의사결정 로그 생성
log = system.create_decision_log(
    execution_id="EXEC-001",
    decision_type=DecisionType.CAPACITY,
    workflow_context=workflow_context,
    approval_responses=[response]
)
```

---

## 4. 데이터 모델

### 4.1 Knowledge Graph 노드 타입

| 노드 타입          | 설명        | 주요 속성                                |
| ------------------ | ----------- | ---------------------------------------- |
| Employee           | 직원        | employeeId, name, grade, status          |
| OrgUnit            | 조직        | orgUnitId, name, parentId, level         |
| Project            | 프로젝트    | projectId, name, status, budget          |
| WorkPackage        | 작업 패키지 | wpId, projectId, status                  |
| Opportunity        | 영업 기회   | opportunityId, dealValue, stage          |
| Assignment         | 배치        | assignmentId, employeeId, projectId      |
| Competency         | 역량        | competencyId, name, category             |
| PersonCompetency   | 직원 역량   | employeeId, competencyId, level          |
| RequiredCompetency | 필요 역량   | projectId, competencyId, minimumLevel    |
| Demand             | 수요        | demandId, orgUnitId, quantityFTE         |
| Availability       | 가용성      | availabilityId, employeeId, availableFTE |

### 4.2 주요 관계 타입

| 관계           | 시작 노드  | 종료 노드   | 설명          |
| -------------- | ---------- | ----------- | ------------- |
| BELONGS_TO     | Employee   | OrgUnit     | 소속 관계     |
| WORKS_ON       | Employee   | Project     | 프로젝트 참여 |
| ASSIGNED_TO    | Assignment | Employee    | 배치 대상     |
| HAS_COMPETENCY | Employee   | Competency  | 역량 보유     |
| REQUIRES       | Project    | Competency  | 필요 역량     |
| OWNS           | OrgUnit    | Opportunity | 기회 소유     |
| PARENT_OF      | OrgUnit    | OrgUnit     | 상위 조직     |

---

## 5. 에러 코드

| 코드 | 설명                | 대응 방안                |
| ---- | ------------------- | ------------------------ |
| E001 | 질문 유형 분류 실패 | 더 구체적인 키워드 포함  |
| E002 | KG 쿼리 실패        | 데이터 존재 여부 확인    |
| E003 | 대안 생성 실패      | 컨텍스트 데이터 확인     |
| E004 | 시뮬레이션 실패     | 베이스라인 데이터 확인   |
| E005 | 검증 실패           | 근거 데이터 확인         |
| E006 | 승인 권한 부족      | 상위 결재자 지정         |
| E007 | 승인 타임아웃       | 재요청 또는 에스컬레이션 |
| E008 | 워크플로 실행 실패  | 로그 확인 후 재시도      |

---

## 6. 부록

### 6.1 전체 Import 목록

```python
# Agents
from backend.agent_runtime.agents import (
    QueryDecompositionAgent,
    DecomposedQuery,
    SubQuery,
    OptionGeneratorAgent,
    DecisionOption,
    OptionSet,
    ImpactSimulatorAgent,
    ImpactAnalysis,
    ScenarioComparison,
    SuccessProbabilityAgent,
    ProbabilityResult,
    RiskFactor,
    ValidatorAgent,
    ValidationResult,
    EvidenceLink,
    WorkflowBuilderAgent,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowContext,
    WorkflowStatus,
    StepType,
)

# HITL System
from backend.agent_runtime.workflows import (
    HITLApprovalSystem,
    ApprovalRequest,
    ApprovalResponse,
    DecisionLog,
    ApprovalStatus,
    ApprovalLevel,
    DecisionType,
)
```

### 6.2 관련 문서

- [PoC Charter](./specs/poc-charter.md)
- [Question Set](./specs/question-set.md)
- [Data Catalog](./specs/data-catalog.md)
- [Ontology 설계](../HR%20의사결정%20지원%20핵심%20Ontology%20설계.md)
- [사용자 가이드](./user-guide.md)
