"""
Day 6 테스트: P7 웹/앱 Prototype UI
UI 컴포넌트 존재 및 구조 검증
"""

from pathlib import Path

import pytest

# 프로젝트 경로
PROJECT_ROOT = Path(__file__).parent.parent
COMPONENTS_DIR = PROJECT_ROOT / "apps" / "web" / "components"


@pytest.mark.day6
class TestUIComponentsExist:
    """TS-D6-00: UI 컴포넌트 파일 존재 확인"""

    def test_conversational_ui_exists(self):
        """ConversationUI.tsx 존재"""
        assert (COMPONENTS_DIR / "ConversationUI.tsx").exists()

    def test_option_compare_exists(self):
        """OptionCompare.tsx 존재"""
        assert (COMPONENTS_DIR / "OptionCompare.tsx").exists()

    def test_explanation_panel_exists(self):
        """ExplanationPanel.tsx 존재"""
        assert (COMPONENTS_DIR / "ExplanationPanel.tsx").exists()

    def test_eval_dashboard_exists(self):
        """EvalDashboard.tsx 존재"""
        assert (COMPONENTS_DIR / "EvalDashboard.tsx").exists()

    def test_graph_viewer_exists(self):
        """GraphViewer.tsx 존재"""
        assert (COMPONENTS_DIR / "GraphViewer.tsx").exists()

    def test_agent_eval_dashboard_exists(self):
        """AgentEvalDashboard.tsx 존재"""
        assert (COMPONENTS_DIR / "AgentEvalDashboard.tsx").exists()

    def test_ontology_scorecard_exists(self):
        """OntologyScoreCard.tsx 존재"""
        assert (COMPONENTS_DIR / "OntologyScoreCard.tsx").exists()

    def test_data_quality_report_exists(self):
        """DataQualityReport.tsx 존재"""
        assert (COMPONENTS_DIR / "DataQualityReport.tsx").exists()


@pytest.mark.day6
class TestConversationUIStructure:
    """TS-D6-01: ConversationUI 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "ConversationUI.tsx"
        if not path.exists():
            pytest.skip("ConversationUI.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_message_interface(self, component_source):
        """TC-D6-01-01: Message 인터페이스 정의"""
        assert "interface Message" in component_source or "type Message" in component_source
        assert "user" in component_source
        assert "assistant" in component_source

    def test_has_scenario_presets(self, component_source):
        """TC-D6-01-02: 시나리오 프리셋 정의"""
        assert "ScenarioPreset" in component_source or "scenarioPreset" in component_source.lower()

    def test_has_constraint_interface(self, component_source):
        """TC-D6-01-03: Constraint 인터페이스 정의"""
        assert "Constraint" in component_source
        # 제약조건 타입 확인
        constraint_types = ["budget", "timeline", "headcount", "utilization"]
        found_types = sum(1 for ct in constraint_types if ct in component_source.lower())
        assert found_types >= 2, f"Found only {found_types} constraint types"

    def test_has_send_message_handler(self, component_source):
        """TC-D6-01-04: 메시지 전송 핸들러"""
        assert "onSendMessage" in component_source or "sendMessage" in component_source

    def test_has_timestamp(self, component_source):
        """TC-D6-01-01: 타임스탬프 필드"""
        assert "timestamp" in component_source.lower()


@pytest.mark.day6
class TestOptionCompareStructure:
    """TS-D6-02: OptionCompare 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "OptionCompare.tsx"
        if not path.exists():
            pytest.skip("OptionCompare.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_decision_option_interface(self, component_source):
        """TC-D6-02-01: DecisionOption 인터페이스"""
        assert "DecisionOption" in component_source or "interface.*Option" in component_source

    def test_has_three_option_types(self, component_source):
        """TC-D6-02-01: 3가지 옵션 타입 정의"""
        assert "CONSERVATIVE" in component_source
        assert "BALANCED" in component_source
        assert "AGGRESSIVE" in component_source

    def test_has_option_scores(self, component_source):
        """TC-D6-02-02: OptionScores 정의"""
        # 스코어 관련 필드 확인
        score_fields = ["impact", "feasibility", "risk", "cost", "time"]
        found_fields = sum(1 for sf in score_fields if sf in component_source.lower())
        assert found_fields >= 3, f"Found only {found_fields} score fields"

    def test_has_recommendation(self, component_source):
        """TC-D6-02-03: 추천 기능"""
        assert "recommendation" in component_source.lower()

    def test_has_impact_analysis(self, component_source):
        """TC-D6-02-05: 영향도 분석"""
        assert "impact" in component_source.lower()
        # baseline/projected 또는 as-is/to-be
        has_comparison = (
            "baseline" in component_source.lower()
            or "projected" in component_source.lower()
            or "as_is" in component_source.lower()
            or "to_be" in component_source.lower()
        )
        assert has_comparison, "No baseline/projected comparison found"

    def test_has_approval_handlers(self, component_source):
        """TC-D6-02-06: 승인/거부 핸들러"""
        assert "onApprove" in component_source or "approve" in component_source.lower()


@pytest.mark.day6
class TestExplanationPanelStructure:
    """TS-D6-03: ExplanationPanel 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "ExplanationPanel.tsx"
        if not path.exists():
            pytest.skip("ExplanationPanel.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_reasoning_steps(self, component_source):
        """TC-D6-03-01: 추론 단계"""
        assert "reasoning" in component_source.lower() or "step" in component_source.lower()

    def test_has_evidence(self, component_source):
        """TC-D6-03-02: Evidence"""
        assert "evidence" in component_source.lower()

    def test_has_assumptions(self, component_source):
        """TC-D6-03-03: 가정"""
        assert "assumption" in component_source.lower()

    def test_has_validation_result(self, component_source):
        """TC-D6-03-04: 검증 결과"""
        # 검증 관련 필드
        validation_keywords = ["validation", "coverage", "hallucination", "risk"]
        found = sum(1 for kw in validation_keywords if kw in component_source.lower())
        assert found >= 2, f"Found only {found} validation keywords"


@pytest.mark.day6
class TestEvalDashboardStructure:
    """TS-D6-04: EvalDashboard 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "EvalDashboard.tsx"
        if not path.exists():
            pytest.skip("EvalDashboard.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_system_health(self, component_source):
        """TC-D6-04-01: 시스템 헬스 상태"""
        assert "health" in component_source.lower() or "status" in component_source.lower()

    def test_has_alerts(self, component_source):
        """TC-D6-04-02: 알림 목록"""
        assert "alert" in component_source.lower() or "notification" in component_source.lower()

    def test_has_activities(self, component_source):
        """TC-D6-04-03: 활동 피드"""
        assert "activit" in component_source.lower() or "feed" in component_source.lower()


@pytest.mark.day6
class TestGraphViewerStructure:
    """TS-D6-05: GraphViewer 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "GraphViewer.tsx"
        if not path.exists():
            pytest.skip("GraphViewer.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_nodes(self, component_source):
        """TC-D6-05-01: 노드 정의"""
        assert "node" in component_source.lower()

    def test_has_edges(self, component_source):
        """TC-D6-05-02: 엣지/관계 정의"""
        assert "edge" in component_source.lower() or "relationship" in component_source.lower()

    def test_has_zoom_pan(self, component_source):
        """TC-D6-05-03: 줌/패닝"""
        zoom_pan_keywords = ["zoom", "pan", "scale", "transform"]
        found = sum(1 for kw in zoom_pan_keywords if kw in component_source.lower())
        assert found >= 1, "No zoom/pan functionality found"


@pytest.mark.day6
class TestAgentEvalDashboardStructure:
    """AgentEvalDashboard 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "AgentEvalDashboard.tsx"
        if not path.exists():
            pytest.skip("AgentEvalDashboard.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_agent_metrics(self, component_source):
        """Agent 평가 지표"""
        metrics = ["completeness", "accuracy", "coverage", "hallucination"]
        found = sum(1 for m in metrics if m in component_source.lower())
        assert found >= 2, f"Found only {found} agent metrics"


@pytest.mark.day6
class TestOntologyScoreCardStructure:
    """OntologyScoreCard 구조 검증"""

    @pytest.fixture
    def component_source(self):
        path = COMPONENTS_DIR / "OntologyScoreCard.tsx"
        if not path.exists():
            pytest.skip("OntologyScoreCard.tsx not found")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_has_ontology_metrics(self, component_source):
        """Ontology 평가 지표"""
        metrics = ["coverage", "link", "duplicate", "freshness"]
        found = sum(1 for m in metrics if m in component_source.lower())
        assert found >= 2, f"Found only {found} ontology metrics"


@pytest.mark.day6
@pytest.mark.acceptance
class TestDay6Acceptance:
    """Day 6 Acceptance 테스트"""

    def test_all_ui_components_exist(self):
        """AC-9 기반: 모든 핵심 UI 컴포넌트 존재"""
        required_components = [
            "ConversationUI.tsx",
            "OptionCompare.tsx",
            "ExplanationPanel.tsx",
            "EvalDashboard.tsx",
            "GraphViewer.tsx",
        ]

        missing = [comp for comp in required_components if not (COMPONENTS_DIR / comp).exists()]

        assert len(missing) == 0, f"Missing components: {missing}"

    def test_component_count(self):
        """UI 컴포넌트 총 개수"""
        tsx_files = list(COMPONENTS_DIR.glob("*.tsx"))
        assert len(tsx_files) >= 8, f"Expected >= 8 components, found {len(tsx_files)}"
