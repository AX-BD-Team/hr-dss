"""
HR DSS - Workflow Builder Agent

의사결정 워크플로를 구성하고 실행하는 오케스트레이션 에이전트
각 에이전트의 실행 순서와 데이터 흐름을 관리
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """워크플로 상태"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"  # HITL 대기
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(Enum):
    """단계 상태"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class StepType(Enum):
    """단계 유형"""

    QUERY_DECOMPOSITION = "QUERY_DECOMPOSITION"
    KG_QUERY = "KG_QUERY"
    OPTION_GENERATION = "OPTION_GENERATION"
    IMPACT_SIMULATION = "IMPACT_SIMULATION"
    PROBABILITY_CALCULATION = "PROBABILITY_CALCULATION"
    VALIDATION = "VALIDATION"
    HITL_APPROVAL = "HITL_APPROVAL"
    DECISION_LOG = "DECISION_LOG"


@dataclass
class StepResult:
    """단계 실행 결과"""

    step_id: str
    step_type: StepType
    status: StepStatus
    output: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float = 0


@dataclass
class WorkflowStep:
    """워크플로 단계"""

    step_id: str
    step_type: StepType
    name: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    required: bool = True
    timeout_seconds: int = 60
    retry_count: int = 0


@dataclass
class WorkflowDefinition:
    """워크플로 정의"""

    workflow_id: str
    name: str
    description: str
    query_type: str
    steps: list[WorkflowStep]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowExecution:
    """워크플로 실행 인스턴스"""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    input_data: dict[str, Any]
    step_results: dict[str, StepResult] = field(default_factory=dict)
    current_step_id: str | None = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    error: str | None = None


@dataclass
class WorkflowContext:
    """워크플로 실행 컨텍스트"""

    user_query: str
    org_unit_id: str | None = None
    constraints: dict[str, Any] = field(default_factory=dict)
    decomposed_query: dict[str, Any] | None = None
    kg_results: dict[str, Any] | None = None
    options: dict[str, Any] | None = None
    impact_analysis: dict[str, Any] | None = None
    probabilities: dict[str, Any] | None = None
    validation_result: dict[str, Any] | None = None
    hitl_decision: dict[str, Any] | None = None


class WorkflowBuilderAgent:
    """워크플로 빌더 에이전트"""

    # 질문 유형별 기본 워크플로
    DEFAULT_WORKFLOWS = {
        "CAPACITY": [
            StepType.QUERY_DECOMPOSITION,
            StepType.KG_QUERY,
            StepType.OPTION_GENERATION,
            StepType.IMPACT_SIMULATION,
            StepType.PROBABILITY_CALCULATION,
            StepType.VALIDATION,
            StepType.HITL_APPROVAL,
            StepType.DECISION_LOG,
        ],
        "GO_NOGO": [
            StepType.QUERY_DECOMPOSITION,
            StepType.KG_QUERY,
            StepType.PROBABILITY_CALCULATION,
            StepType.OPTION_GENERATION,
            StepType.IMPACT_SIMULATION,
            StepType.VALIDATION,
            StepType.HITL_APPROVAL,
            StepType.DECISION_LOG,
        ],
        "HEADCOUNT": [
            StepType.QUERY_DECOMPOSITION,
            StepType.KG_QUERY,
            StepType.OPTION_GENERATION,
            StepType.IMPACT_SIMULATION,
            StepType.PROBABILITY_CALCULATION,
            StepType.VALIDATION,
            StepType.HITL_APPROVAL,
            StepType.DECISION_LOG,
        ],
        "COMPETENCY_GAP": [
            StepType.QUERY_DECOMPOSITION,
            StepType.KG_QUERY,
            StepType.OPTION_GENERATION,
            StepType.IMPACT_SIMULATION,
            StepType.PROBABILITY_CALCULATION,
            StepType.VALIDATION,
            StepType.HITL_APPROVAL,
            StepType.DECISION_LOG,
        ],
    }

    STEP_DESCRIPTIONS = {
        StepType.QUERY_DECOMPOSITION: "사용자 질문을 하위 쿼리로 분해",
        StepType.KG_QUERY: "Knowledge Graph에서 관련 데이터 조회",
        StepType.OPTION_GENERATION: "의사결정 대안 3개 생성",
        StepType.IMPACT_SIMULATION: "As-Is vs To-Be 영향 분석",
        StepType.PROBABILITY_CALCULATION: "성공 확률 계산",
        StepType.VALIDATION: "근거 연결 및 환각 검증",
        StepType.HITL_APPROVAL: "인간 검토 및 승인",
        StepType.DECISION_LOG: "의사결정 기록 저장",
    }

    def __init__(
        self,
        agents: dict[str, Any] | None = None,
        kg_client: Any = None,
        hitl_handler: Callable[[WorkflowExecution, WorkflowContext], dict] | None = None,
    ):
        """
        Args:
            agents: 에이전트 인스턴스 딕셔너리
            kg_client: Knowledge Graph 클라이언트
            hitl_handler: HITL 승인 핸들러 함수
        """
        self.agents = agents or {}
        self.kg_client = kg_client
        self.hitl_handler = hitl_handler
        self.executions: dict[str, WorkflowExecution] = {}

    def build_workflow(
        self,
        query_type: str,
        custom_steps: list[StepType] | None = None,
        skip_hitl: bool = False,
    ) -> WorkflowDefinition:
        """
        질문 유형에 맞는 워크플로 정의 생성

        Args:
            query_type: 질문 유형
            custom_steps: 커스텀 단계 목록 (지정 시 기본 워크플로 대체)
            skip_hitl: HITL 단계 건너뛰기 여부

        Returns:
            WorkflowDefinition: 워크플로 정의
        """
        step_types = custom_steps or self.DEFAULT_WORKFLOWS.get(
            query_type, self.DEFAULT_WORKFLOWS["CAPACITY"]
        )

        if skip_hitl:
            step_types = [s for s in step_types if s != StepType.HITL_APPROVAL]

        steps = []
        prev_step_id = None

        for i, step_type in enumerate(step_types):
            step_id = f"STEP-{i + 1:02d}-{step_type.value}"
            step = WorkflowStep(
                step_id=step_id,
                step_type=step_type,
                name=step_type.value.replace("_", " ").title(),
                description=self.STEP_DESCRIPTIONS.get(step_type, ""),
                depends_on=[prev_step_id] if prev_step_id else [],
                required=step_type not in [StepType.DECISION_LOG],
                timeout_seconds=120 if step_type == StepType.HITL_APPROVAL else 60,
            )
            steps.append(step)
            prev_step_id = step_id

        workflow_id = f"WF-{query_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        return WorkflowDefinition(
            workflow_id=workflow_id,
            name=f"{query_type} 의사결정 워크플로",
            description=f"{query_type} 유형 질문에 대한 의사결정 지원 워크플로",
            query_type=query_type,
            steps=steps,
        )

    def start_execution(
        self,
        workflow: WorkflowDefinition,
        context: WorkflowContext,
    ) -> WorkflowExecution:
        """
        워크플로 실행 시작

        Args:
            workflow: 워크플로 정의
            context: 실행 컨텍스트

        Returns:
            WorkflowExecution: 실행 인스턴스
        """
        execution_id = f"EXEC-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.RUNNING,
            input_data={
                "user_query": context.user_query,
                "org_unit_id": context.org_unit_id,
                "constraints": context.constraints,
            },
            current_step_id=workflow.steps[0].step_id if workflow.steps else None,
        )

        self.executions[execution_id] = execution

        logger.info(f"워크플로 실행 시작: {execution_id} (워크플로: {workflow.workflow_id})")

        return execution

    def execute_step(
        self,
        execution: WorkflowExecution,
        step: WorkflowStep,
        context: WorkflowContext,
    ) -> StepResult:
        """
        단일 단계 실행

        Args:
            execution: 실행 인스턴스
            step: 실행할 단계
            context: 워크플로 컨텍스트

        Returns:
            StepResult: 단계 실행 결과
        """
        started_at = datetime.now()

        result = StepResult(
            step_id=step.step_id,
            step_type=step.step_type,
            status=StepStatus.RUNNING,
            started_at=started_at,
        )

        try:
            logger.info(f"단계 실행: {step.step_id} - {step.name}")

            output = self._execute_step_by_type(step, context)

            result.status = StepStatus.COMPLETED
            result.output = output
            result.completed_at = datetime.now()
            result.duration_ms = (result.completed_at - started_at).total_seconds() * 1000

            # 컨텍스트 업데이트
            self._update_context(step.step_type, output, context)

            logger.info(f"단계 완료: {step.step_id} ({result.duration_ms:.0f}ms)")

        except Exception as e:
            result.status = StepStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()
            result.duration_ms = (result.completed_at - started_at).total_seconds() * 1000

            logger.error(f"단계 실패: {step.step_id} - {e}")

        execution.step_results[step.step_id] = result
        return result

    def _execute_step_by_type(
        self,
        step: WorkflowStep,
        context: WorkflowContext,
    ) -> dict[str, Any]:
        """단계 유형별 실행 로직"""

        if step.step_type == StepType.QUERY_DECOMPOSITION:
            agent = self.agents.get("query_decomposition")
            if agent:
                result = agent.decompose(context.user_query, {"org_unit_id": context.org_unit_id})
                return {
                    "query_type": result.query_type.value,
                    "sub_queries": [
                        {"type": sq.query_type, "query": sq.query, "priority": sq.priority}
                        for sq in result.sub_queries
                    ],
                    "intent": result.intent,
                }
            return self._mock_query_decomposition(context)

        elif step.step_type == StepType.KG_QUERY:
            if self.kg_client:
                # 실제 KG 쿼리 실행
                query_type = (
                    context.decomposed_query.get("query_type", "CAPACITY")
                    if context.decomposed_query
                    else "CAPACITY"
                )
                return self._execute_kg_query(query_type, context)
            return self._mock_kg_query(context)

        elif step.step_type == StepType.OPTION_GENERATION:
            agent = self.agents.get("option_generator")
            if agent:
                query_type = (
                    context.decomposed_query.get("query_type", "CAPACITY")
                    if context.decomposed_query
                    else "CAPACITY"
                )
                result = agent.generate_options(
                    query_type=query_type,
                    context=context.kg_results or {},
                    constraints=context.constraints,
                )
                return agent.to_dict(result)
            return self._mock_option_generation(context)

        elif step.step_type == StepType.IMPACT_SIMULATION:
            agent = self.agents.get("impact_simulator")
            if agent and context.options:
                query_type = (
                    context.decomposed_query.get("query_type", "CAPACITY")
                    if context.decomposed_query
                    else "CAPACITY"
                )
                result = agent.simulate(
                    query_type=query_type,
                    options=context.options,
                    baseline=context.kg_results or {},
                )
                return agent.to_dict(result)
            return self._mock_impact_simulation(context)

        elif step.step_type == StepType.PROBABILITY_CALCULATION:
            agent = self.agents.get("success_probability")
            if agent and context.options:
                results = []
                for opt in context.options.get("options", []):
                    result = agent.calculate_probability(
                        subject_type="OPTION",
                        subject_id=opt.get("option_id", ""),
                        subject_name=opt.get("name", ""),
                        context={**(context.kg_results or {}), "option": opt},
                    )
                    results.append(agent.to_dict(result))
                return {"probabilities": results}
            return self._mock_probability_calculation(context)

        elif step.step_type == StepType.VALIDATION:
            agent = self.agents.get("validator")
            if agent:
                # 현재까지의 결과를 텍스트로 변환
                response_text = self._build_response_text(context)
                evidence = self._collect_evidence(context)
                result = agent.validate(response_text, evidence, {})
                return agent.to_dict(result)
            return self._mock_validation(context)

        elif step.step_type == StepType.HITL_APPROVAL:
            if self.hitl_handler:
                execution = self.executions.get(context.org_unit_id or "")
                if execution:
                    return self.hitl_handler(execution, context)
            return {"status": "AUTO_APPROVED", "reason": "HITL 핸들러 미설정"}

        elif step.step_type == StepType.DECISION_LOG:
            return self._create_decision_log(context)

        return {"status": "UNKNOWN_STEP"}

    def _update_context(
        self,
        step_type: StepType,
        output: dict[str, Any],
        context: WorkflowContext,
    ) -> None:
        """실행 결과로 컨텍스트 업데이트"""
        if step_type == StepType.QUERY_DECOMPOSITION:
            context.decomposed_query = output
        elif step_type == StepType.KG_QUERY:
            context.kg_results = output
        elif step_type == StepType.OPTION_GENERATION:
            context.options = output
        elif step_type == StepType.IMPACT_SIMULATION:
            context.impact_analysis = output
        elif step_type == StepType.PROBABILITY_CALCULATION:
            context.probabilities = output
        elif step_type == StepType.VALIDATION:
            context.validation_result = output
        elif step_type == StepType.HITL_APPROVAL:
            context.hitl_decision = output

    def run_workflow(
        self,
        workflow: WorkflowDefinition,
        context: WorkflowContext,
        stop_on_hitl: bool = True,
    ) -> WorkflowExecution:
        """
        전체 워크플로 실행

        Args:
            workflow: 워크플로 정의
            context: 실행 컨텍스트
            stop_on_hitl: HITL 단계에서 중지 여부

        Returns:
            WorkflowExecution: 최종 실행 결과
        """
        execution = self.start_execution(workflow, context)

        for step in workflow.steps:
            execution.current_step_id = step.step_id

            # 의존성 확인
            for dep_id in step.depends_on:
                dep_result = execution.step_results.get(dep_id)
                if dep_result and dep_result.status == StepStatus.FAILED:
                    if step.required:
                        execution.status = WorkflowStatus.FAILED
                        execution.error = f"의존 단계 실패: {dep_id}"
                        return execution
                    else:
                        # 선택적 단계는 스킵
                        skip_result = StepResult(
                            step_id=step.step_id,
                            step_type=step.step_type,
                            status=StepStatus.SKIPPED,
                        )
                        execution.step_results[step.step_id] = skip_result
                        continue

            # HITL 단계에서 중지
            if step.step_type == StepType.HITL_APPROVAL and stop_on_hitl:
                execution.status = WorkflowStatus.PAUSED
                logger.info(f"HITL 승인 대기 중: {execution.execution_id}")
                return execution

            # 단계 실행
            result = self.execute_step(execution, step, context)

            if result.status == StepStatus.FAILED and step.required:
                execution.status = WorkflowStatus.FAILED
                execution.error = result.error
                return execution

        execution.status = WorkflowStatus.COMPLETED
        execution.completed_at = datetime.now()

        logger.info(f"워크플로 완료: {execution.execution_id}")

        return execution

    def resume_workflow(
        self,
        execution_id: str,
        workflow: WorkflowDefinition,
        context: WorkflowContext,
        hitl_result: dict[str, Any],
    ) -> WorkflowExecution:
        """
        HITL 승인 후 워크플로 재개

        Args:
            execution_id: 실행 ID
            workflow: 워크플로 정의
            context: 실행 컨텍스트
            hitl_result: HITL 승인 결과

        Returns:
            WorkflowExecution: 최종 실행 결과
        """
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"실행 인스턴스를 찾을 수 없음: {execution_id}")

        if execution.status != WorkflowStatus.PAUSED:
            raise ValueError(f"재개 불가능한 상태: {execution.status}")

        # HITL 결과 기록
        context.hitl_decision = hitl_result

        # 현재 HITL 단계 완료 처리
        hitl_step = next((s for s in workflow.steps if s.step_type == StepType.HITL_APPROVAL), None)
        if hitl_step:
            hitl_result_obj = StepResult(
                step_id=hitl_step.step_id,
                step_type=StepType.HITL_APPROVAL,
                status=StepStatus.COMPLETED,
                output=hitl_result,
                completed_at=datetime.now(),
            )
            execution.step_results[hitl_step.step_id] = hitl_result_obj

        # 나머지 단계 실행
        execution.status = WorkflowStatus.RUNNING
        hitl_found = False

        for step in workflow.steps:
            if step.step_type == StepType.HITL_APPROVAL:
                hitl_found = True
                continue

            if not hitl_found:
                continue

            execution.current_step_id = step.step_id
            result = self.execute_step(execution, step, context)

            if result.status == StepStatus.FAILED and step.required:
                execution.status = WorkflowStatus.FAILED
                execution.error = result.error
                return execution

        execution.status = WorkflowStatus.COMPLETED
        execution.completed_at = datetime.now()

        return execution

    # ============================================================
    # Mock 데이터 생성 메서드 (에이전트 미연결 시 사용)
    # ============================================================

    def _mock_query_decomposition(self, context: WorkflowContext) -> dict:
        """Mock 질문 분해 결과"""
        return {
            "query_type": "CAPACITY",
            "sub_queries": [
                {"type": "utilization", "query": "현재 가동률 조회", "priority": 1},
                {"type": "forecast", "query": "향후 12주 수요 예측", "priority": 2},
                {"type": "bottleneck", "query": "병목 구간 식별", "priority": 3},
            ],
            "intent": "12주 내 가동률 병목 예측 및 해결 방안 제시",
        }

    def _mock_kg_query(self, context: WorkflowContext) -> dict:
        """Mock KG 쿼리 결과"""
        return {
            "utilization": {
                "current": 0.85,
                "trend": "INCREASING",
            },
            "bottleneck_weeks": ["W05", "W06", "W07"],
            "gap_fte": 2.5,
            "available_resources": [
                {"employee_id": "EMP-001", "name": "홍길동", "available_fte": 0.5},
                {"employee_id": "EMP-002", "name": "김철수", "available_fte": 0.3},
            ],
        }

    def _mock_option_generation(self, context: WorkflowContext) -> dict:
        """Mock 대안 생성 결과"""
        return {
            "options": [
                {
                    "option_id": "OPT-01",
                    "name": "내부 재배치",
                    "option_type": "CONSERVATIVE",
                    "scores": {"impact": 65, "feasibility": 85, "risk": 25},
                },
                {
                    "option_id": "OPT-02",
                    "name": "외부 인력 활용",
                    "option_type": "BALANCED",
                    "scores": {"impact": 80, "feasibility": 70, "risk": 45},
                },
                {
                    "option_id": "OPT-03",
                    "name": "정규직 채용",
                    "option_type": "AGGRESSIVE",
                    "scores": {"impact": 95, "feasibility": 50, "risk": 65},
                },
            ],
            "recommendation": "OPT-02",
        }

    def _mock_impact_simulation(self, context: WorkflowContext) -> dict:
        """Mock 영향 분석 결과"""
        return {
            "baseline": {"utilization": 0.85, "cost": 100000000},
            "scenarios": [
                {"option_id": "OPT-01", "utilization": 0.78, "cost": 105000000},
                {"option_id": "OPT-02", "utilization": 0.75, "cost": 120000000},
                {"option_id": "OPT-03", "utilization": 0.70, "cost": 180000000},
            ],
        }

    def _mock_probability_calculation(self, context: WorkflowContext) -> dict:
        """Mock 성공 확률 결과"""
        return {
            "probabilities": [
                {"option_id": "OPT-01", "probability": 0.78, "confidence": "HIGH"},
                {"option_id": "OPT-02", "probability": 0.72, "confidence": "MEDIUM"},
                {"option_id": "OPT-03", "probability": 0.58, "confidence": "LOW"},
            ],
        }

    def _mock_validation(self, context: WorkflowContext) -> dict:
        """Mock 검증 결과"""
        return {
            "is_valid": True,
            "evidence_coverage": 0.92,
            "hallucination_risk": 0.08,
            "unverified_claims": [],
        }

    def _execute_kg_query(self, query_type: str, context: WorkflowContext) -> dict:
        """실제 KG 쿼리 실행"""
        # 실제 구현은 kg_client 사용
        return self._mock_kg_query(context)

    def _build_response_text(self, context: WorkflowContext) -> str:
        """컨텍스트에서 응답 텍스트 생성"""
        parts = []
        if context.options:
            for opt in context.options.get("options", []):
                parts.append(f"대안: {opt.get('name', '')}")
        return "\n".join(parts)

    def _collect_evidence(self, context: WorkflowContext) -> list[dict]:
        """컨텍스트에서 증거 수집"""
        evidence = []
        if context.kg_results:
            evidence.append(
                {
                    "source": "KG_QUERY",
                    "data": context.kg_results,
                }
            )
        return evidence

    def _create_decision_log(self, context: WorkflowContext) -> dict:
        """의사결정 로그 생성"""
        return {
            "log_id": f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "query": context.user_query,
            "selected_option": context.hitl_decision.get("selected_option")
            if context.hitl_decision
            else None,
            "decision_maker": context.hitl_decision.get("approver")
            if context.hitl_decision
            else None,
            "rationale": context.hitl_decision.get("rationale") if context.hitl_decision else None,
        }

    # ============================================================
    # 유틸리티 메서드
    # ============================================================

    def get_workflow_status(self, execution_id: str) -> dict[str, Any]:
        """워크플로 실행 상태 조회"""
        execution = self.executions.get(execution_id)
        if not execution:
            return {"error": "실행 인스턴스를 찾을 수 없음"}

        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "current_step": execution.current_step_id,
            "steps_completed": sum(
                1 for r in execution.step_results.values() if r.status == StepStatus.COMPLETED
            ),
            "steps_failed": sum(
                1 for r in execution.step_results.values() if r.status == StepStatus.FAILED
            ),
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error": execution.error,
        }

    def to_dict(self, workflow: WorkflowDefinition) -> dict:
        """워크플로 정의를 딕셔너리로 변환"""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "query_type": workflow.query_type,
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_type": step.step_type.value,
                    "name": step.name,
                    "description": step.description,
                    "depends_on": step.depends_on,
                    "required": step.required,
                    "timeout_seconds": step.timeout_seconds,
                }
                for step in workflow.steps
            ],
            "created_at": workflow.created_at.isoformat(),
        }

    def execution_to_dict(self, execution: WorkflowExecution) -> dict:
        """실행 인스턴스를 딕셔너리로 변환"""
        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "input_data": execution.input_data,
            "current_step_id": execution.current_step_id,
            "step_results": {
                step_id: {
                    "step_type": result.step_type.value,
                    "status": result.status.value,
                    "output": result.output,
                    "error": result.error,
                    "duration_ms": result.duration_ms,
                }
                for step_id, result in execution.step_results.items()
            },
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error": execution.error,
        }


# CLI 테스트용
if __name__ == "__main__":
    import json

    agent = WorkflowBuilderAgent()

    # 워크플로 정의 생성
    workflow = agent.build_workflow("CAPACITY")
    print("=" * 60)
    print("WORKFLOW DEFINITION")
    print("=" * 60)
    print(json.dumps(agent.to_dict(workflow), indent=2, ensure_ascii=False))

    # 워크플로 실행
    context = WorkflowContext(
        user_query="향후 12주간 AI팀의 가동률 병목 구간과 해결 방안은?",
        org_unit_id="ORG-AI-001",
        constraints={"max_budget": 100000000},
    )

    print("\n" + "=" * 60)
    print("WORKFLOW EXECUTION (HITL 전까지)")
    print("=" * 60)

    execution = agent.run_workflow(workflow, context, stop_on_hitl=True)
    print(json.dumps(agent.execution_to_dict(execution), indent=2, ensure_ascii=False))

    # HITL 승인 후 재개
    if execution.status == WorkflowStatus.PAUSED:
        print("\n" + "=" * 60)
        print("HITL 승인 후 재개")
        print("=" * 60)

        hitl_result = {
            "approved": True,
            "selected_option": "OPT-02",
            "approver": "manager@example.com",
            "rationale": "비용 대비 효과가 적절함",
        }

        final_execution = agent.resume_workflow(
            execution.execution_id, workflow, context, hitl_result
        )
        print(json.dumps(agent.execution_to_dict(final_execution), indent=2, ensure_ascii=False))
