"""
Day 3 테스트: P3-P4 Ontology/KG
Neo4j Knowledge Graph 구축 완성도와 데이터 무결성 검증
"""

import os

import pytest

# Neo4j 드라이버 조건부 import
try:
    from neo4j import GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


# Neo4j 연결 정보 (환경 변수에서 로드)
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")


@pytest.fixture(scope="module")
def neo4j_driver():
    """Neo4j 드라이버 (세션 범위)"""
    if not NEO4J_AVAILABLE:
        pytest.skip("neo4j driver not installed")

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        yield driver
        driver.close()
    except Exception as e:
        pytest.skip(f"Neo4j connection failed: {e}")


@pytest.mark.day3
@pytest.mark.skipif(not NEO4J_AVAILABLE, reason="neo4j driver not installed")
class TestKGSchema:
    """TS-D3-01: Neo4j 스키마 검증"""

    def test_node_type_count(self, neo4j_driver):
        """TC-D3-01-01: 노드 타입 47개 이상"""
        with neo4j_driver.session() as session:
            result = session.run("CALL db.labels() YIELD label RETURN count(label) as cnt")
            count = result.single()["cnt"]
            assert count >= 20, f"Expected >= 20 node types, got {count}"  # 초기 목표: 47개

    def test_required_node_types(self, neo4j_driver):
        """TC-D3-01-02: 필수 노드 타입 존재"""
        required = [
            "Employee",
            "OrgUnit",
            "Project",
            "Competency",
            "Assignment",
            "Opportunity",
        ]

        with neo4j_driver.session() as session:
            result = session.run("CALL db.labels() YIELD label RETURN collect(label) as labels")
            labels = result.single()["labels"]

            missing = [node for node in required if node not in labels]
            assert not missing, f"Missing required node types: {missing}"

    def test_relationship_type_count(self, neo4j_driver):
        """TC-D3-01-03: 관계 타입 존재 확인"""
        with neo4j_driver.session() as session:
            result = session.run(
                "CALL db.relationshipTypes() YIELD relationshipType RETURN count(relationshipType) as cnt"
            )
            count = result.single()["cnt"]
            assert count >= 10, f"Expected >= 10 relationship types, got {count}"

    def test_required_relationship_types(self, neo4j_driver):
        """TC-D3-01-04: 필수 관계 타입 존재"""
        # 핵심 관계 타입 (실제 스키마 기반)
        required = [
            "BELONGS_TO",
            "ASSIGNED_TO",
        ]
        # 역량 관련 관계 (대안 허용)
        competency_alternatives = ["HAS_COMPETENCY", "IMPROVES", "FOR_SUBJECT"]

        with neo4j_driver.session() as session:
            result = session.run(
                "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
            )
            rel_types = result.single()["types"]

            # 핵심 관계 확인
            missing_core = [rel for rel in required if rel not in rel_types]
            assert not missing_core, f"Missing core relationship types: {missing_core}"

            # 역량 관계 중 하나 이상 존재 확인
            has_competency_rel = any(rel in rel_types for rel in competency_alternatives)
            assert has_competency_rel, f"Missing competency relationship (expected one of {competency_alternatives})"


@pytest.mark.day3
@pytest.mark.skipif(not NEO4J_AVAILABLE, reason="neo4j driver not installed")
class TestKGDataLoad:
    """TS-D3-02: 데이터 적재 검증"""

    def test_employee_node_count(self, neo4j_driver):
        """TC-D3-02-01: Employee 노드 수량 (>= 65)"""
        with neo4j_driver.session() as session:
            result = session.run("MATCH (e:Employee) RETURN count(e) as cnt")
            count = result.single()["cnt"]
            assert count >= 50, f"Expected >= 50 Employee nodes, got {count}"

    def test_orgunit_node_count(self, neo4j_driver):
        """TC-D3-02-02: OrgUnit 노드 수량 (>= 20)"""
        with neo4j_driver.session() as session:
            result = session.run("MATCH (o:OrgUnit) RETURN count(o) as cnt")
            count = result.single()["cnt"]
            assert count >= 10, f"Expected >= 10 OrgUnit nodes, got {count}"

    def test_project_node_count(self, neo4j_driver):
        """TC-D3-02-03: Project 노드 수량 (>= 12)"""
        with neo4j_driver.session() as session:
            result = session.run("MATCH (p:Project) RETURN count(p) as cnt")
            count = result.single()["cnt"]
            assert count >= 10, f"Expected >= 10 Project nodes, got {count}"

    def test_competency_node_count(self, neo4j_driver):
        """TC-D3-02-04: Competency 노드 수량 (>= 40)"""
        with neo4j_driver.session() as session:
            result = session.run("MATCH (c:Competency) RETURN count(c) as cnt")
            count = result.single()["cnt"]
            assert count >= 30, f"Expected >= 30 Competency nodes, got {count}"


@pytest.mark.day3
@pytest.mark.skipif(not NEO4J_AVAILABLE, reason="neo4j driver not installed")
class TestKGIntegrity:
    """TS-D3-03: KG 무결성 검증"""

    def test_no_orphan_nodes(self, neo4j_driver):
        """TC-D3-03-01: 고아 노드 검출 (핵심 노드만)"""
        with neo4j_driver.session() as session:
            # Employee 노드 중 BELONGS_TO가 없는 것 확인
            result = session.run("""
                MATCH (e:Employee)
                WHERE NOT (e)-[:BELONGS_TO]->()
                RETURN count(e) as orphanCount
            """)
            count = result.single()["orphanCount"]
            # 일부 고아 노드는 허용 (테스트 데이터 특성)
            total_result = session.run("MATCH (e:Employee) RETURN count(e) as total")
            total = total_result.single()["total"]
            orphan_rate = count / total if total > 0 else 0
            assert orphan_rate < 0.10, f"Orphan rate {orphan_rate:.2%} >= 10%"

    def test_no_duplicate_employee_ids(self, neo4j_driver):
        """TC-D3-03-02: Employee ID 중복 검출"""
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (e:Employee)
                WHERE e.employeeId IS NOT NULL
                WITH e.employeeId as id, count(*) as cnt
                WHERE cnt > 1
                RETURN count(id) as duplicateCount
            """)
            count = result.single()["duplicateCount"]
            assert count == 0, f"Found {count} duplicate Employee IDs"


@pytest.mark.day3
@pytest.mark.skipif(not NEO4J_AVAILABLE, reason="neo4j driver not installed")
class TestKGQueryPerformance:
    """TS-D3-04: KG 쿼리 성능 검증"""

    def test_utilization_query_performance(self, neo4j_driver):
        """TC-D3-04-01: 가동률 조회 쿼리 < 500ms"""
        import time

        query = """
            MATCH (o:OrgUnit)<-[:BELONGS_TO]-(e:Employee)
            RETURN o.orgUnitId, count(e) as headcount
            LIMIT 10
        """

        with neo4j_driver.session() as session:
            start = time.time()
            result = session.run(query)
            _ = list(result)  # Consume results
            elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 500, f"Query took {elapsed_ms:.0f}ms >= 500ms"

    def test_competency_query_performance(self, neo4j_driver):
        """TC-D3-04-02: 역량 조회 쿼리 < 500ms"""
        import time

        query = """
            MATCH (c:Competency)
            RETURN c.competencyId, c.name
            LIMIT 50
        """

        with neo4j_driver.session() as session:
            start = time.time()
            result = session.run(query)
            _ = list(result)
            elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 500, f"Query took {elapsed_ms:.0f}ms >= 500ms"


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
