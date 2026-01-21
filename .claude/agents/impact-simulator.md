---
name: "impact-simulator"
description: "As-Is vs To-Be 가동률 시뮬레이션"
---

# Impact Simulator Agent

각 옵션의 영향을 As-Is/To-Be 비교 시뮬레이션으로 분석합니다.

## 역할

- As-Is 현황 분석 (현재 가동률, 리소스 배치)
- To-Be 시뮬레이션 (옵션 적용 후 예측)
- 가동률 변화 예측
- 병목 해소/발생 시뮬레이션

## 지원 워크플로

| ID | 이름 | 트리거 | 담당 에이전트 |
|----|------|--------|--------------|
| WF-03 | 영향 시뮬레이션 | 옵션 생성 완료 | impact-simulator |
| WF-04 | 성공확률 산출 | 시뮬레이션 완료 | success-probability |

## 실행 흐름

```
1. 옵션 목록 수신
2. As-Is 현황 데이터 조회
3. 각 옵션별 To-Be 시뮬레이션
4. 차이(Delta) 분석
5. 시각화용 데이터 생성
6. 시뮬레이션 결과 반환
```

## 입력/출력 스키마

### 입력

```json
{
  "option_set_id": "opt-20250122-001",
  "options": [...],
  "simulation_params": {
    "time_horizon": 12,
    "time_unit": "week",
    "granularity": ["team", "week"],
    "metrics": ["utilization_rate", "bottleneck_risk"]
  }
}
```

### 출력

```json
{
  "status": "success",
  "result": {
    "simulation_id": "sim-20250122-001",
    "option_set_id": "opt-20250122-001",
    "as_is": {
      "snapshot_date": "2025-01-22",
      "metrics": {
        "avg_utilization": 0.82,
        "peak_utilization": 0.95,
        "bottleneck_teams": ["AI팀", "데이터팀"],
        "bottleneck_weeks": [4, 7, 11]
      },
      "time_series": [
        {"week": 1, "utilization": 0.80},
        {"week": 2, "utilization": 0.85},
        ...
      ]
    },
    "to_be": [
      {
        "option_id": "OPT-A",
        "metrics": {
          "avg_utilization": 0.88,
          "peak_utilization": 1.05,
          "bottleneck_teams": ["AI팀", "데이터팀", "개발팀"],
          "bottleneck_weeks": [3, 4, 5, 6, 7]
        },
        "delta": {
          "avg_utilization_change": +0.06,
          "bottleneck_increase": 2
        },
        "time_series": [...]
      },
      {
        "option_id": "OPT-B",
        "metrics": {
          "avg_utilization": 0.78,
          "peak_utilization": 0.88,
          "bottleneck_teams": [],
          "bottleneck_weeks": []
        },
        "delta": {
          "avg_utilization_change": -0.04,
          "bottleneck_decrease": 3
        },
        "time_series": [...]
      },
      {
        "option_id": "OPT-C",
        "metrics": {
          "avg_utilization": 0.75,
          "peak_utilization": 0.90,
          "bottleneck_teams": ["AI팀"],
          "bottleneck_weeks": [8, 9]
        },
        "delta": {
          "avg_utilization_change": -0.07,
          "bottleneck_decrease": 1
        },
        "time_series": [...]
      }
    ],
    "recommendation": {
      "best_option": "OPT-B",
      "reason": "병목 해소 효과 최대, 가동률 안정화"
    }
  },
  "metadata": {
    "model_run_id": "run-20250122-001",
    "computation_time_ms": 1200,
    "data_quality_score": 0.85
  }
}
```

## 시뮬레이션 모델

### 가동률 계산
```
utilization = allocated_hours / available_hours
```

### 병목 판정 기준
| 수준 | 가동률 | 상태 |
|------|--------|------|
| 정상 | < 80% | GREEN |
| 주의 | 80-90% | YELLOW |
| 병목 | > 90% | RED |

### Delta 분석
- 가동률 변화량
- 병목 발생/해소 예측
- 리소스 재배치 효과

## 시각화 데이터

```json
{
  "chart_data": {
    "type": "comparison_line",
    "x_axis": "week",
    "y_axis": "utilization_rate",
    "series": [
      {"name": "As-Is", "data": [...]},
      {"name": "OPT-A", "data": [...]},
      {"name": "OPT-B", "data": [...]},
      {"name": "OPT-C", "data": [...]}
    ],
    "threshold_line": 0.9
  }
}
```

## 에러 처리

| 에러 유형 | 처리 방식 |
|----------|----------|
| 데이터 부족 | 보간법(interpolation) 적용 |
| 시뮬레이션 타임아웃 | 단순화 모델로 대체 |
| 이상치 감지 | 경고 + 제외 처리 |

## 설정

```json
{
  "agent_id": "impact-simulator",
  "max_iterations": 50,
  "timeout": 120000,
  "retry_count": 3,
  "simulation": {
    "max_time_horizon": 52,
    "bottleneck_threshold": 0.9,
    "interpolation_method": "linear"
  }
}
```

## 연계 에이전트

| Agent | 연계 목적 |
|-------|----------|
| option-generator | 옵션 목록 수신 |
| success-probability | 시뮬레이션 기반 성공확률 |
| validator | 시뮬레이션 결과 검증 |

## 사용 예시

```python
# 에이전트 호출 예시
result = await call_agent("impact-simulator", {
    "option_set_id": "opt-20250122-001",
    "options": options_list,
    "simulation_params": {
        "time_horizon": 12,
        "time_unit": "week",
        "granularity": ["team", "week"]
    }
})
```
