"""
HR DSS - Neo4j Data Loader

Mock 데이터를 Neo4j Knowledge Graph에 적재하는 모듈

v0.1.2 업데이트:
- Decision/Workflow 도메인 노드 로딩 추가
- Forecast/Explainability 도메인 노드 로딩 추가
- Learning 도메인 노드 로딩 추가
- 신규 Relationship 타입 지원
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from neo4j import Driver, GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = Any  # type hint용

logger = logging.getLogger(__name__)


@dataclass
class LoadResult:
    """데이터 적재 결과"""
    entity_type: str
    records_processed: int
    records_created: int
    records_updated: int
    errors: list[str]
    duration_ms: float


@dataclass
class LoadSummary:
    """전체 적재 요약"""
    started_at: datetime
    completed_at: datetime
    total_nodes: int
    total_relationships: int
    results: list[LoadResult]
    success: bool
    error_message: str | None = None


class Neo4jDataLoader:
    """Neo4j 데이터 적재기"""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        database: str = "neo4j"
    ):
        if not NEO4J_AVAILABLE:
            raise ImportError(
                "neo4j 패키지가 설치되지 않았습니다. "
                "'pip install neo4j'로 설치해주세요."
            )

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
        # 연결 테스트
        self._driver.verify_connectivity()
        logger.info(f"Neo4j 연결 성공: {self.uri}")

    def close(self) -> None:
        """연결 종료"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j 연결 종료")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def clear_database(self) -> None:
        """데이터베이스 초기화 (모든 노드/관계 삭제)"""
        with self._driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("데이터베이스 초기화 완료")

    def create_constraints_and_indexes(self, schema_path: str | Path) -> None:
        """스키마 파일에서 제약조건 및 인덱스 생성"""
        schema_path = Path(schema_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"스키마 파일을 찾을 수 없습니다: {schema_path}")

        with open(schema_path, encoding="utf-8") as f:
            schema_content = f.read()

        # CREATE CONSTRAINT와 CREATE INDEX 문을 추출 (멀티라인 지원)
        statements = []
        current_statement = []
        in_statement = False

        for line in schema_content.split("\n"):
            line_stripped = line.strip()

            # 주석이나 빈 줄 건너뛰기 (문장 중간이 아닐 때만)
            if not in_statement:
                if not line_stripped or line_stripped.startswith("//"):
                    continue

            # CREATE CONSTRAINT 또는 CREATE INDEX로 시작하면 문장 시작
            if line_stripped.startswith("CREATE CONSTRAINT") or line_stripped.startswith("CREATE INDEX"):
                in_statement = True
                current_statement = [line_stripped]
            elif in_statement:
                current_statement.append(line_stripped)

            # 세미콜론으로 끝나면 문장 완료
            if in_statement and line_stripped.endswith(";"):
                stmt = " ".join(current_statement)
                statements.append(stmt)
                current_statement = []
                in_statement = False

        with self._driver.session(database=self.database) as session:
            for stmt in statements:
                try:
                    session.run(stmt)
                    logger.debug(f"스키마 문 실행: {stmt[:50]}...")
                except Exception as e:
                    # 이미 존재하는 경우 무시
                    if "already exists" not in str(e).lower():
                        logger.warning(f"스키마 문 실행 실패: {e}")

        logger.info(f"스키마 생성 완료: {len(statements)}개 문 처리")

    def load_all_mock_data(self, data_dir: str | Path) -> LoadSummary:
        """모든 Mock 데이터 적재"""
        data_dir = Path(data_dir)
        started_at = datetime.now()
        results = []
        total_nodes = 0
        total_rels = 0

        # 1. 조직 데이터 로드 (orgUnits, jobRoles, deliveryRoles, responsibilities)
        orgs_result = self._load_orgs(data_dir / "orgs.json")
        results.append(orgs_result)
        total_nodes += orgs_result.records_created

        # 2. 인력 데이터 로드 (employees)
        persons_result = self._load_persons(data_dir / "persons.json")
        results.append(persons_result)
        total_nodes += persons_result.records_created

        # 3. 프로젝트 데이터 로드 (projects, workPackages, clients, industries)
        projects_result = self._load_projects(data_dir / "projects.json")
        results.append(projects_result)
        total_nodes += projects_result.records_created

        # 4. 기회 데이터 로드 (opportunities, demandSignals, resourceDemands)
        opps_result = self._load_opportunities(data_dir / "opportunities.json")
        results.append(opps_result)
        total_nodes += opps_result.records_created

        # 5. 역량 데이터 로드 (competencies, competencyEvidences, requirements)
        skills_result = self._load_skills(data_dir / "skills.json")
        results.append(skills_result)
        total_nodes += skills_result.records_created

        # 6. 배치 데이터 로드 (assignments, availabilities, timeBuckets)
        assignments_result = self._load_assignments(data_dir / "assignments.json")
        results.append(assignments_result)
        total_nodes += assignments_result.records_created

        # 7. 학습 데이터 로드 (learningPrograms, courses, enrollments, certifications)
        learning_path = data_dir / "learning.json"
        if learning_path.exists():
            learning_result = self._load_learning(learning_path)
            results.append(learning_result)
            total_nodes += learning_result.records_created

        # 8. 의사결정 데이터 로드 (decisionCases, objectives, constraints, options, etc.)
        decisions_path = data_dir / "decisions.json"
        if decisions_path.exists():
            decisions_result = self._load_decisions(decisions_path)
            results.append(decisions_result)
            total_nodes += decisions_result.records_created

        # 9. 예측/모델 데이터 로드 (models, modelRuns, forecastPoints, findings, evidence)
        forecasts_path = data_dir / "forecasts.json"
        if forecasts_path.exists():
            forecasts_result = self._load_forecasts(forecasts_path)
            results.append(forecasts_result)
            total_nodes += forecasts_result.records_created

        # 10. 워크플로 데이터 로드 (workflowInstances, workflowTasks, approvals)
        workflows_path = data_dir / "workflows.json"
        if workflows_path.exists():
            workflows_result = self._load_workflows(workflows_path)
            results.append(workflows_result)
            total_nodes += workflows_result.records_created

        # 11. 관계 생성
        rels_result = self._create_relationships()
        results.append(rels_result)
        total_rels = rels_result.records_created

        completed_at = datetime.now()

        return LoadSummary(
            started_at=started_at,
            completed_at=completed_at,
            total_nodes=total_nodes,
            total_relationships=total_rels,
            results=results,
            success=all(len(r.errors) == 0 for r in results)
        )

    def _load_orgs(self, filepath: Path) -> LoadResult:
        """조직 데이터 로드"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="orgs",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # OrgUnits
            for org in data.get("orgUnits", []):
                try:
                    # 선택적 필드에 기본값 제공
                    org_data = {
                        "orgUnitId": org.get("orgUnitId"),
                        "name": org.get("name"),
                        "type": org.get("type"),
                        "status": org.get("status", "ACTIVE"),
                        "headCount": org.get("headCount", 0),
                        "parentOrgUnitId": org.get("parentOrgUnitId")
                    }
                    session.run("""
                        MERGE (o:OrgUnit {orgUnitId: $orgUnitId})
                        SET o.name = $name,
                            o.type = $type,
                            o.status = $status,
                            o.headCount = $headCount,
                            o.parentOrgUnitId = $parentOrgUnitId
                    """, **org_data)
                    created += 1
                except Exception as e:
                    errors.append(f"OrgUnit {org.get('orgUnitId')}: {e}")

            # JobRoles
            for role in data.get("jobRoles", []):
                try:
                    role_data = {
                        "jobRoleId": role.get("jobRoleId"),
                        "name": role.get("name"),
                        "category": role.get("category", "GENERAL"),
                        "level": role.get("level", "STAFF"),
                        "description": role.get("description", "")
                    }
                    session.run("""
                        MERGE (j:JobRole {jobRoleId: $jobRoleId})
                        SET j.name = $name,
                            j.category = $category,
                            j.level = $level,
                            j.description = $description
                    """, **role_data)
                    created += 1
                except Exception as e:
                    errors.append(f"JobRole {role.get('jobRoleId')}: {e}")

            # DeliveryRoles
            for role in data.get("deliveryRoles", []):
                try:
                    session.run("""
                        MERGE (d:DeliveryRole {deliveryRoleId: $deliveryRoleId})
                        SET d.name = $name,
                            d.category = $category,
                            d.description = $description
                    """, **role)
                    created += 1
                except Exception as e:
                    errors.append(f"DeliveryRole {role.get('deliveryRoleId')}: {e}")

            # Responsibilities
            for resp in data.get("responsibilities", []):
                try:
                    session.run("""
                        MERGE (r:Responsibility {responsibilityId: $responsibilityId})
                        SET r.name = $name,
                            r.description = $description,
                            r.category = $category
                    """, **resp)
                    created += 1
                except Exception as e:
                    errors.append(f"Responsibility {resp.get('responsibilityId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="orgs",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_persons(self, filepath: Path) -> LoadResult:
        """인력 데이터 로드"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="persons",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            for emp in data.get("employees", []):
                try:
                    # 선택적 필드에 기본값 제공
                    emp_data = {
                        "employeeId": emp.get("employeeId"),
                        "name": emp.get("name"),
                        "email": emp.get("email"),
                        "grade": emp.get("grade"),
                        "status": emp.get("status", "ACTIVE"),
                        "hireDate": emp.get("hireDate"),
                        "orgUnitId": emp.get("orgUnitId"),
                        "jobRoleId": emp.get("jobRoleId"),
                        "deliveryRoleId": emp.get("deliveryRoleId"),
                        "location": emp.get("location", "서울"),
                        "costRate": emp.get("costRate", 0)
                    }
                    session.run("""
                        MERGE (e:Employee {employeeId: $employeeId})
                        SET e.name = $name,
                            e.email = $email,
                            e.grade = $grade,
                            e.status = $status,
                            e.hireDate = date($hireDate),
                            e.orgUnitId = $orgUnitId,
                            e.jobRoleId = $jobRoleId,
                            e.deliveryRoleId = $deliveryRoleId,
                            e.location = $location,
                            e.costRate = $costRate
                    """, **emp_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Employee {emp.get('employeeId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="persons",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_projects(self, filepath: Path) -> LoadResult:
        """프로젝트 데이터 로드"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="projects",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # Projects
            for proj in data.get("projects", []):
                try:
                    session.run("""
                        MERGE (p:Project {projectId: $projectId})
                        SET p.name = $name,
                            p.opportunityId = $opportunityId,
                            p.status = $status,
                            p.startDate = date($startDate),
                            p.endDate = date($endDate),
                            p.priority = $priority,
                            p.pmEmployeeId = $pmEmployeeId,
                            p.ownerOrgUnitId = $ownerOrgUnitId,
                            p.budgetAmount = $budgetAmount,
                            p.actualCost = $actualCost
                    """, **proj)
                    created += 1
                except Exception as e:
                    errors.append(f"Project {proj.get('projectId')}: {e}")

            # WorkPackages
            for wp in data.get("workPackages", []):
                try:
                    session.run("""
                        MERGE (w:WorkPackage {workPackageId: $workPackageId})
                        SET w.projectId = $projectId,
                            w.name = $name,
                            w.startDate = date($startDate),
                            w.endDate = date($endDate),
                            w.criticality = $criticality,
                            w.estimatedFTE = $estimatedFTE,
                            w.status = $status
                    """, **wp)
                    created += 1
                except Exception as e:
                    errors.append(f"WorkPackage {wp.get('workPackageId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="projects",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_opportunities(self, filepath: Path) -> LoadResult:
        """기회 데이터 로드"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="opportunities",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # Opportunities
            for opp in data.get("opportunities", []):
                try:
                    # 선택적 필드에 기본값 제공
                    opp_data = {
                        "opportunityId": opp.get("opportunityId"),
                        "name": opp.get("name"),
                        "customerId": opp.get("customerId", opp.get("clientId")),
                        "customerName": opp.get("customerName", opp.get("clientName")),
                        "stage": opp.get("stage"),
                        "dealValue": opp.get("dealValue", opp.get("value", 0)),
                        "closeProbability": opp.get("closeProbability", opp.get("probability", 0)),
                        "expectedCloseDate": opp.get("expectedCloseDate", opp.get("closeDate")),
                        "estimatedFTE": opp.get("estimatedFTE", opp.get("requiredFTE", 0)),
                        "estimatedDuration": opp.get("estimatedDuration", opp.get("duration", 0)),
                        "ownerOrgUnitId": opp.get("ownerOrgUnitId", opp.get("orgUnitId")),
                        "salesOwnerId": opp.get("salesOwnerId", opp.get("ownerId"))
                    }
                    session.run("""
                        MERGE (o:Opportunity {opportunityId: $opportunityId})
                        SET o.name = $name,
                            o.customerId = $customerId,
                            o.customerName = $customerName,
                            o.stage = $stage,
                            o.dealValue = $dealValue,
                            o.closeProbability = $closeProbability,
                            o.expectedCloseDate = date($expectedCloseDate),
                            o.estimatedFTE = $estimatedFTE,
                            o.estimatedDuration = $estimatedDuration,
                            o.ownerOrgUnitId = $ownerOrgUnitId,
                            o.salesOwnerId = $salesOwnerId
                    """, **opp_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Opportunity {opp.get('opportunityId')}: {e}")

            # DemandSignals
            for sig in data.get("demandSignals", []):
                try:
                    sig_data = {
                        "signalId": sig.get("signalId"),
                        "signalType": sig.get("signalType", sig.get("type")),
                        "sourceType": sig.get("sourceType", "OPPORTUNITY"),
                        "sourceId": sig.get("sourceId", sig.get("opportunityId")),
                        "detectedAt": sig.get("detectedAt", "2025-01-01T00:00:00Z"),
                        "effectiveFrom": sig.get("effectiveFrom", sig.get("startDate", "2025-01-01")),
                        "estimatedFTEChange": sig.get("estimatedFTEChange", sig.get("requiredFTE", 0)),
                        "confidence": sig.get("confidence", sig.get("probability", 0.5)),
                        "status": sig.get("status", "PENDING")
                    }
                    session.run("""
                        MERGE (d:DemandSignal {signalId: $signalId})
                        SET d.signalType = $signalType,
                            d.sourceType = $sourceType,
                            d.sourceId = $sourceId,
                            d.detectedAt = datetime($detectedAt),
                            d.effectiveFrom = date($effectiveFrom),
                            d.estimatedFTEChange = $estimatedFTEChange,
                            d.confidence = $confidence,
                            d.status = $status
                    """, **sig_data)
                    created += 1
                except Exception as e:
                    errors.append(f"DemandSignal {sig.get('signalId')}: {e}")

            # ResourceDemands
            for dem in data.get("resourceDemands", []):
                try:
                    session.run("""
                        MERGE (r:ResourceDemand {demandId: $demandId})
                        SET r.sourceType = $sourceType,
                            r.sourceId = $sourceId,
                            r.requestedOrgUnitId = $requestedOrgUnitId,
                            r.quantityFTE = $quantityFTE,
                            r.startDate = date($startDate),
                            r.endDate = date($endDate),
                            r.probability = $probability,
                            r.priority = $priority,
                            r.status = $status,
                            r.requiredCompetencies = $requiredCompetencies
                    """, **dem)
                    created += 1
                except Exception as e:
                    errors.append(f"ResourceDemand {dem.get('demandId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="opportunities",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_skills(self, filepath: Path) -> LoadResult:
        """역량 데이터 로드"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="skills",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # Competencies
            for comp in data.get("competencies", []):
                try:
                    # 선택적 필드에 기본값 제공
                    comp_data = {
                        "competencyId": comp.get("competencyId"),
                        "name": comp.get("name"),
                        "domain": comp.get("domain", "GENERAL"),
                        "category": comp.get("category"),
                        "description": comp.get("description", "")
                    }
                    session.run("""
                        MERGE (c:Competency {competencyId: $competencyId})
                        SET c.name = $name,
                            c.domain = $domain,
                            c.category = $category,
                            c.description = $description
                    """, **comp_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Competency {comp.get('competencyId')}: {e}")

            # CompetencyEvidences
            for ev in data.get("competencyEvidences", []):
                try:
                    ev_data = {
                        "evidenceId": ev.get("evidenceId"),
                        "employeeId": ev.get("employeeId"),
                        "competencyId": ev.get("competencyId"),
                        "level": ev.get("level", 1),
                        "assessmentDate": ev.get("assessmentDate", ev.get("evaluatedAt", "2025-01-01")),
                        "assessmentType": ev.get("assessmentType", ev.get("source", "SELF")),
                        "validUntil": ev.get("validUntil", ev.get("expiresAt")),
                        "notes": ev.get("notes", "")
                    }
                    session.run("""
                        MERGE (ce:CompetencyEvidence {evidenceId: $evidenceId})
                        SET ce.employeeId = $employeeId,
                            ce.competencyId = $competencyId,
                            ce.level = $level,
                            ce.assessmentDate = date($assessmentDate),
                            ce.assessmentType = $assessmentType,
                            ce.validUntil = CASE WHEN $validUntil IS NOT NULL THEN date($validUntil) ELSE NULL END,
                            ce.notes = $notes
                    """, **ev_data)
                    created += 1
                except Exception as e:
                    errors.append(f"CompetencyEvidence {ev.get('evidenceId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="skills",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_assignments(self, filepath: Path) -> LoadResult:
        """배치 데이터 로드"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="assignments",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # Assignments
            for asn in data.get("assignments", []):
                try:
                    # 선택적 필드에 기본값 제공
                    asn_data = {
                        "assignmentId": asn.get("assignmentId"),
                        "employeeId": asn.get("employeeId"),
                        "projectId": asn.get("projectId"),
                        "workPackageId": asn.get("workPackageId"),
                        "role": asn.get("role", asn.get("deliveryRole")),
                        "allocationFTE": asn.get("allocationFTE", asn.get("allocation", 1.0)),
                        "startDate": asn.get("startDate"),
                        "endDate": asn.get("endDate"),
                        "status": asn.get("status", "ACTIVE"),
                        "billable": asn.get("billable", True)
                    }
                    session.run("""
                        MERGE (a:Assignment {assignmentId: $assignmentId})
                        SET a.employeeId = $employeeId,
                            a.projectId = $projectId,
                            a.workPackageId = $workPackageId,
                            a.role = $role,
                            a.allocationFTE = $allocationFTE,
                            a.startDate = date($startDate),
                            a.endDate = date($endDate),
                            a.status = $status,
                            a.billable = $billable
                    """, **asn_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Assignment {asn.get('assignmentId')}: {e}")

            # Availabilities
            for av in data.get("availabilities", []):
                try:
                    av_data = {
                        "availabilityId": av.get("availabilityId"),
                        "employeeId": av.get("employeeId"),
                        "timeBucketId": av.get("timeBucketId", av.get("weekId")),
                        "availableFTE": av.get("availableFTE", av.get("available", 1.0)),
                        "reason": av.get("reason", "")
                    }
                    session.run("""
                        MERGE (av:Availability {availabilityId: $availabilityId})
                        SET av.employeeId = $employeeId,
                            av.timeBucketId = $timeBucketId,
                            av.availableFTE = $availableFTE,
                            av.reason = $reason
                    """, **av_data)
                    created += 1
                except Exception as e:
                    errors.append(f"Availability {av.get('availabilityId')}: {e}")

            # TimeBuckets
            for tb in data.get("timeBuckets", []):
                try:
                    session.run("""
                        MERGE (t:TimeBucket {bucketId: $bucketId})
                        SET t.bucketType = $bucketType,
                            t.bucketStart = date($bucketStart),
                            t.bucketEnd = date($bucketEnd),
                            t.label = $label
                    """, **tb)
                    created += 1
                except Exception as e:
                    errors.append(f"TimeBucket {tb.get('bucketId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="assignments",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_learning(self, filepath: Path) -> LoadResult:
        """학습 데이터 로드 (LearningProgram, Course, Enrollment, Certification)"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="learning",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # LearningPrograms
            for prog in data.get("learningPrograms", []):
                try:
                    session.run("""
                        MERGE (lp:LearningProgram {programId: $programId})
                        SET lp.name = $name,
                            lp.deliveryMode = $deliveryMode,
                            lp.description = $description,
                            lp.durationHours = $durationHours
                    """, **prog)
                    created += 1
                except Exception as e:
                    errors.append(f"LearningProgram {prog.get('programId')}: {e}")

            # Courses
            for course in data.get("courses", []):
                try:
                    session.run("""
                        MERGE (c:Course {courseId: $courseId})
                        SET c.title = $title,
                            c.deliveryMode = $deliveryMode,
                            c.programId = $programId,
                            c.durationHours = $durationHours,
                            c.competencyId = $competencyId
                    """, **course)
                    created += 1
                except Exception as e:
                    errors.append(f"Course {course.get('courseId')}: {e}")

            # Enrollments
            for enroll in data.get("enrollments", []):
                try:
                    session.run("""
                        MERGE (en:Enrollment {enrollmentId: $enrollmentId})
                        SET en.employeeId = $employeeId,
                            en.courseId = $courseId,
                            en.status = $status,
                            en.plannedStart = date($plannedStart),
                            en.plannedEnd = date($plannedEnd),
                            en.completedAt = CASE WHEN $completedAt IS NOT NULL
                                             THEN date($completedAt) ELSE NULL END
                    """, **enroll)
                    created += 1
                except Exception as e:
                    errors.append(f"Enrollment {enroll.get('enrollmentId')}: {e}")

            # Certifications
            for cert in data.get("certifications", []):
                try:
                    session.run("""
                        MERGE (cert:Certification {certificationId: $certificationId})
                        SET cert.name = $name,
                            cert.level = $level,
                            cert.issuingOrg = $issuingOrg,
                            cert.validityMonths = $validityMonths
                    """, **cert)
                    created += 1
                except Exception as e:
                    errors.append(f"Certification {cert.get('certificationId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="learning",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_decisions(self, filepath: Path) -> LoadResult:
        """의사결정 데이터 로드 (DecisionCase, Objective, Constraint, Option, Scenario, Action, etc.)"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="decisions",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # DecisionCases
            for dc in data.get("decisionCases", []):
                try:
                    session.run("""
                        MERGE (dc:DecisionCase {decisionCaseId: $decisionCaseId})
                        SET dc.type = $type,
                            dc.status = $status,
                            dc.createdAt = datetime($createdAt),
                            dc.requester = $requester,
                            dc.dueDate = CASE WHEN $dueDate IS NOT NULL
                                         THEN date($dueDate) ELSE NULL END,
                            dc.summary = $summary,
                            dc.targetType = $targetType,
                            dc.targetId = $targetId
                    """, **dc)
                    created += 1
                except Exception as e:
                    errors.append(f"DecisionCase {dc.get('decisionCaseId')}: {e}")

            # Objectives
            for obj in data.get("objectives", []):
                try:
                    session.run("""
                        MERGE (obj:Objective {objectiveId: $objectiveId})
                        SET obj.decisionCaseId = $decisionCaseId,
                            obj.metricType = $metricType,
                            obj.operator = $operator,
                            obj.targetValue = $targetValue,
                            obj.scopeType = $scopeType,
                            obj.horizonStart = CASE WHEN $horizonStart IS NOT NULL
                                               THEN date($horizonStart) ELSE NULL END,
                            obj.horizonEnd = CASE WHEN $horizonEnd IS NOT NULL
                                             THEN date($horizonEnd) ELSE NULL END
                    """, **obj)
                    created += 1
                except Exception as e:
                    errors.append(f"Objective {obj.get('objectiveId')}: {e}")

            # Constraints
            for con in data.get("constraints", []):
                try:
                    session.run("""
                        MERGE (con:Constraint {constraintId: $constraintId})
                        SET con.decisionCaseId = $decisionCaseId,
                            con.type = $type,
                            con.severity = $severity,
                            con.expression = $expression,
                            con.startDate = CASE WHEN $startDate IS NOT NULL
                                            THEN date($startDate) ELSE NULL END,
                            con.endDate = CASE WHEN $endDate IS NOT NULL
                                          THEN date($endDate) ELSE NULL END,
                            con.appliesToType = $appliesToType,
                            con.appliesToId = $appliesToId
                    """, **con)
                    created += 1
                except Exception as e:
                    errors.append(f"Constraint {con.get('constraintId')}: {e}")

            # Options
            for opt in data.get("options", []):
                try:
                    session.run("""
                        MERGE (opt:Option {optionId: $optionId})
                        SET opt.decisionCaseId = $decisionCaseId,
                            opt.name = $name,
                            opt.optionType = $optionType,
                            opt.description = $description
                    """, **opt)
                    created += 1
                except Exception as e:
                    errors.append(f"Option {opt.get('optionId')}: {e}")

            # Scenarios
            for sc in data.get("scenarios", []):
                try:
                    session.run("""
                        MERGE (sc:Scenario {scenarioId: $scenarioId})
                        SET sc.optionId = $optionId,
                            sc.baselineSnapshotId = $baselineSnapshotId,
                            sc.assumptions = $assumptions
                    """, **sc)
                    created += 1
                except Exception as e:
                    errors.append(f"Scenario {sc.get('scenarioId')}: {e}")

            # Actions
            for act in data.get("actions", []):
                try:
                    session.run("""
                        MERGE (act:Action {actionId: $actionId})
                        SET act.scenarioId = $scenarioId,
                            act.type = $type,
                            act.owner = $owner,
                            act.startDate = CASE WHEN $startDate IS NOT NULL
                                            THEN date($startDate) ELSE NULL END,
                            act.endDate = CASE WHEN $endDate IS NOT NULL
                                          THEN date($endDate) ELSE NULL END,
                            act.status = $status,
                            act.description = $description
                    """, **act)
                    created += 1
                except Exception as e:
                    errors.append(f"Action {act.get('actionId')}: {e}")

            # Evaluations
            for ev in data.get("evaluations", []):
                try:
                    session.run("""
                        MERGE (ev:Evaluation {evaluationId: $evaluationId})
                        SET ev.optionId = $optionId,
                            ev.totalScore = $totalScore,
                            ev.successProbability = $successProbability,
                            ev.rationale = $rationale
                    """, **ev)
                    created += 1
                except Exception as e:
                    errors.append(f"Evaluation {ev.get('evaluationId')}: {e}")

            # MetricValues
            for mv in data.get("metricValues", []):
                try:
                    session.run("""
                        MERGE (mv:MetricValue {metricValueId: $metricValueId})
                        SET mv.evaluationId = $evaluationId,
                            mv.metricType = $metricType,
                            mv.asIsValue = $asIsValue,
                            mv.toBeValue = $toBeValue,
                            mv.delta = $delta,
                            mv.unit = $unit
                    """, **mv)
                    created += 1
                except Exception as e:
                    errors.append(f"MetricValue {mv.get('metricValueId')}: {e}")

            # ImpactAssessments
            for ia in data.get("impactAssessments", []):
                try:
                    session.run("""
                        MERGE (ia:ImpactAssessment {impactId: $impactId})
                        SET ia.optionId = $optionId,
                            ia.dimension = $dimension,
                            ia.value = $value,
                            ia.narrative = $narrative
                    """, **ia)
                    created += 1
                except Exception as e:
                    errors.append(f"ImpactAssessment {ia.get('impactId')}: {e}")

            # Risks
            for risk in data.get("risks", []):
                try:
                    session.run("""
                        MERGE (r:Risk {riskId: $riskId})
                        SET r.optionId = $optionId,
                            r.category = $category,
                            r.probability = $probability,
                            r.impact = $impact,
                            r.score = $score,
                            r.description = $description
                    """, **risk)
                    created += 1
                except Exception as e:
                    errors.append(f"Risk {risk.get('riskId')}: {e}")

            # DecisionGates
            for gate in data.get("decisionGates", []):
                try:
                    session.run("""
                        MERGE (g:DecisionGate {gateId: $gateId})
                        SET g.decisionCaseId = $decisionCaseId,
                            g.process = $process,
                            g.name = $name,
                            g.sequence = $sequence,
                            g.status = $status
                    """, **gate)
                    created += 1
                except Exception as e:
                    errors.append(f"DecisionGate {gate.get('gateId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="decisions",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_forecasts(self, filepath: Path) -> LoadResult:
        """예측/모델 데이터 로드 (Model, ModelRun, ForecastPoint, Finding, Evidence, DataSnapshot)"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="forecasts",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # Models
            for model in data.get("models", []):
                try:
                    session.run("""
                        MERGE (m:Model {modelId: $modelId})
                        SET m.name = $name,
                            m.type = $type,
                            m.version = $version,
                            m.description = $description
                    """, **model)
                    created += 1
                except Exception as e:
                    errors.append(f"Model {model.get('modelId')}: {e}")

            # DataSnapshots
            for snap in data.get("dataSnapshots", []):
                try:
                    session.run("""
                        MERGE (ds:DataSnapshot {snapshotId: $snapshotId})
                        SET ds.asOf = datetime($asOf),
                            ds.datasetVersions = $datasetVersions,
                            ds.description = $description
                    """, **snap)
                    created += 1
                except Exception as e:
                    errors.append(f"DataSnapshot {snap.get('snapshotId')}: {e}")

            # ModelRuns
            for run in data.get("modelRuns", []):
                try:
                    # 선택적 필드에 기본값 제공
                    run_data = {
                        "runId": run.get("runId"),
                        "modelId": run.get("modelId"),
                        "scenarioId": run.get("scenarioId"),
                        "snapshotId": run.get("snapshotId"),
                        "runAt": run.get("runAt"),
                        "parameters": run.get("parameters", "{}"),
                        "status": run.get("status", "COMPLETED")
                    }
                    session.run("""
                        MERGE (mr:ModelRun {runId: $runId})
                        SET mr.modelId = $modelId,
                            mr.scenarioId = $scenarioId,
                            mr.snapshotId = $snapshotId,
                            mr.runAt = datetime($runAt),
                            mr.parameters = $parameters,
                            mr.status = $status
                    """, **run_data)
                    created += 1
                except Exception as e:
                    errors.append(f"ModelRun {run.get('runId')}: {e}")

            # ForecastPoints
            for fp in data.get("forecastPoints", []):
                try:
                    session.run("""
                        MERGE (fp:ForecastPoint {forecastPointId: $forecastPointId})
                        SET fp.runId = $runId,
                            fp.metricType = $metricType,
                            fp.value = $value,
                            fp.unit = $unit,
                            fp.lowerBound = $lowerBound,
                            fp.upperBound = $upperBound,
                            fp.confidence = $confidence,
                            fp.method = $method,
                            fp.bucketId = $bucketId,
                            fp.subjectType = $subjectType,
                            fp.subjectId = $subjectId
                    """, **fp)
                    created += 1
                except Exception as e:
                    errors.append(f"ForecastPoint {fp.get('forecastPointId')}: {e}")

            # Findings
            for finding in data.get("findings", []):
                try:
                    session.run("""
                        MERGE (f:Finding {findingId: $findingId})
                        SET f.runId = $runId,
                            f.type = $type,
                            f.severity = $severity,
                            f.narrative = $narrative,
                            f.rootCause = $rootCause,
                            f.rank = $rank,
                            f.affectsType = $affectsType,
                            f.affectsId = $affectsId
                    """, **finding)
                    created += 1
                except Exception as e:
                    errors.append(f"Finding {finding.get('findingId')}: {e}")

            # Evidence
            for ev in data.get("evidence", []):
                try:
                    session.run("""
                        MERGE (ev:Evidence {evidenceId: $evidenceId})
                        SET ev.findingId = $findingId,
                            ev.sourceSystem = $sourceSystem,
                            ev.sourceType = $sourceType,
                            ev.sourceRef = $sourceRef,
                            ev.capturedAt = datetime($capturedAt),
                            ev.note = $note
                    """, **ev)
                    created += 1
                except Exception as e:
                    errors.append(f"Evidence {ev.get('evidenceId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="forecasts",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _load_workflows(self, filepath: Path) -> LoadResult:
        """워크플로 데이터 로드 (Approval, WorkflowInstance, WorkflowTask)"""
        start_time = datetime.now()
        errors = []
        created = 0

        if not filepath.exists():
            return LoadResult(
                entity_type="workflows",
                records_processed=0,
                records_created=0,
                records_updated=0,
                errors=[f"파일을 찾을 수 없음: {filepath}"],
                duration_ms=0
            )

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        with self._driver.session(database=self.database) as session:
            # Approvals
            for ap in data.get("approvals", []):
                try:
                    session.run("""
                        MERGE (ap:Approval {approvalId: $approvalId})
                        SET ap.gateId = $gateId,
                            ap.decision = $decision,
                            ap.approvedBy = $approvedBy,
                            ap.approvedAt = datetime($approvedAt),
                            ap.comment = $comment
                    """, **ap)
                    created += 1
                except Exception as e:
                    errors.append(f"Approval {ap.get('approvalId')}: {e}")

            # WorkflowInstances
            for wi in data.get("workflowInstances", []):
                try:
                    session.run("""
                        MERGE (wi:WorkflowInstance {workflowId: $workflowId})
                        SET wi.approvalId = $approvalId,
                            wi.type = $type,
                            wi.status = $status,
                            wi.startedAt = datetime($startedAt),
                            wi.completedAt = CASE WHEN $completedAt IS NOT NULL
                                             THEN datetime($completedAt) ELSE NULL END
                    """, **wi)
                    created += 1
                except Exception as e:
                    errors.append(f"WorkflowInstance {wi.get('workflowId')}: {e}")

            # WorkflowTasks
            for wt in data.get("workflowTasks", []):
                try:
                    session.run("""
                        MERGE (wt:WorkflowTask {taskId: $taskId})
                        SET wt.workflowId = $workflowId,
                            wt.actionId = $actionId,
                            wt.type = $type,
                            wt.owner = $owner,
                            wt.dueDate = CASE WHEN $dueDate IS NOT NULL
                                         THEN date($dueDate) ELSE NULL END,
                            wt.status = $status,
                            wt.completedAt = CASE WHEN $completedAt IS NOT NULL
                                             THEN datetime($completedAt) ELSE NULL END
                    """, **wt)
                    created += 1
                except Exception as e:
                    errors.append(f"WorkflowTask {wt.get('taskId')}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="workflows",
            records_processed=created + len(errors),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def _create_relationships(self) -> LoadResult:
        """노드 간 관계 생성"""
        start_time = datetime.now()
        errors = []
        created = 0

        relationship_queries = [
            # Employee -> OrgUnit
            ("""
                MATCH (e:Employee), (o:OrgUnit)
                WHERE e.orgUnitId = o.orgUnitId
                MERGE (e)-[:BELONGS_TO]->(o)
            """, "Employee-BELONGS_TO-OrgUnit"),

            # Employee -> JobRole
            ("""
                MATCH (e:Employee), (j:JobRole)
                WHERE e.jobRoleId = j.jobRoleId
                MERGE (e)-[:HAS_JOB_ROLE]->(j)
            """, "Employee-HAS_JOB_ROLE-JobRole"),

            # Employee -> DeliveryRole
            ("""
                MATCH (e:Employee), (d:DeliveryRole)
                WHERE e.deliveryRoleId = d.deliveryRoleId
                MERGE (e)-[:HAS_DELIVERY_ROLE]->(d)
            """, "Employee-HAS_DELIVERY_ROLE-DeliveryRole"),

            # OrgUnit -> OrgUnit (parent)
            ("""
                MATCH (child:OrgUnit), (parent:OrgUnit)
                WHERE child.parentOrgUnitId = parent.orgUnitId
                MERGE (child)-[:PART_OF]->(parent)
            """, "OrgUnit-PART_OF-OrgUnit"),

            # Project -> OrgUnit
            ("""
                MATCH (p:Project), (o:OrgUnit)
                WHERE p.ownerOrgUnitId = o.orgUnitId
                MERGE (p)-[:OWNED_BY]->(o)
            """, "Project-OWNED_BY-OrgUnit"),

            # Project -> Employee (PM)
            ("""
                MATCH (p:Project), (e:Employee)
                WHERE p.pmEmployeeId = e.employeeId
                MERGE (p)-[:MANAGED_BY]->(e)
            """, "Project-MANAGED_BY-Employee"),

            # Project -> Opportunity
            ("""
                MATCH (p:Project), (o:Opportunity)
                WHERE p.opportunityId = o.opportunityId
                MERGE (p)-[:ORIGINATED_FROM]->(o)
            """, "Project-ORIGINATED_FROM-Opportunity"),

            # WorkPackage -> Project
            ("""
                MATCH (w:WorkPackage), (p:Project)
                WHERE w.projectId = p.projectId
                MERGE (p)-[:CONTAINS]->(w)
            """, "Project-CONTAINS-WorkPackage"),

            # Assignment -> Employee
            ("""
                MATCH (a:Assignment), (e:Employee)
                WHERE a.employeeId = e.employeeId
                MERGE (a)-[:ASSIGNS]->(e)
            """, "Assignment-ASSIGNS-Employee"),

            # Assignment -> Project
            ("""
                MATCH (a:Assignment), (p:Project)
                WHERE a.projectId = p.projectId
                MERGE (a)-[:FOR_PROJECT]->(p)
            """, "Assignment-FOR_PROJECT-Project"),

            # Assignment -> WorkPackage
            ("""
                MATCH (a:Assignment), (w:WorkPackage)
                WHERE a.workPackageId = w.workPackageId
                MERGE (a)-[:FOR_WORK_PACKAGE]->(w)
            """, "Assignment-FOR_WORK_PACKAGE-WorkPackage"),

            # Employee -> Project (ASSIGNED_TO)
            ("""
                MATCH (a:Assignment)-[:ASSIGNS]->(e:Employee)
                MATCH (a)-[:FOR_PROJECT]->(p:Project)
                MERGE (e)-[r:ASSIGNED_TO]->(p)
                SET r.allocationFTE = a.allocationFTE,
                    r.startDate = a.startDate,
                    r.endDate = a.endDate
            """, "Employee-ASSIGNED_TO-Project"),

            # CompetencyEvidence -> Employee
            ("""
                MATCH (ce:CompetencyEvidence), (e:Employee)
                WHERE ce.employeeId = e.employeeId
                MERGE (ce)-[:BELONGS_TO_EMPLOYEE]->(e)
            """, "CompetencyEvidence-BELONGS_TO_EMPLOYEE-Employee"),

            # CompetencyEvidence -> Competency
            ("""
                MATCH (ce:CompetencyEvidence), (c:Competency)
                WHERE ce.competencyId = c.competencyId
                MERGE (ce)-[:EVIDENCES]->(c)
            """, "CompetencyEvidence-EVIDENCES-Competency"),

            # Employee -> Competency (HAS_COMPETENCY)
            ("""
                MATCH (ce:CompetencyEvidence)-[:BELONGS_TO_EMPLOYEE]->(e:Employee)
                MATCH (ce)-[:EVIDENCES]->(c:Competency)
                MERGE (e)-[r:HAS_COMPETENCY]->(c)
                SET r.level = ce.level,
                    r.assessedAt = ce.assessmentDate
            """, "Employee-HAS_COMPETENCY-Competency"),

            # Availability -> Employee
            ("""
                MATCH (av:Availability), (e:Employee)
                WHERE av.employeeId = e.employeeId
                MERGE (av)-[:FOR_EMPLOYEE]->(e)
            """, "Availability-FOR_EMPLOYEE-Employee"),

            # Availability -> TimeBucket
            ("""
                MATCH (av:Availability), (t:TimeBucket)
                WHERE av.timeBucketId = t.bucketId
                MERGE (av)-[:IN_BUCKET]->(t)
            """, "Availability-IN_BUCKET-TimeBucket"),

            # ResourceDemand -> OrgUnit
            ("""
                MATCH (rd:ResourceDemand), (o:OrgUnit)
                WHERE rd.requestedOrgUnitId = o.orgUnitId
                MERGE (rd)-[:TARGETS_ORG]->(o)
            """, "ResourceDemand-TARGETS_ORG-OrgUnit"),

            # Opportunity -> OrgUnit
            ("""
                MATCH (op:Opportunity), (o:OrgUnit)
                WHERE op.ownerOrgUnitId = o.orgUnitId
                MERGE (op)-[:OWNED_BY]->(o)
            """, "Opportunity-OWNED_BY-OrgUnit"),

            # ============================================================
            # Learning 관계
            # ============================================================

            # Course -> LearningProgram
            ("""
                MATCH (c:Course), (lp:LearningProgram)
                WHERE c.programId = lp.programId
                MERGE (c)-[:PART_OF_PROGRAM]->(lp)
            """, "Course-PART_OF_PROGRAM-LearningProgram"),

            # LearningProgram -> Competency (IMPROVES)
            ("""
                MATCH (c:Course), (comp:Competency)
                WHERE c.competencyId = comp.competencyId
                MATCH (c)-[:PART_OF_PROGRAM]->(lp:LearningProgram)
                MERGE (lp)-[:IMPROVES]->(comp)
            """, "LearningProgram-IMPROVES-Competency"),

            # Enrollment -> Employee
            ("""
                MATCH (en:Enrollment), (e:Employee)
                WHERE en.employeeId = e.employeeId
                MERGE (e)-[:ENROLLED_IN {status: en.status}]->(en)
            """, "Employee-ENROLLED_IN-Enrollment"),

            # Enrollment -> Course
            ("""
                MATCH (en:Enrollment), (c:Course)
                WHERE en.courseId = c.courseId
                MERGE (en)-[:FOR_COURSE]->(c)
            """, "Enrollment-FOR_COURSE-Course"),

            # ============================================================
            # Decision 관계
            # ============================================================

            # DecisionCase -> Target (OrgUnit/Opportunity/Project)
            ("""
                MATCH (dc:DecisionCase), (ou:OrgUnit)
                WHERE dc.targetType = 'OrgUnit' AND dc.targetId = ou.orgUnitId
                MERGE (dc)-[:ABOUT]->(ou)
            """, "DecisionCase-ABOUT-OrgUnit"),

            ("""
                MATCH (dc:DecisionCase), (op:Opportunity)
                WHERE dc.targetType = 'Opportunity' AND dc.targetId = op.opportunityId
                MERGE (dc)-[:ABOUT]->(op)
            """, "DecisionCase-ABOUT-Opportunity"),

            ("""
                MATCH (dc:DecisionCase), (p:Project)
                WHERE dc.targetType = 'Project' AND dc.targetId = p.projectId
                MERGE (dc)-[:ABOUT]->(p)
            """, "DecisionCase-ABOUT-Project"),

            # DecisionCase -> Objective
            ("""
                MATCH (obj:Objective), (dc:DecisionCase)
                WHERE obj.decisionCaseId = dc.decisionCaseId
                MERGE (dc)-[:HAS_OBJECTIVE]->(obj)
            """, "DecisionCase-HAS_OBJECTIVE-Objective"),

            # DecisionCase -> Constraint
            ("""
                MATCH (con:Constraint), (dc:DecisionCase)
                WHERE con.decisionCaseId = dc.decisionCaseId
                MERGE (dc)-[:HAS_CONSTRAINT]->(con)
            """, "DecisionCase-HAS_CONSTRAINT-Constraint"),

            # DecisionCase -> Option
            ("""
                MATCH (opt:Option), (dc:DecisionCase)
                WHERE opt.decisionCaseId = dc.decisionCaseId
                MERGE (dc)-[:HAS_OPTION]->(opt)
            """, "DecisionCase-HAS_OPTION-Option"),

            # Option -> Scenario
            ("""
                MATCH (sc:Scenario), (opt:Option)
                WHERE sc.optionId = opt.optionId
                MERGE (opt)-[:HAS_SCENARIO]->(sc)
            """, "Option-HAS_SCENARIO-Scenario"),

            # Scenario -> Action
            ("""
                MATCH (act:Action), (sc:Scenario)
                WHERE act.scenarioId = sc.scenarioId
                MERGE (sc)-[:INCLUDES_ACTION]->(act)
            """, "Scenario-INCLUDES_ACTION-Action"),

            # Option -> Evaluation
            ("""
                MATCH (ev:Evaluation), (opt:Option)
                WHERE ev.optionId = opt.optionId
                MERGE (opt)-[:HAS_EVALUATION]->(ev)
            """, "Option-HAS_EVALUATION-Evaluation"),

            # Evaluation -> MetricValue
            ("""
                MATCH (mv:MetricValue), (ev:Evaluation)
                WHERE mv.evaluationId = ev.evaluationId
                MERGE (ev)-[:HAS_METRIC]->(mv)
            """, "Evaluation-HAS_METRIC-MetricValue"),

            # Option -> ImpactAssessment
            ("""
                MATCH (ia:ImpactAssessment), (opt:Option)
                WHERE ia.optionId = opt.optionId
                MERGE (opt)-[:HAS_IMPACT]->(ia)
            """, "Option-HAS_IMPACT-ImpactAssessment"),

            # Option -> Risk
            ("""
                MATCH (r:Risk), (opt:Option)
                WHERE r.optionId = opt.optionId
                MERGE (opt)-[:HAS_RISK]->(r)
            """, "Option-HAS_RISK-Risk"),

            # DecisionCase -> DecisionGate
            ("""
                MATCH (g:DecisionGate), (dc:DecisionCase)
                WHERE g.decisionCaseId = dc.decisionCaseId
                MERGE (dc)-[:HAS_GATE]->(g)
            """, "DecisionCase-HAS_GATE-DecisionGate"),

            # DecisionGate -> Approval
            ("""
                MATCH (ap:Approval), (g:DecisionGate)
                WHERE ap.gateId = g.gateId
                MERGE (g)-[:HAS_APPROVAL]->(ap)
            """, "DecisionGate-HAS_APPROVAL-Approval"),

            # Approval -> WorkflowInstance
            ("""
                MATCH (wi:WorkflowInstance), (ap:Approval)
                WHERE wi.approvalId = ap.approvalId
                MERGE (ap)-[:TRIGGERS_WORKFLOW]->(wi)
            """, "Approval-TRIGGERS_WORKFLOW-WorkflowInstance"),

            # WorkflowInstance -> WorkflowTask
            ("""
                MATCH (wt:WorkflowTask), (wi:WorkflowInstance)
                WHERE wt.workflowId = wi.workflowId
                MERGE (wi)-[:HAS_TASK]->(wt)
            """, "WorkflowInstance-HAS_TASK-WorkflowTask"),

            # WorkflowTask -> Action
            ("""
                MATCH (wt:WorkflowTask), (act:Action)
                WHERE wt.actionId = act.actionId
                MERGE (wt)-[:RELATED_TO]->(act)
            """, "WorkflowTask-RELATED_TO-Action"),

            # ============================================================
            # Forecast/Explainability 관계
            # ============================================================

            # ModelRun -> Model
            ("""
                MATCH (mr:ModelRun), (m:Model)
                WHERE mr.modelId = m.modelId
                MERGE (mr)-[:RUNS_MODEL]->(m)
            """, "ModelRun-RUNS_MODEL-Model"),

            # ModelRun -> Scenario
            ("""
                MATCH (mr:ModelRun), (sc:Scenario)
                WHERE mr.scenarioId = sc.scenarioId
                MERGE (mr)-[:FOR_SCENARIO]->(sc)
            """, "ModelRun-FOR_SCENARIO-Scenario"),

            # ModelRun -> DataSnapshot
            ("""
                MATCH (mr:ModelRun), (ds:DataSnapshot)
                WHERE mr.snapshotId = ds.snapshotId
                MERGE (mr)-[:USING_SNAPSHOT]->(ds)
            """, "ModelRun-USING_SNAPSHOT-DataSnapshot"),

            # ModelRun -> ForecastPoint
            ("""
                MATCH (fp:ForecastPoint), (mr:ModelRun)
                WHERE fp.runId = mr.runId
                MERGE (mr)-[:OUTPUTS]->(fp)
            """, "ModelRun-OUTPUTS-ForecastPoint"),

            # ForecastPoint -> TimeBucket
            ("""
                MATCH (fp:ForecastPoint), (tb:TimeBucket)
                WHERE fp.bucketId = tb.bucketId
                MERGE (fp)-[:FOR_BUCKET]->(tb)
            """, "ForecastPoint-FOR_BUCKET-TimeBucket"),

            # ForecastPoint -> Subject (OrgUnit/Project/Opportunity/WorkPackage)
            ("""
                MATCH (fp:ForecastPoint), (ou:OrgUnit)
                WHERE fp.subjectType = 'OrgUnit' AND fp.subjectId = ou.orgUnitId
                MERGE (fp)-[:FOR_SUBJECT]->(ou)
            """, "ForecastPoint-FOR_SUBJECT-OrgUnit"),

            ("""
                MATCH (fp:ForecastPoint), (p:Project)
                WHERE fp.subjectType = 'Project' AND fp.subjectId = p.projectId
                MERGE (fp)-[:FOR_SUBJECT]->(p)
            """, "ForecastPoint-FOR_SUBJECT-Project"),

            # ModelRun -> Finding
            ("""
                MATCH (f:Finding), (mr:ModelRun)
                WHERE f.runId = mr.runId
                MERGE (mr)-[:HAS_FINDING]->(f)
            """, "ModelRun-HAS_FINDING-Finding"),

            # Finding -> Affects (OrgUnit/WorkPackage/Competency/Responsibility)
            ("""
                MATCH (f:Finding), (ou:OrgUnit)
                WHERE f.affectsType = 'OrgUnit' AND f.affectsId = ou.orgUnitId
                MERGE (f)-[:AFFECTS]->(ou)
            """, "Finding-AFFECTS-OrgUnit"),

            ("""
                MATCH (f:Finding), (wp:WorkPackage)
                WHERE f.affectsType = 'WorkPackage' AND f.affectsId = wp.workPackageId
                MERGE (f)-[:AFFECTS]->(wp)
            """, "Finding-AFFECTS-WorkPackage"),

            ("""
                MATCH (f:Finding), (c:Competency)
                WHERE f.affectsType = 'Competency' AND f.affectsId = c.competencyId
                MERGE (f)-[:AFFECTS]->(c)
            """, "Finding-AFFECTS-Competency"),

            # Finding -> Evidence
            ("""
                MATCH (ev:Evidence), (f:Finding)
                WHERE ev.findingId = f.findingId
                MERGE (f)-[:EVIDENCED_BY]->(ev)
            """, "Finding-EVIDENCED_BY-Evidence"),
        ]

        with self._driver.session(database=self.database) as session:
            for query, rel_name in relationship_queries:
                try:
                    result = session.run(query)
                    summary = result.consume()
                    rel_count = summary.counters.relationships_created
                    created += rel_count
                    logger.debug(f"관계 생성: {rel_name} ({rel_count}개)")
                except Exception as e:
                    errors.append(f"{rel_name}: {e}")

        duration = (datetime.now() - start_time).total_seconds() * 1000

        return LoadResult(
            entity_type="relationships",
            records_processed=len(relationship_queries),
            records_created=created,
            records_updated=0,
            errors=errors,
            duration_ms=duration
        )

    def get_statistics(self) -> dict:
        """현재 데이터베이스 통계"""
        stats = {}

        with self._driver.session(database=self.database) as session:
            # 노드 카운트
            result = session.run("""
                MATCH (n)
                WITH labels(n) AS labels
                UNWIND labels AS label
                RETURN label, count(*) AS count
                ORDER BY count DESC
            """)
            stats["nodes"] = {record["label"]: record["count"] for record in result}

            # 관계 카운트
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS type, count(*) AS count
                ORDER BY count DESC
            """)
            stats["relationships"] = {record["type"]: record["count"] for record in result}

            # 총계
            stats["total_nodes"] = sum(stats["nodes"].values())
            stats["total_relationships"] = sum(stats["relationships"].values())

        return stats


# CLI 실행용
if __name__ == "__main__":
    import sys

    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/mock"
    schema_path = sys.argv[2] if len(sys.argv) > 2 else "data/schemas/schema.cypher"

    # 환경변수에서 Neo4j 설정 읽기
    import os
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    print(f"Neo4j URI: {uri}")
    print(f"Data Directory: {data_dir}")
    print(f"Schema Path: {schema_path}")

    try:
        with Neo4jDataLoader(uri, username, password) as loader:
            # 데이터베이스 초기화
            print("\n[1/3] 데이터베이스 초기화 중...")
            loader.clear_database()

            # 스키마 생성
            print("[2/3] 스키마 생성 중...")
            loader.create_constraints_and_indexes(schema_path)

            # 데이터 로드
            print("[3/3] 데이터 로드 중...")
            summary = loader.load_all_mock_data(data_dir)

            # 결과 출력
            print("\n" + "=" * 60)
            print("       DATA LOAD SUMMARY")
            print("=" * 60)
            print(f"Started: {summary.started_at}")
            print(f"Completed: {summary.completed_at}")
            print(f"Duration: {(summary.completed_at - summary.started_at).total_seconds():.2f}s")
            print(f"Total Nodes: {summary.total_nodes}")
            print(f"Total Relationships: {summary.total_relationships}")
            print(f"Success: {summary.success}")

            print("\n" + "-" * 60)
            print("LOAD RESULTS BY ENTITY")
            print("-" * 60)
            for result in summary.results:
                status = "[OK]" if len(result.errors) == 0 else "[NG]"
                print(f"{status} {result.entity_type}: {result.records_created} created, "
                      f"{result.duration_ms:.1f}ms")
                if result.errors:
                    for err in result.errors[:3]:
                        print(f"    Error: {err}")
                    if len(result.errors) > 3:
                        print(f"    ... and {len(result.errors) - 3} more errors")

            # 통계
            print("\n" + "-" * 60)
            print("DATABASE STATISTICS")
            print("-" * 60)
            stats = loader.get_statistics()
            print("Nodes:")
            for label, count in stats["nodes"].items():
                print(f"  {label}: {count}")
            print("\nRelationships:")
            for rel_type, count in stats["relationships"].items():
                print(f"  {rel_type}: {count}")

            print("=" * 60)

    except ImportError as e:
        print(f"Error: {e}")
        print("neo4j 패키지를 설치해주세요: pip install neo4j")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
