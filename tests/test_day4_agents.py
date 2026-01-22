"""
Day 4 테스트: P5 Agent 엔진
6개 서브에이전트의 기능 및 출력 형식 검증
"""

import sys
from pathlib import Path

import pytest

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Agent imports
try:
    from backend.agent_runtime.agents.impact_simulator import ImpactSimulatorAgent
    from backend.agent_runtime.agents.option_generator import OptionGeneratorAgent, OptionType
    from backend.agent_runtime.agents.query_decomposition import QueryDecompositionAgent, QueryType
    from backend.agent_runtime.agents.success_probability import SuccessProbabilityAgent
    from backend.agent_runtime.agents.validator import ValidatorAgent
    from backend.agent_runtime.agents.workflow_builder import WorkflowBuilderAgent

    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.day4
@pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
class TestQueryDecomposition:
    """TS-D4-01: Query Decomposition Agent 검증"""

    @pytest.fixture
    def agent(self):
        return QueryDecompositionAgent()

    def test_capacity_question_a1(self, agent, test_questions):
        """TC-D4-01-01: A-1 질문 분해 (CAPACITY)"""
        result = agent.decompose(test_questions["A-1"])

        assert result is not None, "Decomposition returned None"
        assert result.query_type == QueryType.CAPACITY, (
            f"Expected CAPACITY, got {result.query_type}"
        )
        # horizon은 constraints 내에 있음
        horizon = result.constraints.get("horizon_weeks", 12)
        assert horizon >= 12, f"Expected horizon >= 12, got {horizon}"

    def test_go_nogo_question_b1(self, agent, test_questions):
        """TC-D4-01-02: B-1 질문 분해 (GO_NOGO)"""
        result = agent.decompose(test_questions["B-1"])

        assert result is not None, "Decomposition returned None"
        assert result.query_type == QueryType.GO_NOGO, f"Expected GO_NOGO, got {result.query_type}"

    def test_headcount_question_c1(self, agent, test_questions):
        """TC-D4-01-03: C-1 질문 분해 (HEADCOUNT)"""
        result = agent.decompose(test_questions["C-1"])

        assert result is not None, "Decomposition returned None"
        assert result.query_type == QueryType.HEADCOUNT, (
            f"Expected HEADCOUNT, got {result.query_type}"
        )

    def test_competency_question_d1(self, agent, test_questions):
        """TC-D4-01-04: D-1 질문 분해 (COMPETENCY_GAP)"""
        result = agent.decompose(test_questions["D-1"])

        assert result is not None, "Decomposition returned None"
        assert result.query_type == QueryType.COMPETENCY_GAP, (
            f"Expected COMPETENCY_GAP, got {result.query_type}"
        )

    def test_decomposition_has_required_fields(self, agent, test_questions):
        """질문 분해 결과에 필수 필드 포함"""
        result = agent.decompose(test_questions["A-1"])

        assert hasattr(result, "query_type"), "Missing query_type"
        assert hasattr(result, "intent"), "Missing intent"
        assert hasattr(result, "sub_queries"), "Missing sub_queries"
        assert hasattr(result, "constraints"), "Missing constraints"


@pytest.mark.day4
@pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
class TestOptionGenerator:
    """TS-D4-02: Option Generator Agent 검증"""

    @pytest.fixture
    def agent(self):
        return OptionGeneratorAgent()

    def test_generates_three_options(self, agent):
        """TC-D4-02-01: 3안 생성 확인"""
        context = {"opportunity": {"name": "100억 미디어 AX", "deal_value": 10000000000}}
        result = agent.generate_options("GO_NOGO", context, {})

        assert result is not None, "Generation returned None"
        assert len(result.options) == 3, f"Expected 3 options, got {len(result.options)}"

    def test_option_types_diversity(self, agent):
        """TC-D4-02-01: 옵션 타입 다양성 (CONSERVATIVE/BALANCED/AGGRESSIVE)"""
        context = {"opportunity": {"name": "100억 미디어 AX", "deal_value": 10000000000}}
        result = agent.generate_options("GO_NOGO", context, {})

        types = {opt.option_type for opt in result.options}
        expected_types = {OptionType.CONSERVATIVE, OptionType.BALANCED, OptionType.AGGRESSIVE}

        assert types == expected_types, f"Expected all 3 option types, got {types}"

    def test_options_have_required_fields(self, agent):
        """TC-D4-02-02: Option 필수 필드 확인"""
        context = {"opportunity": {"name": "테스트 기회", "deal_value": 5000000000}}
        result = agent.generate_options("GO_NOGO", context, {})

        for opt in result.options:
            assert opt.name, f"Option {opt.option_id} missing name"
            assert opt.description, f"Option {opt.option_id} missing description"
            assert opt.actions, f"Option {opt.option_id} missing actions"
            assert len(opt.actions) > 0, f"Option {opt.option_id} has no actions"

    def test_recommendation_exists(self, agent):
        """TC-D4-02-03: 추천 옵션 존재"""
        context = {"opportunity": {"name": "테스트 기회", "deal_value": 5000000000}}
        result = agent.generate_options("GO_NOGO", context, {})

        assert result.recommendation is not None, "No recommendation provided"
        option_ids = {opt.option_id for opt in result.options}
        assert result.recommendation in option_ids, "Recommendation not in options"


@pytest.mark.day4
@pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
class TestImpactSimulator:
    """TS-D4-03: Impact Simulator Agent 검증"""

    @pytest.fixture
    def agent(self):
        return ImpactSimulatorAgent()

    def test_as_is_to_be_comparison(self, agent):
        """TC-D4-03-01: As-Is vs To-Be 비교 생성"""
        options = [{"option_id": "OPT-001", "option_type": "BALANCED", "name": "테스트 옵션"}]
        baseline = {"utilization": 0.85, "headcount": 10}
        result = agent.simulate("GO_NOGO", options, baseline, 12)

        assert result is not None, "Simulation returned None"
        assert hasattr(result, "analyses"), "Missing analyses"
        assert len(result.analyses) >= 1, f"Expected >= 1 analysis, got {len(result.analyses)}"
        # 첫 번째 분석의 메트릭 확인
        assert len(result.analyses[0].metrics) >= 3, "Expected >= 3 metrics"

    def test_metrics_have_values(self, agent):
        """TC-D4-03-01: 메트릭에 As-Is/To-Be 값 포함"""
        options = [{"option_id": "OPT-001", "option_type": "BALANCED", "name": "테스트 옵션"}]
        baseline = {"utilization": 0.85, "headcount": 10}
        result = agent.simulate("GO_NOGO", options, baseline, 12)

        for metric in result.analyses[0].metrics:
            assert hasattr(metric, "as_is_value"), f"Metric {metric.name} missing as_is_value"
            assert hasattr(metric, "to_be_value"), f"Metric {metric.name} missing to_be_value"

    def test_time_series_generation(self, agent):
        """TC-D4-03-02: 시계열 예측 생성"""
        options = [{"option_id": "OPT-001", "option_type": "BALANCED", "name": "테스트 옵션"}]
        baseline = {"utilization": 0.85, "headcount": 10}
        result = agent.simulate("GO_NOGO", options, baseline, 12)

        assert hasattr(result.analyses[0], "time_series"), "Missing time_series"


@pytest.mark.day4
@pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
class TestSuccessProbability:
    """TS-D4-04: Success Probability Agent 검증"""

    @pytest.fixture
    def agent(self):
        return SuccessProbabilityAgent()

    def test_probability_range(self, agent):
        """TC-D4-04-01: 확률 범위 0-1"""
        result = agent.calculate_probability(
            subject_type="OPTION",
            subject_id="OPT-001",
            subject_name="테스트 옵션",
            context={},
        )

        assert result is not None, "Calculation returned None"
        assert 0 <= result.success_probability <= 1, (
            f"Probability {result.success_probability} not in [0, 1]"
        )
        assert 0 <= result.confidence <= 1, f"Confidence {result.confidence} not in [0, 1]"

    def test_success_factors_provided(self, agent):
        """TC-D4-04-02: 성공 요인 분해"""
        result = agent.calculate_probability(
            subject_type="OPTION",
            subject_id="OPT-001",
            subject_name="테스트 옵션",
            context={},
        )

        assert hasattr(result, "success_factors"), "Missing success_factors"
        assert len(result.success_factors) > 0, "No success factors provided"

        for factor in result.success_factors:
            assert hasattr(factor, "name"), "Factor missing name"
            assert hasattr(factor, "weight"), "Factor missing weight"
            assert hasattr(factor, "score"), "Factor missing score"


@pytest.mark.day4
@pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
class TestValidator:
    """TS-D4-05: Validator Agent 검증"""

    @pytest.fixture
    def agent(self):
        return ValidatorAgent()

    def test_evidence_coverage_calculation(self, agent):
        """TC-D4-05-01: 근거 연결률 계산"""
        result = agent.validate(
            response_text="AI솔루션팀 가동률 90% 초과 예상",
            available_evidence=[{"source": "TMS", "ref": "Assignment 테이블"}],
            context={},
        )

        assert result is not None, "Validation returned None"
        assert hasattr(result, "evidence_link_rate"), "Missing evidence_link_rate"
        assert 0 <= result.evidence_link_rate <= 1, "evidence_link_rate not in [0, 1]"

    def test_hallucination_detection(self, agent):
        """TC-D4-05-02: 환각 탐지"""
        # 근거 없는 주장
        result = agent.validate(
            response_text="존재하지 않는 프로젝트 PRJ-999가 진행 중입니다",
            available_evidence=[],
            context={},
        )

        assert hasattr(result, "hallucination_risk"), "Missing hallucination_risk"
        # 근거 없으면 환각 위험 높아야 함
        assert result.hallucination_risk >= 0.3, (
            f"Hallucination risk {result.hallucination_risk} too low for unevidenced claim"
        )


@pytest.mark.day4
@pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
class TestWorkflowBuilder:
    """TS-D4-06: Workflow Builder Agent 검증"""

    @pytest.fixture
    def agent(self):
        return WorkflowBuilderAgent()

    def test_workflow_has_eight_steps(self, agent):
        """TC-D4-06-01: 8단계 워크플로 생성"""
        workflow = agent.build_workflow("GO_NOGO")

        assert workflow is not None, "Workflow creation returned None"
        assert hasattr(workflow, "steps"), "Workflow missing steps"
        assert len(workflow.steps) == 8, f"Expected 8 steps, got {len(workflow.steps)}"

    def test_workflow_step_order(self, agent):
        """TC-D4-06-01: 워크플로 단계 순서"""
        workflow = agent.build_workflow("GO_NOGO")

        # 첫 번째 단계는 QUERY_DECOMPOSITION
        from backend.agent_runtime.agents.workflow_builder import StepType

        assert workflow.steps[0].step_type == StepType.QUERY_DECOMPOSITION
        # 마지막 단계는 DECISION_LOG
        assert workflow.steps[-1].step_type == StepType.DECISION_LOG

    def test_hitl_gate_exists(self, agent):
        """TC-D4-06-02: HITL 중단점 존재"""
        workflow = agent.build_workflow("GO_NOGO")

        # HITL_APPROVAL 단계가 있는지 확인
        from backend.agent_runtime.agents.workflow_builder import StepType

        hitl_steps = [step for step in workflow.steps if step.step_type == StepType.HITL_APPROVAL]
        assert len(hitl_steps) > 0, "No HITL step found in workflow"


@pytest.mark.day4
@pytest.mark.acceptance
class TestAgentAcceptance:
    """AC-2: 3안 비교 생성 Acceptance 테스트"""

    @pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
    def test_all_question_types_supported(self, test_questions):
        """4대 유스케이스 모두 처리 가능"""
        agent = QueryDecompositionAgent()

        for q_id, question in test_questions.items():
            result = agent.decompose(question)
            assert result is not None, f"Failed to decompose {q_id}"
            assert result.query_type is not None, f"No query_type for {q_id}"

    @pytest.mark.skipif(not AGENTS_AVAILABLE, reason="Agent modules not available")
    def test_three_options_for_each_type(self):
        """각 질문 유형에 대해 3안 생성"""
        agent = OptionGeneratorAgent()
        query_types = ["GO_NOGO", "CAPACITY", "HEADCOUNT", "COMPETENCY_GAP"]

        for q_type in query_types:
            result = agent.generate_options(q_type, {}, {})
            assert len(result.options) == 3, (
                f"Expected 3 options for {q_type}, got {len(result.options)}"
            )
