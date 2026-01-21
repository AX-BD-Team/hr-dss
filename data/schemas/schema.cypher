// ============================================================
// HR DSS - Knowledge Graph Schema v0.1.2
// Neo4j Cypher Schema Definition
// Generated: 2025-01-24
// Updated: 2026-01-21 - 설계 문서 v0.1.1 기준 누락 노드 추가
// ============================================================

// ------------------------------------------------------------
// 1. CONSTRAINTS (Primary Keys)
// ------------------------------------------------------------

// 1.1 Workforce Domain
CREATE CONSTRAINT organization_pk IF NOT EXISTS
FOR (org:Organization) REQUIRE org.orgId IS UNIQUE;

CREATE CONSTRAINT org_unit_pk IF NOT EXISTS
FOR (o:OrgUnit) REQUIRE o.orgUnitId IS UNIQUE;

CREATE CONSTRAINT job_role_pk IF NOT EXISTS
FOR (j:JobRole) REQUIRE j.jobRoleId IS UNIQUE;

CREATE CONSTRAINT position_pk IF NOT EXISTS
FOR (pos:Position) REQUIRE pos.positionId IS UNIQUE;

CREATE CONSTRAINT employee_pk IF NOT EXISTS
FOR (e:Employee) REQUIRE e.employeeId IS UNIQUE;

CREATE CONSTRAINT employment_assignment_pk IF NOT EXISTS
FOR (ea:EmploymentAssignment) REQUIRE ea.assignmentId IS UNIQUE;

CREATE CONSTRAINT delivery_role_pk IF NOT EXISTS
FOR (d:DeliveryRole) REQUIRE d.deliveryRoleId IS UNIQUE;

// 1.2 Work Domain
CREATE CONSTRAINT client_pk IF NOT EXISTS
FOR (c:Client) REQUIRE c.clientId IS UNIQUE;

CREATE CONSTRAINT industry_pk IF NOT EXISTS
FOR (i:Industry) REQUIRE i.industryId IS UNIQUE;

CREATE CONSTRAINT opportunity_pk IF NOT EXISTS
FOR (o:Opportunity) REQUIRE o.opportunityId IS UNIQUE;

CREATE CONSTRAINT project_pk IF NOT EXISTS
FOR (p:Project) REQUIRE p.projectId IS UNIQUE;

CREATE CONSTRAINT work_package_pk IF NOT EXISTS
FOR (w:WorkPackage) REQUIRE w.workPackageId IS UNIQUE;

CREATE CONSTRAINT work_type_pk IF NOT EXISTS
FOR (wt:WorkType) REQUIRE wt.workTypeId IS UNIQUE;

// 1.3 Demand/Supply Domain
CREATE CONSTRAINT demand_signal_pk IF NOT EXISTS
FOR (ds:DemandSignal) REQUIRE ds.signalId IS UNIQUE;

CREATE CONSTRAINT resource_demand_pk IF NOT EXISTS
FOR (r:ResourceDemand) REQUIRE r.demandId IS UNIQUE;

CREATE CONSTRAINT availability_pk IF NOT EXISTS
FOR (a:Availability) REQUIRE a.availabilityId IS UNIQUE;

CREATE CONSTRAINT assignment_pk IF NOT EXISTS
FOR (a:Assignment) REQUIRE a.assignmentId IS UNIQUE;

CREATE CONSTRAINT timesheet_entry_pk IF NOT EXISTS
FOR (ts:TimesheetEntry) REQUIRE ts.timesheetId IS UNIQUE;

CREATE CONSTRAINT time_bucket_pk IF NOT EXISTS
FOR (t:TimeBucket) REQUIRE t.bucketId IS UNIQUE;

// 1.4 R&R Domain
CREATE CONSTRAINT responsibility_pk IF NOT EXISTS
FOR (r:Responsibility) REQUIRE r.responsibilityId IS UNIQUE;

// 1.5 Competency & Learning Domain
CREATE CONSTRAINT competency_pk IF NOT EXISTS
FOR (c:Competency) REQUIRE c.competencyId IS UNIQUE;

CREATE CONSTRAINT competency_requirement_pk IF NOT EXISTS
FOR (cr:CompetencyRequirement) REQUIRE cr.requirementId IS UNIQUE;

CREATE CONSTRAINT competency_evidence_pk IF NOT EXISTS
FOR (ce:CompetencyEvidence) REQUIRE ce.evidenceId IS UNIQUE;

CREATE CONSTRAINT learning_program_pk IF NOT EXISTS
FOR (lp:LearningProgram) REQUIRE lp.programId IS UNIQUE;

CREATE CONSTRAINT course_pk IF NOT EXISTS
FOR (c:Course) REQUIRE c.courseId IS UNIQUE;

CREATE CONSTRAINT enrollment_pk IF NOT EXISTS
FOR (en:Enrollment) REQUIRE en.enrollmentId IS UNIQUE;

CREATE CONSTRAINT certification_pk IF NOT EXISTS
FOR (cert:Certification) REQUIRE cert.certificationId IS UNIQUE;

// 1.6 Decision Domain
CREATE CONSTRAINT decision_case_pk IF NOT EXISTS
FOR (dc:DecisionCase) REQUIRE dc.decisionCaseId IS UNIQUE;

CREATE CONSTRAINT objective_pk IF NOT EXISTS
FOR (obj:Objective) REQUIRE obj.objectiveId IS UNIQUE;

CREATE CONSTRAINT constraint_pk IF NOT EXISTS
FOR (con:Constraint) REQUIRE con.constraintId IS UNIQUE;

CREATE CONSTRAINT option_pk IF NOT EXISTS
FOR (opt:Option) REQUIRE opt.optionId IS UNIQUE;

CREATE CONSTRAINT scenario_pk IF NOT EXISTS
FOR (sc:Scenario) REQUIRE sc.scenarioId IS UNIQUE;

CREATE CONSTRAINT action_pk IF NOT EXISTS
FOR (act:Action) REQUIRE act.actionId IS UNIQUE;

CREATE CONSTRAINT evaluation_pk IF NOT EXISTS
FOR (ev:Evaluation) REQUIRE ev.evaluationId IS UNIQUE;

CREATE CONSTRAINT metric_value_pk IF NOT EXISTS
FOR (mv:MetricValue) REQUIRE mv.metricValueId IS UNIQUE;

CREATE CONSTRAINT impact_assessment_pk IF NOT EXISTS
FOR (ia:ImpactAssessment) REQUIRE ia.impactId IS UNIQUE;

CREATE CONSTRAINT risk_pk IF NOT EXISTS
FOR (r:Risk) REQUIRE r.riskId IS UNIQUE;

CREATE CONSTRAINT decision_gate_pk IF NOT EXISTS
FOR (g:DecisionGate) REQUIRE g.gateId IS UNIQUE;

CREATE CONSTRAINT approval_pk IF NOT EXISTS
FOR (ap:Approval) REQUIRE ap.approvalId IS UNIQUE;

CREATE CONSTRAINT workflow_instance_pk IF NOT EXISTS
FOR (wi:WorkflowInstance) REQUIRE wi.workflowId IS UNIQUE;

CREATE CONSTRAINT workflow_task_pk IF NOT EXISTS
FOR (wt:WorkflowTask) REQUIRE wt.taskId IS UNIQUE;

// 1.7 Forecast & Explainability Domain
CREATE CONSTRAINT model_pk IF NOT EXISTS
FOR (m:Model) REQUIRE m.modelId IS UNIQUE;

CREATE CONSTRAINT model_run_pk IF NOT EXISTS
FOR (mr:ModelRun) REQUIRE mr.runId IS UNIQUE;

CREATE CONSTRAINT forecast_point_pk IF NOT EXISTS
FOR (fp:ForecastPoint) REQUIRE fp.forecastPointId IS UNIQUE;

CREATE CONSTRAINT finding_pk IF NOT EXISTS
FOR (f:Finding) REQUIRE f.findingId IS UNIQUE;

CREATE CONSTRAINT evidence_pk IF NOT EXISTS
FOR (ev:Evidence) REQUIRE ev.evidenceId IS UNIQUE;

CREATE CONSTRAINT data_snapshot_pk IF NOT EXISTS
FOR (ds:DataSnapshot) REQUIRE ds.snapshotId IS UNIQUE;

// 1.8 Outcome Domain (확장)
CREATE CONSTRAINT project_outcome_pk IF NOT EXISTS
FOR (po:ProjectOutcome) REQUIRE po.outcomeId IS UNIQUE;

CREATE CONSTRAINT utilization_record_pk IF NOT EXISTS
FOR (ur:UtilizationRecord) REQUIRE ur.recordId IS UNIQUE;

// ------------------------------------------------------------
// 2. INDEXES (Performance Optimization)
// ------------------------------------------------------------

// 2.1 Employee Indexes
CREATE INDEX employee_status_idx IF NOT EXISTS
FOR (e:Employee) ON (e.status);

CREATE INDEX employee_grade_idx IF NOT EXISTS
FOR (e:Employee) ON (e.grade);

CREATE INDEX employee_name_idx IF NOT EXISTS
FOR (e:Employee) ON (e.name);

// 2.2 OrgUnit Indexes
CREATE INDEX org_unit_type_idx IF NOT EXISTS
FOR (o:OrgUnit) ON (o.type);

// 2.3 Position Indexes
CREATE INDEX position_status_idx IF NOT EXISTS
FOR (pos:Position) ON (pos.status);

// 2.4 Project Indexes
CREATE INDEX project_status_idx IF NOT EXISTS
FOR (p:Project) ON (p.status);

CREATE INDEX project_priority_idx IF NOT EXISTS
FOR (p:Project) ON (p.priority);

CREATE INDEX project_dates_idx IF NOT EXISTS
FOR (p:Project) ON (p.startDate, p.endDate);

// 2.5 Opportunity Indexes
CREATE INDEX opportunity_stage_idx IF NOT EXISTS
FOR (o:Opportunity) ON (o.stage);

CREATE INDEX opportunity_close_date_idx IF NOT EXISTS
FOR (o:Opportunity) ON (o.expectedCloseDate);

// 2.6 Assignment Indexes
CREATE INDEX assignment_dates_idx IF NOT EXISTS
FOR (a:Assignment) ON (a.startDate, a.endDate);

CREATE INDEX assignment_status_idx IF NOT EXISTS
FOR (a:Assignment) ON (a.status);

// 2.7 TimeBucket Indexes
CREATE INDEX time_bucket_type_idx IF NOT EXISTS
FOR (t:TimeBucket) ON (t.bucketType, t.bucketStart);

// 2.8 Competency Indexes
CREATE INDEX competency_domain_idx IF NOT EXISTS
FOR (c:Competency) ON (c.domain);

CREATE INDEX competency_category_idx IF NOT EXISTS
FOR (c:Competency) ON (c.category);

// 2.9 DecisionCase Indexes
CREATE INDEX decision_case_status_idx IF NOT EXISTS
FOR (dc:DecisionCase) ON (dc.status);

CREATE INDEX decision_case_type_idx IF NOT EXISTS
FOR (dc:DecisionCase) ON (dc.type);

// 2.10 Option Indexes
CREATE INDEX option_type_idx IF NOT EXISTS
FOR (opt:Option) ON (opt.optionType);

// 2.11 Action Indexes
CREATE INDEX action_type_idx IF NOT EXISTS
FOR (act:Action) ON (act.type);

CREATE INDEX action_status_idx IF NOT EXISTS
FOR (act:Action) ON (act.status);

// 2.12 Finding Indexes
CREATE INDEX finding_type_idx IF NOT EXISTS
FOR (f:Finding) ON (f.type);

CREATE INDEX finding_severity_idx IF NOT EXISTS
FOR (f:Finding) ON (f.severity);

// 2.13 ForecastPoint Indexes
CREATE INDEX forecast_point_metric_idx IF NOT EXISTS
FOR (fp:ForecastPoint) ON (fp.metricType);

// 2.14 ModelRun Indexes
CREATE INDEX model_run_status_idx IF NOT EXISTS
FOR (mr:ModelRun) ON (mr.status);

// 2.15 WorkflowTask Indexes
CREATE INDEX workflow_task_status_idx IF NOT EXISTS
FOR (wt:WorkflowTask) ON (wt.status);

// 2.16 DecisionGate Indexes
CREATE INDEX decision_gate_process_idx IF NOT EXISTS
FOR (g:DecisionGate) ON (g.process);

// ------------------------------------------------------------
// 3. NODE LABELS & PROPERTIES
// 설계 문서 v0.1.1 기준으로 정의
// ------------------------------------------------------------

// ============================================================
// 3.1 Workforce & Organization
// ============================================================

// 3.1.1 Organization Node
// Properties:
//   - orgId: String (PK)
//   - name: String

// 3.1.2 OrgUnit Node
// Properties:
//   - orgUnitId: String (PK)
//   - name: String (필수)
//   - type: String (본부/실/팀)
//   - parentOrgUnitId: String
//   - costCenter: String
//   - validFrom: Date
//   - validTo: Date
//   - status: String (ACTIVE, INACTIVE)
//   - headCount: Integer
//   - targetUtilization: Float

// 3.1.3 JobRole Node
// Properties:
//   - jobRoleId: String (PK)
//   - name: String
//   - jobFamily: String
//   - levelBand: String

// 3.1.4 Position Node (TO/정원 슬롯)
// Properties:
//   - positionId: String (PK)
//   - headcountType: String
//   - grade: String
//   - status: String (OPEN, FILLED, FROZEN)
//   - orgUnitId: String
//   - jobRoleId: String

// 3.1.5 Employee Node
// Properties:
//   - employeeId: String (PK, 필수)
//   - name: String
//   - email: String
//   - employmentType: String
//   - grade: String (P1-P5, M1-M3, E1-E2)
//   - status: String (ACTIVE, INACTIVE, ON_LEAVE)
//   - hireDate: Date
//   - terminationDate: Date (nullable)
//   - location: String
//   - costRate: Float (hourly rate)

// 3.1.6 EmploymentAssignment Node (소속/직무/포지션 이력)
// Properties:
//   - assignmentId: String (PK, 또는 employeeId+startDate 복합키)
//   - startDate: Date
//   - endDate: Date
//   - sourceSystem: String

// ============================================================
// 3.2 Work & Portfolio
// ============================================================

// 3.2.1 Client Node
// Properties:
//   - clientId: String (PK)
//   - name: String

// 3.2.2 Industry Node
// Properties:
//   - industryId: String (PK)
//   - name: String

// 3.2.3 Opportunity Node (BizForce 파이프라인)
// Properties:
//   - opportunityId: String (PK)
//   - name: String (필수)
//   - stage: String (LEAD, QUALIFIED, PROPOSAL, NEGOTIATION, CLOSING, WON, LOST)
//   - expectedStartDate: Date (필수)
//   - expectedEndDate: Date
//   - dealValue: Float
//   - expectedMarginTarget: Float
//   - ownerOrgUnitId: String
//   - closeProbability: Float
//   - estimatedFTE: Float
//   - estimatedDuration: Integer (months)

// 3.2.4 Project Node
// Properties:
//   - projectId: String (PK)
//   - name: String
//   - startDate: Date
//   - endDate: Date
//   - priority: String (CRITICAL, HIGH, MEDIUM, LOW)
//   - contractValue: Float
//   - status: String (PLANNED, ACTIVE, COMPLETED, ON_HOLD, CANCELLED)
//   - budgetAmount: Float
//   - actualCost: Float
//   - targetMargin: Float

// 3.2.5 WorkPackage Node (WBS/스트림)
// Properties:
//   - workPackageId: String (PK)
//   - name: String
//   - startDate: Date
//   - endDate: Date
//   - criticality: String (CRITICAL, HIGH, MEDIUM, LOW)
//   - status: String (NOT_STARTED, IN_PROGRESS, COMPLETED)
//   - estimatedFTE: Float

// 3.2.6 WorkType Node (운영/반복업무)
// Properties:
//   - workTypeId: String (PK)
//   - name: String

// ============================================================
// 3.3 Demand & Supply
// ============================================================

// 3.3.1 DemandSignal Node (수요 신호)
// Properties:
//   - signalId: String (PK)
//   - sourceSystem: String (='BizForce', 필수)
//   - closeProbability: Float (필수)
//   - expectedStartDate: Date (필수)
//   - expectedEffortMM: Float
//   - confidence: Float
//   - lastUpdatedAt: DateTime

// 3.3.2 ResourceDemand Node (주차/기간별 요구 FTE/MM)
// Properties:
//   - demandId: String (PK)
//   - quantityFTE: Float (필수, 또는 effortMM)
//   - startDate: Date (필수)
//   - endDate: Date (필수)
//   - priority: String (필수)
//   - probability: Float (0~1, 파이프라인 반영 필수)
//   - sourceType: String (Opportunity/Project/WorkPackage/WorkType)
//   - sourceId: String
//   - status: String (OPEN, PARTIALLY_FILLED, FILLED)

// 3.3.3 Availability Node (가용성)
// Properties:
//   - availabilityId: String (PK, employeeId+bucketId 권장)
//   - availableFTE: Float (필수)
//   - reason: String (필수)
//   - startDate: Date
//   - endDate: Date
//   - bucketId: String
//   - sourceSystem: String (TMS/HR)

// 3.3.4 Assignment Node (투입/배정)
// Properties:
//   - assignmentId: String (PK)
//   - allocationFTE: Float (필수)
//   - startDate: Date (필수)
//   - endDate: Date (필수)
//   - role: String
//   - isTentative: Boolean
//   - sourceSystem: String (TMS)
//   - status: String (PLANNED, ACTIVE, COMPLETED, CANCELLED)
//   - billable: Boolean

// 3.3.5 TimesheetEntry Node (실적, 선택)
// Properties:
//   - timesheetId: String (PK)
//   - date: Date
//   - hours: Float
//   - sourceRef: String

// 3.3.6 TimeBucket Node
// Properties:
//   - bucketId: String (PK, e.g., "2026-W05")
//   - granularity: String (='WEEK')
//   - startDate: Date
//   - endDate: Date
//   - year: Integer
//   - week: Integer
//   - label: String

// ============================================================
// 3.4 R&R / Coverage (핵심역할/대무)
// ============================================================

// 3.4.1 DeliveryRole Node (프로젝트/운영 역할)
// Properties:
//   - deliveryRoleId: String (PK)
//   - name: String (PM/아키텍트/데이터엔지니어/AX컨설턴트 등)

// 3.4.2 Responsibility Node (업무/책임 단위)
// Properties:
//   - responsibilityId: String (PK)
//   - name: String (필수)
//   - criticality: String (필수)
//   - description: String
//   - ownerType: String (OrgUnit/WorkPackage)

// ============================================================
// 3.5 Competency & Learning
// ============================================================

// 3.5.1 Competency Node
// Properties:
//   - competencyId: String (PK)
//   - name: String
//   - domain: String (TECHNICAL, BUSINESS, LEADERSHIP)
//   - category: String
//   - description: String

// 3.5.2 CompetencyRequirement Node
// Properties:
//   - requirementId: String (PK)
//   - requiredLevel: Integer (필수)
//   - weight: Float (필수)
//   - targetType: String (JobRole/WorkPackage/DeliveryRole)
//   - targetId: String

// 3.5.3 CompetencyEvidence Node
// Properties:
//   - evidenceId: String (PK)
//   - level: Integer (1-5, 필수)
//   - assessedAt: Date (필수)
//   - sourceType: String (필수)
//   - assessedBy: String
//   - confidence: Float
//   - validUntil: Date
//   - notes: String

// 3.5.4 LearningProgram Node
// Properties:
//   - programId: String (PK)
//   - name: String (필수)
//   - deliveryMode: String (online/offline/blended, 필수)

// 3.5.5 Course Node
// Properties:
//   - courseId: String (PK)
//   - title: String (필수)
//   - deliveryMode: String (online/offline/blended, 필수)

// 3.5.6 Enrollment Node
// Properties:
//   - enrollmentId: String (PK)
//   - status: String (필수)
//   - plannedStart: Date
//   - plannedEnd: Date

// 3.5.7 Certification Node (선택)
// Properties:
//   - certificationId: String (PK)
//   - name: String
//   - level: String

// ============================================================
// 3.6 Decision, Evaluation, Workflow
// ============================================================

// 3.6.1 DecisionCase Node
// Properties:
//   - decisionCaseId: String (PK)
//   - type: String (PortfolioBottleneck/GoNoGo/Headcount/CapabilityROI, 필수)
//   - createdAt: DateTime (필수)
//   - status: String (필수)
//   - requester: String
//   - dueDate: Date
//   - summary: String

// 3.6.2 Objective Node
// Properties:
//   - objectiveId: String (PK)
//   - metricType: String (필수, e.g., UTILIZATION, SUCCESS_PROB, MARGIN)
//   - operator: String (필수, <=/>=/=)
//   - targetValue: Float (필수)
//   - scopeType: String
//   - horizonStart: Date
//   - horizonEnd: Date

// 3.6.3 Constraint Node
// Properties:
//   - constraintId: String (PK)
//   - type: String (Availability/Budget/Policy/Security, 필수)
//   - severity: String (hard/soft, 필수)
//   - expression: String
//   - startDate: Date
//   - endDate: Date
//   - appliesToType: String
//   - appliesToId: String

// 3.6.4 Option Node
// Properties:
//   - optionId: String (PK)
//   - name: String
//   - optionType: String (Internal/Mixed/Upskill)
//   - description: String

// 3.6.5 Scenario Node
// Properties:
//   - scenarioId: String (PK)
//   - baselineSnapshotId: String
//   - assumptions: String (JSON)

// 3.6.6 Action Node
// Properties:
//   - actionId: String (PK)
//   - type: String (Reassign/Outsource/Upskill/Hire/ScopeChange)
//   - owner: String
//   - startDate: Date
//   - endDate: Date
//   - status: String

// 3.6.7 Evaluation Node
// Properties:
//   - evaluationId: String (PK)
//   - totalScore: Float
//   - successProbability: Float
//   - rationale: String

// 3.6.8 MetricValue Node
// Properties:
//   - metricValueId: String (PK)
//   - metricType: String
//   - asIsValue: Float
//   - toBeValue: Float
//   - delta: Float
//   - unit: String

// 3.6.9 ImpactAssessment Node
// Properties:
//   - impactId: String (PK)
//   - dimension: String (Cost/Speed/Risk/Quality/Capability)
//   - value: Float
//   - narrative: String

// 3.6.10 Risk Node (선택)
// Properties:
//   - riskId: String (PK)
//   - category: String
//   - probability: Float
//   - impact: Float
//   - score: Float
//   - description: String

// 3.6.11 DecisionGate Node
// Properties:
//   - gateId: String (PK)
//   - process: String (VRB/Pre-PRB/PRB)
//   - name: String
//   - sequence: Integer
//   - status: String

// 3.6.12 Approval Node
// Properties:
//   - approvalId: String (PK)
//   - decision: String (approve/reject)
//   - approvedBy: String
//   - approvedAt: DateTime
//   - comment: String

// 3.6.13 WorkflowInstance Node
// Properties:
//   - workflowId: String (PK)
//   - type: String
//   - status: String
//   - startedAt: DateTime

// 3.6.14 WorkflowTask Node
// Properties:
//   - taskId: String (PK)
//   - type: String
//   - owner: String
//   - dueDate: Date
//   - status: String

// ============================================================
// 3.7 Forecast & Explainability (예측/근거/감사)
// ============================================================

// 3.7.1 Model Node
// Properties:
//   - modelId: String (PK)
//   - name: String
//   - type: String (heuristic/ml/rules)
//   - version: String

// 3.7.2 ModelRun Node
// Properties:
//   - runId: String (PK)
//   - runAt: DateTime
//   - parameters: String (JSON)
//   - status: String
//   - scenarioId: String

// 3.7.3 ForecastPoint Node
// Properties:
//   - forecastPointId: String (PK)
//   - metricType: String (필수)
//   - value: Float (필수)
//   - unit: String (필수)
//   - lowerBound: Float
//   - upperBound: Float
//   - confidence: Float
//   - method: String

// 3.7.4 Finding Node (병목/원인/갭)
// Properties:
//   - findingId: String (PK)
//   - type: String (OVER_UTILIZATION/SKILL_GAP/ROLE_GAP/COVERAGE_GAP/MARGIN_RISK, 필수)
//   - severity: String (필수)
//   - narrative: String (필수)
//   - rootCause: String
//   - rank: Integer

// 3.7.5 Evidence Node
// Properties:
//   - evidenceId: String (PK)
//   - sourceSystem: String
//   - sourceType: String (table/query/doc)
//   - sourceRef: String
//   - capturedAt: DateTime
//   - note: String

// 3.7.6 DataSnapshot Node
// Properties:
//   - snapshotId: String (PK)
//   - asOf: DateTime
//   - datasetVersions: String (JSON)

// ============================================================
// 3.8 Outcome (확장)
// ============================================================

// 3.8.1 ProjectOutcome Node
// Properties:
//   - outcomeId: String (PK)
//   - totalScore: Float
//   - label: String
//   - evaluatedAt: DateTime

// 3.8.2 UtilizationRecord Node
// Properties:
//   - recordId: String (PK)
//   - utilization: Float
//   - recordedAt: DateTime

// ------------------------------------------------------------
// 4. RELATIONSHIP TYPES
// 설계 문서 v0.1.1 6장 기준
// ------------------------------------------------------------

// ============================================================
// 4.1 조직/인력 (Workforce & Organization)
// ============================================================
// (OrgUnit)-[:HAS_SUB_UNIT]->(OrgUnit)                         // 조직 계층
// (OrgUnit)-[:PART_OF]->(OrgUnit)                              // 상위 조직 소속
// (OrgUnit)-[:MANAGED_BY]->(Employee)                          // 조직장
// (Employee)-[:BELONGS_TO {startDate, endDate}]->(OrgUnit)     // 소속
// (Employee)-[:HAS_JOB_ROLE {startDate, endDate}]->(JobRole)   // 직무
// (Employee)-[:OCCUPIES {startDate, endDate}]->(Position)      // 포지션 점유
// (Employee)-[:REPORTS_TO]->(Employee)                         // 보고 관계
// (Employee)-[:HAS_DELIVERY_ROLE {since, until}]->(DeliveryRole) // 수행 역할
// (Position)-[:IN_ORGUNIT]->(OrgUnit)                          // 포지션-조직
// (Position)-[:FOR_JOB_ROLE]->(JobRole)                        // 포지션-직무
// (JobRole)-[:MAPS_TO]->(DeliveryRole)                         // 직무-역할 매핑

// ============================================================
// 4.2 파이프라인/프로젝트 (Work & Portfolio)
// ============================================================
// (Opportunity)-[:FOR_CLIENT]->(Client)                        // 고객
// (Opportunity)-[:IN_INDUSTRY]->(Industry)                     // 산업
// (Opportunity)-[:HAS_SIGNAL]->(DemandSignal)                  // 수요 신호
// (DemandSignal)-[:IMPLIES_DEMAND]->(ResourceDemand)           // 수요 연결
// (Project)-[:FOR_CLIENT]->(Client)                            // 프로젝트-고객
// (Project)-[:OWNED_BY]->(OrgUnit)                             // 주관 조직
// (Project)-[:MANAGED_BY]->(Employee)                          // PM
// (Project)-[:CONTAINS]->(WorkPackage)                         // WBS 포함
// (Project)-[:ORIGINATED_FROM]->(Opportunity)                  // 기회에서 전환
// (WorkPackage)-[:DEPENDS_ON]->(WorkPackage)                   // WP 의존성

// ============================================================
// 4.3 수요/공급/투입 (Demand & Supply)
// ============================================================
// (WorkPackage|OrgUnit|Project|Opportunity)-[:HAS_DEMAND]->(ResourceDemand)  // 수요 연결
// (ResourceDemand)-[:FOR_BUCKET]->(TimeBucket)                 // 기간별 수요
// (ResourceDemand)-[:REQUIRES_ROLE]->(DeliveryRole)            // 역할 요구
// (ResourceDemand)-[:REQUIRES_COMPETENCY]->(CompetencyRequirement) // 역량 요구
// (CompetencyRequirement)-[:FOR_COMPETENCY]->(Competency)      // 역량 참조
// (ResourceDemand)-[:TARGETS_ORG]->(OrgUnit)                   // 대상 조직
// (Employee)-[:ASSIGNED_TO {allocationFTE, startDate, endDate}]->(WorkPackage|Project|WorkType) // 투입
// (Employee)-[:WORKS_ON]->(WorkPackage)                        // 작업 수행
// (Employee)-[:HAS_AVAILABILITY]->(Availability)               // 가용성
// (Availability)-[:FOR_BUCKET]->(TimeBucket)                   // 기간별 가용
// (Availability)-[:IN_BUCKET]->(TimeBucket)                    // (별칭)
// (Assignment)-[:ASSIGNS]->(Employee)                          // 배정-직원
// (Assignment)-[:FOR_PROJECT]->(Project)                       // 배정-프로젝트
// (Assignment)-[:FOR_WORK_PACKAGE]->(WorkPackage)              // 배정-WP

// ============================================================
// 4.4 R&R/대무 (핵심역할/Coverage)
// ============================================================
// (OrgUnit)-[:OWNS_RESPONSIBILITY]->(Responsibility)           // 조직-책임
// (WorkPackage)-[:HAS_RESPONSIBILITY]->(Responsibility)        // WP-책임
// (Responsibility)-[:REQUIRES_ROLE]->(DeliveryRole)            // 책임-역할
// (Employee)-[:PRIMARY_FOR {startDate, endDate}]->(Responsibility) // 정(정담당)
// (Employee)-[:BACKUP_FOR {startDate, endDate}]->(Responsibility)  // 부(대무)
// (JobRole)-[:HAS_RESPONSIBILITY]->(Responsibility)            // 직무-책임
// (DeliveryRole)-[:HAS_RESPONSIBILITY]->(Responsibility)       // 역할-책임

// ============================================================
// 4.5 역량/학습 (Competency & Learning)
// ============================================================
// (JobRole|WorkPackage|DeliveryRole)-[:REQUIRES_COMPETENCY]->(CompetencyRequirement) // 역량 요구
// (Employee)-[:HAS_EVIDENCE]->(CompetencyEvidence)             // 역량 증거
// (CompetencyEvidence)-[:FOR_COMPETENCY]->(Competency)         // 역량 참조
// (Employee)-[:HAS_COMPETENCY {level, assessedAt}]->(Competency) // 역량 보유
// (CompetencyEvidence)-[:EVIDENCES]->(Competency)              // 증거-역량
// (CompetencyEvidence)-[:BELONGS_TO_EMPLOYEE]->(Employee)      // 증거-직원
// (LearningProgram)-[:IMPROVES]->(Competency)                  // 프로그램-역량
// (Course)-[:PART_OF_PROGRAM]->(LearningProgram)               // 코스-프로그램
// (Employee)-[:ENROLLED_IN {status, plannedStart, plannedEnd}]->(Course) // 수강
// (Employee)-[:HAS_CERTIFICATION]->(Certification)             // 자격증

// ============================================================
// 4.6 의사결정/옵션/실행 (Decision & Workflow)
// ============================================================
// (DecisionCase)-[:ABOUT]->(OrgUnit|Opportunity|Project)       // 대상
// (DecisionCase)-[:HAS_OBJECTIVE]->(Objective)                 // 목표
// (DecisionCase)-[:HAS_CONSTRAINT]->(Constraint)               // 제약
// (DecisionCase)-[:HAS_OPTION]->(Option)                       // 옵션
// (Option)-[:HAS_SCENARIO]->(Scenario)                         // 시나리오
// (Scenario)-[:INCLUDES_ACTION]->(Action)                      // 액션 포함
// (Option)-[:HAS_EVALUATION]->(Evaluation)                     // 평가
// (Evaluation)-[:HAS_METRIC]->(MetricValue)                    // 지표 값
// (Option)-[:HAS_IMPACT]->(ImpactAssessment)                   // 영향 평가
// (Option)-[:HAS_RISK]->(Risk)                                 // 리스크
// (DecisionCase)-[:HAS_GATE]->(DecisionGate)                   // 게이트
// (DecisionGate)-[:HAS_APPROVAL]->(Approval)                   // 승인
// (DecisionGate)-[:APPROVED_BY]->(Employee)                    // 승인자
// (Approval)-[:TRIGGERS_WORKFLOW]->(WorkflowInstance)          // 워크플로 트리거
// (WorkflowInstance)-[:HAS_TASK]->(WorkflowTask)               // 태스크 포함
// (WorkflowTask)-[:RELATED_TO]->(Action)                       // 액션 연결
// (WorkflowTask)-[:ASSIGNED_TO_EMPLOYEE]->(Employee)           // 담당자

// ============================================================
// 4.7 예측/근거/감사 (Forecast & Explainability)
// ============================================================
// (ModelRun)-[:RUNS_MODEL]->(Model)                            // 모델 실행
// (ModelRun)-[:FOR_SCENARIO]->(Scenario)                       // 시나리오 (As-Is는 baseline)
// (ModelRun)-[:USING_SNAPSHOT]->(DataSnapshot)                 // 스냅샷 사용
// (ModelRun)-[:OUTPUTS]->(ForecastPoint)                       // 예측 결과
// (ForecastPoint)-[:FOR_BUCKET]->(TimeBucket)                  // 기간
// (ForecastPoint)-[:FOR_SUBJECT]->(OrgUnit|Opportunity|Project|WorkPackage) // 대상
// (ModelRun)-[:HAS_FINDING]->(Finding)                         // 발견 사항
// (Finding)-[:AFFECTS]->(OrgUnit|WorkPackage|DeliveryRole|Competency|Responsibility) // 영향 대상
// (Finding)-[:EVIDENCED_BY]->(Evidence)                        // 근거
// (Evidence)-[:REFERENCES]->(Employee|Assignment|Availability|ResourceDemand|DemandSignal) // 원천 데이터

// ============================================================
// 4.8 Outcome (확장)
// ============================================================
// (Project)-[:HAS_OUTCOME]->(ProjectOutcome)                   // 프로젝트 결과
// (OrgUnit)-[:HAS_UTILIZATION]->(UtilizationRecord)            // 가동률 기록
// (UtilizationRecord)-[:IN_PERIOD]->(TimeBucket)               // 기간

// ------------------------------------------------------------
// 5. SAMPLE DATA CREATION (for testing)
// ------------------------------------------------------------

// Create sample TimeBuckets for 12 weeks
WITH range(1, 12) AS weeks
UNWIND weeks AS weekNum
CREATE (tb:TimeBucket {
  bucketId: 'TB-2025-W' + (weekNum < 10 ? '0' : '') + weekNum,
  bucketType: 'WEEK',
  bucketStart: date('2025-01-01') + duration({weeks: weekNum - 1}),
  bucketEnd: date('2025-01-01') + duration({weeks: weekNum}) - duration({days: 1}),
  label: '2025-W' + (weekNum < 10 ? '0' : '') + weekNum
});

// ------------------------------------------------------------
// 6. USEFUL QUERIES
// ------------------------------------------------------------

// 6.1 Find employees with specific competency at level >= N
// MATCH (e:Employee)-[r:HAS_COMPETENCY]->(c:Competency {name: $competencyName})
// WHERE r.level >= $minLevel AND e.status = 'ACTIVE'
// RETURN e, r.level AS competencyLevel

// 6.2 Calculate utilization for org unit in time bucket
// MATCH (ou:OrgUnit {orgUnitId: $orgUnitId})<-[:BELONGS_TO]-(e:Employee)
// MATCH (e)-[a:ASSIGNED_TO]->(p:Project)
// WHERE a.startDate <= $bucketEnd AND a.endDate >= $bucketStart
// WITH ou, SUM(a.allocationFTE) AS assignedFTE
// MATCH (ou)-[cap:HAS_CAPACITY]->(tb:TimeBucket {bucketId: $bucketId})
// RETURN assignedFTE / cap.availableFTE AS utilization

// 6.3 Find bottleneck competencies
// MATCH (rd:ResourceDemand)-[:REQUIRES_COMPETENCY]->(c:Competency)
// WHERE rd.status = 'OPEN'
// WITH c, SUM(rd.quantityFTE * rd.probability) AS demandFTE
// MATCH (e:Employee)-[r:HAS_COMPETENCY]->(c)
// WHERE e.status = 'ACTIVE' AND r.level >= 3
// WITH c, demandFTE, COUNT(e) AS supplyCount
// WHERE demandFTE > supplyCount * 0.8
// RETURN c.name, demandFTE, supplyCount, demandFTE - supplyCount AS gap
// ORDER BY gap DESC

// 6.4 Project success factors analysis
// MATCH (p:Project)-[:HAS_OUTCOME]->(po:ProjectOutcome)
// MATCH (p)-[:MANAGED_BY]->(pm:Employee)
// MATCH (p)<-[:ASSIGNED_TO]-(e:Employee)
// WITH p, po, pm,
//      AVG(e.grade) AS avgGrade,
//      COUNT(DISTINCT e) AS teamSize
// RETURN p.name, po.totalScore, po.label,
//        pm.name AS projectManager,
//        avgGrade, teamSize

// 6.5 Competency gap analysis
// MATCH (p:Project {status: 'PLANNED'})-[:REQUIRES_COMPETENCY]->(c:Competency)
// WITH c, COUNT(p) AS demandingProjects
// MATCH (e:Employee {status: 'ACTIVE'})-[r:HAS_COMPETENCY]->(c)
// WITH c, demandingProjects,
//      COUNT(CASE WHEN r.level >= 4 THEN 1 END) AS experts,
//      COUNT(CASE WHEN r.level >= 3 THEN 1 END) AS proficient
// RETURN c.name, c.domain, demandingProjects, experts, proficient
// ORDER BY demandingProjects DESC, experts ASC
