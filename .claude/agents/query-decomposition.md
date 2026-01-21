---
name: "query-decomposition"
description: "자연어 질문을 목표/제약/기간으로 분해"
---

# Query Decomposition Agent

자연어 질문을 구조화된 형태(목표/제약/기간)로 분해합니다.

## 역할

- 사용자 질문에서 의도(Intent) 추출
- 목표(Goal), 제약(Constraint), 기간(TimeFrame) 분리
- 암묵적 조건 명시화
- 유스케이스 매핑 (A-1, B-1, C-1, D-1)

## 지원 워크플로

| ID | 이름 | 트리거 | 담당 에이전트 |
|----|------|--------|--------------|
| WF-01 | 질문 분석 | 자연어 질문 입력 | query-decomposition |
| WF-02 | 의사결정 요청 | 분해된 질문 | option-generator |

## 실행 흐름

```
1. 자연어 질문 수신
2. Intent 분류 (Capacity/GoNogo/Headcount/Competency)
3. 목표(Goal) 추출
4. 제약조건(Constraint) 추출
5. 시간 범위(TimeFrame) 추출
6. 구조화된 Query 반환
```

## 입력/출력 스키마

### 입력

```json
{
  "question": "향후 12주 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘",
  "context": {
    "user_role": "HR_Manager",
    "org_scope": "전사"
  }
}
```

### 출력

```json
{
  "status": "success",
  "result": {
    "query_id": "qry-20250122-001",
    "intent": "CAPACITY_FORECAST",
    "usecase_id": "A-1",
    "decomposition": {
      "goals": [
        {
          "goal_id": "G-01",
          "description": "가동률 90% 초과 주차 식별",
          "metric": "utilization_rate",
          "threshold": 0.9,
          "operator": ">"
        },
        {
          "goal_id": "G-02",
          "description": "병목 원인 분석",
          "output_type": "root_cause_analysis"
        }
      ],
      "constraints": [
        {
          "constraint_id": "C-01",
          "type": "scope",
          "dimension": "organization",
          "granularity": ["본부", "팀"]
        }
      ],
      "time_frame": {
        "type": "rolling",
        "duration": 12,
        "unit": "week",
        "direction": "future"
      }
    },
    "confidence": 0.92
  },
  "metadata": {
    "processing_time_ms": 150,
    "model_version": "claude-sonnet-4-20250514"
  }
}
```

## Intent 분류 기준

| Intent | 키워드 | 유스케이스 |
|--------|--------|-----------|
| CAPACITY_FORECAST | 가동률, 병목, 리소스 부족 | A-1 |
| GO_NOGO | 수행 가능, 내부/외부, 성공확률 | B-1 |
| HEADCOUNT_ANALYSIS | 증원, 인력 요청, TO | C-1 |
| COMPETENCY_GAP | 역량 갭, 스킬 부족, 교육 ROI | D-1 |

## 분해 규칙

### Goal 추출
- 동사구에서 목표 식별: "예측해줘", "분석해줘", "비교해줘"
- 측정 가능한 지표로 변환
- 임계값이 있으면 threshold로 추출

### Constraint 추출
- 범위 제한: 조직, 기간, 직군
- 필터 조건: "A팀만", "시니어 이상"
- 우선순위: "가장 먼저", "Top 10"

### TimeFrame 추출
- 절대 기간: "2025년 1분기"
- 상대 기간: "향후 12주", "지난 3개월"
- 없으면 기본값: 현재 분기

## 에러 처리

| 에러 유형 | 처리 방식 |
|----------|----------|
| 모호한 질문 | 명확화 요청 (clarification_needed) |
| 복합 Intent | 주요 Intent 선택 + 부가 Intent 표시 |
| 시간 범위 미지정 | 기본값 적용 + 경고 |
| 지원하지 않는 질문 | unsupported_query 반환 |

## 설정

```json
{
  "agent_id": "query-decomposition",
  "max_iterations": 10,
  "timeout": 30000,
  "retry_count": 3,
  "default_time_frame": {
    "duration": 4,
    "unit": "week"
  },
  "confidence_threshold": 0.7
}
```

## 연계 에이전트

| Agent | 연계 목적 |
|-------|----------|
| orchestrator | 분해된 질문 전달 |
| option-generator | 의사결정 옵션 생성 요청 |
| validator | 분해 결과 검증 |

## 사용 예시

```python
# 에이전트 호출 예시
result = await call_agent("query-decomposition", {
    "question": "OOO팀 1명 증원 요청의 원인을 분석해줘",
    "context": {
        "user_role": "HR_Manager",
        "org_scope": "OOO팀"
    }
})

# 결과: intent=HEADCOUNT_ANALYSIS, usecase_id=C-1
```
