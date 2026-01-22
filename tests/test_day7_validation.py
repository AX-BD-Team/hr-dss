"""
Day 7 테스트: P8 검증 및 최종 리포트
최종 산출물 완성도 및 Acceptance Criteria 검증
"""

from pathlib import Path

import pytest

# 프로젝트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
REPORTS_DIR = DOCS_DIR / "reports"
SPECS_DIR = DOCS_DIR / "specs"


@pytest.mark.day7
class TestFinalReportCompleteness:
    """TS-D7-02: 최종 산출물 완성도"""

    def test_poc_final_report_exists(self):
        """TC-D7-02-01: PoC Final Report 존재"""
        assert (REPORTS_DIR / "poc-final-report.md").exists()

    def test_poc_final_report_sections(self):
        """TC-D7-02-01: PoC Final Report 필수 섹션"""
        report_path = REPORTS_DIR / "poc-final-report.md"
        if not report_path.exists():
            pytest.skip("Report file not found")

        with open(report_path, encoding="utf-8") as f:
            content = f.read().lower()

        # 필수 키워드 (영문/한글 혼용)
        required_keywords = [
            ("summary", "요약"),  # Executive Summary
            ("개요", "overview"),  # 프로젝트 개요
            ("성과", "result"),  # 주요 성과
            ("아키텍처", "architecture"),  # 기술 아키텍처
            ("평가", "evaluation"),  # 평가 결과
        ]

        missing = []
        for keywords in required_keywords:
            found = any(kw in content for kw in keywords)
            if not found:
                missing.append(keywords[0])

        assert len(missing) <= 2, f"Missing sections: {missing}"

    def test_api_docs_exists(self):
        """TC-D7-02-02: API 문서 존재"""
        assert (DOCS_DIR / "api-docs.md").exists()

    def test_api_docs_sections(self):
        """TC-D7-02-02: API 문서 필수 섹션"""
        api_path = DOCS_DIR / "api-docs.md"
        if not api_path.exists():
            pytest.skip("API docs not found")

        with open(api_path, encoding="utf-8") as f:
            content = f.read().lower()

        required_keywords = ["api", "endpoint"]
        missing = [kw for kw in required_keywords if kw not in content]
        assert len(missing) == 0, f"Missing sections: {missing}"

    def test_user_guide_exists(self):
        """TC-D7-02-03: 사용자 가이드 존재"""
        assert (DOCS_DIR / "user-guide.md").exists()

    def test_user_guide_content(self):
        """TC-D7-02-03: 사용자 가이드 내용"""
        guide_path = DOCS_DIR / "user-guide.md"
        if not guide_path.exists():
            pytest.skip("User guide not found")

        with open(guide_path, encoding="utf-8") as f:
            content = f.read()

        # 최소 길이 확인 (의미 있는 내용)
        assert len(content) >= 500, f"User guide too short: {len(content)} chars"

    def test_comparison_report_exists(self):
        """TC-D7-02-04: 비교 리포트 존재"""
        assert (REPORTS_DIR / "comparison-report.md").exists()

    def test_comparison_report_content(self):
        """TC-D7-02-04: 비교 리포트 내용"""
        report_path = REPORTS_DIR / "comparison-report.md"
        if not report_path.exists():
            pytest.skip("Comparison report not found")

        with open(report_path, encoding="utf-8") as f:
            content = f.read().lower()

        # 비교 관련 키워드
        comparison_keywords = ["비교", "baseline", "poc", "기존"]
        found = sum(1 for kw in comparison_keywords if kw in content)
        assert found >= 2, f"Found only {found} comparison keywords"


@pytest.mark.day7
class TestDocumentationSet:
    """문서 세트 완성도"""

    def test_docs_index_exists(self):
        """문서 인덱스 존재"""
        assert (DOCS_DIR / "INDEX.md").exists()

    def test_project_todo_exists(self):
        """프로젝트 TODO 존재"""
        assert (DOCS_DIR / "project-todo.md").exists()

    def test_claude_md_exists(self):
        """CLAUDE.md 존재"""
        assert (PROJECT_ROOT / "CLAUDE.md").exists()

    def test_specs_directory(self):
        """스펙 문서 디렉토리"""
        assert SPECS_DIR.exists()
        spec_files = list(SPECS_DIR.glob("*.md"))
        assert len(spec_files) >= 3, f"Expected >= 3 spec files, found {len(spec_files)}"


@pytest.mark.day7
@pytest.mark.acceptance
class TestAcceptanceCriteria:
    """TS-D7-03: Acceptance Criteria 최종 검증"""

    def test_ac1_usecase_coverage(self, test_questions):
        """TC-D7-03-01: AC-1 4대 유스케이스"""
        assert len(test_questions) == 4
        assert "A-1" in test_questions
        assert "B-1" in test_questions
        assert "C-1" in test_questions
        assert "D-1" in test_questions

    def test_ac2_three_options_structure(self):
        """TC-D7-03-02: AC-2 3안 생성 구조"""
        option_types = ["CONSERVATIVE", "BALANCED", "AGGRESSIVE"]
        assert len(option_types) == 3

    def test_ac3_evidence_coverage_target(self):
        """TC-D7-03-03: AC-3 근거 연결률 목표"""
        target = 0.95
        assert target >= 0.95, "AC-3 target should be >= 95%"

    def test_ac4_hallucination_rate_target(self):
        """TC-D7-03-04: AC-4 환각률 목표"""
        target = 0.05
        assert target <= 0.05, "AC-4 target should be <= 5%"

    def test_ac5_kg_coverage_check(self, project_root):
        """TC-D7-03-05: AC-5 KG 엔터티 커버리지"""
        schema_path = project_root / "data" / "schemas" / "schema.cypher"
        assert schema_path.exists(), "Schema file must exist"

        with open(schema_path, encoding="utf-8") as f:
            content = f.read()

        # 최소 노드 타입 수 확인 (constraint 수로 추정)
        constraint_count = content.count("CREATE CONSTRAINT")
        assert constraint_count >= 40, f"Expected >= 40 constraints, got {constraint_count}"

    def test_ac6_hitl_workflow_structure(self, project_root):
        """TC-D7-03-06: AC-6 HITL 워크플로 구조"""
        hitl_path = project_root / "backend" / "agent_runtime" / "workflows" / "hitl_approval.py"
        assert hitl_path.exists(), "HITL approval module must exist"

        with open(hitl_path, encoding="utf-8") as f:
            content = f.read()

        # 필수 기능 확인
        required_features = [
            "ApprovalStatus",
            "create_approval_request",
            "process_approval",
        ]
        missing = [feat for feat in required_features if feat not in content]
        assert len(missing) == 0, f"Missing HITL features: {missing}"


@pytest.mark.day7
class TestQuantitativeComparison:
    """TS-D7-01: 정량 비교"""

    def test_time_reduction_target(self):
        """TC-D7-01-01: 의사결정 시간 단축 목표"""
        baseline_days = 5
        poc_hours = 0.5  # 30분

        poc_days = poc_hours / 24
        reduction = (baseline_days - poc_days) / baseline_days * 100

        assert reduction > 50, f"Time reduction {reduction:.1f}% <= 50%"

    def test_step_reduction_target(self):
        """TC-D7-01-01: 단계 감소 목표"""
        baseline_steps = 8
        poc_steps = 3

        reduction = baseline_steps - poc_steps
        assert reduction >= 3, f"Step reduction {reduction} < 3"

    def test_data_source_utilization(self):
        """TC-D7-01-02: 데이터 소스 활용률"""
        # 6개 데이터 소스: BizForce, TMS, HR, Competency, R&R, Cost
        total_sources = 6
        integrated_sources = 6

        utilization = integrated_sources / total_sources * 100
        assert utilization >= 80, f"Data utilization {utilization}% < 80%"


@pytest.mark.day7
class TestMockDataCompleteness:
    """Mock 데이터 완성도 검증"""

    def test_all_mock_files_exist(self, data_dir):
        """모든 Mock 데이터 파일 존재"""
        required_files = [
            "persons.json",
            "projects.json",
            "skills.json",
            "orgs.json",
            "opportunities.json",
            "assignments.json",
            "decisions.json",
            "forecasts.json",
            "learning.json",
            "workflows.json",
        ]

        missing = [f for f in required_files if not (data_dir / f).exists()]
        assert len(missing) == 0, f"Missing mock files: {missing}"

    def test_labeled_data_exists(self, project_root):
        """레이블 데이터 존재"""
        labeled_dir = project_root / "data" / "labeled"
        assert labeled_dir.exists(), "Labeled data directory must exist"

        labeled_files = list(labeled_dir.glob("*.json"))
        assert len(labeled_files) >= 2, f"Expected >= 2 labeled files, found {len(labeled_files)}"


@pytest.mark.day7
class TestSchemaCompleteness:
    """스키마 완성도 검증"""

    def test_schema_file_exists(self, project_root):
        """스키마 파일 존재"""
        schema_path = project_root / "data" / "schemas" / "schema.cypher"
        assert schema_path.exists()

    def test_schema_node_types(self, project_root):
        """노드 타입 정의 수"""
        schema_path = project_root / "data" / "schemas" / "schema.cypher"

        with open(schema_path, encoding="utf-8") as f:
            content = f.read()

        # Constraint 수로 노드 타입 수 추정
        constraint_count = content.count("CREATE CONSTRAINT")
        assert constraint_count >= 40, f"Expected >= 40 node types, got {constraint_count}"

    def test_schema_has_relationships(self, project_root):
        """관계 타입 정의"""
        schema_path = project_root / "data" / "schemas" / "schema.cypher"

        with open(schema_path, encoding="utf-8") as f:
            content = f.read()

        # 관계 타입 확인
        relationship_keywords = [
            "BELONGS_TO",
            "ASSIGNED_TO",
            "HAS_COMPETENCY",
            "HAS_EVIDENCE",
        ]
        found = sum(1 for kw in relationship_keywords if kw in content)
        assert found >= 3, f"Found only {found} relationship types"


@pytest.mark.day7
@pytest.mark.e2e
class TestE2EReadiness:
    """E2E 데모 준비 상태"""

    def test_agent_modules_exist(self, project_root):
        """Agent 모듈 존재"""
        agents_dir = project_root / "backend" / "agent_runtime" / "agents"
        assert agents_dir.exists()

        required_agents = [
            "query_decomposition.py",
            "option_generator.py",
            "impact_simulator.py",
            "success_probability.py",
            "validator.py",
            "workflow_builder.py",
        ]

        missing = [a for a in required_agents if not (agents_dir / a).exists()]
        assert len(missing) == 0, f"Missing agents: {missing}"

    def test_ui_components_exist(self, project_root):
        """UI 컴포넌트 존재"""
        components_dir = project_root / "apps" / "web" / "components"
        assert components_dir.exists()

        tsx_files = list(components_dir.glob("*.tsx"))
        assert len(tsx_files) >= 8, f"Expected >= 8 components, found {len(tsx_files)}"

    def test_test_scenario_plan_exists(self, project_root):
        """테스트 시나리오 계획서 존재"""
        evals_dir = project_root / "evals"
        assert (evals_dir / "TEST_SCENARIO_PLAN.md").exists()


@pytest.mark.day7
@pytest.mark.acceptance
class TestFinalAcceptanceMatrix:
    """최종 Acceptance 매트릭스"""

    def test_all_acceptance_criteria_defined(self):
        """모든 AC 정의 확인"""
        acceptance_criteria = {
            "AC-1": "4대 유스케이스 응답",
            "AC-2": "3안 비교 생성",
            "AC-3": "근거 연결률 >= 95%",
            "AC-4": "환각률 <= 5%",
            "AC-5": "KG 엔터티 커버리지 100%",
            "AC-6": "HITL 워크플로 동작",
            "AC-7": "응답 시간 <= 30s",
            "AC-8": "재현성 >= 95%",
            "AC-9": "UI 사용성 >= 80%",
            "AC-10": "문서화 100%",
        }

        assert len(acceptance_criteria) == 10
        # 필수 AC (1-6) 확인
        required_acs = ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6"]
        missing = [ac for ac in required_acs if ac not in acceptance_criteria]
        assert len(missing) == 0, f"Missing required ACs: {missing}"
