# HR 의사결정 지원 시스템 - KPI & Acceptance Criteria v1

> 작성일: 2025-01-22 | 버전: 1.0

---

## 1. 개요

이 문서는 PoC의 성공 여부를 판단하는 KPI와 Acceptance Criteria를 정의합니다.

---

## 2. Acceptance Criteria (수용 기준)

### 2.1 필수 수용 기준 (Must-Have)

PoC 성공을 위해 **반드시** 달성해야 하는 기준입니다.

| ID | 기준 | 측정 방법 | 목표 | 판정 |
|----|------|----------|------|------|
| **AC-1** | 4대 유스케이스 응답 | A-1, B-1, C-1, D-1 질문에 구조화된 응답 생성 | 4/4 (100%) | Pass/Fail |
| **AC-2** | 3안 비교 생성 | 각 질문에 대해 3개 Option 생성 및 비교 | 100% | Pass/Fail |
| **AC-3** | 근거 연결률 | 모든 주장에 Evidence 연결 | ≥ 95% | Pass/Fail |
| **AC-4** | 환각률 | 근거 없는 주장 비율 | ≤ 5% | Pass/Fail |
| **AC-5** | KG 엔터티 커버리지 | 28개 필수 노드 타입 모두 존재 | 100% | Pass/Fail |
| **AC-6** | HITL 워크플로 | 승인 → 실행 플로우 동작 | 동작 | Pass/Fail |

### 2.2 권장 수용 기준 (Should-Have)

달성 시 PoC 품질을 높이는 기준입니다.

| ID | 기준 | 측정 방법 | 목표 | 현재 |
|----|------|----------|------|------|
| **AC-7** | 응답 시간 | 질문 입력 → 응답 완료 | ≤ 30초 | - |
| **AC-8** | 재현성 | 동일 입력 시 동일 결과 비율 | ≥ 95% | - |
| **AC-9** | UI 사용성 | 사용자 테스트 완료율 | ≥ 80% | - |
| **AC-10** | 문서화 | API 문서 + 사용자 가이드 완성 | 100% | - |

---

## 3. KPI (핵심 성과 지표)

### 3.1 Agent 성능 KPI

| KPI | 설명 | 측정 방법 | 목표 | 우선순위 |
|-----|------|----------|------|----------|
| **완결성** | 질문에 대한 답변 완성도 | 필수 출력 항목 충족률 | > 90% | P0 |
| **정확성** | 수치/사실 정확도 | 검증 데이터 대비 정확률 | > 85% | P0 |
| **근거 연결률** | 주장에 Evidence 연결 비율 | 연결된 주장 / 전체 주장 | > 95% | P0 |
| **환각률** | 근거 없는 주장 비율 | 근거 없는 주장 / 전체 주장 | < 5% | P0 |
| **재현성** | 동일 입력 시 동일 결과 | 일관성 테스트 통과율 | > 95% | P1 |
| **응답 시간** | 답변 생성 시간 | 평균 응답 시간 | < 30s | P1 |

### 3.2 Ontology/KG KPI

| KPI | 설명 | 측정 방법 | 목표 | 우선순위 |
|-----|------|----------|------|----------|
| **엔터티 커버리지** | 필수 노드 타입 존재 비율 | 존재 노드 타입 / 28 | 100% | P0 |
| **인스턴스 밀도** | 노드당 평균 인스턴스 수 | 총 인스턴스 / 노드 타입 수 | > 10 | P1 |
| **링크율** | 고아 노드 없는 비율 | (전체-고아) / 전체 | > 95% | P0 |
| **중복/충돌** | 키 충돌 비율 | 충돌 건 / 전체 | 0% | P0 |
| **최신성** | 데이터 갱신 주기 준수 | 최신 데이터 비율 | > 90% | P1 |
| **쿼리 성능** | 평균 쿼리 응답 시간 | ms | < 500ms | P1 |

### 3.3 Data Quality KPI

| KPI | 설명 | 측정 방법 | 목표 | 우선순위 |
|-----|------|----------|------|----------|
| **결측률** | 필수 필드 결측 비율 | 결측 값 / 전체 | < 10% | P0 |
| **중복률** | 키 중복 비율 | 중복 키 / 전체 | < 1% | P0 |
| **키 매칭률** | Join Key 연결 성공률 | 매칭 성공 / 전체 | > 95% | P0 |
| **필수필드 충족률** | 질문별 Required Fields 충족 | 충족 필드 / 필요 필드 | > 80% | P0 |
| **형식 일관성** | 데이터 형식 표준 준수율 | 준수 건 / 전체 | > 95% | P1 |

### 3.4 비즈니스 KPI

| KPI | 설명 | 측정 방법 | 목표 | 우선순위 |
|-----|------|----------|------|----------|
| **의사결정 시간 단축** | 기존 대비 시간 절감 | 기존 시간 - PoC 시간 | > 50% | P1 |
| **분석 단계 절감** | 수동 분석 단계 감소 | 기존 단계 - PoC 단계 | > 3단계 | P1 |
| **데이터 활용률** | 연결 데이터 소스 수 | 연결된 소스 / 전체 소스 | > 80% | P2 |

---

## 4. 측정 방법

### 4.1 Agent 평가 방법

```python
# Agent 평가 스크립트 예시
def evaluate_agent_response(response, ground_truth):
    metrics = {
        "completeness": calculate_completeness(response),
        "accuracy": calculate_accuracy(response, ground_truth),
        "evidence_coverage": calculate_evidence_coverage(response),
        "hallucination_rate": calculate_hallucination_rate(response),
    }
    return metrics
```

| 지표 | 계산 방식 |
|------|----------|
| 완결성 | 필수 출력 항목 체크리스트 기반 |
| 정확성 | Ground Truth 대비 오차율 |
| 근거 연결률 | `len(evidenced_claims) / len(all_claims)` |
| 환각률 | `len(unevidenced_claims) / len(all_claims)` |

### 4.2 Ontology/KG 평가 쿼리

```cypher
// 엔터티 커버리지
CALL db.labels() YIELD label
RETURN count(label) as nodeTypeCount

// 링크율 (고아 노드)
MATCH (n)
WHERE NOT (n)--()
RETURN count(n) as orphanCount

// 중복 체크
MATCH (n)
WITH n.id as id, count(*) as cnt
WHERE cnt > 1
RETURN count(id) as duplicateCount
```

### 4.3 Data Quality 평가

```python
def evaluate_data_quality(dataset):
    return {
        "missing_rate": dataset.isnull().sum() / len(dataset),
        "duplicate_rate": dataset.duplicated().sum() / len(dataset),
        "key_match_rate": calculate_key_matching(dataset),
        "required_field_rate": check_required_fields(dataset),
    }
```

---

## 5. 평가 일정

| 평가 시점 | 대상 | 평가 항목 |
|----------|------|----------|
| Day 2 (1/23) | Data | Data Quality KPI |
| Day 3 (1/24) | KG | Ontology KPI |
| Day 4 (1/27) | Agent | Agent 성능 KPI (부분) |
| Day 5 (1/28) | 전체 | 전체 KPI 통합 평가 |
| Day 7 (1/30) | 전체 | 최종 Acceptance 판정 |

---

## 6. 보고 템플릿

### 6.1 일일 KPI 리포트

```markdown
## Daily KPI Report - Day X (YYYY-MM-DD)

### Agent 성능
| KPI | 목표 | 현재 | 상태 |
|-----|------|------|------|
| 완결성 | >90% | XX% | 🟢/🟡/🔴 |
| 근거 연결률 | >95% | XX% | 🟢/🟡/🔴 |

### Ontology/KG
| KPI | 목표 | 현재 | 상태 |
|-----|------|------|------|
| 엔터티 커버리지 | 100% | XX% | 🟢/🟡/🔴 |

### 이슈 및 액션
- [ ] 이슈 1: ...
- [ ] 액션 1: ...
```

### 6.2 최종 Acceptance 판정

```markdown
## PoC Acceptance Report - YYYY-MM-DD

### 필수 수용 기준 (Must-Have)
| ID | 기준 | 목표 | 결과 | 판정 |
|----|------|------|------|------|
| AC-1 | 4대 유스케이스 응답 | 100% | X% | ✅/❌ |
...

### 종합 판정
- [ ] PASS: 필수 기준 모두 충족
- [ ] CONDITIONAL: 일부 미충족, 조건부 승인
- [ ] FAIL: 핵심 기준 미충족
```

---

## 7. 리스크 기반 우선순위

### 7.1 KPI 미달 시 대응

| KPI | 미달 시 영향 | 대응 방안 |
|-----|-------------|----------|
| 근거 연결률 < 95% | 신뢰도 하락 | Validator 로직 강화 |
| 환각률 > 5% | 품질 이슈 | 프롬프트 개선, 검증 단계 추가 |
| KG 커버리지 < 100% | 기능 제한 | 누락 노드 타입 추가 |
| 응답 시간 > 30s | 사용성 저하 | 캐싱, 쿼리 최적화 |

---

## 8. 버전 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2025-01-22 | 초기 버전 작성 |

---

*이 문서는 PoC 진행 중 KPI 기준이 조정될 수 있습니다.*
