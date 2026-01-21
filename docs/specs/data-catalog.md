# HR 의사결정 지원 시스템 - Data Catalog v1

> 작성일: 2025-01-23 | 버전: 1.0

---

## 1. 개요

이 문서는 HR 의사결정 지원 시스템에서 사용하는 데이터 소스, 엔터티, 스키마를 정의합니다.

---

## 2. 데이터 소스 인벤토리

### 2.1 원천 시스템

| 시스템 | 설명 | 데이터 유형 | 갱신 주기 | 연동 방식 |
|--------|------|------------|----------|----------|
| **HR Master** | 인사 기본 정보 | 직원, 조직, 직무 | 실시간 | API/DB |
| **BizForce** | 영업 파이프라인 | Opportunity, 수주 예측 | 일 1회 | API |
| **TMS** | 프로젝트/타임시트 | 프로젝트, 배치, 공수 | 일 1회 | DB |
| **Competency** | 역량 관리 | 역량, 평가, 교육 | 분기 1회 | API |
| **VRB/PRB** | 의사결정 기록 | 심의 결과, 승인 이력 | 이벤트 | Manual/API |

### 2.2 PoC용 Mock 데이터

| 파일명 | 엔터티 | 건수 | 원천 시스템 |
|--------|--------|------|------------|
| `persons.json` | Employee | 100명 | HR Master |
| `orgs.json` | OrgUnit | 20개 | HR Master |
| `projects.json` | Project, WorkPackage | 30개 | TMS |
| `opportunities.json` | Opportunity, DemandSignal | 15개 | BizForce |
| `skills.json` | Competency, CompetencyEvidence | 50개 | Competency |
| `assignments.json` | Assignment, Availability | 150건 | TMS |

---

## 3. 엔터티 스키마

### 3.1 Workforce & Organization 모듈

#### OrgUnit (조직)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `orgUnitId` | string | ✅ | 조직 고유 ID (PK) | HR Master |
| `name` | string | ✅ | 조직명 | HR Master |
| `type` | enum | ✅ | 본부/실/팀/파트 | HR Master |
| `parentOrgUnitId` | string | | 상위 조직 ID (FK) | HR Master |
| `headEmployeeId` | string | | 조직장 사번 (FK) | HR Master |
| `costCenter` | string | | 코스트센터 코드 | HR Master |
| `status` | enum | ✅ | ACTIVE/INACTIVE | HR Master |

#### Employee (직원)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `employeeId` | string | ✅ | 사번 (PK) | HR Master |
| `name` | string | ✅ | 이름 | HR Master |
| `email` | string | ✅ | 이메일 | HR Master |
| `grade` | string | ✅ | 직급 (사원/대리/과장/차장/부장) | HR Master |
| `status` | enum | ✅ | ACTIVE/LEAVE/RESIGNED | HR Master |
| `hireDate` | date | ✅ | 입사일 | HR Master |
| `orgUnitId` | string | ✅ | 소속 조직 ID (FK) | HR Master |
| `jobRoleId` | string | | 직무 ID (FK) | HR Master |
| `managerId` | string | | 직속 상사 사번 (FK) | HR Master |

#### JobRole (직무)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `jobRoleId` | string | ✅ | 직무 ID (PK) | HR Master |
| `name` | string | ✅ | 직무명 | HR Master |
| `jobFamily` | string | ✅ | 직군 (개발/컨설팅/기획/영업) | HR Master |
| `levelBand` | string | | 레벨 밴드 (Junior/Mid/Senior/Lead) | HR Master |
| `description` | string | | 직무 설명 | HR Master |

---

### 3.2 Work & Portfolio 모듈

#### Opportunity (영업 기회)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `opportunityId` | string | ✅ | 기회 ID (PK) | BizForce |
| `name` | string | ✅ | 프로젝트명 | BizForce |
| `clientName` | string | ✅ | 고객사명 | BizForce |
| `industry` | string | | 산업군 | BizForce |
| `stage` | enum | ✅ | LEAD/QUALIFIED/PROPOSAL/NEGOTIATION/WON/LOST | BizForce |
| `dealValue` | number | ✅ | 계약 금액 (원) | BizForce |
| `closeProbability` | number | ✅ | 수주 확률 (0-1) | BizForce |
| `expectedStartDate` | date | | 예상 시작일 | BizForce |
| `expectedEndDate` | date | | 예상 종료일 | BizForce |
| `ownerEmployeeId` | string | ✅ | 담당 영업 사번 (FK) | BizForce |

#### Project (프로젝트)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `projectId` | string | ✅ | 프로젝트 ID (PK) | TMS |
| `name` | string | ✅ | 프로젝트명 | TMS |
| `opportunityId` | string | | 연결된 Opportunity ID (FK) | TMS |
| `status` | enum | ✅ | PLANNED/ACTIVE/COMPLETED/ON_HOLD/CANCELLED | TMS |
| `startDate` | date | ✅ | 시작일 | TMS |
| `endDate` | date | ✅ | 종료일 | TMS |
| `priority` | enum | ✅ | HIGH/MEDIUM/LOW | TMS |
| `pmEmployeeId` | string | ✅ | PM 사번 (FK) | TMS |
| `ownerOrgUnitId` | string | ✅ | 수행 조직 ID (FK) | TMS |
| `budgetAmount` | number | | 예산 (원) | TMS |
| `actualCost` | number | | 실제 비용 (원) | TMS |

#### WorkPackage (작업 패키지)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `workPackageId` | string | ✅ | WP ID (PK) | TMS |
| `projectId` | string | ✅ | 프로젝트 ID (FK) | TMS |
| `name` | string | ✅ | WP명 | TMS |
| `startDate` | date | ✅ | 시작일 | TMS |
| `endDate` | date | ✅ | 종료일 | TMS |
| `criticality` | enum | ✅ | CRITICAL/HIGH/MEDIUM/LOW | TMS |
| `estimatedFTE` | number | ✅ | 예상 투입 FTE | TMS |
| `status` | enum | ✅ | NOT_STARTED/IN_PROGRESS/COMPLETED | TMS |

---

### 3.3 Demand & Supply 모듈

#### DemandSignal (수요 신호)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `signalId` | string | ✅ | 신호 ID (PK) | BizForce |
| `opportunityId` | string | ✅ | Opportunity ID (FK) | BizForce |
| `sourceSystem` | string | ✅ | 원천 시스템 | BizForce |
| `signalType` | enum | ✅ | PIPELINE/FORECAST/CONFIRMED | BizForce |
| `closeProbability` | number | ✅ | 수주 확률 (0-1) | BizForce |
| `expectedStartDate` | date | ✅ | 예상 시작일 | BizForce |
| `createdAt` | datetime | ✅ | 생성일시 | BizForce |

#### ResourceDemand (리소스 수요)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `demandId` | string | ✅ | 수요 ID (PK) | TMS |
| `signalId` | string | | DemandSignal ID (FK) | TMS |
| `projectId` | string | | Project ID (FK) | TMS |
| `workPackageId` | string | | WorkPackage ID (FK) | TMS |
| `deliveryRoleId` | string | ✅ | 필요 역할 ID (FK) | TMS |
| `quantityFTE` | number | ✅ | 필요 FTE | TMS |
| `startDate` | date | ✅ | 시작일 | TMS |
| `endDate` | date | ✅ | 종료일 | TMS |
| `probability` | number | ✅ | 확정 확률 (0-1) | TMS |
| `priority` | enum | ✅ | HIGH/MEDIUM/LOW | TMS |

#### Availability (가용성)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `availabilityId` | string | ✅ | 가용성 ID (PK) | TMS |
| `employeeId` | string | ✅ | 사번 (FK) | TMS |
| `availableFTE` | number | ✅ | 가용 FTE (0-1) | TMS |
| `startDate` | date | ✅ | 시작일 | TMS |
| `endDate` | date | ✅ | 종료일 | TMS |
| `reason` | enum | | AVAILABLE/PARTIAL/LEAVE/PROJECT | TMS |

#### Assignment (배치)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `assignmentId` | string | ✅ | 배치 ID (PK) | TMS |
| `employeeId` | string | ✅ | 사번 (FK) | TMS |
| `projectId` | string | | 프로젝트 ID (FK) | TMS |
| `workPackageId` | string | | WP ID (FK) | TMS |
| `allocationFTE` | number | ✅ | 배치 FTE (0-1) | TMS |
| `startDate` | date | ✅ | 시작일 | TMS |
| `endDate` | date | ✅ | 종료일 | TMS |
| `role` | string | | 역할 (PM/개발자/아키텍트 등) | TMS |
| `status` | enum | ✅ | PLANNED/ACTIVE/COMPLETED | TMS |

#### TimeBucket (시간 버킷)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `bucketId` | string | ✅ | 버킷 ID (PK) | System |
| `granularity` | enum | ✅ | WEEK/MONTH/QUARTER | System |
| `startDate` | date | ✅ | 시작일 | System |
| `endDate` | date | ✅ | 종료일 | System |
| `year` | number | ✅ | 연도 | System |
| `week` | number | | 주차 (1-52) | System |
| `month` | number | | 월 (1-12) | System |
| `quarter` | number | | 분기 (1-4) | System |

---

### 3.4 R&R / Coverage 모듈

#### DeliveryRole (수행 역할)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `deliveryRoleId` | string | ✅ | 역할 ID (PK) | HR Master |
| `name` | string | ✅ | 역할명 (PM/아키텍트/개발자 등) | HR Master |
| `category` | enum | ✅ | MANAGEMENT/TECHNICAL/SUPPORT | HR Master |
| `requiredCompetencies` | array | | 필요 역량 ID 목록 | HR Master |

#### Responsibility (책임)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `responsibilityId` | string | ✅ | 책임 ID (PK) | HR Master |
| `name` | string | ✅ | 책임명 | HR Master |
| `description` | string | | 설명 | HR Master |
| `criticality` | enum | ✅ | CRITICAL/HIGH/MEDIUM/LOW | HR Master |
| `requiredRoleId` | string | | 필요 역할 ID (FK) | HR Master |

---

### 3.5 Competency 모듈

#### Competency (역량)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `competencyId` | string | ✅ | 역량 ID (PK) | Competency |
| `name` | string | ✅ | 역량명 | Competency |
| `domain` | enum | ✅ | TECHNICAL/BUSINESS/LEADERSHIP/SOFT | Competency |
| `category` | string | | 세부 카테고리 | Competency |
| `description` | string | | 설명 | Competency |
| `levelDefinitions` | object | | 레벨별 정의 (1-5) | Competency |

#### CompetencyEvidence (역량 증거)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `evidenceId` | string | ✅ | 증거 ID (PK) | Competency |
| `employeeId` | string | ✅ | 사번 (FK) | Competency |
| `competencyId` | string | ✅ | 역량 ID (FK) | Competency |
| `level` | number | ✅ | 레벨 (1-5) | Competency |
| `assessedAt` | date | ✅ | 평가일 | Competency |
| `sourceType` | enum | ✅ | SELF/MANAGER/360/CERT/PROJECT | Competency |
| `validUntil` | date | | 유효기간 | Competency |

---

### 3.6 Decision & Evaluation 모듈

#### DecisionCase (의사결정 케이스)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `decisionCaseId` | string | ✅ | 케이스 ID (PK) | System |
| `type` | enum | ✅ | CAPACITY_FORECAST/GO_NOGO/HEADCOUNT/COMPETENCY_GAP | System |
| `status` | enum | ✅ | DRAFT/ANALYZING/PENDING_APPROVAL/APPROVED/REJECTED | System |
| `title` | string | ✅ | 제목 | System |
| `description` | string | | 설명 | System |
| `requesterId` | string | ✅ | 요청자 사번 (FK) | System |
| `createdAt` | datetime | ✅ | 생성일시 | System |
| `updatedAt` | datetime | ✅ | 수정일시 | System |

#### Objective (목표)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `objectiveId` | string | ✅ | 목표 ID (PK) | System |
| `decisionCaseId` | string | ✅ | 케이스 ID (FK) | System |
| `metricType` | enum | ✅ | UTILIZATION/SUCCESS_PROB/COST/TIME/GAP_SCORE | System |
| `operator` | enum | ✅ | EQ/GT/GTE/LT/LTE/BETWEEN | System |
| `targetValue` | number | ✅ | 목표값 | System |
| `direction` | enum | | MAXIMIZE/MINIMIZE | System |

#### Constraint (제약)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `constraintId` | string | ✅ | 제약 ID (PK) | System |
| `decisionCaseId` | string | ✅ | 케이스 ID (FK) | System |
| `type` | enum | ✅ | RESOURCE/BUDGET/TIMELINE/POLICY | System |
| `severity` | enum | ✅ | HARD/SOFT | System |
| `expression` | string | ✅ | 제약 표현식 | System |

#### Option (대안)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `optionId` | string | ✅ | 대안 ID (PK) | System |
| `decisionCaseId` | string | ✅ | 케이스 ID (FK) | System |
| `name` | string | ✅ | 대안명 | System |
| `optionType` | enum | ✅ | INTERNAL/EXTERNAL/MIXED/UPSKILL | System |
| `description` | string | | 설명 | System |
| `rank` | number | | 순위 | System |

#### Evaluation (평가)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `evaluationId` | string | ✅ | 평가 ID (PK) | System |
| `optionId` | string | ✅ | 대안 ID (FK) | System |
| `totalScore` | number | ✅ | 총점 (0-100) | System |
| `successProbability` | number | | 성공확률 (0-1) | System |
| `rationale` | string | | 평가 근거 | System |
| `evaluatedAt` | datetime | ✅ | 평가일시 | System |

#### MetricValue (지표값)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `metricValueId` | string | ✅ | 지표값 ID (PK) | System |
| `evaluationId` | string | ✅ | 평가 ID (FK) | System |
| `metricType` | enum | ✅ | IMPACT/FEASIBILITY/RISK/COST/TIME | System |
| `asIsValue` | number | | As-Is 값 | System |
| `toBeValue` | number | | To-Be 값 | System |
| `delta` | number | | 차이값 | System |
| `score` | number | ✅ | 점수 (0-100) | System |

---

### 3.7 Forecast & Audit 모듈

#### Model (모델)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `modelId` | string | ✅ | 모델 ID (PK) | System |
| `name` | string | ✅ | 모델명 | System |
| `type` | enum | ✅ | HEURISTIC/RULES/ML | System |
| `version` | string | ✅ | 버전 | System |
| `description` | string | | 설명 | System |

#### ModelRun (모델 실행)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `runId` | string | ✅ | 실행 ID (PK) | System |
| `modelId` | string | ✅ | 모델 ID (FK) | System |
| `scenarioId` | string | | 시나리오 ID (FK) | System |
| `runAt` | datetime | ✅ | 실행일시 | System |
| `parameters` | object | | 실행 파라미터 | System |
| `status` | enum | ✅ | RUNNING/COMPLETED/FAILED | System |
| `duration` | number | | 실행 시간 (ms) | System |

#### ForecastPoint (예측 포인트)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `forecastPointId` | string | ✅ | 예측 ID (PK) | System |
| `runId` | string | ✅ | 실행 ID (FK) | System |
| `bucketId` | string | ✅ | 시간 버킷 ID (FK) | System |
| `subjectType` | enum | ✅ | ORG_UNIT/PROJECT/EMPLOYEE | System |
| `subjectId` | string | ✅ | 대상 ID | System |
| `metricType` | enum | ✅ | UTILIZATION/DEMAND/SUPPLY/SUCCESS_PROB | System |
| `value` | number | ✅ | 예측값 | System |
| `confidence` | number | ✅ | 신뢰도 (0-1) | System |

#### Finding (발견사항)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `findingId` | string | ✅ | 발견 ID (PK) | System |
| `runId` | string | ✅ | 실행 ID (FK) | System |
| `type` | enum | ✅ | BOTTLENECK/GAP/RISK/OPPORTUNITY | System |
| `severity` | enum | ✅ | CRITICAL/HIGH/MEDIUM/LOW | System |
| `narrative` | string | ✅ | 설명 | System |
| `rootCause` | string | | 근본 원인 | System |

#### Evidence (근거)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `evidenceId` | string | ✅ | 근거 ID (PK) | System |
| `findingId` | string | ✅ | 발견 ID (FK) | System |
| `sourceSystem` | string | ✅ | 원천 시스템 | System |
| `sourceType` | enum | ✅ | DATA/RULE/HISTORY/EXPERT | System |
| `sourceRef` | string | ✅ | 원천 참조 | System |
| `data` | object | | 데이터 | System |
| `confidence` | number | | 신뢰도 (0-1) | System |

---

### 3.8 HITL & Workflow 모듈

#### DecisionGate (의사결정 게이트)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `gateId` | string | ✅ | 게이트 ID (PK) | System |
| `decisionCaseId` | string | ✅ | 케이스 ID (FK) | System |
| `process` | enum | ✅ | VRB/PRE_PRB/PRB | System |
| `status` | enum | ✅ | PENDING/APPROVED/REJECTED/DEFERRED | System |
| `requestedAt` | datetime | ✅ | 요청일시 | System |

#### Approval (승인)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `approvalId` | string | ✅ | 승인 ID (PK) | System |
| `gateId` | string | ✅ | 게이트 ID (FK) | System |
| `decision` | enum | ✅ | APPROVED/REJECTED/DEFERRED | System |
| `approvedBy` | string | ✅ | 승인자 사번 (FK) | System |
| `approvedAt` | datetime | ✅ | 승인일시 | System |
| `comments` | string | | 코멘트 | System |

#### WorkflowTask (워크플로 태스크)

| 필드 | 타입 | 필수 | 설명 | 원천 |
|------|------|------|------|------|
| `taskId` | string | ✅ | 태스크 ID (PK) | System |
| `approvalId` | string | | 승인 ID (FK) | System |
| `actionId` | string | | 액션 ID (FK) | System |
| `type` | enum | ✅ | REASSIGN/HIRE/TRAIN/APPROVE/NOTIFY | System |
| `owner` | string | ✅ | 담당자 사번 (FK) | System |
| `dueDate` | date | ✅ | 마감일 | System |
| `status` | enum | ✅ | PENDING/IN_PROGRESS/COMPLETED/CANCELLED | System |

---

## 4. 데이터 통계

### 4.1 Mock 데이터 규모

| 모듈 | 엔터티 수 | 총 인스턴스 | 비고 |
|------|----------|------------|------|
| Workforce | 3 | ~130 | 직원 100, 조직 20, 직무 10 |
| Work | 3 | ~60 | 프로젝트 30, WP 30 |
| Demand/Supply | 5 | ~200 | 배치 150, 가용성 50 |
| R&R | 2 | ~30 | 역할 10, 책임 20 |
| Competency | 2 | ~100 | 역량 50, 증거 50 |
| Decision | 6 | ~50 | 케이스/옵션/평가 등 |
| Forecast | 5 | ~100 | 예측/발견/근거 등 |
| Workflow | 3 | ~30 | 게이트/승인/태스크 |
| **Total** | **29** | **~700** | |

---

## 5. 버전 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-23 | 초기 버전 작성 |

---

*이 문서는 PoC 진행 중 스키마가 변경될 수 있습니다.*
