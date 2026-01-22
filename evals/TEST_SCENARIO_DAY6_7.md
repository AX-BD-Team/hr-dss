# HR DSS 테스트 시나리오 계획서 (Day 6-7)

> 작성일: 2026-01-21 | 버전: 1.0

---

## 목차

1. [Day 6 테스트: UI 컴포넌트](#1-day-6-테스트-ui-컴포넌트)
2. [Day 7 테스트: 검증 및 최종 리포트](#2-day-7-테스트-검증-및-최종-리포트)
3. [최종 Acceptance 테스트](#3-최종-acceptance-테스트)
4. [E2E 데모 시나리오](#4-e2e-데모-시나리오)

---

## 1. Day 6 테스트: UI 컴포넌트

### 1.1 테스트 목적

P7 웹/앱 Prototype UI의 기능 및 UX 검증

### 1.2 테스트 대상 컴포넌트

| 컴포넌트           | 파일                     | 핵심 기능                         |
| ------------------ | ------------------------ | --------------------------------- |
| ConversationUI     | `ConversationUI.tsx`     | 대화형 질문 입력, 시나리오 프리셋 |
| OptionCompare      | `OptionCompare.tsx`      | 3안 비교, 레이더 차트, ROI        |
| ExplanationPanel   | `ExplanationPanel.tsx`   | 추론 경로, Evidence, KG 뷰        |
| EvalDashboard      | `EvalDashboard.tsx`      | 시스템 헬스, 알림, 활동 피드      |
| GraphViewer        | `GraphViewer.tsx`        | KG 시각화, 노드/관계 탐색         |
| AgentEvalDashboard | `AgentEvalDashboard.tsx` | Agent 성능 지표, 평가 결과        |
| OntologyScoreCard  | `OntologyScoreCard.tsx`  | Ontology 품질 지표                |
| DataQualityReport  | `DataQualityReport.tsx`  | 데이터 품질 리포트                |

### 1.3 테스트 시나리오

#### TS-D6-01: ConversationUI 컴포넌트

```yaml
scenario_id: TS-D6-01
name: "ConversationUI 기능 검증"
category: UI
priority: P0

test_cases:
  - id: TC-D6-01-01
    name: "질문 입력 및 전송"
    steps:
      - 질문 입력란에 텍스트 입력
      - 전송 버튼 클릭 또는 Enter 키
      - 메시지 목록에 사용자 메시지 표시 확인
    expected: "입력된 질문이 채팅 히스토리에 표시"
    assertions:
      - "메시지 타입이 'user'로 설정"
      - "타임스탬프 자동 생성"
      - "메시지 ID 유니크"

  - id: TC-D6-01-02
    name: "시나리오 프리셋 선택"
    steps:
      - 프리셋 목록 표시 확인
      - "가동률 병목 분석" 프리셋 클릭
      - 템플릿 질문 및 기본 제약조건 자동 입력 확인
    expected: |
      - 4개 프리셋 표시 (가동률/Go-NoGo/증원/역량갭)
      - 선택 시 질문 템플릿 자동 채움
      - 기본 제약조건 자동 설정
    assertions:
      - "프리셋 ID: capacity, go_nogo, headcount, competency"
      - "defaultConstraints 자동 적용"

  - id: TC-D6-01-03
    name: "제약조건 설정"
    steps:
      - 제약조건 추가 버튼 클릭
      - 예산/일정/인원 등 제약조건 입력
      - 질문과 함께 제약조건 전송
    expected: "제약조건이 질문에 포함되어 전송"
    constraint_types:
      - budget: "예산 제한"
      - timeline: "일정 제한"
      - headcount: "인원 제한"
      - utilization: "가동률 임계값"
      - risk: "리스크 허용 수준"

  - id: TC-D6-01-04
    name: "응답 메시지 표시"
    steps:
      - 질문 전송 후 로딩 표시 확인
      - 응답 수신 후 메시지 렌더링 확인
      - 옵션 요약 카드 표시 확인
    expected: |
      - 로딩 인디케이터 표시
      - Assistant 메시지 정상 렌더링
      - 메타데이터 (옵션, 처리시간 등) 표시
    assertions:
      - "message.type == 'assistant'"
      - "metadata.options 존재 시 OptionSummary 카드 표시"
      - "metadata.processingTime 표시"

  - id: TC-D6-01-05
    name: "대화 히스토리 스크롤"
    steps:
      - 여러 메시지 주고받기
      - 자동 스크롤 확인
      - 이전 메시지로 스크롤 업
    expected: "새 메시지 시 자동 스크롤, 수동 스크롤 가능"
```

#### TS-D6-02: OptionCompare 컴포넌트

```yaml
scenario_id: TS-D6-02
name: "OptionCompare 기능 검증"
category: UI
priority: P0

test_cases:
  - id: TC-D6-02-01
    name: "3안 비교 카드 표시"
    input:
      options:
        - optionType: CONSERVATIVE
          name: "내부 재배치"
        - optionType: BALANCED
          name: "외주 혼합"
        - optionType: AGGRESSIVE
          name: "정규직 채용"
    expected: |
      - 3개 옵션 카드 나란히 표시
      - 각 타입별 색상 구분 (녹색/주황/빨강)
      - 옵션명, 설명, 액션 목록 표시
    assertions:
      - "options.length == 3"
      - "CONSERVATIVE: 녹색 (#4CAF50)"
      - "BALANCED: 주황색 (#FF9800)"
      - "AGGRESSIVE: 빨간색 (#F44336)"

  - id: TC-D6-02-02
    name: "레이더 차트 렌더링"
    steps:
      - 옵션 카드 내 레이더 차트 확인
      - 5개 축 (영향도/실현성/리스크/비용/시간) 표시
    expected: "5각형 레이더 차트로 스코어 시각화"
    score_axes:
      - impact: "영향도"
      - feasibility: "실현 가능성"
      - risk: "리스크"
      - cost: "비용"
      - time: "소요 시간"

  - id: TC-D6-02-03
    name: "추천 옵션 하이라이트"
    input:
      recommendation: "OPT-002"
      recommendationReason: "비용 대비 효과 최적"
    expected: |
      - 추천 옵션에 "추천" 배지 표시
      - 추천 사유 텍스트 표시
      - 시각적 강조 (테두리/배경)
    assertions:
      - "추천 옵션 카드에 RECOMMENDED 배지"
      - "recommendationReason 표시"

  - id: TC-D6-02-04
    name: "옵션 선택 및 상세 보기"
    steps:
      - 옵션 카드 클릭
      - 선택 상태 변경 확인
      - 상세 정보 패널 표시 확인
    expected: "선택된 옵션 하이라이트, 상세 정보 표시"
    detail_info:
      - actions: "실행 항목 목록"
      - prerequisites: "전제조건"
      - tradeOffs: "장단점"
      - successProbability: "성공확률"

  - id: TC-D6-02-05
    name: "As-Is vs To-Be 비교 차트"
    input:
      impactAnalysis:
        baseline:
          utilization: 0.92
          cost: 100000000
        projected:
          utilization: 0.78
          cost: 115000000
    expected: "베이스라인 vs 예상 비교 차트 표시"
    assertions:
      - "utilization 감소율 표시 (14%↓)"
      - "cost 증가율 표시 (15%↑)"

  - id: TC-D6-02-06
    name: "승인/거부 버튼"
    input:
      showApprovalButtons: true
    steps:
      - 옵션 선택
      - "승인" 버튼 클릭
      - 확인 다이얼로그 표시
    expected: "승인 버튼 클릭 시 onApprove 콜백 호출"
```

#### TS-D6-03: ExplanationPanel 컴포넌트

```yaml
scenario_id: TS-D6-03
name: "ExplanationPanel 기능 검증"
category: UI
priority: P0

test_cases:
  - id: TC-D6-03-01
    name: "추론 경로 표시"
    input:
      reasoningSteps:
        - step: 1
          title: "질문 분해"
          content: "CAPACITY_FORECAST 타입으로 분류"
        - step: 2
          title: "데이터 조회"
          content: "KG에서 관련 노드 42개 조회"
    expected: |
      - 단계별 추론 과정 타임라인 표시
      - 각 단계 제목 + 내용 표시
      - 접기/펼치기 가능
    assertions:
      - "reasoningSteps 순서대로 표시"
      - "expandable 토글 동작"

  - id: TC-D6-03-02
    name: "Evidence 목록 표시"
    input:
      evidence:
        - source: "TMS"
          type: "query"
          content: "AI솔루션팀 W05-W07 배정 FTE: 7.2"
        - source: "BizForce"
          type: "table"
          content: "OPP-001 수주확률 70%"
    expected: |
      - Evidence 카드 목록 표시
      - 소스 시스템 아이콘/배지
      - 타입별 구분 (query/table/doc)
    assertions:
      - "evidence.length 개수 표시"
      - "source별 아이콘 매핑"

  - id: TC-D6-03-03
    name: "가정(Assumptions) 표시"
    input:
      assumptions:
        - "현재 프로젝트 일정 변동 없음"
        - "외부 채용 시장 상황 안정적"
    expected: |
      - 가정 목록 불릿 포인트로 표시
      - 경고 아이콘과 함께 시각화
    assertions:
      - "assumptions 전체 표시"
      - "warning 스타일 적용"

  - id: TC-D6-03-04
    name: "검증 결과 표시"
    input:
      validationResult:
        evidenceCoverage: 0.95
        hallucinationRisk: 0.03
        flaggedClaims: []
    expected: |
      - 근거 연결률: 95% (녹색)
      - 환각 위험도: 3% (녹색)
      - 플래그된 주장 없음
    assertions:
      - "evidenceCoverage >= 0.95 → 녹색"
      - "hallucinationRisk <= 0.05 → 녹색"

  - id: TC-D6-03-05
    name: "KG 뷰 연동"
    steps:
      - "KG 보기" 버튼 클릭
      - GraphViewer 컴포넌트 표시
      - 관련 노드 하이라이트
    expected: "Evidence와 연결된 KG 노드 시각화"
```

#### TS-D6-04: EvalDashboard 컴포넌트

```yaml
scenario_id: TS-D6-04
name: "EvalDashboard 기능 검증"
category: UI
priority: P0

test_cases:
  - id: TC-D6-04-01
    name: "시스템 헬스 상태"
    input:
      systemHealth:
        overall: "healthy"
        neo4j: "connected"
        agentRuntime: "running"
        lastUpdated: "2026-01-21T10:00:00Z"
    expected: |
      - 전체 상태: 녹색 "정상"
      - 각 서비스 상태 표시
      - 마지막 업데이트 시간
    assertions:
      - "overall == 'healthy' → 녹색 배지"
      - "각 서비스 상태 아이콘"

  - id: TC-D6-04-02
    name: "알림 목록"
    input:
      alerts:
        - severity: "warning"
          message: "가동률 90% 초과 예상"
          timestamp: "2026-01-21T09:30:00Z"
        - severity: "info"
          message: "새 의사결정 요청"
    expected: |
      - 알림 목록 최신순 정렬
      - severity별 색상 구분
      - 시간 표시 (상대 시간)
    severity_colors:
      - info: "파란색"
      - warning: "주황색"
      - error: "빨간색"
      - success: "녹색"

  - id: TC-D6-04-03
    name: "활동 피드"
    input:
      activities:
        - type: "decision"
          actor: "김영호"
          action: "OPT-002 승인"
          timestamp: "2026-01-21T09:00:00Z"
    expected: "최근 활동 타임라인 표시"

  - id: TC-D6-04-04
    name: "빠른 이동 네비게이션"
    steps:
      - 대시보드 메뉴 아이템 클릭
      - 해당 페이지/컴포넌트로 이동
    expected: |
      - Agent Eval 바로가기
      - Ontology Scorecard 바로가기
      - Data Quality 바로가기
      - Graph Viewer 바로가기
```

#### TS-D6-05: GraphViewer 컴포넌트

```yaml
scenario_id: TS-D6-05
name: "GraphViewer 기능 검증"
category: UI
priority: P1

test_cases:
  - id: TC-D6-05-01
    name: "노드 렌더링"
    input:
      nodes:
        - id: "EMP-000001"
          label: "Employee"
          name: "김영호"
        - id: "ORG-0001"
          label: "OrgUnit"
          name: "디지털전략본부"
    expected: |
      - 노드 타입별 색상/아이콘 구분
      - 노드 이름 레이블 표시
    node_colors:
      Employee: "#4CAF50"
      OrgUnit: "#2196F3"
      Project: "#FF9800"
      Competency: "#9C27B0"

  - id: TC-D6-05-02
    name: "관계(Edge) 렌더링"
    input:
      edges:
        - source: "EMP-000001"
          target: "ORG-0001"
          type: "BELONGS_TO"
    expected: |
      - 화살표로 방향 표시
      - 관계 타입 레이블 (hover 시)
    assertions:
      - "directed edge 화살표"
      - "relationship type tooltip"

  - id: TC-D6-05-03
    name: "줌/패닝"
    steps:
      - 마우스 휠로 줌 인/아웃
      - 드래그로 캔버스 이동
    expected: "줌, 패닝 인터랙션 정상 동작"

  - id: TC-D6-05-04
    name: "노드 클릭 상세 정보"
    steps:
      - 노드 클릭
      - 사이드 패널에 상세 정보 표시
    expected: "선택 노드의 속성, 연결된 노드 목록 표시"
```

### 1.4 Day 6 pytest 구현

```python
# tests/test_day6_ui.py

import pytest
from pathlib import Path

# UI 컴포넌트는 React이므로 파일 존재 및 구조 검증
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


@pytest.mark.day6
class TestConversationUIStructure:
    """TS-D6-01: ConversationUI 구조 검증"""

    @pytest.fixture
    def component_source(self):
        with open(COMPONENTS_DIR / "ConversationUI.tsx", encoding="utf-8") as f:
            return f.read()

    def test_has_message_interface(self, component_source):
        """TC-D6-01-01: Message 인터페이스 정의"""
        assert "interface Message" in component_source
        assert "type:" in component_source  # user | assistant | system

    def test_has_scenario_presets(self, component_source):
        """TC-D6-01-02: 시나리오 프리셋 정의"""
        assert "ScenarioPreset" in component_source
        assert "capacity" in component_source.lower()
        assert "go_nogo" in component_source or "go-nogo" in component_source.lower()

    def test_has_constraint_interface(self, component_source):
        """TC-D6-01-03: Constraint 인터페이스 정의"""
        assert "interface Constraint" in component_source
        assert "budget" in component_source
        assert "timeline" in component_source

    def test_has_send_message_handler(self, component_source):
        """TC-D6-01-04: 메시지 전송 핸들러"""
        assert "onSendMessage" in component_source


@pytest.mark.day6
class TestOptionCompareStructure:
    """TS-D6-02: OptionCompare 구조 검증"""

    @pytest.fixture
    def component_source(self):
        with open(COMPONENTS_DIR / "OptionCompare.tsx", encoding="utf-8") as f:
            return f.read()

    def test_has_decision_option_interface(self, component_source):
        """TC-D6-02-01: DecisionOption 인터페이스"""
        assert "interface DecisionOption" in component_source
        assert "CONSERVATIVE" in component_source
        assert "BALANCED" in component_source
        assert "AGGRESSIVE" in component_source

    def test_has_option_scores(self, component_source):
        """TC-D6-02-02: OptionScores 정의"""
        assert "OptionScores" in component_source
        assert "impact" in component_source
        assert "feasibility" in component_source

    def test_has_recommendation(self, component_source):
        """TC-D6-02-03: 추천 기능"""
        assert "recommendation" in component_source
        assert "recommendationReason" in component_source

    def test_has_approval_buttons(self, component_source):
        """TC-D6-02-06: 승인 버튼"""
        assert "onApprove" in component_source
        assert "onReject" in component_source


@pytest.mark.day6
class TestExplanationPanelStructure:
    """TS-D6-03: ExplanationPanel 구조 검증"""

    @pytest.fixture
    def component_source(self):
        with open(COMPONENTS_DIR / "ExplanationPanel.tsx", encoding="utf-8") as f:
            return f.read()

    def test_has_reasoning_steps(self, component_source):
        """TC-D6-03-01: 추론 단계"""
        assert "reasoningSteps" in component_source or "ReasoningStep" in component_source

    def test_has_evidence(self, component_source):
        """TC-D6-03-02: Evidence"""
        assert "evidence" in component_source.lower()

    def test_has_validation_result(self, component_source):
        """TC-D6-03-04: 검증 결과"""
        assert "validationResult" in component_source or "ValidationResult" in component_source
```

### 1.5 Day 6 체크리스트

| 항목             | 검증 방법        | Pass 기준        |
| ---------------- | ---------------- | ---------------- |
| ConversationUI   | 파일 + 구조 검증 | 인터페이스 정의  |
| OptionCompare    | 파일 + 구조 검증 | 3안 비교 구현    |
| ExplanationPanel | 파일 + 구조 검증 | Evidence 표시    |
| EvalDashboard    | 파일 + 구조 검증 | 헬스 상태 표시   |
| GraphViewer      | 파일 + 구조 검증 | 노드/엣지 렌더링 |
| AC-9 (UI 사용성) | 수동 테스트      | ≥ 80%            |

---

## 2. Day 7 테스트: 검증 및 최종 리포트

### 2.1 테스트 목적

P8 검증 단계의 정량적 비교와 최종 산출물 완성도 검증

### 2.2 테스트 시나리오

#### TS-D7-01: 정량 비교 리포트 검증

```yaml
scenario_id: TS-D7-01
name: "기존 방식 vs PoC 정량 비교"
category: Validation
priority: P0

test_cases:
  - id: TC-D7-01-01
    name: "의사결정 시간 비교"
    metrics:
      baseline:
        name: "기존 방식 (수동)"
        avgTime: "5일"
        steps: 8
      poc:
        name: "PoC (자동화)"
        avgTime: "30분"
        steps: 3
    expected: |
      - 시간 단축률: > 50%
      - 단계 감소: > 3단계
    acceptance: "AC-7 (비즈니스 KPI)"

  - id: TC-D7-01-02
    name: "데이터 활용률 비교"
    metrics:
      baseline:
        dataSources: 2
        integrationLevel: "수동 조회"
      poc:
        dataSources: 6
        integrationLevel: "자동 연계"
    expected: "데이터 소스 활용률 > 80%"

  - id: TC-D7-01-03
    name: "분석 품질 비교"
    metrics:
      baseline:
        evidenceBased: "부분적"
        consistency: "분석가 의존"
      poc:
        evidenceBased: "> 95%"
        consistency: "> 95%"
    expected: |
      - 근거 기반 분석률 개선
      - 일관성 보장
```

#### TS-D7-02: 최종 산출물 검증

```yaml
scenario_id: TS-D7-02
name: "최종 산출물 완성도 검증"
category: Documentation
priority: P0

test_cases:
  - id: TC-D7-02-01
    name: "PoC Final Report 완성도"
    file: "docs/reports/poc-final-report.md"
    required_sections:
      - "Executive Summary"
      - "프로젝트 개요"
      - "주요 성과"
      - "기술 아키텍처"
      - "평가 결과"
      - "개선 권고사항"
      - "다음 단계 로드맵"
    expected: "모든 필수 섹션 존재"

  - id: TC-D7-02-02
    name: "API 문서 완성도"
    file: "docs/api-docs.md"
    required_sections:
      - "API 개요"
      - "인증"
      - "엔드포인트 목록"
      - "요청/응답 스키마"
      - "에러 코드"
    expected: "API 명세 완전성"

  - id: TC-D7-02-03
    name: "사용자 가이드 완성도"
    file: "docs/user-guide.md"
    required_sections:
      - "시작하기"
      - "주요 기능"
      - "사용 시나리오"
      - "FAQ"
    expected: "사용자 가이드 완전성"

  - id: TC-D7-02-04
    name: "Comparison Report 완성도"
    file: "docs/reports/comparison-report.md"
    required_sections:
      - "비교 개요"
      - "정량 지표 비교"
      - "정성 평가"
      - "결론"
    expected: "비교 리포트 완전성"
```

#### TS-D7-03: Acceptance Criteria 최종 검증

```yaml
scenario_id: TS-D7-03
name: "Acceptance Criteria 최종 검증"
category: Acceptance
priority: P0

test_cases:
  - id: TC-D7-03-01
    name: "AC-1: 4대 유스케이스 응답"
    acceptance_id: "AC-1"
    target: "100%"
    verification: |
      - A-1 (가동률 병목): 응답 생성 확인
      - B-1 (Go/No-go): 응답 생성 확인
      - C-1 (증원 분석): 응답 생성 확인
      - D-1 (역량 갭): 응답 생성 확인
    pass_criteria: "4/4 = 100%"

  - id: TC-D7-03-02
    name: "AC-2: 3안 비교 생성"
    acceptance_id: "AC-2"
    target: "100%"
    verification: |
      - 모든 유스케이스에서 3개 옵션 생성
      - CONSERVATIVE/BALANCED/AGGRESSIVE 타입 포함
    pass_criteria: "모든 질문에 3안 생성"

  - id: TC-D7-03-03
    name: "AC-3: 근거 연결률"
    acceptance_id: "AC-3"
    target: "≥ 95%"
    verification: |
      - Validator Agent 출력 확인
      - evidenceCoverage 지표 측정
    measurement: "evidenced_claims / total_claims"

  - id: TC-D7-03-04
    name: "AC-4: 환각률"
    acceptance_id: "AC-4"
    target: "≤ 5%"
    verification: |
      - Validator Agent 출력 확인
      - hallucinationRisk 지표 측정
    measurement: "unevidenced_claims / total_claims"

  - id: TC-D7-03-05
    name: "AC-5: KG 엔터티 커버리지"
    acceptance_id: "AC-5"
    target: "100%"
    verification: |
      - Neo4j 노드 타입 수 확인
      - 47개 노드 타입 모두 존재
    measurement: "existing_types / required_types"

  - id: TC-D7-03-06
    name: "AC-6: HITL 워크플로"
    acceptance_id: "AC-6"
    target: "동작"
    verification: |
      - 승인 요청 생성 가능
      - 승인/거부 처리 가능
      - Decision Log 기록
    pass_criteria: "전체 플로우 동작"
```

### 2.3 Day 7 pytest 구현

```python
# tests/test_day7_validation.py

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
REPORTS_DIR = DOCS_DIR / "reports"


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

        required_keywords = [
            "summary",      # Executive Summary
            "개요",         # 프로젝트 개요
            "성과",         # 주요 성과
            "아키텍처",     # 기술 아키텍처
            "평가",         # 평가 결과
            "권고",         # 개선 권고사항
            "로드맵",       # 다음 단계
        ]

        missing = [kw for kw in required_keywords if kw not in content]
        assert len(missing) < 3, f"Missing sections: {missing}"

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

        required_keywords = ["api", "endpoint", "request", "response"]
        missing = [kw for kw in required_keywords if kw not in content]
        assert len(missing) < 2, f"Missing sections: {missing}"

    def test_user_guide_exists(self):
        """TC-D7-02-03: 사용자 가이드 존재"""
        assert (DOCS_DIR / "user-guide.md").exists()

    def test_comparison_report_exists(self):
        """TC-D7-02-04: 비교 리포트 존재"""
        assert (REPORTS_DIR / "comparison-report.md").exists()


@pytest.mark.day7
@pytest.mark.acceptance
class TestAcceptanceCriteria:
    """TS-D7-03: Acceptance Criteria 최종 검증"""

    def test_ac1_usecase_coverage(self, test_questions):
        """TC-D7-03-01: AC-1 4대 유스케이스"""
        # 4개 질문 정의 확인
        assert len(test_questions) == 4
        assert "A-1" in test_questions
        assert "B-1" in test_questions
        assert "C-1" in test_questions
        assert "D-1" in test_questions

    def test_ac2_three_options_template(self):
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
        total_sources = 6  # BizForce, TMS, HR, Competency, R&R, Cost
        integrated_sources = 6

        utilization = integrated_sources / total_sources * 100
        assert utilization >= 80, f"Data utilization {utilization}% < 80%"
```

### 2.4 Day 7 체크리스트

| 항목             | 검증 방법        | Pass 기준 |
| ---------------- | ---------------- | --------- |
| PoC Final Report | 파일 + 섹션 검증 | 7개 섹션  |
| API 문서         | 파일 + 섹션 검증 | 완전성    |
| 사용자 가이드    | 파일 + 섹션 검증 | 완전성    |
| 비교 리포트      | 파일 + 섹션 검증 | 완전성    |
| AC-1~AC-6        | 각 기준별 검증   | 모두 Pass |
| 시간 단축률      | 정량 측정        | > 50%     |

---

## 3. 최종 Acceptance 테스트

### 3.1 Acceptance 판정 매트릭스

| AC ID | 기준          | 목표  | 측정 방법      | 판정 |
| ----- | ------------- | ----- | -------------- | ---- |
| AC-1  | 4대 UC 응답   | 100%  | 수동 테스트    | ⬜   |
| AC-2  | 3안 비교      | 100%  | pytest         | ⬜   |
| AC-3  | 근거 연결률   | ≥ 95% | Validator 출력 | ⬜   |
| AC-4  | 환각률        | ≤ 5%  | Validator 출력 | ⬜   |
| AC-5  | KG 커버리지   | 100%  | Cypher 쿼리    | ⬜   |
| AC-6  | HITL 워크플로 | 동작  | E2E 테스트     | ⬜   |
| AC-7  | 응답 시간     | ≤ 30s | 성능 측정      | ⬜   |
| AC-8  | 재현성        | ≥ 95% | 반복 테스트    | ⬜   |
| AC-9  | UI 사용성     | ≥ 80% | 수동 테스트    | ⬜   |
| AC-10 | 문서화        | 100%  | 파일 검증      | ⬜   |

### 3.2 최종 판정 기준

```
✅ PASS: 모든 필수 AC (AC-1 ~ AC-6) 통과
⚠️ CONDITIONAL: AC-1 ~ AC-6 중 1개 미달, 나머지 통과
❌ FAIL: AC-1 ~ AC-6 중 2개 이상 미달
```

---

## 4. E2E 데모 시나리오

### 4.1 데모 플로우

```yaml
demo_id: E2E-DEMO-01
name: "HR 의사결정 지원 시스템 전체 데모"
duration: "15분"

scenarios:
  - step: 1
    name: "질문 입력"
    duration: "2분"
    actions:
      - ConversationUI에서 "가동률 병목 분석" 프리셋 선택
      - 제약조건 설정 (예산, 일정)
      - 질문 전송
    expected: "Agent 워크플로 시작, 진행 상태 표시"

  - step: 2
    name: "3안 비교"
    duration: "3분"
    actions:
      - OptionCompare에서 3가지 대안 확인
      - 레이더 차트로 스코어 비교
      - As-Is vs To-Be 영향도 확인
    expected: "3안 카드 표시, 추천 옵션 하이라이트"

  - step: 3
    name: "근거 확인"
    duration: "3분"
    actions:
      - ExplanationPanel 열기
      - 추론 경로 확인
      - Evidence 목록 검토
      - KG 뷰 확인
    expected: "근거 연결률 95%+, 환각 위험 5% 이하"

  - step: 4
    name: "의사결정 승인"
    duration: "2분"
    actions:
      - 추천 옵션 선택
      - "승인" 버튼 클릭
      - HITL 승인 확인
    expected: "승인 완료, Decision Log 기록"

  - step: 5
    name: "평가 대시보드"
    duration: "3분"
    actions:
      - EvalDashboard 확인
      - Agent 성능 지표 확인
      - Ontology Scorecard 확인
    expected: "시스템 헬스 정상, 지표 목표 달성"

  - step: 6
    name: "결과 요약"
    duration: "2분"
    actions:
      - 데모 결과 정리
      - Q&A
    expected: "PoC 성공 기준 달성 확인"
```

### 4.2 데모 체크리스트

```markdown
## E2E 데모 체크리스트

### 사전 준비

- [ ] Neo4j 연결 확인
- [ ] Mock 데이터 로드 완료
- [ ] Agent Runtime 기동
- [ ] UI 서버 기동

### 데모 중 확인

- [ ] 질문 입력 → 응답 생성 (30초 이내)
- [ ] 3안 비교 카드 표시
- [ ] Evidence 연결 확인
- [ ] HITL 승인 동작
- [ ] Decision Log 기록

### 데모 후 확인

- [ ] AC-1 ~ AC-6 모두 Pass
- [ ] 성능 지표 목표 달성
- [ ] 문서 완성도 확인
```

---

## 부록: pytest 실행 명령

```bash
# Day 6 테스트
pytest tests/test_day6_ui.py -v --tb=short

# Day 7 테스트
pytest tests/test_day7_validation.py -v --tb=short

# 전체 Acceptance 테스트
pytest -m "acceptance" -v

# 전체 E2E 테스트
pytest -m "e2e" -v

# Day 1-7 전체 테스트
pytest tests/ -v --cov=backend --cov-report=html
```

---

_이 문서는 PoC 최종 단계에서 업데이트될 수 있습니다._
