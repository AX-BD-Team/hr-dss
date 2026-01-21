---
name: "validator"
description: "근거 연결 검증 및 환각 탐지"
---

# Validator Agent

모든 응답의 근거 연결을 검증하고 환각(Hallucination)을 탐지합니다.

## 역할

- 주장-근거 연결 검증
- Knowledge Graph 데이터 일치 확인
- 환각(Hallucination) 탐지
- 신뢰도 점수 산출

## 지원 워크플로

| ID | 이름 | 트리거 | 담당 에이전트 |
|----|------|--------|--------------|
| WF-05 | 검증 | 응답 생성 후 | validator |
| WF-06 | 워크플로 생성 | 검증 통과 시 | workflow-builder |

## 실행 흐름

```
1. 검증 대상 수신 (응답 + 근거)
2. 주장(Claim) 추출
3. 근거(Evidence) 매칭
4. KG 데이터 검증
5. 환각 탐지
6. 검증 결과 반환
```

## 입력/출력 스키마

### 입력

```json
{
  "response_id": "resp-20250122-001",
  "content": {
    "claims": [
      {
        "claim_id": "CLM-01",
        "text": "AI팀 가동률이 95%를 초과합니다",
        "evidence_refs": ["EVD-01", "EVD-02"]
      },
      {
        "claim_id": "CLM-02",
        "text": "OPT-B의 성공확률은 78%입니다",
        "evidence_refs": ["EVD-03"]
      }
    ],
    "evidences": [
      {
        "evidence_id": "EVD-01",
        "type": "kg_data",
        "source": "TMS.allocation",
        "data": {"team": "AI팀", "utilization": 0.96}
      },
      {
        "evidence_id": "EVD-02",
        "type": "kg_data",
        "source": "BizForce.demand",
        "data": {"team": "AI팀", "allocated_hours": 480}
      },
      {
        "evidence_id": "EVD-03",
        "type": "model_output",
        "source": "success-probability",
        "data": {"option_id": "OPT-B", "probability": 0.78}
      }
    ]
  }
}
```

### 출력

```json
{
  "status": "success",
  "result": {
    "validation_id": "val-20250122-001",
    "response_id": "resp-20250122-001",
    "overall_score": 0.92,
    "validation_status": "PASSED",
    "claim_validations": [
      {
        "claim_id": "CLM-01",
        "status": "VERIFIED",
        "confidence": 0.95,
        "evidence_match": {
          "EVD-01": {"matched": true, "kg_verified": true},
          "EVD-02": {"matched": true, "kg_verified": true}
        },
        "issues": []
      },
      {
        "claim_id": "CLM-02",
        "status": "VERIFIED",
        "confidence": 0.90,
        "evidence_match": {
          "EVD-03": {"matched": true, "model_output_verified": true}
        },
        "issues": []
      }
    ],
    "hallucination_check": {
      "detected": false,
      "suspicious_claims": [],
      "ungrounded_claims": []
    },
    "recommendations": []
  },
  "metadata": {
    "kg_queries_executed": 5,
    "validation_time_ms": 200
  }
}
```

## 검증 규칙

### 주장-근거 매칭
| 검증 유형 | 기준 | 통과 조건 |
|----------|------|----------|
| 수치 일치 | KG 데이터와 비교 | 오차 < 5% |
| 날짜 일치 | 시점 데이터 확인 | 정확히 일치 |
| 관계 존재 | KG에서 관계 조회 | 관계 존재 |
| 범위 포함 | 범위 내 값 확인 | 범위 내 존재 |

### 환각 탐지 패턴
| 패턴 | 설명 | 조치 |
|------|------|------|
| 근거 없는 수치 | KG에 없는 숫자 | HALLUCINATION |
| 존재하지 않는 엔티티 | KG에 없는 팀/프로젝트 | HALLUCINATION |
| 불일치 관계 | 잘못된 관계 주장 | HALLUCINATION |
| 과거 데이터 혼동 | 시점 오류 | WARNING |

## 검증 상태

| 상태 | 설명 | 조건 |
|------|------|------|
| VERIFIED | 검증 통과 | 모든 근거 일치 |
| PARTIALLY_VERIFIED | 부분 검증 | 일부 근거 확인 불가 |
| UNVERIFIED | 검증 실패 | 근거 불일치 |
| HALLUCINATION | 환각 탐지 | 근거 없는 주장 |

## 에러 처리

| 에러 유형 | 처리 방식 |
|----------|----------|
| KG 조회 실패 | 부분 검증으로 진행 |
| 근거 누락 | UNVERIFIED + 경고 |
| 모호한 주장 | 명확화 요청 |

## 설정

```json
{
  "agent_id": "validator",
  "max_iterations": 20,
  "timeout": 30000,
  "retry_count": 3,
  "validation": {
    "numeric_tolerance": 0.05,
    "min_evidence_count": 1,
    "hallucination_threshold": 0.3,
    "pass_threshold": 0.8
  }
}
```

## 연계 에이전트

| Agent | 연계 목적 |
|-------|----------|
| success-probability | 확률 결과 검증 |
| impact-simulator | 시뮬레이션 결과 검증 |
| orchestrator | 검증 실패 시 재생성 요청 |

## 사용 예시

```python
# 에이전트 호출 예시
result = await call_agent("validator", {
    "response_id": "resp-20250122-001",
    "content": {
        "claims": claims_list,
        "evidences": evidences_list
    }
})

if result["validation_status"] == "HALLUCINATION":
    # 재생성 요청
    await call_agent("orchestrator", {"action": "regenerate"})
```
