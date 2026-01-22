# HR 의사결정 지원 핵심 Ontology 설계 v0.1.1

## Predictive + Simulation + Prescriptive + Explainable + HITL/Workflow

## 0. 설계 목적과 범위

### 목적

HR/조직 운영 의사결정(인력/TO, 프로젝트/사업기회, 역량 투자)에 대해 다음을 **단일 KG(지식그래프)에서** 수행 가능하도록 합니다.

- **예측**: 미래 기간(주차 단위)의 가동률/병목/리스크/성공확률/마진 훼손 가능성
- **시뮬레이션**: 옵션 3안(내부/혼합/역량강화)의 As‑Is vs To‑Be 비교
- **처방**: 실행 가능한 Action(재배치/외부투입/업스킬/채용/스코프조정 등) 생성
- **설명가능/감사**: 결론이 어떤 데이터/가정/모델실행에 의해 나왔는지 추적
- **HITL 승인 이후 실행 연결**: VRB/Pre‑PRB/PRB 등 게이트 승인 후 workflow task로 실행 추적

### 범위(시스템 경계)

- 인사/역량/프로젝트/투입/수요(파이프라인) 데이터가 **그래프에서 연결**되며,
- 예측 알고리즘은 휴리스틱/규칙/모델(ML) 어떤 방식이든 가능하되, **Model/ModelRun/ForecastPoint로 결과를 저장**합니다.

---

## 1. “팔란티어 수준” 예측 정의(운영 가능한 구조)

> “팔란티어 수준”을 PoC 목표에 맞게 **데이터 구조/온톨로지 요건**으로 정의합니다.

1. **목표/제약 기반**

- `DecisionCase`에 **Objective/Constraint**를 구조적으로 저장
  예: `utilization <= 0.90`, `successProbability >= 0.7`, `margin >= 0.15`,
  `핵심인력 A 4주 투입불가`, `보안등급 상 외부 투입 불가`

2. **복수 데이터 연결(수요·공급·역량·비용·리스크·결과)**

- BizForce(수요) ↔ TMS(공급) ↔ R&R(대무/핵심역할) ↔ HR Master(역량) ↔ Cost/Rate ↔ Risk/Outcome
  를 **하나의 그래프 경로**로 연결

3. **예측 + 시뮬레이션 + 처방(대안)**

- 예측 결과를 `ForecastPoint`로 저장(주차·조직·프로젝트 단위)
- 옵션 3안을 `Option/Scenario/Action`으로 모델링해 **To‑Be 예측 재실행**
- 비교 지표를 `Evaluation/MetricValue/ImpactAssessment`로 저장

4. **근거/감사 가능(HITL+Workflow 포함)**

- `ModelRun`이 어떤 `DataSnapshot`과 어떤 `Assumption/Scenario`를 사용했는지 기록
- `Finding(병목/갭/리스크)`에 `Evidence`를 연결하여 설명
- `DecisionGate/Approval`(HITL) 이후 `WorkflowTask`로 실행 연결

---

## 2. 1.3 핵심질문(유스케이스) 정의 업데이트

아래 4개 예제를 **온톨로지로 그대로 표현 가능**하도록 공통 템플릿을 정의합니다.

### 공통 3단계 템플릿

- **(1) 문제 정의**: Scope + Horizon + Objective + Constraint + KPI(측정지표)
- **(2) 대안 탐색**: 3안(내부/혼합/역량강화) + As‑Is vs To‑Be 시뮬레이션 + 리스크/성공확률 비교
- **(3) 보고/기획**: 1페이지 요약 + 실행계획(업무 재배치/대무/교육 일정) + HITL 승인 + Workflow Task 생성

---

### 2.1 예제 A‑1 | 12주 Capacity 병목 예측(포트폴리오/조직)

**문제 정의(1단계)**
“향후 12주 동안 BizForce 파이프라인(수주확도·착수예정)까지 반영하면, 본부/팀별 가동률 90% 초과 주차와 병목 원인(스킬/역할/대무 공백)을 예측해줘.”

- Scope: `OrgUnit(본부/팀)`
- Horizon: `12주`, granularity=`week`
- Objective: `UTILIZATION <= 0.90`
- 병목 원인(근거 가능한 형태):
  - Skill gap: `CompetencyGap` or `Finding(type=SKILL_GAP)`
  - Role gap: `DeliveryRole` 부족(`Finding(type=ROLE_GAP)`)
  - Backup gap: `Responsibility`에 backup 없음(`Finding(type=COVERAGE_GAP)`)

**대안 탐색(2단계)**
“병목 Top3 구간에 대해 1) 내부 재배치 2) 외부 투입 3) 역량강화(2~4주) 3안 만들고 As‑Is vs To‑Be 가동률 비교해줘.”

**보고/기획(3단계)**
“선택안 기준 팀장 보고 1페이지 + 실행계획(인수인계/대무/교육 일정) 생성.”

필요 데이터: BizForce(수요), TMS(공급), R&R/업무분장(대무), HR Master(역량)

---

### 2.2 예제 B‑1 | Go/No‑go + 성공확률(프로젝트/사업기회, VRB/Pre‑PRB 연결)

**문제 정의(1단계)**
“다음달 착수 가정의 ‘100억 미디어 AX’ 사업기회에 대해 내부 수행 가능 여부와 부족 영역(역할/스킬/MM), 수익성 훼손 가능성을 예측해줘.”

- Scope: `Opportunity`(수주 시 `Project`로 전환)
- KPI/목표 예:
  - `SUCCESS_PROB >= 0.70`
  - `MARGIN >= 0.15`
  - `START_DATE = nextMonth`

- 제약 예:
  - 특정 `Employee` 투입불가(Availability)
  - 보안등급 상 외부투입 제한(Constraint)

**대안 탐색(2단계)**
“3안: 1안(내부), 2안(혼합), 3안(구성변경 최소+업스킬).
각 안의 가동률/리스크/성공확률(휴리스틱+모델) 비교.”

**보고/기획(3단계)**
“1안 선택 시 Pre‑PRB/PRB 문서 초안(핵심 포인트/체크리스트/리스크&대응) 생성.”

---

### 2.3 예제 C‑1 | ‘증원 필요’ 원인분해 + 영향도 예측(인력/TO)

**문제 정의(1단계)**
“OOO팀 ‘1명 증원’ 요청. 부족 원인을 업무량/가동률/핵심역할 공백/대무 부재로 분해해줘.”

- Scope: `OrgUnit`
- KPI: `UTILIZATION`, `COVERAGE_GAP_COUNT`, `ROLE_GAP`, `DEMAND_FTE`

**대안 탐색(2단계)**
“3안(1·2안=구성안, 3안=역량강화) 만들고 As‑Is vs To‑Be 영향도 비교.”

**보고/기획(3단계)**
“2안 결정. 다음달 실행 기준(HITL 승인 후) 실행계획/대무 반영/리스크 관리안 생성.”

---

### 2.4 예제 D‑1 | 역량 투자 우선순위 예측(ROI형)

**문제 정의(1단계)**
“AI‑driven 전환 관점에서 조직/직무별 역량 갭 Top10 정량화.”

**대안 탐색(2단계)**
“3안: 1안(내부강사), 2안(외부/온라인 혼합), 3안(업무 재배치 최소+단기 집중 업스킬).
각 안이 갭을 얼마나 줄이고, 결과적으로 가동률/수행 가능성이 어떻게 변하는지 시뮬레이션.”

**보고/기획(3단계)**
“최종안 기준 교육기획서(대상/기간/운영/리스크/성과측정) 생성.”

---

## 3. 온톨로지 모듈(코어) 구성 v0.1.1

기존 v0.1(조직/인력, 프로젝트, 투입/가용, 역량, L&D, 의사결정) 위에
“팔란티어 수준”을 위해 **4개 축**을 추가/강화합니다.

1. **Demand & Pipeline (BizForce)**

- `Opportunity`, `DemandSignal`, `ResourceDemand(probability 포함)`

2. **R&R / Coverage (대무·핵심역할)**

- `Responsibility`, `DeliveryRole`, `PRIMARY_FOR`, `BACKUP_FOR`

3. **Forecast & Explainability (예측/근거/감사)**

- `TimeBucket`, `Model`, `ModelRun`, `ForecastPoint`, `Finding`, `Evidence`, `DataSnapshot`

4. **HITL Gate & Workflow**

- `DecisionGate(VRB/Pre‑PRB/PRB)`, `Approval`, `WorkflowInstance`, `WorkflowTask`

---

## 4. 크로스컷팅 설계 패턴(데이터 구조로 전환 규칙)

### 4.1 시간(Temporal) 모델

- 모든 계획/투입/가용/수요/예측은 기간이 필요
- 표준: `startDate`, `endDate` + (권장) `TimeBucket(week)` 노드로 집계/예측 저장

### 4.2 Scenario(가정) 모델

- **Baseline(As‑Is)**와 **Option Scenario(To‑Be)**를 분리 저장
- `Scenario`는 `Action`들의 집합이며, 모델 실행은 `ModelRun(FOR_SCENARIO)`로 기록

### 4.3 Metric(지표) 모델

- 예측값: `ForecastPoint(metricType, value, bounds, confidence)`
- 옵션 평가값: `MetricValue(asIsValue, toBeValue, delta)`

### 4.4 Explainability(근거) 모델

- 병목/갭/리스크는 `Finding`으로 저장하고
  `Evidence`(원천데이터 참조)로 설명가능하게 연결

### 4.5 HITL + Workflow

- `DecisionGate/Approval`을 저장하고 승인 이후 `WorkflowTask`로 실행 연결
  (실행상태를 그래프에서 끝까지 추적)

---

## 5. 핵심 클래스(노드) 정의 v0.1.1

> “바로 구현 가능한” 수준으로 **라벨/키/필수 속성/주요 속성**만 정리합니다.
> (표준 네이밍: Label=PascalCase, rel=UPPER_SNAKE)

### 5.1 Workforce & Organization

#### Organization

- Key: `orgId`
- Props: `name`

#### OrgUnit

- Key: `orgUnitId` _(초기 PoC는 name 기반 임시키 가능하나 운영은 ID 필수)_
- Props(필수): `name`, `type(본부/실/팀)`
- Props(권장): `parentOrgUnitId`, `costCenter`, `validFrom`, `validTo`

#### JobRole

- Key: `jobRoleId`
- Props: `name`, `jobFamily`, `levelBand`

#### Position (TO/정원 슬롯)

- Key: `positionId`
- Props: `headcountType`, `grade`, `status(OPEN/FILLED/FROZEN)`, `orgUnitId`, `jobRoleId`

#### Employee

- Key: `employeeId`
- Props(필수): `employeeId`
- Props(권장): `name`, `employmentType`, `grade`, `hireDate`, `status`

#### EmploymentAssignment (소속/직무/포지션 이력)

- Key: `assignmentId` _(또는 employeeId+startDate 복합키)_
- Props: `startDate`, `endDate`, `sourceSystem`

---

### 5.2 Work & Portfolio

#### Client / Industry (차원)

- Key: `clientId`, `industryId`
- Props: `name`

#### Opportunity (BizForce 파이프라인)

- Key: `opportunityId`
- Props(필수): `name`, `stage`, `expectedStartDate`
- Props(권장): `expectedEndDate`, `dealValue`, `expectedMarginTarget`, `ownerOrgUnitId`

#### Project

- Key: `projectId`
- Props: `name`, `startDate`, `endDate`, `priority`, `contractValue`

#### WorkPackage (WBS/스트림)

- Key: `workPackageId`
- Props: `name`, `startDate`, `endDate`, `criticality`

#### WorkType (운영/반복업무)

- Key: `workTypeId`
- Props: `name`

---

### 5.3 Demand & Supply

#### DemandSignal (수요 신호)

- Key: `signalId`
- Props(필수): `sourceSystem='BizForce'`, `closeProbability`, `expectedStartDate`
- Props(권장): `expectedEffortMM`, `confidence`, `lastUpdatedAt`

#### ResourceDemand (주차/기간별 요구 FTE/MM)

- Key: `demandId`
- Props(필수):
  - `quantityFTE` _(또는 `effortMM`)_
  - `startDate`, `endDate` _(또는 `bucketId`)_
  - `priority`

- Props(핵심 추가): `probability(0~1)` _(파이프라인 반영을 위해 필수)_
- Props(권장): `sourceType(Opportunity/Project/WorkPackage/WorkType)`, `sourceId`

#### Availability (가용성)

- Key: `availabilityId` _(employeeId+bucketId 권장)_
- Props(필수): `availableFTE`, `reason`, `startDate/endDate or bucketId`
- Props: `sourceSystem(TMS/HR)`

#### Assignment (투입/배정)

- Key: `assignmentId`
- Props(필수): `allocationFTE`, `startDate`, `endDate`
- Props(권장): `isTentative`, `sourceSystem(TMS)`

#### TimesheetEntry (실적, 선택)

- Key: `timesheetId`
- Props: `date`, `hours`, `sourceRef`

---

### 5.4 R&R / Coverage (핵심역할/대무)

#### DeliveryRole (프로젝트/운영 역할)

- Key: `deliveryRoleId`
- Props: `name` _(PM/아키텍트/데이터엔지니어/AX컨설턴트 등)_

#### Responsibility (업무/책임 단위)

- Key: `responsibilityId`
- Props(필수): `name`, `criticality`
- Props(권장): `description`, `ownerType(OrgUnit/WorkPackage)`

> 대무 공백을 “질의 가능한 데이터”로 만들기 위해 최소 두 관계가 필요:

- `PRIMARY_FOR`(정) / `BACKUP_FOR`(부)

---

### 5.5 Competency & Learning

#### Competency

- Key: `competencyId`
- Props: `name`, `domain`, `description`

#### CompetencyRequirement

- Key: `requirementId`
- Props(필수): `requiredLevel`, `weight`
- Props(권장): `targetType(JobRole/WorkPackage/DeliveryRole)`, `targetId`

#### CompetencyEvidence

- Key: `evidenceId`
- Props(필수): `level`, `assessedAt`, `sourceType`
- Props(권장): `assessedBy`, `confidence`

#### LearningProgram / Course / Enrollment

- Key: `programId`, `courseId`, `enrollmentId`
- Props(필수): `name/title`, `deliveryMode(online/offline/blended)`
- Enrollment Props: `status`, `plannedStart`, `plannedEnd`

#### Certification (선택)

- Key: `certificationId`
- Props: `name`, `level`

---

### 5.6 Decision, Evaluation, Workflow

#### DecisionCase

- Key: `decisionCaseId`
- Props(필수): `type(PortfolioBottleneck/GoNoGo/Headcount/CapabilityROI)`, `createdAt`, `status`
- Props(권장): `requester`, `dueDate`, `summary`

#### Objective

- Key: `objectiveId`
- Props(필수): `metricType`, `operator(<=/>=/...)`, `targetValue`, `scopeType`, `horizonStart`, `horizonEnd`

#### Constraint

- Key: `constraintId`
- Props(필수): `type(Availability/Budget/Policy/Security/...)`, `severity(hard/soft)`
- Props(권장): `expression`, `startDate`, `endDate`, `appliesToType`, `appliesToId`

#### Option / Scenario / Action

- Option Key: `optionId`, Props: `name`, `optionType(Internal/Mixed/Upskill)`, `description`
- Scenario Key: `scenarioId`, Props: `baselineSnapshotId`, `assumptions`
- Action Key: `actionId`, Props: `type(Reassign/Outsource/Upskill/Hire/ScopeChange)`, `owner`, `startDate`, `endDate`, `status`

#### Evaluation / MetricValue / ImpactAssessment / Risk

- Evaluation Key: `evaluationId`, Props: `totalScore`, `successProbability`, `rationale`
- MetricValue Key: `metricValueId`, Props: `metricType`, `asIsValue`, `toBeValue`, `delta`, `unit`
- ImpactAssessment Key: `impactId`, Props: `dimension(Cost/Speed/Risk/Quality/Capability/...)`, `value`, `narrative`
- Risk Key(선택): `riskId`, Props: `category`, `probability`, `impact`, `score`, `description`

#### DecisionGate / Approval / WorkflowInstance / WorkflowTask

- Gate Key: `gateId`, Props: `process(VRB/Pre-PRB/PRB)`, `name`, `sequence`, `status`
- Approval Key: `approvalId`, Props: `decision(approve/reject)`, `approvedBy`, `approvedAt`, `comment`
- WorkflowInstance Key: `workflowId`, Props: `type`, `status`, `startedAt`
- WorkflowTask Key: `taskId`, Props: `type`, `owner`, `dueDate`, `status`

---

### 5.7 Forecast & Explainability (예측/근거/감사)

#### TimeBucket

- Key: `bucketId` (예: `2026-W05`)
- Props: `granularity='WEEK'`, `startDate`, `endDate`, `year`, `week`

#### Model / ModelRun

- Model Key: `modelId`, Props: `name`, `type(heuristic/ml/rules)`, `version`
- ModelRun Key: `runId`, Props: `runAt`, `parameters(json)`, `status`, `scenarioId`

#### ForecastPoint

- Key: `forecastPointId`
- Props(필수): `metricType`, `value`, `unit`
- Props(권장): `lowerBound`, `upperBound`, `confidence`, `method`

#### Finding (병목/원인/갭)

- Key: `findingId`
- Props(필수): `type(OVER_UTILIZATION/SKILL_GAP/ROLE_GAP/COVERAGE_GAP/MARGIN_RISK/...)`, `severity`, `narrative`
- Props(권장): `rootCause`, `rank`

#### Evidence / DataSnapshot

- Evidence Key: `evidenceId`, Props: `sourceSystem`, `sourceType(table/query/doc)`, `sourceRef`, `capturedAt`, `note`
- Snapshot Key: `snapshotId`, Props: `asOf`, `datasetVersions(json)`

---

## 6. 핵심 관계(엣지) 정의 v0.1.1

> 아래 관계만으로 A~D 예제가 모두 “그래프 질의”로 풀립니다.
> (괄호는 관계 속성)

### 6.1 조직/인력

- `(OrgUnit)-[:HAS_SUB_UNIT]->(OrgUnit)`
- `(Employee)-[:BELONGS_TO (startDate,endDate)]->(OrgUnit)`
- `(Employee)-[:HAS_JOBROLE (startDate,endDate)]->(JobRole)`
- `(Employee)-[:OCCUPIES (startDate,endDate)]->(Position)`
- `(Position)-[:IN_ORGUNIT]->(OrgUnit)`
- `(Position)-[:FOR_JOBROLE]->(JobRole)`

### 6.2 파이프라인/프로젝트

- `(Opportunity)-[:FOR_CLIENT]->(Client)`
- `(Opportunity)-[:IN_INDUSTRY]->(Industry)`
- `(Opportunity)-[:HAS_SIGNAL]->(DemandSignal)`
- `(DemandSignal)-[:IMPLIES_DEMAND]->(ResourceDemand)`
- `(Project)-[:FOR_CLIENT]->(Client)`
- `(Project)-[:HAS_WORKPACKAGE]->(WorkPackage)`

### 6.3 수요/공급/투입

- `(WorkPackage|OrgUnit|Project|Opportunity)-[:HAS_DEMAND]->(ResourceDemand)`
- `(ResourceDemand)-[:FOR_BUCKET]->(TimeBucket)` _(또는 startDate/endDate로 대체 가능)_
- `(ResourceDemand)-[:REQUIRES_ROLE]->(DeliveryRole)`
- `(ResourceDemand)-[:REQUIRES_COMPETENCY]->(CompetencyRequirement)`
- `(CompetencyRequirement)-[:FOR_COMPETENCY]->(Competency)`
- `(Employee)-[:ASSIGNED_TO (allocationFTE,startDate,endDate)]->(WorkPackage|Project|WorkType)`
- `(Employee)-[:HAS_AVAILABILITY]->(Availability)`
- `(Availability)-[:FOR_BUCKET]->(TimeBucket)`

### 6.4 R&R/대무

- `(OrgUnit)-[:OWNS_RESPONSIBILITY]->(Responsibility)`
- `(WorkPackage)-[:HAS_RESPONSIBILITY]->(Responsibility)`
- `(Responsibility)-[:REQUIRES_ROLE]->(DeliveryRole)`
- `(Employee)-[:PRIMARY_FOR (startDate,endDate)]->(Responsibility)`
- `(Employee)-[:BACKUP_FOR (startDate,endDate)]->(Responsibility)`

### 6.5 역량/학습

- `(JobRole|WorkPackage|DeliveryRole)-[:REQUIRES_COMPETENCY]->(CompetencyRequirement)`
- `(Employee)-[:HAS_EVIDENCE]->(CompetencyEvidence)`
- `(CompetencyEvidence)-[:FOR_COMPETENCY]->(Competency)`
- `(LearningProgram)-[:IMPROVES]->(Competency)`
- `(Course)-[:PART_OF_PROGRAM]->(LearningProgram)`
- `(Employee)-[:ENROLLED_IN (status,plannedStart,plannedEnd)]->(Course)`
- `(Employee)-[:HAS_CERTIFICATION]->(Certification)` _(선택)_

### 6.6 의사결정/옵션/실행

- `(DecisionCase)-[:ABOUT]->(OrgUnit|Opportunity|Project)`
- `(DecisionCase)-[:HAS_OBJECTIVE]->(Objective)`
- `(DecisionCase)-[:HAS_CONSTRAINT]->(Constraint)`
- `(DecisionCase)-[:HAS_OPTION]->(Option)`
- `(Option)-[:HAS_SCENARIO]->(Scenario)`
- `(Scenario)-[:INCLUDES_ACTION]->(Action)`
- `(Option)-[:HAS_EVALUATION]->(Evaluation)`
- `(Evaluation)-[:HAS_METRIC]->(MetricValue)`
- `(Option)-[:HAS_IMPACT]->(ImpactAssessment)`
- `(Option)-[:HAS_RISK]->(Risk)` _(선택)_
- `(DecisionCase)-[:HAS_GATE]->(DecisionGate)`
- `(DecisionGate)-[:HAS_APPROVAL]->(Approval)`
- `(Approval)-[:TRIGGERS_WORKFLOW]->(WorkflowInstance)`
- `(WorkflowInstance)-[:HAS_TASK]->(WorkflowTask)`
- `(WorkflowTask)-[:RELATED_TO]->(Action)`

### 6.7 예측/근거/감사

- `(ModelRun)-[:RUNS_MODEL]->(Model)`
- `(ModelRun)-[:FOR_SCENARIO]->(Scenario)` _(As‑Is는 baseline scenario)_
- `(ModelRun)-[:USING_SNAPSHOT]->(DataSnapshot)`
- `(ModelRun)-[:OUTPUTS]->(ForecastPoint)`
- `(ForecastPoint)-[:FOR_BUCKET]->(TimeBucket)`
- `(ForecastPoint)-[:FOR_SUBJECT]->(OrgUnit|Opportunity|Project|WorkPackage)`
- `(ModelRun)-[:HAS_FINDING]->(Finding)`
- `(Finding)-[:AFFECTS]->(OrgUnit|WorkPackage|DeliveryRole|Competency|Responsibility)`
- `(Finding)-[:EVIDENCED_BY]->(Evidence)`
- `(Evidence)-[:REFERENCES]->(Employee|Assignment|Availability|ResourceDemand|DemandSignal|...)`

---

## 7. “팔란티어 수준 질문”이 온톨로지에서 어떻게 풀리는가(저장 단위)

### A‑1 12주 병목 예측

- 입력:
  - BizForce: `Opportunity/DemandSignal/ResourceDemand(probability)`
  - TMS: `Assignment/Availability`
  - R&R: `Responsibility + PRIMARY_FOR/BACKUP_FOR`
  - HR: `CompetencyEvidence`

- 처리/저장:
  - `ModelRun`(baseline) → `ForecastPoint(UTILIZATION)` by (OrgUnit, TimeBucket)
  - `Finding`(OVER_UTILIZATION/SKILL_GAP/ROLE_GAP/COVERAGE_GAP) + `Evidence`

- 출력:
  - 병목 주차/원인/근거
  - 옵션 3안(각각 Scenario+Action) 생성
  - option별 `ModelRun` 재실행 → To‑Be ForecastPoint
  - `Evaluation/MetricValue`로 As‑Is vs To‑Be 비교 저장

### B‑1 Go/No‑go + 성공확률

- 입력: Opportunity + Demand + Capacity + Rate/Cost + Constraints
- 저장:
  - `ForecastPoint(SUCCESS_PROB, MARGIN, UTILIZATION)` + `Finding(리스크)` + Evidence
  - `DecisionGate(VRB/Pre‑PRB/PRB)` 및 `Approval`
  - 승인 시 `WorkflowTask`로 실행계획 연결

### C‑1 증원 원인분해

- 입력: OrgUnit 수요/공급 + R&R 커버리지
- 저장:
  - `Finding`에 rootCause(업무량/가동률/역할공백/대무부재)를 구조적으로 연결

### D‑1 역량 투자 ROI

- 입력: CompetencyGap(요구 vs 보유) + 교육 옵션 + 기간/비용/가용성
- 저장:
  - 옵션별 `ForecastPoint(SKILL_GAP_SCORE, UTILIZATION, PROJECT_FEASIBILITY)`
  - `ImpactAssessment(Cost/Capability)` + Evidence(근거 데이터/가정)

---

## 8. MVP(v0.1.1)로 반드시 필요한 최소 라벨/관계

PoC에서 “팔란티어 수준”을 검증하려면 최소 아래는 있어야 합니다.

### 반드시(필수)

- Organization/People: `OrgUnit, Employee, JobRole`
- Supply: `Assignment, Availability, TimeBucket`
- Demand: `Opportunity, DemandSignal, ResourceDemand`
- R&R: `Responsibility, DeliveryRole, PRIMARY_FOR, BACKUP_FOR`
- Competency: `Competency, CompetencyEvidence` _(요구역량은 v0.2로 미뤄도 PoC 가능)_
- Decision/Scenario: `DecisionCase, Objective, Constraint, Option, Scenario, Action, Evaluation, MetricValue`
- Forecast/Audit: `Model, ModelRun, ForecastPoint, Finding, Evidence, DataSnapshot`
- HITL/Workflow: `DecisionGate, Approval, WorkflowTask`

### 선택(있으면 정확도/설명력↑)

- `Position(TO)` / `EmploymentAssignment(이력)`
- `CompetencyRequirement`(직무/프로젝트 요구역량)
- `TimesheetEntry`(실적 기반 원인분해)
- `RateCard/Vendor/ExternalResource`(마진/비용 정밀화)
- `Risk`(리스크 레지스터 형태)

---

## 9. 구현(Neo4j) 전환 시 규칙(짧게)

- 모든 노드는 `*Id` 유니크 키를 갖도록(초기 PoC는 name 기반 임시키 가능하지만, 운영은 ID 필수)
- 시간 집계/예측은 `TimeBucket` 중심으로 저장(주차 단위)
- 예측/시뮬레이션 결과는 **반드시** `ModelRun`에 귀속(언제/어떤 스냅샷/어떤 시나리오로 계산했는지)
- 옵션/액션은 문서가 아니라 **그래프 엔티티**로 저장(HITL 승인 후 workflow로 이어짐)
- 근거는 `Evidence`로 연결(“왜 이 결론?”에 대한 감사 가능성 확보)
