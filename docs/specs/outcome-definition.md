# HR 의사결정 지원 시스템 - Outcome Definition v1

> 작성일: 2025-01-24 | 버전: 1.0

---

## 1. 개요

이 문서는 예측 모델의 학습 및 평가에 사용되는 Outcome(성공/실패) 기준을 정의합니다.

---

## 2. 프로젝트 성공 기준

### 2.1 성공 판정 기준

프로젝트의 성공/실패는 다음 기준으로 판정합니다:

| 기준 | 가중치 | 성공 조건 | 측정 방법 | 데이터 소스 |
|------|--------|----------|----------|-------------|
| **납기 준수** | 40% | 실제 종료일 ≤ 계획 종료일 + 허용오차 | `actualEndDate - plannedEndDate` | TMS |
| **마진 목표 달성** | 30% | 실제 마진 ≥ 목표 마진 × 0.9 | `actualMargin / targetMargin` | 정산 데이터 |
| **품질 목표 달성** | 20% | 클레임 건수 = 0, 재작업률 < 5% | 클레임/재작업 건수 | QA 시스템 |
| **고객 만족** | 10% | CSAT ≥ 4.0 (5점 만점) | 고객 설문 | CRM |

### 2.2 종합 성공 점수 계산

```python
def calculate_success_score(project: dict) -> float:
    """프로젝트 성공 점수 계산 (0-100)"""
    scores = {
        "schedule": calculate_schedule_score(project),  # 0-100
        "margin": calculate_margin_score(project),      # 0-100
        "quality": calculate_quality_score(project),    # 0-100
        "satisfaction": calculate_satisfaction_score(project),  # 0-100
    }

    weights = {
        "schedule": 0.40,
        "margin": 0.30,
        "quality": 0.20,
        "satisfaction": 0.10,
    }

    return sum(scores[k] * weights[k] for k in scores)
```

### 2.3 성공 등급 분류

| 등급 | 점수 범위 | 설명 | 라벨 |
|------|----------|------|------|
| **A (Excellent)** | 90-100 | 모든 목표 초과 달성 | SUCCESS |
| **B (Good)** | 75-89 | 대부분 목표 달성 | SUCCESS |
| **C (Acceptable)** | 60-74 | 최소 요건 충족 | PARTIAL |
| **D (Poor)** | 40-59 | 일부 목표 미달 | PARTIAL |
| **F (Failure)** | 0-39 | 심각한 미달 | FAILURE |

---

## 3. 세부 Outcome 정의

### 3.1 납기 준수 (Schedule Adherence)

| 상태 | 조건 | 점수 |
|------|------|------|
| Early | `actual <= planned - 7days` | 100 |
| On-time | `planned - 7days < actual <= planned` | 95 |
| Minor Delay | `planned < actual <= planned + 14days` | 75 |
| Moderate Delay | `planned + 14days < actual <= planned + 30days` | 50 |
| Major Delay | `actual > planned + 30days` | 20 |
| Not Completed | 프로젝트 미완료 | 0 |

```python
def calculate_schedule_score(project: dict) -> float:
    planned = project["plannedEndDate"]
    actual = project.get("actualEndDate")

    if actual is None:
        return 0  # Not completed

    delay_days = (actual - planned).days

    if delay_days <= -7:
        return 100
    elif delay_days <= 0:
        return 95
    elif delay_days <= 14:
        return 75
    elif delay_days <= 30:
        return 50
    else:
        return 20
```

### 3.2 마진 달성 (Margin Achievement)

| 상태 | 조건 | 점수 |
|------|------|------|
| Exceeded | `actual >= target × 1.1` | 100 |
| Met | `target × 0.9 <= actual < target × 1.1` | 90 |
| Near Miss | `target × 0.7 <= actual < target × 0.9` | 60 |
| Below Target | `target × 0.5 <= actual < target × 0.7` | 30 |
| Critical | `actual < target × 0.5` | 0 |

```python
def calculate_margin_score(project: dict) -> float:
    target = project["targetMargin"]
    actual = project.get("actualMargin", 0)

    if target == 0:
        return 50  # N/A

    ratio = actual / target

    if ratio >= 1.1:
        return 100
    elif ratio >= 0.9:
        return 90
    elif ratio >= 0.7:
        return 60
    elif ratio >= 0.5:
        return 30
    else:
        return 0
```

### 3.3 품질 (Quality)

| 상태 | 조건 | 점수 |
|------|------|------|
| Excellent | 클레임 0건 + 재작업률 0% | 100 |
| Good | 클레임 0건 + 재작업률 < 5% | 85 |
| Acceptable | 클레임 1-2건 또는 재작업률 5-10% | 60 |
| Poor | 클레임 3건 이상 또는 재작업률 10-20% | 30 |
| Critical | 클레임 5건 이상 또는 재작업률 > 20% | 0 |

### 3.4 고객 만족 (Customer Satisfaction)

| 상태 | 조건 | 점수 |
|------|------|------|
| Excellent | CSAT ≥ 4.5 | 100 |
| Good | 4.0 ≤ CSAT < 4.5 | 85 |
| Acceptable | 3.5 ≤ CSAT < 4.0 | 60 |
| Poor | 3.0 ≤ CSAT < 3.5 | 30 |
| Critical | CSAT < 3.0 | 0 |

---

## 4. 예측 대상 Outcome

### 4.1 Go/No-go 의사결정용

| Outcome | 설명 | 예측 시점 | 사용 질문 |
|---------|------|----------|----------|
| **SUCCESS_PROBABILITY** | 프로젝트 성공 확률 | 수주 전 | B-1 |
| **EXPECTED_MARGIN** | 예상 마진율 | 수주 전 | B-1 |
| **RESOURCE_FIT** | 리소스 매칭 적합도 | 수주 전 | B-1 |
| **RISK_LEVEL** | 종합 리스크 수준 | 수주 전 | B-1 |

### 4.2 Capacity 예측용

| Outcome | 설명 | 예측 시점 | 사용 질문 |
|---------|------|----------|----------|
| **UTILIZATION** | 가동률 | 향후 12주 | A-1 |
| **BOTTLENECK_PROBABILITY** | 병목 발생 확률 | 향후 12주 | A-1 |
| **DEMAND_ACCURACY** | 수요 예측 정확도 | 사후 검증 | A-1 |

### 4.3 증원 분석용

| Outcome | 설명 | 예측 시점 | 사용 질문 |
|---------|------|----------|----------|
| **HEADCOUNT_JUSTIFIED** | 증원 정당성 | 요청 시점 | C-1 |
| **ROOT_CAUSE_ACCURACY** | 원인 분석 정확도 | 사후 검증 | C-1 |

### 4.4 역량 갭 분석용

| Outcome | 설명 | 예측 시점 | 사용 질문 |
|---------|------|----------|----------|
| **GAP_CLOSURE_RATE** | 갭 해소율 | 투자 후 1년 | D-1 |
| **ROI_ACHIEVED** | ROI 달성 여부 | 투자 후 1년 | D-1 |

---

## 5. 라벨링 가이드라인

### 5.1 라벨 데이터 구조

```json
{
  "labelId": "LBL-PRJ-2024-0001",
  "subjectType": "PROJECT",
  "subjectId": "PRJ-2024-0001",
  "outcomeType": "PROJECT_SUCCESS",
  "labeledAt": "2025-01-24",
  "labeledBy": "SYSTEM",
  "scores": {
    "schedule": 95,
    "margin": 90,
    "quality": 85,
    "satisfaction": 80
  },
  "totalScore": 90.5,
  "label": "SUCCESS",
  "confidence": 1.0,
  "evidence": [
    {
      "metric": "schedule",
      "value": "actualEndDate: 2024-06-28, plannedEndDate: 2024-06-30",
      "source": "TMS"
    },
    {
      "metric": "margin",
      "value": "actualMargin: 18%, targetMargin: 15%",
      "source": "Finance"
    }
  ]
}
```

### 5.2 라벨링 프로세스

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  데이터 수집  │ ──► │  자동 라벨링  │ ──► │  검증/보정   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │
       ▼                   ▼                    ▼
   TMS, Finance,      규칙 기반 점수       전문가 리뷰
   CRM, QA 연동         산출 및 분류        (샘플링)
```

### 5.3 라벨 품질 기준

| 기준 | 목표 | 측정 방법 |
|------|------|----------|
| 완전성 | > 95% | 필수 필드 존재율 |
| 일관성 | > 90% | 동일 케이스 재라벨링 일치율 |
| 정확성 | > 85% | 전문가 검증 일치율 |

---

## 6. 휴리스틱 기반 예측

라벨 데이터가 부족한 초기에는 휴리스틱 기반 예측을 사용합니다.

### 6.1 성공확률 휴리스틱

```python
def heuristic_success_probability(project: dict, resources: list) -> float:
    """휴리스틱 기반 성공확률 예측"""

    # 기본 확률 (프로젝트 유형별)
    base_prob = PROJECT_TYPE_BASE_PROB.get(project["type"], 0.70)

    # 리소스 매칭 팩터
    resource_match = calculate_resource_match(project, resources)
    resource_factor = 0.5 + (resource_match * 0.7)  # 0.5 ~ 1.2

    # 역량 매칭 팩터
    competency_match = calculate_competency_match(project, resources)
    competency_factor = 0.5 + (competency_match * 0.7)  # 0.5 ~ 1.2

    # 과거 이력 팩터
    history_factor = calculate_history_factor(project)  # 0.7 ~ 1.3

    # 리스크 팩터
    risk_factor = 1.0 - (calculate_risk_score(project) * 0.5)  # 0.5 ~ 1.0

    # 종합 확률
    prob = base_prob * resource_factor * competency_factor * history_factor * risk_factor

    return min(max(prob, 0.0), 1.0)  # 0 ~ 1 범위로 제한
```

### 6.2 가동률 휴리스틱

```python
def heuristic_utilization(org_unit: str, time_bucket: str) -> float:
    """휴리스틱 기반 가동률 예측"""

    # 현재 배치 FTE 합계
    assigned_fte = get_assigned_fte(org_unit, time_bucket)

    # 확정 수요
    confirmed_demand = get_confirmed_demand(org_unit, time_bucket)

    # 파이프라인 수요 (확률 가중)
    pipeline_demand = sum(
        d["quantityFTE"] * d["probability"]
        for d in get_pipeline_demand(org_unit, time_bucket)
    )

    # 가용 인력
    available_fte = get_available_fte(org_unit, time_bucket)

    # 가동률 = (배치 + 확정수요 + 파이프라인수요) / 가용인력
    total_demand = assigned_fte + confirmed_demand + pipeline_demand

    if available_fte == 0:
        return 1.0

    return total_demand / available_fte
```

---

## 7. 검증 및 피드백 루프

### 7.1 예측 vs 실제 비교

| 지표 | 계산 방법 | 목표 |
|------|----------|------|
| MAPE | `mean(abs(predicted - actual) / actual)` | < 20% |
| 분류 정확도 | `correct_predictions / total_predictions` | > 80% |
| Precision | `true_positive / (true_positive + false_positive)` | > 75% |
| Recall | `true_positive / (true_positive + false_negative)` | > 75% |

### 7.2 피드백 루프

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   예측 수행   │ ──► │  실제 결과   │ ──► │   모델 개선  │
└─────────────┘     └─────────────┘     └─────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                     피드백 루프
```

---

## 8. 버전 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-24 | 초기 버전 작성 |

---

*이 문서는 PoC 진행 중 Outcome 정의가 변경될 수 있습니다.*
