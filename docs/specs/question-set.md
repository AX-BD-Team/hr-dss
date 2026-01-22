# HR 의사결정 지원 시스템 - Key Question Set v1

> 작성일: 2025-01-22 | 버전: 1.0

---

## 1. 공통 3단계 대화 템플릿

모든 질문은 다음 3단계 흐름을 따릅니다:

| 단계             | 내용                                                | Input         | Output                              |
| ---------------- | --------------------------------------------------- | ------------- | ----------------------------------- |
| **1. 문제 정의** | Scope + Horizon + Objective + Constraint + KPI      | 자연어 질문   | 구조화된 요청서 (DecisionCase)      |
| **2. 대안 탐색** | 3안(내부/혼합/역량강화) + As-Is vs To-Be 시뮬레이션 | DecisionCase  | Option 비교표 (Evaluation)          |
| **3. 보고/기획** | 1페이지 요약 + 실행계획 + HITL 승인 + Workflow      | 선택된 Option | 실행 패키지 (Action + WorkflowTask) |

---

## 2. 4대 핵심 질문 (Use Cases)

### A-1: 12주 Capacity 병목 예측

| 항목            | 내용                                                                |
| --------------- | ------------------------------------------------------------------- |
| **질문 예시**   | "향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인을 예측해줘" |
| **카테고리**    | Capacity Planning                                                   |
| **Horizon**     | 12주 (TimeBucket: WEEK)                                             |
| **핵심 Output** | ForecastPoint(UTILIZATION) + Finding(병목 원인)                     |

#### 단계별 입력/출력

**1단계: 문제 정의**

```yaml
Input:
  question: "향후 12주간 본부/팀별 가동률 90% 초과 주차와 병목 원인 예측"

Output (DecisionCase):
  type: CAPACITY_FORECAST
  scope:
    orgUnits: [전체 본부/팀]
    horizon: 12주
  objective:
    metricType: UTILIZATION
    operator: ">="
    targetValue: 0.9
    direction: MINIMIZE_EXCESS
  constraints:
    - type: RESOURCE
      expression: "가용 인력 범위 내"
  kpis:
    - 병목 발생 주차 수
    - 병목 심각도 (초과 FTE)
    - 원인별 분류
```

**2단계: 대안 탐색**

```yaml
Input: DecisionCase (위 결과)

Output (Option 비교표):
  options:
    - name: "1안: 내부 재배치"
      type: INTERNAL
      actions:
        - 유휴 인력 cross-team 배치
        - 프로젝트 일정 조정
      evaluation:
        utilizationDelta: -5%
        costImpact: 0
        riskLevel: LOW

    - name: "2안: 외부 충원"
      type: MIXED
      actions:
        - 협력사 인력 투입
        - 단기 계약직 채용
      evaluation:
        utilizationDelta: -15%
        costImpact: +20%
        riskLevel: MEDIUM

    - name: "3안: 역량 강화"
      type: UPSKILL
      actions:
        - 멀티스킬 교육
        - R&R 재정의
      evaluation:
        utilizationDelta: -10%
        costImpact: +5%
        riskLevel: LOW
        timeToEffect: 4주
```

**3단계: 보고/기획**

```yaml
Input: 선택된 Option (예: 1안)

Output (실행 패키지):
  summary: "1페이지 요약 보고서"
  actions:
    - type: REASSIGN
      owner: 팀장
      target: [직원A, 직원B]
      dueDate: 2025-02-01
  workflow:
    gate: VRB
    approvers: [본부장]
    tasks:
      - 인력 재배치 실행
      - 주간 가동률 모니터링
```

---

### B-1: Go/No-go + 성공확률

| 항목            | 내용                                                                          |
| --------------- | ----------------------------------------------------------------------------- |
| **질문 예시**   | "'100억 미디어 AX' 프로젝트를 내부 수행 가능한지, 성공확률은 얼마인지 알려줘" |
| **카테고리**    | Project Feasibility                                                           |
| **Horizon**     | 프로젝트 기간                                                                 |
| **핵심 Output** | ForecastPoint(SUCCESS_PROB, MARGIN) + Risk Assessment                         |

#### 단계별 입력/출력

**1단계: 문제 정의**

```yaml
Input:
  question: "'100억 미디어 AX' 내부 수행 가능 여부와 성공확률"

Output (DecisionCase):
  type: GO_NOGO
  scope:
    opportunity: "100억 미디어 AX"
    dealValue: 10,000,000,000
  objective:
    metricType: SUCCESS_PROBABILITY
    operator: ">="
    targetValue: 0.7
  constraints:
    - type: RESOURCE
      expression: "내부 인력 우선"
    - type: MARGIN
      expression: "마진율 >= 15%"
    - type: TIMELINE
      expression: "제안 마감일 준수"
  kpis:
    - 내부 수행 가능률
    - 예상 성공확률
    - 예상 마진율
    - 주요 리스크
```

**2단계: 대안 탐색**

```yaml
Output (Option 비교표):
  options:
    - name: "1안: 100% 내부 수행"
      type: INTERNAL
      resourceMatch:
        required: [PM 1명, 아키텍트 2명, 개발자 5명]
        available: [PM 1명, 아키텍트 1명, 개발자 3명]
        gap: [아키텍트 1명, 개발자 2명]
      evaluation:
        successProbability: 0.45
        estimatedMargin: 18%
        riskLevel: HIGH
        keyRisks:
          - "아키텍트 부족으로 설계 품질 리스크"
          - "개발자 부족으로 일정 지연 리스크"

    - name: "2안: 내부 70% + 외부 30%"
      type: MIXED
      resourceMatch:
        internal: [PM 1명, 아키텍트 1명, 개발자 3명]
        external: [아키텍트 1명, 개발자 2명]
      evaluation:
        successProbability: 0.75
        estimatedMargin: 12%
        riskLevel: MEDIUM
        keyRisks:
          - "외부 인력 온보딩 리스크"
          - "마진율 목표 미달 가능성"

    - name: "3안: 역량 강화 후 수주"
      type: UPSKILL
      actions:
        - "2주간 아키텍트 역량 강화"
        - "개발자 신규 채용"
      evaluation:
        successProbability: 0.65
        estimatedMargin: 16%
        riskLevel: MEDIUM
        timeToReady: 4주
```

---

### C-1: 증원 원인분해

| 항목            | 내용                                             |
| --------------- | ------------------------------------------------ |
| **질문 예시**   | "데이터플랫폼팀 1명 증원 요청의 원인을 분해해줘" |
| **카테고리**    | Headcount Analysis                               |
| **Horizon**     | 현재 + 향후 6개월                                |
| **핵심 Output** | Finding(rootCause) + Evidence                    |

#### 단계별 입력/출력

**1단계: 문제 정의**

```yaml
Input:
  question: "데이터플랫폼팀 1명 증원 요청의 원인분해"

Output (DecisionCase):
  type: HEADCOUNT_ANALYSIS
  scope:
    orgUnit: "데이터플랫폼팀"
    requestedHeadcount: 1
  objective:
    metricType: ROOT_CAUSE
    direction: IDENTIFY
  constraints:
    - type: EVIDENCE
      expression: "모든 주장에 근거 필수"
  kpis:
    - 원인별 기여도 (%)
    - 근거 연결률
    - 대안 유무
```

**2단계: 대안 탐색**

```yaml
Output (Finding 분석):
  rootCauseAnalysis:
    - cause: "수요 증가"
      contribution: 40%
      evidence:
        - source: "BizForce"
          data: "파이프라인 150% 증가 (전년 대비)"
        - source: "TMS"
          data: "프로젝트 할당률 95% (팀 평균 80%)"

    - cause: "역량 미스매치"
      contribution: 30%
      evidence:
        - source: "Competency"
          data: "AI/ML 역량 보유자 1명 (필요 3명)"
        - source: "Project"
          data: "AI 프로젝트 3건 진행 중"

    - cause: "R&R 비효율"
      contribution: 20%
      evidence:
        - source: "Assignment"
          data: "1인 다중 프로젝트 배치 (평균 2.5개)"
        - source: "TimeSheet"
          data: "관리 업무 비중 30%"

    - cause: "이직/휴직"
      contribution: 10%
      evidence:
        - source: "HR Master"
          data: "퇴직 1명 (미충원), 육휴 1명"

  options:
    - name: "1안: 증원 승인"
      type: APPROVE
      recommendation: "AI/ML 전문가 채용"

    - name: "2안: 내부 재배치"
      type: INTERNAL
      recommendation: "타 팀 AI 역량자 전배"

    - name: "3안: 역량 강화"
      type: UPSKILL
      recommendation: "기존 인력 AI/ML 교육 (3개월)"
```

---

### D-1: 역량 투자 ROI

| 항목            | 내용                                                 |
| --------------- | ---------------------------------------------------- |
| **질문 예시**   | "AI-driven 전환 관점에서 역량 갭 Top10을 정량화해줘" |
| **카테고리**    | Competency Gap Analysis                              |
| **Horizon**     | 1년                                                  |
| **핵심 Output** | CompetencyGap + ImpactAssessment                     |

#### 단계별 입력/출력

**1단계: 문제 정의**

```yaml
Input:
  question: "AI-driven 전환 관점 역량 갭 Top10 정량화"

Output (DecisionCase):
  type: COMPETENCY_GAP
  scope:
    domain: "AI-driven Transformation"
    targetCompetencies:
      - "Generative AI"
      - "MLOps"
      - "Data Engineering"
      - "AI Product Management"
  objective:
    metricType: GAP_SCORE
    direction: PRIORITIZE
    topN: 10
  constraints:
    - type: BUDGET
      expression: "연간 교육 예산 내"
  kpis:
    - 역량별 갭 점수
    - 투자 대비 ROI
    - 시급도 (비즈니스 임팩트)
```

**2단계: 대안 탐색**

```yaml
Output (CompetencyGap 분석):
  gapAnalysis:
    - rank: 1
      competency: "Generative AI Application"
      currentLevel: 1.5 # 5점 만점
      requiredLevel: 4.0
      gapScore: 2.5
      affectedProjects: 5
      businessImpact: "HIGH"

    - rank: 2
      competency: "MLOps/LLMOps"
      currentLevel: 2.0
      requiredLevel: 4.5
      gapScore: 2.5
      affectedProjects: 3
      businessImpact: "HIGH"

    # ... Top 10까지

  investmentOptions:
    - name: "1안: 외부 채용 집중"
      type: EXTERNAL_HIRE
      cost: 500M
      timeToEffect: 3개월
      expectedROI: 2.5x

    - name: "2안: 내부 역량 강화"
      type: UPSKILL
      cost: 200M
      timeToEffect: 6개월
      expectedROI: 3.0x

    - name: "3안: 혼합 전략"
      type: MIXED
      cost: 350M
      timeToEffect: 4개월
      expectedROI: 2.8x
```

---

## 3. 질문 확장 (추가 후보)

| ID  | 유형       | 질문 예시                                           | 우선순위 |
| --- | ---------- | --------------------------------------------------- | -------- |
| A-2 | Capacity   | "특정 프로젝트 종료 시 유휴 인력 재배치 시뮬레이션" | P2       |
| B-2 | Go/No-go   | "동시 수주 시 리소스 충돌 분석"                     | P2       |
| C-2 | Headcount  | "전사 인력 구조 최적화 방안"                        | P3       |
| D-2 | Competency | "퇴직 리스크 인력의 역량 대체 계획"                 | P2       |
| E-1 | R&R        | "대무 체계 커버리지 분석"                           | P2       |

---

## 4. 입력 데이터 요구사항

### 질문별 필수 데이터

| 질문 | 필수 노드                                                       | 필수 관계                                 |
| ---- | --------------------------------------------------------------- | ----------------------------------------- |
| A-1  | OrgUnit, Employee, Assignment, TimeBucket, Availability         | BELONGS_TO, ASSIGNED_TO, FOR_BUCKET       |
| B-1  | Opportunity, DemandSignal, ResourceDemand, Employee, Competency | HAS_SIGNAL, IMPLIES_DEMAND, REQUIRES_ROLE |
| C-1  | OrgUnit, Employee, Assignment, Competency, Project              | BELONGS_TO, ASSIGNED_TO, HAS_EVIDENCE     |
| D-1  | Competency, CompetencyEvidence, Employee, LearningProgram       | HAS_EVIDENCE, FOR_COMPETENCY              |

---

## 5. 응답 형식 표준

### 5.1 JSON 응답 스키마

```json
{
  "decisionCase": {
    "id": "string",
    "type": "enum",
    "status": "enum",
    "createdAt": "datetime"
  },
  "analysis": {
    "findings": [
      {
        "type": "string",
        "severity": "enum",
        "narrative": "string",
        "evidence": [
          {
            "sourceSystem": "string",
            "sourceRef": "string",
            "data": "any"
          }
        ]
      }
    ]
  },
  "options": [
    {
      "name": "string",
      "type": "enum",
      "actions": ["string"],
      "evaluation": {
        "metrics": {},
        "risks": [],
        "recommendation": "string"
      }
    }
  ],
  "metadata": {
    "modelRun": "string",
    "confidence": "number",
    "processingTime": "number"
  }
}
```

---

_이 문서는 PoC 진행 중 질문이 추가/수정될 수 있습니다._
