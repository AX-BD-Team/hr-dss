"""
Day 2 테스트: P2 Data Readiness
Mock 데이터 6종의 품질과 스키마 일관성 검증
"""

import re

import pytest


@pytest.mark.day2
class TestMockDataSchema:
    """TS-D2-01: Mock 데이터 스키마 검증"""

    def test_persons_count(self, persons_data):
        """TC-D2-01-01: persons 데이터 수량 (>= 50)"""
        employees = persons_data.get("employees", [])
        assert len(employees) >= 50, f"Expected >= 50 employees, got {len(employees)}"

    def test_persons_required_fields(self, persons_data):
        """TC-D2-01-01: persons 필수 필드 검증"""
        required = ["employeeId", "name", "orgUnitId", "jobRoleId"]
        for emp in persons_data.get("employees", []):
            for field in required:
                assert field in emp, f"Missing field '{field}' in employee {emp.get('employeeId', 'unknown')}"

    def test_persons_id_format(self, persons_data):
        """TC-D2-01-01: employeeId 형식 검증 (EMP-XXXXXX)"""
        pattern = re.compile(r"^EMP-\d{6}$")
        for emp in persons_data.get("employees", []):
            emp_id = emp.get("employeeId", "")
            assert pattern.match(emp_id), f"Invalid employeeId format: {emp_id}"

    def test_projects_count(self, projects_data):
        """TC-D2-01-02: projects 데이터 수량 (>= 10)"""
        projects = projects_data.get("projects", [])
        assert len(projects) >= 10, f"Expected >= 10 projects, got {len(projects)}"

    def test_projects_required_fields(self, projects_data):
        """TC-D2-01-02: projects 필수 필드 검증"""
        required = ["projectId", "name", "status", "startDate"]
        for proj in projects_data.get("projects", []):
            for field in required:
                assert field in proj, f"Missing field '{field}' in project {proj.get('projectId', 'unknown')}"

    def test_projects_status_enum(self, projects_data):
        """TC-D2-01-02: projects status ENUM 검증"""
        valid_statuses = {"ACTIVE", "COMPLETED", "PLANNED", "ON_HOLD"}
        for proj in projects_data.get("projects", []):
            status = proj.get("status", "")
            assert status in valid_statuses, f"Invalid status '{status}' in project {proj.get('projectId')}"

    def test_skills_count(self, skills_data):
        """TC-D2-01-03: skills 역량 데이터 수량 (>= 40)"""
        competencies = skills_data.get("competencies", [])
        assert len(competencies) >= 40, f"Expected >= 40 competencies, got {len(competencies)}"

    def test_skills_required_fields(self, skills_data):
        """TC-D2-01-03: skills 필수 필드 검증"""
        required = ["competencyId", "name", "category"]
        for comp in skills_data.get("competencies", []):
            for field in required:
                assert field in comp, f"Missing field '{field}' in competency {comp.get('competencyId', 'unknown')}"

    def test_orgs_count(self, orgs_data):
        """TC-D2-01-04: orgs 데이터 수량 (>= 20)"""
        org_units = orgs_data.get("orgUnits", [])
        assert len(org_units) >= 20, f"Expected >= 20 orgUnits, got {len(org_units)}"

    def test_orgs_required_fields(self, orgs_data):
        """TC-D2-01-04: orgs 필수 필드 검증"""
        required = ["orgUnitId", "name"]
        for org in orgs_data.get("orgUnits", []):
            for field in required:
                assert field in org, f"Missing field '{field}' in orgUnit {org.get('orgUnitId', 'unknown')}"

    def test_opportunities_count(self, opportunities_data):
        """TC-D2-01-05: opportunities 데이터 수량 (>= 10)"""
        opportunities = opportunities_data.get("opportunities", [])
        assert len(opportunities) >= 10, f"Expected >= 10 opportunities, got {len(opportunities)}"

    def test_opportunities_required_fields(self, opportunities_data):
        """TC-D2-01-05: opportunities 필수 필드 검증"""
        required = ["opportunityId", "name", "dealValue", "stage"]
        for opp in opportunities_data.get("opportunities", []):
            for field in required:
                assert field in opp, f"Missing field '{field}' in opportunity {opp.get('opportunityId', 'unknown')}"

    def test_assignments_count(self, assignments_data):
        """TC-D2-01-06: assignments 데이터 수량 (>= 30)"""
        assignments = assignments_data.get("assignments", [])
        assert len(assignments) >= 30, f"Expected >= 30 assignments, got {len(assignments)}"

    def test_assignments_required_fields(self, assignments_data):
        """TC-D2-01-06: assignments 필수 필드 검증"""
        required = ["assignmentId", "employeeId", "projectId", "allocationFTE"]
        for asn in assignments_data.get("assignments", []):
            for field in required:
                assert field in asn, f"Missing field '{field}' in assignment {asn.get('assignmentId', 'unknown')}"


@pytest.mark.day2
class TestJoinKeyIntegrity:
    """TS-D2-02: Join Key 연결성 검증"""

    def test_employee_org_link(self, persons_data, orgs_data):
        """TC-D2-02-02: employeeId → orgUnitId 연결 검증"""
        org_ids = {org["orgUnitId"] for org in orgs_data.get("orgUnits", [])}

        orphan_count = 0
        for emp in persons_data.get("employees", []):
            if emp.get("orgUnitId") not in org_ids:
                orphan_count += 1

        total = len(persons_data.get("employees", []))
        match_rate = (total - orphan_count) / total if total > 0 else 0
        assert match_rate >= 0.95, f"Employee-Org match rate {match_rate:.2%} < 95%"

    def test_assignment_employee_link(self, assignments_data, persons_data):
        """TC-D2-02-01: assignment → employeeId 연결 검증"""
        emp_ids = {emp["employeeId"] for emp in persons_data.get("employees", [])}

        orphan_count = 0
        for asn in assignments_data.get("assignments", []):
            if asn.get("employeeId") not in emp_ids:
                orphan_count += 1

        total = len(assignments_data.get("assignments", []))
        match_rate = (total - orphan_count) / total if total > 0 else 0
        assert match_rate >= 0.95, f"Assignment-Employee match rate {match_rate:.2%} < 95%"

    def test_assignment_project_link(self, assignments_data, projects_data):
        """TC-D2-02-03: assignment → projectId 연결 검증"""
        proj_ids = {proj["projectId"] for proj in projects_data.get("projects", [])}

        orphan_count = 0
        for asn in assignments_data.get("assignments", []):
            if asn.get("projectId") not in proj_ids:
                orphan_count += 1

        total = len(assignments_data.get("assignments", []))
        match_rate = (total - orphan_count) / total if total > 0 else 0
        assert match_rate >= 0.95, f"Assignment-Project match rate {match_rate:.2%} < 95%"


@pytest.mark.day2
class TestDataQualityMetrics:
    """TS-D2-03: Data Quality 지표 검증"""

    def test_persons_missing_rate(self, persons_data):
        """TC-D2-03-01: persons 결측률 < 10%"""
        required_fields = ["employeeId", "name", "orgUnitId"]
        employees = persons_data.get("employees", [])

        total_fields = len(employees) * len(required_fields)
        missing_count = 0

        for emp in employees:
            for field in required_fields:
                if not emp.get(field):
                    missing_count += 1

        missing_rate = missing_count / total_fields if total_fields > 0 else 0
        assert missing_rate < 0.10, f"Missing rate {missing_rate:.2%} >= 10%"

    def test_no_duplicate_employee_ids(self, persons_data):
        """TC-D2-03-02: employeeId 중복률 < 1%"""
        employees = persons_data.get("employees", [])
        emp_ids = [emp.get("employeeId") for emp in employees]

        unique_count = len(set(emp_ids))
        duplicate_rate = 1 - (unique_count / len(emp_ids)) if emp_ids else 0

        assert duplicate_rate < 0.01, f"Duplicate rate {duplicate_rate:.2%} >= 1%"

    def test_no_duplicate_project_ids(self, projects_data):
        """TC-D2-03-02: projectId 중복률 < 1%"""
        projects = projects_data.get("projects", [])
        proj_ids = [proj.get("projectId") for proj in projects]

        unique_count = len(set(proj_ids))
        duplicate_rate = 1 - (unique_count / len(proj_ids)) if proj_ids else 0

        assert duplicate_rate < 0.01, f"Duplicate rate {duplicate_rate:.2%} >= 1%"


@pytest.mark.day2
@pytest.mark.acceptance
class TestDataReadinessAcceptance:
    """Data Readiness Acceptance 테스트"""

    def test_mock_data_complete(self, all_mock_data):
        """모든 Mock 데이터 파일 존재 확인"""
        required_files = ["persons", "projects", "skills", "orgs", "opportunities", "assignments"]

        for file_key in required_files:
            assert file_key in all_mock_data, f"Missing mock data file: {file_key}"
            assert all_mock_data[file_key], f"Empty mock data: {file_key}"
