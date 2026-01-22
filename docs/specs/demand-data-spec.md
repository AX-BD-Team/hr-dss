# HR 의사결정 지원 시스템 - Demand Data Specification v1

> 작성일: 2025-01-24 | 버전: 1.0

---

## 1. 개요

이 문서는 Capacity 예측 및 수요-공급 매칭을 위한 Demand 데이터 구조와 처리 방법을 정의합니다.

---

## 2. Demand 데이터 유형

### 2.1 Demand 소스 분류

| 유형          | 설명                  | 확정도        | 데이터 소스       |
| ------------- | --------------------- | ------------- | ----------------- |
| **Confirmed** | 확정 프로젝트 수요    | 100%          | TMS (Project)     |
| **Pipeline**  | 파이프라인 기회       | 가변 (10-90%) | CRM (Opportunity) |
| **Forecast**  | 예측 수요             | 추정치        | 영업 예측         |
| **Internal**  | 내부 투자 (R&D, 교육) | 계획 기반     | 내부 계획         |

### 2.2 Demand Signal 유형

```yaml
DemandSignalTypes:
  PROJECT_START:
    description: 신규 프로젝트 시작
    leadTime: 2-4주
    certainty: HIGH

  OPPORTUNITY_WON:
    description: 수주 확정
    leadTime: 4-8주
    certainty: HIGH

  PIPELINE_ADVANCE:
    description: 파이프라인 단계 진행
    leadTime: 가변
    certainty: MEDIUM

  RAMP_UP:
    description: 기존 프로젝트 인력 증가
    leadTime: 2-4주
    certainty: HIGH

  RAMP_DOWN:
    description: 기존 프로젝트 인력 감소
    leadTime: 2-4주
    certainty: HIGH

  EXTENSION:
    description: 프로젝트 기간 연장
    leadTime: 4-8주
    certainty: MEDIUM
```

---

## 3. Demand 데이터 스키마

### 3.1 ResourceDemand (리소스 수요)

```typescript
interface ResourceDemand {
  // 식별자
  demandId: string; // 형식: DEM-{YYYY}-{4digits}

  // 소스 정보
  sourceType: "PROJECT" | "OPPORTUNITY" | "FORECAST" | "INTERNAL";
  sourceId: string; // projectId 또는 opportunityId

  // 수요 상세
  requestedOrgUnitId: string; // 요청 조직
  requiredCompetencies: CompetencyRequirement[];

  // 수량 및 기간
  quantityFTE: number; // 필요 FTE
  startDate: string; // 시작일
  endDate: string; // 종료일

  // 확률 및 우선순위
  probability: number; // 0-1 (확정=1.0)
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

  // 상태
  status: "OPEN" | "PARTIALLY_FILLED" | "FILLED" | "CANCELLED";
  filledFTE: number; // 충족된 FTE

  // 제약조건
  constraints: DemandConstraints;

  // 메타데이터
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

interface CompetencyRequirement {
  competencyId: string;
  minimumLevel: number; // 1-5
  weight: number; // 중요도 가중치
  isRequired: boolean; // 필수 여부
}

interface DemandConstraints {
  minGrade?: string; // 최소 등급
  maxGrade?: string; // 최대 등급
  preferredOrgUnits?: string[]; // 선호 조직
  excludeEmployees?: string[]; // 제외 인력
  locationRequired?: string; // 위치 요건
  securityClearance?: string; // 보안 등급
}
```

### 3.2 DemandSignal (수요 시그널)

```typescript
interface DemandSignal {
  signalId: string; // 형식: SIG-{YYYY}-{6digits}

  // 시그널 정보
  signalType: string; // DemandSignalTypes 참조
  sourceType: string;
  sourceId: string;

  // 영향
  impactType: "INCREASE" | "DECREASE" | "SHIFT";
  affectedDemandId?: string;
  estimatedFTEChange: number;

  // 시간 정보
  detectedAt: string;
  effectiveFrom: string;
  effectiveTo?: string;

  // 확신도
  confidence: number; // 0-1

  // 상태
  status: "DETECTED" | "CONFIRMED" | "PROCESSED" | "EXPIRED";
}
```

### 3.3 DemandForecast (수요 예측)

```typescript
interface DemandForecast {
  forecastId: string; // 형식: FCT-{YYYY}-{4digits}

  // 예측 대상
  targetOrgUnitId: string;
  competencyDomain?: string;

  // 예측 기간
  forecastPeriod: string; // YYYY-Wxx 또는 YYYY-MM
  periodStart: string;
  periodEnd: string;

  // 예측값
  predictedDemandFTE: number;
  predictionLowerBound: number;
  predictionUpperBound: number;

  // 구성 요소
  components: {
    confirmed: number; // 확정 수요
    pipeline: number; // 파이프라인 (확률 가중)
    forecast: number; // 예측 수요
  };

  // 정확도 (사후 검증)
  actualDemandFTE?: number;
  accuracy?: number;

  // 메타데이터
  generatedAt: string;
  modelVersion: string;
}
```

---

## 4. 수요 계산 로직

### 4.1 기간별 총 수요 계산

```python
def calculate_total_demand(
    org_unit_id: str,
    start_date: date,
    end_date: date
) -> dict:
    """특정 조직/기간의 총 수요 계산"""

    # 1. 확정 수요 (프로젝트 배치)
    confirmed = sum(
        d.quantityFTE
        for d in get_demands(org_unit_id, start_date, end_date)
        if d.sourceType == 'PROJECT' and d.status != 'CANCELLED'
    )

    # 2. 파이프라인 수요 (확률 가중)
    pipeline = sum(
        d.quantityFTE * d.probability
        for d in get_demands(org_unit_id, start_date, end_date)
        if d.sourceType == 'OPPORTUNITY'
    )

    # 3. 예측 수요
    forecast = get_forecast_demand(org_unit_id, start_date, end_date)

    return {
        'confirmed': confirmed,
        'pipeline': pipeline,
        'forecast': forecast,
        'total_expected': confirmed + pipeline,
        'total_with_forecast': confirmed + pipeline + forecast,
    }
```

### 4.2 역량별 수요 집계

```python
def aggregate_demand_by_competency(
    org_unit_id: str,
    time_bucket: str
) -> dict[str, float]:
    """역량별 수요 FTE 집계"""

    demands = get_demands_for_period(org_unit_id, time_bucket)
    competency_demand = {}

    for demand in demands:
        effective_fte = demand.quantityFTE * demand.probability

        for req in demand.requiredCompetencies:
            if req.competencyId not in competency_demand:
                competency_demand[req.competencyId] = 0

            # 역량 요구사항 가중치 적용
            competency_demand[req.competencyId] += (
                effective_fte * req.weight
            )

    return competency_demand
```

### 4.3 파이프라인 확률 조정

```python
STAGE_PROBABILITY = {
    'LEAD': 0.10,
    'QUALIFIED': 0.25,
    'PROPOSAL': 0.50,
    'NEGOTIATION': 0.75,
    'CLOSING': 0.90,
    'WON': 1.00,
}

def calculate_pipeline_weighted_demand(opportunity: dict) -> float:
    """파이프라인 기회의 가중 수요 계산"""

    stage = opportunity['stage']
    base_prob = STAGE_PROBABILITY.get(stage, 0.10)

    # 고객사 이력 조정
    customer_factor = get_customer_win_rate_factor(opportunity['customerId'])

    # 프로젝트 유형 조정
    type_factor = get_project_type_factor(opportunity['projectType'])

    # 경쟁 상황 조정
    competition_factor = get_competition_factor(opportunity)

    adjusted_prob = (
        base_prob * customer_factor * type_factor * competition_factor
    )

    return opportunity['estimatedFTE'] * min(adjusted_prob, 1.0)
```

---

## 5. 수요-공급 매칭

### 5.1 매칭 알고리즘

```python
def match_demand_to_supply(
    demand: ResourceDemand,
    available_resources: list[Employee]
) -> list[MatchResult]:
    """수요와 가용 인력 매칭"""

    candidates = []

    for employee in available_resources:
        # 기본 자격 검증
        if not meets_basic_requirements(employee, demand):
            continue

        # 역량 매칭 점수
        competency_score = calculate_competency_match(
            employee, demand.requiredCompetencies
        )

        # 가용성 점수
        availability_score = calculate_availability_score(
            employee, demand.startDate, demand.endDate
        )

        # 비용 점수 (등급 기반)
        cost_score = calculate_cost_efficiency(employee, demand)

        # 종합 점수
        total_score = (
            competency_score * 0.50 +
            availability_score * 0.30 +
            cost_score * 0.20
        )

        candidates.append(MatchResult(
            employeeId=employee.employeeId,
            totalScore=total_score,
            competencyScore=competency_score,
            availabilityScore=availability_score,
            costScore=cost_score,
        ))

    return sorted(candidates, key=lambda x: x.totalScore, reverse=True)
```

### 5.2 역량 매칭 점수

```python
def calculate_competency_match(
    employee: Employee,
    requirements: list[CompetencyRequirement]
) -> float:
    """역량 매칭 점수 계산 (0-100)"""

    if not requirements:
        return 100.0

    total_weight = sum(r.weight for r in requirements)
    weighted_score = 0.0

    for req in requirements:
        employee_level = get_employee_competency_level(
            employee.employeeId, req.competencyId
        )

        if employee_level is None:
            if req.isRequired:
                return 0.0  # 필수 역량 미보유
            score = 0.0
        elif employee_level >= req.minimumLevel:
            # 초과 역량은 보너스
            score = min(100 + (employee_level - req.minimumLevel) * 10, 120)
        else:
            # 미달 역량은 감점
            gap = req.minimumLevel - employee_level
            score = max(0, 100 - gap * 30)

        weighted_score += score * (req.weight / total_weight)

    return min(weighted_score, 100.0)
```

---

## 6. 시간 버킷 관리

### 6.1 TimeBucket 정의

| 버킷 유형   | 기간 | 용도           |
| ----------- | ---- | -------------- |
| **WEEK**    | 7일  | 단기 운영 계획 |
| **MONTH**   | 월   | 중기 용량 계획 |
| **QUARTER** | 분기 | 전략적 계획    |

### 6.2 버킷별 집계

```python
def aggregate_by_time_bucket(
    demands: list[ResourceDemand],
    bucket_type: str,
    start_date: date,
    end_date: date
) -> list[BucketSummary]:
    """시간 버킷별 수요 집계"""

    buckets = generate_buckets(bucket_type, start_date, end_date)
    summaries = []

    for bucket in buckets:
        bucket_demands = [
            d for d in demands
            if overlaps(d.startDate, d.endDate, bucket.start, bucket.end)
        ]

        summary = BucketSummary(
            bucketId=bucket.id,
            bucketStart=bucket.start,
            bucketEnd=bucket.end,
            totalDemandFTE=sum(
                calculate_overlap_fte(d, bucket) * d.probability
                for d in bucket_demands
            ),
            demandCount=len(bucket_demands),
            byPriority={
                p: sum(d.quantityFTE for d in bucket_demands if d.priority == p)
                for p in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            }
        )
        summaries.append(summary)

    return summaries
```

---

## 7. 데이터 파이프라인

### 7.1 데이터 수집 흐름

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    TMS      │────►│   ETL 파이프 │────►│   Demand    │
│  (Projects) │     │    라인     │     │   Store     │
└─────────────┘     └─────────────┘     └─────────────┘
                           ▲
┌─────────────┐            │
│    CRM      │────────────┤
│(Opportunity)│            │
└─────────────┘            │
                           │
┌─────────────┐            │
│   영업 예측  │────────────┘
│  (Forecast) │
└─────────────┘
```

### 7.2 갱신 주기

| 데이터 소스       | 갱신 주기 | 트리거               |
| ----------------- | --------- | -------------------- |
| Project (TMS)     | 실시간    | 프로젝트 변경 이벤트 |
| Opportunity (CRM) | 일 1회    | 배치 동기화          |
| Forecast          | 주 1회    | 예측 모델 재실행     |
| Signal            | 실시간    | 이벤트 감지          |

---

## 8. API 인터페이스

### 8.1 수요 조회 API

```yaml
GET /api/v1/demands
  parameters:
    orgUnitId: string (required)
    startDate: date (required)
    endDate: date (required)
    sourceType: string[] (optional)
    status: string[] (optional)
    minProbability: number (optional)

  response:
    demands: ResourceDemand[]
    summary:
      totalFTE: number
      confirmedFTE: number
      pipelineFTE: number

GET /api/v1/demands/{demandId}
  response:
    demand: ResourceDemand
    matchingCandidates: MatchResult[]
    fulfillmentHistory: Assignment[]
```

### 8.2 수요 예측 API

```yaml
GET /api/v1/forecasts
  parameters:
    orgUnitId: string (required)
    horizon: string (required) # 12w, 6m, 1y
    bucketType: string (optional) # WEEK, MONTH, QUARTER

  response:
    forecasts: DemandForecast[]
    accuracy:
      historicalMAPE: number
      lastPeriodError: number
```

---

## 9. 버전 이력

| 버전 | 날짜       | 변경 내용      |
| ---- | ---------- | -------------- |
| 1.0  | 2025-01-24 | 초기 버전 작성 |

---

_이 문서는 PoC 진행 중 수요 데이터 구조가 변경될 수 있습니다._
