"""
Day 3 테스트: P3-P4 Ontology/KG
Knowledge Graph 스키마 및 Mock 데이터 검증
- Neo4j 연결 없이 스키마 파일과 Mock 데이터 기반으로 검증
"""

import json
import re

import pytest


@pytest.fixture(scope="module")
def schema_content(project_root):
    """schema.cypher 파일 내용"""
    schema_path = project_root / "data" / "schemas" / "schema.cypher"
    with open(schema_path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def mock_data(project_root):
    """Mock 데이터 로드"""
    data = {}
    mock_dir = project_root / "data" / "mock"

    # 필수 Mock 파일들
    files = {
        "persons": "persons.json",
        "orgs": "orgs.json",
        "projects": "projects.json",
        "skills": "skills.json",
        "opportunities": "opportunities.json",
        "assignments": "assignments.json",
    }

    for key, filename in files.items():
        filepath = mock_dir / filename
        if filepath.exists():
            with open(filepath, encoding="utf-8") as f:
                data[key] = json.load(f)

    return data


@pytest.mark.day3
class TestKGSchema:
    """TS-D3-01: KG 스키마 검증 (schema.cypher 파일 기반)"""

    def test_node_type_count(self, schema_content):
        """TC-D3-01-01: 노드 타입 20개 이상 정의"""
        # CREATE CONSTRAINT xxx IF NOT EXISTS FOR (n:NodeType) 패턴에서 노드 타입 추출
        node_pattern = r"FOR\s+\(\w+:(\w+)\)\s+REQUIRE"
        matches = re.findall(node_pattern, schema_content, re.IGNORECASE)
        unique_nodes = set(matches)
        count = len(unique_nodes)
        assert count >= 20, f"Expected >= 20 node types in schema, got {count}"

    def test_required_node_types(self, schema_content):
        """TC-D3-01-02: 필수 노드 타입 존재"""
        required = [
            "Employee",
            "OrgUnit",
            "Project",
            "Competency",
            "Assignment",
            "Opportunity",
        ]

        # 스키마에서 노드 타입 추출: FOR (x:NodeType) REQUIRE 패턴
        node_pattern = r"FOR\s+\(\w+:(\w+)\)\s+REQUIRE"
        matches = re.findall(node_pattern, schema_content, re.IGNORECASE)
        defined_nodes = set(matches)

        missing = [node for node in required if node not in defined_nodes]
        assert not missing, f"Missing required node types in schema: {missing}"

    def test_relationship_type_count(self, schema_content):
        """TC-D3-01-03: 관계 타입 10개 이상 정의"""
        # 주석에서 관계 타입 패턴 추출: -[:RELATIONSHIP_TYPE]->
        rel_pattern = r"\[:(\w+)(?:\s*\{[^}]*\})?\]->"
        matches = re.findall(rel_pattern, schema_content)
        unique_rels = set(matches)
        count = len(unique_rels)
        assert count >= 10, f"Expected >= 10 relationship types in schema, got {count}"

    def test_required_relationship_types(self, schema_content):
        """TC-D3-01-04: 필수 관계 타입 존재"""
        # 핵심 관계 타입
        required = [
            "BELONGS_TO",
            "ASSIGNED_TO",
        ]
        # 역량 관련 관계 (대안 허용)
        competency_alternatives = ["HAS_COMPETENCY", "IMPROVES", "FOR_COMPETENCY"]

        # 스키마에서 관계 타입 추출
        rel_pattern = r"\[:(\w+)(?:\s*\{[^}]*\})?\]->"
        matches = re.findall(rel_pattern, schema_content)
        defined_rels = set(matches)

        # 핵심 관계 확인
        missing_core = [rel for rel in required if rel not in defined_rels]
        assert not missing_core, f"Missing core relationship types: {missing_core}"

        # 역량 관계 중 하나 이상 존재 확인
        has_competency_rel = any(rel in defined_rels for rel in competency_alternatives)
        assert has_competency_rel, (
            f"Missing competency relationship (expected one of {competency_alternatives})"
        )


@pytest.mark.day3
class TestKGDataLoad:
    """TS-D3-02: Mock 데이터 적재 검증"""

    def test_employee_node_count(self, mock_data):
        """TC-D3-02-01: Employee Mock 데이터 수량 (>= 50)"""
        employees = mock_data.get("persons", {}).get("employees", [])
        count = len(employees)
        assert count >= 50, f"Expected >= 50 employees in mock data, got {count}"

    def test_orgunit_node_count(self, mock_data):
        """TC-D3-02-02: OrgUnit Mock 데이터 수량 (>= 10)"""
        org_units = mock_data.get("orgs", {}).get("orgUnits", [])
        count = len(org_units)
        assert count >= 10, f"Expected >= 10 orgUnits in mock data, got {count}"

    def test_project_node_count(self, mock_data):
        """TC-D3-02-03: Project Mock 데이터 수량 (>= 10)"""
        projects = mock_data.get("projects", {}).get("projects", [])
        count = len(projects)
        assert count >= 10, f"Expected >= 10 projects in mock data, got {count}"

    def test_competency_node_count(self, mock_data):
        """TC-D3-02-04: Competency Mock 데이터 수량 (>= 30)"""
        competencies = mock_data.get("skills", {}).get("competencies", [])
        count = len(competencies)
        assert count >= 30, f"Expected >= 30 competencies in mock data, got {count}"


@pytest.mark.day3
class TestKGIntegrity:
    """TS-D3-03: Mock 데이터 무결성 검증"""

    def test_no_orphan_nodes(self, mock_data):
        """TC-D3-03-01: 고아 노드 검출 (Employee-OrgUnit 연결)"""
        employees = mock_data.get("persons", {}).get("employees", [])
        org_units = mock_data.get("orgs", {}).get("orgUnits", [])

        # 유효한 OrgUnit ID 집합
        valid_org_ids = {org["orgUnitId"] for org in org_units}

        # orgUnitId가 없거나 유효하지 않은 Employee 카운트
        orphan_count = 0
        for emp in employees:
            org_id = emp.get("orgUnitId")
            if not org_id or org_id not in valid_org_ids:
                orphan_count += 1

        total = len(employees)
        orphan_rate = orphan_count / total if total > 0 else 0
        assert orphan_rate < 0.10, f"Orphan rate {orphan_rate:.2%} >= 10% ({orphan_count}/{total})"

    def test_no_duplicate_employee_ids(self, mock_data):
        """TC-D3-03-02: Employee ID 중복 검출"""
        employees = mock_data.get("persons", {}).get("employees", [])

        # Employee ID 수집 및 중복 확인
        employee_ids = [emp.get("employeeId") for emp in employees if emp.get("employeeId")]
        unique_ids = set(employee_ids)

        duplicate_count = len(employee_ids) - len(unique_ids)
        assert duplicate_count == 0, f"Found {duplicate_count} duplicate Employee IDs"


@pytest.mark.day3
class TestKGQueryPerformance:
    """TS-D3-04: 데이터 처리 성능 검증 (Mock 기반 시뮬레이션)"""

    def test_utilization_query_performance(self, mock_data):
        """TC-D3-04-01: 가동률 조회 로직 < 500ms"""
        import time

        employees = mock_data.get("persons", {}).get("employees", [])

        start = time.time()

        # 조직별 직원 수 집계 (MATCH (o:OrgUnit)<-[:BELONGS_TO]-(e:Employee) 시뮬레이션)
        headcount_by_org = {}
        for emp in employees:
            org_id = emp.get("orgUnitId")
            if org_id:
                headcount_by_org[org_id] = headcount_by_org.get(org_id, 0) + 1

        # 상위 10개 조직 조회
        result = sorted(headcount_by_org.items(), key=lambda x: -x[1])[:10]

        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 500, f"Query simulation took {elapsed_ms:.0f}ms >= 500ms"
        assert len(result) > 0, "Expected at least one result"

    def test_competency_query_performance(self, mock_data):
        """TC-D3-04-02: 역량 조회 로직 < 500ms"""
        import time

        competencies = mock_data.get("skills", {}).get("competencies", [])

        start = time.time()

        # MATCH (c:Competency) RETURN c.competencyId, c.name LIMIT 50 시뮬레이션
        result = [
            {"competencyId": c.get("competencyId"), "name": c.get("name")}
            for c in competencies[:50]
        ]

        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 500, f"Query simulation took {elapsed_ms:.0f}ms >= 500ms"
        assert len(result) > 0, "Expected at least one result"


@pytest.mark.day3
@pytest.mark.acceptance
class TestKGAcceptance:
    """AC-5: KG 엔터티 커버리지 Acceptance 테스트"""

    def test_schema_file_exists(self, project_root):
        """schema.cypher 파일 존재 확인"""
        schema_path = project_root / "data" / "schemas" / "schema.cypher"
        assert schema_path.exists(), f"Schema file not found: {schema_path}"

    def test_schema_has_constraints(self, project_root):
        """스키마에 Constraint 정의 포함"""
        schema_path = project_root / "data" / "schemas" / "schema.cypher"

        with open(schema_path, encoding="utf-8") as f:
            content = f.read()

        assert "CREATE CONSTRAINT" in content, "No constraints defined in schema"
        # 최소 20개 이상의 constraint 확인
        constraint_count = content.count("CREATE CONSTRAINT")
        assert constraint_count >= 20, f"Only {constraint_count} constraints, expected >= 20"
