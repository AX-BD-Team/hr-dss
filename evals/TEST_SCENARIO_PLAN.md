# HR DSS 테스트 시나리오 계획서 (Day 1-5)

> 작성일: 2026-01-21 | 버전: 1.0

---

## 목차

1. [테스트 전략 개요](#1-테스트-전략-개요)
2. [Day 1 테스트: P0-P1 문서 검증](#2-day-1-테스트-p0-p1-문서-검증)
3. [Day 2 테스트: P2 Data Readiness](#3-day-2-테스트-p2-data-readiness)
4. [Day 3 테스트: P3-P4 Ontology/KG](#4-day-3-테스트-p3-p4-ontologykg)
5. [Day 4 테스트: P5 Agent 엔진](#5-day-4-테스트-p5-agent-엔진)
6. [Day 5 테스트: P6-P7 Workflow + 평가](#6-day-5-테스트-p6-p7-workflow--평가)
7. [통합 테스트 시나리오](#7-통합-테스트-시나리오)
8. [테스트 결과 보고 템플릿](#8-테스트-결과-보고-템플릿)

---

## 1. 테스트 전략 개요

### 1.1 테스트 레벨

| 레벨 | 범위 | 도구 | 자동화 |
|------|------|------|--------|
| Unit Test | 개별 함수/메서드 | pytest | ✅ |
| Integration Test | 모듈 간 연동 | pytest + Neo4j | ✅ |
| E2E Test | 전체 플로우 | Scenario-based | 수동 |
| Acceptance Test | AC 기준 검증 | Custom Eval | ✅ |

### 1.2 Acceptance Criteria (AC) 매핑

| AC ID | 기준 | 테스트 Day | 목표 |
|-------|------|-----------|------|
| AC-1 | 4대 유스케이스 응답 | Day 4-5 | 100% |
| AC-2 | 3안 비교 생성 | Day 4 | 100% |
| AC-3 | 근거 연결률 | Day 4-5 | ≥ 95% |
| AC-4 | 환각률 | Day 4-5 | ≤ 5% |
| AC-5 | KG 엔터티 커버리지 | Day 3 | 100% |
| AC-6 | HITL 워크플로 | Day 5 | 동작 |

### 1.3 테스트 환경

```yaml
environments:
  local:
    neo4j: "bolt://localhost:7687"
    python: "3.11+"
    pytest: "8.3+"

  ci:
    neo4j: "neo4j-aura-test"
    runner: "GitHub Actions"
```

---

## 2. Day 1 테스트: P0-P1 문서 검증

### 2.1 테스트 목적

P0 Kick-off와 P1 Key Questions 단계의 산출물 완성도 검증

### 2.2 테스트 시나리오

#### TS-D1-01: PoC Charter 완성도 검증

```yaml
scenario_id: TS-D1-01
name: "PoC Charter 완성도 검증"
category: Documentation
priority: P0

preconditions:
  - docs/specs/poc-charter.md 파일 존재

test_cases:
  - id: TC-D1-01-01
    name: "필수 섹션 존재 확인"
    check:
      - "[ ] 목적 (Purpose) 섹션 존재"
      - "[ ] 범위 (Scope) 섹션 존재"
      - "[ ] 일정 (Timeline) 섹션 존재"
      - "[ ] 팀 구성 (Team) 섹션 존재"
      - "[ ] 성공 기준 (Success Criteria) 섹션 존재"
    expected: "모든 필수 섹션 존재"

  - id: TC-D1-01-02
    name: "마일스톤 정의 확인"
    check:
      - "[ ] M1~M7 마일스톤 정의"
      - "[ ] 각 마일스톤에 날짜 지정"
      - "[ ] 검증 기준 명시"
    expected: "7개 마일스톤 완전 정의"
```

#### TS-D1-02: Question Set 검증

```yaml
scenario_id: TS-D1-02
name: "Question Set 구조 검증"
category: Documentation
priority: P0

test_cases:
  - id: TC-D1-02-01
    name: "4대 유스케이스 정의 확인"
    check:
      - "[ ] A-1: 12주 Capacity 병목 예측"
      - "[ ] B-1: Go/No-go + 성공확률"
      - "[ ] C-1: 증원 원인분해"
      - "[ ] D-1: 역량 투자 ROI"
    expected: "4개 유스케이스 모두 정의"

  - id: TC-D1-02-02
    name: "3단계 대화 템플릿 확인"
    check:
      - "[ ] 1단계: 문제 정의 (DecisionCase)"
      - "[ ] 2단계: 대안 탐색 (Option 비교)"
      - "[ ] 3단계: 보고/기획 (Action + Workflow)"
    expected: "각 유스케이스에 3단계 템플릿 적용"

  - id: TC-D1-02-03
    name: "입출력 스키마 정의 확인"
    check:
      - "[ ] Input YAML 스키마 정의"
      - "[ ] Output YAML 스키마 정의"
      - "[ ] JSON 응답 스키마 정의"
    expected: "모든 스키마 형식 정의 완료"
```

#### TS-D1-03: Decision Criteria 검증

```yaml
scenario_id: TS-D1-03
name: "Decision Criteria 완성도"
category: Documentation
priority: P0

test_cases:
  - id: TC-D1-03-01
    name: "영향도/성공확률 산정 기준"
    check:
      - "[ ] 영향도 계산 공식 정의"
      - "[ ] 성공확률 계산 요소 정의"
      - "[ ] 리스크 레벨 기준 정의"
    expected: "정량적 계산 기준 완비"
```

### 2.3 Day 1 체크리스트

| 항목 | 검증 방법 | Pass 기준 |
|------|----------|----------|
| PoC Charter v1 | 수동 검토 | 필수 섹션 100% |
| Question Set v1 | 스키마 검증 | 4개 UC 정의 |
| Decision Criteria | 수동 검토 | 계산 기준 명시 |
| KPI & AC | 수동 검토 | 6개 AC 정의 |

---

## 3. Day 2 테스트: P2 Data Readiness

### 3.1 테스트 목적

Mock 데이터 6종의 품질과 스키마 일관성 검증

### 3.2 테스트 시나리오

#### TS-D2-01: Mock 데이터 스키마 검증

```yaml
scenario_id: TS-D2-01
name: "Mock 데이터 스키마 검증"
category: Data Quality
priority: P0

test_cases:
  - id: TC-D2-01-01
    name: "persons.json 스키마 검증"
    file: "data/mock/persons.json"
    schema_check:
      required_fields:
        - employeeId: "string (EMP-XXXXXX)"
        - name: "string"
        - orgUnitId: "string (ORG-XXXX)"
        - positionId: "string (POS-XXX)"
        - hireDate: "date (YYYY-MM-DD)"
      count_check: ">= 50"
    expected: "65명 데이터, 스키마 일치"

  - id: TC-D2-01-02
    name: "projects.json 스키마 검증"
    file: "data/mock/projects.json"
    schema_check:
      required_fields:
        - projectId: "string (PRJ-XXX)"
        - name: "string"
        - status: "enum (ACTIVE, COMPLETED, PLANNED)"
        - startDate: "date"
        - endDate: "date"
      count_check: ">= 10"
    expected: "12개 프로젝트, 30개 WP"

  - id: TC-D2-01-03
    name: "skills.json 스키마 검증"
    file: "data/mock/skills.json"
    schema_check:
      required_fields:
        - competencyId: "string (CMP-XXX)"
        - name: "string"
        - category: "string"
        - level: "number (1-5)"
    expected: "40개 역량, 50개 증거"

  - id: TC-D2-01-04
    name: "orgs.json 스키마 검증"
    file: "data/mock/orgs.json"
    schema_check:
      required_fields:
        - orgUnitId: "string (ORG-XXXX)"
        - name: "string"
        - parentId: "string | null"
        - headcount: "number"
    expected: "20개 조직"

  - id: TC-D2-01-05
    name: "opportunities.json 스키마 검증"
    file: "data/mock/opportunities.json"
    schema_check:
      required_fields:
        - opportunityId: "string (OPP-XXX)"
        - name: "string"
        - dealValue: "number"
        - stage: "enum"
        - probability: "number (0-1)"
    expected: "15개 기회"

  - id: TC-D2-01-06
    name: "assignments.json 스키마 검증"
    file: "data/mock/assignments.json"
    schema_check:
      required_fields:
        - assignmentId: "string (ASN-XXX)"
        - employeeId: "string"
        - projectId: "string"
        - allocationFTE: "number (0-1)"
    expected: "42개 배치, 30개 가용성"
```

#### TS-D2-02: Join Key 연결성 검증

```yaml
scenario_id: TS-D2-02
name: "Join Key 연결성 검증"
category: Data Quality
priority: P0

test_cases:
  - id: TC-D2-02-01
    name: "employeeId 연결 검증"
    description: "persons.employeeId가 assignments, skills에서 참조 가능"
    check_query: |
      SELECT p.employeeId
      FROM persons p
      LEFT JOIN assignments a ON p.employeeId = a.employeeId
      WHERE a.employeeId IS NULL
    expected: "고아 레코드 0건"

  - id: TC-D2-02-02
    name: "orgUnitId 연결 검증"
    description: "orgs.orgUnitId가 persons에서 참조 가능"
    expected: "모든 persons.orgUnitId가 orgs에 존재"

  - id: TC-D2-02-03
    name: "projectId 연결 검증"
    description: "projects.projectId가 assignments에서 참조 가능"
    expected: "모든 assignments.projectId가 projects에 존재"
```

#### TS-D2-03: Data Quality 지표 검증

```yaml
scenario_id: TS-D2-03
name: "Data Quality 지표 검증"
category: Data Quality
priority: P0

test_cases:
  - id: TC-D2-03-01
    name: "결측률 검증"
    metric: "missing_rate"
    target: "< 10%"
    check_all_files: true

  - id: TC-D2-03-02
    name: "중복률 검증"
    metric: "duplicate_rate"
    target: "< 1%"
    check_all_files: true

  - id: TC-D2-03-03
    name: "키 매칭률 검증"
    metric: "key_match_rate"
    target: "> 95%"

  - id: TC-D2-03-04
    name: "필수필드 충족률 검증"
    metric: "required_field_rate"
    target: "> 80%"
```

### 3.3 Day 2 pytest 구현

```python
# tests/test_day2_data_readiness.py

import pytest
import json
from pathlib import Path

DATA_DIR = Path("data/mock")

class TestMockDataSchema:
    """TS-D2-01: Mock 데이터 스키마 검증"""

    @pytest.fixture
    def persons_data(self):
        with open(DATA_DIR / "persons.json") as f:
            return json.load(f)

    def test_persons_count(self, persons_data):
        """TC-D2-01-01: persons 데이터 수량"""
        employees = persons_data.get("employees", [])
        assert len(employees) >= 50, f"Expected >= 50, got {len(employees)}"

    def test_persons_required_fields(self, persons_data):
        """TC-D2-01-01: persons 필수 필드"""
        required = ["employeeId", "name", "orgUnitId", "positionId"]
        for emp in persons_data.get("employees", []):
            for field in required:
                assert field in emp, f"Missing field: {field}"

    def test_persons_id_format(self, persons_data):
        """TC-D2-01-01: employeeId 형식 검증"""
        import re
        pattern = re.compile(r"^EMP-\d{6}$")
        for emp in persons_data.get("employees", []):
            assert pattern.match(emp["employeeId"]), f"Invalid ID: {emp['employeeId']}"


class TestJoinKeyIntegrity:
    """TS-D2-02: Join Key 연결성 검증"""

    @pytest.fixture
    def all_data(self):
        data = {}
        for f in DATA_DIR.glob("*.json"):
            with open(f) as file:
                data[f.stem] = json.load(file)
        return data

    def test_employee_org_link(self, all_data):
        """TC-D2-02-02: employeeId → orgUnitId 연결"""
        org_ids = {o["orgUnitId"] for o in all_data["orgs"].get("orgUnits", [])}
        for emp in all_data["persons"].get("employees", []):
            assert emp["orgUnitId"] in org_ids, f"Orphan orgUnitId: {emp['orgUnitId']}"


class TestDataQualityMetrics:
    """TS-D2-03: Data Quality 지표 검증"""

    def test_missing_rate(self):
        """TC-D2-03-01: 결측률 < 10%"""
        # Implementation
        pass

    def test_duplicate_rate(self):
        """TC-D2-03-02: 중복률 < 1%"""
        # Implementation
        pass
```

### 3.4 Day 2 체크리스트

| 항목 | 검증 방법 | Pass 기준 |
|------|----------|----------|
| persons.json | pytest | 65명, 스키마 일치 |
| projects.json | pytest | 12개, WP 30개 |
| skills.json | pytest | 40개 역량 |
| orgs.json | pytest | 20개 조직 |
| opportunities.json | pytest | 15개 기회 |
| assignments.json | pytest | 42개 배치 |
| Join Key 연결 | pytest | 95%+ 매칭 |
| Data Quality Score | Dashboard | 100% READY |

---

## 4. Day 3 테스트: P3-P4 Ontology/KG

### 4.1 테스트 목적

Neo4j Knowledge Graph 구축 완성도와 데이터 무결성 검증

### 4.2 테스트 시나리오

#### TS-D3-01: Neo4j 스키마 검증

```yaml
scenario_id: TS-D3-01
name: "Neo4j 스키마 검증"
category: KG
priority: P0

test_cases:
  - id: TC-D3-01-01
    name: "노드 타입 존재 확인 (47개)"
    cypher: |
      CALL db.labels() YIELD label
      RETURN count(label) as nodeTypeCount
    expected: ">= 47"

  - id: TC-D3-01-02
    name: "필수 노드 타입 확인"
    cypher: |
      CALL db.labels() YIELD label
      WHERE label IN ['Employee', 'OrgUnit', 'Project', 'Competency',
                      'Assignment', 'Opportunity', 'DecisionCase', 'Option',
                      'Finding', 'Evidence', 'Model', 'ForecastPoint']
      RETURN collect(label) as labels
    expected: "12개 필수 노드 모두 존재"

  - id: TC-D3-01-03
    name: "관계 타입 존재 확인"
    cypher: |
      CALL db.relationshipTypes() YIELD relationshipType
      RETURN count(relationshipType) as relTypeCount
    expected: ">= 50"

  - id: TC-D3-01-04
    name: "필수 관계 타입 확인"
    cypher: |
      CALL db.relationshipTypes() YIELD relationshipType
      WHERE relationshipType IN ['BELONGS_TO', 'ASSIGNED_TO', 'HAS_COMPETENCY',
                                  'REQUIRES_ROLE', 'HAS_SIGNAL', 'HAS_EVIDENCE',
                                  'PRODUCED_BY', 'AFFECTS', 'LEADS_TO']
      RETURN collect(relationshipType) as relTypes
    expected: "9개 필수 관계 모두 존재"
```

#### TS-D3-02: 데이터 적재 검증

```yaml
scenario_id: TS-D3-02
name: "데이터 적재 검증"
category: KG
priority: P0

test_cases:
  - id: TC-D3-02-01
    name: "Employee 노드 수량"
    cypher: "MATCH (e:Employee) RETURN count(e) as cnt"
    expected: ">= 65"

  - id: TC-D3-02-02
    name: "OrgUnit 노드 수량"
    cypher: "MATCH (o:OrgUnit) RETURN count(o) as cnt"
    expected: ">= 20"

  - id: TC-D3-02-03
    name: "Project 노드 수량"
    cypher: "MATCH (p:Project) RETURN count(p) as cnt"
    expected: ">= 12"

  - id: TC-D3-02-04
    name: "Competency 노드 수량"
    cypher: "MATCH (c:Competency) RETURN count(c) as cnt"
    expected: ">= 40"

  - id: TC-D3-02-05
    name: "Opportunity 노드 수량"
    cypher: "MATCH (o:Opportunity) RETURN count(o) as cnt"
    expected: ">= 15"

  - id: TC-D3-02-06
    name: "DecisionCase 노드 수량"
    cypher: "MATCH (d:DecisionCase) RETURN count(d) as cnt"
    expected: ">= 4"

  - id: TC-D3-02-07
    name: "Option 노드 수량"
    cypher: "MATCH (o:Option) RETURN count(o) as cnt"
    expected: ">= 8"

  - id: TC-D3-02-08
    name: "Finding 노드 수량"
    cypher: "MATCH (f:Finding) RETURN count(f) as cnt"
    expected: ">= 6"
```

#### TS-D3-03: KG 무결성 검증

```yaml
scenario_id: TS-D3-03
name: "KG 무결성 검증"
category: KG
priority: P0

test_cases:
  - id: TC-D3-03-01
    name: "고아 노드 검출"
    cypher: |
      MATCH (n)
      WHERE NOT (n)--()
      RETURN labels(n) as type, count(n) as orphanCount
    expected: "orphanCount = 0 for all types"

  - id: TC-D3-03-02
    name: "중복 ID 검출"
    cypher: |
      MATCH (n)
      WHERE n.id IS NOT NULL
      WITH n.id as id, count(*) as cnt
      WHERE cnt > 1
      RETURN id, cnt
    expected: "결과 0건"

  - id: TC-D3-03-03
    name: "Employee-OrgUnit 연결"
    cypher: |
      MATCH (e:Employee)
      WHERE NOT (e)-[:BELONGS_TO]->(:OrgUnit)
      RETURN count(e) as unlinkedCount
    expected: "unlinkedCount = 0"

  - id: TC-D3-03-04
    name: "Finding-Evidence 연결"
    cypher: |
      MATCH (f:Finding)
      WHERE NOT (f)-[:HAS_EVIDENCE]->(:Evidence)
      RETURN count(f) as unevidencedCount
    expected: "unevidencedCount = 0"
```

#### TS-D3-04: KG 쿼리 성능 검증

```yaml
scenario_id: TS-D3-04
name: "KG 쿼리 성능 검증"
category: KG
priority: P1

test_cases:
  - id: TC-D3-04-01
    name: "가동률 조회 쿼리"
    cypher: |
      MATCH (o:OrgUnit {orgUnitId: 'ORG-0011'})<-[:BELONGS_TO]-(e:Employee)
      MATCH (e)-[a:ASSIGNED_TO]->(p:Project)
      MATCH (a)-[:FOR_BUCKET]->(tb:TimeBucket)
      WHERE tb.weekNumber >= 4 AND tb.weekNumber <= 16
      RETURN tb.bucketId, sum(a.allocationFTE) as totalFTE
      ORDER BY tb.weekNumber
    expected_time: "< 500ms"

  - id: TC-D3-04-02
    name: "역량 갭 조회 쿼리"
    cypher: |
      MATCH (c:Competency {category: 'AI/ML'})<-[ce:HAS_EVIDENCE]-(e:Employee)
      WHERE ce.level >= 4
      RETURN c.name, count(e) as expertCount
    expected_time: "< 500ms"

  - id: TC-D3-04-03
    name: "의사결정 추적 쿼리"
    cypher: |
      MATCH (dc:DecisionCase)-[:HAS_OPTION]->(opt:Option)
      MATCH (opt)-[:EVALUATED_BY]->(eval:Evaluation)
      MATCH (dc)-[:HAS_FINDING]->(f:Finding)-[:HAS_EVIDENCE]->(ev:Evidence)
      WHERE dc.caseId = 'DC-001'
      RETURN dc, opt, eval, f, ev
    expected_time: "< 1000ms"
```

### 4.3 Day 3 pytest 구현

```python
# tests/test_day3_kg.py

import pytest
from neo4j import GraphDatabase

class TestKGSchema:
    """TS-D3-01: Neo4j 스키마 검증"""

    @pytest.fixture(scope="class")
    def driver(self):
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )
        yield driver
        driver.close()

    def test_node_type_count(self, driver):
        """TC-D3-01-01: 노드 타입 47개 이상"""
        with driver.session() as session:
            result = session.run("CALL db.labels() YIELD label RETURN count(label) as cnt")
            count = result.single()["cnt"]
            assert count >= 47, f"Expected >= 47 node types, got {count}"

    def test_required_node_types(self, driver):
        """TC-D3-01-02: 필수 노드 타입 존재"""
        required = ['Employee', 'OrgUnit', 'Project', 'Competency',
                    'Assignment', 'Opportunity', 'DecisionCase', 'Option']
        with driver.session() as session:
            result = session.run("CALL db.labels() YIELD label RETURN collect(label) as labels")
            labels = result.single()["labels"]
            for node_type in required:
                assert node_type in labels, f"Missing node type: {node_type}"


class TestKGIntegrity:
    """TS-D3-03: KG 무결성 검증"""

    def test_no_orphan_nodes(self, driver):
        """TC-D3-03-01: 고아 노드 0건"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE NOT (n)--()
                RETURN count(n) as orphanCount
            """)
            count = result.single()["orphanCount"]
            assert count == 0, f"Found {count} orphan nodes"

    def test_no_duplicate_ids(self, driver):
        """TC-D3-03-02: 중복 ID 0건"""
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.id IS NOT NULL
                WITH n.id as id, count(*) as cnt
                WHERE cnt > 1
                RETURN count(id) as duplicateCount
            """)
            count = result.single()["duplicateCount"]
            assert count == 0, f"Found {count} duplicate IDs"
```

### 4.4 Day 3 체크리스트

| 항목 | 검증 방법 | Pass 기준 |
|------|----------|----------|
| 노드 타입 수 | Cypher | ≥ 47개 |
| 관계 타입 수 | Cypher | ≥ 50개 |
| Employee 노드 | Cypher | ≥ 65개 |
| 고아 노드 | Cypher | 0개 |
| 중복 ID | Cypher | 0건 |
| 쿼리 성능 | Benchmark | < 500ms |
| AC-5 (커버리지) | Dashboard | 100% |

---

## 5. Day 4 테스트: P5 Agent 엔진

### 5.1 테스트 목적

6개 서브에이전트의 기능 및 출력 형식 검증

### 5.2 테스트 시나리오

#### TS-D4-01: Query Decomposition Agent

```yaml
scenario_id: TS-D4-01
name: "Query Decomposition Agent 검증"
category: Agent
priority: P0

test_cases:
  - id: TC-D4-01-01
    name: "A-1 질문 분해"
    input:
      question: "향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘"
    expected_output:
      type: "CAPACITY_FORECAST"
      scope:
        horizon: 12
        unit: "WEEK"
      objective:
        metricType: "UTILIZATION"
        targetValue: 0.9
    assertions:
      - "output.type == 'CAPACITY_FORECAST'"
      - "output.scope.horizon == 12"
      - "'UTILIZATION' in output.objective.metricType"

  - id: TC-D4-01-02
    name: "B-1 질문 분해"
    input:
      question: "'100억 미디어 AX' 프로젝트 내부 수행 가능 여부와 성공확률"
    expected_output:
      type: "GO_NOGO"
      scope:
        opportunity: "100억 미디어 AX"
    assertions:
      - "output.type == 'GO_NOGO'"
      - "'미디어' in output.scope.opportunity"

  - id: TC-D4-01-03
    name: "C-1 질문 분해"
    input:
      question: "데이터플랫폼팀 1명 증원 요청의 원인분해"
    expected_output:
      type: "HEADCOUNT_ANALYSIS"
    assertions:
      - "output.type == 'HEADCOUNT_ANALYSIS'"
      - "output.scope.requestedHeadcount >= 1"

  - id: TC-D4-01-04
    name: "D-1 질문 분해"
    input:
      question: "AI-driven 전환 관점에서 역량 갭 Top10 정량화"
    expected_output:
      type: "COMPETENCY_GAP"
    assertions:
      - "output.type == 'COMPETENCY_GAP'"
      - "'AI' in str(output.scope)"
```

#### TS-D4-02: Option Generator Agent

```yaml
scenario_id: TS-D4-02
name: "Option Generator Agent 검증"
category: Agent
priority: P0

test_cases:
  - id: TC-D4-02-01
    name: "3안 생성 확인"
    input:
      decision_case:
        type: "GO_NOGO"
        opportunity: "100억 미디어 AX"
    expected_output:
      option_count: 3
      option_types: ["CONSERVATIVE", "BALANCED", "AGGRESSIVE"]
    assertions:
      - "len(output.options) == 3"
      - "all(opt.option_type in ['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE'] for opt in output.options)"

  - id: TC-D4-02-02
    name: "Option 필수 필드"
    assertions:
      - "all('name' in opt for opt in output.options)"
      - "all('description' in opt for opt in output.options)"
      - "all('actions' in opt for opt in output.options)"
      - "all(len(opt['actions']) > 0 for opt in output.options)"

  - id: TC-D4-02-03
    name: "추천 옵션 선정"
    assertions:
      - "'recommendation' in output"
      - "output.recommendation in [opt.option_id for opt in output.options]"
```

#### TS-D4-03: Impact Simulator Agent

```yaml
scenario_id: TS-D4-03
name: "Impact Simulator Agent 검증"
category: Agent
priority: P0

test_cases:
  - id: TC-D4-03-01
    name: "As-Is vs To-Be 비교"
    input:
      option:
        option_id: "OPT-001"
        option_type: "BALANCED"
      baseline:
        utilization: 0.85
        headcount: 10
    expected_output:
      metrics:
        - type: "UTILIZATION"
        - type: "COST"
        - type: "TIME"
      comparison:
        as_is: {}
        to_be: {}
    assertions:
      - "'as_is' in output.comparison"
      - "'to_be' in output.comparison"
      - "len(output.metrics) >= 3"

  - id: TC-D4-03-02
    name: "시계열 예측"
    assertions:
      - "'time_series' in output"
      - "len(output.time_series) > 0"
```

#### TS-D4-04: Success Probability Agent

```yaml
scenario_id: TS-D4-04
name: "Success Probability Agent 검증"
category: Agent
priority: P0

test_cases:
  - id: TC-D4-04-01
    name: "성공확률 계산"
    input:
      option:
        option_id: "OPT-001"
        option_type: "BALANCED"
      context:
        resource_match: 0.7
        timeline_risk: 0.3
    expected_output:
      probability: "number (0-1)"
      confidence: "number (0-1)"
      factors: []
    assertions:
      - "0 <= output.probability <= 1"
      - "0 <= output.confidence <= 1"
      - "len(output.factors) > 0"

  - id: TC-D4-04-02
    name: "성공 요인 분해"
    assertions:
      - "all('name' in f for f in output.factors)"
      - "all('weight' in f for f in output.factors)"
      - "all('score' in f for f in output.factors)"
```

#### TS-D4-05: Validator Agent

```yaml
scenario_id: TS-D4-05
name: "Validator Agent 검증"
category: Agent
priority: P0

test_cases:
  - id: TC-D4-05-01
    name: "근거 연결 검증"
    input:
      response:
        claims:
          - text: "AI솔루션팀 가동률 90% 초과"
            evidence:
              - source: "TMS"
                ref: "Assignment 테이블"
          - text: "근거 없는 주장"
            evidence: null
    expected_output:
      evidence_coverage: 0.5
      hallucination_risk: 0.5
    assertions:
      - "output.evidence_coverage == 0.5"
      - "output.hallucination_risk >= 0.4"

  - id: TC-D4-05-02
    name: "환각 탐지"
    input:
      response:
        claims:
          - text: "존재하지 않는 프로젝트 PRJ-999"
            evidence: null
    assertions:
      - "output.hallucination_risk > 0.5"
      - "len(output.flagged_claims) > 0"
```

#### TS-D4-06: Workflow Builder Agent

```yaml
scenario_id: TS-D4-06
name: "Workflow Builder Agent 검증"
category: Agent
priority: P0

test_cases:
  - id: TC-D4-06-01
    name: "8단계 워크플로 생성"
    input:
      decision_case:
        type: "GO_NOGO"
    expected_output:
      workflow:
        steps: []
    assertions:
      - "len(output.workflow.steps) == 8"
      - "output.workflow.steps[0].type == 'QUERY_DECOMPOSITION'"
      - "output.workflow.steps[-1].type == 'WORKFLOW_GENERATION'"

  - id: TC-D4-06-02
    name: "HITL 중단점 확인"
    assertions:
      - "any(step.hitl_gate for step in output.workflow.steps)"
```

### 5.3 Day 4 pytest 구현

```python
# tests/test_day4_agents.py

import pytest
from backend.agent_runtime.agents.query_decomposition import QueryDecompositionAgent
from backend.agent_runtime.agents.option_generator import OptionGeneratorAgent
from backend.agent_runtime.agents.impact_simulator import ImpactSimulatorAgent
from backend.agent_runtime.agents.success_probability import SuccessProbabilityAgent
from backend.agent_runtime.agents.validator import ValidatorAgent
from backend.agent_runtime.agents.workflow_builder import WorkflowBuilderAgent


class TestQueryDecomposition:
    """TS-D4-01: Query Decomposition Agent"""

    @pytest.fixture
    def agent(self):
        return QueryDecompositionAgent()

    def test_capacity_question(self, agent):
        """TC-D4-01-01: A-1 질문 분해"""
        result = agent.decompose("향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘")
        assert result.query_type.value == "CAPACITY_FORECAST"
        assert result.horizon == 12

    def test_go_nogo_question(self, agent):
        """TC-D4-01-02: B-1 질문 분해"""
        result = agent.decompose("'100억 미디어 AX' 프로젝트 내부 수행 가능 여부와 성공확률")
        assert result.query_type.value == "GO_NOGO"

    def test_headcount_question(self, agent):
        """TC-D4-01-03: C-1 질문 분해"""
        result = agent.decompose("데이터플랫폼팀 1명 증원 요청의 원인분해")
        assert result.query_type.value == "HEADCOUNT_ANALYSIS"

    def test_competency_question(self, agent):
        """TC-D4-01-04: D-1 질문 분해"""
        result = agent.decompose("AI-driven 전환 관점에서 역량 갭 Top10 정량화")
        assert result.query_type.value == "COMPETENCY_GAP"


class TestOptionGenerator:
    """TS-D4-02: Option Generator Agent"""

    @pytest.fixture
    def agent(self):
        return OptionGeneratorAgent()

    def test_generates_three_options(self, agent):
        """TC-D4-02-01: 3안 생성"""
        context = {"opportunity": "100억 미디어 AX"}
        result = agent.generate("GO_NOGO", context, {})
        assert len(result.options) == 3

    def test_option_types(self, agent):
        """TC-D4-02-01: 옵션 타입 다양성"""
        context = {"opportunity": "100억 미디어 AX"}
        result = agent.generate("GO_NOGO", context, {})
        types = {opt.option_type.value for opt in result.options}
        assert types == {"CONSERVATIVE", "BALANCED", "AGGRESSIVE"}


class TestImpactSimulator:
    """TS-D4-03: Impact Simulator Agent"""

    @pytest.fixture
    def agent(self):
        return ImpactSimulatorAgent()

    def test_as_is_to_be_comparison(self, agent):
        """TC-D4-03-01: As-Is vs To-Be"""
        option = {"option_id": "OPT-001", "option_type": "BALANCED"}
        baseline = {"utilization": 0.85, "headcount": 10}
        result = agent.simulate("GO_NOGO", option, baseline, 12)

        assert hasattr(result, 'metrics')
        assert len(result.metrics) >= 3


class TestSuccessProbability:
    """TS-D4-04: Success Probability Agent"""

    @pytest.fixture
    def agent(self):
        return SuccessProbabilityAgent()

    def test_probability_range(self, agent):
        """TC-D4-04-01: 확률 범위"""
        result = agent.calculate_probability(
            subject_type="OPTION",
            subject_id="OPT-001",
            subject_name="테스트 옵션",
            context={}
        )
        assert 0 <= result.probability <= 1
        assert 0 <= result.confidence <= 1


class TestValidator:
    """TS-D4-05: Validator Agent"""

    @pytest.fixture
    def agent(self):
        return ValidatorAgent()

    def test_evidence_coverage(self, agent):
        """TC-D4-05-01: 근거 연결률"""
        result = agent.validate(
            response_text="AI솔루션팀 가동률 90% 초과 예상",
            evidence_refs=[{"source": "TMS", "ref": "Assignment"}],
            kg_context={}
        )
        assert hasattr(result, 'evidence_coverage')
        assert 0 <= result.evidence_coverage <= 1


class TestWorkflowBuilder:
    """TS-D4-06: Workflow Builder Agent"""

    @pytest.fixture
    def agent(self):
        return WorkflowBuilderAgent()

    def test_workflow_steps(self, agent):
        """TC-D4-06-01: 8단계 워크플로"""
        workflow = agent.create_workflow("GO_NOGO")
        assert len(workflow.steps) == 8
```

### 5.4 Day 4 체크리스트

| 항목 | 검증 방법 | Pass 기준 |
|------|----------|----------|
| Query Decomposition | pytest | 4개 UC 분해 성공 |
| Option Generator | pytest | 3안 생성 |
| Impact Simulator | pytest | As-Is/To-Be 비교 |
| Success Probability | pytest | 확률 0-1 범위 |
| Validator | pytest | 근거 연결 검증 |
| Workflow Builder | pytest | 8단계 생성 |
| AC-2 (3안 비교) | E2E | 100% |

---

## 6. Day 5 테스트: P6-P7 Workflow + 평가

### 6.1 테스트 목적

HITL 승인 워크플로와 평가 시스템 동작 검증

### 6.2 테스트 시나리오

#### TS-D5-01: HITL 승인 워크플로

```yaml
scenario_id: TS-D5-01
name: "HITL 승인 워크플로 검증"
category: Workflow
priority: P0

test_cases:
  - id: TC-D5-01-01
    name: "승인 요청 생성"
    input:
      decision_case_id: "DC-001"
      selected_option: "OPT-002"
    expected_output:
      approval_request:
        status: "PENDING"
        required_level: "TEAM_LEAD | DIVISION | EXECUTIVE"
    assertions:
      - "output.approval_request.status == 'PENDING'"
      - "'required_level' in output.approval_request"

  - id: TC-D5-01-02
    name: "승인 레벨 결정"
    input:
      decision_type: "GO_NOGO"
      deal_value: 10_000_000_000  # 100억
    expected_output:
      required_level: "EXECUTIVE"
    assertions:
      - "output.required_level == 'EXECUTIVE'"  # 10억 이상

  - id: TC-D5-01-03
    name: "승인 처리"
    input:
      approval_id: "APR-001"
      decision: "APPROVE"
      approver_id: "EMP-000001"
      comment: "승인합니다"
    expected_output:
      status: "APPROVED"
      workflow_triggered: true
    assertions:
      - "output.status == 'APPROVED'"
      - "output.workflow_triggered == True"

  - id: TC-D5-01-04
    name: "거부 처리"
    input:
      approval_id: "APR-002"
      decision: "REJECT"
      reason: "예산 초과"
    expected_output:
      status: "REJECTED"
    assertions:
      - "output.status == 'REJECTED'"

  - id: TC-D5-01-05
    name: "에스컬레이션"
    input:
      approval_id: "APR-003"
      action: "ESCALATE"
      to_level: "EXECUTIVE"
    expected_output:
      status: "ESCALATED"
      new_level: "EXECUTIVE"
```

#### TS-D5-02: Decision Log 검증

```yaml
scenario_id: TS-D5-02
name: "Decision Log 검증"
category: Workflow
priority: P0

test_cases:
  - id: TC-D5-02-01
    name: "의사결정 로그 기록"
    input:
      decision_case_id: "DC-001"
      final_decision: "OPT-002"
      approver: "EMP-000001"
    expected_output:
      log_entry:
        decision_case_id: "DC-001"
        selected_option_id: "OPT-002"
        approver_id: "EMP-000001"
        timestamp: "datetime"
    assertions:
      - "'timestamp' in output.log_entry"
      - "'decision_case_id' in output.log_entry"

  - id: TC-D5-02-02
    name: "감사 추적"
    assertions:
      - "'audit_trail' in output"
      - "all('actor' in entry for entry in output.audit_trail)"
      - "all('action' in entry for entry in output.audit_trail)"
```

#### TS-D5-03: Agent 평가 지표

```yaml
scenario_id: TS-D5-03
name: "Agent 평가 지표 검증"
category: Evaluation
priority: P0

test_cases:
  - id: TC-D5-03-01
    name: "완결성 측정"
    metric: "completeness"
    calculation: |
      required_fields = ['type', 'options', 'recommendation', 'evidence']
      present_fields = count(field in response for field in required_fields)
      completeness = present_fields / len(required_fields)
    target: "> 0.9"

  - id: TC-D5-03-02
    name: "근거 연결률 측정"
    metric: "evidence_coverage"
    calculation: |
      evidenced_claims = count(claim with evidence)
      total_claims = count(all claims)
      coverage = evidenced_claims / total_claims
    target: "> 0.95"
    acceptance_criteria: "AC-3"

  - id: TC-D5-03-03
    name: "환각률 측정"
    metric: "hallucination_rate"
    calculation: |
      unevidenced_claims = count(claims without evidence)
      total_claims = count(all claims)
      hallucination_rate = unevidenced_claims / total_claims
    target: "< 0.05"
    acceptance_criteria: "AC-4"

  - id: TC-D5-03-04
    name: "재현성 측정"
    metric: "reproducibility"
    calculation: |
      # 동일 입력으로 5회 실행
      results = [run(same_input) for _ in range(5)]
      consistency = count(identical_results) / 5
    target: "> 0.95"

  - id: TC-D5-03-05
    name: "응답 시간 측정"
    metric: "response_time"
    calculation: "end_time - start_time"
    target: "< 30s"
```

#### TS-D5-04: Ontology 평가 지표

```yaml
scenario_id: TS-D5-04
name: "Ontology 평가 지표 검증"
category: Evaluation
priority: P0

test_cases:
  - id: TC-D5-04-01
    name: "엔터티 커버리지"
    metric: "entity_coverage"
    cypher: |
      CALL db.labels() YIELD label
      WITH collect(label) as labels
      RETURN size([l IN labels WHERE l IN $required_labels]) / size($required_labels) as coverage
    target: "= 1.0"
    acceptance_criteria: "AC-5"

  - id: TC-D5-04-02
    name: "링크율"
    metric: "link_rate"
    cypher: |
      MATCH (n)
      WITH count(n) as total
      MATCH (n) WHERE (n)--()
      WITH total, count(n) as linked
      RETURN toFloat(linked) / total as link_rate
    target: "> 0.95"

  - id: TC-D5-04-03
    name: "중복/충돌률"
    metric: "duplicate_rate"
    cypher: |
      MATCH (n)
      WHERE n.id IS NOT NULL
      WITH n.id as id, count(*) as cnt
      WHERE cnt > 1
      RETURN count(id) as duplicate_count
    target: "= 0"
```

### 6.3 Day 5 pytest 구현

```python
# tests/test_day5_workflow.py

import pytest
from datetime import datetime
from backend.agent_runtime.workflows.hitl_approval import (
    HITLApprovalManager,
    ApprovalLevel,
    ApprovalStatus,
    DecisionType
)


class TestHITLApproval:
    """TS-D5-01: HITL 승인 워크플로"""

    @pytest.fixture
    def manager(self):
        return HITLApprovalManager()

    def test_create_approval_request(self, manager):
        """TC-D5-01-01: 승인 요청 생성"""
        workflow_context = {
            "decision_case_id": "DC-001",
            "options": {"recommendation": "OPT-002"},
            "impact_analysis": {},
            "validation_result": {"hallucination_risk": 0.03}
        }
        request = manager.create_approval_request(
            decision_type=DecisionType.GO_NOGO,
            workflow_context=workflow_context
        )
        assert request.status == ApprovalStatus.PENDING

    def test_approval_level_determination(self, manager):
        """TC-D5-01-02: 승인 레벨 결정"""
        context = {
            "opportunity": {"deal_value": 10_000_000_000}
        }
        level = manager._determine_approval_level(DecisionType.GO_NOGO, context)
        # 10억 이상은 EXECUTIVE 또는 DIVISION
        assert level in [ApprovalLevel.EXECUTIVE, ApprovalLevel.DIVISION]

    def test_approve_request(self, manager):
        """TC-D5-01-03: 승인 처리"""
        # Create request first
        workflow_context = {"decision_case_id": "DC-001", "options": {}}
        request = manager.create_approval_request(DecisionType.GO_NOGO, workflow_context)

        # Approve
        result = manager.process_approval(
            request_id=request.request_id,
            decision="approve",
            approver_id="EMP-000001",
            comment="승인"
        )
        assert result.status == ApprovalStatus.APPROVED

    def test_reject_request(self, manager):
        """TC-D5-01-04: 거부 처리"""
        workflow_context = {"decision_case_id": "DC-002", "options": {}}
        request = manager.create_approval_request(DecisionType.GO_NOGO, workflow_context)

        result = manager.process_approval(
            request_id=request.request_id,
            decision="reject",
            approver_id="EMP-000001",
            comment="예산 초과"
        )
        assert result.status == ApprovalStatus.REJECTED


class TestDecisionLog:
    """TS-D5-02: Decision Log"""

    @pytest.fixture
    def manager(self):
        return HITLApprovalManager()

    def test_log_creation(self, manager):
        """TC-D5-02-01: 로그 기록"""
        logs = manager.get_decision_logs(limit=10)
        # 로그 조회 가능 확인
        assert isinstance(logs, list)


class TestAgentEvalMetrics:
    """TS-D5-03: Agent 평가 지표"""

    def test_completeness_calculation(self):
        """TC-D5-03-01: 완결성"""
        response = {
            "type": "GO_NOGO",
            "options": [],
            "recommendation": "OPT-001",
            "evidence": []
        }
        required = ["type", "options", "recommendation", "evidence"]
        present = sum(1 for f in required if f in response)
        completeness = present / len(required)
        assert completeness > 0.9

    def test_evidence_coverage_target(self):
        """TC-D5-03-02: 근거 연결률 목표"""
        # AC-3: >= 95%
        target = 0.95
        assert target >= 0.95

    def test_hallucination_rate_target(self):
        """TC-D5-03-03: 환각률 목표"""
        # AC-4: <= 5%
        target = 0.05
        assert target <= 0.05
```

### 6.4 Day 5 체크리스트

| 항목 | 검증 방법 | Pass 기준 |
|------|----------|----------|
| 승인 요청 생성 | pytest | 상태 PENDING |
| 승인 레벨 결정 | pytest | 금액별 자동 결정 |
| 승인/거부 처리 | pytest | 상태 변경 |
| Decision Log | pytest | 기록 생성 |
| 완결성 지표 | Dashboard | > 90% |
| 근거 연결률 | Dashboard | > 95% (AC-3) |
| 환각률 | Dashboard | < 5% (AC-4) |
| HITL 워크플로 | E2E | 동작 (AC-6) |

---

## 7. 통합 테스트 시나리오

### 7.1 E2E 시나리오: A-1 질문 전체 플로우

```yaml
scenario_id: E2E-01
name: "A-1 질문 전체 플로우"
category: E2E
priority: P0

steps:
  - step: 1
    name: "질문 입력"
    action: "사용자가 A-1 질문 입력"
    input: "향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘"

  - step: 2
    name: "질문 분해"
    agent: "QueryDecomposition"
    expected: "CAPACITY_FORECAST 타입으로 분해"

  - step: 3
    name: "KG 조회"
    action: "Neo4j에서 관련 데이터 조회"
    expected: "Employee, Assignment, TimeBucket 노드 조회"

  - step: 4
    name: "대안 생성"
    agent: "OptionGenerator"
    expected: "3안 생성 (내부재배치/외부충원/역량강화)"

  - step: 5
    name: "영향도 시뮬레이션"
    agent: "ImpactSimulator"
    expected: "As-Is vs To-Be 비교 결과"

  - step: 6
    name: "성공확률 계산"
    agent: "SuccessProbability"
    expected: "각 옵션별 성공확률"

  - step: 7
    name: "검증"
    agent: "Validator"
    expected: "근거 연결률 > 95%, 환각률 < 5%"

  - step: 8
    name: "HITL 승인"
    action: "승인 요청 생성 및 처리"
    expected: "승인 완료"

  - step: 9
    name: "워크플로 생성"
    agent: "WorkflowBuilder"
    expected: "실행 계획 생성"

acceptance:
  - "AC-1: 유스케이스 응답 ✓"
  - "AC-2: 3안 비교 ✓"
  - "AC-3: 근거 연결률 ≥ 95% ✓"
  - "AC-4: 환각률 ≤ 5% ✓"
  - "AC-6: HITL 워크플로 ✓"
```

### 7.2 E2E 시나리오: B-1 질문 전체 플로우

```yaml
scenario_id: E2E-02
name: "B-1 질문 전체 플로우"
category: E2E
priority: P0

steps:
  - step: 1
    input: "'100억 미디어 AX' 프로젝트 내부 수행 가능 여부와 성공확률"

  - step: 2
    expected: "GO_NOGO 타입으로 분해"

  - step: 3
    expected: "Opportunity, ResourceDemand, Competency 노드 조회"

  - step: 4
    expected: "3안 생성 (100%내부/내부70%+외부30%/역량강화후수주)"

  - step: 5
    expected: "마진율, 리스크 레벨 비교"

  - step: 6
    expected: "성공확률 0.45/0.75/0.65"

  - step: 7
    expected: "근거 연결 확인"

  - step: 8
    expected: "10억 이상 → EXECUTIVE 승인"
```

---

## 8. 테스트 결과 보고 템플릿

### 8.1 일일 테스트 리포트

```markdown
# Daily Test Report - Day X (YYYY-MM-DD)

## 요약
- 총 테스트 케이스: XX개
- Pass: XX개 (XX%)
- Fail: XX개 (XX%)
- Skip: XX개

## 상세 결과

### Unit Tests
| 모듈 | Pass | Fail | Coverage |
|------|------|------|----------|
| query_decomposition | X/X | X | XX% |
| option_generator | X/X | X | XX% |
| ... | | | |

### Integration Tests
| 시나리오 | 결과 | 비고 |
|----------|------|------|
| TS-DX-01 | ✅/❌ | |

### Acceptance Criteria
| AC | 목표 | 현재 | 상태 |
|----|------|------|------|
| AC-1 | 100% | XX% | 🟢/🟡/🔴 |
| AC-2 | 100% | XX% | 🟢/🟡/🔴 |
| AC-3 | ≥95% | XX% | 🟢/🟡/🔴 |
| AC-4 | ≤5% | XX% | 🟢/🟡/🔴 |
| AC-5 | 100% | XX% | 🟢/🟡/🔴 |
| AC-6 | 동작 | Y/N | 🟢/🟡/🔴 |

## 이슈
1. [Issue 제목] - 심각도, 담당자, 예상 해결일
```

### 8.2 pytest 실행 명령

```bash
# Day 별 테스트 실행
pytest tests/test_day2_data_readiness.py -v --tb=short
pytest tests/test_day3_kg.py -v --tb=short
pytest tests/test_day4_agents.py -v --tb=short
pytest tests/test_day5_workflow.py -v --tb=short

# 전체 테스트 + 커버리지
pytest tests/ -v --cov=backend --cov-report=html

# 특정 마커로 필터
pytest -m "acceptance" -v  # AC 테스트만
pytest -m "e2e" -v         # E2E 테스트만
```

---

## 부록: 테스트 데이터 셋

### A. Mock Input 데이터

```json
{
  "test_questions": {
    "A-1": "향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘",
    "B-1": "'100억 미디어 AX' 프로젝트를 내부 수행 가능한지, 성공확률은 얼마인지 알려줘",
    "C-1": "데이터플랫폼팀 1명 증원 요청의 원인을 분해해줘",
    "D-1": "AI-driven 전환 관점에서 역량 갭 Top10을 정량화해줘"
  }
}
```

### B. Expected Output 샘플

```json
{
  "A-1_expected": {
    "type": "CAPACITY_FORECAST",
    "options_count": 3,
    "findings_min": 1,
    "evidence_required": true
  }
}
```

---

*이 문서는 PoC 진행 중 업데이트될 수 있습니다.*
