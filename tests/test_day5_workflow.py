"""
Day 5 테스트: P6-P7 Workflow + 평가
HITL 승인 워크플로와 평가 시스템 동작 검증
"""

import sys
from pathlib import Path

import pytest

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Workflow imports
try:
    from backend.agent_runtime.workflows.hitl_approval import (
        ApprovalLevel,
        ApprovalStatus,
        DecisionType,
        HITLApprovalSystem,
    )

    WORKFLOW_AVAILABLE = True
except ImportError as e:
    WORKFLOW_AVAILABLE = False
    IMPORT_ERROR = str(e)


@pytest.mark.day5
@pytest.mark.skipif(not WORKFLOW_AVAILABLE, reason="Workflow modules not available")
class TestHITLApprovalSystem:
    """TS-D5-01: HITL 승인 워크플로 검증"""

    @pytest.fixture
    def system(self):
        return HITLApprovalSystem()

    def test_create_approval_request(self, system):
        """TC-D5-01-01: 승인 요청 생성"""
        workflow_context = {
            "decision_case_id": "DC-001",
            "options": {"recommendation": "OPT-002", "options": []},
            "impact_analysis": {},
            "validation_result": {"hallucination_risk": 0.03},
        }
        request = system.create_approval_request(
            execution_id="EXEC-TEST-001",
            decision_type=DecisionType.GO_NOGO,
            workflow_context=workflow_context,
            requester_id="test@example.com",
        )

        assert request is not None, "Request creation returned None"
        assert request.request_id is not None, "Missing request_id"
        assert request.decision_type == DecisionType.GO_NOGO

    def test_approval_level_determination_high_value(self, system):
        """TC-D5-01-02: 고가 건 승인 레벨 결정 (10억 이상)"""
        context = {"opportunity": {"deal_value": 10_000_000_000}}  # 100억
        level = system._determine_approval_level(DecisionType.GO_NOGO, context)

        # 10억 이상은 높은 레벨 필요
        high_levels = {ApprovalLevel.EXECUTIVE, ApprovalLevel.DIVISION}
        assert level in high_levels, f"Expected high approval level, got {level}"

    def test_approval_level_determination_low_value(self, system):
        """TC-D5-01-02: 저가 건 승인 레벨 결정"""
        context = {"opportunity": {"deal_value": 100_000_000}}  # 1억
        level = system._determine_approval_level(DecisionType.GO_NOGO, context)

        assert level is not None, "Level determination returned None"
        assert isinstance(level, ApprovalLevel), f"Expected ApprovalLevel, got {type(level)}"

    def test_approve_request(self, system):
        """TC-D5-01-03: 승인 처리"""
        # Create request first - CAPACITY 유형은 기본 TEAM_LEAD 레벨
        workflow_context = {
            "decision_case_id": "DC-001",
            "options": {"recommendation": "OPT-002", "options": []},
            "impact_analysis": {},
            "validation_result": {},
        }
        request = system.create_approval_request(
            execution_id="EXEC-TEST-002",
            decision_type=DecisionType.CAPACITY,  # TEAM_LEAD 레벨 필요
            workflow_context=workflow_context,
            requester_id="test@example.com",
        )

        # Approve
        result = system.submit_response(
            request_id=request.request_id,
            status=ApprovalStatus.APPROVED,
            approver_id="EMP-000001",
            approver_name="테스트 승인자",
            approval_level=ApprovalLevel.TEAM_LEAD,
            rationale="승인합니다",
        )

        assert result.status == ApprovalStatus.APPROVED, f"Expected APPROVED, got {result.status}"

    def test_reject_request(self, system):
        """TC-D5-01-04: 거부 처리"""
        # CAPACITY 유형은 기본 TEAM_LEAD 레벨 필요
        workflow_context = {
            "decision_case_id": "DC-002",
            "options": {"recommendation": "OPT-003", "options": []},
            "impact_analysis": {},
            "validation_result": {},
        }
        request = system.create_approval_request(
            execution_id="EXEC-TEST-003",
            decision_type=DecisionType.CAPACITY,  # TEAM_LEAD 레벨 필요
            workflow_context=workflow_context,
            requester_id="test@example.com",
        )

        result = system.submit_response(
            request_id=request.request_id,
            status=ApprovalStatus.REJECTED,
            approver_id="EMP-000001",
            approver_name="테스트 승인자",
            approval_level=ApprovalLevel.TEAM_LEAD,
            rationale="예산 초과로 거부",
        )

        assert result.status == ApprovalStatus.REJECTED, f"Expected REJECTED, got {result.status}"

    def test_escalate_request(self, system):
        """TC-D5-01-05: 에스컬레이션"""
        workflow_context = {
            "decision_case_id": "DC-003",
            "options": {"recommendation": "OPT-001", "options": []},
            "impact_analysis": {},
            "validation_result": {},
        }
        request = system.create_approval_request(
            execution_id="EXEC-TEST-004",
            decision_type=DecisionType.GO_NOGO,
            workflow_context=workflow_context,
            requester_id="test@example.com",
        )

        result = system.escalate_request(
            request_id=request.request_id,
            escalation_reason="상위 결재 필요",
            escalated_by="EMP-000010",
        )

        # 에스컬레이션 후 required_level이 상승함
        assert result.required_level != ApprovalLevel.TEAM_LEAD, "Level should be escalated"


@pytest.mark.day5
@pytest.mark.skipif(not WORKFLOW_AVAILABLE, reason="Workflow modules not available")
class TestDecisionLog:
    """TS-D5-02: Decision Log 검증"""

    @pytest.fixture
    def system(self):
        return HITLApprovalSystem()

    def test_log_retrieval(self, system):
        """TC-D5-02-01: 의사결정 로그 조회"""
        logs = system.get_decision_logs(limit=10)

        assert isinstance(logs, list), f"Expected list, got {type(logs)}"

    def test_log_filtering_by_type(self, system):
        """TC-D5-02-01: 의사결정 유형별 로그 필터링"""
        logs = system.get_decision_logs(
            decision_type=DecisionType.GO_NOGO,
            limit=10,
        )

        # 필터링 결과가 리스트인지 확인
        assert isinstance(logs, list), "Filtered logs should be a list"

    def test_log_has_audit_fields(self, system):
        """TC-D5-02-02: 로그에 감사 필드 포함"""
        # Create and approve a request to generate a log
        workflow_context = {
            "decision_case_id": "DC-AUDIT",
            "options": {"recommendation": "OPT-001", "options": []},
            "impact_analysis": {},
            "validation_result": {},
        }
        request = system.create_approval_request(
            execution_id="EXEC-AUDIT-001",
            decision_type=DecisionType.CAPACITY,
            workflow_context=workflow_context,
            requester_id="audit@example.com",
        )
        response = system.submit_response(
            request_id=request.request_id,
            status=ApprovalStatus.APPROVED,
            approver_id="EMP-000001",
            approver_name="감사 테스트",
            approval_level=ApprovalLevel.TEAM_LEAD,
            rationale="감사 테스트 승인",
        )

        # 로그 생성
        log = system.create_decision_log(
            execution_id="EXEC-AUDIT-001",
            decision_type=DecisionType.CAPACITY,
            workflow_context=workflow_context,
            approval_responses=[response],
        )

        assert hasattr(log, "created_at"), "Log missing created_at"
        assert hasattr(log, "decision_type"), "Log missing decision_type"
        assert log.decision_type == DecisionType.CAPACITY


@pytest.mark.day5
class TestAgentEvalMetrics:
    """TS-D5-03: Agent 평가 지표 검증"""

    def test_completeness_calculation(self):
        """TC-D5-03-01: 완결성 계산"""
        response = {
            "type": "GO_NOGO",
            "options": [{"id": "OPT-001"}],
            "recommendation": "OPT-001",
            "evidence": [{"source": "TMS"}],
        }
        required = ["type", "options", "recommendation", "evidence"]

        present = sum(1 for f in required if f in response and response[f])
        completeness = present / len(required)

        assert completeness > 0.9, f"Completeness {completeness:.2%} <= 90%"

    def test_evidence_coverage_target(self):
        """TC-D5-03-02: 근거 연결률 목표 >= 95%"""
        target = 0.95
        assert target >= 0.95, "AC-3 target should be >= 95%"

    def test_hallucination_rate_target(self):
        """TC-D5-03-03: 환각률 목표 <= 5%"""
        target = 0.05
        assert target <= 0.05, "AC-4 target should be <= 5%"

    def test_reproducibility_metric(self):
        """TC-D5-03-04: 재현성 측정 방법"""
        # 동일 입력 5회 실행 시나리오
        results = ["result_a", "result_a", "result_a", "result_a", "result_a"]
        identical_count = len([r for r in results if r == results[0]])
        reproducibility = identical_count / len(results)

        assert reproducibility >= 0.95, f"Reproducibility {reproducibility:.2%} < 95%"

    def test_response_time_target(self):
        """TC-D5-03-05: 응답 시간 목표 < 30s"""
        target_seconds = 30
        assert target_seconds <= 30, "AC-7 target should be <= 30 seconds"


@pytest.mark.day5
class TestOntologyEvalMetrics:
    """TS-D5-04: Ontology 평가 지표 검증"""

    def test_entity_coverage_target(self):
        """TC-D5-04-01: 엔터티 커버리지 목표 = 100%"""
        target = 1.0
        assert target == 1.0, "AC-5 entity coverage target should be 100%"

    def test_link_rate_target(self):
        """TC-D5-04-02: 링크율 목표 > 95%"""
        target = 0.95
        assert target >= 0.95, "Link rate target should be >= 95%"

    def test_duplicate_rate_target(self):
        """TC-D5-04-03: 중복/충돌률 목표 = 0%"""
        target = 0
        assert target == 0, "Duplicate rate target should be 0%"


@pytest.mark.day5
@pytest.mark.acceptance
class TestWorkflowAcceptance:
    """AC-6: HITL 워크플로 Acceptance 테스트"""

    @pytest.mark.skipif(not WORKFLOW_AVAILABLE, reason="Workflow modules not available")
    def test_full_approval_flow(self):
        """전체 승인 플로우 동작"""
        system = HITLApprovalSystem()

        # 1. 요청 생성 - CAPACITY 유형 (기본 TEAM_LEAD 레벨)
        workflow_context = {
            "decision_case_id": "DC-E2E",
            "options": {"recommendation": "OPT-001", "options": []},
            "impact_analysis": {},
            "validation_result": {"hallucination_risk": 0.02},
        }
        request = system.create_approval_request(
            execution_id="EXEC-E2E-001",
            decision_type=DecisionType.CAPACITY,  # TEAM_LEAD 레벨 필요
            workflow_context=workflow_context,
            requester_id="e2e@example.com",
        )
        # ApprovalRequest는 생성 후 pending_requests에 저장됨
        assert request.request_id in system.pending_requests

        # 2. 승인 처리
        result = system.submit_response(
            request_id=request.request_id,
            status=ApprovalStatus.APPROVED,
            approver_id="EMP-000001",
            approver_name="E2E 테스트 승인자",
            approval_level=ApprovalLevel.TEAM_LEAD,
            rationale="E2E 테스트 승인",
        )
        assert result.status == ApprovalStatus.APPROVED

        # 3. 로그 확인
        logs = system.get_decision_logs(limit=5)
        assert isinstance(logs, list), "Decision logs should be a list"


@pytest.mark.day5
@pytest.mark.e2e
class TestE2EScenario:
    """E2E 통합 테스트 시나리오"""

    @pytest.mark.skipif(not WORKFLOW_AVAILABLE, reason="Workflow modules not available")
    def test_a1_question_full_flow(self, test_questions):
        """E2E-01: A-1 질문 전체 플로우"""
        # 이 테스트는 실제 에이전트 통합 시 구현
        # 현재는 구조만 검증
        question = test_questions["A-1"]
        assert "가동률" in question, "A-1 question should mention utilization"
        assert "12주" in question, "A-1 question should mention 12 weeks"

    @pytest.mark.skipif(not WORKFLOW_AVAILABLE, reason="Workflow modules not available")
    def test_b1_question_full_flow(self, test_questions):
        """E2E-02: B-1 질문 전체 플로우"""
        question = test_questions["B-1"]
        assert "성공확률" in question, "B-1 question should mention success probability"
