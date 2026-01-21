"""
HR DSS - Knowledge Graph Query Module

Knowledge Graph 쿼리 및 Evidence 연결 기능
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

try:
    from neo4j import Driver, GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = Any

logger = logging.getLogger(__name__)


@dataclass
class Evidence:
    """증거 데이터"""
    evidence_id: str
    evidence_type: str
    source: str
    description: str
    value: Any
    timestamp: datetime | None = None
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass
class QueryResult:
    """쿼리 결과"""
    query_type: str
    data: list[dict]
    evidence: list[Evidence]
    execution_time_ms: float
    total_count: int


class KnowledgeGraphQuery:
    """Knowledge Graph 쿼리 인터페이스"""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        database: str = "neo4j"
    ):
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j 패키지가 설치되지 않았습니다.")

        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver: Driver | None = None

    def connect(self) -> None:
        """Neo4j 연결"""
        self._driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )
        self._driver.verify_connectivity()

    def close(self) -> None:
        """연결 종료"""
        if self._driver:
            self._driver.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # =========================================================
    # A-1: Capacity/Utilization 관련 쿼리
    # =========================================================

    def get_org_utilization(
        self,
        org_unit_id: str,
        start_date: date,
        end_date: date
    ) -> QueryResult:
        """조직별 가동률 조회"""
        start_time = datetime.now()

        query = """
        MATCH (ou:OrgUnit {orgUnitId: $orgUnitId})<-[:BELONGS_TO]-(e:Employee)
        WHERE e.status = 'ACTIVE'
        WITH ou, COLLECT(e) AS employees, COUNT(e) AS headCount

        OPTIONAL MATCH (e:Employee)-[a:ASSIGNED_TO]->(p:Project)
        WHERE e IN employees
          AND date(a.startDate) <= date($endDate)
          AND date(a.endDate) >= date($startDate)

        WITH ou, headCount,
             COALESCE(SUM(a.allocationFTE), 0) AS assignedFTE

        RETURN ou.orgUnitId AS orgUnitId,
               ou.name AS orgUnitName,
               headCount,
               assignedFTE,
               CASE WHEN headCount > 0 THEN assignedFTE / headCount ELSE 0 END AS utilization
        """

        with self._driver.session(database=self.database) as session:
            result = session.run(
                query,
                orgUnitId=org_unit_id,
                startDate=start_date.isoformat(),
                endDate=end_date.isoformat()
            )
            data = [dict(record) for record in result]

        # Evidence 수집
        evidence = [
            Evidence(
                evidence_id=f"EV-UTIL-{org_unit_id}",
                evidence_type="UTILIZATION_CALCULATION",
                source="KG_QUERY",
                description=f"{org_unit_id} 가동률 계산 ({start_date} ~ {end_date})",
                value=data[0] if data else None,
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="ORG_UTILIZATION",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    def get_capacity_forecast(
        self,
        org_unit_id: str,
        weeks: int = 12
    ) -> QueryResult:
        """조직별 Capacity 예측 (12주)"""
        start_time = datetime.now()

        query = """
        MATCH (ou:OrgUnit {orgUnitId: $orgUnitId})<-[:BELONGS_TO]-(e:Employee)
        WHERE e.status = 'ACTIVE'
        WITH ou, COUNT(e) AS availableFTE

        MATCH (tb:TimeBucket)
        WHERE tb.bucketType = 'WEEK'
          AND tb.bucketStart >= date()
          AND tb.bucketStart < date() + duration({weeks: $weeks})

        OPTIONAL MATCH (e:Employee)-[:BELONGS_TO]->(ou)
        OPTIONAL MATCH (e)-[a:ASSIGNED_TO]->(p:Project)
        WHERE date(a.startDate) <= tb.bucketEnd
          AND date(a.endDate) >= tb.bucketStart

        WITH ou, tb, availableFTE,
             COALESCE(SUM(a.allocationFTE), 0) AS demandFTE

        RETURN tb.bucketId AS bucketId,
               tb.label AS weekLabel,
               tb.bucketStart AS weekStart,
               availableFTE,
               demandFTE,
               availableFTE - demandFTE AS gapFTE,
               CASE WHEN availableFTE > 0
                    THEN demandFTE / availableFTE
                    ELSE 0
               END AS utilization
        ORDER BY tb.bucketStart
        """

        with self._driver.session(database=self.database) as session:
            result = session.run(
                query,
                orgUnitId=org_unit_id,
                weeks=weeks
            )
            data = [dict(record) for record in result]

        # Bottleneck 식별
        bottleneck_weeks = [
            d for d in data
            if d.get("utilization", 0) > 0.9
        ]

        evidence = [
            Evidence(
                evidence_id=f"EV-CAP-{org_unit_id}",
                evidence_type="CAPACITY_FORECAST",
                source="KG_QUERY",
                description=f"{org_unit_id} {weeks}주 Capacity 예측",
                value={"total_weeks": len(data), "bottleneck_weeks": len(bottleneck_weeks)},
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="CAPACITY_FORECAST",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    def find_bottleneck_competencies(
        self,
        org_unit_id: str | None = None
    ) -> QueryResult:
        """병목 역량 식별"""
        start_time = datetime.now()

        org_filter = "WHERE rd.requestedOrgUnitId = $orgUnitId" if org_unit_id else ""

        query = f"""
        MATCH (rd:ResourceDemand)-[:TARGETS_ORG]->(ou:OrgUnit)
        {org_filter}
        WHERE rd.status IN ['OPEN', 'PARTIALLY_FILLED']
        WITH rd, ou

        UNWIND rd.requiredCompetencies AS reqComp
        WITH reqComp.competencyId AS compId,
             SUM(rd.quantityFTE * rd.probability) AS demandFTE

        MATCH (c:Competency {{competencyId: compId}})
        OPTIONAL MATCH (e:Employee {{status: 'ACTIVE'}})-[r:HAS_COMPETENCY]->(c)
        WHERE r.level >= 3

        WITH c, demandFTE, COUNT(e) AS supplyCount

        RETURN c.competencyId AS competencyId,
               c.name AS competencyName,
               c.domain AS domain,
               demandFTE,
               supplyCount,
               demandFTE - supplyCount AS gap,
               CASE WHEN supplyCount > 0
                    THEN demandFTE / supplyCount
                    ELSE 999
               END AS demandSupplyRatio
        ORDER BY gap DESC
        LIMIT 10
        """

        params = {"orgUnitId": org_unit_id} if org_unit_id else {}

        with self._driver.session(database=self.database) as session:
            result = session.run(query, **params)
            data = [dict(record) for record in result]

        evidence = [
            Evidence(
                evidence_id="EV-BOTTLENECK-COMP",
                evidence_type="BOTTLENECK_ANALYSIS",
                source="KG_QUERY",
                description="병목 역량 분석",
                value={"bottleneck_count": len([d for d in data if d.get("gap", 0) > 0])},
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="BOTTLENECK_COMPETENCIES",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    # =========================================================
    # B-1: Go/No-go 의사결정 관련 쿼리
    # =========================================================

    def evaluate_opportunity(
        self,
        opportunity_id: str
    ) -> QueryResult:
        """기회 평가 (Go/No-go 분석)"""
        start_time = datetime.now()

        query = """
        MATCH (o:Opportunity {opportunityId: $opportunityId})
        OPTIONAL MATCH (o)-[:OWNED_BY]->(ou:OrgUnit)
        OPTIONAL MATCH (ou)<-[:BELONGS_TO]-(e:Employee {status: 'ACTIVE'})

        WITH o, ou, COUNT(e) AS availableStaff

        OPTIONAL MATCH (rd:ResourceDemand)
        WHERE rd.sourceId = o.opportunityId

        WITH o, ou, availableStaff,
             COALESCE(SUM(rd.quantityFTE), o.estimatedFTE) AS requiredFTE

        RETURN o.opportunityId AS opportunityId,
               o.name AS opportunityName,
               o.stage AS stage,
               o.dealValue AS dealValue,
               o.closeProbability AS closeProbability,
               o.estimatedFTE AS estimatedFTE,
               o.estimatedDuration AS estimatedDuration,
               ou.name AS ownerOrgUnit,
               availableStaff,
               requiredFTE,
               CASE WHEN availableStaff >= requiredFTE THEN true ELSE false END AS resourceFit
        """

        with self._driver.session(database=self.database) as session:
            result = session.run(query, opportunityId=opportunity_id)
            data = [dict(record) for record in result]

        # Resource Fit 분석
        opp_data = data[0] if data else {}
        resource_fit = opp_data.get("resourceFit", False)

        evidence = [
            Evidence(
                evidence_id=f"EV-OPP-{opportunity_id}",
                evidence_type="OPPORTUNITY_EVALUATION",
                source="KG_QUERY",
                description=f"기회 {opportunity_id} 평가",
                value={
                    "resource_fit": resource_fit,
                    "available_staff": opp_data.get("availableStaff"),
                    "required_fte": opp_data.get("requiredFTE")
                },
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="OPPORTUNITY_EVALUATION",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    def find_matching_resources(
        self,
        opportunity_id: str,
        limit: int = 10
    ) -> QueryResult:
        """기회에 맞는 리소스 매칭"""
        start_time = datetime.now()

        query = """
        MATCH (o:Opportunity {opportunityId: $opportunityId})
        OPTIONAL MATCH (o)-[:OWNED_BY]->(ou:OrgUnit)
        OPTIONAL MATCH (ou)<-[:BELONGS_TO]-(e:Employee {status: 'ACTIVE'})

        WITH o, e
        OPTIONAL MATCH (e)-[r:HAS_COMPETENCY]->(c:Competency)

        WITH e,
             COLLECT({competency: c.name, level: r.level}) AS competencies,
             AVG(COALESCE(r.level, 0)) AS avgCompetencyLevel

        OPTIONAL MATCH (e)-[a:ASSIGNED_TO]->(p:Project)
        WHERE date(a.endDate) >= date()
        WITH e, competencies, avgCompetencyLevel,
             COALESCE(SUM(a.allocationFTE), 0) AS currentAllocation

        WHERE currentAllocation < 1.0

        RETURN e.employeeId AS employeeId,
               e.name AS name,
               e.grade AS grade,
               competencies,
               avgCompetencyLevel,
               currentAllocation,
               1.0 - currentAllocation AS availableFTE
        ORDER BY availableFTE DESC, avgCompetencyLevel DESC
        LIMIT $limit
        """

        with self._driver.session(database=self.database) as session:
            result = session.run(query, opportunityId=opportunity_id, limit=limit)
            data = [dict(record) for record in result]

        evidence = [
            Evidence(
                evidence_id=f"EV-MATCH-{opportunity_id}",
                evidence_type="RESOURCE_MATCHING",
                source="KG_QUERY",
                description=f"기회 {opportunity_id} 리소스 매칭",
                value={"candidates_found": len(data)},
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="RESOURCE_MATCHING",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    # =========================================================
    # C-1: 증원 분석 관련 쿼리
    # =========================================================

    def analyze_headcount_need(
        self,
        org_unit_id: str
    ) -> QueryResult:
        """증원 필요성 분석"""
        start_time = datetime.now()

        query = """
        MATCH (ou:OrgUnit {orgUnitId: $orgUnitId})
        OPTIONAL MATCH (ou)<-[:BELONGS_TO]-(e:Employee {status: 'ACTIVE'})
        WITH ou, COUNT(e) AS currentHeadcount, COLLECT(e) AS employees

        // 현재 배치 현황
        OPTIONAL MATCH (emp:Employee)-[a:ASSIGNED_TO]->(p:Project)
        WHERE emp IN employees
          AND date(a.endDate) >= date()
        WITH ou, currentHeadcount,
             COALESCE(SUM(a.allocationFTE), 0) AS currentAssignedFTE

        // 파이프라인 수요
        OPTIONAL MATCH (rd:ResourceDemand)
        WHERE rd.requestedOrgUnitId = ou.orgUnitId
          AND rd.status IN ['OPEN', 'PARTIALLY_FILLED']
        WITH ou, currentHeadcount, currentAssignedFTE,
             COALESCE(SUM(rd.quantityFTE * rd.probability), 0) AS pipelineDemandFTE

        // 과거 이직률 (가정: 연 10%)
        WITH ou, currentHeadcount, currentAssignedFTE, pipelineDemandFTE,
             currentHeadcount * 0.1 AS expectedAttrition

        RETURN ou.orgUnitId AS orgUnitId,
               ou.name AS orgUnitName,
               currentHeadcount,
               currentAssignedFTE,
               pipelineDemandFTE,
               currentHeadcount - currentAssignedFTE AS currentSlack,
               pipelineDemandFTE - (currentHeadcount - currentAssignedFTE) AS projectedGap,
               expectedAttrition,
               CASE
                 WHEN pipelineDemandFTE > (currentHeadcount - currentAssignedFTE) * 1.2
                 THEN 'JUSTIFIED'
                 WHEN pipelineDemandFTE > (currentHeadcount - currentAssignedFTE)
                 THEN 'CONDITIONAL'
                 ELSE 'NOT_JUSTIFIED'
               END AS headcountRecommendation
        """

        with self._driver.session(database=self.database) as session:
            result = session.run(query, orgUnitId=org_unit_id)
            data = [dict(record) for record in result]

        analysis = data[0] if data else {}

        evidence = [
            Evidence(
                evidence_id=f"EV-HC-{org_unit_id}",
                evidence_type="HEADCOUNT_ANALYSIS",
                source="KG_QUERY",
                description=f"{org_unit_id} 증원 필요성 분석",
                value={
                    "recommendation": analysis.get("headcountRecommendation"),
                    "projected_gap": analysis.get("projectedGap")
                },
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="HEADCOUNT_ANALYSIS",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    # =========================================================
    # D-1: 역량 갭 분석 관련 쿼리
    # =========================================================

    def analyze_competency_gap(
        self,
        org_unit_id: str | None = None
    ) -> QueryResult:
        """역량 갭 분석"""
        start_time = datetime.now()

        org_filter = "AND ou.orgUnitId = $orgUnitId" if org_unit_id else ""

        query = f"""
        // 수요 역량
        MATCH (p:Project {{status: 'PLANNED'}})-[:OWNED_BY]->(ou:OrgUnit)
        WHERE 1=1 {org_filter}
        OPTIONAL MATCH (p)-[req:REQUIRES_COMPETENCY]->(c:Competency)

        WITH c, COUNT(p) AS demandingProjects

        // 공급 역량
        MATCH (e:Employee {{status: 'ACTIVE'}})-[r:HAS_COMPETENCY]->(c)
        WITH c, demandingProjects,
             COUNT(CASE WHEN r.level >= 4 THEN 1 END) AS expertCount,
             COUNT(CASE WHEN r.level >= 3 THEN 1 END) AS proficientCount,
             COUNT(e) AS totalWithCompetency

        RETURN c.competencyId AS competencyId,
               c.name AS competencyName,
               c.domain AS domain,
               c.category AS category,
               demandingProjects,
               expertCount,
               proficientCount,
               totalWithCompetency,
               demandingProjects - expertCount AS expertGap,
               CASE
                 WHEN expertCount = 0 AND demandingProjects > 0 THEN 'CRITICAL'
                 WHEN expertCount < demandingProjects * 0.5 THEN 'HIGH'
                 WHEN expertCount < demandingProjects THEN 'MEDIUM'
                 ELSE 'LOW'
               END AS gapSeverity
        ORDER BY expertGap DESC
        """

        params = {"orgUnitId": org_unit_id} if org_unit_id else {}

        with self._driver.session(database=self.database) as session:
            result = session.run(query, **params)
            data = [dict(record) for record in result]

        critical_gaps = [d for d in data if d.get("gapSeverity") == "CRITICAL"]

        evidence = [
            Evidence(
                evidence_id="EV-COMPGAP",
                evidence_type="COMPETENCY_GAP_ANALYSIS",
                source="KG_QUERY",
                description="역량 갭 분석",
                value={
                    "total_competencies_analyzed": len(data),
                    "critical_gaps": len(critical_gaps)
                },
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="COMPETENCY_GAP",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    # =========================================================
    # 그래프 탐색 쿼리
    # =========================================================

    def get_employee_network(
        self,
        employee_id: str,
        depth: int = 2
    ) -> QueryResult:
        """직원 중심 네트워크 조회"""
        start_time = datetime.now()

        query = """
        MATCH (e:Employee {employeeId: $employeeId})
        CALL apoc.path.subgraphAll(e, {
            maxLevel: $depth,
            relationshipFilter: 'BELONGS_TO|ASSIGNED_TO|HAS_COMPETENCY|WORKS_ON'
        }) YIELD nodes, relationships

        RETURN nodes, relationships
        """

        # APOC이 없는 경우 대체 쿼리
        fallback_query = """
        MATCH (e:Employee {employeeId: $employeeId})
        OPTIONAL MATCH (e)-[:BELONGS_TO]->(ou:OrgUnit)
        OPTIONAL MATCH (e)-[:ASSIGNED_TO]->(p:Project)
        OPTIONAL MATCH (e)-[:HAS_COMPETENCY]->(c:Competency)
        OPTIONAL MATCH (e)-[:HAS_JOB_ROLE]->(jr:JobRole)
        OPTIONAL MATCH (e)-[:HAS_DELIVERY_ROLE]->(dr:DeliveryRole)

        RETURN e AS employee,
               ou AS orgUnit,
               COLLECT(DISTINCT p) AS projects,
               COLLECT(DISTINCT c) AS competencies,
               jr AS jobRole,
               dr AS deliveryRole
        """

        with self._driver.session(database=self.database) as session:
            try:
                result = session.run(query, employeeId=employee_id, depth=depth)
                data = [dict(record) for record in result]
            except Exception:
                # APOC 없으면 대체 쿼리 사용
                result = session.run(fallback_query, employeeId=employee_id)
                data = [dict(record) for record in result]

        evidence = [
            Evidence(
                evidence_id=f"EV-NET-{employee_id}",
                evidence_type="NETWORK_ANALYSIS",
                source="KG_QUERY",
                description=f"직원 {employee_id} 네트워크 분석",
                value={"depth": depth},
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="EMPLOYEE_NETWORK",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )

    def get_project_team(
        self,
        project_id: str
    ) -> QueryResult:
        """프로젝트 팀 구성 조회"""
        start_time = datetime.now()

        query = """
        MATCH (p:Project {projectId: $projectId})
        OPTIONAL MATCH (p)-[:MANAGED_BY]->(pm:Employee)
        OPTIONAL MATCH (p)<-[a:ASSIGNED_TO]-(e:Employee)
        OPTIONAL MATCH (p)-[:CONTAINS]->(wp:WorkPackage)

        WITH p, pm, COLLECT(DISTINCT {
            employee: e,
            allocation: a.allocationFTE,
            role: a.role
        }) AS teamMembers, COLLECT(DISTINCT wp) AS workPackages

        RETURN p.projectId AS projectId,
               p.name AS projectName,
               p.status AS status,
               pm.name AS projectManager,
               teamMembers,
               workPackages,
               SIZE(teamMembers) AS teamSize
        """

        with self._driver.session(database=self.database) as session:
            result = session.run(query, projectId=project_id)
            data = [dict(record) for record in result]

        evidence = [
            Evidence(
                evidence_id=f"EV-TEAM-{project_id}",
                evidence_type="PROJECT_TEAM",
                source="KG_QUERY",
                description=f"프로젝트 {project_id} 팀 구성",
                value={"team_size": data[0].get("teamSize", 0) if data else 0},
                timestamp=datetime.now()
            )
        ]

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return QueryResult(
            query_type="PROJECT_TEAM",
            data=data,
            evidence=evidence,
            execution_time_ms=duration,
            total_count=len(data)
        )


# CLI 테스트용
if __name__ == "__main__":
    import os

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    try:
        with KnowledgeGraphQuery(uri, username, password) as kg:
            print("KG Query 테스트")
            print("=" * 60)

            # 조직 가동률 조회
            result = kg.get_org_utilization(
                "ORG-0011",
                date(2025, 1, 1),
                date(2025, 3, 31)
            )
            print(f"\n[조직 가동률] {result.total_count}건, {result.execution_time_ms:.1f}ms")
            for d in result.data:
                print(f"  {d}")

    except Exception as e:
        print(f"Error: {e}")
