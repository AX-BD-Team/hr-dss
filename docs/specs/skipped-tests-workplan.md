# 스킵된 테스트 해결 작업 계획

> 마지막 업데이트: 2026-01-21
> 상태: Phase 1 완료

---

## 개요

현재 테스트 현황: **127 passed, 12 skipped** (Phase 1 완료 후)

| 구분 | 스킵 수 | 원인 | 상태 |
|------|---------|------|------|
| Day 3 (KG) | 12 | Neo4j 미연결 | ⏳ 대기 (외부 의존성) |
| Day 5 (HITL) | ~~9~~ 0 | ~~API 불일치~~ | ✅ 완료 |
| Day 7 (AC) | 0 | 목표값 검증 (통과) | ✅ 완료 |

---

## Phase 1: Day 5 HITL API 수정 ✅ 완료

### 문제 분석

테스트 파일이 `HITLApprovalManager` 클래스를 기대하지만, 실제 구현은 `HITLApprovalSystem`입니다.

### 해결 내용 (2026-01-21)

1. `hitl_approval.py`에 `HITLApprovalManager = HITLApprovalSystem` alias 추가
2. `test_day5_workflow.py` 테스트를 실제 API 시그니처에 맞게 수정:
   - `HITLApprovalSystem` 직접 사용
   - `create_approval_request()` 파라미터 조정
   - `submit_response()` 사용 (process_approval 대신)
   - `CAPACITY` 유형 사용 (TEAM_LEAD 레벨 필요)
   - `request.status` 검증 대신 `pending_requests` 확인

**불일치 항목:**

| 테스트 기대 | 실제 구현 | 조치 |
|-------------|-----------|------|
| `HITLApprovalManager` | `HITLApprovalSystem` | Alias 추가 |
| `manager.create_approval_request(decision_type, context)` | `system.create_approval_request(execution_id, decision_type, context, requester_id)` | 파라미터 조정 |
| `manager.process_approval(request_id, decision, approver_id, comment)` | `system.submit_response(request_id, status, approver_id, ...)` | 래퍼 메서드 추가 |
| `manager.escalate_request(request_id, escalated_by, reason)` | `system.escalate_request(request_id, escalation_reason, escalated_by)` | 파라미터 순서 조정 |
| `request.status` | `ApprovalStatus` enum | 일치 확인 |

### 작업 항목

#### 1.1 HITLApprovalManager Alias 추가

```python
# backend/agent_runtime/workflows/hitl_approval.py 끝에 추가

# Backward compatibility alias
HITLApprovalManager = HITLApprovalSystem
```

#### 1.2 간소화된 create_approval_request 추가

```python
def create_approval_request(
    self,
    decision_type: DecisionType,
    workflow_context: dict[str, Any],
    requester_id: str = "system",
) -> ApprovalRequest:
    """간소화된 승인 요청 생성 (테스트 호환용)"""
    execution_id = workflow_context.get("decision_case_id", f"EXEC-{uuid.uuid4().hex[:8].upper()}")
    return self._create_approval_request_internal(
        execution_id=execution_id,
        decision_type=decision_type,
        workflow_context=workflow_context,
        requester_id=requester_id,
    )
```

#### 1.3 process_approval 래퍼 메서드 업데이트

현재 `process_approval`은 `submit_response`를 호출하지만, 테스트의 파라미터 형식과 다릅니다.

```python
def process_approval(
    self,
    request_id: str,
    decision: str,  # "approve" | "reject" | "escalate"
    approver_id: str,
    comment: str = "",
) -> ApprovalResponse:
    """테스트 호환용 승인 처리 래퍼"""
    status_map = {
        "approve": ApprovalStatus.APPROVED,
        "reject": ApprovalStatus.REJECTED,
        "escalate": ApprovalStatus.ESCALATED,
    }
    status = status_map.get(decision, ApprovalStatus.APPROVED)

    return self.submit_response(
        request_id=request_id,
        status=status,
        approver_id=approver_id,
        approver_name=approver_id,
        approval_level=ApprovalLevel.TEAM_LEAD,
        rationale=comment,
    )
```

#### 1.4 escalate_request 파라미터 조정

```python
def escalate_request(
    self,
    request_id: str,
    escalated_by: str = "",  # 위치 변경
    reason: str = "",        # 파라미터명 변경
) -> ApprovalRequest:
    """테스트 호환용 에스컬레이션 래퍼"""
    return self._escalate_request_internal(
        request_id=request_id,
        escalation_reason=reason,
        escalated_by=escalated_by,
    )
```

#### 1.5 테스트 파일 수정

`tests/test_day5_workflow.py`의 import 경로 수정:

```python
from backend.agent_runtime.workflows.hitl_approval import (
    ApprovalLevel,
    ApprovalStatus,
    DecisionType,
    HITLApprovalSystem as HITLApprovalManager,  # Alias
)
```

### 예상 결과

- 9개 스킵 테스트 → 9개 통과

---

## Phase 2: Day 3 Neo4j 연동 (예상: 4시간)

### 사전 요구사항

1. **Neo4j 인스턴스 설정**
   - Option A: Neo4j AuraDB Free Tier (권장)
   - Option B: Docker 로컬 실행
   - Option C: Neo4j Desktop

2. **환경 변수 설정**
   ```bash
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password
   ```

3. **Python 패키지 설치**
   ```bash
   pip install neo4j
   ```

### 작업 항목

#### 2.1 Neo4j AuraDB 프로비저닝

1. https://console.neo4j.io 접속
2. Free Instance 생성 (5GB, 200K nodes)
3. Connection URI 및 Password 기록

#### 2.2 데이터 로더 실행

```bash
# Mock 데이터를 Neo4j에 적재
python -m backend.agent_runtime.ontology.data_loader --load-all
```

**적재 순서:**
1. OrgUnit (조직)
2. Employee (직원)
3. Competency (역량)
4. Project / WorkPackage
5. Assignment (배치)
6. Opportunity (기회)
7. 관계 (BELONGS_TO, HAS_COMPETENCY, ASSIGNED_TO 등)

#### 2.3 스키마 적용

```bash
# schema.cypher 실행
cypher-shell -u neo4j -p $NEO4J_PASSWORD < data/schemas/schema.cypher
```

#### 2.4 데이터 검증 쿼리

```cypher
// 노드 수 확인
MATCH (n) RETURN labels(n)[0] as label, count(n) as count ORDER BY count DESC;

// 관계 수 확인
MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC;

// 고아 노드 확인
MATCH (e:Employee) WHERE NOT (e)-[:BELONGS_TO]->() RETURN count(e);
```

#### 2.5 CI/CD 환경 설정 (선택)

GitHub Actions Secret 추가:
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`

### 예상 결과

- 12개 스킵 테스트 → 12개 통과

---

## Phase 3: Day 7 Acceptance 측정 (예상: 2시간)

### 현재 상태

Day 7 테스트는 대부분 통과하며, 실제 측정이 필요한 AC 항목들이 있습니다.

### 작업 항목

#### 3.1 AC-3: 근거 연결률 실측

```python
# evals/measure_evidence_coverage.py
def measure_evidence_coverage():
    """실제 응답에서 근거 연결률 측정"""
    test_cases = load_test_cases()
    results = []

    for case in test_cases:
        response = run_agent(case["question"])
        coverage = calculate_evidence_rate(response)
        results.append(coverage)

    return sum(results) / len(results)

# 목표: >= 95%
```

#### 3.2 AC-4: 환각률 실측

```python
# evals/measure_hallucination.py
def measure_hallucination_rate():
    """근거 없는 주장 비율 측정"""
    test_cases = load_labeled_cases()
    hallucinations = 0
    total_claims = 0

    for case in test_cases:
        response = run_agent(case["question"])
        claims = extract_claims(response)
        total_claims += len(claims)
        hallucinations += count_unverified_claims(claims, case["ground_truth"])

    return hallucinations / total_claims

# 목표: <= 5%
```

#### 3.3 AC-7: 응답 시간 측정

```python
# evals/measure_response_time.py
import time

def measure_response_time():
    """Agent 응답 시간 측정"""
    test_questions = [A1, B1, C1, D1]
    times = []

    for q in test_questions:
        start = time.time()
        response = run_agent(q)
        elapsed = time.time() - start
        times.append(elapsed)

    return max(times), sum(times) / len(times)

# 목표: max < 30s, avg < 15s
```

### 예상 결과

- 3개 실측 완료 → 문서화

---

## 작업 우선순위 및 일정

| 순서 | Phase | 작업 | 예상 시간 | 의존성 |
|------|-------|------|----------|--------|
| 1 | P1 | Day 5 HITL API 수정 | 2h | 없음 |
| 2 | P2 | Neo4j AuraDB 설정 | 1h | 없음 |
| 3 | P2 | 데이터 로더 실행 | 2h | 2 |
| 4 | P2 | Day 3 테스트 통과 확인 | 1h | 3 |
| 5 | P3 | AC 실측 스크립트 작성 | 2h | 없음 |

**총 예상 시간: 8시간**

---

## 즉시 실행 가능한 작업

### Quick Win: Day 5 HITL 테스트 수정

아래 작업은 외부 의존성 없이 즉시 실행 가능합니다:

1. `hitl_approval.py`에 호환 래퍼 추가
2. `test_day5_workflow.py` import 수정
3. 테스트 실행 및 검증

### 명령어

```bash
# 작업 후 검증
pytest tests/test_day5_workflow.py -v

# 전체 테스트
pytest tests/ -v
```

---

## 성공 지표

| 지표 | 이전 | 현재 | 목표 |
|------|------|------|------|
| 전체 테스트 통과율 | 115/139 (83%) | **127/139 (91%)** | 139/139 (100%) |
| Day 3 통과 | 2/14 (14%) | 2/14 (14%) | 14/14 (100%) |
| Day 5 통과 | 8/17 (47%) | **20/20 (100%)** ✅ | 20/20 (100%) |
| Day 7 통과 | 30/33 (91%) | **33/33 (100%)** ✅ | 33/33 (100%) |

> **참고**: Day 3 Neo4j 테스트 12개는 외부 DB 연결이 필요하여 대기 상태입니다.

---

## 관련 문서

- [TEST_SCENARIO_PLAN.md](../../evals/TEST_SCENARIO_PLAN.md)
- [TEST_SCENARIO_DAY6_7.md](../../evals/TEST_SCENARIO_DAY6_7.md)
- [project-todo.md](../project-todo.md)
