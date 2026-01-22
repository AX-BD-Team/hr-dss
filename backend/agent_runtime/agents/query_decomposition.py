"""
HR DSS - Query Decomposition Agent

사용자 질문을 분석하여 하위 질의로 분해하는 에이전트
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """질문 유형"""

    CAPACITY = "CAPACITY"  # A-1: 12주 Capacity 병목
    GO_NOGO = "GO_NOGO"  # B-1: Go/No-go 의사결정
    HEADCOUNT = "HEADCOUNT"  # C-1: 증원 분석
    COMPETENCY_GAP = "COMPETENCY_GAP"  # D-1: 역량 갭 분석
    UNKNOWN = "UNKNOWN"


class DataSource(Enum):
    """데이터 소스"""

    EMPLOYEE = "EMPLOYEE"
    ORG_UNIT = "ORG_UNIT"
    PROJECT = "PROJECT"
    OPPORTUNITY = "OPPORTUNITY"
    ASSIGNMENT = "ASSIGNMENT"
    COMPETENCY = "COMPETENCY"
    DEMAND = "DEMAND"
    AVAILABILITY = "AVAILABILITY"


@dataclass
class SubQuery:
    """분해된 하위 질의"""

    sub_query_id: str
    description: str
    data_sources: list[DataSource]
    required_fields: list[str]
    filters: dict[str, Any]
    aggregations: list[str]
    dependencies: list[str] = field(default_factory=list)
    priority: int = 1


@dataclass
class DecomposedQuery:
    """분해된 질의 결과"""

    original_query: str
    query_type: QueryType
    intent: str
    constraints: dict[str, Any]
    sub_queries: list[SubQuery]
    execution_order: list[str]
    decomposed_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0


class QueryDecompositionAgent:
    """질문 분해 에이전트"""

    # 질문 유형별 패턴
    QUERY_PATTERNS = {
        QueryType.CAPACITY: [
            "가동률",
            "capacity",
            "병목",
            "bottleneck",
            "12주",
            "인력 부족",
            "리소스",
            "resource",
            "utilization",
        ],
        QueryType.GO_NOGO: [
            "go/no-go",
            "수주",
            "프로젝트 수락",
            "성공 확률",
            "수행 가능",
            "리소스 매칭",
            "go no go",
        ],
        QueryType.HEADCOUNT: ["증원", "headcount", "인력 충원", "채용", "인원 부족", "팀 확대"],
        QueryType.COMPETENCY_GAP: [
            "역량 갭",
            "competency gap",
            "스킬 부족",
            "역량 개발",
            "교육 투자",
            "ROI",
        ],
    }

    # 질문 유형별 기본 하위 질의 템플릿
    QUERY_TEMPLATES = {
        QueryType.CAPACITY: [
            {
                "id": "capacity_supply",
                "description": "조직별 가용 인력(공급) 조회",
                "data_sources": [DataSource.EMPLOYEE, DataSource.ORG_UNIT, DataSource.AVAILABILITY],
                "required_fields": ["employeeId", "orgUnitId", "availableFTE", "status"],
                "aggregations": ["SUM(availableFTE) BY orgUnitId, timeBucket"],
            },
            {
                "id": "capacity_demand",
                "description": "프로젝트/기회별 수요 조회",
                "data_sources": [DataSource.PROJECT, DataSource.ASSIGNMENT, DataSource.DEMAND],
                "required_fields": [
                    "projectId",
                    "quantityFTE",
                    "probability",
                    "startDate",
                    "endDate",
                ],
                "aggregations": ["SUM(quantityFTE * probability) BY orgUnitId, timeBucket"],
            },
            {
                "id": "capacity_gap",
                "description": "공급-수요 갭 계산",
                "data_sources": [],
                "required_fields": [],
                "dependencies": ["capacity_supply", "capacity_demand"],
                "aggregations": ["supply - demand BY orgUnitId, timeBucket"],
            },
            {
                "id": "bottleneck_identify",
                "description": "병목 구간 식별",
                "data_sources": [],
                "required_fields": [],
                "dependencies": ["capacity_gap"],
                "aggregations": ["FILTER WHERE utilization > 0.9"],
            },
        ],
        QueryType.GO_NOGO: [
            {
                "id": "opportunity_info",
                "description": "기회 정보 조회",
                "data_sources": [DataSource.OPPORTUNITY],
                "required_fields": [
                    "opportunityId",
                    "name",
                    "dealValue",
                    "estimatedFTE",
                    "requiredCompetencies",
                ],
                "aggregations": [],
            },
            {
                "id": "resource_availability",
                "description": "리소스 가용성 조회",
                "data_sources": [
                    DataSource.EMPLOYEE,
                    DataSource.AVAILABILITY,
                    DataSource.ASSIGNMENT,
                ],
                "required_fields": ["employeeId", "availableFTE", "competencies"],
                "aggregations": ["SUM(availableFTE) BY competency"],
            },
            {
                "id": "competency_match",
                "description": "역량 매칭 분석",
                "data_sources": [DataSource.COMPETENCY],
                "required_fields": ["competencyId", "level", "employeeId"],
                "dependencies": ["opportunity_info", "resource_availability"],
                "aggregations": ["MATCH score BY competency requirement"],
            },
            {
                "id": "historical_success",
                "description": "유사 프로젝트 성공률 조회",
                "data_sources": [DataSource.PROJECT],
                "required_fields": ["projectId", "projectType", "outcome", "successScore"],
                "aggregations": ["AVG(successScore) BY projectType"],
            },
        ],
        QueryType.HEADCOUNT: [
            {
                "id": "current_headcount",
                "description": "현재 인력 현황 조회",
                "data_sources": [DataSource.EMPLOYEE, DataSource.ORG_UNIT],
                "required_fields": ["employeeId", "orgUnitId", "status", "grade"],
                "aggregations": ["COUNT BY orgUnitId, grade"],
            },
            {
                "id": "current_utilization",
                "description": "현재 가동률 조회",
                "data_sources": [DataSource.ASSIGNMENT],
                "required_fields": ["assignmentId", "allocationFTE"],
                "aggregations": ["SUM(allocationFTE) / headcount BY orgUnitId"],
            },
            {
                "id": "pipeline_demand",
                "description": "파이프라인 수요 조회",
                "data_sources": [DataSource.OPPORTUNITY, DataSource.DEMAND],
                "required_fields": ["demandId", "quantityFTE", "probability"],
                "aggregations": ["SUM(quantityFTE * probability) BY orgUnitId"],
            },
            {
                "id": "attrition_forecast",
                "description": "이직 예측",
                "data_sources": [DataSource.EMPLOYEE],
                "required_fields": ["employeeId", "tenure", "performanceRating"],
                "aggregations": ["PREDICT attrition_rate BY orgUnitId"],
            },
        ],
        QueryType.COMPETENCY_GAP: [
            {
                "id": "required_competencies",
                "description": "필요 역량 조회",
                "data_sources": [DataSource.PROJECT, DataSource.DEMAND],
                "required_fields": ["competencyId", "minimumLevel", "demandCount"],
                "aggregations": ["COUNT projects BY competencyId"],
            },
            {
                "id": "current_competencies",
                "description": "보유 역량 조회",
                "data_sources": [DataSource.EMPLOYEE, DataSource.COMPETENCY],
                "required_fields": ["employeeId", "competencyId", "level"],
                "aggregations": ["COUNT employees BY competencyId, level"],
            },
            {
                "id": "gap_analysis",
                "description": "역량 갭 분석",
                "data_sources": [],
                "required_fields": [],
                "dependencies": ["required_competencies", "current_competencies"],
                "aggregations": ["required - current BY competencyId"],
            },
            {
                "id": "investment_roi",
                "description": "투자 ROI 분석",
                "data_sources": [],
                "required_fields": ["trainingCost", "expectedRevenue"],
                "dependencies": ["gap_analysis"],
                "aggregations": ["CALCULATE ROI BY competencyId"],
            },
        ],
    }

    def __init__(self, llm_client: Any = None):
        """
        Args:
            llm_client: LLM 클라이언트 (Claude SDK 등)
        """
        self.llm_client = llm_client

    def decompose(self, query: str, context: dict | None = None) -> DecomposedQuery:
        """
        질문을 분해하여 하위 질의로 변환

        Args:
            query: 사용자 질문
            context: 추가 컨텍스트 (조직, 기간 등)

        Returns:
            DecomposedQuery: 분해된 질의
        """
        # 1. 질문 유형 분류
        query_type = self._classify_query(query)

        # 2. 의도 추출
        intent = self._extract_intent(query, query_type)

        # 3. 제약조건 추출
        constraints = self._extract_constraints(query, context)

        # 4. 하위 질의 생성
        sub_queries = self._generate_sub_queries(query_type, constraints)

        # 5. 실행 순서 결정
        execution_order = self._determine_execution_order(sub_queries)

        # 6. 신뢰도 계산
        confidence = self._calculate_confidence(query_type, constraints)

        return DecomposedQuery(
            original_query=query,
            query_type=query_type,
            intent=intent,
            constraints=constraints,
            sub_queries=sub_queries,
            execution_order=execution_order,
            confidence=confidence,
        )

    def _classify_query(self, query: str) -> QueryType:
        """질문 유형 분류"""
        query_lower = query.lower()

        scores = {}
        for q_type, patterns in self.QUERY_PATTERNS.items():
            score = sum(1 for p in patterns if p.lower() in query_lower)
            scores[q_type] = score

        if max(scores.values()) == 0:
            return QueryType.UNKNOWN

        return max(scores, key=scores.get)

    def _extract_intent(self, query: str, query_type: QueryType) -> str:
        """의도 추출"""
        intent_templates = {
            QueryType.CAPACITY: "향후 12주간 조직별 인력 가동률 및 병목 구간 분석",
            QueryType.GO_NOGO: "신규 프로젝트/기회에 대한 수행 가능성 및 성공 확률 평가",
            QueryType.HEADCOUNT: "조직의 증원 필요성 및 적정 인력 규모 분석",
            QueryType.COMPETENCY_GAP: "현재 보유 역량과 필요 역량 간 갭 분석 및 투자 ROI 평가",
            QueryType.UNKNOWN: "질문 의도 파악 필요",
        }
        return intent_templates.get(query_type, "알 수 없는 의도")

    def _extract_constraints(self, query: str, context: dict | None) -> dict[str, Any]:
        """제약조건 추출"""
        constraints = {}

        # 컨텍스트에서 기본 제약조건 추출
        if context:
            if "org_unit_id" in context:
                constraints["orgUnitId"] = context["org_unit_id"]
            if "start_date" in context:
                constraints["startDate"] = context["start_date"]
            if "end_date" in context:
                constraints["endDate"] = context["end_date"]
            if "opportunity_id" in context:
                constraints["opportunityId"] = context["opportunity_id"]

        # 질문에서 추가 제약조건 추출 (간단한 패턴 매칭)
        query_lower = query.lower()

        # 기간 추출
        if "12주" in query_lower:
            constraints["horizon_weeks"] = 12
        elif "6개월" in query_lower:
            constraints["horizon_months"] = 6
        elif "1년" in query_lower:
            constraints["horizon_months"] = 12

        # 조직 추출 (예: "AI팀", "데이터팀" 등)
        org_patterns = ["ai팀", "ai/ml", "데이터팀", "클라우드팀"]
        for pattern in org_patterns:
            if pattern in query_lower:
                constraints["orgUnitPattern"] = pattern
                break

        return constraints

    def _generate_sub_queries(
        self, query_type: QueryType, constraints: dict[str, Any]
    ) -> list[SubQuery]:
        """하위 질의 생성"""
        templates = self.QUERY_TEMPLATES.get(query_type, [])
        sub_queries = []

        for idx, template in enumerate(templates):
            sub_query = SubQuery(
                sub_query_id=template["id"],
                description=template["description"],
                data_sources=[
                    ds if isinstance(ds, DataSource) else DataSource(ds)
                    for ds in template.get("data_sources", [])
                ],
                required_fields=template.get("required_fields", []),
                filters=constraints.copy(),
                aggregations=template.get("aggregations", []),
                dependencies=template.get("dependencies", []),
                priority=idx + 1,
            )
            sub_queries.append(sub_query)

        return sub_queries

    def _determine_execution_order(self, sub_queries: list[SubQuery]) -> list[str]:
        """실행 순서 결정 (의존성 기반 위상 정렬)"""
        # 의존성 그래프 생성
        graph = {sq.sub_query_id: sq.dependencies for sq in sub_queries}
        in_degree = {sq.sub_query_id: len(sq.dependencies) for sq in sub_queries}

        # 위상 정렬
        order = []
        queue = [sq_id for sq_id, deg in in_degree.items() if deg == 0]

        while queue:
            current = queue.pop(0)
            order.append(current)

            for sq_id, deps in graph.items():
                if current in deps:
                    in_degree[sq_id] -= 1
                    if in_degree[sq_id] == 0:
                        queue.append(sq_id)

        return order

    def _calculate_confidence(self, query_type: QueryType, constraints: dict[str, Any]) -> float:
        """신뢰도 계산"""
        base_confidence = 0.5 if query_type == QueryType.UNKNOWN else 0.8

        # 제약조건이 많을수록 신뢰도 증가
        constraint_bonus = min(len(constraints) * 0.05, 0.15)

        return min(base_confidence + constraint_bonus, 1.0)

    def to_dict(self, decomposed: DecomposedQuery) -> dict:
        """결과를 딕셔너리로 변환"""
        return {
            "original_query": decomposed.original_query,
            "query_type": decomposed.query_type.value,
            "intent": decomposed.intent,
            "constraints": decomposed.constraints,
            "sub_queries": [
                {
                    "sub_query_id": sq.sub_query_id,
                    "description": sq.description,
                    "data_sources": [ds.value for ds in sq.data_sources],
                    "required_fields": sq.required_fields,
                    "filters": sq.filters,
                    "aggregations": sq.aggregations,
                    "dependencies": sq.dependencies,
                    "priority": sq.priority,
                }
                for sq in decomposed.sub_queries
            ],
            "execution_order": decomposed.execution_order,
            "decomposed_at": decomposed.decomposed_at.isoformat(),
            "confidence": decomposed.confidence,
        }


# CLI 테스트용
if __name__ == "__main__":
    agent = QueryDecompositionAgent()

    test_queries = [
        "향후 12주간 AI팀의 가동률 병목 구간을 분석해줘",
        "이 프로젝트를 수주해도 될까요? 성공 확률은 어떻게 되나요?",
        "우리 팀에 개발자 2명 증원이 필요한데 정당한가요?",
        "데이터 엔지니어링 역량 갭을 분석하고 교육 투자 ROI를 알려줘",
    ]

    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print("=" * 60)

        result = agent.decompose(query)
        result_dict = agent.to_dict(result)

        print(f"Type: {result_dict['query_type']}")
        print(f"Intent: {result_dict['intent']}")
        print(f"Confidence: {result_dict['confidence']:.2f}")
        print(f"Sub-queries: {len(result_dict['sub_queries'])}")
        print(f"Execution Order: {result_dict['execution_order']}")
