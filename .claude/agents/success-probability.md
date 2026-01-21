---
name: "success-probability"
description: "휴리스틱+모델 기반 성공확률 산출"
---

# Success Probability Agent

각 옵션의 성공확률을 휴리스틱과 모델 기반으로 산출합니다.

## 역할

- 휴리스틱 기반 성공확률 계산
- 모델 기반 예측 (히스토리 데이터 활용)
- 신뢰구간 산출
- 주요 성공/실패 요인 식별

## 지원 워크플로

| ID | 이름 | 트리거 | 담당 에이전트 |
|----|------|--------|--------------|
| WF-04 | 성공확률 산출 | 시뮬레이션 완료 | success-probability |
| WF-05 | 검증 | 확률 산출 완료 | validator |

## 실행 흐름

```
1. 시뮬레이션 결과 수신
2. 휴리스틱 점수 계산
3. 히스토리 기반 모델 예측
4. 가중 평균으로 최종 확률 산출
5. 신뢰구간 및 요인 분석
6. 성공확률 결과 반환
```

## 입력/출력 스키마

### 입력

```json
{
  "simulation_id": "sim-20250122-001",
  "simulation_result": {...},
  "context": {
    "project_type": "DX",
    "project_size": "large",
    "organization": "디지털혁신본부"
  }
}
```

### 출력

```json
{
  "status": "success",
  "result": {
    "probability_set_id": "prob-20250122-001",
    "simulation_id": "sim-20250122-001",
    "probabilities": [
      {
        "option_id": "OPT-A",
        "success_probability": 0.55,
        "confidence_interval": {
          "lower": 0.45,
          "upper": 0.65,
          "confidence_level": 0.95
        },
        "components": {
          "heuristic_score": 0.50,
          "model_score": 0.60,
          "heuristic_weight": 0.4,
          "model_weight": 0.6
        },
        "success_factors": [
          {"factor": "내부 역량 보유", "impact": 0.15},
          {"factor": "유사 프로젝트 경험", "impact": 0.10}
        ],
        "risk_factors": [
          {"factor": "역량 갭 (AI/ML)", "impact": -0.25},
          {"factor": "일정 촉박", "impact": -0.15}
        ]
      },
      {
        "option_id": "OPT-B",
        "success_probability": 0.78,
        "confidence_interval": {
          "lower": 0.70,
          "upper": 0.86,
          "confidence_level": 0.95
        },
        "components": {
          "heuristic_score": 0.75,
          "model_score": 0.80,
          "heuristic_weight": 0.4,
          "model_weight": 0.6
        },
        "success_factors": [
          {"factor": "역량 갭 해소", "impact": 0.20},
          {"factor": "리소스 여유", "impact": 0.15}
        ],
        "risk_factors": [
          {"factor": "외부 의존성", "impact": -0.10},
          {"factor": "비용 증가", "impact": -0.05}
        ]
      },
      {
        "option_id": "OPT-C",
        "success_probability": 0.65,
        "confidence_interval": {
          "lower": 0.55,
          "upper": 0.75,
          "confidence_level": 0.95
        },
        "components": {
          "heuristic_score": 0.60,
          "model_score": 0.68,
          "heuristic_weight": 0.4,
          "model_weight": 0.6
        },
        "success_factors": [
          {"factor": "장기 역량 확보", "impact": 0.20},
          {"factor": "내부 통제", "impact": 0.10}
        ],
        "risk_factors": [
          {"factor": "일정 지연", "impact": -0.20},
          {"factor": "학습 곡선", "impact": -0.10}
        ]
      }
    ],
    "recommendation": {
      "best_option": "OPT-B",
      "probability": 0.78,
      "rationale": "가장 높은 성공확률, 리스크 대비 효과 최대"
    }
  },
  "metadata": {
    "model_version": "prob-model-v1.2",
    "history_sample_size": 150,
    "computation_time_ms": 300
  }
}
```

## 휴리스틱 점수 계산

### 요소별 가중치
| 요소 | 가중치 | 평가 기준 |
|------|--------|----------|
| 역량 커버리지 | 0.25 | skill_coverage |
| 가동률 안정성 | 0.20 | 1 - peak_utilization/1.2 |
| 일정 여유 | 0.15 | buffer_ratio |
| 비용 효율 | 0.15 | 1 - cost_index |
| 리스크 수준 | 0.15 | 1 - risk_index |
| 팀 경험도 | 0.10 | similar_project_count/5 |

### 계산 공식
```
heuristic_score = Σ(weight_i × score_i)
```

## 모델 기반 예측

### 특성(Features)
- 프로젝트 유형
- 프로젝트 규모
- 팀 구성
- 역량 커버리지
- 가동률
- 외부 의존도

### 유사 프로젝트 매칭
```
similarity = cosine_similarity(current_features, historical_features)
success_rate = weighted_average(historical_outcomes, similarity_weights)
```

## 신뢰구간 산출

```
CI = probability ± z * sqrt(p(1-p)/n)

where:
- z = 1.96 (95% 신뢰수준)
- p = success_probability
- n = historical_sample_size
```

## 에러 처리

| 에러 유형 | 처리 방식 |
|----------|----------|
| 히스토리 데이터 부족 | 휴리스틱 가중치 증가 |
| 이상치 프로젝트 | 제외 후 재계산 |
| 특성 누락 | 기본값 적용 + 신뢰구간 확대 |

## 설정

```json
{
  "agent_id": "success-probability",
  "max_iterations": 30,
  "timeout": 60000,
  "retry_count": 3,
  "probability": {
    "heuristic_weight": 0.4,
    "model_weight": 0.6,
    "min_history_samples": 30,
    "confidence_level": 0.95
  }
}
```

## 연계 에이전트

| Agent | 연계 목적 |
|-------|----------|
| impact-simulator | 시뮬레이션 결과 수신 |
| validator | 확률 검증 |
| orchestrator | 최종 결과 전달 |

## 사용 예시

```python
# 에이전트 호출 예시
result = await call_agent("success-probability", {
    "simulation_id": "sim-20250122-001",
    "simulation_result": simulation_data,
    "context": {
        "project_type": "DX",
        "project_size": "large"
    }
})
```
