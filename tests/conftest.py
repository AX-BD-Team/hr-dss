"""
HR DSS 테스트 공통 설정 및 Fixtures
"""

import json
from pathlib import Path

import pytest

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "mock"


@pytest.fixture(scope="session")
def project_root() -> Path:
    """프로젝트 루트 경로"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Mock 데이터 디렉토리"""
    return DATA_DIR


@pytest.fixture(scope="session")
def persons_data():
    """persons.json 데이터"""
    with open(DATA_DIR / "persons.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def projects_data():
    """projects.json 데이터"""
    with open(DATA_DIR / "projects.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def skills_data():
    """skills.json 데이터"""
    with open(DATA_DIR / "skills.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def orgs_data():
    """orgs.json 데이터"""
    with open(DATA_DIR / "orgs.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def opportunities_data():
    """opportunities.json 데이터"""
    with open(DATA_DIR / "opportunities.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def assignments_data():
    """assignments.json 데이터"""
    with open(DATA_DIR / "assignments.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def decisions_data():
    """decisions.json 데이터"""
    with open(DATA_DIR / "decisions.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def forecasts_data():
    """forecasts.json 데이터"""
    with open(DATA_DIR / "forecasts.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def learning_data():
    """learning.json 데이터"""
    with open(DATA_DIR / "learning.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def workflows_data():
    """workflows.json 데이터"""
    with open(DATA_DIR / "workflows.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def all_mock_data(
    persons_data,
    projects_data,
    skills_data,
    orgs_data,
    opportunities_data,
    assignments_data,
    decisions_data,
    forecasts_data,
    learning_data,
    workflows_data,
):
    """모든 Mock 데이터"""
    return {
        "persons": persons_data,
        "projects": projects_data,
        "skills": skills_data,
        "orgs": orgs_data,
        "opportunities": opportunities_data,
        "assignments": assignments_data,
        "decisions": decisions_data,
        "forecasts": forecasts_data,
        "learning": learning_data,
        "workflows": workflows_data,
    }


# 테스트 질문 데이터
TEST_QUESTIONS = {
    "A-1": "향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘",
    "B-1": "'100억 미디어 AX' 프로젝트를 내부 수행 가능한지, 성공확률은 얼마인지 알려줘",
    "C-1": "데이터플랫폼팀 1명 증원 요청의 원인을 분해해줘",
    "D-1": "AI-driven 전환 관점에서 역량 갭 Top10을 정량화해줘",
}


@pytest.fixture
def test_questions():
    """테스트용 4대 질문"""
    return TEST_QUESTIONS


# pytest 마커 등록
def pytest_configure(config):
    config.addinivalue_line("markers", "day2: Day 2 Data Readiness 테스트")
    config.addinivalue_line("markers", "day3: Day 3 KG 테스트")
    config.addinivalue_line("markers", "day4: Day 4 Agent 테스트")
    config.addinivalue_line("markers", "day5: Day 5 Workflow 테스트")
    config.addinivalue_line("markers", "acceptance: Acceptance Criteria 테스트")
    config.addinivalue_line("markers", "e2e: E2E 통합 테스트")
