"""API 테스트"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """헬스 체크 엔드포인트 테스트"""

    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "hr-dss-api"
        assert "timestamp" in data

    def test_readiness_check(self):
        """준비 상태 체크 테스트"""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestAPIInfo:
    """API 정보 테스트"""

    def test_api_info(self):
        """API 정보 테스트"""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "HR-DSS API"
        assert data["version"] == "0.2.0"
        assert "endpoints" in data


class TestAgentsEndpoints:
    """에이전트 API 테스트"""

    def test_list_agent_types(self):
        """에이전트 타입 목록 테스트"""
        response = client.get("/api/v1/agents/types")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) >= 6

    def test_execute_query(self):
        """쿼리 실행 테스트"""
        response = client.post(
            "/api/v1/agents/query",
            json={"question": "향후 12주 가동률 예측"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "request_id" in data
        assert "result" in data

    def test_get_agent_info(self):
        """에이전트 상세 정보 테스트"""
        response = client.get("/api/v1/agents/query-decomposition")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "query-decomposition"

    def test_get_agent_not_found(self):
        """존재하지 않는 에이전트 테스트"""
        response = client.get("/api/v1/agents/non-existent")
        assert response.status_code == 404


class TestDecisionsEndpoints:
    """의사결정 API 테스트"""

    def test_create_decision(self):
        """의사결정 생성 테스트"""
        response = client.post(
            "/api/v1/decisions",
            json={"title": "테스트 의사결정", "question": "테스트 질문입니다"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "테스트 의사결정"
        assert data["status"] == "pending"
        assert "id" in data

    def test_list_decisions(self):
        """의사결정 목록 조회 테스트"""
        response = client.get("/api/v1/decisions")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_decision_workflow(self):
        """의사결정 전체 워크플로우 테스트"""
        # 1. 생성
        create_response = client.post(
            "/api/v1/decisions",
            json={"title": "워크플로우 테스트", "question": "테스트용 질문"},
        )
        assert create_response.status_code == 200
        decision_id = create_response.json()["id"]

        # 2. 조회
        get_response = client.get(f"/api/v1/decisions/{decision_id}")
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "pending"

        # 3. 분석
        analyze_response = client.post(f"/api/v1/decisions/{decision_id}/analyze")
        assert analyze_response.status_code == 200
        assert analyze_response.json()["status"] == "analyzed"

        # 4. 조회 (분석 완료 상태)
        get_response2 = client.get(f"/api/v1/decisions/{decision_id}")
        assert get_response2.json()["status"] == "analyzed"
        assert get_response2.json()["options"] is not None

        # 5. 승인
        approve_response = client.post(
            f"/api/v1/decisions/{decision_id}/approve",
            json={"option_id": "opt-1", "comment": "테스트 승인"},
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"

    def test_decision_not_found(self):
        """존재하지 않는 의사결정 테스트"""
        response = client.get("/api/v1/decisions/non-existent-id")
        assert response.status_code == 404


class TestGraphEndpoints:
    """그래프 API 테스트"""

    def test_get_schema(self):
        """스키마 조회 테스트"""
        response = client.get("/api/v1/graph/schema")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "relationships" in data

    def test_get_stats(self):
        """통계 조회 테스트"""
        response = client.get("/api/v1/graph/stats")
        assert response.status_code == 200
        data = response.json()
        assert "node_count" in data
        assert "relationship_count" in data

    def test_list_node_types(self):
        """노드 타입 목록 테스트"""
        response = client.get("/api/v1/graph/nodes")
        assert response.status_code == 200
        data = response.json()
        assert "node_types" in data

    @patch("backend.api.routers.graph.Neo4jService.execute_query")
    def test_execute_query(self, mock_execute):
        """쿼리 실행 테스트"""
        # Neo4j mock 설정
        mock_execute.return_value = [{"n": {"id": "test-1", "name": "Test Node"}}]

        response = client.post(
            "/api/v1/graph/query",
            json={"cypher": "MATCH (n) RETURN n LIMIT 10"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_dangerous_query_blocked(self):
        """위험한 쿼리 차단 테스트"""
        response = client.post(
            "/api/v1/graph/query",
            json={"cypher": "MATCH (n) DELETE n"},
        )
        assert response.status_code == 400

    @patch("backend.api.routers.graph.Neo4jService.search")
    def test_search_graph(self, mock_search):
        """그래프 검색 테스트"""
        # Neo4j mock 설정
        mock_search.return_value = []

        response = client.get("/api/v1/graph/search", params={"q": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
