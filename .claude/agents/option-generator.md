---
name: "option-generator"
description: "의사결정을 위한 대안 3개 생성 (내부/혼합/역량강화)"
---

# Option Generator Agent

의사결정을 위한 3가지 대안(Option)을 생성합니다.

## 역할

- 분해된 질문 기반 대안 생성
- 내부 수행 / 혼합 / 역량 강화 옵션 제시
- 각 옵션별 장단점 분석
- 비용/리스크/효과 초기 평가

## 지원 워크플로

| ID | 이름 | 트리거 | 담당 에이전트 |
|----|------|--------|--------------|
| WF-02 | 옵션 생성 | 분해된 질문 수신 | option-generator |
| WF-03 | 영향 시뮬레이션 | 옵션 생성 완료 | impact-simulator |

## 실행 흐름

```
1. 분해된 질문(Query) 수신
2. Knowledge Graph에서 관련 데이터 조회
3. 옵션 템플릿 선택 (유스케이스별)
4. 3개 대안 생성
5. 초기 평가 수행
6. 옵션 목록 반환
```

## 입력/출력 스키마

### 입력

```json
{
  "query": {
    "query_id": "qry-20250122-001",
    "intent": "GO_NOGO",
    "usecase_id": "B-1",
    "decomposition": {
      "goals": [...],
      "constraints": [...],
      "time_frame": {...}
    }
  },
  "context": {
    "project_name": "100억 미디어 AX",
    "project_budget": 10000000000,
    "required_skills": ["AI/ML", "Data Engineering", "Cloud"]
  }
}
```

### 출력

```json
{
  "status": "success",
  "result": {
    "option_set_id": "opt-20250122-001",
    "query_id": "qry-20250122-001",
    "options": [
      {
        "option_id": "OPT-A",
        "name": "내부 수행",
        "type": "INTERNAL",
        "description": "기존 내부 인력으로 프로젝트 수행",
        "resource_plan": {
          "internal_headcount": 8,
          "external_headcount": 0,
          "skill_coverage": 0.75
        },
        "initial_assessment": {
          "feasibility": 0.65,
          "cost_index": 0.7,
          "risk_index": 0.4,
          "time_to_delivery": "16주"
        },
        "pros": ["비용 절감", "내부 역량 축적"],
        "cons": ["역량 갭 존재", "일정 리스크"]
      },
      {
        "option_id": "OPT-B",
        "name": "혼합 수행",
        "type": "HYBRID",
        "description": "내부 + 외부 협력사 혼합 구성",
        "resource_plan": {
          "internal_headcount": 5,
          "external_headcount": 4,
          "skill_coverage": 0.95
        },
        "initial_assessment": {
          "feasibility": 0.85,
          "cost_index": 1.0,
          "risk_index": 0.25,
          "time_to_delivery": "12주"
        },
        "pros": ["역량 갭 해소", "일정 준수 가능"],
        "cons": ["비용 증가", "외부 의존성"]
      },
      {
        "option_id": "OPT-C",
        "name": "역량 강화 후 수행",
        "type": "CAPABILITY_BUILD",
        "description": "역량 투자 후 내부 수행",
        "resource_plan": {
          "internal_headcount": 8,
          "external_headcount": 0,
          "training_required": ["AI/ML 부트캠프", "Cloud 인증"]
        },
        "initial_assessment": {
          "feasibility": 0.70,
          "cost_index": 0.85,
          "risk_index": 0.35,
          "time_to_delivery": "20주"
        },
        "pros": ["장기 역량 확보", "지속 가능성"],
        "cons": ["초기 일정 지연", "학습 곡선"]
      }
    ]
  },
  "metadata": {
    "generation_time_ms": 500,
    "data_sources": ["TMS", "HR_Master", "Skill_DB"]
  }
}
```

## 옵션 템플릿

### A-1 (Capacity Forecast)
- **OPT-A**: 현재 인력 유지 + 업무 재배치
- **OPT-B**: 외부 리소스 투입
- **OPT-C**: 프로젝트 일정 조정

### B-1 (Go/No-go)
- **OPT-A**: 내부 수행
- **OPT-B**: 혼합 수행 (내부 + 외부)
- **OPT-C**: 역량 강화 후 수행

### C-1 (Headcount Analysis)
- **OPT-A**: 증원 승인
- **OPT-B**: 업무 재배치로 대응
- **OPT-C**: 외부 인력 활용

### D-1 (Competency Gap)
- **OPT-A**: 내부 교육 프로그램
- **OPT-B**: 외부 교육 + 채용
- **OPT-C**: 전략적 파트너십

## 에러 처리

| 에러 유형 | 처리 방식 |
|----------|----------|
| 데이터 부족 | 가정(assumption) 명시 후 진행 |
| 옵션 생성 실패 | 기본 템플릿 적용 |
| KG 조회 실패 | Mock 데이터로 대체 |

## 설정

```json
{
  "agent_id": "option-generator",
  "max_iterations": 20,
  "timeout": 60000,
  "retry_count": 3,
  "option_count": 3,
  "templates": {
    "A-1": "capacity_options",
    "B-1": "gonogo_options",
    "C-1": "headcount_options",
    "D-1": "competency_options"
  }
}
```

## 연계 에이전트

| Agent | 연계 목적 |
|-------|----------|
| query-decomposition | 분해된 질문 수신 |
| impact-simulator | 각 옵션 영향 시뮬레이션 |
| success-probability | 성공확률 산출 |

## 사용 예시

```python
# 에이전트 호출 예시
result = await call_agent("option-generator", {
    "query": decomposed_query,
    "context": {
        "project_name": "신규 DX 프로젝트",
        "required_skills": ["Cloud", "DevOps"]
    }
})
```
