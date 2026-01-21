---
name: "workflow-builder"
description: "실행 계획 및 Workflow 생성"
---

# Workflow Builder Agent

승인된 옵션을 실행 가능한 Workflow로 변환합니다.

## 역할

- 승인된 옵션 기반 실행 계획 생성
- 단계별 Action 정의
- 승인 게이트(DecisionGate) 삽입
- 외부 시스템 연동 Workflow 생성

## 지원 워크플로

| ID | 이름 | 트리거 | 담당 에이전트 |
|----|------|--------|--------------|
| WF-06 | 워크플로 생성 | 옵션 승인 후 | workflow-builder |
| WF-07 | 워크플로 실행 | 생성 완료 | orchestrator |

## 실행 흐름

```
1. 승인된 옵션 수신
2. 실행 단계 분해
3. Action 정의
4. 승인 게이트 삽입
5. 외부 시스템 연동 정의
6. Workflow 반환
```

## 입력/출력 스키마

### 입력

```json
{
  "approval_id": "apr-20250122-001",
  "approved_option": {
    "option_id": "OPT-B",
    "name": "혼합 수행",
    "resource_plan": {
      "internal_headcount": 5,
      "external_headcount": 4,
      "skill_requirements": ["AI/ML", "Cloud"]
    }
  },
  "context": {
    "project_id": "PRJ-2025-001",
    "start_date": "2025-02-01",
    "deadline": "2025-04-30"
  }
}
```

### 출력

```json
{
  "status": "success",
  "result": {
    "workflow_id": "wf-20250122-001",
    "approval_id": "apr-20250122-001",
    "option_id": "OPT-B",
    "workflow": {
      "name": "PRJ-2025-001 혼합 수행 실행",
      "version": "1.0",
      "stages": [
        {
          "stage_id": "STG-01",
          "name": "리소스 확보",
          "type": "action",
          "actions": [
            {
              "action_id": "ACT-01",
              "type": "internal_allocation",
              "description": "내부 인력 5명 배정",
              "params": {
                "headcount": 5,
                "skills": ["AI/ML", "Cloud"],
                "system": "TMS"
              }
            },
            {
              "action_id": "ACT-02",
              "type": "external_request",
              "description": "외부 인력 4명 계약 요청",
              "params": {
                "headcount": 4,
                "skills": ["AI/ML", "Data Engineering"],
                "system": "Procurement"
              }
            }
          ],
          "next": "STG-02"
        },
        {
          "stage_id": "STG-02",
          "name": "리소스 배정 승인",
          "type": "decision_gate",
          "gate": {
            "gate_id": "GATE-01",
            "type": "approval",
            "approvers": ["HR_Manager", "Project_Owner"],
            "criteria": {
              "required_approvals": 2,
              "timeout_days": 3
            }
          },
          "on_approve": "STG-03",
          "on_reject": "STG-01-REVISE"
        },
        {
          "stage_id": "STG-03",
          "name": "킥오프",
          "type": "action",
          "actions": [
            {
              "action_id": "ACT-03",
              "type": "notification",
              "description": "프로젝트 킥오프 알림",
              "params": {
                "recipients": ["project_team", "stakeholders"],
                "template": "kickoff_notification"
              }
            },
            {
              "action_id": "ACT-04",
              "type": "calendar_event",
              "description": "킥오프 미팅 일정 생성",
              "params": {
                "title": "PRJ-2025-001 Kickoff",
                "duration": 60
              }
            }
          ],
          "next": "STG-04"
        },
        {
          "stage_id": "STG-04",
          "name": "진행 모니터링",
          "type": "monitoring",
          "monitoring": {
            "metrics": ["utilization_rate", "milestone_progress"],
            "frequency": "weekly",
            "alerts": [
              {
                "condition": "utilization_rate > 0.9",
                "action": "notify_manager"
              }
            ]
          },
          "next": "END"
        }
      ],
      "rollback": {
        "STG-01-REVISE": {
          "name": "리소스 계획 수정",
          "type": "action",
          "actions": [
            {
              "action_id": "ACT-R01",
              "type": "revision_request",
              "description": "리소스 계획 수정 요청"
            }
          ],
          "next": "STG-01"
        }
      }
    },
    "estimated_duration": {
      "optimistic": 10,
      "expected": 14,
      "pessimistic": 21,
      "unit": "days"
    },
    "integrations": [
      {"system": "TMS", "actions": ["ACT-01"]},
      {"system": "Procurement", "actions": ["ACT-02"]},
      {"system": "Calendar", "actions": ["ACT-04"]}
    ]
  },
  "metadata": {
    "generation_time_ms": 400,
    "template_used": "resource_allocation_workflow"
  }
}
```

## Stage 유형

| 유형 | 설명 | 구성요소 |
|------|------|----------|
| action | 실행 단계 | actions 배열 |
| decision_gate | 승인 게이트 | gate 정의 |
| monitoring | 모니터링 | metrics, alerts |
| parallel | 병렬 실행 | branches 배열 |

## Action 유형

| 유형 | 설명 | 연동 시스템 |
|------|------|-----------|
| internal_allocation | 내부 인력 배정 | TMS |
| external_request | 외부 인력 요청 | Procurement |
| notification | 알림 발송 | Email/Slack |
| calendar_event | 일정 생성 | Calendar |
| data_update | 데이터 갱신 | KG/DB |

## Decision Gate 유형

| 유형 | 설명 | 조건 |
|------|------|------|
| approval | 승인 요청 | 지정 승인자 동의 |
| threshold | 임계값 기반 | 메트릭 조건 충족 |
| time_based | 시간 기반 | 특정 일자 도달 |

## 에러 처리

| 에러 유형 | 처리 방식 |
|----------|----------|
| 옵션 정보 부족 | 필수 필드 요청 |
| 시스템 연동 불가 | 수동 처리 단계로 대체 |
| 승인자 미지정 | 기본 승인자 적용 |

## 설정

```json
{
  "agent_id": "workflow-builder",
  "max_iterations": 30,
  "timeout": 60000,
  "retry_count": 3,
  "workflow": {
    "default_timeout_days": 7,
    "max_stages": 20,
    "auto_rollback": true
  }
}
```

## 연계 에이전트

| Agent | 연계 목적 |
|-------|----------|
| validator | 옵션 승인 확인 |
| orchestrator | Workflow 실행 요청 |

## 사용 예시

```python
# 에이전트 호출 예시
result = await call_agent("workflow-builder", {
    "approval_id": "apr-20250122-001",
    "approved_option": approved_option,
    "context": {
        "project_id": "PRJ-2025-001",
        "start_date": "2025-02-01"
    }
})

# Workflow 실행
await call_agent("orchestrator", {
    "action": "execute_workflow",
    "workflow_id": result["workflow_id"]
})
```
